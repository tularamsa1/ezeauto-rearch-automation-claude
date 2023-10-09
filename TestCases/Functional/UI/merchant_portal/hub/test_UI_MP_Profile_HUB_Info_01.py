import sys
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.Portal_DashboardPage import PortalDashboardPage
from PageFactory.Portal_LoginPage import PortalLoginPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
@pytest.mark.apiVal
@pytest.mark.portalVal
def test_mp_700_707_063():
    """
    Sub Feature Code: UI_MP_Profile_Info_as_HUB_head
    Sub Feature Description: Verifying Profile information by logging in and log out when logging in as HUB Head
    TC naming code description:
    700: Merchant Portal
    707: HUB
    063: TC063
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE18')
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_cred}")
        txn_org_code = txn_cred['Merchant_Code']
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_org_code}")

        cred_dict = ResourceAssigner.get_org_users_using_category(txn_org_code)
        logger.debug(f"Fetched all category credentials from the ezeauto db : {cred_dict}")
        login_username = cred_dict['HUB']['username']
        logger.debug(f"Fetched login_username credentials from the ezeauto db : {login_username}")
        login_password = cred_dict['HUB']['password']

        logger.debug(f"Fetched login_password credentials from the ezeauto db : {login_password}")
        query = "select org_code from org_employee where username='" + str(login_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select * from org_employee where org_code = '" + org_code + "' and username =" \
                                                                                 " '" + login_username + "';"
            logger.debug(f"Query to fetch profile details from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            name_db = result['name'].values[0]
            logger.debug(f"name of user from db : {name_db}")
            username_db = result['username'].values[0]
            logger.debug(f'username from db : {username_db}')
            email_db = result['email'].values[0]
            logger.debug(f"email id from db : {email_db}")
            mobile_number_db = result['mobile_number'].values[0]
            logger.debug(f"mobile number from db : {mobile_number_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            api_details = DBProcessor.get_api_details('mp_profile')
            logger.info(f"bearer token from api : {response}")
            api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.get_request(api_details)
            logger.info(f"Response obtained for profile is: {response}")

            name_api = response['name']
            logger.debug(f"name from api : {name_api}")
            username_api = response['username']
            logger.debug(f"username from api : {username_api}")
            email_api = response['userEmail']
            logger.debug(f"email from api : {email_api}")
            mobile_number_api = response['userMobileNo']
            logger.debug(f"mobile number from api : {mobile_number_api}")

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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "name": name_db,
                    "username": username_db,
                    "phone_number": mobile_number_db
                }

                actual_api_values = {
                    "name": name_api,
                    "username": username_api,
                    "phone_number": mobile_number_api
                }
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
                    "name": name_api,
                    "username": username_api,
                    "phone_number": mobile_number_api
                }

                actual_db_values = {
                    "name": name_db,
                    "username": username_db,
                    "phone_number": mobile_number_db
                }
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {
                    "name": name_db,
                    "username": username_db,
                    "phone_number": mobile_number_db
                }

                GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
                login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
                login_page_portal.perform_login_to_portal(login_username, login_password)
                portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
                portal_dashboard_page.click_profile()
                profile_details = portal_dashboard_page.fetch_user_profile_details()
                user_profile_details = [details for details in profile_details.split() if details != ":"]
                logger.info(f"user profile details from portal : {user_profile_details}")
                portal_dashboard_page.perform_logout()
                portal_dashboard_page.validation_login_to_dashboard_page()

                actual_portal_values = {
                    "name": user_profile_details[0],
                    "username": user_profile_details[2],
                    "phone_number": user_profile_details[-1]
                }
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
