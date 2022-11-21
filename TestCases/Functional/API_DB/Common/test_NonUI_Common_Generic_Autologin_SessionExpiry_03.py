import random
import secrets
import string
import sys
from time import sleep

import pytest

from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_025():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_SessionExpiry_WithoutDeviceID
    Sub Feature Description: Do txn without deviceID in txn after session expiry -> Expiry time is 60 sec and autologin disabled-> Do login -> Wait to expire -> cash txn should fail
    TC naming code description:
    400:
    401:
    027: TC027
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

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

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Set org settings to default
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        #Set autologin enabled as True
        orgsettings_apidetails_autologinDisable = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                            "password": portal_password,
                                                                                            "settingForOrgCode": org_code})
        orgsettings_apidetails_autologinDisable["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {orgsettings_apidetails_autologinDisable} ")
        response = APIProcessor.send_request(orgsettings_apidetails_autologinDisable)
        logger.debug(f"Response received for setting autoLoginByTokenEnabled as True is : {response}")

        # Set session expiry as 60 seconds
        orgsettings_apidetails_setExpiry = DBProcessor.get_api_details('org_settings_update',
                                                                       request_body={"username": portal_username,
                                                                                     "password": portal_password,
                                                                                     "settingForOrgCode": org_code})
        orgsettings_apidetails_setExpiry["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {orgsettings_apidetails_setExpiry} ")
        response = APIProcessor.send_request(orgsettings_apidetails_setExpiry)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

        query = "select device_identifier,subscriber_id from org_subscription where org_code = '"+org_code+"' and device_identifier_type = 'imei' limit 1;"

        logger.debug(f"Query to fetch data from org_subscription table : {query}")
        result = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query result URL: {result}")

        expected_appId = "ezetap_android"
        expected_deviceIdentifierType = "imei"

        if result.empty:
            # If the merchant doesn't have entries in org_subscription table, creating one entry with new deviceIdentifier
            expected_deviceIdentifier =  random.randint(10000,99999)
            create_sub_id_in_DB = DBProcessor.get_api_details('login_autologin',
                                                            request_body={
                                                                "username": app_username,
                                                                "password": app_password,
                                                                "deviceIdentifier": expected_deviceIdentifier,
                                                                "appId": expected_appId,
                                                                "deviceIdentifierType": expected_deviceIdentifierType})

            create_subId_login_response = APIProcessor.send_request(create_sub_id_in_DB)
            expected_subscriberId= create_subId_login_response['subscriberId']
        else:
            # If merchant has entry in org_subscription table
            expected_deviceIdentifier = result["device_identifier"].iloc[0]
            expected_subscriberId = result["subscriber_id"].iloc[0]



        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            login_api_details = DBProcessor.get_api_details('login_autologin',
                                                      request_body={
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "deviceIdentifier": expected_deviceIdentifier,
                                                          "appId":expected_appId,
                                                          "deviceIdentifierType":expected_deviceIdentifierType})


            login_response = APIProcessor.send_request(login_api_details)
            login_success = login_response['success']

            if login_success == True:
                logger.info(f"Login is Success")
                login_subId = login_response['subscriberId']
                logger.info(f"Expected subscriberID from db   :{expected_subscriberId}")
                logger.info(f"SubscriberID from login response : {login_subId}")

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                              for i in range(20))

                cashTxn_api_details = DBProcessor.get_api_details('cash_payment',
                                                                request_body={"username": app_username,
                                                                              "subscriberId": login_subId,
                                                                              "amount": "109",
                                                                              "nonce": random.randint(10000, 99999),
                                                                              "externalRefNumber": ext_ref_num,
                                                                              "appId": expected_appId,
                                                                              "deviceIdentifierType": expected_deviceIdentifierType})

                cash_txn_response = APIProcessor.send_request(cashTxn_api_details)
                actual_cashTxn_success = cash_txn_response['success']

                if actual_cashTxn_success == True:
                    logger.error(f"Cash txn is Success But expected to be failed without deviceID")

                else:
                    logger.info(f"Cash txn failed as expected without deviceID")
            else:
                logger.error(f"Login Failed")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        ####################### Starting of API Validation ###############################################
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                actual_cashTxn_errorCode = cash_txn_response['errorCode']
                actual_cashTxn_errorMessage = cash_txn_response['errorMessage']
                actual_cashTxn_realCode = cash_txn_response['realCode']
                actual_cashTxn_message = cash_txn_response['message']

                expected_cashTxn_errorCode = "EZETAP_0000073"
                expected_cashTxn_errorMessage = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
                expected_cashTxn_realCode = "AUTH_FAILED"
                expected_cashTxn_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."

                expectedAPIValues_autologin= {"success": False, "errorCode":expected_cashTxn_errorCode, "errorMessage":expected_cashTxn_errorMessage,"realCode":expected_cashTxn_realCode,"message":expected_cashTxn_message}
                actualAPIValues_autologin = {"success": actual_cashTxn_success, "errorCode":actual_cashTxn_errorCode, "errorMessage":actual_cashTxn_errorMessage,"realCode":actual_cashTxn_realCode,"message":actual_cashTxn_message}
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_autologin, actualAPI=actualAPIValues_autologin)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        ####################### End of API Validation ###############################################

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    finally:
        Configuration.executeFinallyBlock(testcase_id)





@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_026():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_SessionExpiry_WithoutDeviceInfo
    Sub Feature Description: Do txn without device info in txn after session expiry -> Expiry time= 60 sec and autologin disabled-> Steps: Do login -> Wait to expire -> cash txn should fail
    TC naming code description:
    400: Generic function
    401: Autologin feature
    026: TC026
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

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

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Set org settings to default
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        #Set autologin enabled as True
        orgsettings_apidetails_autologinDisable = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                            "password": portal_password,
                                                                                            "settingForOrgCode": org_code})
        orgsettings_apidetails_autologinDisable["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {orgsettings_apidetails_autologinDisable} ")
        response = APIProcessor.send_request(orgsettings_apidetails_autologinDisable)
        logger.debug(f"Response received for setting autoLoginByTokenEnabled as True is : {response}")

        # Set session expiry as 60 seconds
        orgsettings_apidetails_setExpiry = DBProcessor.get_api_details('org_settings_update',
                                                                       request_body={"username": portal_username,
                                                                                     "password": portal_password,
                                                                                     "settingForOrgCode": org_code})
        orgsettings_apidetails_setExpiry["RequestBody"]["settings"]["sessionTimeOut"] = "60"
        logger.debug(f"API details  : {orgsettings_apidetails_setExpiry} ")
        response = APIProcessor.send_request(orgsettings_apidetails_setExpiry)
        logger.debug(f"Response received for setting sessionExpiry as 60sec is : {response}")

        query = "select device_identifier,subscriber_id from org_subscription where org_code = '"+org_code+"' and device_identifier_type = 'imei' limit 1;"

        logger.debug(f"Query to fetch data from org_subscription table : {query}")
        result = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query result URL: {result}")

        expected_appId = "ezetap_android"
        expected_deviceIdentifierType = "imei"

        if result.empty:
            # If the merchant doesn't have entries in org_subscription table, creating one entry with new deviceIdentifier
            expected_deviceIdentifier =  random.randint(10000,99999)
            create_sub_id_in_DB = DBProcessor.get_api_details('login_autologin',
                                                            request_body={
                                                                "username": app_username,
                                                                "password": app_password,
                                                                "deviceIdentifier": expected_deviceIdentifier,
                                                                "appId": expected_appId,
                                                                "deviceIdentifierType": expected_deviceIdentifierType})

            create_subId_login_response = APIProcessor.send_request(create_sub_id_in_DB)
            expected_subscriberId= create_subId_login_response['subscriberId']
        else:
            # If merchant has entry in org_subscription table
            expected_deviceIdentifier = result["device_identifier"].iloc[0]
            expected_subscriberId = result["subscriber_id"].iloc[0]



        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            login_api_details = DBProcessor.get_api_details('login_autologin',
                                                      request_body={
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "deviceIdentifier": expected_deviceIdentifier,
                                                          "appId":expected_appId,
                                                          "deviceIdentifierType":expected_deviceIdentifierType})


            login_response = APIProcessor.send_request(login_api_details)
            login_success = login_response['success']

            if login_success == True:
                logger.info(f"Login is Success")
                login_subId = login_response['subscriberId']
                logger.info(f"Expected subscriberID from db   :{expected_subscriberId}")
                logger.info(f"SubscriberID from login response : {login_subId}")

                logger.debug(f"Waiting for 65 seconds to expire session")
                sleep(65)

                ext_ref_num = ''.join(secrets.choice(string.ascii_lowercase + string.digits)
                              for i in range(20))

                cashTxn_api_details = DBProcessor.get_api_details('cash_payment',
                                                                request_body={"username": app_username,
                                                                              "subscriberId": login_subId,
                                                                              "amount": "109",
                                                                              "nonce": random.randint(10000, 99999),
                                                                              "externalRefNumber": ext_ref_num})

                cash_txn_response = APIProcessor.send_request(cashTxn_api_details)
                actual_cashTxn_success = cash_txn_response['success']

                if actual_cashTxn_success == True:
                    logger.error(f"Cash txn is Success But expected to be failed without any device info")

                else:
                    logger.info(f"Cash txn failed as expected without any device info")
            else:
                logger.error(f"Login Failed, expected to be success")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        ####################### Starting of API Validation ###############################################
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                actual_cashTxn_errorCode = cash_txn_response['errorCode']
                actual_cashTxn_errorMessage = cash_txn_response['errorMessage']
                actual_cashTxn_realCode = cash_txn_response['realCode']
                actual_cashTxn_message = cash_txn_response['message']

                expected_cashTxn_errorCode = "EZETAP_0000073"
                expected_cashTxn_errorMessage = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
                expected_cashTxn_realCode = "AUTH_FAILED"
                expected_cashTxn_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."

                expectedAPIValues_autologin= {"success": False, "errorCode":expected_cashTxn_errorCode, "errorMessage":expected_cashTxn_errorMessage,"realCode":expected_cashTxn_realCode,"message":expected_cashTxn_message}
                actualAPIValues_autologin = {"success": actual_cashTxn_success, "errorCode":actual_cashTxn_errorCode, "errorMessage":actual_cashTxn_errorMessage,"realCode":actual_cashTxn_realCode,"message":actual_cashTxn_message}
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_autologin, actualAPI=actualAPIValues_autologin)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        ####################### End of API Validation ###############################################

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    finally:
        Configuration.executeFinallyBlock(testcase_id)