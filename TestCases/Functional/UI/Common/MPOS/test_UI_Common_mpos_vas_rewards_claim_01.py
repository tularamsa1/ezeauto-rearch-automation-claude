import random
from datetime import datetime, timedelta
import json
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.mpos.app_rewards import Rewards, collect_all_campaign_ids_for_org, revert_back_to_original_status
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, rewards_processor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_mpos_600_602_017():
    """
    Sub Feature Code: UI_mpos_vas_Rewards_Claims_Completed
    Sub Feature Description: Verify the Claimed rewards are present on the Rewards tab
    TC naming code description:600:  value_added_services,602: rewards,017: TC017
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
            response_create_campaign = rewards_processor.create_campaign('MER190211001', 'Ezetap@1234', org_code, reward_name)
            logger.debug(f"campaign is created successfully with response: {response_create_campaign.status_code}")
            json_resp = json.loads(response_create_campaign.text)
            campaign_id = json_resp["campaignId"]
            logger.debug(f"campaign_id : {campaign_id}")
            query = "update campaign SET campaign_status = 'LIVE' where campaign_id = '" + str(campaign_id) + "';"
            DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"Updated campaign status into Live for campaign_id = {campaign_id}")
            response = rewards_processor.update_campaign('MER190211001', 'Ezetap@1234', campaign_id)
            logger.debug(f"Response received for updated campaign is : {response}")
            query = f"INSERT INTO `campaign_target_base` (`campaign_id`, `status`, `created_time`, `modified_time`, `created_by`, `modified_by`, `lock_id`, `org_code`, `control_type`) VALUES ('{campaign_id}', 'IN_PROGRESS', NOW(), NOW(), 'EZETAP', 'EZETAP', '1', '{org_code}', 'NORMAL');"
            result = DBProcessor.setValueToDB(query, 'rewards')
            logger.debug(f"result for updated insert query : {result}")
            coupon_code = datetime.now().strftime('%M%S')
            pin = int(datetime.now().strftime('%M%S')) + 1
            response_create_coupon = rewards_processor.create_coupon('MER190211001', 'Ezetap@1234', coupon_code, pin,
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
                tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                query = "update campaign_target_base set status='WON', claim_expiry = '" + str(
                    tomorrow_date) + "' where campaign_id='" + str(campaign_id) + "';"
                logger.debug(f"Query to fetch org_code from the DB : {query}")
                DBProcessor.setValueToDB(query, 'rewards')
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                logger.info(f"App homepage loaded successfully")
                rewards_page = Rewards(app_driver)
                rewards_page.click_on_side_menu()
                rewards_page.click_on_my_rewards_from_side_menu()
                rewards_page.wait_for_goals_tab_to_load()
                rewards_page.click_on_wins()
                rewards_page.click_on_reward_btn()
                rewards_page.click_on_proceed_btn_2()
                rewards_page.click_on_claim_now_btn()
                rewards_page.click_on_cancel_btn()
                query = f"select * from campaign where campaign_id= '{campaign_id}';"
                result = DBProcessor.getValueFromDB(query, 'rewards')
                title_wins = result["description"].values[0]
                logger.debug(f"fetched title of campaign : {title_wins}")
                query = f"select * from coupon where org_code = '{org_code}' Order By created_time DESC limit 1;"
                result = DBProcessor.getValueFromDB(query, 'rewards')
                coupon_code_db = result["coupon_code"].values[0]
                logger.debug(f"fetched coupon code from the rewards Db  : {coupon_code_db}")
                rewards_page.click_on_back_btn()
                title_rewards_tab = rewards_page.fetch_title_from_wins_tab()
                status = rewards_page.fetch_claimed_status()
                rewards_page.click_on_recent_claimed_rewards()
                coupon_code_rewards_tab = rewards_page.fetch_txt_coupon_code_from_rewards_tab()
                logger.debug(f"fetched coupon code from the rewards tab : {coupon_code_rewards_tab}")
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
                expected_app_values = {
                    "coupon_code": coupon_code_db,
                    "title": title_wins,
                    "status": "Claimed"
                }
                actual_app_values = {
                    "coupon_code": coupon_code_rewards_tab,
                    "title": title_rewards_tab,
                    "status": status
                }
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
