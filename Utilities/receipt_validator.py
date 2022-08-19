import re
import requests
import json
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pytest_check as check

from Utilities.DBProcessor import get_value_from_db
from Utilities.ConfigReader import read_config as get_config
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
    datetime = "Date/Time:",
    signature_not_required_text = "SIGNATURE NOT REQUIRED",
    signature_not_available_text = 'SIGN: signature not available',
    customer_copy_text = "***** CUSTOMER COPY *****",
    version_found = "VERSION V-",
    merchant_ref_no_text = "Ref #",
    pin_verified_section_text = "PIN VERIFIED",
    agreement_text = """I agree to pay as per the card issuer agreement and receive chargeslip by electronic means.""",

)

present_receipt_info = {}
index_locations = {}
transaction_type = ['SALE', 'REVERSED', 'REFUND'] 
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
    for tr in section_rows:
        tds = tr.find_all('td')
        if len(tds) == 2:
            if ":" not in tds[1].text:
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
                    key_value_pair = td.text.strip().split(':')
                    # print(key_value_pair)
                    key = key_value_pair[0].strip()
                    value = key_value_pair[1].strip()
                    
                    present_receipt_info[key] = value


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
    possible_div_recipts = driver.find_elements(By.CLASS_NAME, 'receipt')
    if possible_div_recipts:
        l = possible_div_recipts[0]
        inner_html= driver.execute_script("return arguments[0].innerHTML;",l)
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
            
    merchant_text_fields = [", ".join([l.strip() for l in text.replace("\t", "").split("\n") if l.strip()]) for text in merchant_section_texts]

    # TO BE CHECKED LATER IF MORE OTHER FIELDS ARE AVAILABLE
    merchant_info = ", ".join(merchant_text_fields)
    present_receipt_info['merchant_info'] = merchant_info

def _get_present_receipt_info_from_receipt_table_n_post_table_sections(receipt_table):
    global present_receipt_info
    global index_locations
    global transaction_type  # transaction type
    # global mapped_identifier_keys_for_receipt_fields

    present_receipt_info = {}

    rows = receipt_table.find_all('tr')

    rows_with_fields = []
    for row in rows:
        # print(f"{i}".center(50, "-"))
        # print(row)
        tds = row.find_all('td')
        # if not tds:
        #     print_row = rows.pop(0) # here bank logo is also can be printed
        #     # pass
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
    receipt_table_middle_section_rows = rows_with_fields[(index_locations['datetime'] + 1): index_locations['payment_option']]
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
        if ('signature_section' not in indices) and (mapped_identifier_keys_for_receipt_fields['signature_not_available_text'] in paragraph.text):
            present_receipt_info['signature_not_available_text'] = paragraph.text.strip()
            if 'signature_section' in indices:
                print("over-writing the signature index")
            indices['signature_section'] = post_table_elements.index(paragraph)
        
        if mapped_identifier_keys_for_receipt_fields['agreement_text'] in paragraph.text:
            present_receipt_info['agreement_text'] = paragraph.text.strip()
            indices['agreement_section'] = post_table_elements.index(paragraph)

            # processing agreement text
            present_receipt_info['agreement_text'] = "\n".join([line.strip() for line in present_receipt_info['agreement_text'].replace("-", '').splitlines() if line.strip()])

    
    if 'customer_copy_text' in present_receipt_info:
        # cust_copy_text_lines includes customer copy text and version information
        cust_copy_text_lines = [line.strip() for line in present_receipt_info['customer_copy_text'].splitlines() if line.strip()]

        # finding version
        for line in cust_copy_text_lines:
            if mapped_identifier_keys_for_receipt_fields['customer_copy_text'] in line:
                present_receipt_info['customer_copy_text'] = line.strip()
            if mapped_identifier_keys_for_receipt_fields['version_found'] in line:
                present_receipt_info['version'] = line.strip()

    # finding pin verified text
    for para in post_table_elements[:indices['signature_section']]:
        if mapped_identifier_keys_for_receipt_fields['pin_verified_section_text'] in para.text:
            present_receipt_info['pin_verified_section_text'] = para.text.strip()
            break

    # getting unnamed_section extracted
    if ("agreement_section" in indices.keys()) and ("customer_copy" in indices.keys()):
        unnamed_sec_elements = post_table_elements[indices['signature_section'] + 1:indices['agreement_section']]
        unnamed_sec_elements_texts = [elem.text.strip() for elem in unnamed_sec_elements if elem.text.strip()]
        unnamed_section_text = [" ".join([i.strip() for i in w.split("  ") if i.strip()]) for w in unnamed_sec_elements_texts ]

        unnamed_section_text = " ".join(unnamed_section_text)

        if unnamed_section_text.strip():
            present_receipt_info['unnamed_section_text'] = unnamed_section_text.strip()

    elif ("signature_section" in indices.keys()) and ("customer_copy" in indices.keys()):
            unnamed_sec_elements = post_table_elements[indices['signature_section'] + 1:indices['customer_copy']]
            unnamed_sec_elements_texts = [elem.text.strip() for elem in unnamed_sec_elements if elem.text.strip()]
            unnamed_section_text = [" ".join([i.strip() for i in w.split("  ") if i.strip()]) for w in unnamed_sec_elements_texts ]

            unnamed_section_text = " ".join(unnamed_section_text)

            if unnamed_section_text.strip():
                present_receipt_info['unnamed_section_text'] = unnamed_section_text.strip()


    else:
        print("The customer copy or agreement section is not found! Therefore Unable to extract '[[ unnamed_section ]]'")
        logger.warning("The customer copy or agreement section is not found! Therefore Unable to extract '[[ unnamed_section ]]'")

    # global present_receipt_info
    
    logger.info("DETAILS THAT ARE FOUND IN CURRENT RECEIPT")
    logger.info(present_receipt_info)
    logger.info(100*"+")

    print("DETAILS THAT ARE FOUND IN CURRENT RECEIPT".center(100, "-"))
    print(present_receipt_info)
    print(100*"+")


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
            print("No receipt table [-----] inside charge slip found")  # go to logger
            print("Some part of the charge slip is not loaded")

    else:
        print("No receipt found")  # goes to loggger
        print("Charge Slip was not loaded!")

    return present_receipt_info


def compare_present_receipt_info_with_expected_receipt_info(present_details: dict, expected_details: dict) -> dict:
    print("=======   CHARGE SLIP Validation Started    =======")
    fields_that_are_not_present = set()
    matching_fields = set()
    unmatching_fields = set()

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
                    logger.debug(f"{key} found")
                    if expected_details[key] == present_details[key]:
                        matching_fields.add(key)
                        logger.debug(f"'{key}' is matching")
                    else:
                        unmatching_fields.add(key)
                        logger.debug(f"'{key}' is not matching")
                        check.equal(expected_details[key], present_details[key])
                else:
                    fields_that_are_not_present.add(key)
                    print(f"The field '{key}' not present")
                    logger.debug(f"The field '{key}' not present")
            Validator.print_validation_result(expected_details, present_details, matching_fields, unmatching_fields)

        else:
            print("No present receipt info found")
            logger.warning("No present receipt info found")
    print("=======   CHARGE SLIP Validation Completed    =======")
    return {
        "fields_that_are_not_present": fields_that_are_not_present,
        "matching_fields": matching_fields,
        "unmatching_fields": unmatching_fields,
    }


def validate_receipt_info_from_receipt_url(receipt_url: str, expected_details: dict) -> bool:
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

    validation_successful = False
    if receipt_url:
        present_receipt_info_ = None
        try:
            driver = initialize_webdriver()
            driver.get(receipt_url)
            present_receipt_info_ = get_current_charge_slip_data_from_receipt_loaded_webdriver(driver)
            results = compare_present_receipt_info_with_expected_receipt_info(present_receipt_info_, expected_details)

            if results['fields_that_are_not_present']:
        
                logger.warning(f"The following fields are not present in the Charge Slip: {', '.join(results['fields_that_are_not_present'])}")
            else: 
                validation_successful = True

            if results['unmatching_fields']:
                # print("Some fields are not matching")
                logger.warning("Some fields are not matching")
        
                # print("The following fields are not matching:", ", ".join(results['unmatching_fields']))
                validation_successful = False

            # if take_screenshot is True:  # (take_screenshot is True) and (get_config("APIs", "screenshot_on_failure") == "True"):  # check type of bool also
            #     try:
            #         capture_ss_when_exe_failed(driver)
            #         # driver.save_screenshot(screenshot_filepath)
            #         # print(f"Screenshot saved at {screenshot_filepath}")
            #         # logger.warning(f"Screenshot saved at {screenshot_filepath}")
            #     except Exception as e:
            #         logger.exception(f"Screenshot-taking not done due to the following error: {e}")

            
            global_variables.charge_slip_driver = driver


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
    url = f"{env_base_url}/api/2.0/txn/details"
    payload = json.dumps({"username": username, "password": password, "txnId": txn_id})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        json_response = response.json()
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


def perform_charge_slip_validations(txn_id:str, credentials:dict, expected_details:dict):
    validation_sucessful = False

    json_response = get_json_response_of_txn_details(**credentials, txn_id=txn_id)

    try:
        receipt_url_field = "receiptUrl"
        if receipt_url_field in json_response:
            logger.info(f"Receipt URL key('{receipt_url_field}') found from API response")
            receipt_url = json_response[receipt_url_field]  # check here and next lines if no url is found  -- issue from vineeth
            if receipt_url:
                valid_receipt_url = validate_n_get_working_receipt_url(receipt_url)
                if valid_receipt_url:
                    logger.debug(valid_receipt_url)
                    print(valid_receipt_url)
                    validation_sucessful = validate_receipt_info_from_receipt_url(valid_receipt_url, expected_details)
            else:
                logger.warning("Receipt URL value is empty. therefore unable to continue.")
        
    except Exception as e:
        logger.error(f"Unable to fetch receipt url from Error: {e}")
    if not global_variables.str_chargeslip_val_result == "Fail":
        global_variables.str_chargeslip_val_result = "Pass" if validation_sucessful else "Fail"
    return validation_sucessful
