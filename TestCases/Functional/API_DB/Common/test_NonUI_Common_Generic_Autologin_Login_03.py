import sys
from random import randint
import pytest
from Configuration import testsuite_teardown
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_011():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithInvalidUsername
    Sub Feature Description: Login with invalid username
    TC naming code description: pass invalid username and response for success should be false and subscriber id is not generated,400: Generic functions,401: Autologin,011: TC011
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
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "delete from org_subscription where org_code='" + org_code + "';"
        logger.debug(f"Delete org_subscription based on org_code  : {query}")
        result = DBProcessor.setValueToDB(query, "ezetap_demo")
        logger.debug(f"Query result of Delete org_subscription based on org_code : {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution---------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            expected_username = randint(0, 10 ** 8)
            logger.debug(f"expected_username is : {expected_username}")
            expected_device_identifier = randint(0, 10 ** 15)
            expected_device_identifier_type = "imei"
            expected_app_id = "ezetap_android"

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": expected_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "appId": expected_app_id,
                "deviceIdentifierType": expected_device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in the execution is: {response}")
            login_success = response['success']
            logger.debug(f"success is : {login_success}")
            login_errorMessage = response['errorMessage']
            logger.debug(f"errorMessage id is : {login_errorMessage}")
            login_message = response['message']
            logger.debug(f"message id is : {login_message}")
            login_realCode = response['realCode']
            logger.debug(f"realCode id is : {login_realCode}")

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

            expected_success = False
            expected_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_errorMessage = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_realCode = "AUTH_FAILED"

            try:
                expected_api_values = {
                    "success": expected_success,
                    "errorMessage": expected_errorMessage,
                    "message": expected_message,
                    "realCode": expected_realCode
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": login_success,
                    "errorMessage": login_errorMessage,
                    "message": login_message,
                    "realCode": login_realCode
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_012():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithInvalidPassword
    Sub Feature Description: Login with invalid password
    TC naming code description: pass invalid username and response for success should be false and subscriber id is not generated,400: Generic functions,401: Autologin,012: TC012
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
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "delete from org_subscription where org_code='" + org_code + "';"
        logger.debug(f"Delete org_subscription based on org_code  : {query}")
        result = DBProcessor.setValueToDB(query, "ezetap_demo")
        logger.debug(f"Query result of Delete org_subscription based on org_code : {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution---------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            expected_password = randint(0, 10 ** 5)
            logger.debug(f"expected_password is : {expected_password}")
            expected_device_identifier = randint(0, 10 ** 15)
            expected_device_identifier_type = "imei"
            expected_app_id = "ezetap_android"

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": expected_password,
                "deviceIdentifier": expected_device_identifier,
                "appId": expected_app_id,
                "deviceIdentifierType": expected_device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in the execution is: {response}")
            login_success = response['success']
            logger.debug(f"success is : {login_success}")
            login_errorMessage = response['errorMessage']
            logger.debug(f"errorMessage id is : {login_errorMessage}")
            login_message = response['message']
            logger.debug(f"message id is : {login_message}")
            login_realCode = response['realCode']
            logger.debug(f"realCode id is : {login_realCode}")
            login_success = response['success']
            logger.debug(f"success id is : {login_success}")

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

            expected_success = False
            expected_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_errorMessage = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_realCode = "AUTH_FAILED"

            try:
                expected_api_values = {
                    "success": expected_success,
                    "errorMessage": expected_errorMessage,
                    "message": expected_message,
                    "realCode": expected_realCode
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": login_success,
                    "errorMessage": login_errorMessage,
                    "message": login_message,
                    "realCode": login_realCode
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_400_401_014():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_Login_And_AutoLogin
    Sub Feature Description: Login and do autologin with subID and delete entry from DB
    TC naming code description: hit the login api and subscriber_id and token is generated,use the same subscriberid for autologin and again the tokenid is generate, compared both the tokens.Once after that delete the subscriberid from db and again hit the autologin here success should be false,400: Generic functions,401: Autologin,014: TC014
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
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "delete from org_subscription where org_code='" + org_code + "';"
        logger.debug(f"Delete org_subscription based on org_code  : {query}")
        result = DBProcessor.setValueToDB(query, "ezetap_demo")
        logger.debug(f"Query result of Delete org_subscription based on org_code : {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution---------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            expected_errorMessage = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_realCode = "AUTH_FAILED"
            expected_success = False
            expected_device_identifier = randint(0, 10 ** 15)
            expected_device_identifier_type = "imei"
            expected_app_id = "ezetap_android"

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "appId": expected_app_id,
                "deviceIdentifierType": expected_device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in the execution is: {response}")
            login_success = response['success']
            logger.debug(f"success id is : {login_success}")
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {login_subscriber_id}")
            login_token = response['token']
            logger.debug(f"token is : {login_token}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")

            api_details = DBProcessor.get_api_details('autoLogin',request_body={
                "username": app_username,
                "subscriberId": login_subscriber_id ,
                "deviceIdentifier": expected_device_identifier ,
                "appId":"ezetap_android",
                "deviceIdentifierType":"imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Autologin response is :: {response}")
            autologin_success = response['success']
            logger.debug(f"autologin_success is : {autologin_success}")
            autologin_token = response['token']
            logger.debug(f"token id is : {autologin_token}")

            query = "select * from auto_login_token where subscriber_id='" + str(login_subscriber_id) + "';"
            logger.debug(f"Query of auto_login_token table is : {query}")
            result = DBProcessor.getValueFromDB(query,"ezetap_demo")
            logger.debug(f"Query Result of auto_login_token table is : {result}")
            expected_token = result['token'].values[0]
            logger.debug(f"token id is : {expected_token}")

            if login_token == autologin_token:

                query = "delete from auto_login_token where subscriber_id ='"+str(login_subscriber_id)+"';"
                logger.debug(f"Query to delete data from the table : {query}")
                result = DBProcessor.setValueToDB(query)
                logger.debug(f"Fetching result from the delete query : {result}")

                api_details = DBProcessor.get_api_details('DB Refresh', request_body={
                    "username": portal_username,
                    "password": portal_username
                })

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for setting precondition DB refresh is : {response}")

                api_details = DBProcessor.get_api_details('autoLogin',request_body={
                    "username": app_username,
                    "subscriberId": login_subscriber_id,
                    "deviceIdentifier": expected_device_identifier,
                    "appId": "ezetap_android",
                    "deviceIdentifierType": "imei"
                })

                result = APIProcessor.send_request(api_details)
                logger.debug(f"result of autologin is : {result}")
                autlogin_actualValues_errorMessage = result['errorMessage']
                logger.debug(f"Autologin actual value of errorMessage is : {autlogin_actualValues_errorMessage}")
                autlogin_actualValues_message = result['message']
                logger.debug(f"Autologin actual value of message is : {autlogin_actualValues_message}")
                autlogin_actualValues_realCode = result['realCode']
                logger.debug(f"Autologin actual value of realCode is : {autlogin_actualValues_realCode}")
                autologin_actualValues_success = result['success']
                logger.debug(f"Autologin actual value of success is :{autologin_actualValues_success}")

            else:
                logger.error(f"login_token and autologin_token both are not equal")

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
                    "success" : expected_success,
                    "realCode" : expected_realCode,
                    "message" : expected_message,
                    "errorMessage" : expected_errorMessage,
                    "token" : expected_token,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success" : autologin_actualValues_success,
                    "realCode" : autlogin_actualValues_realCode,
                    "message" : autlogin_actualValues_message,
                    "errorMessage" : autlogin_actualValues_errorMessage,
                    "token" : login_token,
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

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
                    "subscriber_id": login_subscriber_id,
                    "expected_device_identifier": str(expected_device_identifier),
                    "org_code": login_org_code,
                    "device_identifier_type": str(expected_device_identifier_type),
                    "app_id": str(expected_app_id)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from org_subscription where org_code='" + str(
                    org_code) + "' and device_identifier_type = 'imei';"
                logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
                result_from_db = DBProcessor.getValueFromDB(query, "ezetap_demo")
                logger.debug(f"Query resultFromDB of org_subscription table : {result_from_db}")
                device_identifier_db = result_from_db['device_identifier'].values[0]
                logger.debug(f"Query result, device_identifier from db is : {device_identifier_db}")
                subscriber_id_db = result_from_db['subscriber_id'].values[0]
                logger.debug(f"Subscriber id from db is : {subscriber_id_db}")
                device_identifier_type_db = result_from_db['device_identifier_type'].values[0]
                logger.debug(f"Query result, device_identifier_type from db is : {device_identifier_type_db}")
                app_id_db = result_from_db['app_id'].values[0]
                logger.debug(f"Query result, app_id from db is : {app_id_db}")
                org_code_db = result_from_db['org_code'].values[0]
                logger.debug(f"Query result, org_code from db is : {org_code_db}")

                actual_db_values = {
                    "subscriber_id": subscriber_id_db,
                    "expected_device_identifier": device_identifier_db,
                    "org_code": org_code_db,
                    "device_identifier_type": device_identifier_type_db,
                    "app_id": app_id_db
                }

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)

