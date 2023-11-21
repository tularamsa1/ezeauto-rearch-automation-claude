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
def test_common_100_115_11_006():
    """
        Sub Feature Code: UI_Common_Card_EZE_EMI_Payback_by_Brand_Percentage_Disable_IMEI_Validation_For_Both_Brand_And_EzeEMI_Flow
        Sub Feature Description: Performing the EZE EMI payback by brand percentage and verify IMEI validation is disabled for both brand emi and eze emi flow
        TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 006: TC006
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

        # Updating the config_data table with param_value as 'ONLINE' for both brand emi and eze emi
        query = f"update config_data set param_value = 'OFFLINE' where entity_id ='{brand_id}' and param_key in ('ezeemiPostingStatus', 'postingStatus')"
        logger.debug(f"Updating config_data table with param_value as OFFLINE for Brand emi and Eze emi : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result for config_data table after updating the param_value as OFFLINE for Brand emi and Eze emi : {result}")
        refresh_db()
        logger.debug(f"Refreshing the DB after updating the config_data table with param_value as OFFLINE for Brand emi and Eze emi : {result}")

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

                # selecting the brand emi pmt mode
                payment_page.click_on_brand_emi_pmt_mode()
                logger.debug("Selected payment mode is Brand EMI")
                payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
                logger.debug(f"Entered the product for Brand EMI: {brand_sku_name}")
                payment_page.check_for_imei_no_validation()
                logger.debug(f"IMEI number is invisible for Brand EMI")

                imei_no = "IMEI number is invisible for Eze EMI and Brand EMI"

            except Exception as e:
                logger.debug(f"An exception occurred: {e}")
                imei_no = "IMEI number is visible for Eze EMI and Brand EMI"

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
                    "imei_no_visibility" : "IMEI number is invisible for Eze EMI and Brand EMI"
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
        query = f"update config_data set param_value = 'ONLINE' where entity_id ='{brand_id}' and param_key in ('ezeemiPostingStatus', 'postingStatus')"
        logger.debug(f"Updating config_data table with param_value as OFFLINE for Brand emi and Eze emi : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result for config_data table after updating the param_value as ONLINE for Brand emi and Eze emi : {result}")
        refresh_db()
        logger.debug(f"Refreshing the DB after updating the config_data table with param_value as ONLINE for Brand emi and Eze emi : {result}")

        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_11_007():
    """
        Sub Feature Code: UI_Common_Card_EZE_EMI_Payback_by_Brand_Percentage_Validate_Brand_Ezetap_Co_Subvented_wallet_Present_On_App_For_Brand_EMI
        Sub Feature Description: Performing the EZE EMI payback by brand percentage and validate Brand-Ezetap co-subvented wallet is reflected in the Brand Emi for specific brand
        TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 007s: TC007
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

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        emi_plan_in_months = 6
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
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled= 1 ,brand_id=brand_id)

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

        query = f"select * from subvention_plan where brand_id='{brand_id}' and status=1 and org_code='{org_code}' and card_type= 'CREDIT' and eze_emi_enabled=b'0';"
        logger.debug(f"Query to fetch data from the subvention_plan table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan table : {result}")
        subvention_plan_id = result['id'].values[0]
        logger.debug(f"Fetching subvention_id from subvention_plan table : {subvention_plan_id}")
        subvention_plan_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_plan_scheme_name}")
        subvention_plan_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from subvention_plan table : {subvention_plan_org_code}")
        subvention_plan_brand_id = result['brand_id'].values[0]
        logger.debug(f"Fetching brand_id from subvention_plan table : {subvention_plan_brand_id}")
        subvention_plan_card_type = result['card_type'].values[0]
        logger.debug(f"Fetching card_type from subvention_plan table : {subvention_plan_card_type}")
        subvention_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_scheme_name}")

        # updating the status as inactive in subvention_plan_details table
        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity in ('BRAND','EZETAP') and subvention_type='PAYBACK' and subvention_value_type='PERCENTAGE' and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

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
            payment_page.select_emi_plan_for_wallet(emi_plan_in_months)
            logger.debug(f"Selected the emi plan in months : {emi_plan_in_months}")

            try:
                payment_page.check_for_use_wallet()
                logger.debug(f"For Brand EMI wallet is visible")
                payment_page.click_on_back_btn()

                brand_emi_wallet = "Specific Brand Custom wallet is visible for Brand EMI"

            except Exception as e:
                logger.debug(f"An exception occurred: {e}")
                brand_emi_wallet = "Specific Brand Custom wallet is invisible for Brand EMI"

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
                    "brand_wallet" : "Specific Brand Custom wallet is visible for Brand EMI"
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "brand_wallet": brand_emi_wallet
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
def test_common_100_115_11_008():
    """
        Sub Feature Code: UI_Common_Card_EZE_EMI_Payback_by_Brand_Percentage_Brand_Ezetap_Co_Subvention_Is_Created_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_6_Months_Tenure
        Sub Feature Description:  Performing the EZE EMI payback by brand percentage and verify the tenure for brand-ezetap co-subvention created scheme and subvention
        is displayed with specific custom wallet for an org via HDFC Dummy PG using EMV VISA Credit card with pin for 6 months tenure (bin: 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 008: TC008
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

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        emi_plan_in_months = 6
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION' order by created_time asc limit 1"
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

        # From brand_sku_Details picking the brand product_name
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

        query = f"select * from subvention_plan where brand_id='{brand_id}' and status=1 and org_code='{org_code}' and card_type= 'CREDIT' and eze_emi_enabled=b'0';"
        logger.debug(f"Query to fetch data from the subvention_plan table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan table : {result}")
        subvention_plan_id = result['id'].values[0]
        logger.debug(f"Fetching subvention_id from subvention_plan table : {subvention_plan_id}")
        subvention_plan_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_plan_scheme_name}")
        subvention_plan_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from subvention_plan table : {subvention_plan_org_code}")
        subvention_plan_brand_id = result['brand_id'].values[0]
        logger.debug(f"Fetching brand_id from subvention_plan table : {subvention_plan_brand_id}")
        subvention_plan_card_type = result['card_type'].values[0]
        logger.debug(f"Fetching card_type from subvention_plan table : {subvention_plan_card_type}")
        subvention_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_scheme_name}")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity='BRAND' and subvention_value_type= 'PERCENTAGE' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month';"
        logger.debug(f"Query to fetch data from the subvention_plan_details table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan_details table : {result}")
        brand_subvention_value = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value from subvention_plan_details table : {brand_subvention_value}")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity='EZETAP' and subvention_value_type= 'PERCENTAGE' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month';"
        logger.debug(f"Query to fetch data from the subvention_plan_details table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan_details table : {result}")
        ezetap_subvention_value = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value from subvention_plan_details table : {ezetap_subvention_value}")

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity in ('BRAND','EZETAP') and subvention_type='PAYBACK' and subvention_value_type='PERCENTAGE' and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

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
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan_for_wallet(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"Selected the emi plan in months : {emi_plan_in_months}")
            subvention_val = (brand_subvention_value + ezetap_subvention_value)
            logger.debug(f"Subvention value is : {subvention_val}")
            razorpay_emi_discount = payment_page.click_on_razorpay_emi_discount("{:.2f}".format(subvention_val))
            logger.debug(f"Check the value for razorpay emi discount : {razorpay_emi_discount}")

            try:
                razorpay_emi_discount_sub_value = str(razorpay_emi_discount).split("@")[1].split("%")[0]
                logger.debug(f"Subvention value for razorpay_emi_discount is : {razorpay_emi_discount_sub_value}")
                wallet_is_displayed = payment_page.check_for_use_wallet()
                logger.debug(f"Clicked on use wallet : {wallet_is_displayed}")

                if razorpay_emi_discount_sub_value == "{:,.2f}".format(subvention_val) and wallet_is_displayed == 1:
                    wallet_displayed = "Subvention and Specific brand custom wallet is displayed"
                else:
                    wallet_displayed = "Subvention and Specific brand custom wallet is not displayed"

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
                    "subvention_value": "{:,.2f}".format(brand_subvention_value + ezetap_subvention_value),
                    "wallet_displayed": "Subvention and Specific brand custom wallet is displayed"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "subvention_value": razorpay_emi_discount_sub_value,
                    "wallet_displayed": wallet_displayed
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
def test_common_100_115_11_009():
    """
        Sub Feature Code: UI_Common_Card_EZE_EMI_Payback_by_Brand_Percentage_Brand_Ezetap_Co_Subvention_Is_Created_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
        Sub Feature Description:  Performing the EZE EMI payback by brand percentage and verify other tenure for brand-ezetap co-subvention created scheme and subvention
        is displayed and specific custom wallet is not displayed for an org via HDFC Dummy PG using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 009: TC009
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

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

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

        # From brand_sku_Details picking the brand product_name
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

        query = f"select * from subvention_plan where brand_id='{brand_id}' and status=1 and org_code='{org_code}' and card_type= 'CREDIT' and eze_emi_enabled=b'0';"
        logger.debug(f"Query to fetch data from the subvention_plan table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan table : {result}")
        subvention_plan_id = result['id'].values[0]
        logger.debug(f"Fetching subvention_id from subvention_plan table : {subvention_plan_id}")
        subvention_plan_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_plan_scheme_name}")
        subvention_plan_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from subvention_plan table : {subvention_plan_org_code}")
        subvention_plan_brand_id = result['brand_id'].values[0]
        logger.debug(f"Fetching brand_id from subvention_plan table : {subvention_plan_brand_id}")
        subvention_plan_card_type = result['card_type'].values[0]
        logger.debug(f"Fetching card_type from subvention_plan table : {subvention_plan_card_type}")
        subvention_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_scheme_name}")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity='BRAND' and subvention_value_type= 'PERCENTAGE' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month';"
        logger.debug(f"Query to fetch data from the subvention_plan_details table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan_details table : {result}")
        brand_subvention_value = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value from subvention_plan_details table : {brand_subvention_value}")

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity in ('BRAND','EZETAP') and subvention_type='PAYBACK' and subvention_value_type='PERCENTAGE' and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

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
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan_for_wallet(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"Selected the emi plan in months : {emi_plan_in_months}")

            try:
                payment_page.click_on_emi_discount("{:.2f}".format(brand_subvention_value))
                logger.debug(f"Check for razorpay emi discount value")
                payment_page.check_for_use_wallet()
                logger.debug(f"Clicked on use wallet")

                wallet_displayed = "Subvention is displayed for specific brand and custom wallet is not displayed"

            except Exception as e:
                logger.debug(f"An exception occurred: {e}")
                wallet_displayed = "Subvention and Specific brand custom wallet is displayed"

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
                    "wallet_displayed": "Subvention is displayed for specific brand and custom wallet is not displayed"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "wallet_displayed": wallet_displayed
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
def test_common_100_115_11_010():
    """
    Sub Feature Code: UI_Common_Card_Eze_EMI_For_Payback_by_Brand_Percentage_Verify_Wallet_Txn_Amount_Greater_Than_GCEW_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_6_Months_Tenure
    Sub Feature Description: Performing the EZE EMI payback by brand percentage and verify the wallet when transaction amount is greater than the GCEW
        for an org via HDFC Dummy PG using EMV VISA Credit card with pin for 6 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 11: EZE EMI, 010: TC010
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

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        emi_plan_in_months = 6
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

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'1';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")
        product_min_amount = result['min_amount'].values[0]
        logger.debug(f"Fetching min_amount value from the brand_sku_details table : {product_min_amount}")
        product_max_amount = result['max_amount'].values[0]
        logger.debug(f"Fetching max_amount value from the brand_sku_details table : {product_max_amount}")

        query = f"select * from subvention_plan where brand_id='{brand_id}' and status=1 and org_code='{org_code}' and card_type= 'CREDIT' and eze_emi_enabled=b'1' ;"
        logger.debug(f"Query to fetch data from the subvention_plan table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan table : {result}")
        subvention_plan_id = result['id'].values[0]
        logger.debug(f"Fetching subvention_id from subvention_plan table : {subvention_plan_id}")

        # Collecting the GCEW wallet balance
        query = f"select * from ezeemi_club_wallet_account where wallet_type='GCEW' and brand_id='{brand_id}'"
        logger.debug(f"Query to fetch data from the ezeemi_club_wallet_account table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for ezeemi_club_wallet_account table : {result}")
        gcew_wallet_balance = result['wallet_balance'].values[0]
        logger.debug(f"collecting the wallet balance from ezeemi_club_wallet_account table : {gcew_wallet_balance}")

        query = f"select * from ezeemi_club_wallet_account where wallet_type='MCEW' and brand_id='{brand_id}'"
        logger.debug(f"Query to fetch data from the ezeemi_club_wallet_account table for MCEW : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for ezeemi_club_wallet_account table for MCEW : {result}")
        mcew_wallet_balance = result['wallet_balance'].values[0]
        logger.debug(f"collecting the wallet balance from ezeemi_club_wallet_account table  for MCEW : {mcew_wallet_balance}")

        # updating the status as inactive in subvention_plan_details table
        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity='EZETAP' and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        query = f"update ezeemi_club_wallet_account set wallet_balance={int(product_max_amount - 900)} where wallet_type='GCEW' and brand_id='{brand_id}'"
        logger.debug(f"Query to update ezeemi_club_wallet_account by subtracting the max amount of product : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from ezeemi_club_wallet_account after subtracting with the max amount of product : {result}")

        query = f"update ezeemi_club_wallet_account set wallet_balance={int(product_max_amount - 1000)} where wallet_type='MCEW' and brand_id='{brand_id}'"
        logger.debug(f"Query to update ezeemi_club_wallet_account by subtracting the max amount of product : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from ezeemi_club_wallet_account after subtracting with the max amount of product : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

        query = f"select * from ezeemi_club_wallet_account where wallet_type='GCEW' and brand_id='{brand_id}'"
        logger.debug(f"Query to fetch data from the ezeemi_club_wallet_account table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for ezeemi_club_wallet_account table : {result}")
        gcew_wallet_balance_2 = result['wallet_balance'].values[0]
        logger.debug(f"Fetching wallet_balance from ezeemi_club_wallet_account table : {gcew_wallet_balance_2}")

        query = f"select * from ezeemi_club_wallet_account where wallet_type='MCEW' and brand_id='{brand_id}'"
        logger.debug(f"Query to fetch data from the ezeemi_club_wallet_account table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for ezeemi_club_wallet_account table : {result}")
        mcew_wallet_balance_2 = result['wallet_balance'].values[0]
        logger.debug(f"Fetching wallet_balance from ezeemi_club_wallet_account table : {mcew_wallet_balance_2}")

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
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = gcew_wallet_balance_2 + 100
            logger.info(f"For GCEW wallet balance adding 100 rupees {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amount, order_id, device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is  : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_eze_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Eze EMI")
            payment_page.click_and_enter_search_products_or_brands(prod=brand_sku_name)
            logger.debug(f"Entered the products for Eze EMI")
            customer_no = '6666666666'
            payment_page.click_and_enter_customer_number(customer_no=customer_no)
            logger.debug(f"entered customer number : {customer_no}")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")

            try:
                payment_page.click_and_enter_imei_no_and_proceed_btn(imei=imei_no)
                logger.debug(f"Entered IMEI number is, {imei_no}")
                logger.debug(f"Proceed button is disabled")
                proceed_btn = "Proceed button is disabled"
            except:
                logger.debug(f"Proceed button is not disabled")
                proceed_btn = "Proceed button is not disabled"

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
                    "proceed_btn": "Proceed button is disabled"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "proceed_btn": proceed_btn
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
        query = f"update ezeemi_club_wallet_account set wallet_balance={gcew_wallet_balance} where wallet_type='GCEW' and brand_id='{brand_id}'"
        logger.debug(f"Query to update ezeemi_club_wallet_account table with wallet_balance for GCEW  : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from ezeemi_club_wallet_account table with wallet_balance for GCEW : {result}")

        query = f"update ezeemi_club_wallet_account set wallet_balance={mcew_wallet_balance} where wallet_type='MCEW' and brand_id='{brand_id}'"
        logger.debug(f"Query to update ezeemi_club_wallet_account table with wallet_balance for MCEW: {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from ezeemi_club_wallet_account table with wallet_balance for MCEW : {result}")

        Configuration.executeFinallyBlock(testcase_id)