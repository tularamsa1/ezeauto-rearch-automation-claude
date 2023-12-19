import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_card_page import CardPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_07_086():
    """
        Sub Feature Code: UI_Common_Card_Brand_EMI_Txn_For_Amount_Greater_Than_EMI_Range_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
        Sub Feature Description: Verify the Brand EMI txn for amount greater than the EMI range for an org via HDFC Dummy PG using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand EMI, 086: TC086
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

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
        logger.debug(f"Active emi setting for credit card")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        brand = result['brand'].values[0]
        logger.debug(f"Fetching brand from the emi table : {brand}")
        brand_max_amount = result['max_amount'].values[0]
        logger.debug(f"Fetching max amount from the emi table : {brand_max_amount}")

        # disabling the eze emi plus
        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand)

        query = f"select * from brand where id='{brand}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_id = result['id'].values[0]
        logger.debug(f"Fetching brand_id value from the brand table : {brand_id}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, middlewareLog=True, q2_log=True)

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
            amount = int(brand_max_amount) + 100
            logger.info(f"Brand EMI minimum amount after adding with 100, {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amount, order_id, device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is  : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_07_087():
    """
        Sub Feature Code: UI_Common_Card_Brand_EMI_Payback_by_Brand_Percentage_With_No_Cost_EMI_Success_Txn_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
        Sub Feature Description: Performing the brand EMI payback by brand percentage with no cost emi success transaction for an org via HDFC Dummy PG using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand EMI, 087: TC087
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

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
        logger.debug(f"Active emi setting for credit card")

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

        query = f"select * from subvention_plan where brand_id='{brand_id}' and org_code='{org_code}' and card_type= 'CREDIT' and bank='HDFC' and eze_emi_enabled=b'0' order by created_time desc limit 1;"
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

        # updating the status as inactive in subvention_plan_details table
        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and" \
                f" subventing_entity='BRAND' and subvention_type='PAYBACK' and subvention_value_type='PERCENTAGE'" \
                f" and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        query = f"update emi set interest_rate='15' where org_code='{org_code}' and " \
                f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Updating the emi setting with interest_rate : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Fetching result after updating emi table with interest_rate :{result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the emi interest_rate and subvention_plan_details")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity='BRAND' " \
                f"and subvention_value_type= 'PERCENTAGE' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month' ;"
        logger.debug(f"Query to fetch data from the subvention_plan_details table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan_details table : {result}")
        sub_value = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value from subvention_plan_details table : {sub_value}")

        query = f"update subvention_plan_details set subvention_value='2.45' where subvention_plan_id='{subvention_plan_id}' and " \
                f"subventing_entity='BRAND' and subvention_value_type= 'PERCENTAGE' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month' ;"
        logger.debug(f"Updating the subvention_value from subvention_plan_details table : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result after updating subvention_value in subvention_plan_details table : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity='BRAND' " \
                f"and subvention_value_type= 'PERCENTAGE' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month' ;"
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
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
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

            #Condition for no cost emi
            no_cost_emi_text = payment_page.fetch_emi_cost_text(emi_plan_in_months)
            if no_cost_emi_text.split('@' '')[-1] == 'NoCost':
                payment_page.select_emi_plan(emi_plan_in_months)
                logger.debug(f"Selected the emi plan in months : {emi_plan_in_months}")
                payment_page.click_on_proceed_homepage()

                #Calculating the emi's using formula
                cal_additional_payback = (amount * (subvention_value / 100))
                logger.debug(f"cal_additional_payback is : {cal_additional_payback}")
                monthly_interest_rate = interest_rate / (12 * 100)
                logger.debug(f"monthly_interest_rate is : {monthly_interest_rate}")
                cal_monthly_emi_amt = (amount - cal_additional_payback) * monthly_interest_rate * ((1 + monthly_interest_rate) ** emi_plan_in_months) / (
                                              (1 + monthly_interest_rate) ** emi_plan_in_months - 1)
                logger.debug(f"cal_monthly_emi_amt is : {cal_monthly_emi_amt}")
                monthly_emi = round(cal_monthly_emi_amt, 2)
                logger.debug(f"Calculated monthly_emi amount : {monthly_emi}")
                total_emi = round((monthly_emi * emi_plan_in_months), 2)
                logger.debug(f"total_emi amount is : {total_emi}")
                total_interest = round((total_emi - (amount - cal_additional_payback)), 2)
                logger.debug(f"total_interest amount is : {total_interest}")

                query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
                logger.debug(f"Query to fetch data from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for txn table : {result}")
                txn_created_time = result['created_time'].values[0]
                logger.debug(f"Fetching created_time value from the txn table : {txn_created_time}")
                txn_id = result['id'].values[0]
                logger.debug(f"Fetching txn_id value from the txn table : {txn_id}")
                rrn = result['rr_number'].values[0]
                logger.debug(f"Fetching rrn value from the txn table : {rrn}")
                auth_code = result['auth_code'].values[0]
                logger.debug(f"Fetching auth_code value from the txn table : {auth_code}")
                batch_number = result['batch_number'].values[0]
                logger.debug(f"Fetching batch_number value from the txn table : {batch_number}")
                amount_db = result['amount'].values[0]
                logger.debug(f"Fetching amount value from the txn table : {amount_db}")
                original_amount_db = result['amount_original'].values[0]
                logger.debug(f"Fetching amount_original value from the txn table : {original_amount_db}")
                amt_cash_back_db = result['amount_cash_back'].values[0]
                logger.debug(f"Fetching amount_cash_back value from the txn table : {amt_cash_back_db}")
                payment_mode_db = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode value from the txn table : {payment_mode_db}")
                payment_status_db = result['status'].values[0]
                logger.debug(f"Fetching status value from the txn table : {payment_status_db}")
                payment_state_db = result['state'].values[0]
                logger.debug(f"Fetching state value from the txn table : {payment_state_db}")
                acquirer_code_db = result['acquirer_code'].values[0]
                logger.debug(f"Fetching acquirer_code value from the txn table : {acquirer_code_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching mid value from the txn table : {mid_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching tid value from the txn table : {tid_db}")
                payment_gateway_db = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway value from the txn table : {payment_gateway_db}")
                settlement_status_db = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status value from the txn table : {settlement_status_db}")
                device_serial_db = result['device_serial'].values[0]
                logger.debug(f"Fetching device_serial value from the txn table : {device_serial_db}")
                sale_amt_db = result['amount_original'].values[0]
                logger.debug(f"Fetching amount_original value from the txn table : {sale_amt_db}")
                merchant_name = result['merchant_name'].values[0]
                logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name}")
                merchant_code_db = result["merchant_code"].iloc[0]
                logger.debug(f"Fetching merchant_code value from the txn table : {merchant_code_db}")
                payment_card_brand_db = result["payment_card_brand"].iloc[0]
                logger.debug(f"Fetching payment_card_brand value from the txn table : {payment_card_brand_db}")
                payment_card_type_db = result["payment_card_type"].iloc[0]
                logger.debug(f"Fetching payment_card_type value from the txn table : {payment_card_type_db}")
                issuer_code_db = result["issuer_code"].iloc[0]
                logger.debug(f"Fetching issuer_code value from the txn table : {issuer_code_db}")
                payment_card_bin_db = result["payment_card_bin"].iloc[0]
                logger.debug(f"Fetching payment_card_bin value from the txn table : {payment_card_bin_db}")
                terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Fetching terminal_info_id value from the txn table : {terminal_info_id_db}")
                txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type value from the txn table : {txn_type_db}")
                card_txn_type_db = result["card_txn_type"].iloc[0]
                logger.debug(f"Fetching card_txn_type value from the txn table : {card_txn_type_db}")
                card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
                logger.debug(f"Fetching card_last_four_digit value from the txn table : {card_last_four_digit_db}")
                customer_name_db = result["customer_name"].values[0]
                logger.debug(f"Fetching customer_name value from the txn table : {customer_name_db}")
                payer_name_db = result["payer_name"].values[0]
                logger.debug(f"Fetching payer_name value from the txn table : {payer_name_db}")
                org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code value from the txn table : {org_code_db}")
                order_id_db = result["external_ref"].iloc[0]
                logger.debug(f"Fetching external_ref value from the txn table : {order_id_db}")
                emi_type_db = result['external_ref7'].values[0]
                logger.debug(f"Fetching external_ref7 from the txn table : {emi_type_db}")
                invoice_number = result['pg_invoice_number'].values[0]
                logger.debug(f"Fetching pg_invoice_number from the txn table : {invoice_number}")
                posting_date = result['posting_date'].values[0]
                logger.debug(f"Fetching posting_date from txn table : {posting_date}")

                query = f"select * from txn_emi where id='{txn_id}';"
                logger.debug(f"Query to fetch data from the txn_emi table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for txn_emi table : {result}")
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
                emi_payback_amount = result['emi_payback_amount'].values[0]
                logger.debug(f"Fetching emi payback amount from txn_emi table : {emi_payback_amount}")
                emi_cashback_type = result['emi_cashback_type'].values[0]
                logger.debug(f"Fetching emi cashback type from txn_emi table : {emi_cashback_type}")
                processer_db = result['processor'].values[0]
                logger.debug(f"Fetching processer value from the txn_emi table : {processer_db}")

            else:
                logger.error("There is no configuration obtained for selected tenure")

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
                    "emi_status": "PENDING",
                    "emi_customer_name": "L3TEST",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "additional_payback": "{:,.2f}".format(emi_payback_amount),
                    "loan_amt": "{:,.2f}".format(amount - cal_additional_payback),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "brand": brand_name,
                    "product": brand_sku_name,
                    "imei_no": str(imei_no),
                    "scheme": subvention_plan_scheme_name
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
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
                logger.debug(f"Fetching total emi amount from txn history for the txn : {txn_id}, {app_total_emi_amount}")
                app_additional_payback = txn_history_page.fetch_additional_payback()
                logger.debug(f"Fetching additional payback from txn history for the txn : {txn_id}, {app_additional_payback}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug( f"Fetching net effective price from txn history for the txn : {txn_id}, {app_net_effective_price}")
                app_product = txn_history_page.fetch_product_text()
                logger.debug(f"Fetching product from txn history for the txn : {txn_id}, {app_product}")
                app_brand_name = txn_history_page.fetch_brand_text()
                logger.debug(f"Fetching brand name from txn history for the txn : {txn_id}, {app_brand_name}")
                app_imei_no = txn_history_page.fetch_imei_text()
                logger.debug(f"Fetching imei or serial no from txn history for the txn : {txn_id}, {app_imei_no}")
                app_scheme = txn_history_page.fetch_scheme_text()
                logger.debug(f"Fetching scheme from txn history for the txn : {txn_id}, {app_scheme}")

                txn_history_page.scroll_to_card_element()
                app_payment_status = txn_history_page.fetch_txn_status_text()
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
                    "emi_customer_name": app_customer_name,
                    "pmt_by": app_payment_by,
                    "card_type": app_card_type,
                    "emi_status": app_emi_status,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "additional_payback": app_additional_payback.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1],
                    "brand": app_brand_name,
                    "product": app_product,
                    "imei_no": app_imei_no,
                    "scheme": app_scheme,
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_date_and_time = date_time_converter.db_datetime(date_from_db=txn_created_time)
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
                    "monthly_emi": monthly_emi,
                    "interest_amt": total_interest,
                    "total_emi_amt": total_emi,
                    "net_cost": total_emi,
                    "emi_type": "BRAND_EMI",
                    "manufacturer": brand_name,
                    "product_name": brand_sku_name,
                    "sku_code": brand_sku_code,
                    "entity": "BRAND",
                    "subvention_type": "PAYBACK",
                    "subvention_amount": emi_payback_amount,
                    "subvention_rate": float(subvention_value)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS obtained for txnlist api is : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                api_amount = response['amount']
                logger.debug(f"Value of amount obtained from txnlist api : {api_amount}")
                api_payment_mode = response['paymentMode']
                logger.debug(f"Value of payment mode obtained from txnlist api : {api_payment_mode}")
                api_payment_status = response['status']
                logger.debug(f"Value of status obtained from txnlist api : {api_payment_status}")
                api_payment_state = response['states'][0]
                logger.debug(f"Value of states obtained from txnlist api : {api_payment_state}")
                api_mid = response['mid']
                logger.debug(f"Value of mid obtained from txnlist api : {api_mid}")
                api_tid = response['tid']
                logger.debug(f"Value of tid obtained from txnlist api : {api_tid}")
                api_acquirer_code = response['acquirerCode']
                logger.debug(f"Value of acquirerCode obtained from txnlist api : {api_acquirer_code}")
                api_settle_status = response['settlementStatus']
                logger.debug(f"Value of settlementStatus obtained from txnlist api : {api_settle_status}")
                api_rrn = response['rrNumber']
                logger.debug(f"Value of rrn obtained from txnlist api : {api_rrn}")
                api_issuer_code = response['issuerCode']
                logger.debug(f"Value of issuerCode obtained from txnlist api : {api_issuer_code}")
                api_txn_type = response['txnType']
                logger.debug(f"Value of txnType obtained from txnlist api : {api_txn_type}")
                api_org_code = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {api_org_code}")
                api_batch_number = response['batchNumber']
                logger.debug(f"Value of batchNumber obtained from txnlist api : {api_batch_number}")
                api_pmt_card_brand = response['paymentCardBrand']
                logger.debug(f"Value of paymentCardBrand obtained from txnlist api : {api_pmt_card_brand}")
                api_pmt_card_type = response['paymentCardType']
                logger.debug(f"Value of paymentCardType obtained from txnlist api : {api_pmt_card_type}")
                api_date_time = response['createdTime']
                logger.debug(f"Value of createdTime obtained from txnlist api : {api_date_time}")
                api_device_serial = response['deviceSerial']
                logger.debug(f"Value of deviceSerial obtained from txnlist api : {api_device_serial}")
                api_card_txn_type_desc = response['cardTxnTypeDesc']
                logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api : {api_card_txn_type_desc}")
                api_merchant_name = response['merchantName']
                logger.debug(f"Value of merchantName obtained from txnlist api : {api_merchant_name}")
                api_card_last_four_digit = response['cardLastFourDigit']
                logger.debug(f"Value of cardLastFourDigit obtained from txnlist api : {api_card_last_four_digit}")
                api_ext_ref_number = response['externalRefNumber']
                logger.debug(f"Value of externalRefNumber obtained from txnlist api : {api_ext_ref_number}")
                api_pmt_card_bin = response['paymentCardBin']
                logger.debug(f"Value of paymentCardBin obtained from txnlist api : {api_pmt_card_bin}")
                api_display_pan = response['displayPAN']
                logger.debug(f"Value of displayPAN obtained from txnlist api : {api_display_pan}")
                api_customer_name = response['customerName']
                logger.debug(f"Value of customerName obtained from txnlist api : {api_customer_name}")
                api_payer_name = response['payerName']
                logger.debug(f"Value of payerName obtained from txnlist api : {api_payer_name}")
                api_name_on_card = response['nameOnCard']
                logger.debug(f"Value of nameOnCard obtained from txnlist api : {api_name_on_card}")
                api_auth_code = response['authCode']
                logger.debug(f"Value of authCode obtained from txnlist api : {api_auth_code}")
                api_card_type = response['cardType']
                logger.debug(f"Value of cardType obtained from txnlist api : {api_card_type}")
                api_emi_term = response['emiTerm']
                logger.debug(f"Value of emiTerm obtained from txnlist api : {api_emi_term}")
                api_emi_status = response['emiStatus']
                logger.debug(f"Value of emiStatus obtained from txnlist api : {api_emi_status}")
                api_interest_rate = response['emiInterestRate']
                logger.debug(f"Value of emiInterestRate obtained from txnlist api : {api_interest_rate}")
                api_emi_type = response['externalRefNumber7']
                logger.debug(f"Value of externalRefNumber7 obtained from txnlist api : {api_emi_type}")
                api_monthly_emi = response['emiDetails']['emi']
                logger.debug(f"Value of emi obtained from txnlist api : {api_monthly_emi}")
                api_interest_amt = response['emiDetails']['interestAmount']
                logger.debug(f"Value of interestAmount obtained from txnlist api : {api_interest_amt}")
                api_loan_amt = response['emiDetails']['loanAmount']
                logger.debug(f"Value of loanAmount obtained from txnlist api : {api_loan_amt}")
                api_total_emi_amt = response['emiDetails']['totalAmountWithInt']
                logger.debug(f"Value of totalAmountWithInt obtained from txnlist api : {api_total_emi_amt}")
                api_manufacturer = response['emiDetails']['manufacturer']
                logger.debug(f"Value of manufacturer obtained from txnlist api : {api_manufacturer}")
                api_sku_code = response['emiDetails']['skuCode']
                logger.debug(f"Value of skuCode obtained from txnlist api : {api_sku_code}")
                api_product_name = response['emiDetails']['productName']
                logger.debug(f"Value of productName obtained from txnlist api : {api_product_name}")
                api_entity = response['emiDetails']['subventionDetails'][0]['entity']
                logger.debug(f"Value of entity obtained from txnlist api : {api_entity}")
                api_subvention_type = response['emiDetails']['subventionDetails'][0]['subventionType']
                logger.debug(f"Value of subventionType obtained from txnlist api : {api_subvention_type}")
                api_subvention_amt = response['emiDetails']['subventionDetails'][0]['subventionAmount']
                logger.debug(f"Value of subventionAmount obtained from txnlist api : {api_subvention_amt}")
                api_subvention_rate = response['emiDetails']['subventionDetails'][0]['subventionRate']
                logger.debug(f"Value of subventionAmount obtained from txnlist api : {api_subvention_rate}")
                api_scheme_name = response['emiDetails']['schemeName']
                logger.debug(f"Value of scheme name obtained from txnlist api : {api_scheme_name}")
                api_net_cost = response.get('emiDetails')['netCost']
                logger.debug(f"Value of netCost obtained from txnlist api : {api_net_cost}")

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
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "net_cost": api_net_cost,
                    "emi_type": api_emi_type,
                    "manufacturer": api_manufacturer,
                    "product_name": api_product_name,
                    "sku_code": api_sku_code,
                    "entity": api_entity,
                    "subvention_type": api_subvention_type,
                    "subvention_amount": api_subvention_amt,
                    "subvention_rate": api_subvention_rate
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                     "txn_amt": "{:.2f}".format(amount),
                     "pmt_mode": "CARD",
                     "pmt_status": "AUTHORIZED",
                     "pmt_state": "AUTHORIZED",
                     "acquirer_code": "HDFC",
                     "issuer_code": issuer_code,
                     "payer_name": "L3TEST/CARD0010",
                     "mid": mid,
                     "tid": tid,
                     "pmt_gateway": "DUMMY",
                     "txn_type": "CHARGE",
                     "settle_status": "PENDING",
                     "pmt_card_brand": "VISA",
                     "pmt_card_type": "CREDIT",
                     "device_serial": device_serial,
                     "order_id": order_id,
                     "org_code": org_code,
                     "pmt_card_bin": "417666",
                     "merchant_code": org_code,
                     "processer": 'EZETAP',
                     "terminal_info_id": terminal_info_id,
                     "card_txn_type": "03",
                     "card_last_four_digit": "0102",
                     "customer_name": "L3TEST/CARD0010",
                     "interest_rate": interest_rate,
                     "monthly_emi": monthly_emi,
                     "total_emi_amt": total_emi,
                     "scheme_code": scheme_code,
                     "emi_txn_amt": float(amount),
                     "emi_original_amt": float(amount),
                     "emi_status": "PENDING",
                     "emi_term": (f"{emi_plan_in_months} month"),
                     "emi_type": "BRAND_EMI",
                     "emi_payback_amount": api_subvention_amt,
                     "emi_total_amount": api_total_emi_amt,
                     "emi_cashback_type": 'PAYBACK',
                     "emi_interest_rate": interest_rate,
                     "brand_name": api_manufacturer,
                     "brand_sku": api_sku_code,
                     "brand_sku_code": api_sku_code,
                     "subvention_scheme_name": api_scheme_name,
                     "subvention_org_code": org_code,
                     "subvention_brand_id": str(brand_id),
                     "subvention_card_type": 'CREDIT',
                     "subvention_entity": "BRAND",
                     "subvention_type": "PAYBACK",
                     "subvention_value_type": "PERCENTAGE",
                     "subvention_tenure": (f"{emi_plan_in_months} month"),
                     "subvention_discount_type": "Additional"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": "{:.2f}".format(amount_db),
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code_db,
                    "payer_name": payer_name_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "txn_type": txn_type_db,
                    "settle_status": settlement_status_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "device_serial": device_serial_db,
                    "order_id": order_id_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "customer_name": customer_name_db,
                    "merchant_code": merchant_code_db,
                    "processer": processer_db,
                    "interest_rate": emi_interest_rate,
                    "emi_status": emi_status,
                    "emi_term": emi_term,
                    "emi_type": emi_type_db,
                    "monthly_emi": emi_amount_monthly,
                    "total_emi_amt": emi_total_amount,
                    "scheme_code": emi_scheme_code,
                    "emi_txn_amt": emi_txn_amount,
                    "emi_original_amt": emi_original_amount,
                    "emi_payback_amount": emi_payback_amount,
                    "emi_total_amount": emi_total_amount,
                    "emi_cashback_type": emi_cashback_type,
                    "emi_interest_rate": emi_interest_rate,
                    "brand_name": brand_name,
                    "brand_sku": brand_sku_code,
                    "brand_sku_code": brand_sku_code ,
                    "subvention_scheme_name": subvention_plan_scheme_name,
                    "subvention_org_code": subvention_plan_org_code,
                    "subvention_brand_id": subvention_plan_brand_id,
                    "subvention_card_type": subvention_plan_card_type,
                    "subvention_entity": subvention_entity,
                    "subvention_type": subvention_type,
                    "subvention_value_type": subvention_value_type,
                    "subvention_tenure": subvention_tenure,
                    "subvention_discount_type": subvention_discount_type
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

        # -----------------------------------------Start of Portal Validation-------------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "date": txn_date,
                    "time": txn_time,
                    "TID": tid,
                    "BATCH NO": batch_number,
                    "INVOICE NO": invoice_number,
                    "APP": "Visa Credit",
                    "payment_option": "EMI SALE",
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "CARD TYPE": "VISA",
                    "AUTH CODE": str(auth_code).strip(),
                    "RRN": rrn,
                    "EMI Txn Id": txn_id,
                    "Tenure": f"{emi_plan_in_months} month",
                    "Card Issuer": f"{issuer_code} Bank",
                    "Payback": f"{subvention_value}%",
                    "Total Payback Amount": "Rs." + "{:.2f}".format(emi_payback_amount),
                    "Loan Amount": "Rs." + "{:.2f}".format(amount - cal_additional_payback),
                    "Applicable Intt Rate(P.A.)": f"{interest_rate}%",
                    "Interest Amt": "Rs." + "{:.2f}".format(total_interest),
                    "EMI Amt": "Rs." + "{:.2f}".format(monthly_emi),
                    "Total Amt with Interest": "Rs." + "{:.2f}".format(total_emi),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "Manufacturer Name": brand_name,
                    "Product Name": brand_sku_name,
                    "Product Desc": brand_sku_code,
                    "Sr. No.": str(imei_no),
                    "pin_verified_section_text": "PIN VERIFIED OK",
                    "unnamed_section_text": f"{customer_name_db} I agree to pay as per the card issuer agreement.",
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id,{"username": app_username,"password": app_password},expected_details=expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        try:
            query = f"update emi set interest_rate='{interest_rate}' where org_code='{org_code}' and " \
                    f"issuer_code='HDFC' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                    f"and tid_type='SUBVENTION'"
            logger.debug(f"Reverting back the  updated interest_rate in emi table : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Fetching result after reverting back the  updated interest_rate in emi table :{result}")

            query = f"update subvention_plan_details set subvention_value='{sub_value}' where subvention_plan_id='{subvention_plan_id}' and " \
                    f"subventing_entity='BRAND' and subvention_value_type= 'PERCENTAGE' and subvention_type='PAYBACK' and tenure='{emi_plan_in_months} month' ;"
            logger.debug(f"Reverting back the  updated subvention_value in subvention_plan_details table : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Fetching result after reverting back the updated subvention_value in subvention_plan_details table : {result}")

            refresh_db()
            logger.debug(f"Refreshing the DB after reverting interest_rate and subvention_value : {result}")
        except Exception as e:
            logger.exception(f"Query updation failed due to expection : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_07_088():
    """
        Sub Feature Code: UI_Common_Card_Brand_EMI_Cashback_by_Brand_Percentage_With_No_Cost_EMI_Success_Txn_For_An_Org_HDFC_Dummy_PG_ICICI_Issuer_EMV_MASTER_CREDIT_Without_Pin_541333_For_3_Months_Tenure
        Sub Feature Description: Performing the brand EMI cashback by brand percentage with no cost emi success transaction for an org via HDFC Dummy PG ICICI isssuer using EMV MASTER Credit card without pin for 3 months tenure (bin: 541333)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand EMI, 023: TC023
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

        # Below function to update bank_code, bank for the bin: 541333
        testsuite_teardown.update_bin_info(bin_number='541333', bank_code='ICICI', bank='ICICI')

        query = f"select bank_code from bin_info where bin='541333'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
        logger.debug(f"Active emi setting for credit card")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='ICICI' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
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
        tid_type = result['tid_type'].values[0]
        logger.debug(f"Fetching tid_type from the emi table : {tid_type}")
        card_type = result['card_type'].values[0]
        logger.debug(f"Fetching card_type from the emi table : {card_type}")
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
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        # From brand_sku_Details picking the first product_name
        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand_sku_details table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")
        brand_sku_category = result['sku_category'].values[0]
        logger.debug(f"Fetching sku_category value from the brand_sku_details table : {brand_sku_category}")
        brand_sku_code = result['sku_code'].values[0]
        logger.debug(f"Fetching sku_code value from the brand_sku_details table : {brand_sku_code}")

        query = f"select * from subvention_plan where brand_id='{brand}' and org_code='{org_code}' and card_type= 'CREDIT' and bank='ICICI' and eze_emi_enabled=b'0' order by created_time desc limit 1;"
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
        subvention_plan_scheme_name = result['scheme_name'].values[0]
        logger.debug(f"Fetching scheme_name from subvention_plan table : {subvention_plan_scheme_name}")

        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity='BRAND' and subvention_type='CASHBACK' and subvention_value_type='PERCENTAGE' and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        query = f"update emi set interest_rate='15.99' where org_code='{org_code}' and " \
                f"issuer_code='ICICI' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Updating the emi setting with interest_rate : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Fetching result after updating emi table with interest_rate :{result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the emi interest_rate and subvention_plan_details")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity='BRAND' " \
                f"and subvention_value_type= 'PERCENTAGE' and subvention_type='CASHBACK' and tenure='{emi_plan_in_months} month' ;"
        logger.debug(f"Query to fetch data from the subvention_plan_details table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for subvention_plan_details table : {result}")
        sub_value = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value from subvention_plan_details table : {sub_value}")

        query = f"update subvention_plan_details set subvention_value='2.68' where subvention_plan_id='{subvention_plan_id}' and subventing_entity='BRAND' " \
                f"and subvention_value_type= 'PERCENTAGE' and subvention_type='CASHBACK' and tenure='{emi_plan_in_months} month' ;"
        logger.debug(f"Updating the subvention_value in subvention_plan_details table : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result after updating subvention_value in subvention_plan_details table : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity='BRAND' and" \
                f" subvention_value_type= 'PERCENTAGE' and subvention_type='CASHBACK' and tenure='{emi_plan_in_months} month' ;"
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
        subvention_subvention_limit = result['subvention_limit'].values[0]
        logger.debug(f"Fetching subvention_limit from subvention_plan_details table : {subvention_subvention_limit}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'DEBIT', 'ACTIVE')
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
            logger.debug(f"Entered amount, order_id and device_serial is : {amount}, {order_id}, {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_MASTER_CREDIT_541333")
            card_page.select_cardtype("EMV_MASTER_CREDIT_541333")
            logger.debug(f"Selected the card type as : EMV_MASTER_CREDIT_541333")

            # Condition for no cost emi
            no_cost_emi_text = payment_page.fetch_emi_cost_text(emi_plan_in_months)
            if no_cost_emi_text.split('@' '')[-1] == 'NoCost':
                payment_page.select_emi_plan(emi_plan_in_months)
                logger.debug(f"Selected the emi plan in months : {emi_plan_in_months}")
                payment_page.click_on_proceed_homepage()

                # Calculating the emi's using formula
                monthly_interest_rate = interest_rate / (12 * 100)
                logger.debug(f"monthly_interest_rate is : {monthly_interest_rate}")
                cal_monthly_emi_amt = amount * monthly_interest_rate * (
                            (1 + monthly_interest_rate) ** emi_plan_in_months) / (
                                              (1 + monthly_interest_rate) ** emi_plan_in_months - 1)
                logger.debug(f"cal_monthly_emi_amt is : {cal_monthly_emi_amt}")
                monthly_emi = round(cal_monthly_emi_amt, 2)
                logger.debug(f"Calculated monthly_emi amount : {monthly_emi}")
                cal_total_emi_amt = monthly_emi * emi_plan_in_months
                logger.debug(f"cal_total_emi_amt is : {cal_total_emi_amt}")
                total_emi = round(cal_total_emi_amt, 2)
                logger.debug(f"calculated total_emi amount : {total_emi}")
                cal_total_interest = total_emi - amount
                logger.debug(f"cal_total_interest is : {cal_total_interest}")
                total_interest = round(cal_total_interest, 2)
                logger.debug(f"calculated total_interest amount : {total_interest}")

                query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
                logger.debug(f"Query to fetch data from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for txn table : {result}")
                txn_created_time = result['created_time'].values[0]
                logger.debug(f"Fetching created_time value from the txn table : {txn_created_time}")
                txn_id = result['id'].values[0]
                logger.debug(f"Fetching txn_id value from the txn table : {txn_id}")
                rrn = result['rr_number'].values[0]
                logger.debug(f"Fetching rrn value from the txn table : {rrn}")
                auth_code = result['auth_code'].values[0]
                logger.debug(f"Fetching auth_code value from the txn table : {auth_code}")
                batch_number = result['batch_number'].values[0]
                logger.debug(f"Fetching batch_number value from the txn table : {batch_number}")
                amount_db = result['amount'].values[0]
                logger.debug(f"Fetching amount value from the txn table : {amount_db}")
                original_amt_db = result['amount_original'].values[0]
                logger.debug(f"Fetching amount_original value from the txn table : {original_amt_db}")
                amt_cash_back_db = result['amount_cash_back'].values[0]
                logger.debug(f"Fetching amount_cash_back value from the txn table : {amt_cash_back_db}")
                payment_mode_db = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode value from the txn table : {payment_mode_db}")
                payment_status_db = result['status'].values[0]
                logger.debug(f"Fetching status value from the txn table : {payment_status_db}")
                payment_state_db = result['state'].values[0]
                logger.debug(f"Fetching state value from the txn table : {payment_state_db}")
                acquirer_code_db = result['acquirer_code'].values[0]
                logger.debug(f"Fetching acquirer_code value from the txn table : {acquirer_code_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching mid value from the txn table : {mid_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching tid value from the txn table : {tid_db}")
                payment_gateway_db = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway value from the txn table : {payment_gateway_db}")
                settlement_status_db = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status value from the txn table : {settlement_status_db}")
                device_serial_db = result['device_serial'].values[0]
                logger.debug(f"Fetching device_serial value from the txn table : {device_serial_db}")
                merchant_name = result['merchant_name'].values[0]
                logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name}")
                merchant_code_db = result["merchant_code"].iloc[0]
                logger.debug(f"Fetching merchant_code value from the txn table : {merchant_code_db}")
                auth_code_db = result['auth_code'].iloc[0]
                logger.debug(f"Fetching auth_code value from the txn table : {auth_code_db}")
                rrn_db = result['rr_number'].iloc[0]
                logger.debug(f"Fetching rr_number value from the txn table : {rrn_db}")
                payment_card_brand_db = result["payment_card_brand"].iloc[0]
                logger.debug(f"Fetching payment_card_brand value from the txn table : {payment_card_brand_db}")
                payment_card_type_db = result["payment_card_type"].iloc[0]
                logger.debug(f"Fetching payment_card_type value from the txn table : {payment_card_type_db}")
                issuer_code_db = result["issuer_code"].iloc[0]
                logger.debug(f"Fetching issuer_code value from the txn table : {issuer_code_db}")
                payment_card_bin_db = result["payment_card_bin"].iloc[0]
                logger.debug(f"Fetching payment_card_bin value from the txn table : {payment_card_bin_db}")
                terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Fetching terminal_info_id value from the txn table : {terminal_info_id_db}")
                txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type value from the txn table : {txn_type_db}")
                card_txn_type_db = result["card_txn_type"].iloc[0]
                logger.debug(f"Fetching card_txn_type value from the txn table : {card_txn_type_db}")
                card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
                logger.debug(f"Fetching card_last_four_digit value from the txn table : {card_last_four_digit_db}")
                customer_name_db = result["customer_name"].values[0]
                logger.debug(f"Fetching customer_name value from the txn table : {customer_name_db}")
                payer_name_db = result["payer_name"].values[0]
                logger.debug(f"Fetching payer_name value from the txn table : {payer_name_db}")
                org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code value from the txn table : {org_code_db}")
                order_id_db = result["external_ref"].iloc[0]
                logger.debug(f"Fetching external_ref value from the txn table : {order_id_db}")
                emi_type_db = result['external_ref7'].values[0]
                logger.debug(f"Fetching external_ref7 from the txn table : {emi_type_db}")
                invoice_number = result['pg_invoice_number'].values[0]
                logger.debug(f"Fetching pg_invoice_number from the txn table : {invoice_number}")
                posting_date = result['posting_date'].values[0]
                logger.debug(f"Fetching posting_date from txn table : {posting_date}")

                query = f"select * from txn_emi where id='{txn_id}';"
                logger.debug(f"Query to fetch data from the txn_emi table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for txn_emi table : {result}")
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
                emi_cashback_amount = result['emi_cashback_amount'].values[0]
                logger.debug(f"Fetching emi cashback amount from txn_emi table : {emi_cashback_amount}")
                emi_cashback_type = result['emi_cashback_type'].values[0]
                logger.debug(f"Fetching emi cashback type from txn_emi table : {emi_cashback_type}")
                processer_db = result['processor'].values[0]
                logger.debug(f"Fetching processer value from the txn_emi table : {processer_db}")

            else:
                raise Exception("There is no configuration obtained for selected tenure")

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
                    "card_type_desc": "*1034 EMV",
                    "mid": mid,
                    "tid": tid,
                    "customer_name": "MASTERCARD",
                    "pmt_by": "EMV",
                    "card_type": "MasterCard",
                    "emi_status": "PENDING",
                    "emi_customer_name": "MASTERCARD",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "cashback": "{:,.2f}".format(emi_cashback_amount),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "brand": brand_name,
                    "product": brand_sku_name,
                    "imei_no": str(imei_no),
                    "scheme": subvention_plan_scheme_name
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
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
                logger.debug(f"Fetching total emi amount from txn history for the txn : {txn_id}, {app_total_emi_amount}")
                app_cashback = txn_history_page.fetch_cashback_text()
                logger.debug(f"Fetching cashback from txn history for the txn : {txn_id}, {app_cashback}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the txn : {txn_id}, {app_net_effective_price}")
                app_product = txn_history_page.fetch_product_text()
                logger.debug(f"Fetching product from txn history for the txn : {txn_id}, {app_product}")
                app_brand_name = txn_history_page.fetch_brand_text()
                logger.debug(f"Fetching brand name from txn history for the txn : {txn_id}, {app_brand_name}")
                app_imei_no = txn_history_page.fetch_imei_text()
                logger.debug(f"Fetching imei or serial no from txn history for the txn : {txn_id}, {app_imei_no}")
                app_scheme = txn_history_page.fetch_scheme_text()
                logger.debug(f"Fetching scheme from txn history for the txn : {txn_id}, {app_scheme}")

                txn_history_page.scroll_to_card_element()
                app_payment_status = txn_history_page.fetch_txn_status_text()
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
                    "emi_status": app_emi_status,
                    "emi_customer_name": app_customer_name,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "cashback": app_cashback.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1],
                    "brand": app_brand_name,
                    "product": app_product,
                    "imei_no": app_imei_no,
                    "scheme": app_scheme
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_date_and_time = date_time_converter.db_datetime(date_from_db=txn_created_time)
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
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "date": expected_date_and_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "EMV",
                    "auth_code": auth_code,
                    "card_last_four_digit": "1034",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "541333",
                    "card_type": "MasterCard",
                    "display_pan": "1034",
                    "customer_name": "MASTERCARD/CARDHOLDER",
                    "payer_name": "MASTERCARD/CARDHOLDER",
                    "name_on_card": "MASTERCARD/CARDHOLDER",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "emi_interest_rate": interest_rate,
                    "monthly_emi": monthly_emi,
                    "interest_amt": total_interest,
                    "total_amount_with_int": total_emi,
                    "total_emi_amt": total_emi,
                    "net_cost": total_emi,
                    "emi_type": "BRAND_EMI",
                    "manufacturer": brand_name,
                    "product_name": brand_sku_name,
                    "sku_code": brand_sku_code,
                    "product_serial": str(imei_no),
                    "entity": "BRAND",
                    "subvention_type": "CASHBACK",
                    "subvention_amount": emi_cashback_amount,
                    "subvention_fixed": emi_cashback_amount,
                    "scheme_name": subvention_plan_scheme_name,
                    "total_cashback": emi_cashback_amount,
                    "user_agreement": f"I agree to pay as per the card issuer agreement. I understand that purchase(s) would be converted into EMI at the sole discretion of the Bank by charging an interest of {interest_rate}% on the monthly reducing balance."
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS obtained for txnlist api is : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                api_amount = response['amount']
                logger.debug(f"Value of amount obtained from txnlist api : {api_amount}")
                api_payment_mode = response['paymentMode']
                logger.debug(f"Value of payment mode obtained from txnlist api : {api_payment_mode}")
                api_payment_status = response['status']
                logger.debug(f"Value of status obtained from txnlist api : {api_payment_status}")
                api_payment_state = response['states'][0]
                logger.debug(f"Value of states obtained from txnlist api : {api_payment_state}")
                api_mid = response['mid']
                logger.debug(f"Value of mid obtained from txnlist api : {api_mid}")
                api_tid = response['tid']
                logger.debug(f"Value of tid obtained from txnlist api : {api_tid}")
                api_acquirer_code = response['acquirerCode']
                logger.debug(f"Value of acquirerCode obtained from txnlist api : {api_acquirer_code}")
                api_settle_status = response['settlementStatus']
                logger.debug(f"Value of settlementStatus obtained from txnlist api : {api_settle_status}")
                api_rrn = response['rrNumber']
                logger.debug(f"Value of rrn obtained from txnlist api : {api_rrn}")
                api_issuer_code = response['issuerCode']
                logger.debug(f"Value of issuerCode obtained from txnlist api : {api_issuer_code}")
                api_txn_type = response['txnType']
                logger.debug(f"Value of txnType obtained from txnlist api : {api_txn_type}")
                api_org_code = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {api_org_code}")
                api_batch_number = response['batchNumber']
                logger.debug(f"Value of batchNumber obtained from txnlist api : {api_batch_number}")
                api_pmt_card_brand = response['paymentCardBrand']
                logger.debug(f"Value of paymentCardBrand obtained from txnlist api : {api_pmt_card_brand}")
                api_pmt_card_type = response['paymentCardType']
                logger.debug(f"Value of paymentCardType obtained from txnlist api : {api_pmt_card_type}")
                api_date_time = response['createdTime']
                logger.debug(f"Value of createdTime obtained from txnlist api : {api_date_time}")
                api_device_serial = response['deviceSerial']
                logger.debug(f"Value of deviceSerial obtained from txnlist api : {api_device_serial}")
                api_card_txn_type_desc = response['cardTxnTypeDesc']
                logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api : {api_card_txn_type_desc}")
                api_merchant_name = response['merchantName']
                logger.debug(f"Value of merchantName obtained from txnlist api : {api_merchant_name}")
                api_card_last_four_digit = response['cardLastFourDigit']
                logger.debug(f"Value of cardLastFourDigit obtained from txnlist api : {api_card_last_four_digit}")
                api_ext_ref_number = response['externalRefNumber']
                logger.debug(f"Value of externalRefNumber obtained from txnlist api : {api_ext_ref_number}")
                api_pmt_card_bin = response['paymentCardBin']
                logger.debug(f"Value of paymentCardBin obtained from txnlist api : {api_pmt_card_bin}")
                api_display_pan = response['displayPAN']
                logger.debug(f"Value of displayPAN obtained from txnlist api : {api_display_pan}")
                api_customer_name = response['customerName']
                logger.debug(f"Value of customerName obtained from txnlist api : {api_customer_name}")
                api_payer_name = response['payerName']
                logger.debug(f"Value of payerName obtained from txnlist api : {api_payer_name}")
                api_name_on_card = response['nameOnCard']
                logger.debug(f"Value of nameOnCard obtained from txnlist api : {api_name_on_card}")
                api_auth_code = response['authCode']
                logger.debug(f"Value of authCode obtained from txnlist api : {api_auth_code}")
                api_card_type = response['cardType']
                logger.debug(f"Value of cardType obtained from txnlist api : {api_card_type}")
                api_emi_term = response['emiTerm']
                logger.debug(f"Value of emiTerm obtained from txnlist api : {api_emi_term}")
                api_emi_status = response['emiStatus']
                logger.debug(f"Value of emiStatus obtained from txnlist api : {api_emi_status}")
                api_interest_rate = response['emiInterestRate']
                logger.debug(f"Value of emiInterestRate obtained from txnlist api : {api_interest_rate}")
                api_emi_type = response['externalRefNumber7']
                logger.debug(f"Value of externalRefNumber7 obtained from txnlist api : {api_emi_type}")
                api_monthly_emi = response['emiDetails']['emi']
                logger.debug(f"Value of emi obtained from txnlist api : {api_monthly_emi}")
                api_interest_amt = response['emiDetails']['interestAmount']
                logger.debug(f"Value of interestAmount obtained from txnlist api : {api_interest_amt}")
                api_loan_amt = response['emiDetails']['loanAmount']
                logger.debug(f"Value of loanAmount obtained from txnlist api : {api_loan_amt}")
                api_total_emi_amt = response['emiDetails']['totalAmountWithInt']
                logger.debug(f"Value of totalAmountWithInt obtained from txnlist api : {api_total_emi_amt}")
                api_manufacturer = response['emiDetails']['manufacturer']
                logger.debug(f"Value of manufacturer obtained from txnlist api : {api_manufacturer}")
                api_sku_code = response['emiDetails']['skuCode']
                logger.debug(f"Value of skuCode obtained from txnlist api : {api_sku_code}")
                api_product_serial = response['emiDetails']['productSerial']
                logger.debug(f"Value of productSerial obtained from txnlist api : {api_product_serial}")
                api_product_name = response['emiDetails']['productName']
                logger.debug(f"Value of productName obtained from txnlist api : {api_product_name}")
                api_entity = response['emiDetails']['subventionDetails'][0]['entity']
                logger.debug(f"Value of entity obtained from txnlist api : {api_entity}")
                api_subvention_type = response['emiDetails']['subventionDetails'][0]['subventionType']
                logger.debug(f"Value of subventionType obtained from txnlist api : {api_subvention_type}")
                api_subvention_amt = response['emiDetails']['subventionDetails'][0]['subventionAmount']
                logger.debug(f"Value of subventionAmount obtained from txnlist api : {api_subvention_amt}")
                api_scheme_name = response['emiDetails']['schemeName']
                logger.debug(f"Value of scheme name obtained from txnlist api : {api_scheme_name}")
                api_net_cost = response['emiDetails']['netCost']
                logger.debug(f"Value of netCost obtained from txnlist api : {api_net_cost}")
                api_total_amt_with_int = response['emiDetails']['totalAmountWithInt']
                logger.debug(f"Value of totalAmountWithInt obtained from txnlist api : {api_total_amt_with_int}")
                api_total_cashback = response['emiDetails']['totalCashBack']
                logger.debug(f"Value of totalCashBack obtained from txnlist api : {api_total_cashback}")
                api_useragreement = response['userAgreement']
                logger.debug(f"Value of 'userAgreement' obtained from txnlist api : {api_useragreement}")

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
                    "emi_interest_rate": api_interest_rate,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "net_cost": api_net_cost,
                    "total_amount_with_int": api_total_amt_with_int,
                    "emi_type": api_emi_type,
                    "manufacturer": api_manufacturer,
                    "product_name": api_product_name,
                    "sku_code": api_sku_code,
                    "product_serial": api_product_serial,
                    "entity": api_entity,
                    "subvention_type": api_subvention_type,
                    "subvention_amount": api_subvention_amt,
                    "subvention_fixed": api_subvention_amt,
                    "scheme_name": api_scheme_name,
                    "total_cashback": api_total_cashback,
                    "user_agreement": api_useragreement
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "txn_amt": "{:.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": "MASTERCARD/CARDHOLDER",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "txn_type": "CHARGE",
                    "settle_status": "PENDING",
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "541333",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "02",
                    "card_last_four_digit": "1034",
                    "customer_name": "MASTERCARD/CARDHOLDER",
                    "interest_rate": interest_rate,
                    "monthly_emi": monthly_emi,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_amt": float(monthly_emi),
                    "tid_type": "SUBVENTION",
                    "card_type": "CREDIT",
                    "emi_original_amt": float(amount),
                    "emi_status": "PENDING",
                    "emi_term": (f"{emi_plan_in_months} month"),
                    "emi_type": "BRAND_EMI",
                    "emi_cashback_amount": api_subvention_amt,
                    "emi_total_amount": api_total_emi_amt,
                    "emi_cashback_type": 'CASHBACK',
                    "emi_interest_rate": interest_rate,
                    "brand_name": api_manufacturer,
                    "brand_sku": api_sku_code,
                    "brand_sku_code": api_sku_code,
                    "subvention_scheme_name": api_scheme_name,
                    "subvention_org_code": org_code,
                    "subvention_brand_id": str(brand_id),
                    "subvention_card_type": 'CREDIT',
                    "subvention_entity": "BRAND",
                    "subvention_type": "CASHBACK",
                    "subvention_value_type": "PERCENTAGE",
                    "subvention_tenure": (f"{emi_plan_in_months} month"),
                    "subvention_discount_type": "Additional",
                    "processer": "EZETAP"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": "{:.2f}".format(amount_db),
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code_db,
                    "payer_name": payer_name_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "txn_type": txn_type_db,
                    "settle_status": settlement_status_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "device_serial": device_serial_db,
                    "merchant_code": merchant_code_db,
                    "auth_code": auth_code_db,
                    "rrn": rrn_db,
                    "order_id": order_id_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "customer_name": customer_name_db,
                    "interest_rate": emi_interest_rate,
                    "emi_status": emi_status,
                    "emi_term": emi_term,
                    "emi_type": emi_type_db,
                    "monthly_emi": emi_amount_monthly,
                    "total_emi_amt": emi_total_amount,
                    "scheme_code": emi_scheme_code,
                    "emi_txn_amt": emi_txn_amount,
                    "emi_amt": emi_amount_monthly,
                    "tid_type": tid_type,
                    "card_type": card_type,
                    "emi_original_amt": emi_original_amount,
                    "emi_cashback_amount": emi_cashback_amount,
                    "emi_total_amount": emi_total_amount,
                    "emi_cashback_type": emi_cashback_type,
                    "emi_interest_rate": emi_interest_rate,
                    "brand_name": brand_name,
                    "brand_sku": brand_sku_code,
                    "brand_sku_code": brand_sku_code ,
                    "subvention_scheme_name": subvention_plan_scheme_name,
                    "subvention_org_code": subvention_plan_org_code,
                    "subvention_brand_id": subvention_plan_brand_id,
                    "subvention_card_type": subvention_plan_card_type,
                    "subvention_entity": subvention_entity,
                    "subvention_type": subvention_type,
                    "subvention_value_type": subvention_value_type,
                    "subvention_tenure": subvention_tenure,
                    "subvention_discount_type": subvention_discount_type,
                    "processer": processer_db
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

        # -----------------------------------------Start of Portal Validation-------------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "date": txn_date,
                    "time": txn_time,
                    "BATCH NO": batch_number,
                    "INVOICE NO": invoice_number,
                    "APP": "MASTERCARD",
                    "payment_option": "EMI SALE",
                    "CARD": f"XXXX-XXXX-XXXX-1034 EMV",
                    "CARD TYPE": "MasterCard",
                    "AUTH CODE": str(auth_code).strip(),
                    "TID": tid,
                    "RRN": rrn,
                    "EMI Txn Id": txn_id,
                    "Tenure": f"{emi_plan_in_months} month",
                    "Card Issuer": f"{issuer_code} Bank",
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "Merch./Mfr Subvention Cashback": f"{subvention_value}%",
                    "Total Cashback Amt": "Rs. " + "{:.2f}".format(emi_cashback_amount),
                    "Manufacturer Name": brand_name,
                    "Product Name": brand_sku_name,
                    "Product Desc": brand_sku_code,
                    "Sr. No.": str(imei_no),
                    "unnamed_section_text": f"{customer_name_db} I agree to pay as per the card issuer agreement.",
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id,{"username": app_username,"password": app_password},expected_details=expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        try:
            query = f"update emi set interest_rate='{interest_rate}' where org_code='{org_code}' and " \
                f"issuer_code='ICICI' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
            logger.debug(f"Reverting back the  updated interest_rate in emi table : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Fetching result after reverting back the  updated interest_rate in emi table :{result}")

            query = f"update subvention_plan_details set subvention_value='{sub_value}' where subvention_plan_id='{subvention_plan_id}' and subventing_entity='BRAND' " \
                    f"and subvention_value_type= 'PERCENTAGE' and subvention_type='CASHBACK' and tenure='{emi_plan_in_months} month' ;"
            logger.debug(f"Reverting back the subvention_value in subvention_plan_details table : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result after reverting back subvention_value in subvention_plan_details table : {result}")
            refresh_db()
            logger.debug(f"DB refresh after reverting subvention_value and interest_rate : {result}")

        except Exception as e:
            logger.exception(f"Query updation failed due to expection : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_07_089():
    """
    Sub Feature Code: UI_Common_Card_Brand_EMI_BO_Instant_Discount_Cashback_by_Brand_Fixed_Success_Txn_For_An_Org_HDFC_Dummy_HDFC_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
    Sub Feature Description: Performing the brand EMI BO Instant Discount cashback by brand fixed success transaction for an org (not ezetap)
    via HDFC Dummy PG for HDFC issuer using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand_EMI, 089: TC089
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
        api_details["RequestBody"]["settings"]["boCashbackEnabled"] = "true"
        api_details["RequestBody"]["settings"]["businessDiscountEnabled"] = "true"
        api_details["RequestBody"]["settings"]["boInstantDiscountEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi, businessDiscountEnabled, boInstantDiscountEnabled and bocashback is enabled in preconditions settings : {response}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
        logger.debug(f"Active emi setting for credit card")

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

        query = f"select * from subvention_plan where brand_id='{brand_id}' and org_code='{org_code}'" \
                f" and card_type= 'CREDIT' and bank='HDFC' and eze_emi_enabled=b'0';"
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

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and " \
                f"subventing_entity ='BRAND' and subvention_value_type= 'FIXED' and subvention_type='CASHBACK' " \
                f"and tenure='{emi_plan_in_months} month' ;"
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

        testsuite_teardown.update_rule_status(org_code=org_code, credit_type='INSTANT', status='ACTIVE')
        logger.debug(f"updated rule status activated INSTANT BO")

        testsuite_teardown.update_rule_status(org_code=org_code, credit_type='CASHBACK', status='INACTIVE')
        logger.debug(f"updated rule status inactivated CASHBACK BO")

        query = f"select * from rule where org_code='{org_code}' and credit_type='INSTANT' and name LIKE '{brand_name}%'"
        logger.debug(f"Query to fetch data from the rule table : {query}")
        result = DBProcessor.getValueFromDB(query=query, db_name='rule_engine')
        logger.debug(f"Fetching result from rule table :{result}")
        rule_id = result['id'].values[0]
        logger.debug(f"Fetching id from the rule table : {rule_id}")

        query = f"select * from subvention_split where rule_id='{rule_id}' and sku_codes='{brand_sku_code}'"
        logger.debug(f"Query to fetch data from the subvention_split table : {query}")
        result = DBProcessor.getValueFromDB(query=query, db_name='rule_engine')
        logger.debug(f"Fetching result from subvention_split table :{result}")
        discount_value_bank = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value by bank from the subvention_split table : {discount_value_bank}")
        discount_value_brand = result['subvention_value'].values[1]
        logger.debug(f"Fetching subvention_value by brand from the subvention_split table : {discount_value_brand}")
        total_discount_value = discount_value_bank + discount_value_brand
        logger.debug(f"total discount value : {total_discount_value}")

        # updating the status as inactive in subvention_plan_details table
        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity='BRAND' and subvention_type='CASHBACK' and subvention_value_type='FIXED' and tenure='{emi_plan_in_months} month'"
        logger.debug(f"Query to update subvention_plan_details with status as ACTIVE : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from subvention_plan_details for status as ACTIVE : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after updating the status as active in subvention_plan_details table")

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
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_brand_emi_pmt_mode()
            logger.debug(f"Selected payment mode is Brand EMI")
            payment_page.click_and_enter_search_products_or_brands(prod=brand_sku_name)
            logger.debug(f"Entered the products")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            payment_page.click_and_enter_imei_no(imei_no)
            logger.debug(f"Entered IMEI number, {imei_no}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan(emi_plan_in_months)
            logger.debug(f"Selected the emi plan in months : {emi_plan_in_months}")
            payment_page.click_on_proceed_homepage()

            logger.debug(f"Started calculating emi part")
            final_amount = amount - total_discount_value
            logger.debug(f"final amount after deducting discount amount: {final_amount}")
            monthly_interest_rate = interest_rate / (12 * 100)
            logger.debug(f"monthly_interest_rate is : {monthly_interest_rate}")
            cal_monthly_emi_amt = final_amount * monthly_interest_rate * (
                    (1 + monthly_interest_rate) ** emi_plan_in_months) / (
                                          (1 + monthly_interest_rate) ** emi_plan_in_months - 1)
            logger.debug(f"cal_monthly_emi_amt is : {cal_monthly_emi_amt}")
            monthly_emi = round(cal_monthly_emi_amt, 2)
            logger.debug(f"Calculated monthly_emi amount : {monthly_emi}")
            total_emi = round((monthly_emi * emi_plan_in_months), 2)
            logger.debug(f"total_emi amount is : {total_emi}")
            total_interest = round((total_emi - final_amount), 2)
            logger.debug(f"total_interest amount is : {total_interest}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table : {txn_created_time}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table : {batch_number}")
            amount_db = result['amount'].values[0]
            logger.debug(f"Fetching amount value from the txn table : {amount_db}")
            amt_cash_back_db = result['amount_cash_back'].values[0]
            logger.debug(f"Fetching amount_cash_back value from the txn table : {amt_cash_back_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode value from the txn table : {payment_mode_db}")
            payment_status_db = result['status'].values[0]
            logger.debug(f"Fetching status value from the txn table : {payment_status_db}")
            payment_state_db = result['state'].values[0]
            logger.debug(f"Fetching state value from the txn table : {payment_state_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from the txn table : {acquirer_code_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid value from the txn table : {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid value from the txn table : {tid_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from the txn table : {payment_gateway_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status value from the txn table : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the txn table : {device_serial_db}")
            sale_amt_db = result['amount_original'].values[0]
            logger.debug(f"Fetching amount_original value from the txn table : {sale_amt_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table : {payment_card_type_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer_code value from the txn table : {issuer_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer_name value from the txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer_name value from the txn table : {payer_name_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table : {org_code_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table : {order_id_db}")
            emi_type_db = result['external_ref7'].values[0]
            logger.debug(f"Fetching external_ref7 from the txn table : {emi_type_db}")
            invoice_number = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg_invoice_number from the txn table : {invoice_number}")
            amount_original = result['amount_original'].values[0]
            logger.debug(f"Fetching amount_original from the txn table : {amount_original}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")

            query = f"select * from txn_emi where id='{txn_id}';"
            logger.debug(f"Query to fetch data from the txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn_emi table : {result}")
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
            emi_cashback_fixed = result['emi_cashback_fixed'].values[0]
            logger.debug(f"Fetching emi cashback fixed amount from txn_emi table : {emi_cashback_fixed}")
            emi_cashback_amount = result['emi_cashback_amount'].values[0]
            logger.debug(f"Fetching emi cashback amount from txn_emi table : {emi_cashback_amount}")
            emi_cashback_type = result['emi_cashback_type'].values[0]
            logger.debug(f"Fetching emi cashback type from txn_emi table : {emi_cashback_type}")

            query = f"select * from bo_txn where txn_id='{txn_id}'"
            logger.debug(f"Query to fetch data from bo_txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query, db_name='rule_engine')
            logger.debug(f"Fetching result for bo_txn table : {result} ")
            discount_bo = result['discount'].values[0]
            logger.debug(f"Fetching discount amount from bo_txn table : {discount_bo}")
            credit_type_bo = result['credit_type'].values[0]
            logger.debug(f"Fetching credit_type from bo_txn table : {credit_type_bo}")
            org_code_bo = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from bo_txn table : {org_code_bo}")
            txn_amount_bo = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from bo_txn table : {txn_amount_bo}")
            payment_mode_bo = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from bo_txn table : {payment_mode_bo}")
            bo_txn_type = result['bo_txn_type'].values[0]
            logger.debug(f"Fetching bo_txn_type from bo_txn table : {bo_txn_type}")

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
                date_and_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(final_amount),
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
                    "emi_status": "PENDING",
                    "emi_customer_name": "L3TEST",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "cashback": "{:,.2f}".format(emi_cashback_fixed),
                    "loan_amt": "{:,.2f}".format(final_amount),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "brand": brand_name,
                    "product": brand_sku_name,
                    "scheme": subvention_scheme_name
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
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
                logger.debug(f"Fetching total emi amount from txn history for the txn : {txn_id}, {app_total_emi_amount}")
                app_cashback = txn_history_page.fetch_cashback_text()
                logger.debug(f"Fetching cashback from txn history for the txn : {txn_id}, {app_cashback}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the txn : {txn_id}, {app_net_effective_price}")
                app_product = txn_history_page.fetch_product_text()
                logger.debug(f"Fetching product from txn history for the txn : {txn_id}, {app_product}")
                app_brand_name = txn_history_page.fetch_brand_text()
                logger.debug(f"Fetching brand name from txn history for the txn : {txn_id}, {app_brand_name}")
                app_imei_no = txn_history_page.fetch_imei_text()
                logger.debug(f"Fetching imei or serial no from txn history for the txn : {txn_id}, {app_imei_no}")
                app_scheme = txn_history_page.fetch_scheme_text()
                logger.debug(f"Fetching scheme from txn history for the txn : {txn_id}, {app_scheme}")

                txn_history_page.scroll_to_card_element()
                app_payment_status = txn_history_page.fetch_txn_status_text()
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
                    "emi_status": app_emi_status,
                    "emi_customer_name": app_customer_name,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "cashback": app_cashback.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1],
                    "brand": app_brand_name,
                    "product": app_product,
                    "scheme": app_scheme
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_date_and_time = date_time_converter.db_datetime(date_from_db=txn_created_time)
                expected_api_values = {
                    "txn_amt": float(final_amount),
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
                    "loan_amt": float(final_amount),
                    "monthly_emi": monthly_emi,
                    "interest_amt": total_interest,
                    "total_emi_amt": total_emi,
                    "net_cost": total_emi,
                    "emi_type": "BRAND_EMI",
                    "manufacturer": brand_name,
                    "product_name": brand_sku_name,
                    "sku_code": brand_sku_code,
                    "entity": "BRAND",
                    "subvention_type": "CASHBACK",
                    "subvention_amount": emi_cashback_fixed,
                    "subvention_fixed": emi_cashback_fixed,
                    "emi_interest_rate": interest_rate,
                    "total_amount_with_int": total_emi,
                    "product_serial": str(imei_no),
                    "scheme_name": subvention_scheme_name,
                    "user_agreement": f"I agree to pay as per the card issuer agreement. I understand that purchase(s) would be converted into EMI at the sole discretion of the Bank by charging an interest of {interest_rate}% on the monthly reducing balance.",
                    "orig_amt": float(amount),
                    "instant_discount": total_discount_value
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS obtained for txnlist api is : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                api_amount = response['amount']
                logger.debug(f"Value of amount obtained from txnlist api : {api_amount}")
                api_payment_mode = response['paymentMode']
                logger.debug(f"Value of payment mode obtained from txnlist api : {api_payment_mode}")
                api_payment_status = response['status']
                logger.debug(f"Value of status obtained from txnlist api : {api_payment_status}")
                api_payment_state = response['states'][0]
                logger.debug(f"Value of states obtained from txnlist api : {api_payment_state}")
                api_mid = response['mid']
                logger.debug(f"Value of mid obtained from txnlist api : {api_mid}")
                api_tid = response['tid']
                logger.debug(f"Value of tid obtained from txnlist api : {api_tid}")
                api_acquirer_code = response['acquirerCode']
                logger.debug(f"Value of acquirerCode obtained from txnlist api : {api_acquirer_code}")
                api_settle_status = response['settlementStatus']
                logger.debug(f"Value of settlementStatus obtained from txnlist api : {api_settle_status}")
                api_rrn = response['rrNumber']
                logger.debug(f"Value of rrn obtained from txnlist api : {api_rrn}")
                api_issuer_code = response['issuerCode']
                logger.debug(f"Value of issuerCode obtained from txnlist api : {api_issuer_code}")
                api_txn_type = response['txnType']
                logger.debug(f"Value of txnType obtained from txnlist api : {api_txn_type}")
                api_org_code = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {api_org_code}")
                api_batch_number = response['batchNumber']
                logger.debug(f"Value of batchNumber obtained from txnlist api : {api_batch_number}")
                api_pmt_card_brand = response['paymentCardBrand']
                logger.debug(f"Value of paymentCardBrand obtained from txnlist api : {api_pmt_card_brand}")
                api_pmt_card_type = response['paymentCardType']
                logger.debug(f"Value of paymentCardType obtained from txnlist api : {api_pmt_card_type}")
                api_date_time = response['createdTime']
                logger.debug(f"Value of createdTime obtained from txnlist api : {api_date_time}")
                api_device_serial = response['deviceSerial']
                logger.debug(f"Value of deviceSerial obtained from txnlist api : {api_device_serial}")
                api_card_txn_type_desc = response['cardTxnTypeDesc']
                logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api : {api_card_txn_type_desc}")
                api_merchant_name = response['merchantName']
                logger.debug(f"Value of merchantName obtained from txnlist api : {api_merchant_name}")
                api_card_last_four_digit = response['cardLastFourDigit']
                logger.debug(f"Value of cardLastFourDigit obtained from txnlist api : {api_card_last_four_digit}")
                api_ext_ref_number = response['externalRefNumber']
                logger.debug(f"Value of externalRefNumber obtained from txnlist api : {api_ext_ref_number}")
                api_pmt_card_bin = response['paymentCardBin']
                logger.debug(f"Value of paymentCardBin obtained from txnlist api : {api_pmt_card_bin}")
                api_display_pan = response['displayPAN']
                logger.debug(f"Value of displayPAN obtained from txnlist api : {api_display_pan}")
                api_customer_name = response['customerName']
                logger.debug(f"Value of customerName obtained from txnlist api : {api_customer_name}")
                api_payer_name = response['payerName']
                logger.debug(f"Value of payerName obtained from txnlist api : {api_payer_name}")
                api_name_on_card = response['nameOnCard']
                logger.debug(f"Value of nameOnCard obtained from txnlist api : {api_name_on_card}")
                api_auth_code = response['authCode']
                logger.debug(f"Value of authCode obtained from txnlist api : {api_auth_code}")
                api_card_type = response['cardType']
                logger.debug(f"Value of cardType obtained from txnlist api : {api_card_type}")
                api_emi_term = response['emiTerm']
                logger.debug(f"Value of emiTerm obtained from txnlist api : {api_emi_term}")
                api_emi_status = response['emiStatus']
                logger.debug(f"Value of emiStatus obtained from txnlist api : {api_emi_status}")
                api_interest_rate = response['emiInterestRate']
                logger.debug(f"Value of emiInterestRate obtained from txnlist api : {api_interest_rate}")
                api_emi_type = response['externalRefNumber7']
                logger.debug(f"Value of externalRefNumber7 obtained from txnlist api : {api_emi_type}")
                api_monthly_emi = response['emiDetails']['emi']
                logger.debug(f"Value of emi obtained from txnlist api : {api_monthly_emi}")
                api_interest_amt = response['emiDetails']['interestAmount']
                logger.debug(f"Value of interestAmount obtained from txnlist api : {api_interest_amt}")
                api_loan_amt = response['emiDetails']['loanAmount']
                logger.debug(f"Value of loanAmount obtained from txnlist api : {api_loan_amt}")
                api_total_emi_amt = response['emiDetails']['totalAmountWithInt']
                logger.debug(f"Value of totalAmountWithInt obtained from txnlist api : {api_total_emi_amt}")
                api_manufacturer = response['emiDetails']['manufacturer']
                logger.debug(f"Value of manufacturer obtained from txnlist api : {api_manufacturer}")
                api_sku_code = response['emiDetails']['skuCode']
                logger.debug(f"Value of skuCode obtained from txnlist api : {api_sku_code}")
                api_product_name = response['emiDetails']['productName']
                logger.debug(f"Value of productName obtained from txnlist api : {api_product_name}")
                api_entity = response['emiDetails']['subventionDetails'][0]['entity']
                logger.debug(f"Value of entity obtained from txnlist api : {api_entity}")
                api_subvention_type = response['emiDetails']['subventionDetails'][0]['subventionType']
                logger.debug(f"Value of subventionType obtained from txnlist api : {api_subvention_type}")
                api_subvention_amt = response['emiDetails']['subventionDetails'][0]['subventionAmount']
                logger.debug(f"Value of subventionAmount obtained from txnlist api : {api_subvention_amt}")
                api_subvention_fixed = response['emiDetails']['subventionDetails'][0]['subventionFixed']
                logger.debug(f"Value of subventionFixed obtained from txnlist api : {api_subvention_fixed}")
                api_scheme_name = response['emiDetails']['schemeName']
                logger.debug(f"Value of scheme name obtained from txnlist api : {api_scheme_name}")
                api_net_cost = response.get('emiDetails')['netCost']
                logger.debug(f"Value of netCost obtained from txnlist api : {api_net_cost}")
                api_total_amt_with_int = response['emiDetails']['totalAmountWithInt']
                logger.debug(f"Value of totalAmountWithInt obtained from txnlist api : {api_total_amt_with_int}")
                api_total_cashback = response['emiDetails']['totalCashBack']
                logger.debug(f"Value of totalCashBack obtained from txnlist api : {api_total_cashback}")
                api_useragreement = response['userAgreement']
                logger.debug(f"Value of 'userAgreement' obtained from txnlist api : {api_useragreement}")
                api_product_serial = response['emiDetails']['productSerial']
                logger.debug(f"Value of productSerial obtained from txnlist api : {api_product_serial}")
                api_original_amount = response.get('amountOriginal')
                logger.debug(f"From response fetch amountOriginal : {api_original_amount}")
                api_bo_instant_discount = response.get('emiDetails')['boInstantDiscount']
                logger.debug(f"From response fetch total boInstantDiscount : {api_bo_instant_discount}")

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
                    "emi_type": api_emi_type,
                    "manufacturer": api_manufacturer,
                    "product_name": api_product_name,
                    "sku_code": api_sku_code,
                    "entity": api_entity,
                    "subvention_type": api_subvention_type,
                    "subvention_amount": api_subvention_amt,
                    "subvention_fixed": api_subvention_fixed,
                    "emi_interest_rate": api_interest_rate,
                    "total_amount_with_int": api_total_amt_with_int,
                    "product_serial": api_product_serial,
                    "scheme_name": api_scheme_name,
                    "user_agreement": api_useragreement,
                    "orig_amt": api_original_amount,
                    "instant_discount": api_bo_instant_discount
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "txn_amt": float(final_amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": "L3TEST/CARD0010",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
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
                    "interest_rate": interest_rate,
                    "monthly_emi": monthly_emi,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(final_amount),
                    "emi_original_amt": float(amount),
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "BRAND_EMI",
                    "emi_cashback_fixed": api_subvention_fixed,
                    "emi_cashback_amount": api_subvention_fixed,
                    "emi_total_amount": api_total_emi_amt,
                    "emi_cashback_type": 'CASHBACK',
                    "emi_interest_rate": interest_rate,
                    "loan_amt": float(final_amount),
                    "brand_name": api_manufacturer,
                    "brand_sku": api_sku_code,
                    "brand_sku_code": api_sku_code,
                    "subvention_scheme_name": api_scheme_name,
                    "subvention_org_code": org_code,
                    "subvention_brand_id": str(brand_id),
                    "subvention_card_type": 'CREDIT',
                    "subvention_entity": "BRAND",
                    "subvention_type": "CASHBACK",
                    "subvention_value_type": "FIXED",
                    "subvention_value": api_subvention_fixed,
                    "subvention_tenure": f"{emi_plan_in_months} month",
                    "subvention_discount_type": None if subvention_discount_type is None else "Additional",
                    "discount_bo": total_discount_value,
                    "credit_type_bo": "INSTANT",
                    "org_code_bo": org_code,
                    "txn_amount_bo": final_amount,
                    "payment_mode_bo": "CARD",
                    "bo_txn_type": "BRAND_EMI",
                    "orig_amt": float(amount)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code_db,
                    "payer_name": payer_name_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "txn_type": txn_type_db,
                    "settle_status": settlement_status_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "device_serial": device_serial_db,
                    "order_id": order_id_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "customer_name": customer_name_db,
                    "interest_rate": emi_interest_rate,
                    "emi_status": emi_status,
                    "emi_term": emi_term,
                    "emi_type": emi_type_db,
                    "loan_amt": emi_loan_amount,
                    "monthly_emi": emi_amount_monthly,
                    "total_emi_amt": emi_total_amount,
                    "scheme_code": emi_scheme_code,
                    "emi_txn_amt": emi_txn_amount,
                    "emi_original_amt": emi_original_amount,
                    "emi_cashback_fixed": emi_cashback_fixed,
                    "emi_cashback_amount": emi_cashback_amount,
                    "emi_total_amount": emi_total_amount,
                    "emi_cashback_type": emi_cashback_type,
                    "emi_interest_rate": emi_interest_rate,
                    "brand_name": brand_name,
                    "brand_sku": brand_sku_code,
                    "brand_sku_code": brand_sku_code,
                    "subvention_scheme_name": subvention_scheme_name,
                    "subvention_org_code": subvention_plan_org_code,
                    "subvention_brand_id": subvention_plan_brand_id,
                    "subvention_card_type": subvention_plan_card_type,
                    "subvention_entity": subvention_entity,
                    "subvention_type": subvention_type,
                    "subvention_value_type": subvention_value_type,
                    "subvention_value": subvention_value,
                    "subvention_tenure": subvention_tenure,
                    "subvention_discount_type": subvention_discount_type,
                    "discount_bo": discount_bo,
                    "credit_type_bo": credit_type_bo,
                    "org_code_bo": org_code_bo,
                    "txn_amount_bo": txn_amount_bo,
                    "payment_mode_bo": payment_mode_bo,
                    "bo_txn_type": bo_txn_type,
                    "orig_amt": amount_original
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

        # -----------------------------------------Start of Portal Validation-------------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(final_amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "date": txn_date,
                    "time": txn_time,
                    "BATCH NO": batch_number,
                    "INVOICE NO": invoice_number,
                    "APP": "Visa Credit",
                    "payment_option": "EMI SALE",
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "CARD TYPE": "VISA",
                    "AUTH CODE": str(auth_code).strip(),
                    "TID": tid,
                    "RRN": rrn,
                    "EMI Txn Id": txn_id,
                    "Tenure": f"{emi_plan_in_months} month",
                    "Card Issuer": "HDFC Bank",
                    "Cashback": "Rs " + "{:.2f}".format(emi_cashback_fixed),
                    "Total Cashback Amt": "Rs. " + "{:.2f}".format(emi_cashback_amount),
                    "EMI Amt": "Rs." + "{:.2f}".format(monthly_emi),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(final_amount),
                    "Manufacturer Name": brand_name,
                    "Product Name": brand_sku_name,
                    "Product Desc": brand_sku_code,
                    "Sr. No.": str(imei_no),
                    "unnamed_section_text": f"{customer_name_db} I agree to pay as per the card issuer agreement."
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id, {
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_07_090():
    """
    Sub Feature Code: UI_Common_Card_Brand_EMI_BO_Cashback_Discount_Cashback_by_Brand_Fixed_Success_Txn_For_An_Org_HDFC_Dummy_HDFC_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
    Sub Feature Description: Performing the brand EMI BO Cashback Discount cashback by brand fixed success transaction for an org (not ezetap)
    via HDFC Dummy PG for HDFC issuer using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 07: Brand_EMI, 090: TC090
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
        api_details["RequestBody"]["settings"]["boCashbackEnabled"] = "true"
        api_details["RequestBody"]["settings"]["businessDiscountEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received when emi, emi for client, offering_emi cashback, brand_emi, businessDiscountEnabled and bocashback is enabled in preconditions settings : {response}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        emi_plan_in_months = 3
        logger.debug(f"Value of emi plan in months is : {emi_plan_in_months}")

        testsuite_teardown.update_emi_status_for_org(org_code, 'CREDIT', 'ACTIVE')
        logger.debug(f"Active emi setting for credit card")

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

        query = f"select * from subvention_plan where brand_id='{brand_id}' and org_code='{org_code}' and card_type= 'CREDIT' and bank='HDFC' and eze_emi_enabled=b'0' order by created_time desc limit 1;"
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

        query = f"select * from subvention_plan_details where subvention_plan_id='{subvention_plan_id}' and subventing_entity ='BRAND' and subvention_value_type= 'FIXED' and subvention_type='CASHBACK' and tenure='{emi_plan_in_months} month' ;"
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

        testsuite_teardown.update_rule_status(org_code=org_code, credit_type='CASHBACK', status='ACTIVE')
        logger.debug(f"updated rule status activated CASHBACK BO")

        testsuite_teardown.update_rule_status(org_code=org_code, credit_type='INSTANT', status='INACTIVE')
        logger.debug(f"updated rule status inactivated INSTANT BO")

        query = f"select * from rule where org_code='{org_code}' and credit_type='CASHBACK' and name LIKE '{brand_name}%'"
        logger.debug(f"Query to fetch data from the rule table : {query}")
        result = DBProcessor.getValueFromDB(query=query, db_name='rule_engine')
        logger.debug(f"Fetching result from rule table :{result}")
        rule_id = result['id'].values[0]
        logger.debug(f"Fetching id from the rule table : {rule_id}")

        query = f"select * from subvention_split where rule_id='{rule_id}' and sku_codes='{brand_sku_code}'"
        logger.debug(f"Query to fetch data from the subvention_split table : {query}")
        result = DBProcessor.getValueFromDB(query=query, db_name='rule_engine')
        logger.debug(f"Fetching result from subvention_split table :{result}")
        discount_value_bank = result['subvention_value'].values[0]
        logger.debug(f"Fetching subvention_value by bank from the subvention_split table : {discount_value_bank}")
        discount_value_brand = result['subvention_value'].values[1]
        logger.debug(f"Fetching subvention_value by brand from the subvention_split table : {discount_value_brand}")
        total_discount_value = discount_value_bank + discount_value_brand
        logger.debug(f"total discount value : {total_discount_value}")

        # updating the status as inactive in subvention_plan_details table
        testsuite_teardown.update_subvention_plan_details(subvention_plan_id)

        query = f"update subvention_plan_details set status = 1 where subvention_plan_id ='{subvention_plan_id}' and subventing_entity='BRAND' and subvention_type='CASHBACK' and subvention_value_type='FIXED' and tenure='{emi_plan_in_months} month'"
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
            login_page.perform_login(username=app_username, password=app_password)
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
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"Selected the emi plan in months : {emi_plan_in_months}")
            payment_page.click_on_proceed_homepage()

            logger.debug(f"Started calculating emi part")
            monthly_interest_rate = interest_rate / (12 * 100)
            logger.debug(f"monthly_interest_rate is : {monthly_interest_rate}")
            cal_monthly_emi_amt = amount * monthly_interest_rate * (
                    (1 + monthly_interest_rate) ** emi_plan_in_months) / (
                                          (1 + monthly_interest_rate) ** emi_plan_in_months - 1)
            logger.debug(f"cal_monthly_emi_amt is : {cal_monthly_emi_amt}")
            monthly_emi = round(cal_monthly_emi_amt, 2)
            logger.debug(f"Calculated monthly_emi amount : {monthly_emi}")
            total_emi = round((monthly_emi * emi_plan_in_months), 2)
            logger.debug(f"total_emi amount is : {total_emi}")
            net_amt = total_emi - total_discount_value - subvention_value
            logger.debug(f"net_amt after deducting cashback amt {net_amt}")
            total_interest = round((total_emi - amount), 2)
            logger.debug(f"total_interest amount is : {total_interest}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table : {txn_created_time}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table : {batch_number}")
            amount_db = result['amount'].values[0]
            logger.debug(f"Fetching amount value from the txn table : {amount_db}")
            amt_cash_back_db = result['amount_cash_back'].values[0]
            logger.debug(f"Fetching amount_cash_back value from the txn table : {amt_cash_back_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode value from the txn table : {payment_mode_db}")
            payment_status_db = result['status'].values[0]
            logger.debug(f"Fetching status value from the txn table : {payment_status_db}")
            payment_state_db = result['state'].values[0]
            logger.debug(f"Fetching state value from the txn table : {payment_state_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from the txn table : {acquirer_code_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid value from the txn table : {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid value from the txn table : {tid_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from the txn table : {payment_gateway_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status value from the txn table : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the txn table : {device_serial_db}")
            sale_amt_db = result['amount_original'].values[0]
            logger.debug(f"Fetching amount_original value from the txn table : {sale_amt_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table : {payment_card_type_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer_code value from the txn table : {issuer_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer_name value from the txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer_name value from the txn table : {payer_name_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table : {org_code_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table : {order_id_db}")
            emi_type_db = result['external_ref7'].values[0]
            logger.debug(f"Fetching external_ref7 from the txn table : {emi_type_db}")
            invoice_number = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg_invoice_number from the txn table : {invoice_number}")
            amount_original = result['amount_original'].values[0]
            logger.debug(f"Fetching amount_original from the txn table : {amount_original}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")

            query = f"select * from txn_emi where id='{txn_id}';"
            logger.debug(f"Query to fetch data from the txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn_emi table : {result}")
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
            emi_cashback_fixed = result['emi_cashback_fixed'].values[0]
            logger.debug(f"Fetching emi cashback fixed amount from txn_emi table : {emi_cashback_fixed}")
            emi_cashback_amount = result['emi_cashback_amount'].values[0]
            logger.debug(f"Fetching emi cashback amount from txn_emi table : {emi_cashback_amount}")
            emi_cashback_type = result['emi_cashback_type'].values[0]
            logger.debug(f"Fetching emi cashback type from txn_emi table : {emi_cashback_type}")
            bo_additional_cashback_amount = result['bo_additional_cashback_amount'].values[0]
            logger.debug(f"Fetching bo_additional_cashback_amount from txn_emi table : {bo_additional_cashback_amount}")

            query = f"select * from bo_txn where txn_id='{txn_id}'"
            logger.debug(f"Query to fetch data from bo_txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query, db_name='rule_engine')
            logger.debug(f"Fetching result for bo_txn table : {result} ")
            discount_bo = result['discount'].values[0]
            logger.debug(f"Fetching discount amount from bo_txn table : {discount_bo}")
            credit_type_bo = result['credit_type'].values[0]
            logger.debug(f"Fetching credit_type from bo_txn table : {credit_type_bo}")
            org_code_bo = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from bo_txn table : {org_code_bo}")
            txn_amount_bo = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from bo_txn table : {txn_amount_bo}")
            payment_mode_bo = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from bo_txn table : {payment_mode_bo}")
            bo_txn_type = result['bo_txn_type'].values[0]
            logger.debug(f"Fetching bo_txn_type from bo_txn table : {bo_txn_type}")

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
                    "emi_status": "PENDING",
                    "emi_customer_name": "L3TEST",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "cashback": "{:,.2f}".format(emi_cashback_fixed),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(net_amt),
                    "brand": brand_name,
                    "product": brand_sku_name,
                    "imei_no": str(imei_no),
                    "scheme": subvention_scheme_name,
                    "additional_cashback": "{:,.2f}".format(total_discount_value)
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
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
                app_emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the txn : {txn_id}, {app_emi_status}")
                app_tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the txn : {txn_id}, {app_tenure}")
                app_lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the txn : {txn_id}, {app_lender}")
                additional_cashback = txn_history_page.fetch_additional_cashback()
                logger.debug(f"Fetching additional_cashback from txn history for the txn : {txn_id}, {additional_cashback}")
                app_monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the txn : {txn_id}, {app_monthly_emi}")
                app_total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the txn : {txn_id}, {app_total_interest}")
                app_total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the txn : {txn_id}, {app_total_emi_amount}")
                app_cashback = txn_history_page.fetch_cashback_text()
                logger.debug(f"Fetching cashback from txn history for the txn : {txn_id}, {app_cashback}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the txn : {txn_id}, {app_net_effective_price}")
                app_product = txn_history_page.fetch_product_text()
                logger.debug(f"Fetching product from txn history for the txn : {txn_id}, {app_product}")
                app_brand_name = txn_history_page.fetch_brand_text()
                logger.debug(f"Fetching brand name from txn history for the txn : {txn_id}, {app_brand_name}")
                app_imei_no = txn_history_page.fetch_imei_text()
                logger.debug(f"Fetching imei or serial no from txn history for the txn : {txn_id}, {app_imei_no}")
                app_scheme = txn_history_page.fetch_scheme_text()
                logger.debug(f"Fetching scheme from txn history for the txn : {txn_id}, {app_scheme}")

                txn_history_page.scroll_to_card_element()
                app_payment_status = txn_history_page.fetch_txn_status_text()
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
                    "emi_status": app_emi_status,
                    "emi_customer_name": app_customer_name,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "cashback": app_cashback.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1],
                    "brand": app_brand_name,
                    "product": app_product,
                    "imei_no": app_imei_no,
                    "scheme": app_scheme,
                    "additional_cashback": additional_cashback.split(' ')[1]
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_date_and_time = date_time_converter.db_datetime(date_from_db=txn_created_time)
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
                    "net_cost": net_amt,
                    "emi_type": "BRAND_EMI",
                    "manufacturer": brand_name,
                    "product_name": brand_sku_name,
                    "sku_code": brand_sku_code,
                    "entity": "BRAND",
                    "subvention_type": "CASHBACK",
                    "subvention_amount": emi_cashback_fixed,
                    "subvention_fixed": emi_cashback_fixed,
                    "emi_interest_rate": interest_rate,
                    "total_amount_with_int": total_emi,
                    "product_serial": str(imei_no),
                    "scheme_name": subvention_scheme_name,
                    "user_agreement": f"I agree to pay as per the card issuer agreement. I understand that purchase(s) would be converted into EMI at the sole discretion of the Bank by charging an interest of {interest_rate}% on the monthly reducing balance.",
                    "orig_amt": float(amount),
                    "bo_additional_cashback": total_discount_value
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS obtained for txnlist api is : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                api_amount = response['amount']
                logger.debug(f"Value of amount obtained from txnlist api : {api_amount}")
                api_payment_mode = response['paymentMode']
                logger.debug(f"Value of payment mode obtained from txnlist api : {api_payment_mode}")
                api_payment_status = response['status']
                logger.debug(f"Value of status obtained from txnlist api : {api_payment_status}")
                api_payment_state = response['states'][0]
                logger.debug(f"Value of states obtained from txnlist api : {api_payment_state}")
                api_mid = response['mid']
                logger.debug(f"Value of mid obtained from txnlist api : {api_mid}")
                api_tid = response['tid']
                logger.debug(f"Value of tid obtained from txnlist api : {api_tid}")
                api_acquirer_code = response['acquirerCode']
                logger.debug(f"Value of acquirerCode obtained from txnlist api : {api_acquirer_code}")
                api_settle_status = response['settlementStatus']
                logger.debug(f"Value of settlementStatus obtained from txnlist api : {api_settle_status}")
                api_rrn = response['rrNumber']
                logger.debug(f"Value of rrn obtained from txnlist api : {api_rrn}")
                api_issuer_code = response['issuerCode']
                logger.debug(f"Value of issuerCode obtained from txnlist api : {api_issuer_code}")
                api_txn_type = response['txnType']
                logger.debug(f"Value of txnType obtained from txnlist api : {api_txn_type}")
                api_org_code = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {api_org_code}")
                api_batch_number = response['batchNumber']
                logger.debug(f"Value of batchNumber obtained from txnlist api : {api_batch_number}")
                api_pmt_card_brand = response['paymentCardBrand']
                logger.debug(f"Value of paymentCardBrand obtained from txnlist api : {api_pmt_card_brand}")
                api_pmt_card_type = response['paymentCardType']
                logger.debug(f"Value of paymentCardType obtained from txnlist api : {api_pmt_card_type}")
                api_date_time = response['createdTime']
                logger.debug(f"Value of createdTime obtained from txnlist api : {api_date_time}")
                api_device_serial = response['deviceSerial']
                logger.debug(f"Value of deviceSerial obtained from txnlist api : {api_device_serial}")
                api_card_txn_type_desc = response['cardTxnTypeDesc']
                logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api : {api_card_txn_type_desc}")
                api_merchant_name = response['merchantName']
                logger.debug(f"Value of merchantName obtained from txnlist api : {api_merchant_name}")
                api_card_last_four_digit = response['cardLastFourDigit']
                logger.debug(f"Value of cardLastFourDigit obtained from txnlist api : {api_card_last_four_digit}")
                api_ext_ref_number = response['externalRefNumber']
                logger.debug(f"Value of externalRefNumber obtained from txnlist api : {api_ext_ref_number}")
                api_pmt_card_bin = response['paymentCardBin']
                logger.debug(f"Value of paymentCardBin obtained from txnlist api : {api_pmt_card_bin}")
                api_display_pan = response['displayPAN']
                logger.debug(f"Value of displayPAN obtained from txnlist api : {api_display_pan}")
                api_customer_name = response['customerName']
                logger.debug(f"Value of customerName obtained from txnlist api : {api_customer_name}")
                api_payer_name = response['payerName']
                logger.debug(f"Value of payerName obtained from txnlist api : {api_payer_name}")
                api_name_on_card = response['nameOnCard']
                logger.debug(f"Value of nameOnCard obtained from txnlist api : {api_name_on_card}")
                api_auth_code = response['authCode']
                logger.debug(f"Value of authCode obtained from txnlist api : {api_auth_code}")
                api_card_type = response['cardType']
                logger.debug(f"Value of cardType obtained from txnlist api : {api_card_type}")
                api_emi_term = response['emiTerm']
                logger.debug(f"Value of emiTerm obtained from txnlist api : {api_emi_term}")
                api_emi_status = response['emiStatus']
                logger.debug(f"Value of emiStatus obtained from txnlist api : {api_emi_status}")
                api_interest_rate = response['emiInterestRate']
                logger.debug(f"Value of emiInterestRate obtained from txnlist api : {api_interest_rate}")
                api_emi_type = response['externalRefNumber7']
                logger.debug(f"Value of externalRefNumber7 obtained from txnlist api : {api_emi_type}")
                api_monthly_emi = response['emiDetails']['emi']
                logger.debug(f"Value of emi obtained from txnlist api : {api_monthly_emi}")
                api_interest_amt = response['emiDetails']['interestAmount']
                logger.debug(f"Value of interestAmount obtained from txnlist api : {api_interest_amt}")
                api_loan_amt = response['emiDetails']['loanAmount']
                logger.debug(f"Value of loanAmount obtained from txnlist api : {api_loan_amt}")
                api_total_emi_amt = response['emiDetails']['totalAmountWithInt']
                logger.debug(f"Value of totalAmountWithInt obtained from txnlist api : {api_total_emi_amt}")
                api_manufacturer = response['emiDetails']['manufacturer']
                logger.debug(f"Value of manufacturer obtained from txnlist api : {api_manufacturer}")
                api_sku_code = response['emiDetails']['skuCode']
                logger.debug(f"Value of skuCode obtained from txnlist api : {api_sku_code}")
                api_product_name = response['emiDetails']['productName']
                logger.debug(f"Value of productName obtained from txnlist api : {api_product_name}")
                api_entity = response['emiDetails']['subventionDetails'][0]['entity']
                logger.debug(f"Value of entity obtained from txnlist api : {api_entity}")
                api_subvention_type = response['emiDetails']['subventionDetails'][0]['subventionType']
                logger.debug(f"Value of subventionType obtained from txnlist api : {api_subvention_type}")
                api_subvention_amt = response['emiDetails']['subventionDetails'][0]['subventionAmount']
                logger.debug(f"Value of subventionAmount obtained from txnlist api : {api_subvention_amt}")
                api_subvention_fixed = response['emiDetails']['subventionDetails'][0]['subventionFixed']
                logger.debug(f"Value of subventionFixed obtained from txnlist api : {api_subvention_fixed}")
                api_scheme_name = response['emiDetails']['schemeName']
                logger.debug(f"Value of scheme name obtained from txnlist api : {api_scheme_name}")
                api_net_cost = response.get('emiDetails')['netCost']
                logger.debug(f"Value of netCost obtained from txnlist api : {api_net_cost}")
                api_total_amt_with_int = response['emiDetails']['totalAmountWithInt']
                logger.debug(f"Value of totalAmountWithInt obtained from txnlist api : {api_total_amt_with_int}")
                api_total_cashback = response['emiDetails']['totalCashBack']
                logger.debug(f"Value of totalCashBack obtained from txnlist api : {api_total_cashback}")
                api_useragreement = response['userAgreement']
                logger.debug(f"Value of 'userAgreement' obtained from txnlist api : {api_useragreement}")
                api_product_serial = response['emiDetails']['productSerial']
                logger.debug(f"Value of productSerial obtained from txnlist api : {api_product_serial}")
                api_original_amount = response.get('amountOriginal')
                logger.debug(f"From response fetch amountOriginal : {api_original_amount}")
                api_bo_additional_cashback = response.get('emiDetails')['boAdditionalCashback']
                logger.debug(f"From response fetch boAdditionalCashback : {api_bo_additional_cashback}")

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
                    "emi_type": api_emi_type,
                    "manufacturer": api_manufacturer,
                    "product_name": api_product_name,
                    "sku_code": api_sku_code,
                    "entity": api_entity,
                    "subvention_type": api_subvention_type,
                    "subvention_amount": api_subvention_amt,
                    "subvention_fixed": api_subvention_fixed,
                    "emi_interest_rate": api_interest_rate,
                    "total_amount_with_int": api_total_amt_with_int,
                    "product_serial": api_product_serial,
                    "scheme_name": api_scheme_name,
                    "user_agreement": api_useragreement,
                    "orig_amt": api_original_amount,
                    "bo_additional_cashback": api_bo_additional_cashback
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
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
                    "pmt_gateway": "DUMMY",
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
                    "interest_rate": interest_rate,
                    "monthly_emi": monthly_emi,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "BRAND_EMI",
                    "emi_cashback_fixed": api_subvention_fixed,
                    "emi_cashback_amount": api_subvention_fixed,
                    "emi_total_amount": api_total_emi_amt,
                    "emi_cashback_type": 'CASHBACK',
                    "emi_interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "brand_name": api_manufacturer,
                    "brand_sku": api_sku_code,
                    "brand_sku_code": api_sku_code,
                    "subvention_scheme_name": api_scheme_name,
                    "subvention_org_code": org_code,
                    "subvention_brand_id": str(brand_id),
                    "subvention_card_type": 'CREDIT',
                    "subvention_entity": "BRAND",
                    "subvention_type": "CASHBACK",
                    "subvention_value_type": "FIXED",
                    "subvention_value": api_subvention_fixed,
                    "subvention_tenure": f"{emi_plan_in_months} month",
                    "subvention_discount_type": None if subvention_discount_type is None else "Additional",
                    "discount_bo": total_discount_value,
                    "credit_type_bo": "CASHBACK",
                    "org_code_bo": org_code,
                    "txn_amount_bo": amount,
                    "payment_mode_bo": "CARD",
                    "bo_txn_type": "BRAND_EMI",
                    "orig_amt": float(amount),
                    "bo_additional_cashback_amt": total_discount_value
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code_db,
                    "payer_name": payer_name_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "txn_type": txn_type_db,
                    "settle_status": settlement_status_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "device_serial": device_serial_db,
                    "order_id": order_id_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "customer_name": customer_name_db,
                    "interest_rate": emi_interest_rate,
                    "emi_status": emi_status,
                    "emi_term": emi_term,
                    "emi_type": emi_type_db,
                    "loan_amt": emi_loan_amount,
                    "monthly_emi": emi_amount_monthly,
                    "total_emi_amt": emi_total_amount,
                    "scheme_code": emi_scheme_code,
                    "emi_txn_amt": emi_txn_amount,
                    "emi_original_amt": emi_original_amount,
                    "emi_cashback_fixed": emi_cashback_fixed,
                    "emi_cashback_amount": emi_cashback_amount,
                    "emi_total_amount": emi_total_amount,
                    "emi_cashback_type": emi_cashback_type,
                    "emi_interest_rate": emi_interest_rate,
                    "brand_name": brand_name,
                    "brand_sku": brand_sku_code,
                    "brand_sku_code": brand_sku_code,
                    "subvention_scheme_name": subvention_scheme_name,
                    "subvention_org_code": subvention_plan_org_code,
                    "subvention_brand_id": subvention_plan_brand_id,
                    "subvention_card_type": subvention_plan_card_type,
                    "subvention_entity": subvention_entity,
                    "subvention_type": subvention_type,
                    "subvention_value_type": subvention_value_type,
                    "subvention_value": subvention_value,
                    "subvention_tenure": subvention_tenure,
                    "subvention_discount_type": subvention_discount_type,
                    "discount_bo": discount_bo,
                    "credit_type_bo": credit_type_bo,
                    "org_code_bo": org_code_bo,
                    "txn_amount_bo": txn_amount_bo,
                    "payment_mode_bo": payment_mode_bo,
                    "bo_txn_type": bo_txn_type,
                    "orig_amt": amount_original,
                    "bo_additional_cashback_amt": bo_additional_cashback_amount
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

        # -----------------------------------------Start of Portal Validation-------------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "date": txn_date,
                    "time": txn_time,
                    "BATCH NO": batch_number,
                    "INVOICE NO": invoice_number,
                    "APP": "Visa Credit",
                    "payment_option": "EMI SALE",
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "CARD TYPE": "VISA",
                    "AUTH CODE": str(auth_code).strip(),
                    "TID": tid,
                    "RRN": rrn,
                    "EMI Txn Id": txn_id,
                    "Tenure": f"{emi_plan_in_months} month",
                    "Card Issuer": f"{issuer_code} Bank",
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "Manufacturer Name": brand_name,
                    "Product Name": brand_sku_name,
                    "Product Desc": brand_sku_code,
                    "Sr. No.": str(imei_no),
                    "unnamed_section_text": f"{customer_name_db} I agree to pay as per the card issuer agreement.",
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id, {
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)