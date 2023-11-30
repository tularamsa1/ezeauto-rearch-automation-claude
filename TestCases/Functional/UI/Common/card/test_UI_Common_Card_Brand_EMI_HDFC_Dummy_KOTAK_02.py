import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_card_page import CardPage
from PageFactory.sa.app_payment_page import PaymentPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_139():
    """
    Sub Feature Code: UI_Common_Card_Brand_EMI_Txn_EMI_Options_Not_Available_For_An_Org_HDFC_Dummy_Kotak_EMV_VISA_DebitCard_With_Pin_428090_For_3_Months_Tenure
    Sub Feature Description: Performing the brand EMI transaction when the EMI options are not available for an org (not ezetap) via HDFC
    Dummy PG for Kotak issuer using EMV VISA Debit card with pin for 3 months tenure (bin: 428090)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand_EMI, 139: TC139
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        query = f"select org_code from org_employee where username = {portal_username}"
        logger.debug(
            f"Query to fetch org_code from the org_employee table for portal username {portal_username} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        root_org_code = result['org_code'].values[0]
        logger.debug(
            f"Fetching org_code from the org_employee table for portal username {portal_username} : {root_org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid value from the terminal_info table : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid value from the terminal_info table : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id value from the terminal_info table : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        api_details["RequestBody"]["settings"]["brandEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["boCashbackEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi and bocashback is enabled in preconditions settings : {response}")

        # Below function to update bank_code, bank for the bin: 428090
        testsuite_teardown.update_bin_info(bin_number='428090', bank_code='KOTAK', bank='KOTAK')

        query = f"select bank_code from bin_info where bin='428090'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='DEBIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as inactive for debit card")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='DEBIT', status='INACTIVE')
        logger.debug(f"updated emi settings for {org_code} as inactive for debit card")
        testsuite_teardown.update_emi_status_for_root_org(root_org_code=root_org_code, card_type='DEBIT',
                                                          status='INACTIVE', issuer_code=issuer_code, emi_type='BRAND')
        logger.debug(f"updated emi settings for {root_org_code} as inactive for debit card for {issuer_code}")
        testsuite_teardown.update_emi_status_for_root_org(root_org_code=root_org_code, card_type='DEBIT',
                                                          status='INACTIVE', issuer_code=issuer_code, emi_type='NORMAL')
        logger.debug(f"updated emi settings for {root_org_code} as inactive for debit card for {issuer_code}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='KOTAK' and card_type='DEBIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        interest_rate = result['interest_rate'].values[0]
        logger.debug(f"Fetching interest_rate from the emi table : {interest_rate}")
        term = result['term'].values[0]
        logger.debug(f"Fetching term from the emi table : {term}")
        scheme_code = result['scheme_code'].values[0]
        logger.debug(f"Fetching scheme_code from the emi table : {scheme_code}")
        brand_id = result['brand'].values[0]
        logger.debug(f"Fetching brand_id from the emi table : {brand_id}")

        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand_id)

        query = f"select * from brand where id='{brand_id}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")
        brand_sku_category = result['sku_category'].values[0]
        logger.debug(f"Fetching sku_category value from the brand_sku_details table : {brand_sku_category}")
        brand_sku_code = result['sku_code'].values[0]
        logger.debug(f"Fetching sku_code value from the brand_sku_details table : {brand_sku_code}")

        query = f"select * from subvention_plan where brand_id='{brand_id}' and org_code='{org_code}' and card_type= 'DEBIT' and bank='KOTAK' and eze_emi_enabled=b'0' order by created_time desc limit 1;"
        logger.debug(f"Query to fetch data from the subvention_plan table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan table : {result}")
        subvention_plan_id = result['id'].values[0]
        logger.debug(f"Fetching subvention_id from subvention_plan table : {subvention_plan_id}")
        subvention_plan_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from subvention_plan table : {subvention_plan_org_code}")
        subvention_plan_brand_id = result['brand_id'].values[0]
        logger.debug(f"Fetching brand_id from subvention_plan table : {subvention_plan_brand_id}")
        subvention_plan_card_type = result['card_type'].values[0]
        logger.debug(f"Fetching card_type from subvention_plan table : {subvention_plan_card_type}")
        subvention_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_scheme_name}")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity ='BRAND' and subvention_value_type= 'FIXED' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month' ;"
        logger.debug(f"Query to fetch data from the subvention_plan_details table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan_details table : {result}")
        subvention_entity = result['subventing_entity'].values[0]
        logger.debug(f"Fetching subventing_entity from subvention_plan_details table : {subvention_entity}")
        subvention_type = result['subvention_type'].values[0]
        logger.debug(f"Fetching subvention_type from subvention_plan_details table : {subvention_type}")
        subvention_value_type = result['subvention_value_type'].values[0]
        logger.debug(f"Fetching subvention_value_type from subvention_plan_details table : {subvention_value_type}")
        subvention_value = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value from subvention_plan_details table : {subvention_value}")
        subvention_tenure = result['tenure'].values[0]
        logger.debug(f"Fetching tenure from subvention_plan_details table : {subvention_tenure}")
        subvention_discount_type = result['discount_type'].values[0]
        logger.debug(f"Fetching discount_type from subvention_plan_details table : {subvention_discount_type}")

        # updating the status as inactive in subvention_plan_details table
        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity='BRAND' and subvention_type='PAYBACK' and subvention_value_type='FIXED' and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(4000, 5000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(prod=brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei=imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_DEBIT_428090")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            error_msg = payment_page.fetch_error_msg_brand_emi()

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------

        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of App Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_app_values = {
                    "err_msg": "No EMI Options available on this Card. Please try a different card."
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "err_msg": error_msg
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------

    finally:
        try:
            testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='DEBIT', status='ACTIVE')
            logger.debug(f"updated emi settings for {org_code} as inactive for debit card")
            testsuite_teardown.update_emi_status_for_root_org(root_org_code=root_org_code, card_type='DEBIT',
                                                              status='ACTIVE', issuer_code=issuer_code, emi_type='BRAND')
            logger.debug(f"updated emi settings for {root_org_code} as active for debit card for {issuer_code}")
            testsuite_teardown.update_emi_status_for_root_org(root_org_code=root_org_code, card_type='DEBIT',
                                                              status='ACTIVE', issuer_code=issuer_code, emi_type='NORMAL')
            logger.debug(f"updated emi settings for {root_org_code} as active for debit card for {issuer_code}")
        except Exception as e:
            logger.exception(f"Query updation failed due to expection : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_140():
    """
    Sub Feature Code: UI_Common_Card_Brand_EMI_Txn_ICICI_Debit_Issuer_Not_Enabled_In_Org_Settings_For_An_Org_HDFC_Dummy_Kotak_EMV_VISA_DebitCard_With_Pin_428090_For_3_Months_Tenure
    Sub Feature Description: Performing the brand EMI transaction when ICICI debit issuer is not enabled in the org settings for an org (not ezetap) via HDFC
    Dummy PG for Kotak issuer using EMV VISA Debit card with pin for 3 months tenure (bin: 428090)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand_EMI, 140: TC140
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid value from the terminal_info table : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid value from the terminal_info table : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id value from the terminal_info table : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        api_details["RequestBody"]["settings"]["brandEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["boCashbackEnabled"] = "true"
        api_details["RequestBody"]["settings"]["enabledEmiIssuerBanks"] = "{\"HDFC\":\"DEBIT\",\"AXIS\":\"DEBIT\"," \
                                                                          "\"ICICI\":\"DEBIT\"}"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi and bocashback is enabled in preconditions settings : {response}")

        # Below function to update bank_code, bank for the bin: 428090
        testsuite_teardown.update_bin_info(bin_number='428090', bank_code='KOTAK', bank='KOTAK')

        query = f"select bank_code from bin_info where bin='428090'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='DEBIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as inactive for debit card")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='KOTAK' and card_type='DEBIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        interest_rate = result['interest_rate'].values[0]
        logger.debug(f"Fetching interest_rate from the emi table : {interest_rate}")
        term = result['term'].values[0]
        logger.debug(f"Fetching term from the emi table : {term}")
        scheme_code = result['scheme_code'].values[0]
        logger.debug(f"Fetching scheme_code from the emi table : {scheme_code}")
        brand_id = result['brand'].values[0]
        logger.debug(f"Fetching brand_id from the emi table : {brand_id}")

        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand_id)

        query = f"select * from brand where id='{brand_id}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")
        brand_sku_category = result['sku_category'].values[0]
        logger.debug(f"Fetching sku_category value from the brand_sku_details table : {brand_sku_category}")
        brand_sku_code = result['sku_code'].values[0]
        logger.debug(f"Fetching sku_code value from the brand_sku_details table : {brand_sku_code}")

        query = f"select * from subvention_plan where brand_id='{brand_id}' and org_code='{org_code}' and card_type= 'DEBIT' and bank='KOTAK' and eze_emi_enabled=b'0' order by created_time desc limit 1;"
        logger.debug(f"Query to fetch data from the subvention_plan table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan table : {result}")
        subvention_plan_id = result['id'].values[0]
        logger.debug(f"Fetching subvention_id from subvention_plan table : {subvention_plan_id}")
        subvention_plan_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from subvention_plan table : {subvention_plan_org_code}")
        subvention_plan_brand_id = result['brand_id'].values[0]
        logger.debug(f"Fetching brand_id from subvention_plan table : {subvention_plan_brand_id}")
        subvention_plan_card_type = result['card_type'].values[0]
        logger.debug(f"Fetching card_type from subvention_plan table : {subvention_plan_card_type}")
        subvention_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_scheme_name}")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity ='BRAND' and subvention_value_type= 'FIXED' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month' ;"
        logger.debug(f"Query to fetch data from the subvention_plan_details table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan_details table : {result}")
        subvention_entity = result['subventing_entity'].values[0]
        logger.debug(f"Fetching subventing_entity from subvention_plan_details table : {subvention_entity}")
        subvention_type = result['subvention_type'].values[0]
        logger.debug(f"Fetching subvention_type from subvention_plan_details table : {subvention_type}")
        subvention_value_type = result['subvention_value_type'].values[0]
        logger.debug(f"Fetching subvention_value_type from subvention_plan_details table : {subvention_value_type}")
        subvention_value = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value from subvention_plan_details table : {subvention_value}")
        subvention_tenure = result['tenure'].values[0]
        logger.debug(f"Fetching tenure from subvention_plan_details table : {subvention_tenure}")
        subvention_discount_type = result['discount_type'].values[0]
        logger.debug(f"Fetching discount_type from subvention_plan_details table : {subvention_discount_type}")

        # updating the status as inactive in subvention_plan_details table
        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity='BRAND' and subvention_type='PAYBACK' and subvention_value_type='FIXED' and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(4000, 5000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(prod=brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei=imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_DEBIT_428090")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            error_msg = payment_page.fetch_error_msg_brand_emi()

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------

        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of App Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_app_values = {
                    "err_msg": "Card Not Supported for EMI. Please try a different card"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "err_msg": error_msg
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_141():
    """
    Sub Feature Code: UI_Common_Card_Brand_EMI_Txn_EMI_Not_Enabled_Bin_Info_Level_For_An_Org_HDFC_Dummy_Kotak_EMV_VISA_DebitCard_With_Pin_428090_For_3_Months_Tenure
    Sub Feature Description: Performing the brand EMI transaction when EMI is not enabled at the bin_info level for an org (not ezetap) via HDFC
    Dummy PG for Kotak issuer using EMV VISA Debit card with pin for 3 months tenure (bin: 428090)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand_EMI, 141: TC141
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid value from the terminal_info table : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid value from the terminal_info table : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id value from the terminal_info table : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        api_details["RequestBody"]["settings"]["brandEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["boCashbackEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi and bocashback is enabled in preconditions settings : {response}")

        # Below function to update bank_code, bank for the bin: 428090
        testsuite_teardown.update_bin_info(bin_number='428090', bank_code='KOTAK', bank='KOTAK')

        query = f"select bank_code from bin_info where bin='428090'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        query = f"update bin_info set emi_enabled=b'0' where bin='428090';"
        logger.debug(f"Query to update bin_info table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")
        refresh_db()
        logger.debug(f"Database refreshed")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='DEBIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for debit card")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='KOTAK' and card_type='DEBIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        interest_rate = result['interest_rate'].values[0]
        logger.debug(f"Fetching interest_rate from the emi table : {interest_rate}")
        term = result['term'].values[0]
        logger.debug(f"Fetching term from the emi table : {term}")
        scheme_code = result['scheme_code'].values[0]
        logger.debug(f"Fetching scheme_code from the emi table : {scheme_code}")
        brand_id = result['brand'].values[0]
        logger.debug(f"Fetching brand_id from the emi table : {brand_id}")

        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand_id)

        query = f"select * from brand where id='{brand_id}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")
        brand_sku_category = result['sku_category'].values[0]
        logger.debug(f"Fetching sku_category value from the brand_sku_details table : {brand_sku_category}")
        brand_sku_code = result['sku_code'].values[0]
        logger.debug(f"Fetching sku_code value from the brand_sku_details table : {brand_sku_code}")

        query = f"select * from subvention_plan where brand_id='{brand_id}' and org_code='{org_code}' and card_type= 'DEBIT' and bank='KOTAK' and eze_emi_enabled=b'0' order by created_time desc limit 1;"
        logger.debug(f"Query to fetch data from the subvention_plan table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan table : {result}")
        subvention_plan_id = result['id'].values[0]
        logger.debug(f"Fetching subvention_id from subvention_plan table : {subvention_plan_id}")
        subvention_plan_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from subvention_plan table : {subvention_plan_org_code}")
        subvention_plan_brand_id = result['brand_id'].values[0]
        logger.debug(f"Fetching brand_id from subvention_plan table : {subvention_plan_brand_id}")
        subvention_plan_card_type = result['card_type'].values[0]
        logger.debug(f"Fetching card_type from subvention_plan table : {subvention_plan_card_type}")
        subvention_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_scheme_name}")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity ='BRAND' and subvention_value_type= 'FIXED' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month' ;"
        logger.debug(f"Query to fetch data from the subvention_plan_details table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan_details table : {result}")
        subvention_entity = result['subventing_entity'].values[0]
        logger.debug(f"Fetching subventing_entity from subvention_plan_details table : {subvention_entity}")
        subvention_type = result['subvention_type'].values[0]
        logger.debug(f"Fetching subvention_type from subvention_plan_details table : {subvention_type}")
        subvention_value_type = result['subvention_value_type'].values[0]
        logger.debug(f"Fetching subvention_value_type from subvention_plan_details table : {subvention_value_type}")
        subvention_value = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value from subvention_plan_details table : {subvention_value}")
        subvention_tenure = result['tenure'].values[0]
        logger.debug(f"Fetching tenure from subvention_plan_details table : {subvention_tenure}")
        subvention_discount_type = result['discount_type'].values[0]
        logger.debug(f"Fetching discount_type from subvention_plan_details table : {subvention_discount_type}")

        # updating the status as inactive in subvention_plan_details table
        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity='BRAND' and subvention_type='PAYBACK' and subvention_value_type='FIXED' and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(4000, 5000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(prod=brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei=imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_DEBIT_428090")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            error_msg = payment_page.fetch_error_msg_brand_emi()

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------

        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of App Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_app_values = {
                    "err_msg": "EMI not supported on this Card. Please try a different card."
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "err_msg": error_msg
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------

    finally:
        try:
            query = f"update bin_info set emi_enabled=b'1' where bin='428090';"
            logger.debug(f"Query to update bin_info table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
            refresh_db()
            logger.debug(f"Database refreshed")
        except Exception as e:
            logger.exception(f"Query updation failed due to expection : {e}")
        Configuration.executeFinallyBlock(testcase_id)