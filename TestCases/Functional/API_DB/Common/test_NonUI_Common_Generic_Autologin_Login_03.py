import sys
from random import randint, random

import pytest


from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, card_processor, \
    ResourceAssigner, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_011():
    """
        Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithInvalidUsername
        Sub Feature Description: Login with invalid username
        TC naming code description: pass invalid username and response for success should be false and subscriber id is not generated
            400: Generic functions
            401: Autologin
            011: TC011
     """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + "' and device_identifier_type = 'imei' limit 1;"

        logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
        resultFromDB = DBProcessor.getValueFromDB(query, "ezetap_demo")
        print("resultFromDB is :", resultFromDB)

        if resultFromDB.empty:

            expected_deviceIdentifier = randint(0, 10 ** 15)
            print("expected_deviceIdentifier", expected_deviceIdentifier)

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            expected_Sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_Sub_id}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + "' and device_identifier_type = 'imei' limit 1;"

            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expected_deviceIdentifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_deviceIdentifier}")
            expected_Sub_id = result['subscriber_id'].values[0]
            logger.debug(f"Subscriber id is : {expected_Sub_id}")

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

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": expected_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
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
            # expected_errorCode = "EZETAP_0000041"
            expected_errorMessage = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_realCode = "AUTH_FAILED"

            try:
                expected_api_values = {"success": expected_success,
                                       "errorMessage": expected_errorMessage,
                                       "message": expected_message,
                                       "realCode": expected_realCode

                                       }

                actual_api_values = {
                    "success": login_success,
                    "errorMessage": login_errorMessage,
                    "message": login_message,
                    "realCode": login_realCode

                }

                # ---------------------------------------------------------------------------------------------
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
        TC naming code description: pass invalid username and response for success should be false and subscriber id is not generated
            400: Generic functions
            401: Autologin
            012: TC012
     """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + "' and device_identifier_type = 'imei' limit 1;"

        logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
        resultFromDB = DBProcessor.getValueFromDB(query, "ezetap_demo")
        print("resultFromDB is :", resultFromDB)

        if resultFromDB.empty:

            expected_deviceIdentifier = randint(0, 10 ** 15)
            print("expected_deviceIdentifier", expected_deviceIdentifier)

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            expected_Sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_Sub_id}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + "' and device_identifier_type = 'imei' limit 1;"

            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expected_deviceIdentifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_deviceIdentifier}")
            expected_Sub_id = result['subscriber_id'].values[0]
            logger.debug(f"Subscriber id is : {expected_Sub_id}")

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

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": expected_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
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
            # expected_errorCode = "EZETAP_0000041"
            expected_errorMessage = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_realCode = "AUTH_FAILED"

            try:
                expected_api_values = {"success": expected_success,
                                       "errorMessage": expected_errorMessage,
                                       "message": expected_message,
                                       "realCode": expected_realCode
                                       }

                actual_api_values = {
                    "success": login_success,
                    "errorMessage": login_errorMessage,
                    "message": login_message,
                    "realCode": login_realCode

                }

                # ---------------------------------------------------------------------------------------------
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
def test_common_400_401_014():
    """
        Sub Feature Code: NonUI_Common_Generic_Autologin_Login_And_AutoLogin
        Sub Feature Description: Login and do autologin with subID and delete entry from DB
        TC naming code description: hit the login api and subscriber_id and token is generated,
        use the same subscriberid for autologin and again the tokenid is generate, compared both the tokens.
        Once after that delete the subscriberid from db and again hit the autologin here success should be false
            400: Generic functions
            401: Autologin
            014: TC014
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + "' and device_identifier_type = 'imei' limit 1;"

        logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
        resultFromDB = DBProcessor.getValueFromDB(query, "ezetap_demo")
        print("resultFromDB is :", resultFromDB)

        if resultFromDB.empty:

            expected_deviceIdentifier = randint(0, 10 ** 15)
            print("expected_deviceIdentifier", expected_deviceIdentifier)

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            expected_Sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_Sub_id}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + "' and device_identifier_type = 'imei' limit 1;"

            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expected_deviceIdentifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_deviceIdentifier}")
            expected_Sub_id = result['subscriber_id'].values[0]
            logger.debug(f"Subscriber id is : {expected_Sub_id}")

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
            logger.debug(f"errorMessage is : {expected_errorMessage}")
            expected_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            logger.debug(f"message is : {expected_message}")
            expected_realCode = "AUTH_FAILED"
            logger.debug(f"realCode is : {expected_realCode}")
            expected_success = False
            logger.debug(f"success is : {expected_success}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Login API Response is :", response)
            login_success = response['success']
            logger.debug(f"success id is : {login_success}")
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {login_subscriber_id}")
            print("login_subscriber_id is:",login_subscriber_id)
            login_token = response['token']
            logger.debug(f"token is : {login_token}")

            api_details = DBProcessor.get_api_details('autoLogin',
                                                      request_body={"username": app_username,
                                                                    "subscriberId": login_subscriber_id ,
                                                                    "deviceIdentifier": expected_deviceIdentifier ,
                                                                    "appId":"ezetap_android",
                                                                    "deviceIdentifierType":"imei"
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            print("Autologin response is :", response)
            autologin_success = response['success']
            logger.debug(f"success id is : {autologin_success}")
            print("autologin_success is", autologin_success)
            autologin_token = response['token']
            logger.debug(f"token id is : {autologin_token}")
            print("autologin_token is", autologin_token)


            query = "select * from auto_login_token where subscriber_id='" + str(login_subscriber_id) + "';"
            result = DBProcessor.getValueFromDB(query,"ezetap_demo")
            print("result of ",result)
            expected_token = result['token'].values[0]
            print("expected_token",expected_token)
            logger.debug(f"token id is : {expected_token}")

            if login_token == autologin_token:

                query = "delete from auto_login_token where subscriber_id ='"+str(login_subscriber_id)+"';"
                logger.debug(f"Query to delete data from the table : {query}")
                result = DBProcessor.setValueToDB(query)
                logger.debug(f"Fetching result from the delete query : {result}")
                print("Deleted db result is :", result)

                api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                      "password": portal_username})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for setting precondition DB refresh is : {response}")

                api_details = DBProcessor.get_api_details('autoLogin',
                                                          request_body={"username": app_username,
                                                                        "subscriberId": login_subscriber_id,
                                                                        "deviceIdentifier": expected_deviceIdentifier,
                                                                        "appId": "ezetap_android",
                                                                        "deviceIdentifierType": "imei"
                                                                        }
                                                          )

                result = APIProcessor.send_request(api_details)
                print("result of autologin: ", result)
                autlogin_actualValues_errorMessage = result['errorMessage']
                logger.debug(f"Autologin actual value of errorMessage is : {autlogin_actualValues_errorMessage}")
                autlogin_actualValues_message = result['message']
                logger.debug(f"Autologin actual value of message is : {autlogin_actualValues_message}")
                autlogin_actualValues_realCode = result['realCode']
                logger.debug(f"Autologin actual value of realCode is : {autlogin_actualValues_realCode}")
                autologin_actualValues_success = result['success']
                logger.debug(f"Autologin actual value of success is :{autologin_actualValues_success}")

            else:
                print("login_token and autologin_token both are not equal")


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
                expected_api_values = { "success" : expected_success,
                                        "realCode" : expected_realCode,
                                        "message" : expected_message,
                                        "errorMessage" : expected_errorMessage,
                                        "token" : expected_token,
                                       }

                actual_api_values = { "success" : autologin_actualValues_success,
                                      "realCode" : autlogin_actualValues_realCode,
                                      "message" : autlogin_actualValues_message,
                                      "errorMessage" : autlogin_actualValues_errorMessage,
                                      "token" : login_token,
                                    }

                # ---------------------------------------------------------------------------------------------
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

