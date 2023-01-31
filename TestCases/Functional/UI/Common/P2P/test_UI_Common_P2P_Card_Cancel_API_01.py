import sys
import random
import pytest
from time import sleep
from Configuration import testsuite_teardown, TestSuiteSetup
from Configuration import Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_500_503_048():
    """
    Sub Feature Code: UI_Common_P2P_Card_Cancel_API_Wrong_Password_48
    Sub Feature Description: Send cancel API for Card transaction request with wrong password in API request
    TC naming code description: 500: P2P, 503: P2P_Card, 048: TC048
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

        query = "select sett.setting_value from setting sett LEFT JOIN org_employee empl on empl.id=sett.entity_id where empl.username ='" + str(
            app_username) + "'and sett.setting_name='onlyP2PUser';"
        logger.debug(f"Query to fetch setting_value from the DB for the user {app_username}: {query}")
        result = DBProcessor.getValueFromDB(query)

        if (len(result)) >= 1:
            # If current app_user is onlyP2P allowed user
            current_setting_val = result['setting_value'].values[0]
            logger.debug(f"Query result, 'onlyP2PUser' setting_value of {app_username}: {current_setting_val}")
            if current_setting_val == "true":
                logger.info(f"Current app user is only P2P allowed user")
            else:
                logger.error(f"Current app user can do normal transactions as well")
        else:
            logger.error(f"Current app user can do normal transactions as well")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

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

            # # Checking P2P notification
            # app_driver.open_notifications()
            # logger.info(f"Pulled notification bar")
            #
            # actual_notification = home_page.check_p2p_notification()
            #
            # expected_notification = "Push 2 Pay is ON"
            # if actual_notification == expected_notification:
            #     logger.debug(f"Located the P2P connection notification")
            # else:
            #     logger.error(f"Could not find P2P connection notification on device")
            #     raise Exception("Could not find P2P connection notification on device")
            #
            # app_driver.back()

            external_ref_num = random.randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            amount = random.randint(100, 200)
            logger.debug(f"amount random number is: {amount}")

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": str(amount),
                "paymentMode": "CARD",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": ""+device_serial+"|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_p2p_request_id = response['p2pRequestId']
            logger.debug(f"Response of Start api, start_p2p_request_id value is : {start_p2p_request_id}")
            sleep(2)

            wrong_password = random.randint(0, 10 ** 7)
            logger.debug(f"wrong_password random number is: {wrong_password}")

            #pass wrong password
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "password": wrong_password,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Cancel api is : {response}")
            cancel_error_code = response['errorCode']
            logger.debug(f"Response of Cancel api, cancel_error_code value is : {cancel_error_code}")
            cancel_error_message = response['errorMessage']
            logger.debug(f"Response of Cancel api, cancel_error_message value is : {cancel_error_message}")
            cancel_message = response['message']
            logger.debug(f"Response of Cancel api, cancel_message value is : {cancel_message}")
            cancel_real_code = response['realCode']
            logger.debug(f"Response of Cancel api, cancel_real_code value is : {cancel_real_code}")
            cancel_success = response['success']
            logger.debug(f"Response of Cancel api, success value is : {cancel_success}")

            query = "select * from p2p_request where id = '" + str(start_p2p_request_id) + "';"
            logger.debug(f"Query to fetch p2p_request from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of p2p_request table is : {result}")
            status_db = result['status'].values[0]
            logger.debug(f"Query result of status_db : {status_db}")
            transaction_id_db = result['transactionId'].values[0]
            logger.debug(f"Query result of transaction_id_db : {transaction_id_db}")

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()

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
            expected_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
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
                    "success": cancel_success,
                    "error_message": cancel_error_message,
                    "message": cancel_message,
                    "real_code": cancel_real_code,
                    "error_code": cancel_error_code
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
                    "status": "RECEIVED",
                    "transaction_id": None,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "status": status_db,
                    "transaction_id": transaction_id_db
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
def test_500_503_049():
    """
    Sub Feature Code: UI_Common_P2P_Card_Cancel_API_Wrong_Username_49
    Sub Feature Description: Send cancel API for Card transaction request with wrong username in API request
    TC naming code description: 500: P2P, 503: P2P_Card, 049: TC049
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

        query = "select sett.setting_value from setting sett LEFT JOIN org_employee empl on empl.id=sett.entity_id where empl.username ='" + str(
            app_username) + "'and sett.setting_name='onlyP2PUser';"
        logger.debug(f"Query to fetch setting_value from the DB for the user {app_username}: {query}")
        result = DBProcessor.getValueFromDB(query)

        if (len(result)) >= 1:
            # If current app_user is onlyP2P allowed user
            current_setting_val = result['setting_value'].values[0]
            logger.debug(f"Query result, 'onlyP2PUser' setting_value of {app_username}: {current_setting_val}")
            if current_setting_val == "true":
                logger.info(f"Current app user is only P2P allowed user")
            else:
                logger.error(f"Current app user can do normal transactions as well")
        else:
            logger.error(f"Current app user can do normal transactions as well")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False,config_log=False)

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

            external_ref_num = random.randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            amount = random.randint(100, 200)
            logger.debug(f"amount random number is: {amount}")

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": str(amount),
                "paymentMode": "CARD",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": "" + device_serial + "|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_p2p_request_id = response['p2pRequestId']
            logger.debug(f"Response of Start api, start_p2p_request_id value is : {start_p2p_request_id}")
            sleep(2)

            wrong_username = random.randint(0, 10 ** 8)
            logger.debug(f"wrong_password random number is: {wrong_username}")

            # pass wrong username
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": wrong_username,
                "password": app_password,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Cancel api is : {response}")
            cancel_error_code = response['errorCode']
            logger.debug(f"Response of Cancel api, cancel_error_code value is : {cancel_error_code}")
            cancel_error_message = response['errorMessage']
            logger.debug(f"Response of Cancel api, cancel_error_message value is : {cancel_error_message}")
            cancel_message = response['message']
            logger.debug(f"Response of Cancel api, cancel_message value is : {cancel_message}")
            cancel_real_code = response['realCode']
            logger.debug(f"Response of Cancel api, cancel_real_code value is : {cancel_real_code}")
            cancel_success = response['success']
            logger.debug(f"Response of Cancel api, success value is : {cancel_success}")

            query = "select * from p2p_request where id = '" + str(start_p2p_request_id) + "';"
            logger.debug(f"Query to fetch p2p_request from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of p2p_request table is : {result}")
            status_db = result['status'].values[0]
            logger.debug(f"Query result of status_db : {status_db}")
            transaction_id_db = result['transactionId'].values[0]
            logger.debug(f"Query result of transaction_id_db : {transaction_id_db}")

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()

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
            expected_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
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
                    "success": cancel_success,
                    "error_message": cancel_error_message,
                    "message": cancel_message,
                    "real_code": cancel_real_code,
                    "error_code": cancel_error_code
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
                    "status": "RECEIVED",
                    "transaction_id": None,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "status": status_db,
                    "transaction_id": transaction_id_db
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
def test_500_503_050():
    """
    Sub Feature Code: UI_Common_P2P_Card_Cancel_API_Wrong_App_Key_50
    Sub Feature Description: Send cancel API for Card transaction request with wrong appkey in API request
    TC naming code description: 500: P2P, 503: P2P_Card, 050: TC050
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

        query = "select sett.setting_value from setting sett LEFT JOIN org_employee empl on empl.id=sett.entity_id where empl.username ='" + str(
            app_username) + "'and sett.setting_name='onlyP2PUser';"
        logger.debug(f"Query to fetch setting_value from the DB for the user {app_username}: {query}")
        result = DBProcessor.getValueFromDB(query)

        if (len(result)) >= 1:
            # If current app_user is onlyP2P allowed user
            current_setting_val = result['setting_value'].values[0]
            logger.debug(f"Query result, 'onlyP2PUser' setting_value of {app_username}: {current_setting_val}")
            if current_setting_val == "true":
                logger.info(f"Current app user is only P2P allowed user")
            else:
                logger.error(f"Current app user can do normal transactions as well")
        else:
            logger.error(f"Current app user can do normal transactions as well")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False,config_log=False)

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

            external_ref_num = random.randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            amount = random.randint(100, 200)
            logger.debug(f"amount random number is: {amount}")

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": str(amount),
                "paymentMode": "CARD",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": "" + device_serial + "|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_p2p_request_id = response['p2pRequestId']
            logger.debug(f"Response of Start api, start_p2p_request_id value is : {start_p2p_request_id}")
            sleep(2)

            # Pass wrong App_Key
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key[:2],
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Cancel api is : {response}")
            cancel_error_code = response['errorCode']
            logger.debug(f"Response of Cancel api, cancel_error_code value is : {cancel_error_code}")
            cancel_error_message = response['errorMessage']
            logger.debug(f"Response of Cancel api, cancel_error_message value is : {cancel_error_message}")
            cancel_message = response['message']
            logger.debug(f"Response of Cancel api, cancel_message value is : {cancel_message}")
            cancel_real_code = response['realCode']
            logger.debug(f"Response of Cancel api, cancel_real_code value is : {cancel_real_code}")
            cancel_success = response['success']
            logger.debug(f"Response of Cancel api, success value is : {cancel_success}")

            query = "select * from p2p_request where id = '" + str(start_p2p_request_id) + "';"
            logger.debug(f"Query to fetch p2p_request from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of p2p_request table is : {result}")
            status_db = result['status'].values[0]
            logger.debug(f"Query result of status_db : {status_db}")
            transaction_id_db = result['transactionId'].values[0]
            logger.debug(f"Query result of transaction_id_db : {transaction_id_db}")

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()

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
            expected_error_message = "Invalid credentials. Verify your credentials, login again, or contact your supervisor."
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
                    "success": cancel_success,
                    "error_message": cancel_error_message,
                    "message": cancel_message,
                    "real_code": cancel_real_code,
                    "error_code": cancel_error_code
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
                    "status": "RECEIVED",
                    "transaction_id": None,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "status": status_db,
                    "transaction_id": transaction_id_db
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
def test_500_503_051():
    """
    Sub Feature Code: UI_Common_P2P_Card_Cancel_API_Wrong_P2PID_51
    Sub Feature Description: Send cancel API for Card transaction request with wrong P2P ID in API request
    TC naming code description: 500: P2P, 503: P2P_Card, 051: TC051
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

        query = "select sett.setting_value from setting sett LEFT JOIN org_employee empl on empl.id=sett.entity_id where empl.username ='" + str(
            app_username) + "'and sett.setting_name='onlyP2PUser';"
        logger.debug(f"Query to fetch setting_value from the DB for the user {app_username}: {query}")
        result = DBProcessor.getValueFromDB(query)

        if (len(result)) >= 1:
            # If current app_user is onlyP2P allowed user
            current_setting_val = result['setting_value'].values[0]
            logger.debug(f"Query result, 'onlyP2PUser' setting_value of {app_username}: {current_setting_val}")
            if current_setting_val == "true":
                logger.info(f"Current app user is only P2P allowed user")
            else:
                logger.error(f"Current app user can do normal transactions as well")
        else:
            logger.error(f"Current app user can do normal transactions as well")


        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False,config_log=False)

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

            external_ref_num = random.randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            amount = random.randint(100, 200)
            logger.debug(f"amount random number is: {amount}")

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": str(amount),
                "paymentMode": "CARD",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": "" + device_serial + "|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_p2p_request_id = response['p2pRequestId']
            logger.debug(f"Response of Start api, start_p2p_request_id value is : {start_p2p_request_id}")
            sleep(2)

            # Pass wrong P2PID
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id[:2]
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Cancel api is : {response}")
            cancel_error_code = response['errorCode']
            logger.debug(f"Response of Cancel api, cancel_error_code value is : {cancel_error_code}")
            cancel_error_message = response['errorMessage']
            logger.debug(f"Response of Cancel api, cancel_error_message value is : {cancel_error_message}")
            cancel_message = response['message']
            logger.debug(f"Response of Cancel api, cancel_message value is : {cancel_message}")
            cancel_real_code = response['realCode']
            logger.debug(f"Response of Cancel api, cancel_real_code value is : {cancel_real_code}")
            cancel_success = response['success']
            logger.debug(f"Response of Cancel api, success value is : {cancel_success}")
            cancel_message_code = response['messageCode']
            logger.debug(f"Response of Cancel api, cancel_message_code value is : {cancel_message_code}")

            query = "select * from p2p_request where id = '" + str(start_p2p_request_id) + "';"
            logger.debug(f"Query to fetch p2p_request from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of p2p_request table is : {result}")
            status_db = result['status'].values[0]
            logger.debug(f"Query result of status_db : {status_db}")
            transaction_id_db = result['transactionId'].values[0]
            logger.debug(f"Query result of transaction_id_db : {transaction_id_db}")

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()

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
            expected_message_code = None
            expected_message = "EZETAP_0000604"
            expected_error_code = "EZETAP_0000604"
            expected_error_message = "EZETAP_0000604"
            expected_real_code = "P2P_ORIGINAL_REQUEST_NOT_FOUND_FOR_CANCEL"

            try:
                expected_api_values = {
                    "success": expected_success,
                    "error_message": expected_error_message,
                    "message": expected_message,
                    "real_code": expected_real_code,
                    "error_code": expected_error_code,
                    "message_code": expected_message_code
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": cancel_success,
                    "error_message": cancel_error_message,
                    "message": cancel_message,
                    "real_code": cancel_real_code,
                    "error_code": cancel_error_code,
                    "message_code": cancel_message_code
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
                    "status": "RECEIVED",
                    "transaction_id": None,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "status": status_db,
                    "transaction_id": transaction_id_db
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