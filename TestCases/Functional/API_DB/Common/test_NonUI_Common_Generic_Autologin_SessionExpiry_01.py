import secrets
import string
import sys
import random
from time import sleep
import pytest
from Configuration import testsuite_teardown
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator,ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_400_401_015():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_Successtxn_AfterSessionExpiry
    Sub Feature Description: Login and do success txn after session expiry
    TC naming code description: 400: Generic functions,401: Autologin,015: TC015
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

        query = "delete from org_subscription where org_code='"+org_code+"';"
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

            expected_device_identifier = random.randint(0, 10 ** 15)
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
            logger.debug(f"Login Response is : {response}")
            login_success = response['success']
            login_autologin_by_token_enabled = response['setting']['autoLoginByTokenEnabled']
            logger.debug(f"AutoLoginEnabled id is : {login_autologin_by_token_enabled}")
            login_username = response['username']
            logger.debug(f"username is : {login_username}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {login_subscriber_id}")

            if login_success == True:

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                                      for i in range(20))

                api_details = DBProcessor.get_api_details('cash_payment',request_body={
                        "username": app_username,
                        "amount": "109",
                        "nonce": random.randint(10000, 99999),
                        "externalRefNumber": ext_ref_num,
                        "deviceIdentifier": expected_device_identifier,
                        "appId": "ezetap_android",
                        "deviceIdentifierType": "imei",
                        "subscriberId": login_subscriber_id
                    }
                )

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Cash txn response is : {response}")
                cash_txn_success = response['success']

                if cash_txn_success == True:
                    logger.error(f"Cash txn is Success")

                else:
                    logger.info(f"Cash txn failed")
            else:
                logger.error(f"Login Failed, expected to be success")

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
                    "success": cash_txn_success,
                    "autologin_by_token_enabled": login_autologin_by_token_enabled,
                    "orgCode": login_org_code,
                    "username": login_username
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

                query = "select * from org_subscription where org_code='" + str(org_code) + "' and device_identifier_type = 'imei';"
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

                logger.debug(f"actual_db_values: {actual_db_values}")

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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_400_401_016():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_Successtxn_WithExpiredToken
    Sub Feature Description: Login and do success txn using expired token
    TC naming code description:400: Generic functions,401: Autologin,016: TC016
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

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

            expected_device_identifier = random.randint(0, 10 ** 15)
            expected_device_identifier_type = "imei"
            expected_app_id = "ezetap_android"

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "appId":expected_app_id,
                "deviceIdentifierType": expected_device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in execution is : {response}")
            login_success = response['success']
            login_autologin_by_token_enabled = response['setting']['autoLoginByTokenEnabled']
            logger.debug(f"AutoLoginEnabled id is : {login_autologin_by_token_enabled}")
            login_username = response['username']
            logger.debug(f"username is : {login_username}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {login_subscriber_id}")

            if login_success == True:

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                query = "update auto_login_token set expired=1 where subscriber_id ='" + str(login_subscriber_id) + "';"
                logger.debug(f"Query to fetch org_code from the DB : {query}")
                result = DBProcessor.setValueToDB(query)
                logger.debug(f"result of auto_login_token: {result}")
                logger.debug(f"Update the auto_login_token set expired =1 : {query}")

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                                      for i in range(20))

                api_details = DBProcessor.get_api_details('cash_payment',request_body={
                        "username": app_username,
                        "amount": "109",
                        "nonce": random.randint(10000, 99999),
                        "externalRefNumber": ext_ref_num,
                        "deviceIdentifier": expected_device_identifier,
                        "appId": "ezetap_android",
                        "deviceIdentifierType": "imei",
                        "subscriberId": login_subscriber_id
                    }
                )

                response = APIProcessor.send_request(api_details)
                logger.debug(f"cash_payment response",response)
                cash_txn_success = response['success']

                if cash_txn_success == True:
                    logger.error(f"Cash txn is Success")

                else:
                    logger.error(f"Cash txn failed")
            else:
                logger.error(f"Login Failed, expected to be success")

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
                expected_api_values =  {
                    "success": True,
                    "autologin_by_token_enabled": True,
                    "orgCode": org_code,
                    "username": app_username
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": cash_txn_success,
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

                logger.debug(f"actual_db_values: {actual_db_values}")

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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_400_401_017():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_SessionExpiry_InvalidAppID
    Sub Feature Description: Do txn using invalid appID after session expiry
    TC naming code description:400: Generic functions,401: Autologin,017: TC017
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

        query = "delete from org_subscription where org_code='"+org_code+"';"
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

            expected_device_identifier = random.randint(0, 10 ** 15)
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
            login_success = response['success']
            logger.debug(f"success id is : {login_success}")
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {login_subscriber_id}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")

            if login_success == True:

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                                      for i in range(20))
                expected_appID = 'abc'

                api_details = DBProcessor.get_api_details('cash_payment',request_body={
                        "username": app_username,
                        "amount": "109",
                        "nonce": random.randint(10000, 99999),
                        "externalRefNumber": ext_ref_num,
                        "deviceIdentifier": expected_device_identifier,
                        "appId": expected_appID,
                        "deviceIdentifierType": "imei",
                        "subscriberId": login_subscriber_id
                })

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Cash txn Response is: {response}")
                actual_cash_txn_success = response['success']
                logger.debug(f"success id is : {actual_cash_txn_success}")
                actual_cash_txn_error_code = response['errorCode']
                logger.debug(f"errorCode id is : {actual_cash_txn_error_code}")
                actual_cash_txn_error_message = response['errorMessage']
                logger.debug(f"errorMessage id is : {actual_cash_txn_error_message}")
                actual_cash_txn_real_code = response['realCode']
                logger.debug(f"realCode id is : {actual_cash_txn_real_code}")
                actual_cash_txn_message = response['message']
                logger.debug(f"message id is : {actual_cash_txn_message}")

                if actual_cash_txn_success == True:
                    logger.info(f"Cash txn is Success")

                else:
                    logger.error(f"Cash txn failed")
            else:
                logger.error(f"Login Failed, expected to be success")

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

            expected_cash_txn_error_code = "EZETAP_0000073"
            expected_cash_txn_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_cash_txn_real_code = "AUTH_FAILED"
            expected_cash_txn_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."

            try:
                expected_api_values = {
                    "success": False,
                    "errorCode":expected_cash_txn_error_code,
                    "errorMessage":expected_cash_txn_error_message,
                    "realCode":expected_cash_txn_real_code,
                    "message":expected_cash_txn_message
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": actual_cash_txn_success,
                    "errorCode": actual_cash_txn_error_code,
                    "errorMessage": actual_cash_txn_error_message,
                    "realCode": actual_cash_txn_real_code,
                    "message": actual_cash_txn_message
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

                query = "select * from org_subscription where org_code='" + str(org_code) + "' and device_identifier_type = 'imei';"
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

                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-----------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_400_401_018():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_SessionExpiry_InvalidDeviceID
    Sub Feature Description: Do txn using invalid device ID after session expiry
    TC naming code description: 400: Generic functions,401: Autologin,018: TC018
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

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

            expected_device_identifier = random.randint(0, 10 ** 15)
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
            logger.debug(f"Login response in execution is : {response}")
            login_success = response['success']
            logger.debug(f"success id is : {login_success}")
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {login_subscriber_id}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")

            if login_success == True:

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                                      for i in range(20))

                expected_device_identifier_cash_payment = 'abc'

                api_details = DBProcessor.get_api_details('cash_payment',request_body={
                    "username": app_username,
                    "amount": "109",
                    "nonce": random.randint(10000, 99999),
                    "externalRefNumber": ext_ref_num,
                    "deviceIdentifier": expected_device_identifier_cash_payment,
                    "appId": "ezetap_android",
                    "deviceIdentifierType": "imei",
                    "subscriberId": login_subscriber_id
                })

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Cash txn Response is: {response}")
                actual_cash_txn_success = response['success']
                logger.debug(f"success id is : {actual_cash_txn_success}")
                actual_cash_txn_error_code = response['errorCode']
                logger.debug(f"errorCode id is : {actual_cash_txn_error_code}")
                actual_cash_txn_error_message = response['errorMessage']
                logger.debug(f"errorMessage id is : {actual_cash_txn_error_message}")
                actual_cash_txn_real_code = response['realCode']
                logger.debug(f"realCode id is : {actual_cash_txn_real_code}")
                actual_cash_txn_message = response['message']
                logger.debug(f"message id is : {actual_cash_txn_message}")

                if actual_cash_txn_success == True:
                    logger.info(f"Cash txn is Success")

                else:
                    logger.error(f"Cash txn failed")
            else:
                logger.error(f"Login Failed, expected to be success")

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

            expected_cash_txn_error_code = "EZETAP_0000073"
            expected_cash_txn_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_cash_txn_real_code = "AUTH_FAILED"
            expected_cash_txn_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."

            try:
                expected_api_values = {
                    "success": False,
                    "errorCode":expected_cash_txn_error_code,
                    "errorMessage":expected_cash_txn_error_message,
                    "realCode":expected_cash_txn_real_code,
                    "message":expected_cash_txn_message
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": actual_cash_txn_success,
                    "errorCode": actual_cash_txn_error_code,
                    "errorMessage": actual_cash_txn_error_message,
                    "realCode": actual_cash_txn_real_code,
                    "message": actual_cash_txn_message
                }

                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
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

                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation----------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_400_401_019():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_SessionExpiry_InvalidDeviceID
    Sub Feature Description:Do txn using invalid deviceID type after session expiry
    TC naming code description: 400: Generic functions, 401: Autologin,019: TC019
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)-------------------------------
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

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

            expected_app_id = 'ezetap_android'
            expected_device_identifier = random.randint(0, 10 ** 15)
            expected_device_identifier_type = "imei"

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_device_identifier,
                "appId":  expected_app_id,
                "deviceIdentifierType": expected_device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Login response in execution is : {response}")
            login_success = response['success']
            logger.debug(f"success id is : {login_success}")
            login_subscriber_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {login_subscriber_id}")
            login_autologin_by_token_enabled = response['setting']['autoLoginByTokenEnabled']
            logger.debug(f"AutoLoginEnabled id is : {login_autologin_by_token_enabled}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")
            login_username = response['username']
            logger.debug(f"username is : {login_username}")

            if login_success == True:

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                                      for i in range(20))

                expected_device_identifier_cash_payment = 'zmx'
                expected_app_id = "ezetap_android"
                expected_device_identifier_type = "imei"

                api_details = DBProcessor.get_api_details('cash_payment',request_body={
                        "username": app_username,
                        "amount": "109",
                        "nonce": random.randint(10000, 99999),
                        "externalRefNumber": ext_ref_num,
                        "deviceIdentifier": expected_device_identifier_cash_payment,
                        "appId": expected_app_id,
                        "deviceIdentifierType": expected_device_identifier_type,
                        "subscriberId": login_subscriber_id
                })

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Cash txn Response is : {response}")
                actual_cash_txn_success = response['success']
                logger.debug(f"success id is : {actual_cash_txn_success}")
                actual_cash_txn_error_code = response['errorCode']
                logger.debug(f"errorCode id is : {actual_cash_txn_error_code}")
                actual_cash_txn_error_message = response['errorMessage']
                logger.debug(f"errorMessage id is : {actual_cash_txn_error_message}")
                actual_cash_txn_real_code = response['realCode']
                logger.debug(f"realCode id is : {actual_cash_txn_real_code}")
                actual_cash_txn_message = response['message']
                logger.debug(f"message id is : {actual_cash_txn_message}")

                if actual_cash_txn_success == True:
                    logger.info(f"Cash txn is Success")

                else:
                    logger.error(f"Cash txn failed")
            else:
                logger.error(f"Login Failed, expected to be success")

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

            expected_cash_txn_error_code = "EZETAP_0000073"
            expected_cash_txn_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_cash_txn_real_code = "AUTH_FAILED"
            expected_cash_txn_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."

            try:
                expected_api_values = {
                    "success": False,
                    "errorCode": expected_cash_txn_error_code,
                    "errorMessage": expected_cash_txn_error_message,
                    "realCode": expected_cash_txn_real_code,
                    "message": expected_cash_txn_message
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": actual_cash_txn_success,
                    "errorCode": actual_cash_txn_error_code,
                    "errorMessage": actual_cash_txn_error_message,
                    "realCode": actual_cash_txn_real_code,
                    "message": actual_cash_txn_message
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

                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation----------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)