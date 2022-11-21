import sys
from random import randint, random

import pytest

from Configuration import Configuration, testsuite_teardown
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, card_processor, \
    ResourceAssigner, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_006():
    """
     Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithInvalidAppId
     Sub Feature Description: Login with invalid appID
     TC naming code description: pass the invalid appid and in response success will be true and subsciberid is generated
         400: Generic functions
         401: Autologin
         006: TC006
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

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

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

        # -----------------------------------------Start of Test Execution---------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            expected_appId = 'amzm'

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": expected_appId,
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {login_subscriber_id}")
            login_autologin_by_token_enabled = response['setting']['autoLoginByTokenEnabled']
            logger.debug(f"AutoLoginEnabled id is : {login_autologin_by_token_enabled}")
            login_success = response['success']
            logger.debug(f"success is : {login_success}")
            login_username = response['username']
            logger.debug(f"username is : {login_username}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")

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
                expected_api_values = {"success": True,
                                       "subscriber_id": expected_Sub_id,
                                       "autologin_by_token_enabled": True,
                                       "orgCode": org_code,
                                       "username": app_username
                                       }

                actual_api_values = {
                    "success": login_success,
                    "subscriber_id": login_subscriber_id,
                    "autologin_by_token_enabled": login_autologin_by_token_enabled,
                    "orgCode": login_org_code,
                    "username": login_username
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
def test_common_400_401_007():
    """
     Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithEmptyDeviceID
     Sub Feature Description: Login with empty device ID
     TC naming code description: pass the device id empty and response for success should be true and subscriber id is not generated
         400: Generic functions
         401: Autologin
         007: TC007
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

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")


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

        # -----------------------------------------Start of Test Execution---------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": '',
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            login_autologin_by_token_enabled = response['setting']['autoLoginByTokenEnabled']
            logger.debug(f"AutoLoginEnabled id is : {login_autologin_by_token_enabled}")
            login_success = response['success']
            logger.debug(f"success is : {login_success}")
            login_username = response['username']
            logger.debug(f"username is : {login_username}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")

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
                expected_api_values = {"success": True,
                                       "autologin_by_token_enabled": True,
                                       "orgCode": org_code,
                                       "username": app_username
                                       }

                actual_api_values = {
                    "success": login_success,
                    "autologin_by_token_enabled": login_autologin_by_token_enabled,
                    "orgCode": login_org_code,
                    "username": login_username
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
def test_common_400_401_008():
    """
       Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithInvalidDeviceID
       Sub Feature Description: Loginwith invalid device ID
       TC naming code description: pass the invalid device id and response for success should be true and subscriber id should generated
           400: Generic functions
           401: Autologin
           008: TC008
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

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")


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

        # -----------------------------------------Start of Test Execution---------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": "mxnz", #passing the invalid deviceid
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {login_subscriber_id}")
            login_autologin_by_token_enabled = response['setting']['autoLoginByTokenEnabled']
            logger.debug(f"AutoLoginEnabled id is : {login_autologin_by_token_enabled}")
            login_success = response['success']
            logger.debug(f"success is : {login_success}")
            login_username = response['username']
            logger.debug(f"username is : {login_username}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")

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
                expected_api_values = {"success": True,
                                       # "subscriber_id": expected_Sub_id,  #subscriber_id's both are getting failed
                                       # "autologin_by_token_enabled": True,
                                       # "orgCode": org_code,
                                       # "username": app_username
                                       }

                actual_api_values = {
                    "success": login_success,
                    # "subscriber_id": login_subscriber_id,
                    # "autologin_by_token_enabled": login_autologin_by_token_enabled,
                    # "orgCode": login_org_code,
                    # "username": login_username
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
def test_common_400_401_009():
    """
        Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithInvalidDeviceIDType
        Sub Feature Description: Login with invalid deviceID type
        TC naming code description: pass the invalid device id Type and response for success should be false and subscriber id is not generated
            400: Generic functions
            401: Autologin
            009: TC009
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


        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

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

        # -----------------------------------------Start of Test Execution---------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": "kslma" #passing the invalid deviceidentifierType
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            login_success = response['success']
            logger.debug(f"success is : {login_success}")
            login_errorCode = response['errorCode']
            logger.debug(f"errorCode is : {login_errorCode}")
            login_errorMessage = response['errorMessage']
            logger.debug(f"errorMessage is : {login_errorMessage}")
            login_message = response['message']
            logger.debug(f"message is : {login_message}")
            login_realCode = response['realCode']
            logger.debug(f"realCode is : {login_realCode}")


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

            expected_errorCode = "SESSION_EXPIRED"
            expected_errorMessage = "Your session has expired. Please login again."
            expected_message ="Your session has expired. Please login again."
            expected_realCode = "SESSION_EXPIRED"

            try:
                expected_api_values = {"success": False,
                                       # "errorCode" : expected_errorCode,
                                       # "errorMessage" : expected_errorMessage,
                                       # "message" : expected_message,
                                       # "realCode" : expected_realCode
                                       }

                actual_api_values = {
                    "success": login_success,
                    # "errorCode": login_errorCode,
                    # "errorMessage": login_errorMessage,
                    # "message": login_message,
                    # "realCode": login_realCode
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
def test_common_400_401_010():
    """
     Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithEmptyDeviceIDType
     Sub Feature Description: Login with empty deviceID type
     TC naming code description: pass the empty device id Type and response for success should be true and subscriber id is not generated
         400: Generic functions
         401: Autologin
         010: TC010
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


        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")


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


        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(org_code) + "' and device_identifier_type = 'imei' limit 1;"

        logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
        resultFromDB = DBProcessor.getValueFromDB(query,"ezetap_demo")
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

        # -----------------------------------------Start of Test Execution---------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": ""
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