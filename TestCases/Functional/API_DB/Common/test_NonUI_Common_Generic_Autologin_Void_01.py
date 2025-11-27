import random
import sys

import pytest

from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, card_processor, merchant_creator, ConfigReader, \
    Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

# app_username = "3456564537"
# app_password = "S1234567"
# portal_username = "8976986700"
# portal_password = "S1234567"

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_033():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_Void_Success
    Sub Feature Description: Void a txn successfully with autologin enabled. Steps: Do login -> Do card txn -> Do success void
    TC naming code description:
    400: Generic function
    401: Autologin feature
    033: TC033
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
                logger.info("Login is Success as expected")
                login_subId = login_response['subscriberId']
                logger.info(f"Expected subscriberID from db   :  {expected_subscriberId}")
                logger.info(f"SubscriberID from login response : {login_subId}")

                ###################### Card transaction ################################################################
                original_amount = random.randint(700,730)
                card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_MASTER")
                card_txn_api_details = DBProcessor.get_api_details('Card_api',
                                                          request_body={"deviceSerial": merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC", payment_gateway="DUMMY"),
                                                              "username": app_username,
                                                              "password": app_password,
                                                              "amount": str(original_amount),
                                                              "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                              "nonce": card_details['Nonce'],
                                                              "externalRefNumber": str(
                                                                  card_details['External Ref']) + str(
                                                                  random.randint(0, 9))})

                response = APIProcessor.send_request(card_txn_api_details)
                card_payment_success = response['success']
                if card_payment_success == True:
                    logger.info(f"Card payment is success as expected")
                    txn_id = response['txnId']
                    confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                    confirm_card_txn_api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                              request_body={"username": app_username,
                                                                            "password": app_password,
                                                                            "ezetapDeviceData": confirm_data["Ezetap Device Data"],
                                                                            "txnId": txn_id,
                                                                            })
                    confirm_response = APIProcessor.send_request(confirm_card_txn_api_details)
                    confirm_success = confirm_response['success']
                    if confirm_success == True:
                        logger.debug(f"Card confirmation API is success")



                        void_txn_api_details = DBProcessor.get_api_details('Void_autologin',
                                                                            request_body={"txnId": txn_id,
                                                                                          "username": app_username,
                                                                                          "addlAuthPin":app_password,
                                                                                          "deviceIdentifier": expected_deviceIdentifier,
                                                                                          "appId": expected_appId,
                                                                                          "deviceIdentifierType": expected_deviceIdentifierType,
                                                                                          "subscriberId":login_subId})



                        void_response = APIProcessor.send_request(void_txn_api_details)
                        void_success = void_response['success']

                        if void_success == False:
                            logger.error(f"Void failed, expected to be success")
                        else:
                            logger.debug(f"Void is success as expected")

                    else:
                        logger.error(f"Card confirmation API is failed, expcted to be success")
                else:
                    logger.error(f"Card payment API failed, expected to be success")

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
                logger.info(f"Started API validation for the test case : {testcase_id}")
                try:
                    expectedAPIValues_void = {"success": True}
                    actualAPIValues_void = {"success": void_success}
                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_void,
                                                   actualAPI=actualAPIValues_void)
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
def test_common_400_401_034():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_Void_InvalidPassword
    Sub Feature Description: Void a txn with invalid password with autologin enabled. Steps: Do login -> Do card txn -> Do void (failed)
    TC naming code description:
    400: Generic function
    401: Autologin
    034: TC034
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
                logger.info(f"Expected subscriberID from db   :  {expected_subscriberId}")
                logger.info(f"SubscriberID from login response :  {login_subId}")

                ###################### Card transaction ################################################################
                original_amount = random.randint(700,730)
                card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_MASTER")
                card_txn_api_details = DBProcessor.get_api_details('Card_api',
                                                          request_body={"deviceSerial": merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC", payment_gateway="DUMMY"),
                                                              "username": app_username,
                                                              "password": app_password,
                                                              "amount": str(original_amount),
                                                              "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                              "nonce": card_details['Nonce'],
                                                              "externalRefNumber": str(
                                                                  card_details['External Ref']) + str(
                                                                  random.randint(0, 9))})

                response = APIProcessor.send_request(card_txn_api_details)
                card_payment_success = response['success']
                if card_payment_success == True:
                    txn_id = response['txnId']
                    confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                    confirm_card_txn_api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                              request_body={"username": app_username,
                                                                            "password": app_password,
                                                                            "ezetapDeviceData": confirm_data["Ezetap Device Data"],
                                                                            "txnId": txn_id,
                                                                            })
                    confirm_response = APIProcessor.send_request(confirm_card_txn_api_details)
                    confirm_success = confirm_response['success']


                    if confirm_success == True:
                        logger.debug(f"Card confirmation API is success")
                    else:
                        logger.error(f"Card confirmation API is failed")

                invalid_password = "GK123456"
                void_txn_api_details = DBProcessor.get_api_details('Void_autologin',
                                                                    request_body={"txnId": txn_id,
                                                                                  "username": app_username,
                                                                                  "addlAuthPin":invalid_password,
                                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                                  "appId": expected_appId,
                                                                                  "deviceIdentifierType": expected_deviceIdentifierType,
                                                                                  "subscriberId":login_subId})



                void_response = APIProcessor.send_request(void_txn_api_details)
                void_success = void_response['success']

                if void_success == False:
                    logger.debug(f"Void failed as expected")
                else:
                    logger.error(f"Void is success, expected to be failed due to invalid password")

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
                logger.info(f"Started API validation for the test case : {testcase_id}")
                try:
                    expectedAPIValues_void = {"success": False}
                    actualAPIValues_void = {"success": void_success}
                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_void,
                                                   actualAPI=actualAPIValues_void)
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
def test_common_400_401_035():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_Void_EmptyPassword
    Sub Feature Description: Void a txn with empty password with enabled autologin. Steps: Do login -> Do card txn -> Do void (failed)
    TC naming code description:
    400: Generic function
    401: Autologin feature
    035: TC035
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

                ###################### Card transaction ################################################################
                original_amount = random.randint(700,730)
                card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_MASTER")
                card_txn_api_details = DBProcessor.get_api_details('Card_api',
                                                          request_body={"deviceSerial": merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC", payment_gateway="DUMMY"),
                                                              "username": app_username,
                                                              "password": app_password,
                                                              "amount": str(original_amount),
                                                              "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                              "nonce": card_details['Nonce'],
                                                              "externalRefNumber": str(
                                                                  card_details['External Ref']) + str(
                                                                  random.randint(0, 9))})

                response = APIProcessor.send_request(card_txn_api_details)
                card_payment_success = response['success']
                if card_payment_success == True:
                    txn_id = response['txnId']
                    confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                    confirm_card_txn_api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                              request_body={"username": app_username,
                                                                            "password": app_password,
                                                                            "ezetapDeviceData": confirm_data["Ezetap Device Data"],
                                                                            "txnId": txn_id,
                                                                            })
                    confirm_response = APIProcessor.send_request(confirm_card_txn_api_details)
                    confirm_success = confirm_response['success']


                    if confirm_success == True:
                        logger.debug(f"Card confirmation API is success")
                    else:
                        logger.error(f"Card confirmation API is failed")

                empty_password = ""
                void_txn_api_details = DBProcessor.get_api_details('Void_autologin',
                                                                    request_body={"txnId": txn_id,
                                                                                  "username": app_username,
                                                                                  "addlAuthPin":empty_password,
                                                                                  "deviceIdentifier": expected_deviceIdentifier,
                                                                                  "appId": expected_appId,
                                                                                  "deviceIdentifierType": expected_deviceIdentifierType,
                                                                                  "subscriberId":login_subId})



                void_response = APIProcessor.send_request(void_txn_api_details)
                void_success = void_response['success']

                if void_success == False:
                    logger.debug(f"Void failed as expected")
                else:
                    logger.error(f"Void is success, expected to be failed due to empty password")

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
                logger.info(f"Started API validation for the test case : {testcase_id}")
                try:
                    expectedAPIValues_void = {"success": False}
                    actualAPIValues_void = {"success": void_success}
                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues_void,
                                                   actualAPI=actualAPIValues_void)
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