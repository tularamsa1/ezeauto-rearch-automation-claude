import sys
import time
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_login_page import LoginPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger


logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_mpos_400_407_003():
    """
     Sub Feature Code: UI_Common_UI_DSN_Setting_AutoLogin_Token_Enabled
     Sub Feature Description: Verifying the org setting "autologin by token enabled" is enabled
     TC naming code description: 400: Generic Actions, 407: Login, 003: TC003
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from org_settings_update api:  {response}")

            success_status = response.get('success')
            logger.debug(f"From response fetch success_status : {success_status}")
            # ------------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "success_status": True,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success_status": success_status,
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
def test_mpos_400_407_004():
    """
     Sub Feature Code:UI_Common_DSN_Setting_MQTT
     Sub Feature Description: Verifying the org setting "MQTT" is enabled
     TC naming code description: 400: Generic Actions, 407: Login, 004: TC004
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["mqttEnabled"] = "true"
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from org_settings_update api:  {response}")

            success_status = response.get('success')
            logger.debug(f"From response fetch success_status : {success_status}")
            # ------------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "success_status": True,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success_status": success_status,
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
@pytest.mark.appVal
@pytest.mark.dbVal
@pytest.mark.apiVal
def test_mpos_400_407_009():
    """
    Sub Feature Code: UI_Common_DSN_API_User_Device_Swapping
    Sub Feature Description: Verifying flow of user device swapping  using API
    TC naming code description: 400: Generic Actions, 407: Login, 009: TC009
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
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_un=portal_username,
                                                       portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        api_details["RequestBody"]["settings"]["mqttEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query= f" select * from terminal_info where org_code ='{org_code}' and payment_gateway= 'HDFC' and acquirer_code = 'HDFC'";
        logger.debug(f"Query to fetch terminal_info details: {query}")
        result=DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table :{result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the terminal_info table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the terminal_info table : {tid}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            device_serial_number = ConfigReader.read_config("dsn_device_serial", "device_serial")
            logger.debug(f" device_serial_number is :{device_serial_number}")
            new_device_serial_number = ConfigReader.read_config("dsn_device_serial", "new_device_serial")
            logger.debug(f" new_device_serial_number is :{new_device_serial_number}")

            api_details = DBProcessor.get_api_details('dsn_device_mapping', request_body={
                "username": app_username,
                "password": app_password,
                "merchantUsername": app_username,
                "tid": tid,
                "mid": mid,
                "deviceSerial": device_serial_number,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from dsn_device_mapping api:  {response}")

            query = f"select id from org_employee where org_code ='{org_code}';"
            logger.debug(f"Query to fetch org_employee details: {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for org_employee table :{result}")
            emp_id = result['id'].values[0]
            logger.debug(f"Fetching id from the org_employee table : {emp_id}")

            query = f"select * from org_subscription where type_id ='{emp_id}' and device_identifier='{device_serial_number}';"
            logger.debug(f"Query to fetch org_subscription details: {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for org_subscription table :{result}")
            subscriber_id = result['subscriber_id'].values[0]
            logger.debug(f"Fetching subscriber_id from the org_subscription table : {subscriber_id}")
            logger.info("Waiting for few seconds to fetch correct data from db before hitting swap endpoint")
            time.sleep(3)

            api_details = DBProcessor.get_api_details('dsn_device_swap', request_body={
                "username": app_username,
                "password": app_password,
                "merchantUsername": app_username,
                "deviceSerial": device_serial_number,
                "newDeviceSerial": new_device_serial_number,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from dsn_device_mapping api:  {response}")

            success_status = response.get('success')
            logger.debug(f"From response fetch success_status : {success_status}")
            message_code = response.get('messageCode')
            logger.debug(f"From response fetch messageCode : {message_code}")
            message = response.get('message')
            logger.debug(f"From response fetch message : {message}")
            real_code = response.get('realCode')
            logger.debug(f"From response fetch real_code : {real_code}")

            query = f"select * from org_subscription where type_id ='{emp_id}' and device_identifier='{subscriber_id}';"
            logger.debug(f"Query to fetch org_subscription details: {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for org_subscription table :{result}")
            device_identifier_old = result['device_identifier'].values[0]
            logger.debug(f"Fetching device_identifier from the org_subscription table : {device_identifier_old}")
            org_code_old = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the org_subscription table : {org_code_old}")

            query = f"select * from org_subscription where type_id ='{emp_id}' and device_identifier='{new_device_serial_number}';"
            logger.debug(f"Query to fetch org_subscription details: {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for org_subscription table :{result}")
            device_identifier_new = result['device_identifier'].values[0]
            logger.debug(f"Fetching new device_identifier from the org_subscription table : {device_identifier_new}")
            device_identifier_type_new = result['device_identifier_type'].values[0]
            logger.debug(f"Fetching new device_identifier_type from the org_subscription table : {device_identifier_type_new}")
            type_id_new = result['type_id'].values[0]
            logger.debug(f"Fetching new type_id from the org_subscription table : {type_id_new}")
            org_code_new = result['org_code'].values[0]
            logger.debug(f"Fetching new org_code from the org_subscription table : {org_code_new}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.select_environment()
            logger.info(f"Logging in the MPOS application using username : {app_username}")

            # ------------------------------------------------------------------------------------------------
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

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_app_values = {'Result': "SUCCESS"}
                try:
                    login_page.validate_login_page()
                    result = 'SUCCESS'
                except:
                    result = 'FAILED'
                actual_app_values = {'Result': result}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "success_status": True,
                    "message_code": "EZETAP_0001650",
                    "message": "Device Swapped SuccessFully",
                    "real_code": "DEVICE_SWAPPED_SUCCESSFULLY",
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success_status": success_status,
                    "message_code": message_code,
                    "message": message,
                    "real_code": real_code,
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
                    "org_code_new": org_code,
                    "device_identifier_new": new_device_serial_number,
                    "device_identifier_type_new": "dsn",
                    "type_id_new": str(emp_id),
                    "org_code_old": "EZETAP",
                    "device_identifier_old": subscriber_id,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "org_code_new": org_code_new,
                    "device_identifier_new": device_identifier_new,
                    "device_identifier_type_new": device_identifier_type_new,
                    "type_id_new": type_id_new,
                    "org_code_old": org_code_old,
                    "device_identifier_old": device_identifier_old,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

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
        try:
            api_details = DBProcessor.get_api_details('dsn_device_unmapping', request_body={
                "username": app_username,
                "password": app_password,
                "deviceSerial": new_device_serial_number,
            })
            logger.debug(f"api details are {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from dsn_device_unmapping api:  {response}")

        except Exception as e:
            logger.exception(f"Not able to unmap due to : {e}")
        Configuration.executeFinallyBlock(testcase_id)