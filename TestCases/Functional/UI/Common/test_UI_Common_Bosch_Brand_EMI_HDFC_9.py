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
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.mpos.app_base_page import BasePage
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, Validator, date_time_converter, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger



logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_200():
    """
    Sub Feature Code: UI_Common_Check_Bosch_Brand_Visibility_in_MPOS
    Sub Feature Description: Verify that the Bosch brand is not reflected in the MPOS app and is not displayed in the select product screen when it is disabled at org level
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand_EMI, 200: TC200
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

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and acquirer_code='HDFC' and payment_gateway='HDFC' "
        logger.debug(f"Query to fetch data from the terminal_info table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for terminal_info table : {result}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

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
        api_details["RequestBody"]["settings"]["brandEmiSettings"] = '{}'
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when brand_emi is disabled in preconditions settings : {response}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for credit card")
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
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(3001, 4000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.info(f"Selected payment mode is Brand EMI")
            logger.debug(f"Check for bosch brand option")
            try:
                payment_page.is_bosch_brand_visible()
                logger.debug(f"Bosch brand option is invisible")
                bosch_brand = "Feature invisible"
            except:
                logger.debug(f"Brand emi option is still visible")
                bosch_brand = "Feature is visible"

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                expected_app_values = {
                    "brand_emi_btn": "Feature invisible"
                }
                actual_app_values = {
                    "brand_emi_btn": bosch_brand
                }
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        try:
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["brandEmiSettings"] = '{"Bosch": ""}'
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(
                f"Response received for resetting preconditions settings : {response}")
        except Exception as e:
            logger.exception(f"Not able to unmap due to : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_197():
    """
    Sub Feature Code:  UI_Common_Disable_Brand_EMI_in_Org_Settings
    Sub Feature Description: Disable the brand EMI at org and verify that the brand EMI option is not displayed in the universal pay screen under affordability.
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand_EMI, 197: TC197
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

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and acquirer_code='HDFC' and payment_gateway='HDFC' "
        logger.debug(f"Query to fetch data from the terminal_info table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for terminal_info table : {result}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

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
        api_details["RequestBody"]["settings"]["brandEmiEnabled"] = "False"
        api_details["RequestBody"]["settings"]["brandEmiSettings"] = '{"Bosch": ""}'
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when brand_emi is disabled in preconditions settings : {response}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for credit card")
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
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(3001, 4000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            logger.debug(f"Check for brand emi option")
            try:
                payment_page.is_brand_emi_pmt_mode_visible()
                logger.debug(f"Brand emi option is invisible")
                brand_emi = "Feature invisible"
            except:
                logger.debug(f"Brand emi option is still visible")
                brand_emi = "Feature is visible"
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                expected_app_values = {
                    "brand_emi_btn": "Feature invisible"
                }
                actual_app_values = {
                    "brand_emi_btn": brand_emi
                }
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        try:
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["brandEmiEnabled"] = "true"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(
                f"Response received for resetting preconditions settings : {response}")

        except Exception as e:
            logger.exception(f"Not able to unmap due to : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_205():
    """
    Sub Feature Code: -  UI_Common_Check_Success_Transaction_Message_in_MySQLDB
    Sub Feature Description: Verify the Successful message for a valid IMEI number under the brand_validation table in the MySQL
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: BRAND_EMI, 205: TC205
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
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")

        sku_code = 'HBF113BR0Z'
        imei_code = '00510419102091003125'
        query = (f"select b.id, bs.sku_name from brand b join brand_sku_details bs on b.id = bs.brand_id where"
                 f" b.brand_name = 'Bosch' and b.status = 1 and bs.sku_code = '{sku_code}' order by b.created_time desc,"
                 f" bs.created_time desc limit 1;")
        logger.debug(f"Query to fetch data from the brand_sku_details table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for brand_sku_details table : {result}")
        product_name = result["sku_name"].iloc[0]
        logger.debug(f"Fetching product_name from the brand_sku_details table: {product_name}")
        brand_id = result["id"].iloc[0]
        logger.debug(f"Fetching brand_id from the brand table : brand_id : {brand_id}")

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
        #unblocking imei code
        api_details = DBProcessor.get_api_details('unblock_imei', request_body={
            "MATERIAL_CODE": sku_code,
            "IMEI_CODE": imei_code,
            "DATE_TIME": "20052024",
            "STATUS": "2"
        })
        response = APIProcessor.send_request_non_dev(api_details)
        logger.debug(f"Response received from unblock_imei api:  {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for credit card")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(3000, 4000)
            emi_plan_in_months = 6
            logger.debug(f"product name is : {product_name}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")
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
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.info(f"Selected payment mode is Brand EMI")
            logger.info(f"Select Brand as Bosch")
            payment_page.click_on_bosch_brand()
            logger.info(f"searching for product by clicking search icon")
            payment_page.click_and_enter_search_products_or_brands(product_name)
            logger.info(f"{product_name} : is being selected as product")
            payment_page.click_and_enter_imei_no(imei_code)
            logger.info(f"Enter the IMEI number")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"Selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            txn_id = result['id'].values[0]

            query = f"select * from brand_validation where org_code ='{org_code}' and brand_id ={brand_id} order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the brand table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result for brand table : {result}")
            error_message = result['error_message'].values[0]
            logger.debug(f"Fetching error_message value from the brand_validation table : {error_message}")
            error_code = result['error_code'].values[0]
            logger.debug(f"Fetching error_code value from the brand_validation table : {error_code}")
            status = result['status'].values[0]
            logger.debug(f"Fetching status value from the brand_validation table : {status}")
            brand_name = result['brand_name'].values[0]
            logger.debug(f"Fetching brand_name value from the brand_validation table : {status}")
            offer_type = result['offer_type'].values[0]
            logger.debug(f"Fetching error_code value from the brand_validation table : {offer_type}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the brand_validation table : {device_serial_db}")
            brand_emi_post_status = result['brand_emi_post_status'].values[0]
            logger.debug(f"Fetching error_code value from the brand_validation table : {brand_emi_post_status}")
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -------------------------------- ---------End of Test Execution--------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_app_values = {
                    "status": "SUCCESS",
                    "brand_name":'Bosch',
                    "offer_type": 'BRAND_EMI',
                    "device_serial" : device_serial,
                    "brand_emi_post_status": 'BLOCKED'
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "status": status,
                    "brand_name": brand_name,
                    "offer_type": offer_type,
                    "device_serial": device_serial_db,
                    "brand_emi_post_status": brand_emi_post_status
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
            api_details = DBProcessor.get_api_details('Void/Reversal_Card_Txn', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": txn_id,
            })
            logger.debug(f"api details are {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Reversal_Card_Txn api:  {response}")
        except Exception as e:
            logger.exception(f"Unbale to void txn due to : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_204():
    """
    Sub Feature Code: UI_Common_Check_Error_Message_for_Invalid_IMEI_in_MySQLDB
    Sub Feature Description: Verify the error message for an invalid IMEI number under the brand_validation table in the MySQL
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: BRAND_EMI, 204: TC204
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
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")

        query = (f"select b.id, bs.sku_code, bs.sku_name from brand b join brand_sku_details bs on b.id = bs.brand_id"
                 f" where b.brand_name ='bosch' and  bs.sku_code ='INVALID';")
        logger.debug(f"Query to fetch data from the brand_sku_details table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for brand_sku_details and brand table : {result}")
        product_name = result["sku_name"].iloc[0]
        logger.debug(f"Fetching product_name from the brand_sku_details table: {product_name}")
        brand_id = result["id"].iloc[0]
        logger.debug(f"Fetching brand_id from the brand table: {brand_id}")
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

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for credit card")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(3000, 4000)
            invalid_imei_number = "01235434"
            logger.debug(f"Invalid imei number is : {invalid_imei_number}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")
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
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.info(f"Selected payment mode is Brand EMI")
            logger.info(f"Select Brand as Bosch")
            payment_page.click_on_bosch_brand()
            logger.info(f"searching for product by clicking search icon")
            payment_page.click_and_enter_search_products_or_brands(product_name)
            logger.info(f"{product_name} : is being selected as product")
            payment_page.click_and_enter_imei_no(invalid_imei_number)
            logger.info(f"Enter the invalid IMEI number")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")

            query = (f"select * from brand_validation where org_code ='{org_code}' and brand_id ={brand_id} order by"
                     f" created_time desc limit 1;")
            logger.debug(f"Query to fetch data from the brand table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result for brand table : {result}")
            error_message = result['error_message'].values[0]
            logger.debug(f"Fetching error_message value from the brand_validation table : {error_message}")
            error_code = result['error_code'].values[0]
            logger.debug(f"Fetching error_code value from the brand_validation table : {error_code}")
            status = result['status'].values[0]
            logger.debug(f"Fetching status value from the brand_validation table : {status}")
            brand_name = result['brand_name'].values[0]
            logger.debug(f"Fetching brand_name value from the brand_validation table : {status}")
            device_serial = result['device_serial'].values[0]
            logger.debug(f"Fetching error_code value from the brand_validation table : {device_serial}")
            offer_type = result['offer_type'].values[0]
            logger.debug(f"Fetching error_code value from the brand_validation table : {offer_type}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the brand_validation table : {device_serial_db}")
            brand_emi_post_status = result['brand_emi_post_status'].values[0]
            logger.debug(f"Fetching error_code value from the brand_validation table : {brand_emi_post_status}")
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
                # --------------------------------------------------------------------------------------------
                expected_app_values = {
                    "error_code": "EZETAP_7200015",
                    "error_message": "EMI cant be offered as invalid OEM IMEI code",
                    "status": "FAILED",
                    "brand_name":'Bosch',
                    "offer_type": 'BRAND_EMI',
                    "device_serial" : device_serial,
                    "brand_emi_post_status": 'VALIDATE_FAILED'
                }
                logger.debug(f"expected_app_values: {expected_app_values}")
                actual_app_values = {
                    "error_code": error_code,
                    "error_message": error_message,
                    "status": status,
                    "brand_name": brand_name,
                    "offer_type": offer_type,
                    "device_serial": device_serial_db,
                    "brand_emi_post_status": brand_emi_post_status
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
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_07_167():
    """
    Sub Feature Code: UI_Common_Verify_Brand_EMI_Flow_(No_Cashback)_EMV_VISA_CreditCard_With_Pin_417666_with_6_month_tenure_for_Merchant_level
    Sub Feature Description: Performing a Brand EMI transaction at Merchant level via HDFC-HDFC using EMV VISA Credit card with pin for 6 months tenure (bin: 417666) with cash back type none
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand_EMI, 167: TC167
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = (f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' "
                 f"and acquirer_code='HDFC' and payment_gateway='HDFC' ")
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
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
        api_details["RequestBody"]["settings"]["brandEmiSettings"] = '{"Bosch": ""}'
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for org_settings_update details : {response}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        emi_plan_in_months = 6
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")
        sku_code = 'HBF113BR0Z'
        imei_code = '00510419102091003125'
        query = (f"select b.id, bs.sku_name from brand b join brand_sku_details bs on b.id = bs.brand_id where"
                 f" b.brand_name = 'Bosch' and b.status = 1 and bs.sku_code = '{sku_code}' order by b.created_time desc,"
                 f" bs.created_time desc limit 1;")
        logger.debug(f"Query to fetch data from the brand_sku_details table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for brand_sku_details table : {result}")
        product_name = result["sku_name"].iloc[0]
        logger.debug(f"Fetching product_name from the brand_sku_details table: {product_name}")
        brand_id = result["id"].iloc[0]
        logger.debug(f"Fetching brand_id from the brand table : brand_id : {brand_id}")

        testsuite_teardown.update_emi_status_for_a_brand(org_code, 'CREDIT', 'ACTIVE', brand_id)
        logger.debug(f"updated emi settings for {org_code} as active for debit card")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION' and brand = '{brand_id}'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        interest_rate = result['interest_rate'].values[0]
        logger.debug(f"Fetching interest_rate from the emi table : {interest_rate}")
        term = result['term'].values[0]
        logger.debug(f"Fetching term from the emi table : {term}")
        scheme_code = result['scheme_code'].values[0]
        logger.debug(f"Fetching scheme_code from the emi table : {scheme_code}")
        id_emi = result['id'].values[0]
        logger.debug(f"Fetching id from the emi table : {id}")

        query = (f"select * from subvention_plan where org_code='{org_code}' and card_type= 'CREDIT' and bank='HDFC' "
                 f"order by created_time desc limit 1;")
        logger.debug(f"Query to fetch data from the subvention_plan table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan table : {result}")
        subvention_plan_id = result['id'].values[0]
        logger.debug(f"Fetching subvention_id from subvention_plan table : {subvention_plan_id}")
        # updating the status as inactive in subvention_plan_details table
        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)
        #unblocking imei code for bosch brand
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
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(3500, 4000)
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
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
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.info(f"Selected payment mode is Brand EMI")
            card_page = CardPage(driver=app_driver)
            payment_page.click_on_bosch_brand()
            logger.info(f"Selected Brand as Bosch")
            logger.info(f"searching for product by clicking search icon")
            payment_page.click_and_enter_search_products_or_brands(product_name)
            logger.info(f"Enter the Product")
            payment_page.click_and_enter_imei_no(imei_code)
            logger.info(f"Enter the IMEI number")
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"Selected the emi plan in months : {emi_plan_in_months}")
            payment_page.click_on_proceed_homepage()

            logger.debug(f"Started calculating emi part")
            monthly_interest_rate = interest_rate / (12 * 100)
            cal_monthly_emi_amt = amount * monthly_interest_rate * (
                    (1 + monthly_interest_rate) ** emi_plan_in_months) / (
                                          (1 + monthly_interest_rate) ** emi_plan_in_months - 1)
            monthly_emi = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi}")
            cal_total_emi_amt = monthly_emi * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest}")

            query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table : {pmt_status}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table : {issuer_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : {txn_type}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table : {pmt_state}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table : {payment_gateway}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table : {batch_number}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table : {amount_txn}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table : {card_last_four_digit}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table : {payment_mode}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table : {merchant_name}")
            pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table : {pmt_card_bin}")
            terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table : {terminal_info_id_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table : {tid_txn}")
            device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from the txn table : {device_serial_txn}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table : {order_id_txn}")
            card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table : {card_txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : {org_code_txn}")
            emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table : {emi_type}")
            invoice_number = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table : {invoice_number}")
            amount_original = result['amount_original'].values[0]
            logger.debug(f"Fetching amount original from the txn table : {amount_original}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {posting_date}")
            emi_id_txn = result['emi_id'].values[0]
            logger.debug(f"Fetching emi_id_txn from the txn table : {emi_id_txn}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate}")
            emi_status = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status}")
            emi_term = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term}")
            emi_loan_amount = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount}")
            emi_amount_monthly = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly}")
            emi_total_amount = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount}")
            emi_scheme_code = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code}")
            emi_txn_amount = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount}")
            emi_original_amount = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount}")

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
                date_and_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "device_serial": device_serial,
                    "batch_number": batch_number,
                    "card_type_desc": "*0102 EMV with PIN",
                    "mid": mid,
                    "tid": tid,
                    "customer_name": "L3TEST",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "customer": "L3TEST/CARD0010",
                    "emi_status": "PENDING",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(total_emi)
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the txn : {txn_id}, {app_payment_by}")
                app_card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the txn : {txn_id}, {app_card_type}")
                app_customer = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the txn : {txn_id}, {app_customer}")
                app_emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the txn : {txn_id}, {app_emi_status}")
                app_tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the txn : {txn_id}, {app_tenure}")
                app_lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the txn : {txn_id}, {app_lender}")
                app_monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the txn : {txn_id}, {app_monthly_emi}")
                app_total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the txn : {txn_id}, {app_total_interest}")
                app_total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(
                    f"Fetching total emi amount from txn history for the txn : {txn_id}, {app_total_emi_amount}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(
                    f"Fetching net effective price from txn history for the txn : {txn_id}, {app_net_effective_price}")
                app_brand_name = txn_history_page.fetch_brand_text()
                logger.debug(f"Fetching brand name from txn history for the txn : {txn_id}, {app_brand_name}")
                app_imei_no = txn_history_page.fetch_imei_text()
                logger.debug(f"Fetching imei or serial no from txn history for the txn : {txn_id}, {app_imei_no}")
                app_product = txn_history_page.fetch_product_text()
                logger.debug(f"Fetching product from txn history for the txn : {txn_id}, {app_product}")
                logger.debug(f"Scrolling to send e-receipt element on app screen")
                base_page = BasePage(driver=app_driver)
                base_page.scroll_to_text('Send E-Receipt')
                logger.debug(f"Scrolled to send e-receipt element on app screen")
                app_payment_status = txn_history_page.fetch_emi_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the txn : {txn_id}, {app_card_type_desc}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {txn_id}, {app_customer_name}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": app_payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settle_status,
                    "auth_code": app_auth_code,
                    "date": app_date_time,
                    "device_serial": app_device_serial,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "mid": app_mid,
                    "tid": app_tid,
                    "customer_name": app_customer_name,
                    "pmt_by": app_payment_by,
                    "card_type": app_card_type,
                    "customer": app_customer,
                    "emi_status": app_emi_status,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1]
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_date_and_time = date_time_converter.db_datetime(date_from_db=created_time)
                expected_api_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "HDFC",
                    "settle_status": "PENDING",
                    "rrn": rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "org_code": org_code,
                    "batch_number": batch_number,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "date": expected_date_and_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "EMV with PIN",
                    "auth_code": auth_code,
                    "card_last_four_digit": "0102",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "card_type": "VISA",
                    "display_pan": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "name_on_card": "L3TEST/CARD0010",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "interest_amt": total_interest,
                    "total_emi_amt": total_emi,
                    "net_cost": total_emi,
                    "emi_type": "BRAND_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount : {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode : {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status : {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state : {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid : {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid : {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status : {api_settle_status}")
                api_rrn = response.get('rrNumber')
                logger.debug(f"From response fetch rrn : {api_rrn}")
                api_issuer_code = response.get('issuerCode')
                logger.debug(f"From response fetch issuer_code : {api_issuer_code}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type : {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code : {api_org_code}")
                api_batch_number = response.get('batchNumber')
                logger.debug(f"From response fetch batch_number : {api_batch_number}")
                api_pmt_card_brand = response.get('paymentCardBrand')
                logger.debug(f"From response fetch payment_card_brand : {api_pmt_card_brand}")
                api_pmt_card_type = response.get('paymentCardType')
                logger.debug(f"From response fetch payment_card_type : {api_pmt_card_type}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time : {api_date_time}")
                api_device_serial = response.get('deviceSerial')
                logger.debug(f"From response fetch device_serial : {api_device_serial}")
                api_card_txn_type_desc = response.get('cardTxnTypeDesc')
                logger.debug(f"From response fetch card_txn_type_desc : {api_card_txn_type_desc}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name : {api_merchant_name}")
                api_card_last_four_digit = response.get('cardLastFourDigit')
                logger.debug(f"From response fetch card_last_four_digit : {api_card_last_four_digit}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number : {api_ext_ref_number}")
                api_pmt_card_bin = response.get('paymentCardBin')
                logger.debug(f"From response fetch payment_card_bin : {api_pmt_card_bin}")
                api_display_pan = response.get('displayPAN')
                logger.debug(f"From response fetch display_pan : {api_display_pan}")
                api_auth_code = response.get('authCode')
                logger.debug(f"From response fetch auth_code : {api_auth_code}")
                api_card_type = response.get('cardType')
                logger.debug(f"From response fetch card_type : {api_card_type}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name : {api_customer_name}")
                api_payer_name = response.get('payerName')
                logger.debug(f"From response fetch payer_name : {api_payer_name}")
                api_name_on_card = response.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card : {api_name_on_card}")
                api_emi_term = response.get('emiTerm')
                logger.debug(f"From response fetch emi_term : {api_emi_term}")
                api_emi_status = response.get('emiStatus')
                logger.debug(f"From response fetch emi_status : {api_emi_status}")
                api_interest_rate = response.get('emiInterestRate')
                logger.debug(f"From response fetch emi_interest_rate : {api_interest_rate}")
                api_emi_type = response.get('externalRefNumber7')
                logger.debug(f"From response fetch emi_type : {api_emi_type}")
                api_loan_amt = response.get('emiDetails')['loanAmount']
                logger.debug(f"From response fetch loan_amount : {api_loan_amt}")
                api_monthly_emi = response.get('emiDetails')['emi']
                logger.debug(f"From response fetch monthly emi : {api_monthly_emi}")
                api_interest_amt = response.get('emiDetails')['interestAmount']
                logger.debug(f"From response fetch interest_amount : {api_interest_amt}")
                api_total_emi_amt = response.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"From response fetch total emi amount : {api_total_emi_amt}")
                api_net_cost = response.get('emiDetails')['netCost']
                logger.debug(f"From response fetch net cost : {api_net_cost}")

                actual_api_values = {
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_status": api_payment_status,
                    "pmt_state": api_payment_state,
                    "mid": api_mid,
                    "tid": api_tid,
                    "acquirer_code": api_acquirer_code,
                    "settle_status": api_settle_status,
                    "rrn": api_rrn,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "org_code": api_org_code,
                    "batch_number": api_batch_number,
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
                    "card_txn_type_desc": api_card_txn_type_desc,
                    "auth_code": api_auth_code,
                    "card_last_four_digit": api_card_last_four_digit,
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "pmt_card_bin": api_pmt_card_bin,
                    "card_type": api_card_type,
                    "display_pan": api_display_pan,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "net_cost": api_net_cost,
                    "emi_type": api_emi_type
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": "L3TEST/CARD0010",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "HDFC",
                    "txn_type": "CHARGE",
                    "settle_status": "PENDING",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "03",
                    "card_last_four_digit": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "orig_amt": float(amount),
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "BRAND_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "emi_id": id_emi
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_txn,
                    "pmt_mode": payment_mode,
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "payer_name": payer_name,
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "pmt_gateway": payment_gateway,
                    "txn_type": txn_type,
                    "settle_status": settle_status,
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "terminal_info_id": terminal_info_id_txn,
                    "card_txn_type": card_txn_type,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name,
                    "orig_amt": amount_original,
                    "interest_rate": emi_interest_rate,
                    "emi_status": emi_status,
                    "emi_term": emi_term,
                    "emi_type": emi_type,
                    "loan_amt": emi_loan_amount,
                    "monthly_emi": emi_amount_monthly,
                    "total_emi_amt": emi_total_amount,
                    "scheme_code": emi_scheme_code,
                    "emi_txn_amt": emi_txn_amount,
                    "emi_original_amt": emi_original_amount,
                    "emi_id": emi_id_txn
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": rrn,
                    "AUTH CODE": str(auth_code).strip(),
                    "CARD TYPE": "VISA",
                    "BATCH NO": batch_number,
                    "TID": tid,
                    "payment_option": "EMI SALE",
                    "EMI Txn Id": txn_id,
                    "Tenure": f"{emi_plan_in_months} month",
                    "Card Issuer": f"{issuer_code} Bank",
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "EMI Amt": "Rs." + "{:.2f}".format(monthly_emi),
                    "INVOICE NO": invoice_number,
                    "APP": "Visa Credit",
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_details=expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)