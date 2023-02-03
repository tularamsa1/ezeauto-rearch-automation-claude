import random
import string
import sys
import pytest
from time import sleep
from Configuration import Configuration, testsuite_teardown, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, \
    APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_500_503_030():
    """
    Sub Feature Code: UI_common_P2P_Card_Queue_Status_API_30
    Sub Feature Description: Sending two notifications and check the status of second notification (Card) as in queue using status API
    TC naming code description: 500: P2P, 503: P2P_CARD, 030: TC 030
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "select * from app_key where org_code ='" + str(org_code) + "'"
        logger.debug(f"Query to fetch app_key from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        app_key = result['app_key'].values[0]
        logger.debug(f"Query result, app_key : {app_key}")

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
        logger.info(f"Query from terminal_info, device_serial : {device_serial}")
        logger.info(f"Query from terminal_info, mid : {mid}")
        logger.info(f"Query from terminal_info, tid : {tid}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQR')
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
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
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
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
            logger.info(f"Pulled notification bar for checking P2P notification")
            actual_notification = ""
            try:
                actual_notification = home_page.check_p2p_notification()
            except:
                logger.error(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
                logger.info(f"P2P notification message on device is : {actual_notification}")
                logger.info(f"P2P notification message on device is as expected")
            else:
                logger.error(f"Actual P2P notification message on device is : {actual_notification}")
                app_driver.back()
                raise Exception("P2P connection notification message mismatch on device")

            app_driver.back()

            # Start API for BQR
            amount_bqr = random.randint(401, 999)
            logger.info(f"Generated amount for BQR txn: {amount_bqr}")
            ext_ref_number_bqr = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number of BQR:  {ext_ref_number_bqr}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount_bqr,
                "externalRefNumber": ext_ref_number_bqr,
                "paymentMode": "BHARATQR",
                "pushTo": push_to
            })
            resp_start_bqr = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API for BQR is : {resp_start_bqr}")

            request_id_bqr = resp_start_bqr['p2pRequestId']
            start_success_bqr = resp_start_bqr['success']
            sleep(2)

            # Check status of BQR request after receiving to the device
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after BQR request received is : {resp_status_bqr}")

            status_received_success_bqr = resp_status_bqr['success']
            status_received_mssg_bqr = resp_status_bqr['message']
            status_received_mssgcode_bqr = resp_status_bqr['messageCode']
            status_received_realcode_bqr = resp_status_bqr['realCode']

            # Start API for CARD
            amount_card = random.randint(401, 999)
            logger.info(f"Generated amount for CARD txn: {amount_card}")
            ext_ref_number_card = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number of CARD:  {ext_ref_number_bqr}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount_card,
                "externalRefNumber": ext_ref_number_card,
                "paymentMode": "CARD",
                "pushTo": push_to
            })
            resp_start_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API for CARD is : {resp_start_card}")

            request_id_card = resp_start_card['p2pRequestId']
            start_success_card = resp_start_card['success']

            sleep(2)

            # Check status of CARD request which is in queue
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_status_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API of queued CARD : {resp_status_card}")

            status_queue_success = resp_status_card['success']
            status_queue_mssg = resp_status_card['message']
            status_queue_mssgcode = resp_status_card['messageCode']
            status_queue_realcode = resp_status_card['realCode']

            # Fetch values from DB table p2p_request after receiving BQR to device
            query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving BQR to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_bqr_1 = result['status'].values[0]

            # Fetch values from DB table p2p_request of queued CARD
            query = "select * from p2p_request where id='" + str(request_id_card) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request of queued CARD : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_card_1 = result['status'].values[0]

            payment_page = PaymentPage(app_driver)
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page for BQR")
            sleep(2)
            payment_page.click_on_proceed_homepage()
            sleep(2)

            # Cancel card pmt request
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_cancel_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P cancel API of card pmt request : {resp_cancel_card}")

            payment_page.click_on_cancel_p2p_request_ok()
            logger.debug("Clicked Ok on p2p transaction cancel for card payment")
            sleep(2)

            # Check status of request after canceling card txn using cancel API
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_status_card_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after canceling card txn using API is : {resp_status_card_1}")

            # Check status of request after payment of BQR
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after BQR payment is : {resp_status_bqr_1}")

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
                    # BQR txn details
                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",

                    # Queued CARD txn request status
                    "start_success_1": True,
                    "status_success_1": True,
                    "status_mssg_1": "P2P_STATUS_QUEUED",
                    "status_mssg_code_1": "P2P_STATUS_QUEUED",
                    "status_real_code_1": "P2P_STATUS_IN_QUEUE",
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                                     "start_success": start_success_bqr,
                                     "status_success": status_received_success_bqr,
                                     "status_mssg": status_received_mssg_bqr,
                                     "status_mssg_code": status_received_mssgcode_bqr,
                                     "status_real_code": status_received_realcode_bqr,

                                     "start_success_1": start_success_card,
                                     "status_success_1": status_queue_success,
                                     "status_mssg_1": status_queue_mssg,
                                     "status_mssg_code_1": status_queue_mssgcode,
                                     "status_real_code_1": status_queue_realcode,
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
                    "p2p_status_bqr": "RECEIVED",
                    "p2p_status_card": "QUEUED",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "p2p_status_bqr": db_p2p_request_status_bqr_1,
                    "p2p_status_card": db_p2p_request_status_card_1,
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
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_500_503_031():
    """
    Sub Feature Code: UI_Common_P2P_Card_Queue_Disabled_31
    Sub Feature Description: Send one BQR and card payment notifications using start API when Queue functionality is disabled and check status of both requests
    TC naming code description: 500: P2P, 503: P2P_CARD, 031: TC 031
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "select * from app_key where org_code ='" + str(org_code) + "'"
        logger.debug(f"Query to fetch app_key from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        app_key = result['app_key'].values[0]
        logger.debug(f"Query result, app_key : {app_key}")

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
        logger.info(f"Query from terminal_info, device_serial : {device_serial}")
        logger.info(f"Query from terminal_info, mid : {mid}")
        logger.info(f"Query from terminal_info, tid : {tid}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update p2p_setting set disable_queue=1 where org_code='" + str(org_code) + "';"
        logger.debug(f"Query to update queue as disabled in DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for DB refresh is : {response}")

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
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
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
            logger.info(f"Pulled notification bar for checking P2P notification")
            actual_notification = ""
            try:
                actual_notification = home_page.check_p2p_notification()
            except:
                logger.error(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
                logger.info(f"P2P notification message on device is : {actual_notification}")
                logger.info(f"P2P notification message on device is as expected")
            else:
                logger.error(f"Actual P2P notification message on device is : {actual_notification}")
                app_driver.back()
                raise Exception("P2P connection notification message mismatch on device")

            app_driver.back()

            # Start API for UPI
            amount_upi = random.randint(201, 300)
            logger.info(f"Generated amount: {amount_upi}")
            ext_ref_number_upi = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number of upi:  {ext_ref_number_upi}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount_upi,
                "externalRefNumber": ext_ref_number_upi,
                "paymentMode": "UPI",
                "pushTo": push_to
            })
            resp_start_upi = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API for UPI is : {resp_start_upi}")

            request_id_upi = resp_start_upi['p2pRequestId']
            start_success_upi = resp_start_upi['success']

            # Start API for CARD
            amount_card = random.randint(401, 999)
            logger.info(f"Generated amount for CARD: {amount_card}")
            ext_ref_number_card = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number of CARD:  {ext_ref_number_card}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount_card,
                "externalRefNumber": ext_ref_number_card,
                "paymentMode": "CARD",
                "pushTo": push_to
            })
            resp_start_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API for CARD is : {resp_start_card}")

            start_card_success = resp_start_card['success']
            start_card_mssg = resp_start_card['message']
            start_card_mssgcode = resp_start_card['messageCode']
            start_card_realcode = resp_start_card['realCode']
            start_card_error_code = resp_start_card['errorCode']
            start_card_error_mssg = resp_start_card['errorMessage']

            sleep(2)

            # Check status of UPI request after receiving to the device
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_upi
            })
            resp_status_upi = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after UPI request received is : {resp_status_upi}")

            status_received_success_upi = resp_status_upi['success']
            status_received_mssg_upi = resp_status_upi['message']
            status_received_mssgcode_upi = resp_status_upi['messageCode']
            status_received_realcode_upi = resp_status_upi['realCode']

            # Fetch values from DB table p2p_request after receiving UPI to device
            query = "select * from p2p_request where id='" + str(request_id_upi) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving UPI request to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_upi_1 = result['status'].values[0]

            payment_page = PaymentPage(app_driver)
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page for UPI txn")
            sleep(2)
            payment_page.click_on_proceed_homepage()

            # Check status of request after payment of UPI
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_upi
            })
            resp_status_upi_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after UPI payment is : {resp_status_upi_1}")

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
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",

                    "start_success_1": False,
                    "start_mssg_1": "Device is busy with pending notification.",
                    "start_mssg_code_1": None,
                    "start_error_code_1": "EZETAP_0000623",
                    "start_error_message_1": "Device is busy with pending notification.",
                    "start_real_code_1": "P2P_DEVICE_BUSY_WITH_PENDING_NOTIFICATION",
                }

                actual_api_values = {
                                     "start_success": start_success_upi,
                                     "status_success": status_received_success_upi,
                                     "status_mssg": status_received_mssg_upi,
                                     "status_mssg_code": status_received_mssgcode_upi,
                                     "status_real_code": status_received_realcode_upi,

                                     "start_success_1": start_card_success,
                                     "start_mssg_1": start_card_mssg,
                                     "start_mssg_code_1": start_card_mssgcode,
                                     "start_error_code_1": start_card_error_code,
                                     "start_error_message_1": start_card_error_mssg,
                                     "start_real_code_1": start_card_realcode,
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
@pytest.mark.dbVal
def test_500_503_034():
    """
    Sub Feature Code: UI_Common_P2P_Card_Queue_Cancel_First_Transaction_API_34
    Sub Feature Description: Cancel first notification among two queued notifications (second notification for Card) using cancel API from billing system
    TC naming code description: 500: P2P, 503: P2P_CARD, 034: TC 034
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "select * from app_key where org_code ='" + str(org_code) + "'"
        logger.debug(f"Query to fetch app_key from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        app_key = result['app_key'].values[0]
        logger.debug(f"Query result, app_key : {app_key}")

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
        logger.info(f"Query from terminal_info, device_serial : {device_serial}")
        logger.info(f"Query from terminal_info, mid : {mid}")
        logger.info(f"Query from terminal_info, tid : {tid}")

        # Get details from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)

        db_upi_config_id = result['id'].values[0]
        db_upi_config_mid = result['mid'].values[0]
        db_upi_config_tid = result['tid'].values[0]
        db_upi_terminal_info_id = result['terminal_info_id'].values[0]
        db_upi_vpa = result['vpa'].values[0]

        logger.info(f"from upi_merchant_config, config id is : {db_upi_config_id}")
        logger.info(f"from upi_merchant_config, mid is : {db_upi_config_mid}")
        logger.info(f"from upi_merchant_config, tid is : {db_upi_config_tid}")
        logger.info(f"from upi_merchant_config, terminal_info_id is : {db_upi_terminal_info_id}")
        logger.info(f"from upi_merchant_config, vpa is : {db_upi_vpa}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
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
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
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
            logger.info(f"Pulled notification bar for checking P2P notification")
            actual_notification = ""
            try:
                actual_notification = home_page.check_p2p_notification()
            except:
                logger.error(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
                logger.info(f"P2P notification message on device is : {actual_notification}")
                logger.info(f"P2P notification message on device is as expected")
            else:
                logger.error(f"Actual P2P notification message on device is : {actual_notification}")
                app_driver.back()
                raise Exception("P2P connection notification message mismatch on device")

            app_driver.back()

            # Start API for UPI
            amount_upi = random.randint(201, 300)
            logger.info(f"Generated amount for UPI txn: {amount_upi}")
            ext_ref_number_upi = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number of UPI:  {ext_ref_number_upi}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount_upi,
                "externalRefNumber": ext_ref_number_upi,
                "paymentMode": "UPI",
                "pushTo": push_to
            })
            resp_start_upi = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API for UPI is : {resp_start_upi}")

            request_id_upi = resp_start_upi['p2pRequestId']
            start_success_upi = resp_start_upi['success']
            sleep(2)

            # Check status of UPI request after receiving to the device
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_upi
            })
            resp_status_upi = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after UPI request received is : {resp_status_upi}")

            status_received_success_upi = resp_status_upi['success']
            status_received_mssg_upi = resp_status_upi['message']
            status_received_mssgcode_upi = resp_status_upi['messageCode']
            status_received_realcode_upi = resp_status_upi['realCode']

            # Start API for CARD
            amount_card = random.randint(401, 999)
            logger.info(f"Generated amount for Card txn: {amount_upi}")
            ext_ref_number_card = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number of CARD:  {ext_ref_number_card}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount_card,
                "externalRefNumber": ext_ref_number_card,
                "paymentMode": "CARD",
                "pushTo": push_to
            })
            resp_start_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API for CARD is : {resp_start_card}")

            request_id_card = resp_start_card['p2pRequestId']
            start_success_card = resp_start_card['success']

            sleep(2)

            # Check status of CARD request which is in queue
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_status_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API of queued CARD : {resp_status_card}")

            status_queue_success = resp_status_card['success']
            status_queue_mssg = resp_status_card['message']
            status_queue_mssgcode = resp_status_card['messageCode']
            status_queue_realcode = resp_status_card['realCode']

            # Fetch values from DB table p2p_request after receiving UPI to device
            query = "select * from p2p_request where id='" + str(request_id_upi) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving UPI to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_upi_1 = result['status'].values[0]

            # Fetch values from DB table p2p_request of queued CARD
            query = "select * from p2p_request where id='" + str(request_id_card) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request of queued CARD : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_card_1 = result['status'].values[0]
            sleep(2)

            # Cancel UPI pmt request
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_upi
            })
            resp_cancel_upi = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P cancel API of UPI pmt request : {resp_cancel_upi}")

            cancel_upi_success = resp_cancel_upi['success']
            cancel_upi_mssg = resp_cancel_upi['message']
            cancel_upi_errorcode = resp_cancel_upi['errorCode']
            cancel_upi_errormssg = resp_cancel_upi['errorMessage']
            cancel_upi_realcode = resp_cancel_upi['realCode']
            sleep(2)

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_proceed_homepage()
            sleep(2)

            # Cancel CARD pmt request
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_cancel_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P cancel API of CARD pmt request : {resp_cancel_card}")

            cancel_card_success = resp_cancel_card['success']
            logger.debug(f"Result of success of status API after canceling card payment using cancel API : {cancel_card_success}")

            sleep(2)
            payment_page.click_on_cancel_p2p_request_ok()
            logger.debug("Clicked Ok on p2p transaction cancel for card payment")

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
                    # UPI txn details
                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",

                    # Queued CARD txn request status
                    "start_success_1": True,
                    "status_success_1": True,
                    "status_mssg_1": "P2P_STATUS_QUEUED",
                    "status_mssg_code_1": "P2P_STATUS_QUEUED",
                    "status_real_code_1": "P2P_STATUS_IN_QUEUE",

                    # UPI txn cancel API
                    "cancel_upi_success": False,
                    "cancel_upi_mssg": "Transaction already initiated, cant initiate cancellation.",
                    "cancel_upi_errorcode": "EZETAP_0000610",
                    "cancel_upi_errormssg": "Transaction already initiated, cant initiate cancellation.",
                    "cancel_upi_realcode": "P2P_PAYMENT_INITIATED",

                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "start_success": start_success_upi,
                    "status_success": status_received_success_upi,
                    "status_mssg": status_received_mssg_upi,
                    "status_mssg_code": status_received_mssgcode_upi,
                    "status_real_code": status_received_realcode_upi,

                    "start_success_1": start_success_card,
                    "status_success_1": status_queue_success,
                    "status_mssg_1": status_queue_mssg,
                    "status_mssg_code_1": status_queue_mssgcode,
                    "status_real_code_1": status_queue_realcode,

                    # UPI txn cancel API
                    "cancel_upi_success": cancel_upi_success,
                    "cancel_upi_mssg": cancel_upi_mssg,
                    "cancel_upi_errorcode": cancel_upi_errorcode,
                    "cancel_upi_errormssg": cancel_upi_errormssg,
                    "cancel_upi_realcode": cancel_upi_realcode,
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
                    "p2p_status_upi_1": "RECEIVED",
                    "p2p_status_upi_2": "COMPLETED",

                    "p2p_status_card_1": "QUEUED",
                    "p2p_status_card_2": "CANCELED_FROM_EXTERNAL_SYSTEM"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from p2p_request where id='" + str(request_id_upi) + "';"
                logger.debug(f"Query to fetch UPI data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_upi_2 = result['status'].values[0]

                query = "select * from p2p_request where id='" + str(request_id_card) + "';"
                logger.debug(f"Query to fetch CARD data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_card_2 = result['status'].values[0]

                actual_db_values = {
                    "p2p_status_upi_1": db_p2p_request_status_upi_1,
                    "p2p_status_upi_2": db_p2p_request_status_upi_2,

                    "p2p_status_card_1": db_p2p_request_status_card_1,
                    "p2p_status_card_2": db_p2p_request_status_card_2,
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
        Configuration.executeFinallyBlock(testcase_id)