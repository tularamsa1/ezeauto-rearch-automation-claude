import pytest
import random
import string
import sys
from time import sleep
from Configuration import Configuration, testsuite_teardown, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, \
    APIProcessor, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_500_503_004():
    """
    Sub Feature Code: UI_Common_P2P_Card_Start_API_Cancel_From_Device_04
    Sub Feature Description: Send notification for card, cancel the payment from device and check the status using API
    TC naming code description: 500: P2P, 503: P2P_BQR, 004: TC 004
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
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
        logger.info(f"Query from terminal_info, mid : {mid}")
        logger.info(f"Query from terminal_info, tid : {tid}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CARD')
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

            amount = random.randint(401, 999)
            logger.info(f"Generated amount: {amount}")
            ext_ref_number = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number:  {ext_ref_number}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount,
                "paymentMode": "CARD",
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start}")

            request_id = resp_start['p2pRequestId']
            start_success = resp_start['success']

            sleep(2)

            # Check status of request after receiving to the device
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            resp_status_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after request received is : {resp_status_1}")

            status_received_success = resp_status_1['success']
            status_received_mssg = resp_status_1['message']
            status_received_mssgcode = resp_status_1['messageCode']
            status_received_realcode = resp_status_1['realCode']

            # Fetch values from DB table p2p_request after receiving to device
            query = "select * from p2p_request where id='" + str(request_id) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status = result['status'].values[0]
            db_p2p_request_txn_id = result['transactionId'].values[0]

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            sleep(2)

            # Check status of request after cancel payment
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            resp_status_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after cancelling card txn payment is : {resp_status_2}")

            status_after_pmt_success = resp_status_2['success']
            status_after_pmt_mssgcode = resp_status_2['messageCode']
            status_after_pmt_mssg = resp_status_2['message']
            status_after_pmt_realcode = resp_status_2['realCode']
            status_after_pmt_username = resp_status_2['username']

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
                    "status_success_1": True,
                    "status_mssg_code_1": "P2P_DEVICE_CANCELED",
                    "status_real_code_1": "P2P_DEVICE_CANCELED",
                    "status_mssg_1": "PushToPay Notification has been Canceled on Receiving device.",
                    "status_username_1": app_username
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                                     "start_success": start_success,
                                     "status_success": status_received_success,
                                     "status_mssg": status_received_mssg,
                                     "status_mssg_code": status_received_mssgcode,
                                     "status_real_code": status_received_realcode,
                                     "status_success_1": status_after_pmt_success,
                                     "status_mssg_code_1": status_after_pmt_mssgcode,
                                     "status_real_code_1": status_after_pmt_realcode,
                                     "status_mssg_1": status_after_pmt_mssg,
                                     "status_username_1": status_after_pmt_username
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
                    "p2p_status": "RECEIVED",
                    "p2p_txn_id": None,
                    "p2p_status_1": "CANCELED",
                    "p2p_txn_id_1": None
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from p2p_request where id='" + str(request_id) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_1 = result['status'].values[0]
                db_p2p_request_txn_id_1 = result['transactionId'].values[0]

                actual_db_values = {
                    "p2p_status": db_p2p_request_status,
                    "p2p_txn_id": db_p2p_request_txn_id,
                    "p2p_status_1": db_p2p_request_status_1,
                    "p2p_txn_id_1": db_p2p_request_txn_id_1,
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
@pytest.mark.dbVal
def test_common_500_503_037():
    """
    Sub Feature Code: UI_Common_P2P_Card_Cancel_API_37
    Sub Feature Description: Sending payment notification with payment mode as Card in start API and cancel the notification using cancel API and do status API
    TC naming code description: 500: P2P, 503: P2P_CARD, 037: TC 037
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
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
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

            # Start API for CARD
            amount_card = random.randint(401, 999)
            logger.info(f"Generated amount for card txn: {amount_card}")
            ext_ref_number_card = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number of card:  {ext_ref_number_card}")
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
            logger.debug(f"Response received for P2P start API for card is : {resp_start_card}")

            request_id_card = resp_start_card['p2pRequestId']
            start_success_card = resp_start_card['success']
            sleep(2)

            # Check status of card request after receiving to the device
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_status_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after card request received is : {resp_status_card}")

            status_received_success_card = resp_status_card['success']
            status_received_mssg_card = resp_status_card['message']
            status_received_mssgcode_card = resp_status_card['messageCode']
            status_received_realcode_card = resp_status_card['realCode']

            # Cancel card pmt request
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_cancel_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P cancel API of card pmt request : {resp_cancel_card}")

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_cancel_p2p_request_ok()
            logger.debug("Clicked Ok for p2p transaction cancel for card payment")
            sleep(2)

            # Check status of request after canceling card txn using cancel API
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_status_card_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after canceling card txn using API is : {resp_status_card_1}")

            status_after_cancel_success_card = resp_status_card_1['success']
            status_after_cancel_mssgcode_card = resp_status_card_1['messageCode']
            status_after_cancel_mssg_card = resp_status_card_1['message']
            status_after_cancel_realcode_card = resp_status_card_1['realCode']
            status_after_cancel_username_card = resp_status_card_1['username']
            status_after_cancel_rqst_id_card = resp_status_card_1['p2pRequestId']

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
                    # Card txn details
                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",

                    # Card txn cancel API
                    "status_success_2": True,
                    "status_mssg_code_2": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "status_real_code_2": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "status_mssg_2": "PushToPay Notification has been Canceled from Billing/External System.",
                    "status_username_2": app_username,
                    "status_req_id_2": request_id_card,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "start_success": start_success_card,
                    "status_success": status_received_success_card,
                    "status_mssg": status_received_mssg_card,
                    "status_mssg_code": status_received_mssgcode_card,
                    "status_real_code": status_received_realcode_card,

                    "status_success_2": status_after_cancel_success_card,
                    "status_mssg_code_2": status_after_cancel_mssgcode_card,
                    "status_real_code_2": status_after_cancel_realcode_card,
                    "status_mssg_2": status_after_cancel_mssg_card,
                    "status_username_2": status_after_cancel_username_card,
                    "status_req_id_2": status_after_cancel_rqst_id_card,
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
                    "p2p_status_card_2": "CANCELED_FROM_EXTERNAL_SYSTEM",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from p2p_request where id='" + str(request_id_card) + "';"
                logger.debug(f"Query to fetch card data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_card_2 = result['status'].values[0]

                actual_db_values = {
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