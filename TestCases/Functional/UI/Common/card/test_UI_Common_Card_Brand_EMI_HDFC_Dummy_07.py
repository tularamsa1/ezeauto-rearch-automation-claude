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
def test_common_100_115_07_081():
    """
        Sub Feature Code: UI_Common_Card_Brand_EMI_Verify_EMI_Settings_Are_Inactive_For_Given_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
        Sub Feature Description: Verify emi settings are inactive for an given org (root or specific org) via HDFC Dummy PG using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand EMI, 081: TC081
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
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")

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

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        # Below function to update bank_code, bank for the bin: 417666
        testsuite_teardown.update_bin_info(bin_number='417666', bank_code='HDFC', bank='HDFC')

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        brand = result['brand'].values[0]
        logger.debug(f"Fetching brand from the emi table : {brand}")

        # disabling the eze emi plus
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand)

        query = f"select * from brand where id='{brand}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_id = result['id'].values[0]
        logger.debug(f"Fetching brand_id value from the brand table : {brand_id}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='INACTIVE')
        logger.debug(f"updated emi settings for {org_code} as inactive for credit card")
        testsuite_teardown.update_emi_status_for_root_org(root_org_code='EZETAP', card_type='CREDIT', status='INACTIVE', issuer_code=issuer_code, emi_type='BRAND')
        logger.debug(f"updated emi settings for EZETAP as inactive for credit card for {issuer_code}")
        testsuite_teardown.update_emi_status_for_root_org(root_org_code='EZETAP', card_type='CREDIT',status='INACTIVE', issuer_code=issuer_code, emi_type='NORMAL')
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
            amount = random.randint(3001, 4000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amount, order_id, device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is  : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            actual_no_emi_options = payment_page.fetch_error_msg_brand_emi()
            logger.info(f"No EMI options message is, {actual_no_emi_options}")

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
                expected_app_values = {
                    "no_emi_options": "No EMI Options available on this Card. Please try a different card."
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "no_emi_options": actual_no_emi_options
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
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
        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as inactive for credit card")
        testsuite_teardown.update_emi_status_for_root_org(root_org_code='EZETAP', card_type='CREDIT', status='ACTIVE', issuer_code=issuer_code, emi_type='BRAND')
        logger.debug(f"updated emi settings for EZETAP as inactive for credit card for {issuer_code}")
        testsuite_teardown.update_emi_status_for_root_org(root_org_code='EZETAP', card_type='CREDIT', status='ACTIVE', issuer_code=issuer_code, emi_type='NORMAL')
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_082():
    """
        Sub Feature Code: UI_Common_Card_Brand_EMI_Txn_Verification_When_EMI_Not_Enabled_In_Bin_Info_Table_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
        Sub Feature Description: Verify Brand transaction when emi is not enabled in the bin_info table for an org via HDFC Dummy PG using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand EMI, 082: TC082
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
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")

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

        query = f"update bin_info set emi_enabled= 0 where bin='417666' and bank_code='HDFC' and bank='HDFC' and payment_card_type= 'CREDIT' "
        logger.debug(f"Query to update bin_info for emi_enabled to INACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from bin_info for emi_enabled to INACTIVE : {result}")
        refresh_db()
        logger.debug(f"Refreshing the DB after updating the bin_info table: {result}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        brand = result['brand'].values[0]
        logger.debug(f"Fetching brand from the emi table : {brand}")

        # disabling the eze emi plus
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand)

        query = f"select * from brand where id='{brand}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_id = result['id'].values[0]
        logger.debug(f"Fetching brand_id value from the brand table : {brand_id}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
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
            amount = random.randint(3001, 4000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amount, order_id, device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is  : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            actual_no_emi_options = payment_page.fetch_error_msg_brand_emi()
            logger.info(f"No EMI options message is, {actual_no_emi_options}")

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
                expected_app_values = {
                    "no_emi_options": "EMI not supported on this Card. Please try a different card."
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "no_emi_options": actual_no_emi_options
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
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
        query = f"update bin_info set emi_enabled= 1 where bin='417666' and bank_code='HDFC' and bank='HDFC' and payment_card_type= 'CREDIT' "
        logger.debug(f"Query to update bin_info for emi_enabled to ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from bin_info for emi_enabled to ACTIVE : {result}")
        refresh_db()
        logger.debug(f"Refreshing the DB after reverting the bin_info table: {result}")

        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_083():
    """
        Sub Feature Code: UI_Common_Card_Brand_EMI_Txn_For_With_Card_When_Payment_Card_Type_UNKNOWN_In_DB_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
        Sub Feature Description: Verify brand transaction with card when payment card type is UNKNOWN in db for an org via HDFC Dummy PG using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand EMI, 083: TC083
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
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")

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

        query = f"update bin_info set payment_card_type= 'UNKNOWN' where bin = '417666' and bank_code = 'HDFC' and bank = 'HDFC'"
        logger.debug(f"Query to update bin_info for payment_card_type as UNKNOWN : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from bin_info for payment_card_type as UNKNOWN : {result}")
        refresh_db()
        logger.debug(f"Refreshing the DB after updating the bin_info table: {result}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        brand = result['brand'].values[0]
        logger.debug(f"Fetching brand from the emi table : {brand}")

        # disabling the eze emi plus
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand)

        query = f"select * from brand where id='{brand}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_id = result['id'].values[0]
        logger.debug(f"Fetching brand_id value from the brand table : {brand_id}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
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
            amount = random.randint(3001, 4000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amount, order_id, device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is  : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            actual_no_emi_options = payment_page.fetch_error_msg_brand_emi()
            logger.info(f"No EMI options message is, {actual_no_emi_options}")

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
                expected_app_values = {
                    "no_emi_options": "EMI not supported on this Card. Please try a different card."
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "no_emi_options": actual_no_emi_options
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
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

        query = f"update bin_info set payment_card_type= 'CREDIT' where bin = '417666' and bank_code = 'HDFC' and bank = 'HDFC'"
        logger.debug(f"Query to update bin_info for payment_card_type as CREDIT : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from bin_info for payment_card_type as CREDIT : {result}")
        refresh_db()
        logger.debug(f"Refreshing the DB after reverting the bin_info table: {result}")

        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_084():
    """
        Sub Feature Code: UI_Common_Card_Brand_EMI_Txn_For_With_Card_When_Payment_Card_Type_PREPAID_In_DB_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
        Sub Feature Description: Verify brand transaction with card when payment card type is PREPAID in db for an org via HDFC Dummy PG using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand EMI, 084: TC084
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

        query = f"update bin_info set payment_card_type = 'PREPAID' where bin = '417666' and bank_code = 'HDFC' and bank = 'HDFC'"
        logger.debug(f"Query to update bin_info for payment_card_type as PREPAID : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from bin_info for payment_card_type as PREPAID : {result}")
        refresh_db()
        logger.debug(f"Refreshing the DB after updating the bin_info table: {result}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        brand = result['brand'].values[0]
        logger.debug(f"Fetching brand from the emi table : {brand}")

        # disabling the eze emi plus
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand)

        query = f"select * from brand where id='{brand}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_id = result['id'].values[0]
        logger.debug(f"Fetching brand_id value from the brand table : {brand_id}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
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
            amount = random.randint(3001, 4000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amount, order_id, device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is  : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            actual_no_emi_options = payment_page.fetch_error_msg_brand_emi()
            logger.info(f"No EMI options message is, {actual_no_emi_options}")

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
                expected_app_values = {
                    "no_emi_options": "EMI not supported on this Card. Please try a different card."
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "no_emi_options": actual_no_emi_options
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
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
        query = f"update bin_info set payment_card_type = 'CREDIT' where bin = '417666' and bank_code = 'HDFC' and bank = 'HDFC'"
        logger.debug(f"Query to update bin_info for payment_card_type as CREDIT : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from bin_info for payment_card_type as CREDIT : {result}")
        refresh_db()
        logger.debug(f"Refreshing the DB after reverting the bin_info table: {result}")

        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_085():
    """
        Sub Feature Code: UI_Common_Card_Brand_EMI_Txn_For_Amount_Lesser_Than_EMI_Range_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
        Sub Feature Description: Verify the Brand EMI txn for amount lesser than the EMI range for an org via HDFC Dummy PG using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
        TC naming code description: 100: Payment Method, 115: C85: TC085
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
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")

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

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        brand = result['brand'].values[0]
        logger.debug(f"Fetching brand from the emi table : {brand}")
        brand_min_amount = result['min_amount'].values[0]
        logger.debug(f"Fetching min amount from the emi table : {brand_min_amount}")

        # disabling the eze emi plus
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand)

        query = f"select * from brand where id='{brand}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_id = result['id'].values[0]
        logger.debug(f"Fetching brand_id value from the brand table : {brand_id}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
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
            amount = int(brand_min_amount) - 100
            logger.info(f"Brand EMI minimum amount after subracting with 100, {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amount, order_id, device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is  : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            actual_no_emi_options = payment_page.fetch_error_msg_brand_emi()
            logger.info(f"No EMI options message is, {actual_no_emi_options}")

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
                expected_app_values = {
                    "no_emi_options": "Transaction Amount not eligible for EMI."
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "no_emi_options": actual_no_emi_options
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
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