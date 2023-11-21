import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_11_001():
    """
    Sub Feature Code: UI_Common_Card_EZE_EMI_Payback_by_Brand_Percentage_Validate_Brand_Ezetap_Co_Subvented_Brands_Are_Listed_In_The_Brand_Emi_Flow_In_App
    Sub Feature Description: Performing the EZE EMI payback by brand percentage and validate Brand-Ezetap co-subvented brands are listed in the Brand Emi Flow, only specific Brands should be listed in the app
    TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 001: TC001
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
        api_details["RequestBody"]["settings"]["ezeEmiWalletEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi, bocashback and EZEEMI is enabled in preconditions settings : {response}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
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

        # enabling eze emi
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=1, brand_id=brand_id)

        query = f"select * from brand where id='{brand_id}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        #From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
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
            brand_list = payment_page.list_of_brands()
            logger.debug(f"List of Brand displayed for Brand EMI is, {brand_list}")

            assert brand_name in brand_list
            brand = ["Specified Brand is visible" if brand_name in brand_list else "Specified Brand is not visible"]

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
                    "brand_visibility" : "Specified Brand is visible"
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "brand_visibility": brand[0]
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_11_002():
    """
        Sub Feature Code: UI_Common_Card_EZE_EMI_Payback_by_Brand_Percentage_Validate_Brand_Ezetap_Co_Subvented_Brands_Are_Listed_In_The_Eze_Emi_Flow_In_App
        Sub Feature Description: Performing the EZE EMI payback by brand percentage and validate Brand-Ezetap co-subvented brands are listed in the Eze Emi Flow, only specific Brands should be listed in the app
        TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 002: TC002
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
        api_details["RequestBody"]["settings"]["ezeEmiWalletEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi, bocashback and EZEEMI is enabled in preconditions settings : {response}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
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

        # enabling eze emi
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=1, brand_id=brand_id)

        query = f"select * from brand where id='{brand_id}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'1';"
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
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_eze_emi_pmt_mode()
            logger.debug(f"Selected payment mode is EZE EMI")
            payment_page.click_and_enter_search_products_or_brands(prod=brand_sku_name)
            logger.debug(f"Entered the products")
            customer_no = '6666666666'
            payment_page.click_and_enter_customer_number(customer_no=customer_no)
            logger.debug(f"entered customer number : {customer_no}")
            brand_list = payment_page.list_of_brands()
            logger.debug(f"List of Brand displayed for EZE EMI is, {brand_list}")

            assert brand_name in brand_list
            brand = ["Specified Brand is visible" if brand_name in brand_list else "Specified Brand is not visible"]

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
                    "brand_visibility" : "Specified Brand is visible"
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "brand_visibility": brand[0]
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_11_003():
    """
        Sub Feature Code: UI_Common_Card_EZE_EMI_Payback_by_Brand_Percentage_Enable_IMEI_Validation_For_Both_Brand_And_EzeEMI_Flow
        Sub Feature Description: Performing the EZE EMI payback by brand percentage and verify IMEI validation is enabled for both brand emi and eze emi flow
        TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 003: TC003
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
        api_details["RequestBody"]["settings"]["ezeEmiWalletEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi, bocashback and EZEEMI is enabled in preconditions settings : {response}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='EZEEMI'" \
                f"and tid_type='SUBVENTION';"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        brand_id = result['brand'].values[0]
        logger.debug(f"Fetching brand_id from the emi table : {brand_id}")

        # enabling eze emi
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=1, brand_id=brand_id)

        query = f"select * from brand where id='{brand_id}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        #Updating the config_data table with param_value as 'ONLINE' for both brand emi and eze emi
        query = f"update config_data set param_value = 'ONLINE' where entity_id ='{brand_id}' and param_key in ('ezeemiPostingStatus', 'postingStatus')"
        logger.debug(f"Updating config_data table with param_value as ONLINE for Brand emi and Eze emi : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result for config_data table after updating the param_value as ONLINE for Brand emi and Eze emi : {result}")
        refresh_db()
        logger.debug(f"Refreshing the DB after updating the config_data table with param_value as ONLINE for Brand emi and Eze emi : {result}")

        #From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'1';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        eze_emi_brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {eze_emi_brand_sku_name}")

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
            payment_page.click_on_eze_emi_pmt_mode()
            logger.debug(f"Selected payment mode is EZE EMI")
            payment_page.click_and_enter_search_products_or_brands(prod=eze_emi_brand_sku_name)
            logger.debug(f"Entered the products")
            customer_no = '6666666666'
            payment_page.click_and_enter_customer_number(customer_no)
            logger.debug(f"Entered customer mobile number is : {customer_no}")

            try:
                payment_page.check_for_imei_no_validation()
                logger.debug(f"IMEI number is visible for Eze EMI")
                payment_page.click_on_back_btn()

                query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                        f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                        f"and tid_type='SUBVENTION';"
                logger.debug(f"Query to fetch data from the emi table for brand emi : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from emi table for brand emi :{result}")
                brand_id = result['brand'].values[0]
                logger.debug(f"Fetching brand_id from the emi table for brand emi : {brand_id}")

                query = f"select * from brand where id='{brand_id}'"
                logger.debug(f"Query to fetch data from the brand table : {query}")
                result = DBProcessor.getValueFromDB(query=query)
                logger.debug(f"Query result for brand table : {result}")
                brand_name = result['brand_name'].values[0]
                logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

                query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
                logger.debug(f"Query to fetch data from the brand_sku_details table for brand emi : {query}")
                result = DBProcessor.getValueFromDB(query=query)
                logger.debug(f"Query result for brand table for brand emi : {result}")
                brand_sku_name = result['sku_name'].values[0]
                logger.debug(f"Fetching sku_name value from the brand_sku_details table for brand emi : {brand_sku_name}")

                #selecting the brand emi pmt mode
                payment_page.click_on_brand_emi_pmt_mode()
                logger.debug("Selected payment mode is Brand EMI")
                payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
                logger.debug(f"Entered the product for Brand EMI: {brand_sku_name}")
                payment_page.check_for_imei_no_validation()
                logger.debug(f"IMEI number is visible for Brand EMI")

                imei_no = "IMEI number is visible for both Brand EMI and Eze EMI"

            except Exception as e:
                logger.debug(f"An exception occurred: {e}")
                imei_no = "IMEI number is invisible for both Brand EMI and Eze EMI"

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
                    "imei_no_visibility" : "IMEI number is visible for both Brand EMI and Eze EMI"
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "imei_no_visibility": imei_no
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_11_004():
    """
        Sub Feature Code: UI_Common_Card_EZE_EMI_Payback_by_Brand_Percentage_Enable_IMEI_Validation_For_Brand_EMI_Disable_For_EzeEMI
        Sub Feature Description: Performing the EZE EMI payback by brand percentage and verify IMEI validation is enabled for brand emi and disabled for eze emi
        TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 004: TC004
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
        api_details["RequestBody"]["settings"]["ezeEmiWalletEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi, bocashback and EZEEMI is enabled in preconditions settings : {response}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='EZEEMI'" \
                f"and tid_type='SUBVENTION';"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        brand_id = result['brand'].values[0]
        logger.debug(f"Fetching brand_id from the emi table : {brand_id}")

        # enabling eze emi
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=1, brand_id=brand_id)

        query = f"select * from brand where id='{brand_id}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        #Updating the config_data table with param_value as 'OFFLINE' for and eze emi and ONLINE for brand emi
        query = f"update config_data set param_value = 'OFFLINE' where entity_id ='{brand_id}' and param_key = 'ezeemiPostingStatus'"
        logger.debug(f"Updating config_data table with param_value as OFFLINE for Eze emi : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result for config_data table after updating the param_value as OFFLINE for Eze emi : {result}")

        query = f"update config_data set param_value = 'ONLINE' where entity_id ='{brand_id}' and param_key = 'postingStatus'"
        logger.debug(f"Updating config_data table with param_value as ONLINE for Brand emi : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result for config_data table after updating the param_value as ONLINE for Brand emi : {result}")

        refresh_db()
        logger.debug(f"Refreshing the DB after updating the config_data table with given param_value for Brand emi and Eze emi : {result}")

        #From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'1';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        eze_emi_brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {eze_emi_brand_sku_name}")

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
            payment_page.click_on_eze_emi_pmt_mode()
            logger.debug(f"Selected payment mode is EZE EMI")
            payment_page.click_and_enter_search_products_or_brands(eze_emi_brand_sku_name)
            logger.debug(f"Clicked on EzeEMI brand is : {eze_emi_brand_sku_name}")
            customer_no = '6666666666'
            payment_page.click_and_enter_customer_number(customer_no)
            logger.debug(f"Entered customer mobile number is : {customer_no}")

            try:
                payment_page.check_for_imei_no_validation()
                logger.debug(f"IMEI number is invisible for Eze EMI ")
                payment_page.click_on_back_btn()

                query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                        f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                        f"and tid_type='SUBVENTION';"
                logger.debug(f"Query to fetch data from the emi table for brand emi : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from emi table for brand emi :{result}")
                brand_id = result['brand'].values[0]
                logger.debug(f"Fetching brand_id from the emi table for brand emi : {brand_id}")

                query = f"select * from brand where id='{brand_id}'"
                logger.debug(f"Query to fetch data from the brand table : {query}")
                result = DBProcessor.getValueFromDB(query=query)
                logger.debug(f"Query result for brand table : {result}")
                brand_name = result['brand_name'].values[0]
                logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

                query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
                logger.debug(f"Query to fetch data from the brand_sku_details table for brand emi : {query}")
                result = DBProcessor.getValueFromDB(query=query)
                logger.debug(f"Query result for brand table for brand emi : {result}")
                brand_sku_name = result['sku_name'].values[0]
                logger.debug(f"Fetching sku_name value from the brand_sku_details table for brand emi : {brand_sku_name}")

                #selecting the brand emi pmt mode
                payment_page.click_on_brand_emi_pmt_mode()
                logger.debug("Selected payment mode is Brand EMI")
                payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
                logger.debug(f"Entered the product for Brand EMI: {brand_sku_name}")
                payment_page.check_for_imei_no_validation()
                logger.debug(f"IMEI number is visible for Brand EMI")

                imei_no = "IMEI number is visible for Brand EMI"

            except Exception as e:
                logger.debug(f"An exception occurred: {e}")
                imei_no = "IMEI number is invisible for Brand EMI"

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
                    "imei_no_visibility" : "IMEI number is visible for Brand EMI"
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "imei_no_visibility": imei_no
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
        query = f"update config_data set param_value = 'ONLINE' where entity_id ='{brand_id}' and param_key = 'ezeemiPostingStatus'"
        logger.debug(f"Updating config_data table with param_value as ONLINE for Eze emi : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result for config_data table after updating the param_value as ONLINE for Eze emi : {result}")

        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_11_005():
    """
        Sub Feature Code: UI_Common_Card_EZE_EMI_Payback_by_Brand_Percentage_Enable_IMEI_Validation_For_EzeEMI_Disable_For_Brand_EMI
        Sub Feature Description: Performing the EZE EMI payback by brand percentage and verify IMEI validation is enabled for eze emi and disabled for brand emi
        TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 005: TC005
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
        api_details["RequestBody"]["settings"]["ezeEmiWalletEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi, bocashback and EZEEMI is enabled in preconditions settings : {response}")

        query = f"select * from brand where brand_name = 'EZEMI_DOBRAND'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_id = result['id'].values[0]
        logger.debug(f"Fetching brand_id value from the brand table : {brand_id}")
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        # Updating the config_data table with param_value as 'ONLINE' for and eze emi and OFFLINE for brand emi
        query = f"update config_data set param_value = 'ONLINE' where entity_id ='{brand_id}' and param_key = 'ezeemiPostingStatus'"
        logger.debug(f"Updating config_data table with param_value as ONLINE for Eze emi : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result for config_data table after updating the param_value as ONLINE for Eze emi : {result}")

        query = f"update config_data set param_value = 'OFFLINE' where entity_id ='{brand_id}' and param_key = 'postingStatus'"
        logger.debug(f"Updating config_data table with param_value as OFFLINE for Brand emi : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result for config_data table after updating the param_value as OFFLINE for Brand emi : {result}")

        refresh_db()
        logger.debug(f"Refreshing the DB after updating the config_data table with given param_value for Brand emi and Eze emi : {result}")

        #From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
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
            payment_page.click_on_eze_emi_pmt_mode()
            logger.debug(f"Selected payment mode is EZE EMI")
            payment_page.click_and_enter_search_products_or_brands(brand_name)
            logger.debug(f"Clicked on EzeEMI brand is : {brand_name}")
            customer_no = '6666666666'
            payment_page.click_and_enter_customer_number(customer_no)
            logger.debug(f"Entered customer mobile number is : {customer_no}")

            try:
                payment_page.check_for_imei_no_validation()
                logger.debug(f"IMEI number is invisible for Eze EMI ")
                payment_page.click_on_back_btn()

                #selecting the brand emi pmt mode
                payment_page.click_on_brand_emi_pmt_mode()
                logger.debug("Selected payment mode is Brand EMI")
                payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
                logger.debug(f"Entered the product for Brand EMI: {brand_sku_name}")
                payment_page.check_for_imei_no_validation()
                logger.debug(f"IMEI number is visible for Brand EMI")

                imei_no = "IMEI number is visible for Eze EMI"

            except Exception as e:
                logger.debug(f"An exception occurred: {e}")
                imei_no = "IMEI number is invisible for Eze EMI"

            except Exception as e:
                logger.debug(f"An exception occurred: {e}")

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
                    "imei_no_visibility" : "IMEI number is visible for Eze EMI"
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "imei_no_visibility": imei_no
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
        query = f"update config_data set param_value = 'ONLINE' where entity_id ='{brand_id}' and param_key = 'postingStatus'"
        logger.debug(f"Updating config_data table with param_value as ONLINE for Brand emi : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result for config_data table after updating the param_value as ONLINE for Brand emi : {result}")

        Configuration.executeFinallyBlock(testcase_id)