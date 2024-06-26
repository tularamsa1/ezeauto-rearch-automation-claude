import json
import random
import sys
import pytest
from datetime import datetime, timedelta
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.mpos.app_rewards import Rewards, collect_all_campaign_ids_for_org, revert_back_to_original_status
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, rewards_processor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_mpos_600_602_002():
    """
    Sub Feature Code: UI_mpos_vas_Rewards_Navigation_Main Screen
    Sub Feature Description: Verify user is navigated to rewards screen by clicking on rewards tab from MPOS main screen
    TC naming code description: 600:value_added_services,602: rewards,002: TC002
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
        testsuite_teardown.revert_org_settings_default(org_code, portal_un=portal_username,
                                                       portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["enableRewardForMerchants"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, reward_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
             # home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            rewards_page = Rewards(app_driver)
            rewards_page.click_on_my_rewards_tab_from_main_screen()
            logger.debug("clicking on my rewards from home page")
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
                expected_app_values = {"text": "My Rewards"}
                text = rewards_page.fetch_txt_from_my_rewards_screen()
                actual_app_values = {"text": text}
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
def test_mpos_600_602_003():
    """
    Sub Feature Code: UI_mpos_vas_Rewards_Navigation_Side_Menu
    Sub Feature Description: Verify user is navigated to rewards upon clicking on rewards from the side menu
    TC naming code description:600:  value_added_services,602: rewards,003: TC003
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
        testsuite_teardown.revert_org_settings_default(org_code, portal_un=portal_username,
                                                       portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["enableRewardForMerchants"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, reward_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
             # home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_to_load_today_sales()
            logger.info(f"App homepage loaded successfully")
            rewards_page = Rewards(app_driver)
            rewards_page.click_on_side_menu()
            rewards_page.click_on_my_rewards_from_side_menu()
            logger.debug("clicking on my rewards from side menu")
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
                expected_app_values = {"text": "My Rewards"}
                text = rewards_page.fetch_txt_from_my_rewards_screen()
                actual_app_values = {"text": text}
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
def test_mpos_600_602_004():
    """
    Sub Feature Code: UI_mpos_vas_Rewards_Navigation_Home_Dashboard
    Sub Feature Description: Verify user should navigate to rewards upon clicking on rewards dashboard
    TC naming code description:600:  value_added_services,602: rewards,004: TC004
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
        testsuite_teardown.revert_org_settings_default(org_code, portal_un=portal_username,
                                                       portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        in_progress_list_ids, won_list_ids, claimed_list_ids = collect_all_campaign_ids_for_org(org_code)
        logger.debug(f"Collected campaign ids with status IN_PROGRESS, WON and CLAIMED")
        try:
            yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            query = "UPDATE campaign_target_base SET status = 'EXPIRY', claim_expiry = '" + str(
                yesterday_date) + "' WHERE (status = 'WON' OR status = 'IN_PROGRESS' or status = 'CLAIMED') AND org_code = '" + str(
                org_code) + "';"
            DBProcessor.setValueToDB(query, 'rewards')
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                           "password": portal_password,
                                                                                           "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["enableRewardForMerchants"] = "true"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions is : {response}")
            for _ in range(3):
                reward_name = f"COUPON_ENABLED : {random.randint(1, 10000)}"
                response_create_campaign = rewards_processor.create_campaign('MER190211001', 'Ezetap@1234', org_code,
                                                                             reward_name)
                logger.debug("campaign is created successfully")
                json_resp = json.loads(response_create_campaign.text)
                campaign_id = json_resp["campaignId"]
                logger.debug(f"campaign_id : {campaign_id}")
                response = rewards_processor.update_campaign('MER190211001', 'Ezetap@1234', campaign_id)
                logger.debug(f"Response received for updated campaign is : {response.status_code}")
                query = f"INSERT INTO `campaign_target_base` (`campaign_id`, `status`, `created_time`, `modified_time`, `created_by`, `modified_by`, `lock_id`, `org_code`, `control_type`) VALUES ('{campaign_id}', 'IN_PROGRESS', NOW(), NOW(), 'EZETAP', 'EZETAP', '1', '{org_code}', 'NORMAL');"
                result = DBProcessor.setValueToDB(query, 'rewards')
                logger.debug(f"result for updated insert query : {result}")
                coupon_code = datetime.now().strftime('%M%S')
                pin = int(datetime.now().strftime('%M%S')) + 1
                response_create_coupon = rewards_processor.create_coupon('MER190211001', 'Ezetap@1234', coupon_code,
                                                                         pin,
                                                                         reward_name)
                logger.debug(f"Flipkart coupan Created : {response_create_coupon}")
                api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                      "password": portal_password})
                logger.debug(f"API details for DB refresh  : {api_details} ")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for DB  Refresh is : {response}")
        except Exception as e:
            revert_back_to_original_status(in_progress_list_ids, won_list_ids, claimed_list_ids)
            raise e
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, reward_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            try:
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                 # home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                logger.info(f"App homepage loaded successfully")
                rewards_page = Rewards(app_driver)
                b, b1, c1 = rewards_page.get_rewards_dashboard_coordinates()
                logger.debug(f"Relative co-ordinates of rewards dashboard {b} and {b1} and {c1}")
                rewards_page.scroll_to_element_horizontally(swipe_count=3, b=b, b1=b1, c1=c1)
                rewards_page.click_on_rewards_from_dashboard()
                text = rewards_page.fetch_txt_from_my_rewards_screen()
            finally:
                revert_back_to_original_status(in_progress_list_ids, won_list_ids, claimed_list_ids)
                logger.debug(f"campaign ids are being reverted back to its original status")
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
                expected_app_values = {"text": "My Rewards"}
                actual_app_values = {"text": text}
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
