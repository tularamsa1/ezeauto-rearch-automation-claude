import sys
from random import randint, random
import pytest
from Configuration import testsuite_teardown
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor,ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_001():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_SuccessLogin
    Sub Feature Description: Login successfully with autologin enabled
    TC naming code description: autologin should be enabled and in response subscriberid is generated and success will be true, 400: Generic functions,401: Autologin,001: TC001
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(org_code) + "' and device_identifier_type = 'imei';"
        logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
        result_from_db = DBProcessor.getValueFromDB(query,"ezetap_demo")
        logger.debug(f"Query resultFromDB of org_subscription table : {result_from_db}")

        if result_from_db.empty:
            expected_device_identifier = random.randint(10000,99999)
            logger.debug(f"expected_deviceIdentifier is : {expected_device_identifier}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier ,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login Response is : {response}")
            expected_sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_sub_id}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(org_code) + "' and device_identifier_type = 'imei';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "ezetap_demo")
            logger.debug(f"Query result of org_subscription table : {result}")
            expected_device_identifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_device_identifier}")
            expected_sub_id = result['subscriber_id'].values[0]
            logger.debug(f"Subscriber id is : {expected_sub_id}")

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

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier ,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in the execution is: {response}")
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Expected Subscriber id is: {login_subscriber_id}")
            login_autologin_by_token_enabled = response['setting']['autoLoginByTokenEnabled']
            logger.debug(f"AutoLoginEnabled id is : {login_autologin_by_token_enabled }")
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
                expected_api_values = {
                    "success": True,
                    "autologin_by_token_enabled": True,
                    "orgCode" :org_code,
                    "username" : app_username
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": login_success,
                    "autologin_by_token_enabled": login_autologin_by_token_enabled,
                    "orgCode":login_org_code,
                    "username": login_username
               }

                logger.debug(f"actual_api_values: {actual_api_values}")
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
def test_common_400_401_002():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithoutDeviceIDType
    Sub Feature Description: Login without DeviceIDType with autologin enabled
    TC naming code description: don't pass deviceidtype in response the success will be true but the subscriber_id is not generated,400: Generic functions,401: Autologin,002: TC002
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(org_code) + "' and device_identifier_type = 'imei' limit 1;"
        logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
        result_from_db = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query resultFromDB of org_subscription table : {result_from_db}")

        if result_from_db.empty:
            expected_device_identifier = randint(0, 10 ** 15)
            logger.debug(f"expected_deviceIdentifier is : {expected_device_identifier}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login Response is : {response}")
            expected_sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_sub_id}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(org_code) + "' and device_identifier_type = 'imei' limit 1;"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "ezetap_demo")
            logger.debug(f"Query result of org_subscription table : {result}")
            expected_device_identifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_device_identifier}")
            expected_sub_id = result['subscriber_id'].values[0]
            logger.debug(f"Subscriber id is : {expected_sub_id}")

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

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "appId": "ezetap_android",
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in the execution is: {response}")
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
                expected_api_values = {
                    "success": True,
                    "autologin_by_token_enabled": True,
                    "orgCode": org_code,
                    "username": app_username
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": login_success,
                    "autologin_by_token_enabled": login_autologin_by_token_enabled,
                    "orgCode": login_org_code,
                    "username": login_username
                }

                logger.debug(f"actual_api_values: {actual_api_values}")
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
def test_common_400_401_003():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithoutDeviceID
    Sub Feature Description: Login without DeviceID with autologin enabled
    TC naming code description: don't pass the deviceid in response the success will be true and subscriberid is not generated,400: Generic functions,401: Autologin,003: TC003
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(org_code) + "' and device_identifier_type = 'imei';"
        logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
        result_from_db = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query resultFromDB of org_subscription table : {result_from_db}")

        if result_from_db.empty:
            expected_device_identifier = randint(0, 10 ** 15)
            logger.debug(f"expected_device_identifier is : {expected_device_identifier}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login Response is : {response}")
            expected_sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_sub_id}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + "' and device_identifier_type = 'imei';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "ezetap_demo")
            logger.debug(f"Query result of org_subscription table : {result}")
            expected_device_identifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_device_identifier}")
            expected_sub_id = result['subscriber_id'].values[0]
            logger.debug(f"Subscriber id is : {expected_sub_id}")

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

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in the execution is: {response}")
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
                expected_api_values = {
                    "success": True,
                    "autologin_by_token_enabled": True,
                    "orgCode": org_code,
                    "username": app_username
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": login_success,
                    "autologin_by_token_enabled": login_autologin_by_token_enabled,
                    "orgCode": login_org_code,
                    "username": login_username
                }

                logger.debug(f"actual_api_values: {actual_api_values}")
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
def test_common_400_401_004():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithoutAppID
    Sub Feature Description: Login without appID
    TC naming code description: don't pass the appid in response the success will be true and subscriber_id is not generated,400: Generic functions,401: Autologin,004: TC004
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)-------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + "' and device_identifier_type = 'imei' limit 1;"
        logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
        result_from_db = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query resultFromDB of org_subscription table : {result_from_db}")

        if result_from_db.empty:
            expected_device_identifier = randint(0, 10 ** 15)
            logger.debug(f"expected_deviceIdentifier is : {expected_device_identifier}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login Response is : {response}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(org_code) + "' and device_identifier_type = 'imei' limit 1;"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of org_subscription table : {result}")
            expected_device_identifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_device_identifier}")
            expected_sub_id = result['subscriber_id'].values[0]
            logger.debug(f"Subscriber id is : {expected_sub_id}")

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

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in the execution is: {response}")
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
                expected_api_values = {
                    "success": True,
                    "autologin_by_token_enabled": True,
                    "orgCode": org_code,
                    "username": app_username
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": login_success,
                    "autologin_by_token_enabled": login_autologin_by_token_enabled,
                    "orgCode": login_org_code,
                    "username": login_username
                }

                logger.debug(f"actual_api_values: {actual_api_values}")
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
def test_common_400_401_005():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_LoginWithEmptyAppID
    Sub Feature Description: Login with empty app ID
    TC naming code description: pass empty appid in response the success will be true and subscriber_id is not generated,400: Generic functions,401: Autologin,005: TC005
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + "' and device_identifier_type = 'imei';"
        logger.debug(f"Query to fetch deviceIdentifier and subscriberid from the DB : {query}")
        result_from_db = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query resultFromDB of org_subscription table : {result_from_db}")

        if result_from_db.empty:
            expected_device_identifier = randint(0, 10 ** 15)
            logger.debug(f"expected_deviceIdentifier is : {expected_device_identifier}")

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "appId": "",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login Response is : {response}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + "' and device_identifier_type = 'imei' limit 1;"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of org_subscription table : {result}")
            expected_device_identifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_device_identifier}")
            expected_sub_id = result['subscriber_id'].values[0]
            logger.debug(f"Subscriber id is : {expected_sub_id}")

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

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "appId": "",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in the execution is: {response}")
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
                expected_api_values = {
                    "success": True,
                    "autologin_by_token_enabled": True,
                    "orgCode": org_code,
                    "username": app_username
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": login_success,
                    "autologin_by_token_enabled": login_autologin_by_token_enabled,
                    "orgCode": login_org_code,
                    "username": login_username
                }

                logger.debug(f"actual_api_values: {actual_api_values}")
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