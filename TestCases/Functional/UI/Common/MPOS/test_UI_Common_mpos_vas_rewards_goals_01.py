import json
import sys
import random
from datetime import datetime, timedelta
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.mpos.app_rewards import Rewards, revert_back_to_original_status, collect_all_campaign_ids_for_org
from Utilities import ResourceAssigner, DBProcessor, ConfigReader, Validator, APIProcessor, rewards_processor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_mpos_600_602_010():
    """
    Sub Feature Code: UI_mpos_vas_Rewards_Goals_Order_Of_Creation
    Sub Feature Description: Recently created goals  should be displayed first
    TC naming code description: 600: Value added service, 602: Rewards, 010: TC010
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
                yesterday_date) + "' WHERE (status = 'WON' OR status = 'IN_PROGRESS' or status = 'CLAIMED') " \
                                  "AND org_code = '" + str(org_code) + "';"
            DBProcessor.setValueToDB(query, 'rewards')
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                           "password": portal_password,
                                                                                           "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["enableRewardForMerchants"] = "true"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions is : {response}")
            reward_name = f"COUPON_ENABLED : {random.randint(1, 10000)}"
            end_date = datetime.now() + timedelta(days=3)
            formatted_end_date = end_date.strftime('%Y-%m-%d')
            response_create_campaign = rewards_processor.create_campaign_reward('MER190211001', 'Ezetap@1234', org_code,
                                                                                formatted_end_date, reward_name)
            logger.debug("campaign is created successfully")
            json_resp = json.loads(response_create_campaign.text)
            campaign_id = json_resp["campaignId"]
            logger.debug(f"campaign_id : {campaign_id}")
            campaign_description = json_resp["description"]
            logger.debug(f"campaign_description : {campaign_description}")
            response_update_campaign = rewards_processor.update_campaign('MER190211001', 'Ezetap@1234', campaign_id)
            json_resp = json.loads(response_update_campaign.text)
            logger.debug(f" response received from updated campaign {json_resp}")
            query = "UPDATE campaign SET campaign_status = 'LIVE' where campaign_id = '" + str(campaign_id) + "';"
            logger.debug(f"query  is  {query}")
            result = DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"result for updated campaign table: {result}")
            query = f"INSERT INTO `campaign_target_base` (`campaign_id`, `status`, `created_time`, `modified_time`, " \
                    f"`created_by`, `modified_by`, `lock_id`, `org_code`, `control_type`) VALUES ('{campaign_id}', " \
                    f"'IN_PROGRESS', NOW(), NOW(), 'EZEAUTO', 'EZEAUTO', '1', '{org_code}', 'NORMAL');"
            result = DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"result for updated insert query : {result}")
            end_date_1 = datetime.now() + timedelta(days=4)
            formatted_end_date_1 = end_date_1.strftime('%Y-%m-%d')
            response_create_campaign = rewards_processor.create_campaign_reward('MER190211001', 'Ezetap@1234', org_code,
                                                                                formatted_end_date_1, reward_name)
            logger.debug("2nd campaign is created successfully")
            json_resp = json.loads(response_create_campaign.text)
            campaign_id_1 = json_resp["campaignId"]
            logger.debug(f"campaign_id_1 : {campaign_id}")
            campaign_description_1 = json_resp["description"]
            logger.debug(f"campaign_description_1 : {campaign_description_1}")
            response_update_campaign = rewards_processor.update_campaign('MER190211001', 'Ezetap@1234', campaign_id_1)
            json_resp = json.loads(response_update_campaign.text)
            logger.debug(f" response received from updated campaign {json_resp}")
            query = "UPDATE campaign SET campaign_status = 'LIVE' where campaign_id = '" + str(campaign_id_1) + "';"
            logger.debug(f"query  is  {query}")
            result = DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"result for updated campaign table to live : {result}")
            query = f"INSERT INTO `campaign_target_base` (`campaign_id`, `status`, `created_time`, `modified_time`," \
                    f" `created_by`, `modified_by`, `lock_id`, `org_code`, `control_type`) VALUES ('{campaign_id_1}'," \
                    f" 'IN_PROGRESS', NOW(), NOW(), 'EZEAUTO', 'EZEAUTO', '1', '{org_code}', 'NORMAL');"
            result = DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"result for updated insert query : {result}")
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
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.debug(f"App homepage loaded successfully")
                reward_page = Rewards(app_driver)
                reward_page.click_on_side_menu()
                reward_page.click_on_my_rewards_from_side_menu()
                logger.debug("Reward button is being clicked from side menu")
                try:
                    expiry_1, expiry_2 = reward_page.get_goal_expiry_date()
                    validation = "SUCCESS" if expiry_1 == "in 4 days" and expiry_2 == "in 5 days" else "Failed"
                except Exception as e:
                    validation = f"N/A: {str(e)}"
            finally:
                revert_back_to_original_status(in_progress_list_ids, won_list_ids, claimed_list_ids)
                logger.debug(f"campaign ids are being reverted back to its original status")
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
                expected_app_values = {"result": "SUCCESS"}

                actual_app_values = {"result": validation}
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
def test_mpos_600_602_011():
    """
    Sub Feature Code: UI_mpos_vas_Rewards_Goals_Live
    Sub Feature Description: Verify the LIVE Goals are present under Goals tab
    TC naming code description: 600: Value added service, 602: Rewards, 011: TC011
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
                yesterday_date) + "' WHERE (status = 'WON' OR status = 'IN_PROGRESS' or status = 'CLAIMED') AND " \
                                  "org_code = '" + str(org_code) + "';"
            DBProcessor.setValueToDB(query, 'rewards')
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                           "password": portal_password,
                                                                                           "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["enableRewardForMerchants"] = "true"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions is : {response}")
            reward_name = f"COUPON_ENABLED : {random.randint(1, 10000)}"
            end_date = datetime.now() + timedelta(days=3)
            formatted_end_date = end_date.strftime('%Y-%m-%d')
            response_create_campaign = rewards_processor.create_campaign_reward('MER190211001', 'Ezetap@1234', org_code,
                                                                                formatted_end_date, reward_name)
            logger.debug("campaign is created successfully")
            json_resp = json.loads(response_create_campaign.text)
            campaign_id = json_resp["campaignId"]
            logger.debug(f"campaign_id : {campaign_id}")
            campaign_description = json_resp["description"]
            logger.debug(f"campaign_description : {campaign_description}")
            response_update_campaign = rewards_processor.update_campaign('MER190211001', 'Ezetap@1234', campaign_id)
            json_resp = json.loads(response_update_campaign.text)
            logger.debug(f" response received from updated campaign {json_resp}")
            query = "UPDATE campaign SET campaign_status = 'LIVE' where campaign_id = '" + str(campaign_id) + "';"
            logger.debug(f"query  is  {query}")
            result = DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"result for updated campaign table : {result}")
            query = f"INSERT INTO `campaign_target_base` (`campaign_id`, `status`, `created_time`, `modified_time`," \
                    f" `created_by`, `modified_by`, `lock_id`, `org_code`, `control_type`) VALUES ('{campaign_id}', " \
                    f"'IN_PROGRESS', NOW(), NOW(), 'EZEAUTO', 'EZEAUTO', '1', '{org_code}', 'NORMAL');"
            result = DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"result for updated insert query : {result}")
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
                logger.debug(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                 # home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.debug(f"App homepage loaded successfully")
                reward_page = Rewards(app_driver)
                reward_page.click_on_side_menu()
                reward_page.click_on_my_rewards_from_side_menu()
                logger.info("Reward button is being clicked from side menu")
                try:
                    goal_description = reward_page.get_goal_description()
                    if goal_description == campaign_description:
                        result = "SUCCESS"
                except Exception as e:
                    result = f"N/A{str(e)}"
            finally:
                revert_back_to_original_status(in_progress_list_ids, won_list_ids, claimed_list_ids)
                logger.debug(f"campaign ids are being reverted back to its original status")

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
                expected_app_values = {"result": "SUCCESS"}
                actual_app_values = {"result": result}
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
def test_mpos_600_602_012():
    """
    Sub Feature Code: UI_mpos_vas_Rewards_Goals_Expired
    Sub Feature Description: Verify the expired Goals are present at the bottom of the Goals tab with the right message
    TC naming code description: 600: Value added service, 602: Rewards, 012: TC012
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
            reward_name = f"COUPON_ENABLED : {random.randint(1, 10000)}"
            end_date = datetime.now() + timedelta(days=3)
            formatted_end_date = end_date.strftime('%Y-%m-%d')
            response_create_campaign = rewards_processor.create_campaign_reward('MER190211001', 'Ezetap@1234', org_code,
                                                                                formatted_end_date, reward_name)
            logger.debug("campaign is created successfully")
            json_resp = json.loads(response_create_campaign.text)
            campaign_id = json_resp["campaignId"]
            logger.debug(f"campaign_id : {campaign_id}")
            campaign_description = json_resp["description"]
            logger.debug(f"campaign_description : {campaign_description}")
            response_update_campaign = rewards_processor.update_campaign('MER190211001', 'Ezetap@1234', campaign_id)
            json_resp = json.loads(response_update_campaign.text)
            logger.debug(f"response received from updated campaign {json_resp}")
            query = "UPDATE campaign SET campaign_status = 'LIVE' where campaign_id = '" + str(campaign_id) + "';"
            logger.debug(f"query  is  {query}")
            result = DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"result for updated campaign table : {result}")
            query = f"INSERT INTO `campaign_target_base` (`campaign_id`, `status`, `created_time`, `modified_time`," \
                    f" `created_by`, `modified_by`, `lock_id`, `org_code`, `control_type`) VALUES ('{campaign_id}', " \
                    f"'IN_PROGRESS', NOW(), NOW(), 'EZEAUTO', 'EZEAUTO', '1', '{org_code}', 'NORMAL');"
            result = DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"result for updated insert query : {result}")
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
                yesterday_date = datetime.now() - timedelta(days=1)
                formatted_datetime = yesterday_date.strftime('%Y-%m-%d %H:%M:%S')
                query = "update campaign set end_date= '" + str(
                    formatted_datetime) + "' where campaign_id='" + str(campaign_id) + "';"
                logger.debug(f"Query to update goal to expiry : {query}")
                DBProcessor.setValueToDB(query, 'rewards')
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                 # home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.debug(f"App homepage loaded successfully")
                reward_page = Rewards(app_driver)
                reward_page.click_on_side_menu()
                reward_page.click_on_my_rewards_from_side_menu()
                logger.info("Reward button is being clicked from side menu")
                expected_date = yesterday_date.strftime('%d %B %Y')
                logger.debug(f"Expected date is : {expected_date}")
                expiry_description = reward_page.get_goal_description()
                logger.debug(f"expiry_description is : {expiry_description}")
                expiry_date = reward_page.get_expiry_date()
                logger.debug(f"expiry_date is : {expiry_date}")
                expiry_status = reward_page.get_expiry_status()
                logger.debug(f"expiry_status is : {expiry_status}")
            finally:
                revert_back_to_original_status(in_progress_list_ids, won_list_ids, claimed_list_ids)
                logger.debug(f"campaign ids are being reverted back to its original status")

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
                expected_app_values = {"title": campaign_description,
                                       "expiry_date": expected_date,
                                       "status": "Expired"}

                actual_app_values = {"title": expiry_description,
                                     "expiry_date": expiry_date,
                                     "status": expiry_status}
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
