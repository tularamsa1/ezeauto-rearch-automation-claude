import random
import sys

import pytest

from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, APIProcessor, DBProcessor, ConfigReader, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


# app_username = "3456564537"
# app_password = "S1234567"
# portal_username = "8976986700"
# portal_password = "S1234567"

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_032():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: NonUI_Common_Generic_Autologin_AutoLoginAPI_DisableAutologin
    Sub Feature Description: Call autologin API after disabling autologin feature. Steps : Disable autologin -> Do login
    TC naming code description:
    400: Generic function
    401: Autologin
    032: TC032
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

        query = "select device_identifier,subscriber_id from org_subscription where org_code = '"+org_code+"' and device_identifier_type = 'imei' limit 1;"
        logger.debug(f"Query to fetch data from org_subscription table : {query}")
        result = DBProcessor.getValueFromDB(query, "ezetap_demo")
        logger.debug(f"Query result URL: {result}")

        expected_appId = "ezetap_android"
        expected_deviceIdentifierType = "imei"

        if result.empty:
            # If the merchant doesn't have entries in org_subscription table, creating one entry with new deviceIdentifier
            expected_deviceIdentifier =  random.randint(-10000,99999)
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
            login_username = login_response['username']
            login_autologinEnabled = login_response['setting']['autoLoginByTokenEnabled']

            if login_success == True:
                logger.info(f"Login is Success as expected")
                logger.info(f"Expected subscriberID from db   :  {expected_subscriberId}")
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

            # Token should be null in login response, since autoLogin is disabled
            try:
                expectedAPIValues_autologin= {"success": True, "username":app_username, "autoLoginByTokenEnabled":False}
                actualAPIValues_autologin = {"success": login_success, "username":login_username, "autoLoginByTokenEnabled":login_autologinEnabled}
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

