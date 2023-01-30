import string
import sys
import random
import pytest
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
from Configuration import testsuite_teardown, Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.PAX_TransHistoryPage import PaxTransHistoryPage
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, date_time_converter, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
def test_500_501_011():
    """
    Sub Feature Code: UI_Common_P2P_UPI_Start_API_Without_Payment_Mode_11
    Sub Feature Description: Send notification without payment mode, do successful UPI payment from device and validate status using status API
    TC naming code description: 500: P2P, 501: P2P_UPI, 011: TC 011
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

        query = "select * from terminal_info where org_code='" + str(org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
        logger.info(f"Query from terminal_info, device_serial : {device_serial}")
        logger.info(f"Query from terminal_info, mid : {mid}")
        logger.info(f"Query from terminal_info, tid : {tid}")

        # Get details from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
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

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
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
            redis_data = "b'"+device_serial+"|ezetap_android|"+org_code+"'"
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

            amount = random.randint(201, 300)
            logger.info(f"Generated amount: {amount}")
            ext_ref_number = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number:  {ext_ref_number}")
            push_to = {"deviceId": ""+device_serial+"|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount,
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start}")

            request_id = resp_start['p2pRequestId']
            start_success = resp_start['success']

            sleep(1)

            #Check status of request after receiving to the device
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
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            sleep(2)
            payment_page.click_on_proceed_homepage()
            # app_driver.reset()

            # Check status of request after payment
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            resp_status_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after UPI payment is : {resp_status_2}")

            status_after_pmt_success = resp_status_2['success']
            status_after_pmt_mssgcode = resp_status_2['messageCode']
            status_after_pmt_mssg = resp_status_2['message']
            status_after_pmt_realcode = resp_status_2['realCode']
            status_after_pmt_username = resp_status_2['username']
            status_after_pmt_rqst_id = resp_status_2['p2pRequestId']
            txn_id = resp_status_2['txnId']
            logger.debug(f"Transaction ID of UPI payment: {txn_id}")

            # Fetch values from DB table txn after payment
            query = "select * from txn where id='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details from DB table txn after UPI payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time = result['created_time'].values[0]

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
            date_and_time = date_time_converter.to_app_format(txn_created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                pax_txn_history_page = PaxTransHistoryPage(app_driver)
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number)

                payment_status = pax_txn_history_page.fetch_txn_status_text()
                payment_mode = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id = pax_txn_history_page.fetch_txn_id_text()
                app_amount = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = pax_txn_history_page.fetch_date_time_text()

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time
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
            date = date_time_converter.db_datetime(txn_created_time)
            try:
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date,
                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",
                    "status_success_1": True,
                    "status_mssg_code_1": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_1": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_1": "Transaction done on device, Please look at Txn status.",
                    "status_username_1": app_username,
                    "status_req_id_1": request_id,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "mid": mid_api,
                                     "txn_type": txn_type_api,
                                     "tid": tid_api,
                                     "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "start_success": start_success,
                                     "status_success": status_received_success,
                                     "status_mssg": status_received_mssg,
                                     "status_mssg_code": status_received_mssgcode,
                                     "status_real_code": status_received_realcode,
                                     "status_success_1": status_after_pmt_success,
                                     "status_mssg_code_1": status_after_pmt_mssgcode,
                                     "status_real_code_1": status_after_pmt_realcode,
                                     "status_mssg_1": status_after_pmt_mssg,
                                     "status_username_1": status_after_pmt_username,
                                     "status_req_id_1": status_after_pmt_rqst_id,
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
                    "txn_amt": float(amount),
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

                    "p2p_status": "RECEIVED",
                    "p2p_txn_id": None,
                    "p2p_status_1": "COMPLETED",
                    "p2p_txn_id_1": txn_id

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                amount_db = int(result["amount"].iloc[0])
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                txn_type_db = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                upi_txn_status_db = result["status"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_org_code_db = result["org_code"].iloc[0]

                query = "select * from p2p_request where id='" + str(request_id) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_1 = result['status'].values[0]
                db_p2p_request_txn_id_1 = result['transactionId'].values[0]


                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "pmt_mode": payment_mode_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "settle_status": settlement_status_db,
                    "txn_type": txn_type_db,

                    "upi_txn_status": upi_txn_status_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_upi_mc_id": upi_upi_mc_id_db,
                    "upi_org_code": upi_org_code_db,

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
@pytest.mark.appVal
def test_500_501_012():
    """
    Sub Feature Code: UI_Common_P2P_UPI_Start_API_With_Payment_Mode_12
    Sub Feature Description: Send notification with payment mode as UPI, do successful payment from device and validate status using status API
    TC naming code description: 500: P2P, 501: P2P_UPI, 012: TC 012
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

        query = "select * from terminal_info where org_code='" + str(org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
        logger.info(f"Query from terminal_info, device_serial : {device_serial}")
        logger.info(f"Query from terminal_info, mid : {mid}")
        logger.info(f"Query from terminal_info, tid : {tid}")

        # Get details from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
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

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
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
            redis_data = "b'"+device_serial+"|ezetap_android|"+org_code+"'"
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

            amount = random.randint(201, 300)
            logger.info(f"Generated amount: {amount}")
            ext_ref_number = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number:  {ext_ref_number}")
            push_to = {"deviceId": ""+device_serial+"|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount,
                "externalRefNumber": ext_ref_number,
                "paymentMode": "UPI",
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start}")

            request_id = resp_start['p2pRequestId']
            start_success = resp_start['success']

            sleep(1)

            #Check status of request after receiving to the device
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

            payment_page = PaymentPage(app_driver)
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            sleep(2)
            payment_page.click_on_proceed_homepage()
            # app_driver.reset()

            # Check status of request after payment
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            resp_status_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after UPI payment is : {resp_status_2}")

            status_after_pmt_success = resp_status_2['success']
            status_after_pmt_mssgcode = resp_status_2['messageCode']
            status_after_pmt_mssg = resp_status_2['message']
            status_after_pmt_realcode = resp_status_2['realCode']
            status_after_pmt_username = resp_status_2['username']
            status_after_pmt_rqst_id = resp_status_2['p2pRequestId']
            txn_id = resp_status_2['txnId']
            logger.debug(f"Transaction ID of UPI payment: {txn_id}")

            # Fetch values from DB table txn after payment
            query = "select * from txn where id='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details from DB table txn after UPI payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time = result['created_time'].values[0]

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
            date_and_time = date_time_converter.to_app_format(txn_created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                pax_txn_history_page = PaxTransHistoryPage(app_driver)
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number)

                payment_status = pax_txn_history_page.fetch_txn_status_text()
                payment_mode = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id = pax_txn_history_page.fetch_txn_id_text()
                app_amount = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = pax_txn_history_page.fetch_date_time_text()

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time
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
            date = date_time_converter.db_datetime(txn_created_time)
            try:
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date,
                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",
                    "status_success_1": True,
                    "status_mssg_code_1": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_1": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_1": "Transaction done on device, Please look at Txn status.",
                    "status_username_1": app_username,
                    "status_req_id_1": request_id,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "mid": mid_api,
                                     "txn_type": txn_type_api,
                                     "tid": tid_api,
                                     "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "start_success": start_success,
                                     "status_success": status_received_success,
                                     "status_mssg": status_received_mssg,
                                     "status_mssg_code": status_received_mssgcode,
                                     "status_real_code": status_received_realcode,
                                     "status_success_1": status_after_pmt_success,
                                     "status_mssg_code_1": status_after_pmt_mssgcode,
                                     "status_real_code_1": status_after_pmt_realcode,
                                     "status_mssg_1": status_after_pmt_mssg,
                                     "status_username_1": status_after_pmt_username,
                                     "status_req_id_1": status_after_pmt_rqst_id,
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
                    "txn_amt": float(amount),
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

                    "p2p_status": "RECEIVED",
                    "p2p_status_1": "COMPLETED",
                    "p2p_txn_id_1": txn_id

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                amount_db = int(result["amount"].iloc[0])
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                txn_type_db = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                upi_txn_status_db = result["status"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_org_code_db = result["org_code"].iloc[0]

                query = "select * from p2p_request where id='" + str(request_id) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_1 = result['status'].values[0]
                db_p2p_request_txn_id_1 = result['transactionId'].values[0]


                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "pmt_mode": payment_mode_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "settle_status": settlement_status_db,
                    "txn_type": txn_type_db,

                    "upi_txn_status": upi_txn_status_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_upi_mc_id": upi_upi_mc_id_db,
                    "upi_org_code": upi_org_code_db,

                    "p2p_status": db_p2p_request_status,
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
@pytest.mark.appVal
def test_500_501_015():
    """
    Sub Feature Code: UI_Common_P2P_UPI_Normal_Txn_P2P_Enabled_15
    Sub Feature Description: Perform a normal UPI transaction and P2P transaction when P2P is enabled
    TC naming code description: 500: P2P, 501: P2P_UPI, 015: TC 015
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

        query = "select * from terminal_info where org_code='" + str(org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
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

        # Disable 'Only P2P allowed User'
        query = "update setting set setting_value ='false' where setting_name='onlyP2PUser' and entity_id ='"+str(user_id)+"';"
        logger.debug(f"Query to update user as 'allow only P2P' as disabled in DB : {query}")
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
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
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

            # Doing normal UPI txn
            normal_amount = random.randint(201, 300)
            normal_order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(normal_amount, normal_order_id)
            logger.debug(f"Entered amount for normal UPI txn is : {normal_amount}")
            logger.debug(f"Entered order_id for normal UPI txn is : {normal_order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(normal_amount, normal_order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully for normal UPI txn")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the normal UPI transaction : {app_payment_status}")
            payment_page.click_on_proceed_homepage()
            logger.debug(f"Redirected to home page after normal UPI txn")

            # Get normal UPI txn_id from DB
            query = "select * from upi_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch normal upi transaction id from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)

            normal_txn_id = result["txn_id"].iloc[0]
            normal_upi_status_db = result["status"].iloc[0]
            normal_upi_txn_type_db = result["txn_type"].iloc[0]
            normal_upi_upi_mc_id_db = int(result["upi_mc_id"].iloc[0])
            normal_upi_bank_code_db = result["bank_code"].iloc[0]
            normal_upi_org_code_db = result["org_code"].iloc[0]

            # Fetch values from DB table txn after normal UPI payment
            query = "select * from txn where id='" + str(normal_txn_id) + "';"
            logger.debug(f"Query to fetch details from txn table txn after normal UPI payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            normal_txn_created_time = result['created_time'].values[0]
            normal_amount_db = int(result["amount"].iloc[0])
            normal_payment_status_db = result["status"].iloc[0]
            normal_payment_state_db = result["state"].iloc[0]
            normal_payment_mode_db = result["payment_mode"].iloc[0]
            normal_acquirer_code_db = result["acquirer_code"].iloc[0]
            normal_bank_code_db = result["bank_code"].iloc[0]
            normal_payment_gateway_db = result["payment_gateway"].iloc[0]
            normal_mid_db = result["mid"].iloc[0]
            normal_tid_db = result["tid"].iloc[0]
            normal_settlement_status_db = result["settlement_status"].iloc[0]
            normal_txn_type_db = result["txn_type"].iloc[0]

            # Doing P2P UPI txn
            amount = random.randint(201, 300)
            logger.info(f"Generated amount: {amount}")
            ext_ref_number = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number:  {ext_ref_number}")
            push_to = {"deviceId": ""+device_serial+"|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount,
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start}")

            request_id = resp_start['p2pRequestId']
            start_success = resp_start['success']

            sleep(1)

            #Check status of request after receiving to the device
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
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            sleep(2)
            payment_page.click_on_proceed_homepage()

            # Check status of request after payment
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            resp_status_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after UPI payment is : {resp_status_2}")

            status_after_pmt_success = resp_status_2['success']
            status_after_pmt_mssgcode = resp_status_2['messageCode']
            status_after_pmt_mssg = resp_status_2['message']
            status_after_pmt_realcode = resp_status_2['realCode']
            status_after_pmt_username = resp_status_2['username']
            status_after_pmt_rqst_id = resp_status_2['p2pRequestId']
            txn_id = resp_status_2['txnId']
            logger.debug(f"Transaction ID of BQR payment: {txn_id}")

            # Fetch values from DB table txn after P2P payment
            query = "select * from txn where id='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details from DB table txn after UPI payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time = result['created_time'].values[0]

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
            date_and_time = date_time_converter.to_app_format(txn_created_time)
            normal_date_and_time = date_time_converter.to_app_format(normal_txn_created_time)
            try:
                expected_app_values = {
                    "pmt_mode_1": "UPI",
                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": str(normal_amount) + ".00",
                    "settle_status_1": "SETTLED",
                    "txn_id_1": normal_txn_id,
                    "pmt_msg_1": "PAYMENT SUCCESSFUL",
                    "date_1": normal_date_and_time,

                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                pax_txn_history_page = PaxTransHistoryPage(app_driver)
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number)

                payment_status = pax_txn_history_page.fetch_txn_status_text()
                payment_mode = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id = pax_txn_history_page.fetch_txn_id_text()
                app_amount = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = pax_txn_history_page.fetch_date_time_text()

                pax_txn_history_page.click_back_Btn_transaction_details()
                pax_txn_history_page.click_on_transaction_by_order_id(normal_order_id)
                normal_payment_status = pax_txn_history_page.fetch_txn_status_text()
                normal_payment_mode = pax_txn_history_page.fetch_txn_type_text()
                normal_app_txn_id = pax_txn_history_page.fetch_txn_id_text()
                normal_app_amount = pax_txn_history_page.fetch_txn_amount_text()
                normal_app_settlement_status = pax_txn_history_page.fetch_settlement_status_text()
                normal_app_payment_msg = pax_txn_history_page.fetch_txn_payment_message_text()
                normal_app_date_and_time = pax_txn_history_page.fetch_date_time_text()

                actual_app_values = {
                    "pmt_mode_1": normal_payment_mode,
                    "pmt_status_1": normal_payment_status.split(':')[1],
                    "txn_amt_1": normal_app_amount.split(' ')[1],
                    "txn_id_1": normal_app_txn_id,
                    "settle_status_1": normal_app_settlement_status,
                    "pmt_msg_1": normal_app_payment_msg,
                    "date_1": normal_app_date_and_time,

                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time
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
            date = date_time_converter.db_datetime(txn_created_time)
            normal_date = date_time_converter.db_datetime(normal_txn_created_time)
            try:
                expected_api_values = {
                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": float(normal_amount),
                    "pmt_mode_1": "UPI",
                    "pmt_state_1": "SETTLED",
                    "settle_status_1": "SETTLED",
                    "acquirer_code_1": "HDFC",
                    "issuer_code_1": "HDFC",
                    "txn_type_1": "CHARGE",
                    "mid_1": db_upi_config_mid,
                    "tid_1": db_upi_config_tid,
                    "org_code_1": org_code,
                    "date_1": normal_date,

                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date,

                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",
                    "status_success_1": True,
                    "status_mssg_code_1": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_1": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_1": "Transaction done on device, Please look at Txn status.",
                    "status_username_1": app_username,
                    "status_req_id_1": request_id,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                response = [x for x in response["txns"] if x["txnId"] == normal_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

                normal_status_api = response["status"]
                normal_amount_api = float(response["amount"])
                normal_payment_mode_api = response["paymentMode"]
                normal_state_api = response["states"][0]
                normal_settlement_status_api = response["settlementStatus"]
                normal_issuer_code_api = response["issuerCode"]
                normal_acquirer_code_api = response["acquirerCode"]
                normal_org_code_api = response["orgCode"]
                normal_mid_api = response["mid"]
                normal_tid_api = response["tid"]
                normal_txn_type_api = response["txnType"]
                normal_date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                actual_api_values = {"pmt_status_1": normal_status_api,
                                     "txn_amt_1": normal_amount_api,
                                     "pmt_mode_1": normal_payment_mode_api,
                                     "pmt_state_1": normal_state_api,
                                     "settle_status_1": normal_settlement_status_api,
                                     "acquirer_code_1": normal_acquirer_code_api,
                                     "issuer_code_1": normal_issuer_code_api,
                                     "mid_1": normal_mid_api,
                                     "txn_type_1": normal_txn_type_api,
                                     "tid_1": normal_tid_api,
                                     "org_code_1": normal_org_code_api,
                                     "date_1": date_time_converter.from_api_to_datetime_format(normal_date_api),

                                     "pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "mid": mid_api,
                                     "txn_type": txn_type_api,
                                     "tid": tid_api,
                                     "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),

                                     "start_success": start_success,
                                     "status_success": status_received_success,
                                     "status_mssg": status_received_mssg,
                                     "status_mssg_code": status_received_mssgcode,
                                     "status_real_code": status_received_realcode,
                                     "status_success_1": status_after_pmt_success,
                                     "status_mssg_code_1": status_after_pmt_mssgcode,
                                     "status_real_code_1": status_after_pmt_realcode,
                                     "status_mssg_1": status_after_pmt_mssg,
                                     "status_username_1": status_after_pmt_username,
                                     "status_req_id_1": status_after_pmt_rqst_id,
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
                    "txn_amt_1": float(normal_amount),
                    "pmt_status_1": "AUTHORIZED",
                    "pmt_state_1": "SETTLED",
                    "pmt_mode_1": "UPI",
                    "acquirer_code_1": "HDFC",
                    "bank_code_1": "HDFC",
                    "payment_gateway_1": "HDFC",
                    "mid_1": db_upi_config_mid,
                    "tid_1": db_upi_config_tid,
                    "settle_status_1": "SETTLED",
                    "txn_type_1": "CHARGE",

                    "txn_amt": float(amount),
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

                    "upi_txn_status_1": "AUTHORIZED",
                    "upi_bank_code_1": "HDFC",
                    "upi_txn_type_1": "PAY_QR",
                    "upi_upi_mc_id_1": db_upi_config_id,
                    "upi_org_code_1": org_code,

                    "upi_txn_status": "AUTHORIZED",
                    "upi_bank_code": "HDFC",
                    "upi_txn_type": "PAY_QR",
                    "upi_upi_mc_id": db_upi_config_id,
                    "upi_org_code": org_code,

                    "p2p_status": "RECEIVED",
                    "p2p_txn_id": None,
                    "p2p_status_1": "COMPLETED",
                    "p2p_txn_id_1": txn_id

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                amount_db = int(result["amount"].iloc[0])
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                txn_type_db = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_org_code_db = result["org_code"].iloc[0]

                query = "select * from p2p_request where id='" + str(request_id) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_1 = result['status'].values[0]
                db_p2p_request_txn_id_1 = result['transactionId'].values[0]


                actual_db_values = {
                    "txn_amt_1": normal_amount_db,
                    "pmt_status_1": normal_payment_status_db,
                    "pmt_state_1": normal_payment_state_db,
                    "pmt_mode_1": normal_payment_mode_db,
                    "acquirer_code_1": normal_acquirer_code_db,
                    "bank_code_1": normal_bank_code_db,
                    "payment_gateway_1": normal_payment_gateway_db,
                    "mid_1": normal_mid_db,
                    "tid_1": normal_tid_db,
                    "settle_status_1": normal_settlement_status_db,
                    "txn_type_1": normal_txn_type_db,

                    "txn_amt": amount_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "pmt_mode": payment_mode_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "settle_status": settlement_status_db,
                    "txn_type": txn_type_db,

                    "upi_txn_status_1": normal_upi_status_db,
                    "upi_bank_code_1": normal_upi_bank_code_db,
                    "upi_txn_type_1": normal_upi_txn_type_db,
                    "upi_upi_mc_id_1": normal_upi_upi_mc_id_db,
                    "upi_org_code_1": normal_upi_org_code_db,

                    "upi_txn_status": upi_status_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_upi_mc_id": upi_upi_mc_id_db,
                    "upi_org_code": upi_org_code_db,

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
def test_500_501_035():
    """
    Sub Feature Code: UI_Common_P2P_UPI_Cancel_API_35
    Sub Feature Description: Sending payment notification with payment mode as UPI and cancel the notification using cancel API and do status API
    TC naming code description: 500: P2P, 501: P2P_UPI, 035: TC 035
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

            payment_page = PaymentPage(app_driver)
            sleep(2)
            payment_page.click_on_proceed_homepage()

            # Check status of request after payment
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_upi
            })
            resp_status_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after UPI payment is : {resp_status_2}")

            txn_id = resp_status_2['txnId']
            logger.debug(f"Transaction ID of UPI request cancel: {txn_id}")

            # Fetch values from DB table txn after payment
            query = "select * from txn where id='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details from DB table txn after UPI payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time = result['created_time'].values[0]

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
            date_and_time = date_time_converter.to_app_format(txn_created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount_upi) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                pax_txn_history_page = PaxTransHistoryPage(app_driver)
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number_upi)

                payment_status = pax_txn_history_page.fetch_txn_status_text()
                payment_mode = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id = pax_txn_history_page.fetch_txn_id_text()
                app_amount = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = pax_txn_history_page.fetch_date_time_text()

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time
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
            try:
                expected_api_values = {
                    # UPI txn details
                    "start_success": True,
                    "status_success": True,
                    "status_mssg": "Notification has been received on POS Device.",
                    "status_mssg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",

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
                    "p2p_status_upi_2": "COMPLETED",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from p2p_request where id='" + str(request_id_upi) + "';"
                logger.debug(f"Query to fetch UPI data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_upi_2 = result['status'].values[0]

                actual_db_values = {
                    "p2p_status_upi_2": db_p2p_request_status_upi_2,
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