import secrets
import string
import sys
import random

from time import sleep

import pytest

from Configuration import Configuration,testsuite_teardown
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, card_processor, \
    ResourceAssigner, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_015():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_Successtxn_AfterSessionExpiry
    Sub Feature Description: Login and do success txn after session expiry
    TC naming code description:
        400: Generic functions
        401: Autologin
        015: TC015
     """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(completed)-------------------------------------------

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

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + " and deviceIdentifierType = imei limit 1';"

        logger.debug(f"Query to fetch org_code from the DB : {query}")
        resultFromDB = DBProcessor.getValueFromDB(query)

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code
                                                                                       }
                                                  )

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code
                                                                                       }
                                                  )

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

        if resultFromDB.empty:

            expected_deviceIdentifier = random.randint(0, 10 ** 15)
            print("expected_deviceIdentifier", expected_deviceIdentifier)

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Login Response is :", response)
            expected_Sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_Sub_id}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + " and deviceIdentifierType = imei limit 1';"

            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expected_deviceIdentifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_deviceIdentifier}")
            expected_Sub_id = result['subscriberId'].values[0]
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
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            login_success = response['success']
            login_autologin_by_token_enabled = response['setting']['autoLoginByTokenEnabled']
            logger.debug(f"AutoLoginEnabled id is : {login_autologin_by_token_enabled}")
            login_username = response['username']
            logger.debug(f"username is : {login_username}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")


            if login_success == True:

                login_subscriber_id = response['subscriberId']
                logger.debug(f"Subscriber id is : {login_subscriber_id}")
                print("subscriber id is :", login_subscriber_id)

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                                      for i in range(20))

                api_details = DBProcessor.get_api_details('cash_payment',request_body={
                        "username": app_username,
                        "amount": "109",
                        "nonce": random.randint(10000, 99999),
                        "externalRefNumber": ext_ref_num,
                        "deviceIdentifier": expected_deviceIdentifier,
                        "appId": "ezetap_android",
                        "deviceIdentifierType": "imei",
                        "subscriberId": expected_Sub_id
                    }
                )

                response = APIProcessor.send_request(api_details)
                print("Cash txn response is :", response)
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
                expected_api_values =  {"success": True,
                                         "subscriber_id": expected_Sub_id,
                                         "autologin_by_token_enabled": True,
                                         "orgCode": org_code,
                                         "username": app_username
                                        }

                actual_api_values = {
                    "success": cash_txn_success,
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
def test_common_400_401_016():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_Successtxn_WithExpiredToken
    Sub Feature Description: Login and do success txn using expired token
    TC naming code description:
        400: Generic functions
        401: Autologin
        016: TC016
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(completed)-------------------------------------------

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

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + " and deviceIdentifierType = imei limit 1';"

        logger.debug(f"Query to fetch org_code from the DB : {query}")
        resultFromDB = DBProcessor.getValueFromDB(query)


        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code
                                                                                       }
                                                  )

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                                            "password": portal_password,
                                                                                                            "settingForOrgCode": org_code
                                                                                                            }
                                                 )

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

        if resultFromDB.empty:

            expected_deviceIdentifier = random.randint(0, 10 ** 15)
            print("expected_deviceIdentifier", expected_deviceIdentifier)

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier ,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })


            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            expected_Sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_Sub_id}")


        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + " and deviceIdentifierType = imei limit 1';"

            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expected_deviceIdentifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_deviceIdentifier}")
            expected_Sub_id = result['subscriberId'].values[0]
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
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Response is :", response)
            login_success = response['success']
            login_autologin_by_token_enabled = response['setting']['autoLoginByTokenEnabled']
            logger.debug(f"AutoLoginEnabled id is : {login_autologin_by_token_enabled}")
            login_username = response['username']
            logger.debug(f"username is : {login_username}")
            login_org_code = response['orgCode']
            logger.debug(f"orgCode is : {login_org_code}")


            if login_success == True:

                login_subscriber_id = response['subscriberId']
                logger.debug(f"Subscriber id is : {login_subscriber_id}")
                print("subscriber id is :", login_subscriber_id)

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                query = "update auto_login_token set expired=1 where subscriber_id ='" + str(login_subscriber_id) + "';"
                logger.debug(f"Query to fetch org_code from the DB : {query}")
                result = DBProcessor.setValueToDB(query)
                logger.debug(f"Update the auto_login_token set expired =1 : {query}")
                print("Update the auto_login_token  result :", result)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                                      for i in range(20))

                api_details = DBProcessor.get_api_details('cash_payment',request_body={
                        "username": app_username,
                        "amount": "109",
                        "nonce": random.randint(10000, 99999),
                        "externalRefNumber": ext_ref_num,
                        "deviceIdentifier": expected_deviceIdentifier,
                        "appId": "ezetap_android",
                        "deviceIdentifierType": "imei",
                        "subscriberId": expected_Sub_id
                    }
                )

                response = APIProcessor.send_request(api_details)
                print("Response is :", response)
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
                expected_api_values =  {"success": True,
                                        "subscriber_id": expected_Sub_id,
                                        "autologin_by_token_enabled": True,
                                        "orgCode": org_code,
                                        "username": app_username
                                        }

                actual_api_values = {
                    "success": cash_txn_success,
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
def test_common_400_401_017():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_SessionExpiry_InvalidAppID
    Sub Feature Description: Do txn using invalid appID after session expiry
    TC naming code description:
        400: Generic functions
        401: Autologin
        017: TC017
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(completed)-------------------------------------------

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

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + " and deviceIdentifierType = imei limit 1';"

        logger.debug(f"Query to fetch org_code from the DB : {query}")
        resultFromDB = DBProcessor.getValueFromDB(query)


        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")


        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code
                                                                                       }
                                                  )

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                                            "password": portal_password,
                                                                                                            "settingForOrgCode": org_code
                                                                                                            }
                                                 )

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

        if resultFromDB.empty:

            expected_deviceIdentifier = random.randint(0, 10 ** 15)
            print("expected_deviceIdentifier", expected_deviceIdentifier)

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier ,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Login Response is :", response)
            expected_Sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_Sub_id}")

        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + " and deviceIdentifierType = imei limit 1';"

            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expected_deviceIdentifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_deviceIdentifier}")
            expected_Sub_id = result['subscriberId'].values[0]
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
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Login Response is :", response)
            login_success = response['success']
            logger.debug(f"success id is : {login_success}")


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
                        "deviceIdentifier": expected_deviceIdentifier,
                        "appId": expected_appID,
                        "deviceIdentifierType": "imei",
                        "subscriberId": expected_Sub_id
                    }
                )

                response = APIProcessor.send_request(api_details)
                print("Cash txn Response is :", response)
                actual_cashTxn_success = response['success']
                logger.debug(f"success id is : {actual_cashTxn_success}")
                actual_cashTxn_errorCode = response['errorCode']
                logger.debug(f"errorCode id is : {actual_cashTxn_errorCode}")
                actual_cashTxn_errorMessage = response['errorMessage']
                logger.debug(f"errorMessage id is : {actual_cashTxn_errorMessage}")
                actual_cashTxn_realCode = response['realCode']
                logger.debug(f"realCode id is : {actual_cashTxn_realCode}")
                actual_cashTxn_message = response['message']
                logger.debug(f"message id is : {actual_cashTxn_message}")

                if actual_cashTxn_success == True:
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

            expected_cashTxn_errorCode = "EZETAP_0000073"
            expected_cashTxn_errorMessage = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_cashTxn_realCode = "AUTH_FAILED"
            expected_cashTxn_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."

            try:
                expected_api_values = { "success": False,
                                        "errorCode":expected_cashTxn_errorCode,
                                        "errorMessage":expected_cashTxn_errorMessage,
                                        "realCode":expected_cashTxn_realCode,
                                        "message":expected_cashTxn_message
                                      }

                actual_api_values = {"success": actual_cashTxn_success,
                                     "errorCode": actual_cashTxn_errorCode,
                                     "errorMessage": actual_cashTxn_errorMessage,
                                     "realCode": actual_cashTxn_realCode,
                                     "message": actual_cashTxn_message
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
def test_common_400_401_018():
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_SessionExpiry_InvalidDeviceID
    Sub Feature Description: Do txn using invalid device ID after session expiry
    TC naming code description:
        400: Generic functions
        401: Autologin
        018: TC018
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(completed)-------------------------------------------

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

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + " and deviceIdentifierType = imei limit 1';"

        logger.debug(f"Query to fetch org_code from the DB : {query}")
        resultFromDB = DBProcessor.getValueFromDB(query)


        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code
                                                                                       }

                                                  )

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                                            "password": portal_password,
                                                                                                            "settingForOrgCode": org_code
                                                                                                            }
                                                 )

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

        if resultFromDB.empty:

            expected_deviceIdentifier = random.randint(0, 10 ** 15)
            print("expected_deviceIdentifier", expected_deviceIdentifier)

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier ,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Login Response is :", response)
            expected_Sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_Sub_id}")


        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + " and deviceIdentifierType = imei limit 1';"

            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expected_deviceIdentifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_deviceIdentifier}")
            expected_Sub_id = result['subscriberId'].values[0]
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
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Login Response is :", response)
            login_success = response['success']
            logger.debug(f"success id is : {login_success}")


            if login_success == True:

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                                      for i in range(20))

                expected_deviceIdentifier = 'zmxl'

                api_details = DBProcessor.get_api_details('cash_payment',request_body={
                        "username": app_username,
                        "amount": "109",
                        "nonce": random.randint(10000, 99999),
                        "externalRefNumber": ext_ref_num,
                        "deviceIdentifier": expected_deviceIdentifier,
                        "appId": "ezetap_android",
                        "deviceIdentifierType": "imei",
                        "subscriberId": expected_Sub_id
                    }
                )

                response = APIProcessor.send_request(api_details)
                print("Cash txn Response is :", response)
                actual_cashTxn_success = response['success']
                logger.debug(f"success id is : {actual_cashTxn_success}")
                actual_cashTxn_errorCode = response['errorCode']
                logger.debug(f"errorCode id is : {actual_cashTxn_errorCode}")
                actual_cashTxn_errorMessage = response['errorMessage']
                logger.debug(f"errorMessage id is : {actual_cashTxn_errorMessage}")
                actual_cashTxn_realCode = response['realCode']
                logger.debug(f"realCode id is : {actual_cashTxn_realCode}")
                actual_cashTxn_message = response['message']
                logger.debug(f"message id is : {actual_cashTxn_message}")

                if actual_cashTxn_success == True:
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

            expected_cashTxn_errorCode = "EZETAP_0000073"
            expected_cashTxn_errorMessage = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_cashTxn_realCode = "AUTH_FAILED"
            expected_cashTxn_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."

            try:
                expected_api_values = { "success": False,
                                        "errorCode":expected_cashTxn_errorCode,
                                        "errorMessage":expected_cashTxn_errorMessage,
                                        "realCode":expected_cashTxn_realCode,
                                        "message":expected_cashTxn_message
                                      }

                actual_api_values = {"success": actual_cashTxn_success,
                                     "errorCode": actual_cashTxn_errorCode,
                                     "errorMessage": actual_cashTxn_errorMessage,
                                     "realCode": actual_cashTxn_realCode,
                                     "message": actual_cashTxn_message
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
def test_common_400_401_019():
    """
     Sub Feature Code: NonUI_Common_Generic_Autologin_SessionExpiry_InvalidDeviceID
     Sub Feature Description:Do txn using invalid deviceID type after session expiry
     TC naming code description:
         400: Generic functions
         401: Autologin
         019: TC019
     """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(completed)-------------------------------------------

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

        query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
            org_code) + " and deviceIdentifierType = imei limit 1';"

        logger.debug(f"Query to fetch org_code from the DB : {query}")
        resultFromDB = DBProcessor.getValueFromDB(query)


        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, closedloop_log=False, q2_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code
                                                                                       }
                                                  )

        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions for autoLoginByTokenEnabled is : {response}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                                            "password": portal_password,
                                                                                                            "settingForOrgCode": org_code
                                                                                                            }
                                                 )

        api_details["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

        if resultFromDB.empty:

            expected_deviceIdentifier = random.randint(0, 10 ** 15)
            print("expected_deviceIdentifier", expected_deviceIdentifier)

            api_details = DBProcessor.get_api_details('Login', request_body={
                "username": app_username,
                "password": app_password,
                "deviceIdentifier": expected_deviceIdentifier ,
                "appId": "ezetap_android",
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Login Response is :", response)
            expected_Sub_id = response['subscriberId']
            logger.debug(f"Subscriber id is : {expected_Sub_id}")


        else:
            query = "select device_identifier, subscriber_id from org_subscription where org_code='" + str(
                org_code) + " and deviceIdentifierType = imei limit 1';"

            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expected_deviceIdentifier = result['device_identifier'].values[0]
            logger.debug(f"Query result, device_identifier : {expected_deviceIdentifier}")
            expected_Sub_id = result['subscriberId'].values[0]
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
                "deviceIdentifierType": "imei"
            })

            response = APIProcessor.send_request(api_details)
            print("Login Response is :", response)
            login_success = response['success']
            logger.debug(f"success id is : {login_success}")


            if login_success == True:

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                                      for i in range(20))

                expected_deviceIdentifierType = 'zmx'

                api_details = DBProcessor.get_api_details('cash_payment',request_body={
                        "username": app_username,
                        "amount": "109",
                        "nonce": random.randint(10000, 99999),
                        "externalRefNumber": ext_ref_num,
                        "deviceIdentifier": expected_deviceIdentifier,
                        "appId": "ezetap_android",
                        "deviceIdentifierType": expected_deviceIdentifierType,
                        "subscriberId": expected_Sub_id
                    }
                )

                response = APIProcessor.send_request(api_details)
                print("Cash txn Response is :", response)
                actual_cashTxn_success = response['success']
                logger.debug(f"success id is : {actual_cashTxn_success}")
                actual_cashTxn_errorCode = response['errorCode']
                logger.debug(f"errorCode id is : {actual_cashTxn_errorCode}")
                actual_cashTxn_errorMessage = response['errorMessage']
                logger.debug(f"errorMessage id is : {actual_cashTxn_errorMessage}")
                actual_cashTxn_realCode = response['realCode']
                logger.debug(f"realCode id is : {actual_cashTxn_realCode}")
                actual_cashTxn_message = response['message']
                logger.debug(f"message id is : {actual_cashTxn_message}")

                if actual_cashTxn_success == True:
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

            # expected_cashTxn_errorCode = "SESSION_EXPIRED"
            # expected_cashTxn_errorMessage = "Your session has expired. Please login again."
            # expected_cashTxn_realCode = "SESSION_EXPIRED"
            # expected_cashTxn_message = "Your session has expired. Please login again."

            try:
                expected_api_values = { "success": False,
                                        # "errorCode":expected_cashTxn_errorCode,
                                        # "errorMessage":expected_cashTxn_errorMessage,
                                        # "realCode":expected_cashTxn_realCode,
                                        # "message":expected_cashTxn_message
                                      }

                actual_api_values = {"success": actual_cashTxn_success,
                                     # "errorCode": actual_cashTxn_errorCode,
                                     # "errorMessage": actual_cashTxn_errorMessage,
                                     # "realCode": actual_cashTxn_realCode,
                                     # "message": actual_cashTxn_message
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