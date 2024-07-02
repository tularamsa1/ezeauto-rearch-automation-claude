import datetime
from datetime import timedelta
import random
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, date_time_converter, \
    Ezewallet_processor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_200_202_026():
    """
        Sub Feature Code: UI_Common_Config_Ezewallet_Verify_search_By_Date_And_Date_clickable
        Sub Feature Description:verify search by date option clickable and also user is able to select the particular date(Role: agent)
        TC naming code description: 100: Payment Method, 200: Ezewallet, 202: North Bihar, 026: TC026
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        org_code = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["MerchantCode"]
        logger.debug(f"Fetching the org_code from Ezewallet sheet : {org_code}")
        app_username = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Username"]
        logger.debug(f"Fetching the app_username from Ezewallet sheet : {app_username}")
        app_password = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Password"]
        logger.debug(f"Fetching the app_password from Ezewallet sheet : {app_password}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet in preconditions : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
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
            logger.info(f"App homepage loaded successfully")
            home_page.click_side_menu_eng()
            logger.debug(f"clicked on side menu")
            home_page.click_on_eze_wallet()
            logger.debug(f"clicked on eze wallet option from the side menu")
            home_page.click_on_my_passbook()
            try:
                home_page.click_on_search_by_date_in_agency_or_agent_passbook_screen()
                logger.debug(f"search by date is visible and it is clickable")
                today_date = datetime.date.today()
                formatted_date = today_date.strftime("%a, %b ") + f"{today_date.day}"
                home_page.click_on_given_date(date=formatted_date)
                logger.debug(f"clicked on today date: {formatted_date} in the calendar")
                msg = "user is able to click on the search by date option and also able to select a particular date"
            except Exception as e:
                logger.error(f"unable to click on the search by date or unable to select a particular date"
                             f" due to error: {e}")
                msg = "user is not able to click on the search by date option or not able to select a particular date"

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
                    "msg": "user is able to click on the search by date option and also able to select a"
                           " particular date"

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
        # -----------------------------------------End of App Validation--------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_200_202_027():
    """
        Sub Feature Code: UI_Common_Config_Ezewallet_Verify_Txn_On_Present_Date
        Sub Feature Description: verify transaction done on present date in agency passbook(Role: Agency)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 027: TC027
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

        agent_user = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Username"]
        logger.debug(f"Fetching the app_username from Ezewallet sheet : {app_username}")


        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet in preconditions : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
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
            logger.info(f"App homepage loaded successfully")
            home_page.click_side_menu_eng()
            logger.debug(f"clicked on side menu")
            home_page.click_on_eze_wallet()
            logger.debug(f"clicked on ezewallet option from the side menu")
            home_page.click_on_transfer_funds()
            logger.debug("clicked on the transfer_funds btn")
            amount = random.randint(1, 50)
            home_page.perform_transfer_funds_from_agency_to_agent(agent_wallet_id=agent_user, transfer_amount=amount)
            home_page.click_on_confirm_btn()
            home_page.click_on_go_to_wallet_btn()
            query = f"select * from wallet_txn where merchant_id='{org_code}' order by created_time  desc limit 1;"
            result = DBProcessor.getValueFromDB(query, 'closedloop')
            created_time_db = result['created_time'].values[0]
            logger.debug(f"fetched created_time from db : {created_time_db}")
            transfer_mode = result['transfer_mode'].values[0]
            logger.debug(f"fetched transfer_mode from db : {transfer_mode}")
            query = (f"select * from account where entity_id ='NORTH_BIHAR_POWER_DISTRIB' and account_type="
                     f"'LEDGER_ACCOUNT';")
            result = DBProcessor.getValueFromDB(query, 'closedloop')
            agency_balance_db = result['balance'].values[0]

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
                date_and_time = date_time_converter.to_app_format(created_time_db)
                expected_app_values = {
                    "txn_amt": str(amount),
                    "agency_balance": str(agency_balance_db).rstrip("0").rstrip("."),
                    "date": date_and_time.replace(",", "")
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.click_on_agency_passbook()
                home_page.click_on_search_by_date_in_agency_or_agent_passbook_screen()
                today_date = datetime.date.today()
                formatted_date = today_date.strftime("%a, %b ") + f"{today_date.day}"
                home_page.click_on_given_date(date=formatted_date)
                logger.debug(f"clicked on today date: {formatted_date} in the calendar")
                home_page.click_on_ok_btn()
                formatted_transfer_mode = "Add funds" if transfer_mode == "ADDFUNDS" else "Transfer funds"
                app_txn_amount = home_page.fetch_agency_transaction_amount(formatted_transfer_mode)
                app_agency_balance = home_page.fetch_agency_balance_from_txn_history()
                app_date = home_page.fetch_agency_transaction_date(formatted_transfer_mode)

                actual_app_values = {
                    "txn_amt": app_txn_amount.split(' ')[1],
                    "agency_balance": app_agency_balance.split(' ')[1].replace(",", ""),
                    "date": app_date
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation--------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_200_202_028():
    """
        Sub Feature Code: UI_Common_Config_Ezewallet_Verify_Txn_On_Past_Date
        Sub Feature Description: verify transaction done on past date in agency passbook(Role: Agency)
        TC naming code description: 100: Payment Method, 200: Ezewallet, 202: North Bihar, 028: TC028
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
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet in preconditions : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
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
            logger.info(f"App homepage loaded successfully")
            home_page.click_side_menu_eng()
            logger.debug(f"clicked on side menu")
            home_page.click_on_eze_wallet()
            logger.debug(f"clicked on ezewallet option from the side menu")
            home_page.click_on_agency_passbook()
            home_page.click_on_search_by_date_in_agency_or_agent_passbook_screen()
            yesterday_date = datetime.date.today() - timedelta(days=1)
            formatted_yesterday_date_date = yesterday_date.strftime("%a, %b ") + f"{yesterday_date.day}"
            home_page.click_on_given_date(date=formatted_yesterday_date_date)
            logger.debug(f"clicked on today date: {formatted_yesterday_date_date} in the calendar")
            home_page.click_on_ok_btn()

            try:
                no_txn_msg = home_page.fetch_no_transaction_msg()
                amount_db = "No txn done"
                date_and_time = "No txn done"
                app_txn_amount = None
                app_date = "No txn done"
            except:
                yesterday_date_db_formate = yesterday_date.strftime('%Y-%m-%d')
                logger.debug(f"yesterday : {yesterday_date_db_formate}")
                query = (f"select * from wallet_txn where merchant_id='{org_code}' and created_time LIKE "
                         f"'%{yesterday_date_db_formate}%' order by created_time  desc limit 1;")
                logger.debug(f"query to fetch past txn details : {query}")
                result = DBProcessor.getValueFromDB(query, 'closedloop')
                created_time_db = result['created_time'].values[0]
                logger.debug(f"fetched txn time from db : {created_time_db}")
                transfer_mode = result['transfer_mode'].values[0]
                logger.debug(f"fetched transfer_mode from db : {transfer_mode}")
                amount_db = result['amount'].values[0]
                logger.debug(f"fetched txn amount from db : {amount_db}")
                date_and_time = date_time_converter.to_app_format(created_time_db)

                formatted_transfer_mode = "Add funds" if transfer_mode == "ADDFUNDS" else "Transfer funds"
                app_txn_amount = home_page.fetch_agency_transaction_amount(formatted_transfer_mode)
                logger.debug(f"fetched txn amount from app: {app_txn_amount}")

                app_date = home_page.fetch_agency_transaction_date(formatted_transfer_mode)
                logger.debug(f"fetched date from app: {app_txn_amount}")
                no_txn_msg = "Txn found"

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
                    "txn_msg": no_txn_msg,
                    "txn_amt": str(amount_db).rstrip("0").rstrip("."),
                    "date": date_and_time.replace(",", "")
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "txn_msg": no_txn_msg,
                    "txn_amt": app_txn_amount.split(' ')[1] if app_txn_amount is not None else "No txn done",
                    "date": app_date
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation--------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
