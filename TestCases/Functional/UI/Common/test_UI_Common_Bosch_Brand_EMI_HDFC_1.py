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
@pytest.mark.dbVal
def test_common_100_115_07_158():
    """
        Sub Feature Code:- UI_Common_Verify_Products_in_Brand_Sku_Details_Table.
        Sub Feature Description:Performing the verification if the products are correctly recorded in the database.
        TC naming code description: 100: Payment Method, 115: CARD_UI, 07: BRAND_EMI, 158: TC158
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        api_details["RequestBody"]["settings"]["brandEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["brandEmiSettings"] = '{"Bosch": ""}'
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        query = f"select id from brand where brand_name='Bosch';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_id = result['id'].values[0]
        logger.debug(f"brand_id for org_employee table is : {brand_id}")

        testsuite_teardown.update_product_details(brand_id)

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = f"select b.id, bs.sku_code, bs.sku_name from brand b join brand_sku_details bs on b.id = bs.brand_id where b.brand_name ='bosch';"
            logger.debug(f"Query to fetch data from the brand and brand_sku_details tables: {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result for brand and brand_sku_details tables: {result}")
            sku_code_list = result['sku_code'].tolist()
            logger.debug(f"SKU codes for products are: {sku_code_list}")

            bosch_sku_list = {'BEL553MS0I','CMC33S05NI','DWKA98G60I','DWS97BA62I','EC9A5RB90I','GI81NAE31I','HBF113BR0Z','PNH6B6F10I','SMS6HVI00I','WLJ20161IN','WOE653D0IN','WOE703S0IN','WT44B202IN'}
            logger.debug(f"list of pre define sku code for bosch brand are {bosch_sku_list}")
            result_sku_code = testsuite_teardown.check_sku_code(sku_code_list, bosch_sku_list)
            logger.debug(f"Verified result is:'{result_sku_code}'")

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
        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "result": "Verified, Product is available in brand_sku_details table"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")
                actual_db_values = {
                    "result": result_sku_code
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation------------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_115_07_153():
    """
        Sub Feature Code:- UI_Common_Verify_Brand_Name_in_Database
        Sub Feature Description: Performing the verification if the Bosch brand name is correctly recorded in the database.
        TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand EMI, 153: TC153
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            query = f"select * from brand where brand_name='bosch'"
            logger.debug(f"Query to fetch data from the brand table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result for brand table : {result}")
            brand_name = result['brand_name'].values[0]
            logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")
            status = result['status'].values[0]
            logger.debug(f"Fetching brand_name value from the brand table : {status}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------
        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "brand_name": 'Bosch',
                    "status" : b'\x01'
                }
                logger.debug(f"expected_db_values: {expected_db_values}")
                actual_db_values = {
                    "brand_name": brand_name,
                    "status": status
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation------------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_165():
    """
    Sub Feature Code: - UI_Common_Check_Invalid_Product_Range
    Sub Feature Description: Validate "Invalid Product in the range-" error message by Performing a Brand EMI
    transaction with Min and max amount  via HDFC-HDFC using EMV VISA Credit card with pin(bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: BRAND_EMI, 165: TC165
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"fetching org code from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='HDFC' "
        logger.debug(f"Query to fetch data from the terminal_info table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        api_details["RequestBody"]["settings"]["brandEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["brandEmiSettings"] = '{"Bosch": ""}'
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        sku_code = 'HBF113BR0Z'
        query = (f"select b.*, bs.* from brand b join brand_sku_details bs on b.id = bs.brand_id where b.brand_name = 'Bosch' and"
                 f" b.status = 1 and bs.sku_code = '{sku_code}' order by b.created_time desc, bs.created_time desc limit 1;")
        logger.debug(f"Query to fetch data from the brand_sku_details table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for brand_sku_details table : {result}")
        product_name = result["sku_name"].iloc[0]
        logger.debug(f"Fetching product_name from the brand_sku_details table: {product_name}")
        min_amount = result["min_amount"].iloc[0]
        logger.debug(f"Fetching min_amount from the brand_sku_details table: {min_amount}")
        max_amount = result["max_amount"].iloc[0]
        logger.debug(f"Fetching max_amount from the brand_sku_details table: {max_amount}")
        brand_id = result["id"].iloc[0]
        logger.debug(f"Fetching brand_id from the brand table : {brand_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, middlewareLog=False, q2_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(2000, 3000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)

            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.info(f"Selected payment mode is Brand EMI")
            payment_page.click_on_bosch_brand()
            logger.info(f"Selected Brand as Bosch")
            logger.info(f"searching for product by clicking search icon")
            payment_page.click_and_enter_search_products_or_brands(product_name)
            logger.info(f"Enter the Product")
            error_min = payment_page.fetch_min_amount_error()
            logger.debug(f"error message for minimum value is {error_min} ")

            app_driver.reset()
            amount_max = random.randint(99000, 99500)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username for second time: {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount_max, order_number=order_id,
                                                                               device_serial=device_serial)
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.info(f"Selected payment mode is Brand EMI")
            payment_page.click_on_bosch_brand()
            logger.info(f"Selected Brand as Bosch")
            logger.info(f"searching for product by clicking search icon")
            payment_page.click_and_enter_search_products_or_brands(product_name)
            logger.info(f"Entered the Product, '{product_name}")
            error_max = payment_page.fetch_min_amount_error()
            logger.debug(f"error message for maximum value is: {error_max} ")
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------)
                expected_app_values = {
                    "error_min": f"Invalid Product in the range ¤ {'{:,.2f}'.format(min_amount)} to ¤ {'{:,.2f}'.format(max_amount)}",
                    "error_max": f"Invalid Product in the range ¤ {'{:,.2f}'.format(min_amount)} to ¤ {'{:,.2f}'.format(max_amount)}",
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "error_min": error_min,
                    "error_max": error_max
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_168():
    """
    Sub Feature Code: UI_Common_Check_Minimum_and_Maximum_EMI_Eligibility_EMV_VISA_DebitCard_With_Pin_428090_at_merchant_level
    Sub Feature Description: Verify Error Message For Minimum and Maximum Emi Eligibility at Merchant level  via HDFC-HDFC using EMV VISA Debit Card(bin: 428090)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: BRAND_EMI, 168: TC168
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"fetching org code from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='HDFC' "
        logger.debug(f"Query to fetch data from the terminal_info table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        api_details["RequestBody"]["settings"]["brandEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["brandEmiSettings"] = '{"Bosch": ""}'

        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        sku_code = 'HBF113BR0Z'
        imei_code = '00510419102091003125'

        query = f"select b.id, bs.sku_name, bs.min_amount, bs.max_amount from brand b join brand_sku_details bs on b.id = bs.brand_id where b.brand_name = 'Bosch' and b.status = 1 and bs.sku_code = '{sku_code}' order by b.created_time desc, bs.created_time desc limit 1;"
        logger.debug(f"Query to fetch data from the brand_sku_details table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for brand_sku_details table : {result}")
        min_amount_product = result["min_amount"].iloc[0]
        logger.debug(f"Fetching min_amount from the brand_sku_details table : min_amount_product : {min_amount_product}")
        max_amount_product = result["max_amount"].iloc[0]
        logger.debug(f"Fetching max_amount from the brand_sku_details table : max_amount : {max_amount_product}")
        product_name = result["sku_name"].iloc[0]
        logger.debug(f"Fetching max_amount from the brand_sku_details table : sku_name_product : {product_name}")
        brand_id = result["id"].iloc[0]
        logger.debug(f"Fetching brand_id from the brand table : brand_id : {brand_id}")

        query = f"update brand_sku_details set min_amount = '{float(min_amount_product) -1000}' where brand_id = {brand_id} and sku_name ='{product_name}';"
        logger.debug(f"Query to fetch data from the brand_sku_details table for the {org_code} : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.info(f"RESULT of updating brand_sku_details table: {result}")

        refresh_db()
        logger.info(f"DB refreshed")

        query = f"select * from brand_sku_details where brand_id ='{brand_id}' and sku_name = '{product_name}';"
        logger.debug(f"Query to fetch data from the brand_sku_details table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for brand_sku_details table : {result}")
        min_amount_updated = result["min_amount"].iloc[0]
        logger.debug(f"Fetching updated min_amount from the brand_sku_details table for the product '{product_name}': {min_amount_updated}")

        testsuite_teardown.update_emi_status_for_a_brand(org_code, 'DEBIT', 'ACTIVE', brand_id)

        query = (f"select * from emi where org_code = '{org_code}' and term = '3 month' and brand = '{brand_id}' and "
                 f"card_type ='DEBIT' and issuer_code = 'HDFC' and emi_type = 'BRAND' and tid_type = 'SUBVENTION' and"
                 f" status ='ACTIVE' order by created_time desc limit 1;")
        logger.debug(f"Query to fetch data from the emi table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for brand_sku_details table : {result}")
        min_amount_emi = result["min_amount"].iloc[0]
        logger.debug(f"Fetching min_amount from the emi table : min_amount : {min_amount_emi}")
        max_amount_emi = result["max_amount"].iloc[0]
        logger.debug(f"Fetching max_amount from the emi table : max_amount : {max_amount_emi}")

        #Unblocking imei code
        api_details = DBProcessor.get_api_details('unblock_imei', request_body={
            "MATERIAL_CODE": sku_code,
            "IMEI_CODE": imei_code,
            "DATE_TIME": "20052024",
            "STATUS": "2"
        })
        response = APIProcessor.send_request_non_dev(api_details)
        logger.debug(f"Response received from unblock_imei api:  {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, middlewareLog=False, q2_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(min_amount_updated, min_amount_emi)
            logger.debug(f'Randomly generated amount is {amount}')
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)

            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.info(f"Selected payment mode is Brand EMI")
            payment_page.click_on_bosch_brand()
            logger.info(f"Selected Brand as Bosch")
            logger.info(f"searching for product by clicking search icon")
            payment_page.click_and_enter_search_products_or_brands(product_name)
            logger.info(f"Enter the Product")
            payment_page.click_and_enter_imei_no(imei_code)
            logger.info(f"Enter the IMEI number")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_DEBIT_428090")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            error = payment_page.fetch_min_amount_error()
            logger.debug(f"error  is {error} ")
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------)
                expected_app_values = {
                    "error": "Transaction Amount not eligible for EMI.",
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "error": error,
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            query = f"update brand_sku_details set min_amount = '{float(min_amount_updated) + 1000}' where brand_id = {brand_id} and sku_name ='{product_name}';"
            logger.debug(f"Query to fetch data from the brand_sku_details table for the {org_code} : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.info(f"result of updating brand_sku_details table: {result}")
            refresh_db()
            logger.info(f"DB refreshed")
        except Exception as e:
            logger.exception(f"Not able to revert brand_sku_details : {e}")
        Configuration.executeFinallyBlock(testcase_id)