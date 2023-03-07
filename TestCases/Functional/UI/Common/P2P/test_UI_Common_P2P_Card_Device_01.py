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
def test_common_500_503_018():
    """
    Sub Feature Code: UI_Common_P2P_CARD_Reconnect_Network_Cancel_Transaction_Device_18
    Sub Feature Description: Turnoff network from device after receiving notification, cancel payment from device after network is back and check the status using status API
    TC naming code description: 500: P2P, 503: P2P_CARD, 018: TC018
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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id, "true")
            # logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            # login_page = LoginPage(app_driver)
            # login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"Logged in to the app")
            logger.info(f"Loaded home page")

            device_serial = GlobalVariables.str_device_id

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification")
            try:
                actual_notification = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.info(f"P2P notification message on device is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device. Actual notification: {actual_notification}")

            app_driver.back()

            external_ref_num = random.randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            amount = random.randint(100, 200)
            logger.debug(f"amount random number is: {amount}")

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount,
                "paymentMode": "CARD",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": ""+device_serial+"|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_success = response['success']
            logger.debug(f"Response of Start api, start_success is : {start_success}")
            start_p2p_request_id = response['p2pRequestId']
            logger.debug(f"Response of Start api, start_p2p_request_id value is : {start_p2p_request_id}")
            sleep(2)

            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Status api is : {response}")
            status_success = response['success']
            logger.debug(f"Response of Status api, success value is : {status_success}")
            status_message_code = response['messageCode']
            logger.debug(f"Response of Status api, status_message_code value is : {status_message_code}")
            status_message = response['message']
            logger.debug(f"Response of Status api, status_message value is : {status_message}")
            status_real_code = response['realCode']
            logger.debug(f"Response of Status api, status_real_code value is : {status_real_code}")

            query = "select * from p2p_request where id = '" + str(start_p2p_request_id) + "';"
            logger.debug(f"Query to fetch p2p_request from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of p2p_request table is : {result}")
            status_db = result['status'].values[0]
            logger.debug(f"Query result of status_db : {status_db}")
            transaction_id_db = result['transactionId'].values[0]
            logger.debug(f"Query result of transaction_id_db : {transaction_id_db}")

            #turn off the wifi
            app_driver.toggle_wifi()
            logger.debug(f"Turned off network")

            sleep(2)
            #turn on the wifi
            app_driver.toggle_wifi()
            logger.debug(f"Turned on network again")

            # Checking redis connection after wifi is turned on
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server after network reconnection")

            # Checking P2P notification after reconnecting wifi
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification after network reconnection")
            try:
                actual_notification2 = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device after network reconnection")
            logger.info(f"Expected P2P notification message after network reconnection is : {expected_notification}")

            if actual_notification2 == expected_notification:
                logger.info(f"P2P notification message on device after network reconnection is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device after network reconnection. Actual notification: {actual_notification2}")

            app_driver.back()

            sleep(2)

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            sleep(2)

            #check DB and status api after txn cancelled
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"After cancellation response obtained for Status api is : {response}")
            status_success_2 = response['success']
            logger.debug(f"After cancellation response obtained for Status api, status_success_2 is : {status_success_2}")
            status_message_code_2 = response['messageCode']
            logger.debug(f"After cancellation response obtained for Status api, status_message_code_2 is : {status_message_code_2}")
            status_message_2 = response['message']
            logger.debug(f"After cancellation response obtained for Status api, status_message_2 is : {status_message_2}")
            status_real_code_2 = response['realCode']
            logger.debug(f"After cancellation response obtained for Status api, status_real_code_2 is : {status_real_code_2}")
            status_username_2 = response['username']
            logger.debug(f"After cancellation response obtained for Status api, status_username_2 is : {status_username_2}")
            status_p2p_request_id_2 = response['p2pRequestId']
            logger.debug(f"After cancellation response obtained for Status api, status_p2p_request_id_2 is : {status_p2p_request_id_2}")

            query = "select * from p2p_request where id = '" + str(start_p2p_request_id) + "';"
            logger.debug(f"Query to fetch after cancellation from p2p_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of after cancellation from p2p_request table is : {result}")
            status_db_2 = result['status'].values[0]
            logger.debug(f"Query result of after cancellation from p2p_request table, status_db_2 is : {status_db_2}")
            transaction_id_db_2 = result['transactionId'].values[0]
            logger.debug(f"Query result of after cancellation from p2p_request table, transaction_id_db_2 is : {transaction_id_db_2}")

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
                    "start_success": True,
                    "status_success": True,
                    "status_msg": "Notification has been received on POS Device.",
                    "status_msg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",
                    "status_success_2": True,
                    "status_msg_code_2": "P2P_DEVICE_CANCELED",
                    "status_real_code_2": "P2P_DEVICE_CANCELED",
                    "status_msg_2": "PushToPay Notification has been Canceled on Receiving device.",
                    "status_username_2": app_username,
                    "status_req_id_2": start_p2p_request_id,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "start_success": start_success,
                    "status_success": status_success,
                    "status_msg": status_message,
                    "status_msg_code": status_message_code,
                    "status_real_code": status_real_code,
                    "status_success_2": status_success_2,
                    "status_msg_code_2": status_message_code_2,
                    "status_real_code_2": status_real_code_2,
                    "status_msg_2": status_message_2,
                    "status_username_2": status_username_2,
                    "status_req_id_2": status_p2p_request_id_2,
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")

            try:
                expected_db_values = {
                    "p2p_status": "RECEIVED",
                    "p2p_txn_id": transaction_id_db,
                    "p2p_status_2": "CANCELED",
                    "p2p_txn_id_2": None,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from p2p_request where id='" + str(start_p2p_request_id) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result['status'].values[0]
                status_txn_id_2 = result['transactionId'].values[0]

                actual_db_values = {
                    "p2p_status": status_db,
                    "p2p_txn_id": transaction_id_db_2,
                    "p2p_status_2": status_db_2,
                    "p2p_txn_id_2": status_txn_id_2,
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
def test_common_500_503_019():
    """
    Sub Feature Code: UI_Common_P2P_CARD_Reconnect_Network_Cancel_Transaction_API_19
    Sub Feature Description: Turnoff network from device after receiving notification, cancel payment using cancel API after network is back and check the status using status API
    TC naming code description: 500: P2P, 503: P2P_CARD, 019: TC019
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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id, "true")
            # logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            # login_page = LoginPage(app_driver)
            # login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"Logged in to the app")
            logger.info(f"Loaded home page")

            device_serial = GlobalVariables.str_device_id

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification")
            try:
                actual_notification = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.info(f"P2P notification message on device is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device. Actual notification: {actual_notification}")

            app_driver.back()

            external_ref_num = random.randint(0, 10 ** 5)
            logger.debug(f"externalRefNum random number is: {external_ref_num}")

            amount = random.randint(100, 200)
            logger.debug(f"amount random number is: {amount}")

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount,
                "paymentMode": "CARD",
                "externalRefNumber": str(external_ref_num),
                "pushTo": {"deviceId": ""+device_serial+"|ezetap_android"}
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Start api is : {response}")
            start_success = response['success']
            logger.debug(f"Response of Start api, start_success is : {start_success}")
            start_p2p_request_id = response['p2pRequestId']
            logger.debug(f"Response of Start api, start_p2p_request_id value is : {start_p2p_request_id}")

            sleep(2)

            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of obtained for Status api is : {response}")
            status_success = response['success']
            logger.debug(f"Response of Status api, success value is : {status_success}")
            status_message_code = response['messageCode']
            logger.debug(f"Response of Status api, status_message_code value is : {status_message_code}")
            status_message = response['message']
            logger.debug(f"Response of Status api, status_message value is : {status_message}")
            status_real_code = response['realCode']
            logger.debug(f"Response of Status api, status_real_code value is : {status_real_code}")

            query = "select * from p2p_request where id = '" + str(start_p2p_request_id) + "';"
            logger.debug(f"Query to fetch p2p_request from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of p2p_request table is : {result}")
            status_db = result['status'].values[0]
            logger.debug(f"Query result of status_db : {status_db}")
            transaction_id_db = result['transactionId'].values[0]
            logger.debug(f"Query result of transaction_id_db : {transaction_id_db}")

            #turn off the wifi
            app_driver.toggle_wifi()
            logger.debug(f"Turned off network")

            sleep(2)
            #turn on the wifi
            app_driver.toggle_wifi()
            logger.debug(f"Turned on network again")

            # Checking redis connection after wifi is turned on
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server after network reconnection")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification after network reconnection")
            try:
                actual_notification2 = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device after network reconnection")

            logger.info(f"Expected P2P notification message after network reconnection is : {expected_notification}")

            if actual_notification2 == expected_notification:
                logger.info(f"P2P notification message on device after network reconnection is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device after network reconnection. Actual notification: {actual_notification2}")

            app_driver.back()

            sleep(2)

            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
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
            cancel_message_code = response['messageCode']
            logger.debug(f"Response of Cancel api, cancel_message_code value is : {cancel_message_code}")
            sleep(2)

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_cancel_p2p_request_ok()

            #check DB and status api after txn cancelled using API
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"After Cancelling, response obtained for Status api is : {response}")
            status_success_2 = response['success']
            logger.debug(f"After Cancelling, response obtained for Status api, status_success_2 is : {status_success_2}")
            status_message_code_2 = response['messageCode']
            logger.debug(f"After Cancelling, response obtained for Status api, status_message_code_2 is : {status_message_code_2}")
            status_message_2 = response['message']
            logger.debug(f"After Cancelling, response obtained for Status api, status_message_2 is : {status_message_2}")
            status_real_code_2 = response['realCode']
            logger.debug(f"After Cancelling, response obtained for Status api, status_real_code_2 is : {status_real_code_2}")
            status_username_2 = response['username']
            logger.debug(f"After Cancelling, response obtained for Status api, status_username_2 is : {status_username_2}")
            status_p2p_request_id_2 = response['p2pRequestId']
            logger.debug(f"After Cancelling, response obtained for Status api, status_p2p_request_id_2 is : {status_p2p_request_id_2}")

            query = "select * from p2p_request where id = '" + str(start_p2p_request_id) + "';"
            logger.debug(f"Query to fetch after txn from p2p_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of after txn from p2p_request table is : {result}")
            status_db_2 = result['status'].values[0]
            logger.debug(f"Query result of after txn from p2p_request table, status_db_2 is : {status_db_2}")
            transaction_id_db_2 = result['transactionId'].values[0]
            logger.debug(f"Query result of after txn from p2p_request table, transaction_id_db_2 is : {transaction_id_db_2}")

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
                    "start_success": True,
                    "status_success": True,
                    "status_msg": "Notification has been received on POS Device.",
                    "status_msg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",
                    "status_success_2": True,
                    "status_msg_code_2": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "status_real_code_2": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "status_msg_2": "PushToPay Notification has been Canceled from Billing/External System.",
                    "status_username_2": app_username,
                    "status_req_id_2": start_p2p_request_id,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "start_success": start_success,
                    "status_success": status_success,
                    "status_msg": status_message,
                    "status_msg_code": status_message_code,
                    "status_real_code": status_real_code,
                    "status_success_2": status_success_2,
                    "status_msg_code_2": status_message_code_2,
                    "status_real_code_2": status_real_code_2,
                    "status_msg_2": status_message_2,
                    "status_username_2": status_username_2,
                    "status_req_id_2": status_p2p_request_id_2,
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")

            try:
                expected_db_values = {
                    "p2p_status": "RECEIVED",
                    "p2p_txn_id": transaction_id_db,
                    "p2p_status_2": "CANCELED_FROM_EXTERNAL_SYSTEM",
                    "p2p_txn_id_2": None,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from p2p_request where id='" + str(start_p2p_request_id) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result['status'].values[0]
                status_txn_id_2 = result['transactionId'].values[0]

                actual_db_values = {
                    "p2p_status": status_db,
                    "p2p_txn_id": transaction_id_db_2,
                    "p2p_status_2": status_db_2,
                    "p2p_txn_id_2": status_txn_id_2,
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