import random
import sys

import pytest

from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


# app_username = "3456564537"
# app_password = "S1234567"
# portal_username = "8976986700"
# portal_password = "S1234567"

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_400_401_027():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_AutoLoginAPI_Success
    Sub Feature Description: Call autologin API successfully -> Autologin enabled -> steps:Do login -> fetch subID -> Do autologin -> expire token through DB -> do autologin
    TC naming code description:
    400: Generic function
    401: Autologin feature
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


        # Set autologin enabled
        orgsettings_apidetails_autoLoginEnable = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                            "password": portal_password,
                                                                                            "settingForOrgCode": org_code})
        orgsettings_apidetails_autoLoginEnable["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {orgsettings_apidetails_autoLoginEnable} ")
        response = APIProcessor.send_request(orgsettings_apidetails_autoLoginEnable)
        logger.debug(f"Response received for setting autoLoginByTokenEnabled as True is : {response}")


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
                logger.info("Login is Success")
                login_subId = login_response['subscriberId']
                logger.info(f"Expected subscriberID from db   :{expected_subscriberId}")
                logger.info(f"SubscriberID from login response : {login_subId}")

                autologin_api_details = DBProcessor.get_api_details('autoLogin',
                                                                request_body={"username": app_username,
                                                                              "subscriberId": login_subId,
                                                                              "deviceIdentifier": expected_deviceIdentifier,
                                                                              "appId": expected_appId,
                                                                              "deviceIdentifierType": expected_deviceIdentifierType})

                autologin_response = APIProcessor.send_request(autologin_api_details)
                autologin_success = autologin_response['success']

                if autologin_success == True:
                    logger.info(f"Autologin is Success")
                    autologin_token1 = autologin_response['token']

                    query = "select expired from auto_login_token where subscriber_id = '" + login_subId + "';"
                    logger.debug(f"Query to fetch data from auto_login_token table : {query}")
                    result = DBProcessor.getValueFromDB(query, "ezetap_demo")
                    logger.debug(f"Query result URL: {result}")
                    db_expired = result["expired"].iloc[0]
                    logger.info(f"Value for 'expired' from auto_login_table : expected = 0, actual = {db_expired}")


                    update_query = "update auto_login_token set expired=1 where subscriber_id ='"+login_subId+"';"
                    logger.debug(f"Query to update auto_login_token table : {query}")
                    update_result = DBProcessor.setValueToDB(update_query, "ezetap_demo")
                    logger.debug(f"Query result URL for update: {result}")

                    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                          "password": portal_password})
                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Response received for setting precondition DB refresh is : {response}")

                    # Hit autologin API and fetch token2

                    autologin_api_details2 = DBProcessor.get_api_details('autoLogin',
                                                                        request_body={"username": app_username,
                                                                                      "subscriberId": login_subId,
                                                                                      "deviceIdentifier": expected_deviceIdentifier,
                                                                                      "appId": expected_appId,
                                                                                      "deviceIdentifierType": expected_deviceIdentifierType})

                    autologin_response2 = APIProcessor.send_request(autologin_api_details2)
                else:
                    logger.error(f"Autologin failed expected to be success")
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

                autologin_success2 = autologin_response2['success']
                autologin_username2 = autologin_response2['username']
                autologin_token_enabled2 = autologin_response2['setting']['autoLoginByTokenEnabled']
                autologin_subscriberID2 = autologin_response2['subscriberId']
                autologin_token2 = autologin_response2['token']
                if autologin_token1 == autologin_token2:
                    logger.error(f"First and second tokens are same after updating DB")
                    autologin_token1 = "First token"
                    autologin_token2 = "Second token"
                else:
                    autologin_token1 = "token"
                    autologin_token2 = "token"


                expectedAPIValues_autologin= {"success": True, "username":app_username, "autoLoginByTokenEnabled":True,"subscriberId":login_subId,"token":autologin_token1}
                actualAPIValues_autologin = {"success": autologin_success2, "username":autologin_username2, "autoLoginByTokenEnabled":autologin_token_enabled2,"subscriberId":autologin_subscriberID2,"token":autologin_token2}
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_autologin, actualAPI=actualAPIValues_autologin)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        ####################### End of API Validation ###############################################

        ####################### Starting of DB Validation ###############################################
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                expectedDBValues = {"expired": 0}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select expired from auto_login_token where subscriber_id = '"+login_subId+"';"
                logger.debug(f"Query to fetch data from auto_login_token table in DB validation: {query}")
                result = DBProcessor.getValueFromDB(query, "ezetap_demo")
                logger.debug(f"Query result URL: {result}")
                db_expired = result["expired"].iloc[0]
                actualDBValues = {"expired": db_expired}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                # msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            # # -----------------------------------------End of DB Validation---------------------------------------



        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    finally:
        Configuration.executeFinallyBlock(testcase_id)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_028():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_AutoLoginAPI_01
    Sub Feature Description: Call autologin API with invalid sub ID - > Autologin enabled -> Steps: Do login -> Fetch subId -> Do autologin with invalid SubID
    TC naming code description:
    400: Generic function
    401: Autologin feature
    028: TC028
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

        orgsettings_apidetails_autoLoginEnable = DBProcessor.get_api_details('org_settings_update',
                                                                             request_body={"username": portal_username,
                                                                                           "password": portal_password,
                                                                                           "settingForOrgCode": org_code})
        orgsettings_apidetails_autoLoginEnable["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {orgsettings_apidetails_autoLoginEnable} ")
        response = APIProcessor.send_request(orgsettings_apidetails_autoLoginEnable)
        logger.debug(f"Response received for setting autoLoginByTokenEnabled as True is : {response}")


        query = "select device_identifier,subscriber_id from org_subscription where org_code = '" + org_code + "' and device_identifier_type = 'imei' limit 1;"
        logger.debug(f"Query to fetch data from org_subscription table : {query}")
        result = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query result URL: {result}")

        expected_appId = "ezetap_android"
        expected_deviceIdentifierType = "imei"

        if result.empty:
            # If the merchant doesn't have entries in org_subscription table, creating one entry with new deviceIdentifier
            expected_deviceIdentifier = random.randint(10000, 99999)
            create_sub_id_in_DB = DBProcessor.get_api_details('login_autologin',
                                                              request_body={
                                                                  "username": app_username,
                                                                  "password": app_password,
                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                  "appId": expected_appId,
                                                                  "deviceIdentifierType": expected_deviceIdentifierType})

            create_subId_login_response = APIProcessor.send_request(create_sub_id_in_DB)
            expected_subscriberId = create_subId_login_response['subscriberId']
        else:
            # If merchant has entry in org_subscription table
            expected_deviceIdentifier = result["device_identifier"].iloc[0]
            expected_subscriberId = result["subscriber_id"].iloc[0]

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

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
                                                                "appId": expected_appId,
                                                                "deviceIdentifierType": expected_deviceIdentifierType})

            login_response = APIProcessor.send_request(login_api_details)
            login_success = login_response['success']

            if login_success == True:
                logger.info("Login is Success")
                login_subId = login_response['subscriberId']
                logger.info(f"Expected subscriberID from db   : {expected_subscriberId}")
                logger.info(f"SubscriberID from login response :  {login_subId}")


                invalid_subId = "38927359877"

                autologin_api_details = DBProcessor.get_api_details('autoLogin',
                                                                    request_body={"username": app_username,
                                                                                  "subscriberId": invalid_subId,
                                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                                  "appId": expected_appId,
                                                                                  "deviceIdentifierType": expected_deviceIdentifierType})

                autologin_response = APIProcessor.send_request(autologin_api_details)
                autologin_success = autologin_response['success']

                if autologin_success == False:
                    logger.info(f"Autologin failed as expected due to invalid SubId")
                else:
                    logger.error(f"Autologin is success, expected to be failed due to invalid SubId")

            else:
                logger.error("Login Failed")

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

                autologin_success = autologin_response['success']
                autologin_errorCode = autologin_response['errorCode']
                autologin_errorMessage = autologin_response['errorMessage']
                autologin_realCode = autologin_response['realCode']

                logger.info(f"Started API validation for the test case : {testcase_id}")
                try:
                    expectedAPIValues_autologin = {"success": False, "errorCode": "EZETAP_0000073",
                                                   "errorMessage": "Invalid credentials. Verify your credentials, login again, or contact your supervisor.",
                                                   "realCode": "AUTH_FAILED"}
                    actualAPIValues_autologin = {"success": autologin_success, "errorCode": autologin_errorCode,
                                                 "errorMessage": autologin_errorMessage, "realCode": autologin_realCode}
                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_autologin,
                                                   actualAPI=actualAPIValues_autologin)
                except Exception as e:
                    Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")
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
def test_common_400_401_029():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_AutoLoginAPI_InvalidUsername
    Sub Feature Description: Call autologin API with invalid username. Autologin enabled. Steps : Do login -> Fetch subID -> Do autologin with invalid username
    TC naming code description:
    400: Generic function
    401: Autologin Feature
    029: TC029
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

        orgsettings_apidetails_autoLoginEnable = DBProcessor.get_api_details('org_settings_update',
                                                                             request_body={"username": portal_username,
                                                                                           "password": portal_password,
                                                                                           "settingForOrgCode": org_code})
        orgsettings_apidetails_autoLoginEnable["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {orgsettings_apidetails_autoLoginEnable} ")
        response = APIProcessor.send_request(orgsettings_apidetails_autoLoginEnable)
        logger.debug(f"Response received for setting autoLoginByTokenEnabled as True is : {response}")


        query = "select device_identifier,subscriber_id from org_subscription where org_code = '" + org_code + "' and device_identifier_type = 'imei' limit 1;"
        logger.debug(f"Query to fetch data from org_subscription table : {query}")
        result = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query result URL: {result}")

        expected_appId = "ezetap_android"
        expected_deviceIdentifierType = "imei"

        if result.empty:
            # If the merchant doesn't have entries in org_subscription table, creating one entry with new deviceIdentifier
            expected_deviceIdentifier = random.randint(10000, 99999)
            create_sub_id_in_DB = DBProcessor.get_api_details('login_autologin',
                                                              request_body={
                                                                  "username": app_username,
                                                                  "password": app_password,
                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                  "appId": expected_appId,
                                                                  "deviceIdentifierType": expected_deviceIdentifierType})

            create_subId_login_response = APIProcessor.send_request(create_sub_id_in_DB)
            expected_subscriberId = create_subId_login_response['subscriberId']
        else:
            # If merchant has entry in org_subscription table
            expected_deviceIdentifier = result["device_identifier"].iloc[0]
            expected_subscriberId = result["subscriber_id"].iloc[0]

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

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
                                                                "appId": expected_appId,
                                                                "deviceIdentifierType": expected_deviceIdentifierType})

            login_response = APIProcessor.send_request(login_api_details)
            login_success = login_response['success']

            if login_success == True:
                logger.info("Login is Success")
                login_subId = login_response['subscriberId']
                logger.info(f"Expected subscriberID from db   : {expected_subscriberId}")
                logger.info(f"SubscriberID from login response : {login_subId}")


                invalid_username = "389273598"

                autologin_api_details = DBProcessor.get_api_details('autoLogin',
                                                                    request_body={"username": invalid_username,
                                                                                  "subscriberId": login_subId,
                                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                                  "appId": expected_appId,
                                                                                  "deviceIdentifierType": expected_deviceIdentifierType})

                autologin_response = APIProcessor.send_request(autologin_api_details)
                autologin_success = autologin_response['success']

                if autologin_success == False:
                    logger.info(f"Autologin failed as expected due to invalid username")
                else:
                    logger.error(f"Autologin is success, expected to be failed due to invalid username")

            else:
                logger.error("Login Failed")

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

                autologin_success = autologin_response['success']
                autologin_errorCode = autologin_response['errorCode']
                autologin_errorMessage = autologin_response['errorMessage']
                autologin_realCode = autologin_response['realCode']

                logger.info(f"Started API validation for the test case : {testcase_id}")
                try:
                    expectedAPIValues_autologin = {"success": False, "errorCode": "EZETAP_0000073",
                                                   "errorMessage": "Invalid credentials. Verify your credentials, login again, or contact your supervisor.",
                                                   "realCode": "AUTH_FAILED"}
                    actualAPIValues_autologin = {"success": autologin_success, "errorCode": autologin_errorCode,
                                                 "errorMessage": autologin_errorMessage, "realCode": autologin_realCode}
                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_autologin,
                                                   actualAPI=actualAPIValues_autologin)
                except Exception as e:
                    Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")
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
def test_common_400_401_030():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_AutoLoginAPI_EmptySubID
    Sub Feature Description: Call autologin API with empty subID. Autologin enabled. Steps: Do login -> Do autologin using empty subID
    TC naming code description:
    400: Generic function
    401: Autologin feature
    030: TC030
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

        orgsettings_apidetails_autoLoginEnable = DBProcessor.get_api_details('org_settings_update',
                                                                             request_body={"username": portal_username,
                                                                                           "password": portal_password,
                                                                                           "settingForOrgCode": org_code})
        orgsettings_apidetails_autoLoginEnable["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {orgsettings_apidetails_autoLoginEnable} ")
        response = APIProcessor.send_request(orgsettings_apidetails_autoLoginEnable)
        logger.debug(f"Response received for setting autoLoginByTokenEnabled as True is : {response}")


        query = "select device_identifier,subscriber_id from org_subscription where org_code = '" + org_code + "' and device_identifier_type = 'imei' limit 1;"

        logger.debug(f"Query to fetch data from org_subscription table : {query}")
        result = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query result URL: {result}")

        expected_appId = "ezetap_android"
        expected_deviceIdentifierType = "imei"

        if result.empty:
            # If the merchant doesn't have entries in org_subscription table, creating one entry with new deviceIdentifier
            expected_deviceIdentifier = random.randint(10000, 99999)
            create_sub_id_in_DB = DBProcessor.get_api_details('login_autologin',
                                                              request_body={
                                                                  "username": app_username,
                                                                  "password": app_password,
                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                  "appId": expected_appId,
                                                                  "deviceIdentifierType": expected_deviceIdentifierType})

            create_subId_login_response = APIProcessor.send_request(create_sub_id_in_DB)
            expected_subscriberId = create_subId_login_response['subscriberId']
        else:
            # If merchant has entry in org_subscription table
            expected_deviceIdentifier = result["device_identifier"].iloc[0]
            expected_subscriberId = result["subscriber_id"].iloc[0]

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

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
                                                                "appId": expected_appId,
                                                                "deviceIdentifierType": expected_deviceIdentifierType})

            login_response = APIProcessor.send_request(login_api_details)
            login_success = login_response['success']

            empty_subId = ""

            if login_success == True:
                logger.info("Login is Success")
                login_subId = login_response['subscriberId']
                logger.info(f"Expected subscriberID from db   : {expected_subscriberId}")
                logger.info(f"SubscriberID from login response : {login_subId}")

                autologin_api_details = DBProcessor.get_api_details('autoLogin',
                                                                    request_body={"username": app_username,
                                                                                  "subscriberId": empty_subId,
                                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                                  "appId": expected_appId,
                                                                                  "deviceIdentifierType": expected_deviceIdentifierType})

                autologin_response = APIProcessor.send_request(autologin_api_details)
                autologin_success = autologin_response['success']

                if autologin_success == False:
                    logger.info(f"Autologin failed as expected due to empty subId")
                else:
                    logger.error(f"Autologin is success, expected to be failed due to empty subId")

            else:
                logger.error("Login Failed")

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

                autologin_success = autologin_response['success']
                autologin_errorCode = autologin_response['errorCode']
                autologin_errorMessage = autologin_response['errorMessage']
                autologin_realCode = autologin_response['realCode']

                logger.info(f"Started API validation for the test case : {testcase_id}")
                try:
                    expectedAPIValues_autologin = {"success": False, "errorCode": "EZETAP_0000073",
                                                   "errorMessage": "Invalid credentials. Verify your credentials, login again, or contact your supervisor.",
                                                   "realCode": "AUTH_FAILED"}
                    actualAPIValues_autologin = {"success": autologin_success, "errorCode": autologin_errorCode,
                                                 "errorMessage": autologin_errorMessage, "realCode": autologin_realCode}
                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_autologin,
                                                   actualAPI=actualAPIValues_autologin)
                except Exception as e:
                    Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")
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
def test_common_400_401_031():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_AutoLoginAPI_EmptyUsername
    Sub Feature Description: Call autologin API with empty username. Autologinenabled. Steps: Do login -> Fetch subID -> Do autologin with empty username
    TC naming code description:
    400: Generic function
    401: Autologin
    031: TC031
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

        orgsettings_apidetails_autoLoginEnable = DBProcessor.get_api_details('org_settings_update',
                                                                             request_body={"username": portal_username,
                                                                                           "password": portal_password,
                                                                                           "settingForOrgCode": org_code})
        orgsettings_apidetails_autoLoginEnable["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        logger.debug(f"API details  : {orgsettings_apidetails_autoLoginEnable} ")
        response = APIProcessor.send_request(orgsettings_apidetails_autoLoginEnable)
        logger.debug(f"Response received for setting autoLoginByTokenEnabled as True is : {response}")

        query = "select device_identifier,subscriber_id from org_subscription where org_code = '" + org_code + "' and device_identifier_type = 'imei' limit 1;"

        logger.debug(f"Query to fetch data from org_subscription table : {query}")
        result = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query result URL: {result}")

        expected_appId = "ezetap_android"
        expected_deviceIdentifierType = "imei"

        if result.empty:
            # If the merchant doesn't have entries in org_subscription table, creating one entry with new deviceIdentifier
            expected_deviceIdentifier = random.randint(10000, 99999)
            create_sub_id_in_DB = DBProcessor.get_api_details('login_autologin',
                                                              request_body={
                                                                  "username": app_username,
                                                                  "password": app_password,
                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                  "appId": expected_appId,
                                                                  "deviceIdentifierType": expected_deviceIdentifierType})

            create_subId_login_response = APIProcessor.send_request(create_sub_id_in_DB)
            expected_subscriberId = create_subId_login_response['subscriberId']
        else:
            # If merchant has entry in org_subscription table
            expected_deviceIdentifier = result["device_identifier"].iloc[0]
            expected_subscriberId = result["subscriber_id"].iloc[0]

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

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
                                                                "appId": expected_appId,
                                                                "deviceIdentifierType": expected_deviceIdentifierType})

            login_response = APIProcessor.send_request(login_api_details)
            login_success = login_response['success']

            empty_username = ""

            if login_success == True:
                logger.info("Login is Success")
                login_subId = login_response['subscriberId']
                logger.info(f"Expected subscriberID from db   : {expected_subscriberId}")
                logger.info(f"SubscriberID from login response : {login_subId}")

                autologin_api_details = DBProcessor.get_api_details('autoLogin',
                                                                    request_body={"username": empty_username,
                                                                                  "subscriberId": login_subId,
                                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                                  "appId": expected_appId,
                                                                                  "deviceIdentifierType": expected_deviceIdentifierType})

                autologin_response = APIProcessor.send_request(autologin_api_details)
                autologin_success = autologin_response['success']

                if autologin_success == False:
                    logger.info(f"Autologin failed as expected due to empty username")
                else:
                    logger.error(f"Autologin is success, expected to be failed due to empty username")

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

                autologin_success = autologin_response['success']
                autologin_errorCode = autologin_response['errorCode']
                autologin_errorMessage = autologin_response['errorMessage']
                autologin_realCode = autologin_response['realCode']

                logger.info(f"Started API validation for the test case : {testcase_id}")
                try:
                    expectedAPIValues_autologin = {"success": False, "errorCode": "EZETAP_0000073",
                                                   "errorMessage": "Invalid credentials. Verify your credentials, login again, or contact your supervisor.",
                                                   "realCode": "AUTH_FAILED"}
                    actualAPIValues_autologin = {"success": autologin_success, "errorCode": autologin_errorCode,
                                                 "errorMessage": autologin_errorMessage, "realCode": autologin_realCode}
                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_autologin,
                                                   actualAPI=actualAPIValues_autologin)
                except Exception as e:
                    Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        ####################### End of API Validation ###############################################

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    finally:
        Configuration.executeFinallyBlock(testcase_id)
