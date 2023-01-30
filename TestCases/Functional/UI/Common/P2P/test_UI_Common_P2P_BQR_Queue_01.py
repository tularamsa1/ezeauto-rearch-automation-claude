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
from PageFactory.PAX_TransHistoryPage import PaxTransHistoryPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, \
    APIProcessor, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_500_502_025():
    """
    Sub Feature Code: UI_common_P2P_BQR_Queue_Status_API_25
    Sub Feature Description: Sending two notifications and check the status of second notification (BQR) as in queue using status API
    TC naming code description: 500: P2P, 502: P2P_BQR, 025: TC 025
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

        # Get details from bharatqr_merchant_config table
        query = "select * from bharatqr_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)

        db_bqr_config_id = result['id'].values[0]
        db_bqr_config_mid = result['mid'].values[0]
        db_bqr_config_tid = result['tid'].values[0]
        db_bqr_terminal_info_id = result['terminal_info_id'].values[0]
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]

        logger.info(f"from bharatqr_merchant_config, config id is : {db_bqr_config_id}")
        logger.info(f"from bharatqr_merchant_config, mid is : {db_bqr_config_mid}")
        logger.info(f"from bharatqr_merchant_config, tid is : {db_bqr_config_tid}")
        logger.info(f"from bharatqr_merchant_config, terminal_info_id is : {db_bqr_terminal_info_id}")
        logger.info(f"from bharatqr_merchant_config, merchant_pan is : {db_bqr_config_merchant_pan}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

            app_driver.back()

            # Start API for UPI
            amount_upi = random.randint(201, 300)
            logger.info(f"Generated amount for UPI: {amount_upi}")
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

            # Start API for BQR
            amount_bqr = random.randint(401, 1000)
            logger.info(f"Generated amount for BQR: {amount_bqr}")
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

            # Check status of BQR request which is in queue
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API of queued BQR : {resp_status_bqr}")

            status_queue_success = resp_status_bqr['success']
            status_queue_mssg = resp_status_bqr['message']
            status_queue_mssgcode = resp_status_bqr['messageCode']
            status_queue_realcode = resp_status_bqr['realCode']

            # Fetch values from DB table p2p_request of queued BQR
            query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request of queued BQR : {query}")
            result_bqr_DB = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetch queued BQR request data from p2p_request table : {result_bqr_DB}")
            db_p2p_request_status_bqr_1 = result_bqr_DB['status'].values[0]

            payment_page = PaymentPage(app_driver)
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully for UPI")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page for UPI")
            sleep(2)
            payment_page.click_on_proceed_homepage()

            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully for BQR")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page for BQR")
            sleep(2)
            payment_page.click_on_proceed_homepage()

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
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",

                    "start_success_1": True,
                    "status_success_1": True,
                    "status_mssg_1": "P2P_STATUS_QUEUED",
                    "status_mssg_code_1": "P2P_STATUS_QUEUED",
                    "status_real_code_1": "P2P_STATUS_IN_QUEUE",
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                                     "status_success": status_received_success_upi,
                                     "status_mssg": status_received_mssg_upi,
                                     "status_mssg_code": status_received_mssgcode_upi,
                                     "status_real_code": status_received_realcode_upi,

                                     "start_success_1": start_success_bqr,
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
                    "p2p_status_bqr": "QUEUED",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "p2p_status_bqr": db_p2p_request_status_bqr_1,
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
@pytest.mark.appVal
def test_500_501_026():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Queue_Disabled_26
    Sub Feature Description: Send two notifications (second notification of BQR) when Queue functionality is disabled
    TC naming code description: 500: P2P, 502: P2P_BQR, 026: TC 026
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

        query = "update p2p_setting set disable_queue=1 where org_code='" + str(org_code) + "';"
        logger.debug(f"Query to update queue as disabled in DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for DB refresh is : {response}")

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
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

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

            # Start API for BQR
            amount_bqr = random.randint(401, 1000)
            logger.info(f"Generated amount for BQR: {amount_bqr}")
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

            start_bqr_success = resp_start_bqr['success']
            start_bqr_mssg = resp_start_bqr['message']
            start_bqr_mssgcode = resp_start_bqr['messageCode']
            start_bqr_realcode = resp_start_bqr['realCode']
            start_bqr_error_code = resp_start_bqr['errorCode']
            start_bqr_error_mssg = resp_start_bqr['errorMessage']

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

            status_after_pmt_success_upi = resp_status_upi_1['success']
            status_after_pmt_mssgcode_upi = resp_status_upi_1['messageCode']
            status_after_pmt_mssg_upi = resp_status_upi_1['message']
            status_after_pmt_realcode_upi = resp_status_upi_1['realCode']
            status_after_pmt_username_upi = resp_status_upi_1['username']
            status_after_pmt_rqst_id_upi = resp_status_upi_1['p2pRequestId']
            txn_id_upi = resp_status_upi_1['txnId']
            logger.debug(f"Transaction ID of UPI payment: {txn_id_upi}")

            # Fetch values from DB table txn after payment of UPI
            query = "select * from txn where id='" + str(txn_id_upi) + "';"
            logger.debug(f"Query to fetch details from DB table txn after UPI payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time_upi = result['created_time'].values[0]

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
            date_and_time_upi = date_time_converter.to_app_format(txn_created_time_upi)
            # date_and_time_upi = date_time_converter.to_app_format(txn_created_time_upi)
            try:
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount_upi) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id_upi,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time_upi,
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                pax_txn_history_page = PaxTransHistoryPage(app_driver)
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number_upi)

                payment_status_upi = pax_txn_history_page.fetch_txn_status_text()
                payment_mode_upi = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id_upi = pax_txn_history_page.fetch_txn_id_text()
                app_amount_upi = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status_upi = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg_upi = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time_upi = pax_txn_history_page.fetch_date_time_text()

                actual_app_values = {
                    "pmt_mode": payment_mode_upi,
                    "pmt_status": payment_status_upi.split(':')[1],
                    "txn_amt": app_amount_upi.split(' ')[1],
                    "txn_id": app_txn_id_upi,
                    "settle_status": app_settlement_status_upi,
                    "pmt_msg": app_payment_msg_upi,
                    "date": app_date_and_time_upi,
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            date_upi = date_time_converter.db_datetime(txn_created_time_upi)
            try:
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount_upi),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date_upi,
                    #----------------------------------
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
                    #-------------------------------------------
                    "status_success_2": True,
                    "status_mssg_code_2": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_2": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_2": "Transaction done on device, Please look at Txn status.",
                    "status_username_2": app_username,
                    "status_req_id_2": request_id_upi,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                response_api_upi = [x for x in response["txns"] if x["txnId"] == txn_id_upi][0]
                logger.debug(f"Response after filtering data of UPI txn is : {response_api_upi}")

                status_api_upi = response_api_upi["status"]
                amount_api_upi = float(response_api_upi["amount"])
                payment_mode_api_upi = response_api_upi["paymentMode"]
                state_api_upi = response_api_upi["states"][0]
                settlement_status_api_upi = response_api_upi["settlementStatus"]
                issuer_code_api_upi = response_api_upi["issuerCode"]
                acquirer_code_api_upi = response_api_upi["acquirerCode"]
                org_code_api_upi = response_api_upi["orgCode"]
                mid_api_upi = response_api_upi["mid"]
                tid_api_upi = response_api_upi["tid"]
                txn_type_api_upi = response_api_upi["txnType"]
                date_api_upi = response_api_upi["createdTime"]

                actual_api_values = {"pmt_status": status_api_upi,
                                     "txn_amt": amount_api_upi,
                                     "pmt_mode": payment_mode_api_upi,
                                     "pmt_state": state_api_upi,
                                     "settle_status": settlement_status_api_upi,
                                     "acquirer_code": acquirer_code_api_upi,
                                     "issuer_code": issuer_code_api_upi,
                                     "mid": mid_api_upi,
                                     "txn_type": txn_type_api_upi,
                                     "tid": tid_api_upi,
                                     "org_code": org_code_api_upi,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api_upi),
                                     # --------------------------------------------------
                                     "start_success": start_success_upi,
                                     "status_success": status_received_success_upi,
                                     "status_mssg": status_received_mssg_upi,
                                     "status_mssg_code": status_received_mssgcode_upi,
                                     "status_real_code": status_received_realcode_upi,

                                     "start_success_1": start_bqr_success,
                                     "start_mssg_1": start_bqr_mssg,
                                     "start_mssg_code_1": start_bqr_mssgcode,
                                     "start_error_code_1": start_bqr_error_code,
                                     "start_error_message_1": start_bqr_error_mssg,
                                     "start_real_code_1": start_bqr_realcode,
                                    # ----------------------------------------------------
                                     "status_success_2": status_after_pmt_success_upi,
                                     "status_mssg_code_2": status_after_pmt_mssgcode_upi,
                                     "status_real_code_2": status_after_pmt_realcode_upi,
                                     "status_mssg_2": status_after_pmt_mssg_upi,
                                     "status_username_2": status_after_pmt_username_upi,
                                     "status_req_id_2": status_after_pmt_rqst_id_upi,
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
                    "txn_amt": float(amount_upi),
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "settle_status": "SETTLED",
                    "txn_type": "CHARGE",

                    "upi_txn_status": "AUTHORIZED",
                    "upi_bank_code": "HDFC",
                    "upi_txn_type": "PAY_QR",
                    "upi_upi_mc_id": db_upi_config_id,
                    "upi_org_code": org_code,

                    "p2p_status_upi_1": "RECEIVED",
                    "p2p_status_upi_2": "COMPLETED",
                    "p2p_txn_id_upi": txn_id_upi,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id_upi + "'"
                logger.debug(f"Query to fetch UPI txn data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                amount_db_upi = int(result["amount"].iloc[0])
                payment_status_db_upi = result["status"].iloc[0]
                payment_state_db_upi = result["state"].iloc[0]
                payment_mode_db_upi = result["payment_mode"].iloc[0]
                acquirer_code_db_upi = result["acquirer_code"].iloc[0]
                bank_code_db_upi = result["bank_code"].iloc[0]
                payment_gateway_db_upi = result["payment_gateway"].iloc[0]
                mid_db_upi = result["mid"].iloc[0]
                tid_db_upi= result["tid"].iloc[0]
                settlement_status_db_upi = result["settlement_status"].iloc[0]
                txn_type_db_upi = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_upi + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                upi_txn_status_db = result["status"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_org_code_db = result["org_code"].iloc[0]

                query = "select * from p2p_request where id='" + str(request_id_upi) + "';"
                logger.debug(f"Query to fetch UPI data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_upi_2 = result['status'].values[0]
                db_p2p_request_txn_id_upi = result['transactionId'].values[0]

                actual_db_values = {
                    "txn_amt": amount_db_upi,
                    "pmt_status": payment_status_db_upi,
                    "pmt_state": payment_state_db_upi,
                    "pmt_mode": payment_mode_db_upi,
                    "acquirer_code": acquirer_code_db_upi,
                    "bank_code": bank_code_db_upi,
                    "payment_gateway": payment_gateway_db_upi,
                    "mid": mid_db_upi,
                    "tid": tid_db_upi,
                    "settle_status": settlement_status_db_upi,
                    "txn_type": txn_type_db_upi,
                    #---------------------------
                    "upi_txn_status": upi_txn_status_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_upi_mc_id": upi_upi_mc_id_db,
                    "upi_org_code": upi_org_code_db,
                    # -------------------------------------------------------
                    "p2p_status_upi_1": db_p2p_request_status_upi_1,
                    "p2p_status_upi_2": db_p2p_request_status_upi_2,
                    "p2p_txn_id_upi": db_p2p_request_txn_id_upi
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
@pytest.mark.appVal
def test_500_502_027():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Queue_Success_Transactions_27
    Sub Feature Description: Send one UPI and BQR transactions and confirm both transactions where BQR transaction was in queue
    TC naming code description: 500: P2P, 502: P2P_BQR, 027: TC 027
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

        # Get details from bharatqr_merchant_config table
        query = "select * from bharatqr_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)

        db_bqr_config_id = result['id'].values[0]
        db_bqr_config_mid = result['mid'].values[0]
        db_bqr_config_tid = result['tid'].values[0]
        db_bqr_terminal_info_id = result['terminal_info_id'].values[0]
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]

        logger.info(f"from bharatqr_merchant_config, config id is : {db_bqr_config_id}")
        logger.info(f"from bharatqr_merchant_config, mid is : {db_bqr_config_mid}")
        logger.info(f"from bharatqr_merchant_config, tid is : {db_bqr_config_tid}")
        logger.info(f"from bharatqr_merchant_config, terminal_info_id is : {db_bqr_terminal_info_id}")
        logger.info(f"from bharatqr_merchant_config, merchant_pan is : {db_bqr_config_merchant_pan}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

            app_driver.back()

            # Start API for UPI
            amount_upi = random.randint(201, 300)
            logger.info(f"Generated amount for UPI: {amount_upi}")
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

            # Start API for BQR
            amount_bqr = random.randint(401, 1000)
            logger.info(f"Generated amount for BQR: {amount_bqr}")
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

            # Check status of BQR request which is in queue
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API of queued BQR : {resp_status_bqr}")

            status_queue_success = resp_status_bqr['success']
            status_queue_mssg = resp_status_bqr['message']
            status_queue_mssgcode = resp_status_bqr['messageCode']
            status_queue_realcode = resp_status_bqr['realCode']

            # Fetch values from DB table p2p_request after receiving UPI to device
            query = "select * from p2p_request where id='" + str(request_id_upi) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving UPI to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetch UPI request data from p2p_request table after receiving to device: {result}")
            db_p2p_request_status_upi_1 = result['status'].values[0]

            # Fetch values from DB table p2p_request of queued BQR
            query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request of queued BQR : {query}")
            result_bqr_DB = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetch queued BQR request data from p2p_request table : {result_bqr_DB}")
            db_p2p_request_status_bqr_1 = result_bqr_DB['status'].values[0]

            payment_page = PaymentPage(app_driver)
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully for UPI")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page for UPI")
            sleep(2)
            payment_page.click_on_proceed_homepage()

            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully for BQR")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page for BQR")
            sleep(2)
            payment_page.click_on_proceed_homepage()

            sleep(2)

            # Check status of request after payment of UPI
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_upi
            })
            resp_status_upi_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after UPI payment is : {resp_status_upi_1}")

            status_after_pmt_success_upi = resp_status_upi_1['success']
            status_after_pmt_mssgcode_upi = resp_status_upi_1['messageCode']
            status_after_pmt_mssg_upi = resp_status_upi_1['message']
            status_after_pmt_realcode_upi = resp_status_upi_1['realCode']
            status_after_pmt_username_upi = resp_status_upi_1['username']
            status_after_pmt_rqst_id_upi = resp_status_upi_1['p2pRequestId']
            txn_id_upi = resp_status_upi_1['txnId']
            logger.debug(f"Transaction ID of UPI payment: {txn_id_upi}")

            # Fetch values from DB table txn after payment of UPI
            query = "select * from txn where id='" + str(txn_id_upi) + "';"
            logger.debug(f"Query to fetch details from DB table txn after UPI payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time_upi = result['created_time'].values[0]

            # Check status of request after payment of BQR
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after BQR payment is : {resp_status_bqr_1}")

            status_after_pmt_success_bqr = resp_status_bqr_1['success']
            status_after_pmt_mssgcode_bqr = resp_status_bqr_1['messageCode']
            status_after_pmt_mssg_bqr = resp_status_bqr_1['message']
            status_after_pmt_realcode_bqr = resp_status_bqr_1['realCode']
            status_after_pmt_username_bqr = resp_status_bqr_1['username']
            status_after_pmt_rqst_id_bqr = resp_status_bqr_1['p2pRequestId']
            txn_id_bqr = resp_status_bqr_1['txnId']
            logger.debug(f"Transaction ID of BQR payment: {txn_id_bqr}")

            # Fetch values from DB table txn after payment of BQR
            query = "select * from txn where id='" + str(txn_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table txn after BQR payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time_bqr = result['created_time'].values[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            logger.debug(f"status of BQR request : {resp_status_bqr}")
            logger.debug(f"status of queued UPI : {resp_status_upi}")
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
            date_and_time_upi = date_time_converter.to_app_format(txn_created_time_upi)
            date_and_time_bqr = date_time_converter.to_app_format(txn_created_time_bqr)
            try:
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount_upi) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id_upi,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time_upi,

                    "pmt_mode_1": "BHARAT QR",
                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": str(amount_bqr) + ".00",
                    "settle_status_1": "SETTLED",
                    "txn_id_1": txn_id_bqr,
                    "pmt_msg_1": "PAYMENT SUCCESSFUL",
                    "date_1": date_and_time_bqr
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                pax_txn_history_page = PaxTransHistoryPage(app_driver)
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number_upi)

                payment_status_upi = pax_txn_history_page.fetch_txn_status_text()
                payment_mode_upi = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id_upi = pax_txn_history_page.fetch_txn_id_text()
                app_amount_upi = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status_upi = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg_upi = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time_upi = pax_txn_history_page.fetch_date_time_text()

                pax_txn_history_page.click_back_Btn_transaction_details()
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number_bqr)
                payment_status_bqr = pax_txn_history_page.fetch_txn_status_text()
                payment_mode_bqr = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id_bqr = pax_txn_history_page.fetch_txn_id_text()
                app_amount_bqr = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status_bqr = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg_bqr = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time_bqr = pax_txn_history_page.fetch_date_time_text()

                actual_app_values = {
                    "pmt_mode": payment_mode_upi,
                    "pmt_status": payment_status_upi.split(':')[1],
                    "txn_amt": app_amount_upi.split(' ')[1],
                    "txn_id": app_txn_id_upi,
                    "settle_status": app_settlement_status_upi,
                    "pmt_msg": app_payment_msg_upi,
                    "date": app_date_and_time_upi,

                    "pmt_mode_1": payment_mode_bqr,
                    "pmt_status_1": payment_status_bqr.split(':')[1],
                    "txn_amt_1": app_amount_bqr.split(' ')[1],
                    "txn_id_1": app_txn_id_bqr,
                    "settle_status_1": app_settlement_status_bqr,
                    "pmt_msg_1": app_payment_msg_bqr,
                    "date_1": app_date_and_time_bqr
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            date_upi = date_time_converter.db_datetime(txn_created_time_upi)
            date_bqr = date_time_converter.db_datetime(txn_created_time_bqr)

            try:
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount_upi),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date_upi,

                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": float(amount_bqr),
                    "pmt_mode_1": "BHARATQR",
                    "pmt_state_1": "SETTLED",
                    "settle_status_1": "SETTLED",
                    "acquirer_code_1": "HDFC",
                    "issuer_code_1": "HDFC",
                    "txn_type_1": "CHARGE",
                    "mid_1": db_bqr_config_mid,
                    "tid_1": db_bqr_config_tid,
                    "org_code_1": org_code,
                    "date_1": date_bqr,
                    #----------------------------------
                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",

                    "start_success_1": True,
                    "status_success_1": True,
                    "status_mssg_1": "P2P_STATUS_QUEUED",
                    "status_mssg_code_1": "P2P_STATUS_QUEUED",
                    "status_real_code_1": "P2P_STATUS_IN_QUEUE",
                    #-------------------------------------------
                    "status_success_2": True,
                    "status_mssg_code_2": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_2": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_2": "Transaction done on device, Please look at Txn status.",
                    "status_username_2": app_username,
                    "status_req_id_2": request_id_upi,

                    "status_success_3": True,
                    "status_mssg_code_3": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_3": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_3": "Transaction done on device, Please look at Txn status.",
                    "status_username_3": app_username,
                    "status_req_id_3": request_id_bqr,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                response_api_upi = [x for x in response["txns"] if x["txnId"] == txn_id_upi][0]
                logger.debug(f"Response after filtering data of UPI txn is : {response_api_upi}")

                status_api_upi = response_api_upi["status"]
                amount_api_upi = float(response_api_upi["amount"])
                payment_mode_api_upi = response_api_upi["paymentMode"]
                state_api_upi = response_api_upi["states"][0]
                settlement_status_api_upi = response_api_upi["settlementStatus"]
                issuer_code_api_upi = response_api_upi["issuerCode"]
                acquirer_code_api_upi = response_api_upi["acquirerCode"]
                org_code_api_upi = response_api_upi["orgCode"]
                mid_api_upi = response_api_upi["mid"]
                tid_api_upi = response_api_upi["tid"]
                txn_type_api_upi = response_api_upi["txnType"]
                date_api_upi = response_api_upi["createdTime"]

                response_api_bqr = [x for x in response["txns"] if x["txnId"] == txn_id_bqr][0]
                logger.debug(f"Response after filtering data of BQR txn is : {response_api_bqr}")

                status_api_bqr = response_api_bqr["status"]
                amount_api_bqr = float(response_api_bqr["amount"])
                payment_mode_api_bqr = response_api_bqr["paymentMode"]
                state_api_bqr = response_api_bqr["states"][0]
                settlement_status_api_bqr = response_api_bqr["settlementStatus"]
                issuer_code_api_bqr = response_api_bqr["issuerCode"]
                acquirer_code_api_bqr = response_api_bqr["acquirerCode"]
                org_code_api_bqr = response_api_bqr["orgCode"]
                mid_api_bqr = response_api_bqr["mid"]
                tid_api_bqr = response_api_bqr["tid"]
                txn_type_api_bqr = response_api_bqr["txnType"]
                date_api_bqr = response_api_bqr["createdTime"]

                # -------------------------------------------------------


                actual_api_values = {"pmt_status": status_api_upi,
                                     "txn_amt": amount_api_upi,
                                     "pmt_mode": payment_mode_api_upi,
                                     "pmt_state": state_api_upi,
                                     "settle_status": settlement_status_api_upi,
                                     "acquirer_code": acquirer_code_api_upi,
                                     "issuer_code": issuer_code_api_upi,
                                     "mid": mid_api_upi,
                                     "txn_type": txn_type_api_upi,
                                     "tid": tid_api_upi,
                                     "org_code": org_code_api_upi,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api_upi),

                                     "pmt_status_1": status_api_bqr,
                                     "txn_amt_1": amount_api_bqr,
                                     "pmt_mode_1": payment_mode_api_bqr,
                                     "pmt_state_1": state_api_bqr,
                                     "settle_status_1": settlement_status_api_bqr,
                                     "acquirer_code_1": acquirer_code_api_bqr,
                                     "issuer_code_1": issuer_code_api_bqr,
                                     "mid_1": mid_api_bqr,
                                     "txn_type_1": txn_type_api_bqr,
                                     "tid_1": tid_api_bqr,
                                     "org_code_1": org_code_api_bqr,
                                     "date_1": date_time_converter.from_api_to_datetime_format(date_api_bqr),
                                     # --------------------------------------------------
                                     "start_success": start_success_upi,
                                     "status_success": status_received_success_upi,
                                     "status_mssg": status_received_mssg_upi,
                                     "status_mssg_code": status_received_mssgcode_upi,
                                     "status_real_code": status_received_realcode_upi,

                                     "start_success_1": start_success_bqr,
                                     "status_success_1": status_queue_success,
                                     "status_mssg_1": status_queue_mssg,
                                     "status_mssg_code_1": status_queue_mssgcode,
                                     "status_real_code_1": status_queue_realcode,

                                    # ----------------------------------------------------
                                     "status_success_2": status_after_pmt_success_upi,
                                     "status_mssg_code_2": status_after_pmt_mssgcode_upi,
                                     "status_real_code_2": status_after_pmt_realcode_upi,
                                     "status_mssg_2": status_after_pmt_mssg_upi,
                                     "status_username_2": status_after_pmt_username_upi,
                                     "status_req_id_2": status_after_pmt_rqst_id_upi,

                                     "status_success_3": status_after_pmt_success_bqr,
                                     "status_mssg_code_3": status_after_pmt_mssgcode_bqr,
                                     "status_real_code_3": status_after_pmt_realcode_bqr,
                                     "status_mssg_3": status_after_pmt_mssg_bqr,
                                     "status_username_3": status_after_pmt_username_bqr,
                                     "status_req_id_3": status_after_pmt_rqst_id_bqr,
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
                    "txn_amt": float(amount_upi),
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "settle_status": "SETTLED",
                    "txn_type": "CHARGE",

                    "txn_amt_1": float(amount_bqr),
                    "pmt_status_1": "AUTHORIZED",
                    "pmt_state_1": "SETTLED",
                    "pmt_mode_1": "BHARATQR",
                    "acquirer_code_1": "HDFC",
                    "bank_code_1": "HDFC",
                    "payment_gateway_1": "HDFC",
                    "mid_1": db_bqr_config_mid,
                    "tid_1": db_bqr_config_tid,
                    "settle_status_1": "SETTLED",
                    "txn_type_1": "CHARGE",

                    "upi_txn_status": "AUTHORIZED",
                    "upi_bank_code": "HDFC",
                    "upi_txn_type": "PAY_QR",
                    "upi_upi_mc_id": db_upi_config_id,
                    "upi_org_code": org_code,

                    "bqr_pmt_status": "Transaction Success",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount_bqr,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": db_bqr_terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": db_bqr_config_id,
                    "bqr_txn_primary_id": txn_id_bqr,
                    "bqr_merchant_pan": db_bqr_config_merchant_pan,
                    "bqr_org_code": org_code,

                    "p2p_status_upi_1": "RECEIVED",
                    "p2p_status_upi_2": "COMPLETED",

                    "p2p_status_bqr_1": "QUEUED",
                    "p2p_status_bqr_2": "COMPLETED",
                    "p2p_txn_id_upi": txn_id_upi,
                    "p2p_txn_id_1_bqr": txn_id_bqr

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id_upi + "'"
                logger.debug(f"Query to fetch BQR txn data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                amount_db_upi = int(result["amount"].iloc[0])
                payment_status_db_upi = result["status"].iloc[0]
                payment_state_db_upi = result["state"].iloc[0]
                payment_mode_db_upi = result["payment_mode"].iloc[0]
                acquirer_code_db_upi = result["acquirer_code"].iloc[0]
                bank_code_db_upi = result["bank_code"].iloc[0]
                payment_gateway_db_upi = result["payment_gateway"].iloc[0]
                mid_db_upi = result["mid"].iloc[0]
                tid_db_upi = result["tid"].iloc[0]
                settlement_status_db_upi = result["settlement_status"].iloc[0]
                txn_type_db_upi = result["txn_type"].iloc[0]

                query = "select * from txn where id='" + txn_id_bqr + "'"
                logger.debug(f"Query to fetch BQR txn data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                amount_db_bqr = int(result["amount"].iloc[0])
                payment_status_db_bqr = result["status"].iloc[0]
                payment_state_db_bqr = result["state"].iloc[0]
                payment_mode_db_bqr = result["payment_mode"].iloc[0]
                acquirer_code_db_bqr = result["acquirer_code"].iloc[0]
                bank_code_db_bqr = result["bank_code"].iloc[0]
                payment_gateway_db_bqr = result["payment_gateway"].iloc[0]
                mid_db_bqr = result["mid"].iloc[0]
                tid_db_bqr= result["tid"].iloc[0]
                settlement_status_db_bqr = result["settlement_status"].iloc[0]
                txn_type_db_bqr = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_upi + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                upi_txn_status_db = result["status"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_org_code_db = result["org_code"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id_bqr + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = int(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from p2p_request where id='" + str(request_id_upi) + "';"
                logger.debug(f"Query to fetch UPI data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_upi_2 = result['status'].values[0]
                db_p2p_request_txn_id_upi = result['transactionId'].values[0]

                query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
                logger.debug(f"Query to fetch BQR data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_bqr_2 = result['status'].values[0]
                db_p2p_request_txn_id_bqr = result['transactionId'].values[0]

                actual_db_values = {
                    "txn_amt": amount_db_upi,
                    "pmt_status": payment_status_db_upi,
                    "pmt_state": payment_state_db_upi,
                    "pmt_mode": payment_mode_db_upi,
                    "acquirer_code": acquirer_code_db_upi,
                    "bank_code": bank_code_db_upi,
                    "payment_gateway": payment_gateway_db_upi,
                    "mid": mid_db_upi,
                    "tid": tid_db_upi,
                    "settle_status": settlement_status_db_upi,
                    "txn_type": txn_type_db_upi,

                    "txn_amt_1": amount_db_bqr,
                    "pmt_status_1": payment_status_db_bqr,
                    "pmt_state_1": payment_state_db_bqr,
                    "pmt_mode_1": payment_mode_db_bqr,
                    "acquirer_code_1": acquirer_code_db_bqr,
                    "bank_code_1": bank_code_db_bqr,
                    "payment_gateway_1": payment_gateway_db_bqr,
                    "mid_1": mid_db_bqr,
                    "tid_1": tid_db_bqr,
                    "settle_status_1": settlement_status_db_bqr,
                    "txn_type_1": txn_type_db_bqr,
                    #---------------------------
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_org_code": bqr_org_code_db,

                    "upi_txn_status": upi_txn_status_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_upi_mc_id": upi_upi_mc_id_db,
                    "upi_org_code": upi_org_code_db,
                    # -------------------------------------------------------
                    "p2p_status_upi_1": db_p2p_request_status_upi_1,
                    "p2p_status_upi_2": db_p2p_request_status_upi_2,

                    "p2p_status_bqr_1": db_p2p_request_status_bqr_1,
                    "p2p_status_bqr_2": db_p2p_request_status_bqr_2,
                    "p2p_txn_id_upi": db_p2p_request_txn_id_upi,
                    "p2p_txn_id_1_bqr": db_p2p_request_txn_id_bqr
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
@pytest.mark.appVal
def test_500_502_028():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Queue_Cancel_First_Transaction_Device_28
    Sub Feature Description: Push Card and BQR notifications and first cancel Card txn from device, then confirm success BQR txn which was in queue
    TC naming code description: 500: P2P, 502: P2P_BQR, 028: TC 028
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

        # Get details from bharatqr_merchant_config table
        query = "select * from bharatqr_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)

        db_bqr_config_id = result['id'].values[0]
        db_bqr_config_mid = result['mid'].values[0]
        db_bqr_config_tid = result['tid'].values[0]
        db_bqr_terminal_info_id = result['terminal_info_id'].values[0]
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]

        logger.info(f"from bharatqr_merchant_config, config id is : {db_bqr_config_id}")
        logger.info(f"from bharatqr_merchant_config, mid is : {db_bqr_config_mid}")
        logger.info(f"from bharatqr_merchant_config, tid is : {db_bqr_config_tid}")
        logger.info(f"from bharatqr_merchant_config, terminal_info_id is : {db_bqr_terminal_info_id}")
        logger.info(f"from bharatqr_merchant_config, merchant_pan is : {db_bqr_config_merchant_pan}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQR')
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

            app_driver.back()

            # Start API for CARD
            amount_card = random.randint(401, 1000)
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

            # Start API for BQR
            amount_bqr = random.randint(401, 1000)
            logger.info(f"Generated amount for BQR: {amount_bqr}")
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

            # Check status of BQR request which is in queue
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API of queued BQR : {resp_status_bqr}")

            status_queue_success = resp_status_bqr['success']
            status_queue_mssg = resp_status_bqr['message']
            status_queue_mssgcode = resp_status_bqr['messageCode']
            status_queue_realcode = resp_status_bqr['realCode']

            # Fetch values from DB table p2p_request after receiving card to device
            query = "select * from p2p_request where id='" + str(request_id_card) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving card to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_card_1 = result['status'].values[0]

            # Fetch values from DB table p2p_request of queued BQR
            query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request of queued BQR : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_bqr_1 = result['status'].values[0]

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page for card payment")
            sleep(2)

            # pmt_status = payment_page.is_qrcode_displayed()
            # logger.info(f"Checked for QR code display")
            # logger.debug(f"Payment status of last txn : {pmt_status}")
            #
            # if pmt_status == "Payment Successful":
            #     pass
            # elif pmt_status == "Payment Failed":
            #     payment_page.perform_click(payment_page.btn_proceedToHomepage)
            # elif pmt_status == "Payment Pending":
            #     payment_page.perform_click(payment_page.btn_proceedToHomepage)
            #     payment_page.perform_click(payment_page.lbl_skip)
            # elif pmt_status == "":
            #     logger.info(f"Payment status : {pmt_status}")
            # else:
            #     payment_page.validate_upi_bqr_payment_screen()
            #     logger.info("Payment QR generated and displayed successfully")
            #     payment_page.click_on_back_btn()
            #     payment_page.click_on_transaction_cancel_yes()
            #     logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            #     sleep(2)
            #     payment_page.click_on_proceed_homepage()

            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            sleep(2)
            payment_page.click_on_proceed_homepage()

            sleep(2)

            # Check status of request after canceling card txn from device
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_status_card_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after canceling card from device is : {resp_status_card_1}")

            status_after_cancel_success_card = resp_status_card_1['success']
            status_after_cancel_mssgcode_card = resp_status_card_1['messageCode']
            status_after_cancel_mssg_card = resp_status_card_1['message']
            status_after_cancel_realcode_card = resp_status_card_1['realCode']
            status_after_cancel_username_card = resp_status_card_1['username']
            status_after_cancel_rqst_id_card = resp_status_card_1['p2pRequestId']

            # Check status of request after payment of BQR
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after BQR payment is : {resp_status_bqr_1}")

            status_after_pmt_success_bqr = resp_status_bqr_1['success']
            status_after_pmt_mssgcode_bqr = resp_status_bqr_1['messageCode']
            status_after_pmt_mssg_bqr = resp_status_bqr_1['message']
            status_after_pmt_realcode_bqr = resp_status_bqr_1['realCode']
            status_after_pmt_username_bqr = resp_status_bqr_1['username']
            status_after_pmt_rqst_id_bqr = resp_status_bqr_1['p2pRequestId']
            txn_id_bqr = resp_status_bqr_1['txnId']
            logger.debug(f"Transaction ID of BQR payment: {txn_id_bqr}")

            # Fetch values from DB table txn after payment of BQR
            query = "select * from txn where id='" + str(txn_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table txn after BQR payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time_bqr = result['created_time'].values[0]

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
            date_and_time_bqr = date_time_converter.to_app_format(txn_created_time_bqr)
            try:
                expected_app_values = {
                    "pmt_mode_1": "BHARAT QR",
                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": str(amount_bqr) + ".00",
                    "settle_status_1": "SETTLED",
                    "txn_id_1": txn_id_bqr,
                    "pmt_msg_1": "PAYMENT SUCCESSFUL",
                    "date_1": date_and_time_bqr
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                pax_txn_history_page = PaxTransHistoryPage(app_driver)
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number_bqr)
                payment_status_bqr = pax_txn_history_page.fetch_txn_status_text()
                payment_mode_bqr = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id_bqr = pax_txn_history_page.fetch_txn_id_text()
                app_amount_bqr = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status_bqr = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg_bqr = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time_bqr = pax_txn_history_page.fetch_date_time_text()

                actual_app_values = {
                    "pmt_mode_1": payment_mode_bqr,
                    "pmt_status_1": payment_status_bqr.split(':')[1],
                    "txn_amt_1": app_amount_bqr.split(' ')[1],
                    "txn_id_1": app_txn_id_bqr,
                    "settle_status_1": app_settlement_status_bqr,
                    "pmt_msg_1": app_payment_msg_bqr,
                    "date_1": app_date_and_time_bqr
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            date_bqr = date_time_converter.db_datetime(txn_created_time_bqr)
            try:
                expected_api_values = {
                    # UPI txn details
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount_bqr),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "org_code": org_code,
                    "date": date_bqr,

                    # Card txn details
                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",

                    # BQR txn
                    "start_success_1": True,
                    "status_success_1": True,
                    "status_mssg_1": "P2P_STATUS_QUEUED",
                    "status_mssg_code_1": "P2P_STATUS_QUEUED",
                    "status_real_code_1": "P2P_STATUS_IN_QUEUE",

                    # Card txn cancel
                    "status_success_2": True,
                    "status_mssg_code_2": "P2P_DEVICE_CANCELED",
                    "status_real_code_2": "P2P_DEVICE_CANCELED",
                    "status_mssg_2": "PushToPay Notification has been Canceled on Receiving device.",
                    "status_username_2": app_username,
                    "status_req_id_2": request_id_card,

                    # BQR txn success
                    "status_success_3": True,
                    "status_mssg_code_3": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_3": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_3": "Transaction done on device, Please look at Txn status.",
                    "status_username_3": app_username,
                    "status_req_id_3": request_id_bqr,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                response_api_bqr = [x for x in response["txns"] if x["txnId"] == txn_id_bqr][0]
                logger.debug(f"Response after filtering data of BQR txn is : {response_api_bqr}")

                status_api_bqr = response_api_bqr["status"]
                amount_api_bqr = float(response_api_bqr["amount"])
                payment_mode_api_bqr = response_api_bqr["paymentMode"]
                state_api_bqr = response_api_bqr["states"][0]
                settlement_status_api_bqr = response_api_bqr["settlementStatus"]
                issuer_code_api_bqr = response_api_bqr["issuerCode"]
                acquirer_code_api_bqr = response_api_bqr["acquirerCode"]
                org_code_api_bqr = response_api_bqr["orgCode"]
                mid_api_bqr = response_api_bqr["mid"]
                tid_api_bqr = response_api_bqr["tid"]
                txn_type_api_bqr = response_api_bqr["txnType"]
                date_api_bqr = response_api_bqr["createdTime"]

                actual_api_values = {
                                     "pmt_status": status_api_bqr,
                                     "txn_amt": amount_api_bqr,
                                     "pmt_mode": payment_mode_api_bqr,
                                     "pmt_state": state_api_bqr,
                                     "settle_status": settlement_status_api_bqr,
                                     "acquirer_code": acquirer_code_api_bqr,
                                     "issuer_code": issuer_code_api_bqr,
                                     "mid": mid_api_bqr,
                                     "txn_type": txn_type_api_bqr,
                                     "tid": tid_api_bqr,
                                     "org_code": org_code_api_bqr,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api_bqr),
                                     # --------------------------------------------------
                                     "start_success": start_success_card,
                                     "status_success": status_received_success_card,
                                     "status_mssg": status_received_mssg_card,
                                     "status_mssg_code": status_received_mssgcode_card,
                                     "status_real_code": status_received_realcode_card,

                                     "start_success_1": start_success_bqr,
                                     "status_success_1": status_queue_success,
                                     "status_mssg_1": status_queue_mssg,
                                     "status_mssg_code_1": status_queue_mssgcode,
                                     "status_real_code_1": status_queue_realcode,
                                    # ----------------------------------------------------
                                     "status_success_2": status_after_cancel_success_card,
                                     "status_mssg_code_2": status_after_cancel_mssgcode_card,
                                     "status_real_code_2": status_after_cancel_realcode_card,
                                     "status_mssg_2": status_after_cancel_mssg_card,
                                     "status_username_2": status_after_cancel_username_card,
                                     "status_req_id_2": status_after_cancel_rqst_id_card,

                                     "status_success_3": status_after_pmt_success_bqr,
                                     "status_mssg_code_3": status_after_pmt_mssgcode_bqr,
                                     "status_real_code_3": status_after_pmt_realcode_bqr,
                                     "status_mssg_3": status_after_pmt_mssg_bqr,
                                     "status_username_3": status_after_pmt_username_bqr,
                                     "status_req_id_3": status_after_pmt_rqst_id_bqr,
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
                    "txn_amt": float(amount_bqr),
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "BHARATQR",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "settle_status": "SETTLED",
                    "txn_type": "CHARGE",

                    "bqr_pmt_status": "Transaction Success",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount_bqr,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": db_bqr_terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": db_bqr_config_id,
                    "bqr_txn_primary_id": txn_id_bqr,
                    "bqr_merchant_pan": db_bqr_config_merchant_pan,
                    "bqr_org_code": org_code,

                    "p2p_status_card_1": "RECEIVED",
                    "p2p_status_card_2": "CANCELED",

                    "p2p_status_upi_1": "QUEUED",
                    "p2p_status_upi_2": "COMPLETED",
                    "p2p_txn_id_1_upi": txn_id_bqr

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id_bqr + "'"
                logger.debug(f"Query to fetch BQR txn data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                amount_db_bqr = int(result["amount"].iloc[0])
                payment_status_db_bqr = result["status"].iloc[0]
                payment_state_db_bqr = result["state"].iloc[0]
                payment_mode_db_bqr = result["payment_mode"].iloc[0]
                acquirer_code_db_bqr = result["acquirer_code"].iloc[0]
                bank_code_db_bqr = result["bank_code"].iloc[0]
                payment_gateway_db_bqr = result["payment_gateway"].iloc[0]
                mid_db_bqr = result["mid"].iloc[0]
                tid_db_bqr = result["tid"].iloc[0]
                settlement_status_db_bqr = result["settlement_status"].iloc[0]
                txn_type_db_bqr = result["txn_type"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id_bqr + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = int(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from p2p_request where id='" + str(request_id_card) + "';"
                logger.debug(f"Query to fetch card data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_card_2 = result['status'].values[0]

                query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
                logger.debug(f"Query to fetch BQR data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_bqr_2 = result['status'].values[0]
                db_p2p_request_txn_id_bqr = result['transactionId'].values[0]

                actual_db_values = {
                    "txn_amt": amount_db_bqr,
                    "pmt_status": payment_status_db_bqr,
                    "pmt_state": payment_state_db_bqr,
                    "pmt_mode": payment_mode_db_bqr,
                    "acquirer_code": acquirer_code_db_bqr,
                    "bank_code": bank_code_db_bqr,
                    "payment_gateway": payment_gateway_db_bqr,
                    "mid": mid_db_bqr,
                    "tid": tid_db_bqr,
                    "settle_status": settlement_status_db_bqr,
                    "txn_type": txn_type_db_bqr,
                    #---------------------------
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_org_code": bqr_org_code_db,
                    # -------------------------------------------------------
                    "p2p_status_card_1": db_p2p_request_status_card_1,
                    "p2p_status_card_2": db_p2p_request_status_card_2,

                    "p2p_status_bqr_1": db_p2p_request_status_bqr_1,
                    "p2p_status_bqr_2": db_p2p_request_status_bqr_2,
                    "p2p_txn_id_1_bqr": db_p2p_request_txn_id_bqr
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
@pytest.mark.appVal
def test_500_502_029():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Queue_Cancel_First_Transaction_API_29
    Sub Feature Description: Cancel first notification among two queued notifications (second notification for BQR) using cancel API from billing system
    TC naming code description: 500: P2P, 502: P2P_BQR, 029: TC 029
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

        query = "select id from org_employee where username ='" + str(app_username) + "'"
        logger.debug(f"Query to fetch user id from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        user_id = result['id'].values[0]
        logger.debug(f"Query result, user id : {user_id}")

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

        # Get details from bharatqr_merchant_config table
        query = "select * from bharatqr_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)

        db_bqr_config_id = result['id'].values[0]
        db_bqr_config_mid = result['mid'].values[0]
        db_bqr_config_tid = result['tid'].values[0]
        db_bqr_terminal_info_id = result['terminal_info_id'].values[0]
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]

        logger.info(f"from bharatqr_merchant_config, config id is : {db_bqr_config_id}")
        logger.info(f"from bharatqr_merchant_config, mid is : {db_bqr_config_mid}")
        logger.info(f"from bharatqr_merchant_config, tid is : {db_bqr_config_tid}")
        logger.info(f"from bharatqr_merchant_config, terminal_info_id is : {db_bqr_terminal_info_id}")
        logger.info(f"from bharatqr_merchant_config, merchant_pan is : {db_bqr_config_merchant_pan}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQR')
        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
            logger.info(f"Pulled notification bar")

            actual_notification = home_page.check_p2p_notification()

            expected_notification = "Push 2 Pay is ON"
            if actual_notification == expected_notification:
                logger.debug(f"Located the P2P connection notification")
            else:
                logger.error(f"Could not find P2P connection notification on device")
                raise Exception("Could not find P2P connection notification on device")

            app_driver.back()

            # Start API for CARD
            amount_card = random.randint(401, 1000)
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

            # Start API for BQR
            amount_bqr = random.randint(401, 1000)
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

            # Check status of BQR request which is in queue
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API of queued BQR : {resp_status_bqr}")

            status_queue_success = resp_status_bqr['success']
            status_queue_mssg = resp_status_bqr['message']
            status_queue_mssgcode = resp_status_bqr['messageCode']
            status_queue_realcode = resp_status_bqr['realCode']

            # Fetch values from DB table p2p_request after receiving card to device
            query = "select * from p2p_request where id='" + str(request_id_card) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving card to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_card_1 = result['status'].values[0]

            # Fetch values from DB table p2p_request of queued BQR
            query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request of queued BQR : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_bqr_1 = result['status'].values[0]

            # Cancel card pmt request
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_card
            })
            resp_cancel_card = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P cancel API of card pmt request : {resp_cancel_card}")

            cancel_card_success = resp_cancel_card['success']
            cancel_card_mssg = resp_cancel_card['message']
            cancel_card_mssgcode = resp_cancel_card['messageCode']
            cancel_card_realcode = resp_cancel_card['realCode']

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_cancel_p2p_request_ok()
            logger.debug("Clicked Ok on p2p transaction cancel for card payment")
            sleep(2)

            # pmt_status = payment_page.is_qrcode_displayed()
            # logger.info(f"Checked for QR code display")
            # logger.debug(f"Payment status of last txn : {pmt_status}")
            #
            # if pmt_status == "Payment Successful":
            #     pass
            # elif pmt_status == "Payment Failed":
            #     payment_page.perform_click(payment_page.btn_proceedToHomepage)
            # elif pmt_status == "Payment Pending":
            #     payment_page.perform_click(payment_page.btn_proceedToHomepage)
            #     payment_page.perform_click(payment_page.lbl_skip)
            # elif pmt_status == "":
            #     logger.info(f"Payment status : {pmt_status}")
            # else:
            #     payment_page.validate_upi_bqr_payment_screen()
            #     logger.info("Payment QR generated and displayed successfully")
            #     payment_page.click_on_back_btn()
            #     payment_page.click_on_transaction_cancel_yes()
            #     logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            #     sleep(2)
            #     payment_page.click_on_proceed_homepage()

            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            sleep(2)
            payment_page.click_on_proceed_homepage()

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

            # Check status of request after payment of BQR
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after BQR payment is : {resp_status_bqr_1}")

            status_after_pmt_success_bqr = resp_status_bqr_1['success']
            status_after_pmt_mssgcode_bqr = resp_status_bqr_1['messageCode']
            status_after_pmt_mssg_bqr = resp_status_bqr_1['message']
            status_after_pmt_realcode_bqr = resp_status_bqr_1['realCode']
            status_after_pmt_username_bqr = resp_status_bqr_1['username']
            status_after_pmt_rqst_id_bqr = resp_status_bqr_1['p2pRequestId']
            txn_id_bqr = resp_status_bqr_1['txnId']
            logger.debug(f"Transaction ID of BQR payment: {txn_id_bqr}")

            # Fetch values from DB table txn after payment of BQR
            query = "select * from txn where id='" + str(txn_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table txn after BQR payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time_bqr = result['created_time'].values[0]

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
            date_and_time_bqr = date_time_converter.to_app_format(txn_created_time_bqr)
            try:
                expected_app_values = {
                    "pmt_mode_1": "BHARAT QR",
                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": str(amount_bqr) + ".00",
                    "settle_status_1": "SETTLED",
                    "txn_id_1": txn_id_bqr,
                    "pmt_msg_1": "PAYMENT SUCCESSFUL",
                    "date_1": date_and_time_bqr
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                pax_txn_history_page = PaxTransHistoryPage(app_driver)
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number_bqr)
                payment_status_bqr = pax_txn_history_page.fetch_txn_status_text()
                payment_mode_bqr = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id_bqr = pax_txn_history_page.fetch_txn_id_text()
                app_amount_bqr = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status_bqr = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg_bqr = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time_bqr = pax_txn_history_page.fetch_date_time_text()

                actual_app_values = {
                    "pmt_mode_1": payment_mode_bqr,
                    "pmt_status_1": payment_status_bqr.split(':')[1],
                    "txn_amt_1": app_amount_bqr.split(' ')[1],
                    "txn_id_1": app_txn_id_bqr,
                    "settle_status_1": app_settlement_status_bqr,
                    "pmt_msg_1": app_payment_msg_bqr,
                    "date_1": app_date_and_time_bqr
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            date_bqr = date_time_converter.db_datetime(txn_created_time_bqr)
            try:
                expected_api_values = {
                    # UPI txn details
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount_bqr),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "org_code": org_code,
                    "date": date_bqr,

                    # Card txn details
                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",

                    # Queued BQR txn request status
                    "start_success_1": True,
                    "status_success_1": True,
                    "status_mssg_1": "P2P_STATUS_QUEUED",
                    "status_mssg_code_1": "P2P_STATUS_QUEUED",
                    "status_real_code_1": "P2P_STATUS_IN_QUEUE",

                    # Card txn cancel API
                    "status_success_2": True,
                    "status_mssg_code_2": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "status_real_code_2": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "status_mssg_2": "PushToPay Notification has been Canceled from Billing/External System.",
                    "status_username_2": app_username,
                    "status_req_id_2": request_id_card,

                    # success BQR txn status
                    "status_success_3": True,
                    "status_mssg_code_3": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_3": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_3": "Transaction done on device, Please look at Txn status.",
                    "status_username_3": app_username,
                    "status_req_id_3": request_id_bqr,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                response_api_bqr = [x for x in response["txns"] if x["txnId"] == txn_id_bqr][0]
                logger.debug(f"Response after filtering data of BQR txn is : {response_api_bqr}")

                status_api_bqr = response_api_bqr["status"]
                amount_api_bqr = float(response_api_bqr["amount"])
                payment_mode_api_bqr = response_api_bqr["paymentMode"]
                state_api_bqr = response_api_bqr["states"][0]
                settlement_status_api_bqr = response_api_bqr["settlementStatus"]
                issuer_code_api_bqr = response_api_bqr["issuerCode"]
                acquirer_code_api_bqr = response_api_bqr["acquirerCode"]
                org_code_api_bqr = response_api_bqr["orgCode"]
                mid_api_bqr = response_api_bqr["mid"]
                tid_api_bqr = response_api_bqr["tid"]
                txn_type_api_bqr = response_api_bqr["txnType"]
                date_api_bqr = response_api_bqr["createdTime"]

                actual_api_values = {
                                     "pmt_status": status_api_bqr,
                                     "txn_amt": amount_api_bqr,
                                     "pmt_mode": payment_mode_api_bqr,
                                     "pmt_state": state_api_bqr,
                                     "settle_status": settlement_status_api_bqr,
                                     "acquirer_code": acquirer_code_api_bqr,
                                     "issuer_code": issuer_code_api_bqr,
                                     "mid": mid_api_bqr,
                                     "txn_type": txn_type_api_bqr,
                                     "tid": tid_api_bqr,
                                     "org_code": org_code_api_bqr,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api_bqr),
                                     # --------------------------------------------------
                                     "start_success": start_success_card,
                                     "status_success": status_received_success_card,
                                     "status_mssg": status_received_mssg_card,
                                     "status_mssg_code": status_received_mssgcode_card,
                                     "status_real_code": status_received_realcode_card,

                                     "start_success_1": start_success_bqr,
                                     "status_success_1": status_queue_success,
                                     "status_mssg_1": status_queue_mssg,
                                     "status_mssg_code_1": status_queue_mssgcode,
                                     "status_real_code_1": status_queue_realcode,

                                    # ----------------------------------------------------
                                     "status_success_2": status_after_cancel_success_card,
                                     "status_mssg_code_2": status_after_cancel_mssgcode_card,
                                     "status_real_code_2": status_after_cancel_realcode_card,
                                     "status_mssg_2": status_after_cancel_mssg_card,
                                     "status_username_2": status_after_cancel_username_card,
                                     "status_req_id_2": status_after_cancel_rqst_id_card,

                                     "status_success_3": status_after_pmt_success_bqr,
                                     "status_mssg_code_3": status_after_pmt_mssgcode_bqr,
                                     "status_real_code_3": status_after_pmt_realcode_bqr,
                                     "status_mssg_3": status_after_pmt_mssg_bqr,
                                     "status_username_3": status_after_pmt_username_bqr,
                                     "status_req_id_3": status_after_pmt_rqst_id_bqr,
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
                    "txn_amt": float(amount_bqr),
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "BHARATQR",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "settle_status": "SETTLED",
                    "txn_type": "CHARGE",

                    "bqr_pmt_status": "Transaction Success",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount_bqr,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": db_bqr_terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": db_bqr_config_id,
                    "bqr_txn_primary_id": txn_id_bqr,
                    "bqr_merchant_pan": db_bqr_config_merchant_pan,
                    "bqr_org_code": org_code,

                    "p2p_status_card_1": "RECEIVED",
                    "p2p_status_card_2": "CANCELED_FROM_EXTERNAL_SYSTEM",

                    "p2p_status_bqr_1": "QUEUED",
                    "p2p_status_bqr_2": "COMPLETED",
                    "p2p_txn_id_1_bqr": txn_id_bqr

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id_bqr + "'"
                logger.debug(f"Query to fetch BQR txn data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                amount_db_bqr = int(result["amount"].iloc[0])
                payment_status_db_bqr = result["status"].iloc[0]
                payment_state_db_bqr = result["state"].iloc[0]
                payment_mode_db_bqr = result["payment_mode"].iloc[0]
                acquirer_code_db_bqr = result["acquirer_code"].iloc[0]
                bank_code_db_bqr = result["bank_code"].iloc[0]
                payment_gateway_db_bqr = result["payment_gateway"].iloc[0]
                mid_db_bqr = result["mid"].iloc[0]
                tid_db_bqr = result["tid"].iloc[0]
                settlement_status_db_bqr = result["settlement_status"].iloc[0]
                txn_type_db_bqr = result["txn_type"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id_bqr + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = int(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from p2p_request where id='" + str(request_id_card) + "';"
                logger.debug(f"Query to fetch card data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_card_2 = result['status'].values[0]

                query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
                logger.debug(f"Query to fetch BQR data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_bqr_2 = result['status'].values[0]
                db_p2p_request_txn_id_bqr = result['transactionId'].values[0]

                actual_db_values = {
                    "txn_amt": amount_db_bqr,
                    "pmt_status": payment_status_db_bqr,
                    "pmt_state": payment_state_db_bqr,
                    "pmt_mode": payment_mode_db_bqr,
                    "acquirer_code": acquirer_code_db_bqr,
                    "bank_code": bank_code_db_bqr,
                    "payment_gateway": payment_gateway_db_bqr,
                    "mid": mid_db_bqr,
                    "tid": tid_db_bqr,
                    "settle_status": settlement_status_db_bqr,
                    "txn_type": txn_type_db_bqr,
                    #---------------------------
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_org_code": bqr_org_code_db,
                    # -------------------------------------------------------
                    "p2p_status_card_1": db_p2p_request_status_card_1,
                    "p2p_status_card_2": db_p2p_request_status_card_2,

                    "p2p_status_bqr_1": db_p2p_request_status_bqr_1,
                    "p2p_status_bqr_2": db_p2p_request_status_bqr_2,
                    "p2p_txn_id_1_bqr": db_p2p_request_txn_id_bqr
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