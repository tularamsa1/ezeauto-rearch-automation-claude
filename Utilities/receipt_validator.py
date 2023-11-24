import re
import time
from playwright.sync_api import Playwright, sync_playwright
import pandas as pd
import requests
import json
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pytest_check as check

from Configuration import TestSuiteSetup
from Utilities.DBProcessor import get_value_from_db
from Utilities.ConfigReader import read_config as get_config
from Utilities.charge_slip_validator import charge_slip_validator
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities import Validator
from DataProvider import GlobalVariables as global_variables, GlobalVariables, GlobalConstants

logger = EzeAutoLogger(__name__)

'''
expected_details = {
    'bank_logo': 'http://d.eze.cc/images/logos/cs_bank_hdfc.png',
    'date': '2022-06-14',
    'time': '21:16:36',
    'merchant_ref_no': 'Ref # 0614211623',
    'merchant_info': 'UPI_HDFCBANK_HDFCPG, address1, city1',
    'payment_option': 'SALE',
    'AUTH CODE': 'NA',
    'RRN': '1752597',
    'PAID BY:': 'UPI',
    'BASE AMOUNT:': 'Rs.390.00',
    'signature_not_required_text': 'SIGNATURE NOT REQUIRED',
    'signature_not_available_text': 'SIGN: signature not available',
    'customer_copy_text': '***** CUSTOMER COPY *****',
    'ezetap_logo': '/portal/images/ezetap_wb_logo.gif',
    'version': 'VERSION V-2.0.0',
    'unnamed_section_text': 'abc@upi'
}

'''


# class defintion for custom exceptions
class ReceiptValidationError(Exception):
    def __init__(self, message):
        self.message = message


class TransactionAPIJsonResponseError(Exception):
    def __init__(self, response):
        self.response = response


def initialize_webdriver(maximize=False):
    try:
        logger.info("Initializing webdriver")
        opt = webdriver.ChromeOptions()
        if maximize is True:
            opt.add_argument("--start-maximized")
        chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(options=opt)
    except Exception as e:
        logger.exception(e, exc_info=True)
        print(e)
        raise ReceiptValidationError("Unable to initialize webdriver")

    return driver


# global variables for this module ----------------------

# mapped dictionary that is used to identify each fields based on text
mapped_identifier_keys_for_receipt_fields = dict(
    datetime="Date/Time:",
    signature_not_required_text="SIGNATURE NOT REQUIRED",
    signature_not_available_text='SIGN: signature not available',
    customer_copy_text="***** CUSTOMER COPY *****",
    version_found="VERSION V-",
    merchant_ref_no_text="Ref #",
    pin_verified_section_text="PIN VERIFIED",
    agreement_text="""I agree to pay as per the card issuer agreement and receive chargeslip by electronic means.""",
    customer_consent_for_emi_text_id="CUSTOMER CONSENT FOR EMI",  # -------------------------------------------------------?????? NEW ADDITION .......................... here
)

present_receipt_info = None
index_locations = {}
transaction_type = [
    'SALE', 'REVERSED', 'REFUND', 'EMI SALE',
    'DEBIT SALE', 'VOID SALE', 'NBFC EMI Sale', 'Sale Cash Back', 'VOID CASH ONLY', 'Cash Only'
]


# -------------------------------------------------------


# function definitions
def _find_date_n_time_from_single_row(receipt_timestamp_row):
    global mapped_identifier_keys_for_receipt_fields
    global present_receipt_info
    date_time = " ".join([td.text.strip().replace(mapped_identifier_keys_for_receipt_fields['datetime'], '').strip() \
                          for td in receipt_timestamp_row.find_all('td') if td.text.strip()])

    # find date and time from '2022-06-13 14:44:36'
    date_results = re.findall(r'\d{4}-\d{2}-\d{2}', date_time)
    time_results = re.findall(r'\d{2}:\d{2}:\d{2}', date_time)
    if date_results:
        present_receipt_info['date'] = date_results[0]
    if time_results:
        present_receipt_info['time'] = time_results[0]

    if date_results or time_results:
        return True
    else:
        return False


# not ideal to iterate on each field check.
# Ideal is to run all checks in one single for loop. for now are taking which is not ideal
def _find_datetime_from_rows(rows_with_fields):
    global index_locations
    is_having_datetime = None
    for row in rows_with_fields:
        is_having_datetime = _find_date_n_time_from_single_row(row)
        if is_having_datetime:
            index_locations['datetime'] = rows_with_fields.index(row)
            break
    return is_having_datetime


def _get_key_values_from_table_rows(section_rows):
    global present_receipt_info
    global mapped_identifier_keys_for_receipt_fields
    for tr in section_rows:
        tds = tr.find_all('td')
        if len(tds) == 2:
            if ":" not in tds[1].text:  # checking if second td is not a key value pair
                # below line of code modified. old: key = tr.find_all('td')[0].text.strip().rstrip(":").rstrip()
                key = tr.find_all('td')[0].text.strip()
                value = tr.find_all('td')[1].text.strip()
                present_receipt_info[key] = value
            else:
                for td in tds:
                    key_value_pair = td.text.strip().split(':')
                    key = key_value_pair[0].strip()
                    value = key_value_pair[1].strip()
                    present_receipt_info[key] = value
        elif len(tds) == 1:
            for td in tds:
                if td.text.strip():
                    text_lines_found = [text.strip() for text in td.stripped_strings if ("------" not in text)]
                    text_lines_found = [i for i in text_lines_found if i]  # removing empty lines

                    if not text_lines_found:
                        continue

                    # checking if emi consent text is found
                    if (text_lines_found[0] == mapped_identifier_keys_for_receipt_fields[
                        "customer_consent_for_emi_text_id"]):
                        # customer consent for emi text is found
                        present_receipt_info["customer_consent_for_emi_text"] = "\n".join(text_lines_found)
                    else:
                        # new changes --starts here
                        colon_splits = td.text.strip().split(':')
                        if not colon_splits:
                            logger.info("No colon splits found")
                            logger.info(td.text.strip())
                            # pass
                        elif len(colon_splits) == 2:
                            key_value_pair = colon_splits
                            key = key_value_pair[0].strip()
                            value = key_value_pair[1].strip()
                            present_receipt_info[key] = value
                        else:
                            text_lines_with_colon = []
                            text_lines_without_colon = []
                            for l in text_lines_found:
                                if ":" in l:
                                    text_lines_with_colon.append(l)
                                else:
                                    text_lines_without_colon.append(l)

                            # without colon
                            if text_lines_without_colon:
                                combined_lines_without_colon = '\n'.join(text_lines_without_colon)
                                present_receipt_info["unidentified_sections"].append(
                                    combined_lines_without_colon.strip())

                            # with colon
                            for line in text_lines_with_colon:
                                splits_from_line = line.split(":")
                                if len(splits_from_line) == 2:
                                    key, value = splits_from_line[0].strip(), splits_from_line[1].strip()
                                    present_receipt_info[key] = value
                                else:
                                    present_receipt_info["unidentified_sections"].append(line.strip())

    # removing already known texts
    known_texts = [
        "PRODUCT INFORMATION",
    ]
    for kt in known_texts:
        if kt in present_receipt_info["unidentified_sections"]:
            present_receipt_info["unidentified_sections"].remove(kt)


def _switch_handles(driver) -> None:
    # to fetch the first child window handle
    if len(driver.window_handles) > 1:
        chwnd = driver.window_handles[1]
        # to switch focus the first child window handle
        driver.switch_to.window(chwnd)

        print(driver.current_url)
        logger.debug(driver.current_url)
    else:
        print("No child window found")
        logger.error("No child window found")

    return driver  # use OOPs to work with same driver always


def _check_if_receipt_is_found_on_page(driver):
    receipt_found = False
    inner_html = ""

    # to identify element and obtain innerHTML with execute_script
    # possible_div_recipts = driver.find_elements(By.CLASS_NAME, 'receipt')
    # possible_div_recipts = (driver.query_selector(".receipt"))
    # print(type(possible_div_recipts))
    # if possible_div_recipts:
    #     print(f"possible_div_recipts : {possible_div_recipts}")
    #     l = possible_div_recipts[0]
    # inner_html= driver.execute_script("return arguments[0].innerHTML;",l)
    count = 0
    while True:
        if driver.locator(".receipt").is_visible():
            inner_html = (driver.locator(".receipt").inner_html())
            break
        else:
            count = count + 1
            if count == 10:
                inner_html = None
                break
    # print(f"inner_html : {inner_html}")
    receipt_found = True

    return driver, inner_html, receipt_found


def _check_if_receipt_table_is_found_on_page(soup):
    receipt_table_found = False
    receipt_table = None

    receipt_table_list = soup.find_all('table')
    if receipt_table_list:
        receipt_table = receipt_table_list[0]  # improper
        receipt_table_found = True
    else:
        logger.critical("No receipt table found")

    return receipt_table, receipt_table_found


def _extract_merchant_info(merchant_info_rows):
    global present_receipt_info
    global mapped_identifier_keys_for_receipt_fields

    merchant_section_texts = [row.text.strip() for row in merchant_info_rows if row.text.strip()]

    for row in merchant_section_texts:
        if mapped_identifier_keys_for_receipt_fields['merchant_ref_no_text'] in row:
            # get the merchant ref no as popped element
            present_receipt_info['merchant_ref_no'] = merchant_section_texts.pop(merchant_section_texts.index(row))

    merchant_text_fields = [", ".join([l.strip() for l in text.replace("\t", "").split("\n") if l.strip()]) for text in
                            merchant_section_texts]

    # TO BE CHECKED LATER IF MORE OTHER FIELDS ARE AVAILABLE
    merchant_info = ", ".join(merchant_text_fields)
    present_receipt_info['merchant_info'] = merchant_info


def _get_present_receipt_info_from_receipt_table_n_post_table_sections(receipt_table):
    global present_receipt_info
    global index_locations
    global transaction_type  # transaction type
    global mapped_identifier_keys_for_receipt_fields

    present_receipt_info = {}
    present_receipt_info["unidentified_sections"] = []              # ?????? NEW ADDITION .......................... here

    rows = receipt_table.find_all('tr')

    rows_with_fields = []
    for row in rows:
        tds = row.find_all('td')
        if len(tds) == 1 and tds[0].find_all('img'):
            images = tds[0].find_all('img')

            image = images[0]

            # getting attribute value of image
            image_alt_text = image.get('alt')
            if image_alt_text == 'Bank':
                print("bank logo is found")
                logger.info("bank logo is found")
                image_src = image.get('src')
                present_receipt_info['bank_logo'] = image_src
            else:
                print("bank logo is not found")
                logger.info("bank logo is not found")
                # present_receipt_info['bank_logo'] = None     # ==== CHECK THIS>>>>>> EMRE


        # removing rows those are just used for giving space or padding
        elif hasattr(row, "class") and ('amount-padding' in row.get_attribute_list('class')):
            print("Found amount padding. Therefore not adding this row to present_receipt_info")
            logger.debug("Found amount padding. Therefore not adding this row to present_receipt_info")
        else:
            # print(row)
            rows_with_fields.append(row)
    # print(rows_with_fields)
    # getting index of datetime row from rows_with_fields list

    if not _find_datetime_from_rows(rows_with_fields):
        print("No datetime found")
        logger.warning("No datetime found")

    # print(rows_with_fields)
    for row in rows_with_fields:
        if len(row.find_all('td')) == 1:
            for payment_option in transaction_type:
                if payment_option in row.text:
                    index_locations['payment_option'] = rows_with_fields.index(row)
                    break

    # print(rows_with_fields)
    merchant_info_rows = rows_with_fields[:index_locations['datetime']]
    # print(merchant_info_rows)
    _extract_merchant_info(merchant_info_rows)

    # this section might be a problem if there are not receipt table middle section rows
    receipt_table_middle_section_rows = rows_with_fields[
                                        (index_locations['datetime'] + 1): index_locations['payment_option']]
    # the above section contains TID, BATCH NO, INVOICE NO, AID, APP .. TSI etc
    _get_key_values_from_table_rows(receipt_table_middle_section_rows)

    payment_info_rows = rows_with_fields[index_locations['payment_option'] + 1:]
    payment_option = rows_with_fields[index_locations['payment_option']].text.strip()

    # payment_info_rows
    present_receipt_info['payment_option'] = payment_option  # SALE etc.

    _get_key_values_from_table_rows(payment_info_rows)

    if ("CARD" in present_receipt_info) and ("\n" in present_receipt_info['CARD']):
        card_number_n_emv = [line.strip() for line in present_receipt_info['CARD'].split("\n") if line.strip()]
        present_receipt_info["CARD"] = " ".join(card_number_n_emv)

    # POST TABLE SECTION ===========================
    post_table_elements = payment_info_rows[-1].find_all_next('p')

    # paragraph_texts = []
    indices = {}

    for paragraph in post_table_elements:
        possible_images = paragraph.find_all('img')

        if possible_images:
            for image in possible_images:
                image_alt_text = image.get('alt')
                image_src = image.get('src')

                if image_alt_text == 'signature':
                    present_receipt_info['signature_image'] = image_src
                    indices['signature_section'] = post_table_elements.index(paragraph)  # what to do with "SIGN:"
                elif image_alt_text == 'Ezetap':
                    present_receipt_info['ezetap_logo'] = image_src
                else:
                    print("No relevant image found though images are present")
                    logger.warning("No relevant image found though images are present")

        if mapped_identifier_keys_for_receipt_fields['customer_copy_text'] in paragraph.text:
            present_receipt_info['customer_copy_text'] = paragraph.text.strip()
            indices['customer_copy'] = post_table_elements.index(paragraph)

        if mapped_identifier_keys_for_receipt_fields['signature_not_required_text'] in paragraph.text:
            present_receipt_info['signature_not_required_text'] = paragraph.text.strip()
            if 'signature_section' in indices:
                print("over-writing the signature index")
            indices['signature_section'] = post_table_elements.index(paragraph)

        # added newly to fix -- on jul 13, 2022
        if ('signature_section' not in indices) and (
                mapped_identifier_keys_for_receipt_fields['signature_not_available_text'] in paragraph.text):
            present_receipt_info['signature_not_available_text'] = paragraph.text.strip()
            if 'signature_section' in indices:
                print("over-writing the signature index")
            indices['signature_section'] = post_table_elements.index(paragraph)

        if mapped_identifier_keys_for_receipt_fields['agreement_text'] in paragraph.text:
            present_receipt_info['agreement_text'] = paragraph.text.strip()
            indices['agreement_section'] = post_table_elements.index(paragraph)

            # processing agreement text
            present_receipt_info['agreement_text'] = "\n".join(
                [line.strip() for line in present_receipt_info['agreement_text'].replace("-", '').splitlines() if
                 line.strip()])

    if 'customer_copy_text' in present_receipt_info:
        # cust_copy_text_lines includes customer copy text and version information
        cust_copy_text_lines = [line.strip() for line in present_receipt_info['customer_copy_text'].splitlines() if
                                line.strip()]

        # finding version
        for line in cust_copy_text_lines:
            if mapped_identifier_keys_for_receipt_fields['customer_copy_text'] in line:
                present_receipt_info['customer_copy_text'] = line.strip()
            if mapped_identifier_keys_for_receipt_fields['version_found'] in line:
                present_receipt_info['version'] = line.strip()

    # finding pin verified text
    if 'signature_section' in indices.keys():
        for para in post_table_elements[:indices['signature_section']]:
            if "pin_verified_section_text" in mapped_identifier_keys_for_receipt_fields.keys():
                if mapped_identifier_keys_for_receipt_fields['pin_verified_section_text'] in para.text:
                    present_receipt_info['pin_verified_section_text'] = para.text.strip()
                    break
            # else:
            #     break

    # getting unnamed_section extracted
    if ("agreement_section" in indices.keys()) and ("customer_copy" in indices.keys()):
        if 'signature_section' in indices.keys():
            unnamed_sec_elements = post_table_elements[indices['signature_section'] + 1:indices['agreement_section']]
            unnamed_sec_elements_texts = [elem.text.strip() for elem in unnamed_sec_elements if elem.text.strip()]
            unnamed_section_text = [" ".join([i.strip() for i in w.split("  ") if i.strip()]) for w in
                                    unnamed_sec_elements_texts]

            unnamed_section_text = " ".join(unnamed_section_text)

            if unnamed_section_text.strip():
                present_receipt_info['unnamed_section_text'] = unnamed_section_text.strip()

    elif ("signature_section" in indices.keys()) and ("customer_copy" in indices.keys()):
        unnamed_sec_elements = post_table_elements[indices['signature_section'] + 1:indices['customer_copy']]
        unnamed_sec_elements_texts = [elem.text.strip() for elem in unnamed_sec_elements if elem.text.strip()]
        unnamed_section_text = [" ".join([i.strip() for i in w.split("  ") if i.strip()]) for w in
                                unnamed_sec_elements_texts]

        unnamed_section_text = " ".join(unnamed_section_text)

        if unnamed_section_text.strip():
            present_receipt_info['unnamed_section_text'] = unnamed_section_text.strip()


    else:
        logger.warning(
            "The customer copy or agreement section is not found! Therefore Unable to extract '[[ unnamed_section ]]'")

    logger.info("DETAILS THAT ARE FOUND IN CURRENT RECEIPT")
    logger.info(present_receipt_info)
    logger.info(100 * "+")

    print("DETAILS THAT ARE FOUND IN CURRENT RECEIPT".center(100, "-"))
    print(present_receipt_info)
    print(100 * "+")


def get_receipt_url_from_db(txn_id) -> str:
    query = f"""SELECT  receipt_url_shortcode FROM txn WHERE id = '{txn_id}';"""

    logger.info('Getting the receipt url info from the db')
    df = get_value_from_db(query)

    if df.shape[0] and df.shape[0]:
        receipt_url_shortcode = df.iloc[0]['receipt_url_shortcode']
        logger.debug('Successfully retrieved the receipt url info from the db')
        try:
            env = str(get_config("APIs", "env")).lower()
        except Exception as e:
            logger.warning(f"Unable to get env from config.ini: {e}. set env first.")
            raise Exception(f"Unable to get env from config.ini: {e}. set env first.")
        base_url = get_config("APIs", "baseurl")
        url = f"{base_url}/r/o/{receipt_url_shortcode}/"
    else:
        logger.warning(f"No receipt url info is found in DB for the given txn id '{txn_id}'. Please check the DB.")
        url = None

    return url


def get_current_charge_slip_data_from_receipt_loaded_webdriver(driver) -> dict:
    global present_receipt_info

    # switching handles if there are multiple windows
    # driver = _switch_handles(driver)

    driver, inner_html, receipt_found = _check_if_receipt_is_found_on_page(driver)
    if receipt_found:
        soup = BeautifulSoup(inner_html, 'html.parser')  # get soup object to parse the html
        receipt_table, receipt_table_found = _check_if_receipt_table_is_found_on_page(soup)
        if receipt_table_found:
            _get_present_receipt_info_from_receipt_table_n_post_table_sections(receipt_table)

        else:
            logger.info("No receipt table [-----] inside charge slip found")  # go to logger
            logger.info("Some part of the charge slip is not loaded")

    else:
        logger.info("No receipt found")  # goes to loggger
        logger.info("Charge Slip was not loaded!")

    return present_receipt_info


def compare_present_receipt_info_with_expected_receipt_info(present_details: dict, expected_details: dict, txn_id,
                                                            valid_receipt_url) -> dict:
    print("=======   CHARGE SLIP Validation Started    =======")
    fields_that_are_not_present = set()
    matching_fields = set()
    unmatching_fields = set()
    # # logo validation
    value_cs_logo_validation_enabled = get_config(section="Validations", key="cs_logo_validation")
    cs_logo_validation_enabled = str(value_cs_logo_validation_enabled).strip().title() == 'True'
    # # logo_validation = None
    if cs_logo_validation_enabled:
        logo_validation_1 = validate_logo_from_charge_slip(txn_id, url=valid_receipt_url)
        # validation_list.append(logo_validation)

        if logo_validation_1 is True:
            logger.info(f"Logo Validation is Passed")
        if logo_validation_1 is False:
            logger.info(f"Logo Validation is Failed")

        expected_details['logo_validation'] = True
        present_details['logo_validation'] = logo_validation_1

    expected_details, present_details = Validator.filter_values("chargeslip", expected_details, present_details)
    if expected_details == {} and present_details == {}:
        print("Expected and actual values list is empty.")
        if not GlobalVariables.str_chargeslip_val_result in ("Fail", "Pass"):
            GlobalVariables.str_chargeslip_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
    elif expected_details == "" and present_details == "":
        print("Expected and actual values list is empty.")
        if not GlobalVariables.str_chargeslip_val_result in ("Fail", "Pass"):
            GlobalVariables.str_chargeslip_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
    else:
        if present_details:
            for key in expected_details:
                if key in present_details:
                    GlobalVariables.tot_chargeslip_val = GlobalVariables.tot_chargeslip_val + 1
                    logger.debug(f"{key} found")
                    # below if block is to handle the net cost value for brand emi axis issuer root org
                    if key == 'Net cost':
                        pattern = re.compile(r'Rs\.\d{1,3}(,\d{3})*\.\d{2}')
                        present_details[key] = pattern.search(present_details[key].strip()).group()
                    if expected_details[key] == present_details[key]:
                        matching_fields.add(key)
                        logger.debug(f"'{key}' is matching")
                    else:
                        unmatching_fields.add(key)
                        logger.debug(f"'{key}' is not matching")
                        check.equal(expected_details[key], present_details[key])
                else:
                    fields_that_are_not_present.add(key)
                    print(f"The field '{key}' not present in actual values list")
                    logger.debug(f"The field '{key}' not present in actual values list")
                    check.equal(f"Expected key {key}", f"Actual key ''", f"Expected field {key} is not available in"
                                                                         f" the actual values list.")
            Validator.print_validation_result(expected_details, present_details, matching_fields, unmatching_fields)

        else:
            print("No present receipt info found")
            logger.warning("No present receipt info found")
            GlobalVariables.str_chargeslip_val_result = "Fail"
            check.equal("Charge slip expected", "Chargeslip unavailable", "Unable to read the contents of chargeslip "
                                                                          "page. Receipt may not have loaded.")
    print("=======   CHARGE SLIP Validation Completed    =======")
    return {
        "fields_that_are_not_present": fields_that_are_not_present,
        "matching_fields": matching_fields,
        "unmatching_fields": unmatching_fields,
    }


# def run(playwright, receipt_url:str):
#     chromium = playwright.chromium
#     browser = chromium.launch(headless=False, slow_mo=1000)
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto(receipt_url)
#     GlobalVariables.portalDriver = page
#     # GlobalVariables.portalDriver.pause()

def validate_receipt_info_from_receipt_url(receipt_url: str, expected_details: dict, txn_id) -> bool:
    '''
    This function will validate the receipt info from the receipt url.\n
    It will return a boolean value indicating if the receipt info is matching with the expected receipt info.\n
    If the validation is failing it will try to take screenshot of the page and save it to the path specified in the screenshot_filepath.
    If there are issues in taking screenshot, it will log an exception.

    params:
        receipt_url: str
        expected_details: dict
        # screenshot_filepath: str
    return:
        validation_successful: bool

    '''
    # time.sleep(5)
    validation_successful = False
    print("##########")
    if receipt_url:
        present_receipt_info_ = None
        try:
            # driver = initialize_webdriver()
            # driver.get(receipt_url)
            # browser = playwright.firefox.launch(headless=False, slow_mo=1000)
            # print("##########")
            # context = browser.new_context()
            # page = context.new_page()
            # page.goto(receipt_url)
            # driver = page
            # with sync_playwright() as playwright:
            #     run(playwright, receipt_url)
            # driver = GlobalVariables.portalDriver
            if GlobalVariables.context == '':
                TestSuiteSetup.launch_browser_and_context_initialize()
            TestSuiteSetup.initialize_chargeslip_browser()
            GlobalVariables.charge_slip_page.goto(receipt_url)
            present_receipt_info_ = get_current_charge_slip_data_from_receipt_loaded_webdriver(GlobalVariables.charge_slip_page)
            results = compare_present_receipt_info_with_expected_receipt_info(present_receipt_info_, expected_details, txn_id, receipt_url)

            if results['fields_that_are_not_present']:

                logger.warning(
                    f"The following fields are not present in the Charge Slip: {', '.join(results['fields_that_are_not_present'])}")
            else:
                validation_successful = True

            if results['unmatching_fields']:
                logger.warning("Some fields are not matching")

                validation_successful = False

            # if take_screenshot is True:  # (take_screenshot is True) and (get_config("APIs", "screenshot_on_failure") == "True"):  # check type of bool also
            #     try:
            #         capture_ss_when_exe_failed(driver)
            #         # driver.save_screenshot(screenshot_filepath)
            #         # print(f"Screenshot saved at {screenshot_filepath}")
            #         # logger.warning(f"Screenshot saved at {screenshot_filepath}")
            #     except Exception as e:
            #         logger.exception(f"Screenshot-taking not done due to the following error: {e}")

            
            global_variables.charge_slip_driver = GlobalVariables.portalDriver
            # global_variables.charge_slip_driver = driver


        except ReceiptValidationError as e:
            print(e)
            logger.exception(f"Reciept Validation Error: {e}. Therefore Cannot proceed to validate", exc_info=True)

        except Exception as e:
            print(e)
            logger.exception(f"Error: {e}. Therefore Cannot proceed to validate", exc_info=True)

    else:
        print("No reciept url found")
        logger.warning("No reciept url found")

    return validation_successful


def get_json_response_of_txn_details(txn_id, username, password):
    env_base_url = get_config("APIs", "baseurl")
    url = f"{env_base_url}/api/2.0/txn/list"
    payload = json.dumps({"username": username, "password": password})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        json_response = response.json()
        json_response = [x for x in json_response["txns"] if x["txnId"] == txn_id][0]

    elif response.status_code == 500:
        raise TransactionAPIJsonResponseError(
            f"Unable to fetch txn details due to Interal Server Error \
                [{response.status_code}]\
                    . May be due to API server issue")
    else:
        raise TransactionAPIJsonResponseError(
            f"Unable to fetch txn details due to Error from reponse. \
                Response Code is [{response.status_code}]")
    return json_response


def validate_n_get_working_receipt_url(receipt_url_from_api):
    env_base_url = get_config("APIs", "baseurl")

    try:

        if env_base_url in receipt_url_from_api:
            print("API Fetched receipt URL is valid")
            logger.info("API Fetched receipt URL is valid")
            valid_receipt_url = receipt_url_from_api
        else:
            _, the_rest_part = receipt_url_from_api.split("//")
            split_parts = the_rest_part.split("/")  # ['d.eze.cc', 'r', 'o', 'eqq9jf3r', '']
            split_parts[0] = env_base_url
            valid_receipt_url = "/".join(split_parts)
            print("API Fetched receipt URL is invalid. It has been replaced with the valid base URL")
            logger.info("API Fetched receipt URL is invalid. It has been replaced with the valid base URL")
            print(f"Now using the valid receipt URL:", valid_receipt_url)
            logger.debug(f"Now using the valid receipt URL: {valid_receipt_url}")

    except Exception as e:
        logger.critical(f"Getting Valid Receipt URL Error: {e}")
        valid_receipt_url = None

    return valid_receipt_url


def get_txn_record_details(txn_id: str) -> pd.Series:
    query = f'select * from txn where id="{txn_id}"'
    result = get_value_from_db(query)

    if result.shape[0]:
        if result.shape[0] == 1:
            pass  # the pass takes out of the if section. in all other cases exceptions are raised
        else:
            print(f"it seems multiple rows are there for txn_id: {txn_id}")
            raise Exception(f"it seems multiple rows are there for txn_id: {txn_id}")
    else:
        print(f"No records found for the txn_id: {txn_id}")
        raise Exception(f"No records found for the txn_id: {txn_id}")

    txn_details_from_db = result.iloc[0]
    return txn_details_from_db


def get_acquirer_code_n_payment_gateway_from_txn_id(txn_id: str):
    txn_details_from_db = get_txn_record_details(txn_id)
    return dict(
        acquirer_code=txn_details_from_db['acquirer_code'],
        payment_gateway=txn_details_from_db['payment_gateway']
    )


def validate_logo_from_charge_slip(txn_id: str, url: str):
    banks_with_fiserv_ezetap_logo = {
        "ICICI": "FDC",
        "IDFC": "IDFC_FDC",
    }  # this could read of json file

    logger.info(f"Getting acquirer code and payment gateway information from DB for {txn_id}")
    acquirer_n_pg = get_acquirer_code_n_payment_gateway_from_txn_id(txn_id)
    acquirer = acquirer_n_pg['acquirer_code']
    pg = acquirer_n_pg['payment_gateway']

    if pg in banks_with_fiserv_ezetap_logo.values():
        ezetap_logo = 'fiserv.ezetap'
    else:
        ezetap_logo = 'ezetap'

    company_logo_valid, bank_logo_valid = charge_slip_validator.validate_chargeslip_image_logos_from_url(url,
                                                                                                         bank=acquirer,
                                                                                                         company=ezetap_logo,
                                                                                                         visualize=True)
    if company_logo_valid and bank_logo_valid:
        logger.info(f"Both Ezetap Logo and Bank Logo validations are successful")
    elif company_logo_valid:
        if company_logo_valid is True:
            logger.info(f"Ezetap Logo Validation is successful")
        elif company_logo_valid is False:
            logger.info(f"Ezetap Logo Validation is unsuccessful")
        else:
            logger.info(f"It seems no ezetap logo is found for txn_id '{txn_id}'")
    elif bank_logo_valid:
        if bank_logo_valid is True:
            logger.info(f"Bank Logo Validation is successful")
        elif bank_logo_valid is False:
            logger.info(f"Bank Logo Validation is unsuccessful")
        else:
            logger.info(f"It seems no Bank Logo is found for txn_id '{txn_id}'")
    else:
        logger.info(f"Both Ezetap Logo and Bank Logo validations are unsuccessful")

    # company_logo_valid, bank_logo_valid
    return all([company_logo_valid, bank_logo_valid])


def perform_charge_slip_validations(txn_id: str, credentials: dict, expected_details: dict):
    validation_sucessful = False

    # validation_list = []

    json_response = get_json_response_of_txn_details(**credentials, txn_id=txn_id)

    try:
        receipt_url_field = "receiptUrl"
        if receipt_url_field in json_response:
            logger.info(f"Receipt URL key('{receipt_url_field}') found from API response")
            receipt_url = json_response[
                receipt_url_field]  # check here and next lines if no url is found  -- issue from vineeth
            if receipt_url:
                valid_receipt_url = validate_n_get_working_receipt_url(receipt_url)
                print(f"valid_receipt_url : {valid_receipt_url}")
                if valid_receipt_url:
                    print("after valid receipt url")
                    logger.debug(valid_receipt_url)
                    print(valid_receipt_url)
                    validation_sucessful = validate_receipt_info_from_receipt_url(valid_receipt_url, expected_details,
                                                                                  txn_id)

                    # with sync_playwright() as playwright:
                    #     print("with with")
                    validation_sucessful = validate_receipt_info_from_receipt_url(valid_receipt_url, expected_details)
                else:
                    check.equal("Charge slip expected", "Charge slip unavailable", "Charge slip is not available.")
            else:
                logger.warning("Receipt URL value is empty. therefore unable to continue.")
                check.equal("Charge slip expected", "Charge slip unavailable", "Charge slip is not available.")
        else:
            logger.warning("Receipt url is not available.")
            check.equal("Charge slip expected", "Charge slip unavailable", "Charge slip is not available.")
    except Exception as e:
        logger.error(f"Unable to fetch receipt url from Error: {e}")
    if not global_variables.str_chargeslip_val_result == "Fail":
        global_variables.str_chargeslip_val_result = "Pass" if validation_sucessful else "Fail"
    return validation_sucessful

# playwright = sync_playwright()
# playwright.start()
#
# with sync_playwright() as playwright:
#     validate_receipt_info_from_receipt_url('https://dev16.ezetap.com/r/o/1bqwH2u9/',{}, playwright)
