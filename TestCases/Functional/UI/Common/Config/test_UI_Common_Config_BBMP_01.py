import random
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_300_307_001():
    """
    Sub Feature Code: UI_Common_Config_BBMP_Verify_Config_Screen_With_All_Type_Of_Violation_Displayed
    Sub Feature Description: Verify config screen with all the type of violation displayed as per configured in UI JSON
    TC naming code description: 100: Payment Method, 300: Config, 307: BBMP, 001: TC001
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
        logger.debug(f"Fetching org_code value from the org_employee table {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_on_start_btn()
            logger.info(f"Clicked on start button")
            logger.info(f"Fetching all the BBMP type of violation text in UI screen")
            list_of_bbmp_violations = home_page.fetch_all_bbmp_violation()
            logger.info(f"Fetched all the BBMP type of violation text in UI screen, {list_of_bbmp_violations}")

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
                expected_app_values = {
                    "violation_type_1": "SWM Violation",
                    "violation_type_2": "Plastic Ban Enforcement",
                    "violation_type_3": "Non Compliance at Public Gathering",
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "violation_type_1": list_of_bbmp_violations[0],
                    "violation_type_2": list_of_bbmp_violations[1],
                    "violation_type_3": list_of_bbmp_violations[2],
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

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
def test_common_100_300_307_002():
    """
    Sub Feature Code: UI_Common_Config_BBMP_Verify_SVM_Violation_All_Type_Of_Spot_Fines_Displayed
    Sub Feature Description: Verify SVM violation all types of spot fines displayed as per configured in UI JSON
    TC naming code description: 100: Payment Method, 300: Config, 307: BBMP, 001: TC002
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
        logger.debug(f"Fetching org_code value from the org_employee table {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_on_start_btn()
            logger.info(f"Clicked on start button")
            home_page.click_on_svm_violation()
            logger.debug("Clicked on SWM Violation button")
            logger.info(f"Fetching all the sub lobs text of swa violation in UI screen")
            list_of_swa_violation_spot_fines = home_page.fetch_all_fine_names_of_swm_violation()
            logger.info(
                f"Fetched all the sub lobs text of swa violation in UI screen, {list_of_swa_violation_spot_fines}")

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
                expected_app_values = {
                    "spot_fine_type_1": "Public Nuisance",
                    "spot_fine_type_2": "Non Segregation of Waste",
                    "spot_fine_type_3": "Unauthorized Handing Over of Waste",
                    "spot_fine_type_4": "Mixing of segregated waste by BBMP staff",
                    "spot_fine_type_5": "Street Vendor",
                    "spot_fine_type_6": "Burning of Waste/Unauthroized Burial",
                    "spot_fine_type_7": "Construction/Demolition Waste",
                    "spot_fine_type_8": "Other Offences"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "spot_fine_type_1": list_of_swa_violation_spot_fines[0],
                    "spot_fine_type_2": list_of_swa_violation_spot_fines[1],
                    "spot_fine_type_3": list_of_swa_violation_spot_fines[2],
                    "spot_fine_type_4": list_of_swa_violation_spot_fines[3],
                    "spot_fine_type_5": list_of_swa_violation_spot_fines[4],
                    "spot_fine_type_6": list_of_swa_violation_spot_fines[5],
                    "spot_fine_type_7": list_of_swa_violation_spot_fines[6],
                    "spot_fine_type_8": list_of_swa_violation_spot_fines[7]
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

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
def test_common_100_300_307_003():
    """
    Sub Feature Code: UI_Common_Config_BBMP_Verify_SVM_Violation_Type_Of_Spot_Fine_Public_Nuisance (Select Fine Type : Not wearing mask)
    Sub Feature Description: Verify SVM violation and type of spot fine is public nuisance (Select Fine Type : Not wearing mask)
    TC naming code description: 100: Payment Method, 300: Config, 307: BBMP, 003: TC003
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
        logger.debug(f"Fetching org_code value from the org_employee table {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_on_start_btn()
            logger.info(f"Clicked on start button")
            home_page.click_on_svm_violation()
            logger.debug("Clicked on SWM Violation button")
            home_page.click_on_public_nuisance()
            logger.debug("Clicked on Public Nuisance button")
            home_page.click_on_not_wearing_mask()
            logger.info(f"Clicked on not wearing mask button")
            try:
                logger.info(f"Validating the Enter details and pay screen")
                home_page.validate_enter_details_and_pay_screen_title()
                logger.info(f"Enter Details & Pay Screen title is visible")
                home_page.validate_fine_tittle_for_not_wearing_mask()
                logger.info(f"Fine title is visible")

                msg = "Enter_details_&_pay_screen and fine for title are visible in amount screen"

            except Exception as e:
                logger.error(f"Enter_details_&_pay_screen is not visible due to error : {e}")
                msg = "Enter_details_&_pay_screen and fine for title are not visible in amount screen"

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
                expected_app_values = {
                    "msg": "Enter_details_&_pay_screen and fine for title are visible in amount screen"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "msg": msg
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_300_307_004():
    """
    Sub Feature Code: UI_Common_Config_BBMP_Verify_Success_Cash_SVM_Violation_Type_Of_Spot_Fine_Non_Segregation_Of_Waste (Select Type of Establishment : Domestic)
    Sub Feature Description:Verify success cash txn for type of spot fine is non segregation of waste (Select Type of Establishment : Domestic)
    TC naming code description: 100: Payment Method, 300: Config, 307: BBMP, 004: TC004
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
        logger.debug(f"Fetching org_code value from the org_employee table {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_on_start_btn()
            logger.info(f"Clicked on start button")
            home_page.click_on_svm_violation()
            logger.debug("Clicked on SWM Violation button")
            home_page.click_on_non_segregation_of_waste()
            logger.debug("Clicked on Non segregation of waste button")
            name = 'test_' + str(random.randint(1, 100))
            ph_number = random.randint(6000000000, 9000000000)
            ward_no = random.randint(100, 500)
            home_page.enter_details_for_domestic(name, ph_number, ward_no, "test_locality")
            fine_amount = home_page.fetch_amount_from_enter_details_and_pay_screen()
            logger.debug(f"Fetched fine amount from the enter details and pay screen : {fine_amount}")
            payment_pg = PaymentPage(app_driver)
            payment_pg.click_on_cash_payment_mode_and_confirm_btn()
            logger.debug('clicked on the cash mode and confirm on the LOB page')
            payment_pg.click_on_proceed_homepage()

            query = (f"select * from txn where org_code ='{org_code}' and customer_mobile ='{ph_number}' "
                     f"order by created_time Desc limit 1;")
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            customer_mobile = result['customer_mobile'].iloc[0]
            logger.debug(f"Fetching customer_mobile from txn table : {customer_mobile}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            status_db = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            external_ref2_db = result['external_ref2'].values[0]
            logger.debug(f"fetched external_ref4 from txn table is : {external_ref2_db}")
            external_ref3_db = result['external_ref3'].values[0]
            logger.debug(f"fetched external_ref5 from txn table is : {external_ref3_db}")
            auth_code_db = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code_db}")
            merchant_name_db = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name_db}")
            merchant_code_db = result['merchant_code'].values[0]
            logger.debug(f"Fetching merchant_code from txn table : {merchant_code_db}")
            txn_type_db = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table : {txn_type_db}")
            user_mobile_db = result['user_mobile'].values[0]
            logger.debug(f"Fetching user_mobile from txn table : {user_mobile_db}")
            username_db = result['username'].values[0]
            logger.debug(f"Fetching username from txn table : {username_db}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            amount_original_db = result['amount_original'].iloc[0]
            logger.debug(f"Fetching amount_original from txn table : {amount_original_db}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "Cash Payment",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": f"{fine_amount:,}.00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_name": str(ph_number),
                    "reference_2": "Non segregated waste",
                    "reference_3": "Domestic Violation"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                txn_history_page = TransHistoryPage(app_driver)
                home_page.click_on_history_config()
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(
                    f"Fetching txn customer mobile from txn history for the txn : {txn_id}, {app_customer_mobile}")
                app_reference_2 = txn_history_page.fetch_reference_2_text()
                logger.info(f"fetching txn Reference 2 {app_reference_2}")
                app_reference_3 = txn_history_page.fetch_reference_3_text()
                logger.info(f"fetching txn Reference 3 {app_reference_3}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "customer_name": str(app_customer_mobile),
                    "reference_2": app_reference_2,
                    "reference_3": app_reference_3
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "txn_amt": fine_amount,
                    "pmt_mode": "CASH",
                    "user_mobile": app_username,
                    "txn_type": txn_type,
                    "acquirer_code": "NONE" if auth_code_db is None else auth_code_db,
                    "order_no": external_ref,
                    "total_amt": float(fine_amount),
                    "org_code": org_code_txn,
                    "merchant_code": org_code,
                    "merchant_name": merchant_name_db,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                org_code_api = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {org_code_api}")
                order_no_api = response['orderNumber']
                logger.debug(f"Value of orderNumber obtained from txnlist api : {order_no_api}")
                status_api = response["status"]
                logger.debug(f"Value of status no obtained from txnlist api : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"Value of amount no obtained from txnlist api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Value of payment mode no obtained from txnlist api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Value of state no obtained from txnlist api : {state_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Value of txn type no obtained from txnlist api : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"Value of date api no obtained from txnlist api : {date_api}")
                user_mobile_api = response['userMobile']
                logger.debug(f"Value of user mobile no obtained from txnlist api : {user_mobile_api}")
                settle_status_api = response['settlementStatus']
                logger.debug(f"Value of settlementStatus obtained from txnlist api : {settle_status_api}")
                acquirer_code_api = response['acquirerCode']
                logger.debug(f"Value of acquirerCode obtained from txnlist api : {acquirer_code_api}")
                total_amt_api = response['totalAmount']
                logger.debug(f"Value of totalAmount obtained from txnlist api : {total_amt_api}")
                org_code_api = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {org_code_api}")
                merchant_code_api = response['merchantCode']
                logger.debug(f"Value of merchantCcode obtained from txnlist api : {merchant_code_api}")
                merchant_name_api = response['merchantName']
                logger.debug(f"Value of merchantName obtained from txnlist api : {merchant_name_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "settle_status": settle_status_api,
                    "pmt_state": state_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "user_mobile": user_mobile_api,
                    "txn_type": txn_type_api,
                    "acquirer_code": acquirer_code_api,
                    "order_no": order_no_api,
                    "total_amt": total_amt_api,
                    "org_code": org_code_api,
                    "merchant_code": merchant_code_api,
                    "merchant_name": merchant_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
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
                        "pmt_state": "SETTLED",
                        "user_mobile": app_username,
                        "user_name": app_username,
                        "txn_type": "CHARGE",
                        "pmt_status": "AUTHORIZED",
                        "settle_status": "SETTLED",
                        "pmt_mode": "CASH",
                        "org_code": org_code,
                        "merchant_code": org_code,
                        "txn_amt": fine_amount,
                        "amt_original": fine_amount,
                        "external_ref2": "Non segregated waste",
                        "external_ref3": "Domestic Violation"
                    }
                    logger.debug(f"expected_db_values: {expected_db_values}")

                    actual_db_values = {
                        "pmt_state": state_db,
                        "user_mobile": user_mobile_db,
                        "user_name": username_db,
                        "txn_type": txn_type_db,
                        "pmt_status": status_db,
                        "settle_status": settlement_status_db,
                        "pmt_mode": payment_mode_db,
                        "org_code": org_code,
                        "merchant_code": merchant_code_db,
                        "txn_amt": amount_db,
                        "amt_original": amount_original_db,
                        "external_ref2": external_ref2_db,
                        "external_ref3": external_ref3_db,
                    }
                    logger.debug(f"actual_db_values : {actual_db_values}")
                    Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
                except Exception as e:
                    Configuration.perform_db_val_exception(testcase_id, e)
                logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {'PAID BY:': 'CASH',
                                               'BASE AMOUNT:': f"Rs.{fine_amount:,}.00",
                                               'date': txn_date,
                                               'time': txn_time
                                               }
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_300_307_005():
    """
    Sub Feature Code: UI_Common_Config_BBMP_Verify_Success_Cash_SVM_Violation_Type_Of_Spot_Fine_Non_Segregation_Of_Waste (Select Type of Establishment : Small Commerical Establishment)
    Sub Feature Description: Verify success cash txn for type of spot fine is non segregation of waste (Select Type of Establishment : Small Commerical Establishment)
    TC naming code description: 100: Payment Method, 300: Config, 307: BBMP, 005: TC005
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
        logger.debug(f"Fetching org_code value from the org_employee table {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_on_start_btn()
            logger.info(f"Clicked on start button")
            home_page.click_on_svm_violation()
            logger.debug("Clicked on SWM Violation button")
            home_page.click_on_non_segregation_of_waste()
            logger.debug("Clicked on Non segregation of waste button")
            name = 'test_' + str(random.randint(1, 100))
            ph_number = random.randint(6000000000, 9000000000)
            ward_no = random.randint(100, 500)
            home_page.enter_details_for_small_commercial_establishment(name, ph_number, ward_no, "test_locality")
            fine_amount = home_page.fetch_amount_from_enter_details_and_pay_screen()
            logger.debug(f"Fetched fine amount from the enter details and pay screen : {fine_amount}")
            payment_pg = PaymentPage(app_driver)
            payment_pg.click_on_cash_payment_mode_and_confirm_btn()
            logger.debug('clicked on the cash mode and confirm on the LOB page')
            payment_pg.click_on_proceed_homepage()

            query = (f"select * from txn where org_code ='{org_code}' and customer_mobile ='{ph_number}' "
                     f"order by created_time Desc limit 1;")
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            customer_mobile = result['customer_mobile'].iloc[0]
            logger.debug(f"Fetching customer_mobile from txn table : {customer_mobile}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            status_db = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            external_ref2_db = result['external_ref2'].values[0]
            logger.debug(f"fetched external_ref4 from txn table is : {external_ref2_db}")
            external_ref3_db = result['external_ref3'].values[0]
            logger.debug(f"fetched external_ref5 from txn table is : {external_ref3_db}")
            auth_code_db = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code_db}")
            merchant_name_db = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name_db}")
            merchant_code_db = result['merchant_code'].values[0]
            logger.debug(f"Fetching merchant_code from txn table : {merchant_code_db}")
            txn_type_db = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table : {txn_type_db}")
            user_mobile_db = result['user_mobile'].values[0]
            logger.debug(f"Fetching user_mobile from txn table : {user_mobile_db}")
            username_db = result['username'].values[0]
            logger.debug(f"Fetching username from txn table : {username_db}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            amount_original_db = result['amount_original'].iloc[0]
            logger.debug(f"Fetching amount_original from txn table : {amount_original_db}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "Cash Payment",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": f"{fine_amount:,}.00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_name": str(ph_number),
                    "reference_2": "Non segregated waste",
                    "reference_3": "SMALL COMMERCIAL EST. VIOLATION"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                txn_history_page = TransHistoryPage(app_driver)
                home_page.click_on_history_config()
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(
                    f"Fetching txn customer mobile from txn history for the txn : {txn_id}, {app_customer_mobile}")
                app_reference_2 = txn_history_page.fetch_reference_2_text()
                logger.info(f"fetching txn Reference 2 {app_reference_2}")
                app_reference_3 = txn_history_page.fetch_reference_3_text()
                logger.info(f"fetching txn Reference 3 {app_reference_3}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "customer_name": str(app_customer_mobile),
                    "reference_2": app_reference_2,
                    "reference_3": app_reference_3
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "txn_amt": fine_amount,
                    "pmt_mode": "CASH",
                    "user_mobile": app_username,
                    "txn_type": txn_type,
                    "acquirer_code": "NONE" if auth_code_db is None else auth_code_db,
                    "order_no": external_ref,
                    "total_amt": float(fine_amount),
                    "org_code": org_code_txn,
                    "merchant_code": org_code,
                    "merchant_name": merchant_name_db,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                org_code_api = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {org_code_api}")
                order_no_api = response['orderNumber']
                logger.debug(f"Value of orderNumber obtained from txnlist api : {order_no_api}")
                status_api = response["status"]
                logger.debug(f"Value of status no obtained from txnlist api : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"Value of amount no obtained from txnlist api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Value of payment mode no obtained from txnlist api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Value of state no obtained from txnlist api : {state_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Value of txn type no obtained from txnlist api : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"Value of date api no obtained from txnlist api : {date_api}")
                user_mobile_api = response['userMobile']
                logger.debug(f"Value of user mobile no obtained from txnlist api : {user_mobile_api}")
                settle_status_api = response['settlementStatus']
                logger.debug(f"Value of settlementStatus obtained from txnlist api : {settle_status_api}")
                acquirer_code_api = response['acquirerCode']
                logger.debug(f"Value of acquirerCode obtained from txnlist api : {acquirer_code_api}")
                total_amt_api = response['totalAmount']
                logger.debug(f"Value of totalAmount obtained from txnlist api : {total_amt_api}")
                org_code_api = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {org_code_api}")
                merchant_code_api = response['merchantCode']
                logger.debug(f"Value of merchantCcode obtained from txnlist api : {merchant_code_api}")
                merchant_name_api = response['merchantName']
                logger.debug(f"Value of merchantName obtained from txnlist api : {merchant_name_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "settle_status": settle_status_api,
                    "pmt_state": state_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "user_mobile": user_mobile_api,
                    "txn_type": txn_type_api,
                    "acquirer_code": acquirer_code_api,
                    "order_no": order_no_api,
                    "total_amt": total_amt_api,
                    "org_code": org_code_api,
                    "merchant_code": merchant_code_api,
                    "merchant_name": merchant_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
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
                        "pmt_state": "SETTLED",
                        "user_mobile": app_username,
                        "user_name": app_username,
                        "txn_type": "CHARGE",
                        "pmt_status": "AUTHORIZED",
                        "settle_status": "SETTLED",
                        "pmt_mode": "CASH",
                        "org_code": org_code,
                        "merchant_code": org_code,
                        "txn_amt": fine_amount,
                        "amt_original": fine_amount,
                        "external_ref2": "Non segregated waste",
                        "external_ref3": "SMALL COMMERCIAL EST. VIOLATION"
                    }
                    logger.debug(f"expected_db_values: {expected_db_values}")

                    actual_db_values = {
                        "pmt_state": state_db,
                        "user_mobile": user_mobile_db,
                        "user_name": username_db,
                        "txn_type": txn_type_db,
                        "pmt_status": status_db,
                        "settle_status": settlement_status_db,
                        "pmt_mode": payment_mode_db,
                        "org_code": org_code,
                        "merchant_code": merchant_code_db,
                        "txn_amt": amount_db,
                        "amt_original": amount_original_db,
                        "external_ref2": external_ref2_db,
                        "external_ref3": external_ref3_db,
                    }
                    logger.debug(f"actual_db_values : {actual_db_values}")
                    Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
                except Exception as e:
                    Configuration.perform_db_val_exception(testcase_id, e)
                logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {'PAID BY:': 'CASH',
                                               'BASE AMOUNT:': f"Rs.{fine_amount:,}.00",
                                               'date': txn_date,
                                               'time': txn_time
                                               }
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
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
