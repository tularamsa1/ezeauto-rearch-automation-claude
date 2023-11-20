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
def test_common_100_115_05_086():
    """
    Sub Feature Code: UI_Common_Card_Normal_EMI_Check_Eligibility_For_An_Org_HDFC_Dummy_ICICI_EMV_VISA_DebitCard_With_Pin_428090_For_3_Months_Tenure
    Sub Feature Description: Performing the normal EMI check eligibility transaction for an org (not ezetap) via HDFC Dummy PG
    for ICICI issuer using EMV VISA Debit card with pin for 3 months tenure (bin: 428090)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 05: NORMAL_EMI, 086: TC086
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].values[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result['id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Below function to update bank_code, bank for the bin: 428090
        testsuite_teardown.update_bin_info(bin_number='428090', bank_code='ICICI', bank='ICICI')

        query = f"select bank_code from bin_info where bin='428090'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for normal emi setup to be enabled:  {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='DEBIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for debit card")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(3001, 4000)
            emi_plan_in_months = 3
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
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
            payment_page.click_on_bank_emi_pmt_mode()
            logger.info(f"Selected payment mode is Bank EMI")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_DEBIT_428090")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")

            query = f"select * from debit_emi_txn_request where org_code='{org_code}' order by id desc limit 1;"
            logger.debug(f"Query to fetch data from debit_emi_txn_request table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for debit_emi_txn_request table : {result} ")
            eligibility_status = result['eligibility_status'].values[0]
            logger.debug(f"Fetching eligibility_status from debit_emi_txn_request table : {eligibility_status}")
            txn_amount_posting_status = result['txn_amount_posting_status'].values[0]
            logger.debug(f"Fetching txn_amount_posting_status from debit_emi_txn_request : {txn_amount_posting_status}")
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

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "txn_amt_posting_status": "PENDING",
                    "eligibility_status": "SUCCESS"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt_posting_status": txn_amount_posting_status,
                    "eligibility_status": eligibility_status
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_05_087():
    """
    Sub Feature Code: UI_Common_Card_Normal_EMI_Txn_EMI_Not_Enabled_Bin_Info_Level_For_An_Org_HDFC_Dummy_ICICI_EMV_VISA_DebitCard_With_Pin_428090
    Sub Feature Description: Performing the normal EMI transaction when EMI is not enabled at the bin_info level
    for an org (not ezetap) via HDFC Dummy PG for ICICI issuer using EMV VISA Debit card with pin (bin: 428090)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 05: NORMAL_EMI, 087: TC087
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].values[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result['id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Below function to update bank_code, bank for the bin: 428090
        testsuite_teardown.update_bin_info(bin_number='428090', bank_code='ICICI', bank='ICICI')

        query = f"select bank_code from bin_info where bin='428090'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        query = f"update bin_info set emi_enabled=b'0' where bin='428090';"
        logger.debug(f"Query to update bin_info table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")
        refresh_db()
        logger.debug(f"Database refreshed")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for normal emi setup to be enabled:  {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='DEBIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for debit card")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(3001, 4000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
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
            payment_page.click_on_bank_emi_pmt_mode()
            logger.info(f"Selected payment mode is Bank EMI")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_DEBIT_428090")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            error_msg = payment_page.fetch_error_msg_normal_emi()
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
        # -----------------------------------------End of App Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        query = f"update bin_info set emi_enabled=b'1' where bin='428090';"
        logger.debug(f"Query to update bin_info table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")
        refresh_db()
        logger.debug(f"Database refreshed")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_115_05_088():
    """
    Sub Feature Code: UI_Common_Card_Normal_EMI_Txn_EMI_Not_Enabled_In_Org_Settings_For_An_Org_HDFC_Dummy_ICICI_EMV_VISA_DebitCard_With_Pin_428090
    Sub Feature Description: Performing the normal EMI transaction when EMI is not enabled in the org settings
    for an org (not ezetap) via HDFC Dummy PG for ICICI issuer using EMV VISA Debit card with pin (bin: 428090)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 05: NORMAL_EMI, 088: TC088
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].values[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result['id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Below function to update bank_code, bank for the bin: 428090
        testsuite_teardown.update_bin_info(bin_number='428090', bank_code='ICICI', bank='ICICI')

        query = f"select bank_code from bin_info where bin='428090'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "false"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for normal emi setup to be enabled:  {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='DEBIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for debit card")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(3001, 4000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
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
            error_msg = payment_page.check_bank_emi_pmt_mode_present()
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
                    "err_msg": "bank emi payment mode is not present"
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
        # -----------------------------------------End of App Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)