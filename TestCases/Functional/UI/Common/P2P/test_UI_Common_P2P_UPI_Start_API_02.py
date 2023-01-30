import sys
import pytest
from numpy.random import randint

from Configuration import testsuite_teardown, TestSuiteSetup
from Configuration import Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_500_501_038():
    """
    Sub Feature Code: UI_Common_P2P_UPI_Start_API_Wrong_device_Serial_38
    Sub Feature Description: Send start API for UPI transaction with wrong device_serial in API request
    TC naming code description: 500: P2P, 501: P2P_UPI, 038: TC038
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "select * from app_key where org_code = '" + str(org_code) + "' AND status = 'ACTIVE';"
        logger.debug(f"Query to fetch app_key from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of app_key table is : {result}")
        app_key = result['app_key'].values[0]
        logger.debug(f"Query result of app_key : {app_key}")

        query = "select id from org_employee where username ='" + str(app_username) + "'"
        logger.debug(f"Query to fetch user id from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        user_id = result['id'].values[0]

        query = "select * from terminal_info where org_code='" + str(org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Query to fetch device_serial from the DB is : {device_serial}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"Logged in to the app")
            logger.info(f"Loaded home page")

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                logger.error(f"Could not find P2P connection in redis server")
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

            app_driver.back()

            external_ref_num = randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            #pass wrong device_serial
            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": "201",
                "paymentMode": "UPI",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": ""+device_serial[:-2]+"|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_success = response['success']
            logger.debug(f"Response of Start api, success value is : {start_success}")
            start_error_code = response['errorCode']
            logger.debug(f"Response of Start api, start_error_code value is : {start_error_code}")
            start_error_message = response['errorMessage']
            logger.debug(f"Response of Start api, start_error_message value is : {start_error_message}")
            start_message = response['message']
            logger.debug(f"Response of Start api, start_message value is : {start_message}")
            start_real_code = response['realCode']
            logger.debug(f"Response of Start api, start_real_code value is : {start_real_code}")

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
            expected_message = "DeviceId not found. Please resend with Valid DeviceId."
            expected_error_message = "DeviceId not found. Please resend with Valid DeviceId."
            expected_real_code = "P2P_DEVICE_NOT_FOUND"
            expected_error_code = "EZETAP_0000382"

            try:
                expected_api_values = {
                    "success": expected_success,
                    "error_message": expected_error_message,
                    "message": expected_message,
                    "real_code": expected_real_code,
                    "error_code": expected_error_code
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": start_success,
                    "error_message": start_error_message,
                    "message": start_message,
                    "real_code": start_real_code,
                    "error_code": start_error_code
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

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
def test_500_501_039():
    """
    Sub Feature Code: UI_Common_P2P_UPI_Start_API_Wrong_App_Key_39
    Sub Feature Description: Send start API for UPI transaction with wrong appkey in API request
    TC naming code description: 500: P2P, 501: P2P_UPI, 039: TC039
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "select * from app_key where org_code = '" + str(org_code) + "' AND status = 'ACTIVE';"
        logger.debug(f"Query to fetch app_key from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of app_key table is : {result}")
        app_key = result['app_key'].values[0]
        logger.debug(f"Query result of app_key : {app_key}")

        query = "select * from terminal_info where org_code='" + str(org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Query to fetch device_serial from the DB is : {device_serial}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"Logged in to the app")
            logger.info(f"Loaded home page")

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                logger.error(f"Could not find P2P connection in redis server")
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

            app_driver.back()

            external_ref_num = randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            #pass wrong appkey
            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key[:-2],
                "amount": "201",
                "paymentMode": "UPI",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": ""+device_serial+"|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_success = response['success']
            logger.debug(f"Response of Start api, success value is : {start_success}")
            start_error_code = response['errorCode']
            logger.debug(f"Response of Start api, start_error_code value is : {start_error_code}")
            start_error_message = response['errorMessage']
            logger.debug(f"Response of Start api, start_error_message value is : {start_error_message}")
            start_message = response['message']
            logger.debug(f"Response of Start api, start_message value is : {start_message}")
            start_real_code = response['realCode']
            logger.debug(f"Response of Start api, start_real_code value is : {start_real_code}")
            start_errorCode = response['errorCode']
            logger.debug(f"Response of Start api, start_errorCode value is : {start_errorCode}")

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
            expected_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_real_code = "AUTH_FAILED"
            expected_errorCode = 'EZETAP_0000073'

            try:
                expected_api_values = {
                    "success": expected_success,
                    "error_message": expected_error_message,
                    "message": expected_message,
                    "real_code": expected_real_code,
                    "error_code": expected_errorCode
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": start_success,
                    "error_message": start_error_message,
                    "message": start_message,
                    "real_code": start_real_code,
                    "error_code": start_errorCode
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

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
def test_500_501_040():
    """
    Sub Feature Code: UI_Common_P2P_UPI_Start_API_Without_App_Key_40
    Sub Feature Description: Send start API for UPI transaction without appkey in API request
    TC naming code description: 500: P2P, 501: P2P_UPI, 040: TC040
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "select * from app_key where org_code = '" + str(org_code) + "' AND status = 'ACTIVE';"
        logger.debug(f"Query to fetch app_key from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of app_key table is : {result}")
        app_key = result['app_key'].values[0]
        logger.debug(f"Query result of app_key : {app_key}")

        query = "select * from terminal_info where org_code='" + str(org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Query to fetch device_serial from the DB is : {device_serial}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"Logged in to the app")
            logger.info(f"Loaded home page")

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                logger.error(f"Could not find P2P connection in redis server")
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

            app_driver.back()

            external_ref_num = randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            #without appkey
            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "amount": "201",
                "paymentMode": "UPI",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": ""+device_serial+"|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_success = response['success']
            logger.debug(f"Response of Start api, success value is : {start_success}")
            start_error_code = response['errorCode']
            logger.debug(f"Response of Start api, start_error_code value is : {start_error_code}")
            start_error_message = response['errorMessage']
            logger.debug(f"Response of Start api, start_error_message value is : {start_error_message}")
            start_message = response['message']
            logger.debug(f"Response of Start api, start_message value is : {start_message}")
            start_real_code = response['realCode']
            logger.debug(f"Response of Start api, start_real_code value is : {start_real_code}")

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
            expected_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_real_code = "AUTH_FAILED"
            expected_error_code = "EZETAP_0000073"

            try:
                expected_api_values = {
                    "success": expected_success,
                    "error_message": expected_error_message,
                    "message": expected_message,
                    "real_code": expected_real_code,
                    "error_code": expected_error_code
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": start_success,
                    "error_message": start_error_message,
                    "message": start_message,
                    "real_code": start_real_code,
                    "error_code": start_error_code
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

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
def test_500_501_041():
    """
    Sub Feature Code: UI_Common_P2P_UPI_Start_API_Wrong_Password_41
    Sub Feature Description: Send start API for UPI transaction with wrong password in API request
    TC naming code description: 500: P2P, 501: P2P_UPI, 041: TC041
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "select * from app_key where org_code = '" + str(org_code) + "' AND status = 'ACTIVE';"
        logger.debug(f"Query to fetch app_key from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of app_key table is : {result}")
        app_key = result['app_key'].values[0]
        logger.debug(f"Query result of app_key : {app_key}")

        query = "select * from terminal_info where org_code='" + str(org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Query to fetch device_serial from the DB is : {device_serial}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"Logged in to the app")
            logger.info(f"Loaded home page")

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                logger.error(f"Could not find P2P connection in redis server")
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

            app_driver.back()

            external_ref_num = randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            wrong_password = randint(0, 10 ** 7)
            logger.debug(f"wrong_password random number is: {wrong_password}")

            #wrong password
            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": wrong_password,
                "amount": "201",
                "paymentMode": "UPI",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": ""+device_serial+"|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_success = response['success']
            logger.debug(f"Response of Start api, success value is : {start_success}")
            start_error_code = response['errorCode']
            logger.debug(f"Response of Start api, start_error_code value is : {start_error_code}")
            start_error_message = response['errorMessage']
            logger.debug(f"Response of Start api, start_error_message value is : {start_error_message}")
            start_message = response['message']
            logger.debug(f"Response of Start api, start_message value is : {start_message}")
            start_real_code = response['realCode']
            logger.debug(f"Response of Start api, start_real_code value is : {start_real_code}")

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
            expected_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_real_code = "AUTH_FAILED"
            expected_error_code = "EZETAP_0000073"

            try:
                expected_api_values = {
                    "success": expected_success,
                    "error_message": expected_error_message,
                    "message": expected_message,
                    "real_code": expected_real_code,
                    "error_code": expected_error_code
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": start_success,
                    "error_message": start_error_message,
                    "message": start_message,
                    "real_code": start_real_code,
                    "error_code": start_error_code
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

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
def test_500_501_042():
    """
    Sub Feature Code: UI_Common_P2P_UPI_Start_API_Wrong_Username_42
    Sub Feature Description: Send start API for UPI transaction with wrong username in API request
    TC naming code description: 500: P2P, 501: P2P_UPI, 042: TC042
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "select * from app_key where org_code = '" + str(org_code) + "' AND status = 'ACTIVE';"
        logger.debug(f"Query to fetch app_key from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of app_key table is : {result}")
        app_key = result['app_key'].values[0]
        logger.debug(f"Query result of app_key : {app_key}")

        query = "select * from terminal_info where org_code='" + str(org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Query to fetch device_serial from the DB is : {device_serial}")

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"Logged in to the app")
            logger.info(f"Loaded home page")

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                logger.error(f"Could not find P2P connection in redis server")
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

            app_driver.back()

            external_ref_num = randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            wrong_username = randint(0, 10 ** 8)
            logger.debug(f"wrong_password random number is: {wrong_username}")

            #wrong password
            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": wrong_username,
                "password": app_password,
                "amount": "201",
                "paymentMode": "UPI",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": ""+device_serial+"|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_success = response['success']
            logger.debug(f"Response of Start api, success value is : {start_success}")
            start_error_code = response['errorCode']
            logger.debug(f"Response of Start api, start_error_code value is : {start_error_code}")
            start_error_message = response['errorMessage']
            logger.debug(f"Response of Start api, start_error_message value is : {start_error_message}")
            start_message = response['message']
            logger.debug(f"Response of Start api, start_message value is : {start_message}")
            start_real_code = response['realCode']
            logger.debug(f"Response of Start api, start_real_code value is : {start_real_code}")
            start_error_code = response['errorCode']
            logger.debug(f"Response of Start api, start_error_code value is : {start_error_code}")

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
            expected_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
            expected_real_code = "AUTH_FAILED"
            expected_error_code = "EZETAP_0000073"

            try:
                expected_api_values = {
                    "success": expected_success,
                    "error_message": expected_error_message,
                    "message": expected_message,
                    "real_code": expected_real_code,
                    "error_code": expected_error_code
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": start_success,
                    "error_message": start_error_message,
                    "message": start_message,
                    "real_code": start_real_code,
                    "error_code": start_error_code
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

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