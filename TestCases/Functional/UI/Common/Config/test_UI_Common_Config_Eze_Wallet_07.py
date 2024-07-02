import random
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_200_202_029():
    """
        Sub Feature Code: UI_Common_Ezewallet_Balance_Is_Displayed (Role: Agency)
        Sub Feature Description: Verify whether the balance is displayed correctly in ezewallet screen (Role: Agency)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 029: TC029
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
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for Eze_wallet is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet setting preconditions is : {response}")

        # Fetching the agency balance
        query = f"select * from account where entity_id ='{org_code}' and account_type='LEDGER_ACCOUNT';"
        logger.debug(f"Query to fetch data from the account table: {query}")
        result = DBProcessor.getValueFromDB(query, "closedloop")
        logger.debug(f"Query result for account table : {result}")
        balance_db = result['balance'].values[0]
        logger.debug(f"Fetching balance value from account table {balance_db}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX app using agency username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_navigation_drawer()
            logger.info(f"Clicked on navigation drawer")
            logger.info(f"Clicking on Eze_wallet")
            home_page.click_on_eze_wallet()
            logger.info(f"Clicked on Eze_wallet")
            app_balance_value = home_page.fetch_balance_txt().split(' ')
            logger.info(f"Fetched app balance text value is: {app_balance_value}")
            balance_value = ["₹ " + app_balance_value[1] if "." in app_balance_value[1] else "₹ " + app_balance_value[1] + ".0"]
            logger.info(f"Fetched app balance_value is: {app_balance_value}")

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
                expected_db_values = {
                    "balance": balance_value[0].replace(',','')
                }
                logger.debug(f"expected_app_values: {expected_db_values}")

                actual_db_values = {
                    "balance": '₹ ' + str(balance_db)
                }
                logger.debug(f"actual_app_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_200_202_030():
    """
        Sub Feature Code: UI_Common_Ezewallet_Withdraw_Fund_Is_Displayed_Clickable_&_Navigate_Withdraw_Fund_Screen (Role: Agency)
        Sub Feature Description: Verify whether withdraw fund option is displayed under quick action
        and Verify user is clickable on withdraw funds and navigate to withdraw fund screen (Role: Agency)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 030: TC030
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
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for Eze_wallet is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet setting preconditions is : {response}")

        # Fetching the agency balance
        query = f"select * from account where entity_id ='{org_code}' and account_type='LEDGER_ACCOUNT';"
        logger.debug(f"Query to fetch data from the account table: {query}")
        result = DBProcessor.getValueFromDB(query, "closedloop")
        logger.debug(f"Query result for account table : {result}")
        balance_db = result['balance'].values[0]
        logger.debug(f"Fetching balance value from account table {balance_db}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX app using agency username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_navigation_drawer()
            logger.info(f"Clicked on navigation drawer")
            logger.info(f"Clicking on Eze_wallet")
            home_page.click_on_eze_wallet()
            logger.info(f"Clicked on Eze_wallet")
            try:
                home_page.click_on_withdraw_funds()
                home_page.validate_withdraw_fund_title()
                logger.info("Clicked on withdraw funds quick actions and navigated to withdraw fund screen")
                msg = "With Draw funds is displayed in quick action and able to click, navigate to withdraw fund screen"

            except Exception as e:
                logger.error(f"With Draw funds is not displayed in quick action and able to click, navigate to"
                             f" withdraw fund screen due : {e}")
                msg = ("With Draw funds is not displayed in quick action and able to click, navigate "
                       "to withdraw fund screen")

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

        # -----------------------------------------Start of App Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                expected_app_values = {
                    "msg": "With Draw funds is displayed in quick action and able to click, navigate to withdraw"
                           " fund screen"
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
        # -----------------------------------------End of App Validation------------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_200_202_031():
    """
        Sub Feature Code: UI_Common_Ezewallet_Verify_Agency_Name_Displayed_Correctly_In_WithDraw_Fund_Screen (Role: Agency)
        Sub Feature Description: Verify the agency name is displayed correctly in the withdraw Fund screen (Role: Agency)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 031: TC031
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
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for Eze_wallet is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet setting preconditions is : {response}")

        # Fetching agency name
        query = f"select ext_meta_data from agent where agent_id ='{app_username}';"
        logger.debug(f"Query to fetch data from the agent table: {query}")
        result = DBProcessor.getValueFromDB(query, "closedloop")
        logger.debug(f"Query result for agent table : {result}")
        agency_name_db = result['ext_meta_data'].values[0]
        logger.debug(f"Fetching agency_name_db value from the agent table {agency_name_db}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX app using agency username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_navigation_drawer()
            logger.info(f"Clicked on navigation drawer")
            logger.info(f"Clicking on Eze_wallet")
            home_page.click_on_eze_wallet()
            logger.info(f"Clicked on Eze_wallet")
            home_page.click_on_withdraw_funds()
            logger.info(f"Clicked on withdraw funds")
            agency_name = home_page.fetch_agency_name_txt()
            logger.info(f"Agency name in with draw funds is :{agency_name}")

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
                expected_db_values = {
                    "agency_name": agency_name
                }
                logger.debug(f"expected_app_values: {expected_db_values}")

                actual_db_values = {
                    "agency_name": agency_name_db.split(':')[1].replace('}', '').replace('"', '')
                }
                logger.debug(f"actual_app_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_200_202_032():
    """
        Sub Feature Code: UI_Common_Ezewallet_Verify_WithDraw_Flow (Role: Agency)
        Sub Feature Description: Verify the flow of withdraw fund (Role: Agency)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 032: TC032
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

        query = (f"select username,org_code from org_employee where org_code in "
                 f"(select org_code from org_employee where username='{str(app_username)}')"
                 f"and roles='ROLE_CLAGENT';")
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for org_employee table : {result}")
        agent_username = result['username'].values[0]
        logger.info(f"Fetching agent mobile_no from org_employee table: {agent_username}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from org_employee table {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for Eze_wallet is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX app using agency username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_navigation_drawer()
            logger.info(f"Clicked on navigation drawer")
            logger.info(f"Clicking on Eze_wallet")
            home_page.click_on_eze_wallet()
            logger.info(f"Clicked on Eze_wallet")
            home_page.click_on_withdraw_funds()
            logger.info(f"Clicked on withdraw funds")
            transfer_amt = random.randint(10, 50)
            logger.info(f"Randomly generated transfer_amt is : {transfer_amt}")
            home_page.enter_mobile_no_and_transfer_amt(agent_mobile_no=agent_username, transfer_amt=transfer_amt)
            logger.info(f"Enter with draw funds details")
            home_page.click_on_lang_proceed()
            logger.info(f"Clicked on proceed button")
            home_page.click_on_confirm_btn()
            logger.info(f"Clicked on confirm button")
            home_page.click_on_go_to_wallet()
            logger.info(f"Clicked on go to wallet")
            wallet_top_balance = home_page.fetch_balance_txt().split(' ')
            logger.info(f"Fetch balance value after wallet top_up : {wallet_top_balance}")
            wallet_top_bal = ["₹ " + wallet_top_balance[1] if "." in wallet_top_balance[1] else "₹ " + wallet_top_balance[1] + ".0"]
            logger.info(f"Fetched app  wallet_top_bal is: { wallet_top_bal}")

            query = f"select * from account where entity_id = '{org_code}';"
            logger.debug(f"Query to fetch data from the account table: {query}")
            result = DBProcessor.getValueFromDB(query, "closedloop")
            logger.debug(f"Query result for account table : {result}")
            balance_db = result['balance'].values[0]
            logger.debug(f"Fetching balance value from account table {balance_db}")
            account_type_db = result['account_type'].values[0]
            logger.debug(f"Fetching account_type value from account table {account_type_db}")
            entity_type_db = result['entity_type'].values[0]
            logger.debug(f"Fetching entity_type value from account table {entity_type_db}")
            entity_id_db = result['entity_id'].values[0]
            logger.debug(f"Fetching entity_id value from account table {entity_id_db}")
            status_db = result['status'].values[0]
            logger.debug(f"Fetching status value from account table {status_db}")

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
                expected_db_values = {
                    "balance": wallet_top_bal[0].replace(',', ''),
                    "account_type": "LEDGER_ACCOUNT",
                    "entity_type": "MERCHANT",
                    "entity_id": org_code,
                    "status": "ACTIVE"
                }
                logger.debug(f"expected_app_values: {expected_db_values}")

                actual_db_values = {
                    "balance": '₹ ' + str(balance_db),
                    "account_type": account_type_db,
                    "entity_type": entity_type_db,
                    "entity_id": entity_id_db,
                    "status": status_db
                }
                logger.debug(f"actual_app_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_200_202_033():
    """
        Sub Feature Code: UI_Common_Ezewallet_Enter_Invalid_Wallet_ID (Role: Agency)
        Sub Feature Description: Verify by entering invalid wallet id  (Role: Agency)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 033: TC033
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
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for Eze_wallet is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX app using agency username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_navigation_drawer()
            logger.info(f"Clicked on navigation drawer")
            logger.info(f"Clicking on Eze_wallet")
            home_page.click_on_eze_wallet()
            logger.info(f"Clicked on Eze_wallet")
            home_page.click_on_withdraw_funds()
            logger.info(f"Clicked on withdraw funds")
            transfer_amt = random.randint(10, 50)
            logger.info(f"Randomly generated transfer_amt is : {transfer_amt}")
            agent_mobile_no = '1232729123'
            home_page.enter_mobile_no_and_transfer_amt(agent_mobile_no=agent_mobile_no, transfer_amt=transfer_amt)
            logger.info(f"Enter with draw funds details")

            try:
                home_page.click_on_lang_proceed()
                logger.info(f"Clicked on proceed button")
                home_page.click_on_confirm_btn()
                logger.info(f"Clicked on confirm button")
                home_page.validate_withdraw_fund_title()
                logger.info(f"Agent doesn't exist is visible when clicked on proceed button")
                msg = "Agent Doesn't Exist"

            except Exception as e:
                logger.error(f"Agent doesn't exist is not visible due to: {e}")
                msg = "Agent Does Exist"

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

        # -----------------------------------------Start of App Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                expected_app_values = {
                    "msg": "Agent Doesn't Exist"
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
        # -----------------------------------------End of App Validation------------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)