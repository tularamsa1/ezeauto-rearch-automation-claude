import random
import string
import sys
import pytest
from time import sleep
from datetime import datetime
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
@pytest.mark.appVal
def test_common_500_502_006():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Start_API_Without_Payment_Mode_06
    Sub Feature Description: Send notification without payment mode, do successful BQR payment from device and validate status
    TC naming code description: 500: P2P, 502: P2P_BQR, 006: TC 006
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

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQR')

        testsuite_teardown.revert_p2p_settings(portal_username, portal_password,app_username, app_password, org_code)
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

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
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

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, commx_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
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
                raise Exception("Exception in locating P2P notification on device")
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

            sleep(2)

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
            payment_page.is_payment_page_displayed_P2P()
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            sleep(2)
            payment_page.click_on_proceed_homepage()
            sleep(2)

            # Check status of request after payment
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            resp_status_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after BQR payment is : {resp_status_2}")

            status_after_pmt_success = resp_status_2['success']
            status_after_pmt_mssgcode = resp_status_2['messageCode']
            status_after_pmt_mssg = resp_status_2['message']
            status_after_pmt_realcode = resp_status_2['realCode']
            status_after_pmt_username = resp_status_2['username']
            status_after_pmt_rqst_id = resp_status_2['p2pRequestId']
            txn_id = resp_status_2['txnId']
            logger.debug(f"Transaction ID of BQR payment: {txn_id}")

            # Fetch values from DB table txn after payment
            query = "select * from txn where id='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details from DB table txn after BQR payment : {query}")
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
                    "pmt_mode": "BHARAT QR",
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
            finally:
                pax_txn_history_page.click_back_Btn_transaction_details()
                pax_txn_history_page.click_back_Btn()
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
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
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
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": db_bqr_terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": db_bqr_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_merchant_pan": db_bqr_config_merchant_pan,
                    "bqr_org_code": org_code,

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

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
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
def test_common_500_502_007():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Start_API_With_Payment_Mode_07
    Sub Feature Description: Send notification with payment mode as BQR, do successful payment from device and validate status using status API
    TC naming code description: 500: P2P, 502: P2P_BQR, 007: TC 007
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

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
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

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False, commx_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
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
                raise Exception("Exception in locating P2P notification on device")
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
            push_to = {"deviceId": ""+device_serial+"|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount,
                "paymentMode": "BHARATQR",
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start}")

            request_id = resp_start['p2pRequestId']
            start_success = resp_start['success']

            sleep(2)

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
            sleep(2)

            # Fetch values from DB table p2p_request after receiving to device
            query = "select * from p2p_request where id='" + str(request_id) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status = result['status'].values[0]

            payment_page = PaymentPage(app_driver)
            payment_page.is_qrcode_displayed_P2P()
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
            logger.debug(f"Response received for P2P status API after BQR payment is : {resp_status_2}")

            status_after_pmt_success = resp_status_2['success']
            status_after_pmt_mssgcode = resp_status_2['messageCode']
            status_after_pmt_mssg = resp_status_2['message']
            status_after_pmt_realcode = resp_status_2['realCode']
            status_after_pmt_username = resp_status_2['username']
            status_after_pmt_rqst_id = resp_status_2['p2pRequestId']
            txn_id = resp_status_2['txnId']
            logger.debug(f"Transaction ID of BQR payment: {txn_id}")

            # Fetch values from DB table txn after payment
            query = "select * from txn where id='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details from DB table txn after BQR payment : {query}")
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
                    "pmt_mode": "BHARAT QR",
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
            finally:
                pax_txn_history_page.click_back_Btn_transaction_details()
                pax_txn_history_page.click_back_Btn()
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
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
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

                    # "cancel_bqr_success": False,
                    # "cancel_bqr_mssg": "Transaction already initiated, cant initiate cancellation.",
                    # "cancel_bqr_errorcode": "EZETAP_0000610",
                    # "cancel_bqr_errormssg": "Transaction already initiated, cant initiate cancellation.",
                    # "cancel_bqr_realcode": "P2P_PAYMENT_INITIATED",
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
                                     #
                                     # "cancel_bqr_success": cancel_bqr_success,
                                     # "cancel_bqr_mssg": cancel_bqr_mssg,
                                     # "cancel_bqr_errorcode": cancel_bqr_errorcode,
                                     # "cancel_bqr_errormssg": cancel_bqr_errormssg,
                                     # "cancel_bqr_realcode": cancel_bqr_realcode,
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
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": db_bqr_terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": db_bqr_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_merchant_pan": db_bqr_config_merchant_pan,
                    "bqr_org_code": org_code,

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

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
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
def test_common_500_502_010():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Normal_Txn_P2P_Enabled_10
    Sub Feature Description: Perform a normal BQR-UPI transactions and BQR-UPI P2P transactions
    TC naming code description: 500: P2P, 502: P2P_BQR, 010: TC 010
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

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQR')
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
                app_username, app_password = testsuite_teardown.get_normal_p2p_user(portal_username, portal_password, app_username, app_password, org_code)
                logger.info(f"New user to do normal transaction is {app_username} with password {app_password}")
            else:
                logger.info(f"Current app user can do normal transactions as well")
        else:
            logger.info(f"Current app user can do normal transactions as well")

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
        logger.info(f"Query from terminal_info, mid : {mid}")
        logger.info(f"Query from terminal_info, tid : {tid}")

        # Get details from bharatqr_merchant_config table
        query = "select * from bharatqr_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)

        db_bqr_config_id = result['id'].values[0]
        logger.info(f"from bharatqr_merchant_config, config id is : {db_bqr_config_id}")

        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"from bharatqr_merchant_config, mid is : {db_bqr_config_mid}")

        db_bqr_config_tid = result['tid'].values[0]
        logger.info(f"from bharatqr_merchant_config, tid is : {db_bqr_config_tid}")

        db_bqr_terminal_info_id = result['terminal_info_id'].values[0]
        logger.info(f"from bharatqr_merchant_config, terminal_info_id is : {db_bqr_terminal_info_id}")

        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"from bharatqr_merchant_config, merchant_pan is : {db_bqr_config_merchant_pan}")

        # Get details from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)

        db_upi_config_id = result['id'].values[0]
        logger.info(f"from upi_merchant_config, config id is : {db_upi_config_id}")

        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"from upi_merchant_config, mid is : {db_upi_config_mid}")

        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"from upi_merchant_config, tid is : {db_upi_config_tid}")

        db_upi_terminal_info_id = result['terminal_info_id'].values[0]
        logger.info(f"from upi_merchant_config, terminal_info_id is : {db_upi_terminal_info_id}")

        db_upi_vpa = result['vpa'].values[0]
        logger.info(f"from upi_merchant_config, vpa is : {db_upi_vpa}")

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

            # Doing normal BQR txn
            normal_amount_bqr = random.randint(401, 999)
            normal_order_id_bqr = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(normal_amount_bqr, normal_order_id_bqr)
            logger.debug(f"Entered amount for normal BQR txn is : {normal_amount_bqr}")
            logger.debug(f"Entered order_id for normal BQR txn is : {normal_order_id_bqr}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(normal_amount_bqr, normal_order_id_bqr)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully for normal BQR txn")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the normal BQR transaction : {app_payment_status}")
            payment_page.click_on_proceed_homepage()
            logger.debug(f"Redirected to home page after normal BQR txn")

            # Get normal BQR txn_id from DB
            query = "select * from bharatqr_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            normal_txn_id_bqr = result["id"].iloc[0]
            normal_bqr_status_db_bqr = result["status_desc"].iloc[0]
            normal_bqr_state_db_bqr = result["state"].iloc[0]
            normal_bqr_amount_db_bqr = int(result["txn_amount"].iloc[0])
            normal_bqr_txn_type_db_bqr = result["txn_type"].iloc[0]
            normal_bqr_terminal_info_id_db_bqr = result["terminal_info_id"].iloc[0]
            normal_bqr_bank_code_db_bqr = result["bank_code"].iloc[0]
            normal_bqr_merchant_config_id_db_bqr = result["merchant_config_id"].iloc[0]
            normal_bqr_txn_primary_id_db_bqr = result["transaction_primary_id"].iloc[0]
            normal_bqr_merchant_pan_db_bqr = result["merchant_pan"].iloc[0]
            normal_bqr_org_code_db_bqr = result['org_code'].values[0]

            # Fetch values from DB table txn after normal BQR payment
            query = "select * from txn where id='" + str(normal_txn_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table txn after normal BQR payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            normal_txn_created_time_bqr = result['created_time'].values[0]
            normal_amount_db_bqr = int(result["amount"].iloc[0])
            normal_payment_status_db_bqr = result["status"].iloc[0]
            normal_payment_state_db_bqr = result["state"].iloc[0]
            normal_payment_mode_db_bqr = result["payment_mode"].iloc[0]
            normal_acquirer_code_db_bqr = result["acquirer_code"].iloc[0]
            normal_bank_code_db_bqr = result["bank_code"].iloc[0]
            normal_payment_gateway_db_bqr = result["payment_gateway"].iloc[0]
            normal_mid_db_bqr = result["mid"].iloc[0]
            normal_tid_db_bqr = result["tid"].iloc[0]
            normal_settlement_status_db_bqr = result["settlement_status"].iloc[0]
            normal_txn_type_db_bqr = result["txn_type"].iloc[0]

            # Doing P2P BQR txn
            amount_bqr_p2p = random.randint(401, 999)
            logger.info(f"Generated amount: {amount_bqr_p2p}")
            ext_ref_number_bqr_p2p = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number for P2P BQR txn:  {ext_ref_number_bqr_p2p}")
            push_to = {"deviceId": ""+device_serial+"|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount_bqr_p2p,
                "externalRefNumber": ext_ref_number_bqr_p2p,
                "pushTo": push_to
            })
            resp_start_bqr = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API for BQR is : {resp_start_bqr}")

            request_id_bqr = resp_start_bqr['p2pRequestId']
            start_success_bqr = resp_start_bqr['success']
            sleep(2)

            #Check status of request after receiving to the device
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after BQR request received is : {resp_status_bqr_1}")

            status_received_success_bqr = resp_status_bqr_1['success']
            status_received_mssg_bqr = resp_status_bqr_1['message']
            status_received_mssgcode_bqr = resp_status_bqr_1['messageCode']
            status_received_realcode_bqr = resp_status_bqr_1['realCode']

            # Fetch values from DB table p2p_request after receiving to device
            query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_bqr = result['status'].values[0]
            db_p2p_request_txn_id_bqr = result['transactionId'].values[0]

            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_P2P()
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
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
                "origP2pRequestId": request_id_bqr
            })
            resp_status_bqr_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after BQR payment is : {resp_status_bqr_2}")

            status_after_bqr_pmt_success = resp_status_bqr_2['success']
            status_after_bqr_pmt_mssgcode = resp_status_bqr_2['messageCode']
            status_after_bqr_pmt_mssg = resp_status_bqr_2['message']
            status_after_bqr_pmt_realcode = resp_status_bqr_2['realCode']
            status_after_bqr_pmt_username = resp_status_bqr_2['username']
            status_after_bqr_pmt_rqst_id = resp_status_bqr_2['p2pRequestId']
            txn_id_bqr = resp_status_bqr_2['txnId']
            logger.debug(f"Transaction ID of BQR payment: {txn_id_bqr}")

            # Fetch values from DB table txn after payment
            query = "select * from txn where id='" + str(txn_id_bqr) + "';"
            logger.debug(f"Query to fetch details from DB table txn after BQR payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time_bqr = result['created_time'].values[0]

            # Doing normal UPI txn
            normal_amount_upi = random.randint(201, 300)
            normal_order_id_upi = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(normal_amount_upi, normal_order_id_upi)
            logger.debug(f"Entered amount for normal UPI txn is : {normal_amount_upi}")
            logger.debug(f"Entered order_id for normal UPI txn is : {normal_order_id_upi}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(normal_amount_upi, normal_order_id_upi)
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

            normal_txn_id_upi = result["txn_id"].iloc[0]
            normal_upi_status_db = result["status"].iloc[0]
            normal_upi_txn_type_db = result["txn_type"].iloc[0]
            normal_upi_upi_mc_id_db = int(result["upi_mc_id"].iloc[0])
            normal_upi_bank_code_db = result["bank_code"].iloc[0]
            normal_upi_org_code_db = result["org_code"].iloc[0]

            # Fetch values from DB table txn after normal UPI payment
            query = "select * from txn where id='" + str(normal_txn_id_upi) + "';"
            logger.debug(f"Query to fetch details from txn table txn after normal UPI payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            normal_txn_created_time_upi = result['created_time'].values[0]
            normal_amount_db_upi = int(result["amount"].iloc[0])
            normal_payment_status_db_upi = result["status"].iloc[0]
            normal_payment_state_db_upi = result["state"].iloc[0]
            normal_payment_mode_db_upi = result["payment_mode"].iloc[0]
            normal_acquirer_code_db_upi = result["acquirer_code"].iloc[0]
            normal_bank_code_db_upi = result["bank_code"].iloc[0]
            normal_payment_gateway_db_upi = result["payment_gateway"].iloc[0]
            normal_mid_db_upi = result["mid"].iloc[0]
            normal_tid_db_upi = result["tid"].iloc[0]
            normal_settlement_status_db_upi = result["settlement_status"].iloc[0]
            normal_txn_type_db_upi = result["txn_type"].iloc[0]

            # Doing P2P UPI txn
            amount_upi = random.randint(201, 300)
            logger.info(f"Generated amount: {amount_upi}")
            ext_ref_number_upi_p2p = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number for UPI P2P txn:  {ext_ref_number_upi_p2p}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount_upi,
                "externalRefNumber": ext_ref_number_upi_p2p,
                "pushTo": push_to
            })
            resp_start_upi = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start_upi}")

            request_id_upi = resp_start_upi['p2pRequestId']
            start_success_upi = resp_start_upi['success']

            sleep(2)

            # Check status of request after receiving to the device
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id_upi
            })
            resp_status_upi_1 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after request received is : {resp_status_upi_1}")

            status_received_success_upi = resp_status_upi_1['success']
            status_received_mssg_upi = resp_status_upi_1['message']
            status_received_mssgcode_upi = resp_status_upi_1['messageCode']
            status_received_realcode_upi = resp_status_upi_1['realCode']

            # Fetch values from DB table p2p_request after receiving to device
            query = "select * from p2p_request where id='" + str(request_id_upi) + "';"
            logger.debug(f"Query to fetch details from DB table p2p_request after receiving to device : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_p2p_request_status_upi = result['status'].values[0]
            db_p2p_request_txn_id_upi = result['transactionId'].values[0]

            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_P2P()
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
                "origP2pRequestId": request_id_upi
            })
            resp_status_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after UPI payment is : {resp_status_2}")

            status_after_upi_pmt_success = resp_status_2['success']
            status_after_upi_pmt_mssgcode = resp_status_2['messageCode']
            status_after_upi_pmt_mssg = resp_status_2['message']
            status_after_upi_pmt_realcode = resp_status_2['realCode']
            status_after_upi_pmt_username = resp_status_2['username']
            status_after_upi_pmt_rqst_id = resp_status_2['p2pRequestId']
            txn_id_upi = resp_status_2['txnId']
            logger.debug(f"Transaction ID of UPI payment: {txn_id_upi}")

            # Fetch values from DB table txn after P2P payment
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
            date_and_time_bqr = date_time_converter.to_app_format(txn_created_time_bqr)
            normal_date_and_time_bqr = date_time_converter.to_app_format(normal_txn_created_time_bqr)

            date_and_time_upi = date_time_converter.to_app_format(txn_created_time_upi)
            normal_date_and_time_upi = date_time_converter.to_app_format(normal_txn_created_time_upi)
            try:
                expected_app_values = {
                    "pmt_mode_bqr_1": "BHARAT QR",
                    "pmt_status_bqr_1": "AUTHORIZED",
                    "txn_amt_bqr_1": str(normal_amount_bqr) + ".00",
                    "settle_status_bqr_1": "SETTLED",
                    "txn_id_bqr_1": normal_txn_id_bqr,
                    "pmt_msg_bqr_1": "PAYMENT SUCCESSFUL",
                    "date_bqr_1": normal_date_and_time_bqr,

                    "pmt_mode_bqr": "BHARAT QR",
                    "pmt_status_bqr": "AUTHORIZED",
                    "txn_amt_bqr": str(amount_bqr_p2p) + ".00",
                    "settle_status_bqr": "SETTLED",
                    "txn_id_bqr": txn_id_bqr,
                    "pmt_msg_bqr": "PAYMENT SUCCESSFUL",
                    "date_bqr": date_and_time_bqr,

                    "pmt_mode_upi_1": "UPI",
                    "pmt_status_upi_1": "AUTHORIZED",
                    "txn_amt_upi_1": str(normal_amount_upi) + ".00",
                    "settle_status_upi_1": "SETTLED",
                    "txn_id_upi_1": normal_txn_id_upi,
                    "pmt_msg_upi_1": "PAYMENT SUCCESSFUL",
                    "date_upi_1": normal_date_and_time_upi,

                    "pmt_mode_upi": "UPI",
                    "pmt_status_upi": "AUTHORIZED",
                    "txn_amt_upi": str(amount_upi) + ".00",
                    "settle_status_upi": "SETTLED",
                    "txn_id_upi": txn_id_upi,
                    "pmt_msg_upi": "PAYMENT SUCCESSFUL",
                    "date_upi": date_and_time_upi
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                pax_txn_history_page = PaxTransHistoryPage(app_driver)
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number_bqr_p2p)

                payment_status_bqr = pax_txn_history_page.fetch_txn_status_text()
                payment_mode_bqr = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id_bqr = pax_txn_history_page.fetch_txn_id_text()
                app_amount_bqr = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status_bqr = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg_bqr = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time_bqr = pax_txn_history_page.fetch_date_time_text()

                pax_txn_history_page.click_back_Btn_transaction_details()
                pax_txn_history_page.click_on_transaction_by_order_id(normal_order_id_bqr)
                normal_payment_status_bqr = pax_txn_history_page.fetch_txn_status_text()
                normal_payment_mode_bqr = pax_txn_history_page.fetch_txn_type_text()
                normal_app_txn_id_bqr = pax_txn_history_page.fetch_txn_id_text()
                normal_app_amount_bqr = pax_txn_history_page.fetch_txn_amount_text()
                normal_app_settlement_status_bqr = pax_txn_history_page.fetch_settlement_status_text()
                normal_app_payment_msg_bqr = pax_txn_history_page.fetch_txn_payment_message_text()
                normal_app_date_and_time_bqr = pax_txn_history_page.fetch_date_time_text()

                pax_txn_history_page.click_back_Btn_transaction_details()
                pax_txn_history_page.click_on_transaction_by_order_id(ext_ref_number_upi_p2p)
                payment_status_upi = pax_txn_history_page.fetch_txn_status_text()
                payment_mode_upi = pax_txn_history_page.fetch_txn_type_text()
                app_txn_id_upi = pax_txn_history_page.fetch_txn_id_text()
                app_amount_upi = pax_txn_history_page.fetch_txn_amount_text()
                app_settlement_status_upi = pax_txn_history_page.fetch_settlement_status_text()
                app_payment_msg_upi = pax_txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time_upi = pax_txn_history_page.fetch_date_time_text()

                pax_txn_history_page.click_back_Btn_transaction_details()
                pax_txn_history_page.click_on_transaction_by_order_id(normal_order_id_upi)
                normal_payment_status_upi = pax_txn_history_page.fetch_txn_status_text()
                normal_payment_mode_upi = pax_txn_history_page.fetch_txn_type_text()
                normal_app_txn_id_upi = pax_txn_history_page.fetch_txn_id_text()
                normal_app_amount_upi = pax_txn_history_page.fetch_txn_amount_text()
                normal_app_settlement_status_upi = pax_txn_history_page.fetch_settlement_status_text()
                normal_app_payment_msg_upi = pax_txn_history_page.fetch_txn_payment_message_text()
                normal_app_date_and_time_upi = pax_txn_history_page.fetch_date_time_text()

                actual_app_values = {
                    "pmt_mode_bqr_1": normal_payment_mode_bqr,
                    "pmt_status_bqr_1": normal_payment_status_bqr.split(':')[1],
                    "txn_amt_bqr_1": normal_app_amount_bqr.split(' ')[1],
                    "txn_id_bqr_1": normal_app_txn_id_bqr,
                    "settle_status_bqr_1": normal_app_settlement_status_bqr,
                    "pmt_msg_bqr_1": normal_app_payment_msg_bqr,
                    "date_bqr_1": normal_app_date_and_time_bqr,

                    "pmt_mode_bqr": payment_mode_bqr,
                    "pmt_status_bqr": payment_status_bqr.split(':')[1],
                    "txn_amt_bqr": app_amount_bqr.split(' ')[1],
                    "txn_id_bqr": app_txn_id_bqr,
                    "settle_status_bqr": app_settlement_status_bqr,
                    "pmt_msg_bqr": app_payment_msg_bqr,
                    "date_bqr": app_date_and_time_bqr,

                    "pmt_mode_upi_1": normal_payment_mode_upi,
                    "pmt_status_upi_1": normal_payment_status_upi.split(':')[1],
                    "txn_amt_upi_1": normal_app_amount_upi.split(' ')[1],
                    "txn_id_upi_1": normal_app_txn_id_upi,
                    "settle_status_upi_1": normal_app_settlement_status_upi,
                    "pmt_msg_upi_1": normal_app_payment_msg_upi,
                    "date_upi_1": normal_app_date_and_time_upi,

                    "pmt_mode_upi": payment_mode_upi,
                    "pmt_status_upi": payment_status_upi.split(':')[1],
                    "txn_amt_upi": app_amount_upi.split(' ')[1],
                    "txn_id_upi": app_txn_id_upi,
                    "settle_status_upi": app_settlement_status_upi,
                    "pmt_msg_upi": app_payment_msg_upi,
                    "date_upi": app_date_and_time_upi
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            finally:
                pax_txn_history_page.click_back_Btn_transaction_details()
                pax_txn_history_page.click_back_Btn()
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            date_bqr = date_time_converter.db_datetime(txn_created_time_bqr)
            normal_date_bqr = date_time_converter.db_datetime(normal_txn_created_time_bqr)

            date_upi = date_time_converter.db_datetime(txn_created_time_upi)
            normal_date_upi = date_time_converter.db_datetime(normal_txn_created_time_upi)
            try:
                expected_api_values = {
                    "pmt_status_bqr_1": "AUTHORIZED",
                    "txn_amt_bqr_1": float(normal_amount_bqr),
                    "pmt_mode_bqr_1": "BHARATQR",
                    "pmt_state_bqr_1": "SETTLED",
                    "settle_status_bqr_1": "SETTLED",
                    "acquirer_code_bqr_1": "HDFC",
                    "issuer_code_bqr_1": "HDFC",
                    "txn_type_bqr_1": "CHARGE",
                    "mid_bqr_1": db_bqr_config_mid,
                    "tid_bqr_1": db_bqr_config_tid,
                    "org_code_bqr_1": org_code,
                    "date_bqr_1": normal_date_bqr,

                    "pmt_status_bqr": "AUTHORIZED",
                    "txn_amt_bqr": float(amount_bqr_p2p),
                    "pmt_mode_bqr": "BHARATQR",
                    "pmt_state_bqr": "SETTLED",
                    "settle_status_bqr": "SETTLED",
                    "acquirer_code_bqr": "HDFC",
                    "issuer_code_bqr": "HDFC",
                    "txn_type_bqr": "CHARGE",
                    "mid_bqr": db_bqr_config_mid,
                    "tid_bqr": db_bqr_config_tid,
                    "org_code_bqr": org_code,
                    "date_bqr": date_bqr,

                    "start_success_bqr": True,
                    "status_success_bqr": True,
                    "status_mssg_bqr": "Notification has been received on POS Device.",
                    "status_mssg_code_bqr": "P2P_DEVICE_RECEIVED",
                    "status_real_code_bqr": "P2P_DEVICE_RECEIVED",
                    "status_success_bqr_1": True,
                    "status_mssg_code_bqr_1": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_bqr_1": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_bqr_1": "Transaction done on device, Please look at Txn status.",
                    "status_username_bqr_1": app_username,
                    "status_req_id_bqr_1": request_id_bqr,

                    "pmt_status_upi_1": "AUTHORIZED",
                    "txn_amt_upi_1": float(normal_amount_upi),
                    "pmt_mode_upi_1": "UPI",
                    "pmt_state_upi_1": "SETTLED",
                    "settle_status_upi_1": "SETTLED",
                    "acquirer_code_upi_1": "HDFC",
                    "issuer_code_upi_1": "HDFC",
                    "txn_type_upi_1": "CHARGE",
                    "mid_upi_1": db_upi_config_mid,
                    "tid_upi_1": db_upi_config_tid,
                    "org_code_upi_1": org_code,
                    "date_upi_1": normal_date_upi,

                    "pmt_status_upi": "AUTHORIZED",
                    "txn_amt_upi": float(amount_upi),
                    "pmt_mode_upi": "UPI",
                    "pmt_state_upi": "SETTLED",
                    "settle_status_upi": "SETTLED",
                    "acquirer_code_upi": "HDFC",
                    "issuer_code_upi": "HDFC",
                    "txn_type_upi": "CHARGE",
                    "mid_upi": db_upi_config_mid,
                    "tid_upi": db_upi_config_tid,
                    "org_code_upi": org_code,
                    "date_upi": date_upi,

                    "start_success_upi": True,
                    "status_success_upi": True,
                    "status_mssg_upi": "Notification has been received on POS Device.",
                    "status_mssg_code_upi": "P2P_DEVICE_RECEIVED",
                    "status_real_code_upi": "P2P_DEVICE_RECEIVED",
                    "status_success_upi_1": True,
                    "status_mssg_code_upi_1": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_upi_1": "P2P_DEVICE_TXN_DONE",
                    "status_mssg_upi_1": "Transaction done on device, Please look at Txn status.",
                    "status_username_upi_1": app_username,
                    "status_req_id_upi_1": request_id_upi,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)

                response_normal_bqr = [x for x in response["txns"] if x["txnId"] == normal_txn_id_bqr][0]
                logger.debug(f"Response after filtering data of current txn is : {response_normal_bqr}")

                normal_bqr_status_api = response_normal_bqr["status"]
                normal_bqr_amount_api = float(response_normal_bqr["amount"])
                normal_bqr_payment_mode_api = response_normal_bqr["paymentMode"]
                normal_bqr_state_api = response_normal_bqr["states"][0]
                normal_bqr_settlement_status_api = response_normal_bqr["settlementStatus"]
                normal_bqr_issuer_code_api = response_normal_bqr["issuerCode"]
                normal_bqr_acquirer_code_api = response_normal_bqr["acquirerCode"]
                normal_bqr_org_code_api = response_normal_bqr["orgCode"]
                normal_bqr_mid_api = response_normal_bqr["mid"]
                normal_bqr_tid_api = response_normal_bqr["tid"]
                normal_bqr_txn_type_api = response_normal_bqr["txnType"]
                normal_bqr_date_api = response_normal_bqr["createdTime"]

                response_p2p_bqr = [x for x in response["txns"] if x["txnId"] == txn_id_bqr][0]
                logger.debug(f"Response after filtering data of current txn is : {response_p2p_bqr}")

                status_api_bqr = response_p2p_bqr["status"]
                amount_api_bqr = float(response_p2p_bqr["amount"])
                payment_mode_api_bqr = response_p2p_bqr["paymentMode"]
                state_api_bqr = response_p2p_bqr["states"][0]
                settlement_status_api_bqr = response_p2p_bqr["settlementStatus"]
                issuer_code_api_bqr = response_p2p_bqr["issuerCode"]
                acquirer_code_api_bqr = response_p2p_bqr["acquirerCode"]
                org_code_api_bqr = response_p2p_bqr["orgCode"]
                mid_api_bqr = response_p2p_bqr["mid"]
                tid_api_bqr = response_p2p_bqr["tid"]
                txn_type_api_bqr = response_p2p_bqr["txnType"]
                date_api_bqr = response_p2p_bqr["createdTime"]

                response_normal_upi = [x for x in response["txns"] if x["txnId"] == normal_txn_id_upi][0]
                logger.debug(f"Response after filtering data of current txn is : {response_normal_upi}")

                normal_upi_status_api = response_normal_upi["status"]
                normal_upi_amount_api = float(response_normal_upi["amount"])
                normal_upi_payment_mode_api = response_normal_upi["paymentMode"]
                normal_upi_state_api = response_normal_upi["states"][0]
                normal_upi_settlement_status_api = response_normal_upi["settlementStatus"]
                normal_upi_issuer_code_api = response_normal_upi["issuerCode"]
                normal_upi_acquirer_code_api = response_normal_upi["acquirerCode"]
                normal_upi_org_code_api = response_normal_upi["orgCode"]
                normal_upi_mid_api = response_normal_upi["mid"]
                normal_upi_tid_api = response_normal_upi["tid"]
                normal_upi_txn_type_api = response_normal_upi["txnType"]
                normal_upi_date_api = response_normal_upi["createdTime"]

                response_p2p_upi = [x for x in response["txns"] if x["txnId"] == txn_id_upi][0]
                logger.debug(f"Response after filtering data of current txn is : {response_p2p_upi}")

                status_api_upi = response_p2p_upi["status"]
                amount_api_upi = float(response_p2p_upi["amount"])
                payment_mode_api_upi = response_p2p_upi["paymentMode"]
                state_api_upi = response_p2p_upi["states"][0]
                settlement_status_api_upi = response_p2p_upi["settlementStatus"]
                issuer_code_api_upi = response_p2p_upi["issuerCode"]
                acquirer_code_api_upi = response_p2p_upi["acquirerCode"]
                org_code_api_upi = response_p2p_upi["orgCode"]
                mid_api_upi = response_p2p_upi["mid"]
                tid_api_upi = response_p2p_upi["tid"]
                txn_type_api_upi = response_p2p_upi["txnType"]
                date_api_upi = response_p2p_upi["createdTime"]

                actual_api_values = {
                    "pmt_status_bqr_1": normal_bqr_status_api,
                    "txn_amt_bqr_1": normal_bqr_amount_api,
                    "pmt_mode_bqr_1": normal_bqr_payment_mode_api,
                    "pmt_state_bqr_1": normal_bqr_state_api,
                    "settle_status_bqr_1": normal_bqr_settlement_status_api,
                    "acquirer_code_bqr_1": normal_bqr_acquirer_code_api,
                    "issuer_code_bqr_1": normal_bqr_issuer_code_api,
                    "mid_bqr_1": normal_bqr_mid_api,
                    "txn_type_bqr_1": normal_bqr_txn_type_api,
                    "tid_bqr_1": normal_bqr_tid_api,
                    "org_code_bqr_1": normal_bqr_org_code_api,
                    "date_bqr_1": date_time_converter.from_api_to_datetime_format(normal_bqr_date_api),

                    "pmt_status_bqr": status_api_bqr,
                    "txn_amt_bqr": amount_api_bqr,
                    "pmt_mode_bqr": payment_mode_api_bqr,
                    "pmt_state_bqr": state_api_bqr,
                    "settle_status_bqr": settlement_status_api_bqr,
                    "acquirer_code_bqr": acquirer_code_api_bqr,
                    "issuer_code_bqr": issuer_code_api_bqr,
                    "mid_bqr": mid_api_bqr,
                    "txn_type_bqr": txn_type_api_bqr,
                    "tid_bqr": tid_api_bqr,
                    "org_code_bqr": org_code_api_bqr,
                    "date_bqr": date_time_converter.from_api_to_datetime_format(date_api_bqr),

                    "start_success_bqr": start_success_bqr,
                    "status_success_bqr": status_received_success_bqr,
                    "status_mssg_bqr": status_received_mssg_bqr,
                    "status_mssg_code_bqr": status_received_mssgcode_bqr,
                    "status_real_code_bqr": status_received_realcode_bqr,
                    "status_success_bqr_1": status_after_bqr_pmt_success,
                    "status_mssg_code_bqr_1": status_after_bqr_pmt_mssgcode,
                    "status_real_code_bqr_1": status_after_bqr_pmt_realcode,
                    "status_mssg_bqr_1": status_after_bqr_pmt_mssg,
                    "status_username_bqr_1": status_after_bqr_pmt_username,
                    "status_req_id_bqr_1": status_after_bqr_pmt_rqst_id,

                    "pmt_status_upi_1": normal_upi_status_api,
                    "txn_amt_upi_1": normal_upi_amount_api,
                    "pmt_mode_upi_1": normal_upi_payment_mode_api,
                    "pmt_state_upi_1": normal_upi_state_api,
                    "settle_status_upi_1": normal_upi_settlement_status_api,
                    "acquirer_code_upi_1": normal_upi_acquirer_code_api,
                    "issuer_code_upi_1": normal_upi_issuer_code_api,
                    "mid_upi_1": normal_upi_mid_api,
                    "txn_type_upi_1": normal_upi_txn_type_api,
                    "tid_upi_1": normal_upi_tid_api,
                    "org_code_upi_1": normal_upi_org_code_api,
                    "date_upi_1": date_time_converter.from_api_to_datetime_format(normal_upi_date_api),

                    "pmt_status_upi": status_api_upi,
                    "txn_amt_upi": amount_api_upi,
                    "pmt_mode_upi": payment_mode_api_upi,
                    "pmt_state_upi": state_api_upi,
                    "settle_status_upi": settlement_status_api_upi,
                    "acquirer_code_upi": acquirer_code_api_upi,
                    "issuer_code_upi": issuer_code_api_upi,
                    "mid_upi": mid_api_upi,
                    "txn_type_upi": txn_type_api_upi,
                    "tid_upi": tid_api_upi,
                    "org_code_upi": org_code_api_upi,
                    "date_upi": date_time_converter.from_api_to_datetime_format(date_api_upi),

                    "start_success_upi": start_success_upi,
                    "status_success_upi": status_received_success_upi,
                    "status_mssg_upi": status_received_mssg_upi,
                    "status_mssg_code_upi": status_received_mssgcode_upi,
                    "status_real_code_upi": status_received_realcode_upi,
                    "status_success_upi_1": status_after_upi_pmt_success,
                    "status_mssg_code_upi_1": status_after_upi_pmt_mssgcode,
                    "status_real_code_upi_1": status_after_upi_pmt_realcode,
                    "status_mssg_upi_1": status_after_upi_pmt_mssg,
                    "status_username_upi_1": status_after_upi_pmt_username,
                    "status_req_id_upi_1": status_after_upi_pmt_rqst_id,
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
                    "txn_amt_bqr_1": float(normal_amount_bqr),
                    "pmt_status_bqr_1": "AUTHORIZED",
                    "pmt_state_bqr_1": "SETTLED",
                    "pmt_mode_bqr_1": "BHARATQR",
                    "acquirer_code_bqr_1": "HDFC",
                    "bank_code_bqr_1": "HDFC",
                    "payment_gateway_bqr_1": "HDFC",
                    "mid_bqr_1": db_bqr_config_mid,
                    "tid_bqr_1": db_bqr_config_tid,
                    "settle_status_bqr_1": "SETTLED",
                    "txn_type_bqr_1": "CHARGE",

                    "txn_amt_bqr": float(amount_bqr_p2p),
                    "pmt_status_bqr": "AUTHORIZED",
                    "pmt_state_bqr": "SETTLED",
                    "pmt_mode_bqr": "BHARATQR",
                    "acquirer_code_bqr": "HDFC",
                    "bank_code_bqr": "HDFC",
                    "payment_gateway_bqr": "HDFC",
                    "mid_bqr": db_bqr_config_mid,
                    "tid_bqr": db_bqr_config_tid,
                    "settle_status_bqr": "SETTLED",
                    "txn_type_bqr": "CHARGE",

                    "bqr_pmt_status_1": "Transaction Success",
                    "bqr_pmt_state_1": "SETTLED",
                    "bqr_txn_amt_1": normal_amount_bqr,
                    "bqr_txn_type_1": "DYNAMIC_QR",
                    "bqr_terminal_info_id_1": db_bqr_terminal_info_id,
                    "bqr_bank_code_1": "HDFC",
                    "bqr_merchant_config_id_1": db_bqr_config_id,
                    "bqr_txn_primary_id_1": normal_txn_id_bqr,
                    "bqr_merchant_pan_1": db_bqr_config_merchant_pan,
                    "bqr_org_code_1": org_code,

                    "bqr_pmt_status": "Transaction Success",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount_bqr_p2p,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": db_bqr_terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": db_bqr_config_id,
                    "bqr_txn_primary_id": txn_id_bqr,
                    "bqr_merchant_pan": db_bqr_config_merchant_pan,
                    "bqr_org_code": org_code,

                    "p2p_status_bqr": "RECEIVED",
                    "p2p_txn_id_bqr": None,
                    "p2p_status_bqr_1": "COMPLETED",
                    "p2p_txn_id_bqr_1": txn_id_bqr,

                    "txn_amt_upi_1": float(normal_amount_upi),
                    "pmt_status_upi_1": "AUTHORIZED",
                    "pmt_state_upi_1": "SETTLED",
                    "pmt_mode_upi_1": "UPI",
                    "acquirer_code_upi_1": "HDFC",
                    "bank_code_upi_1": "HDFC",
                    "payment_gateway_upi_1": "HDFC",
                    "mid_upi_1": db_upi_config_mid,
                    "tid_upi_1": db_upi_config_tid,
                    "settle_status_upi_1": "SETTLED",
                    "txn_type_upi_1": "CHARGE",

                    "txn_amt_upi": float(amount_upi),
                    "pmt_status_upi": "AUTHORIZED",
                    "pmt_state_upi": "SETTLED",
                    "pmt_mode_upi": "UPI",
                    "acquirer_code_upi": "HDFC",
                    "bank_code_upi": "HDFC",
                    "payment_gateway_upi": "HDFC",
                    "mid_upi": db_upi_config_mid,
                    "tid_upi": db_upi_config_tid,
                    "settle_status_upi": "SETTLED",
                    "txn_type_upi": "CHARGE",

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

                    "p2p_status_upi": "RECEIVED",
                    "p2p_txn_id_upi": None,
                    "p2p_status_upi_1": "COMPLETED",
                    "p2p_txn_id_upi_1": txn_id_upi

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id_bqr + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
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

                query = "select * from p2p_request where id='" + str(request_id_bqr) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_bqr_1 = result['status'].values[0]
                db_p2p_request_txn_id_bqr_1 = result['transactionId'].values[0]

                query = "select * from txn where id='" + txn_id_upi + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
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

                query = "select * from upi_txn where txn_id='" + txn_id_upi + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_org_code_db = result["org_code"].iloc[0]

                query = "select * from p2p_request where id='" + str(request_id_upi) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_upi_1 = result['status'].values[0]
                db_p2p_request_txn_id_upi_1 = result['transactionId'].values[0]


                actual_db_values = {
                    "txn_amt_bqr_1": normal_amount_db_bqr,
                    "pmt_status_bqr_1": normal_payment_status_db_bqr,
                    "pmt_state_bqr_1": normal_payment_state_db_bqr,
                    "pmt_mode_bqr_1": normal_payment_mode_db_bqr,
                    "acquirer_code_bqr_1": normal_acquirer_code_db_bqr,
                    "bank_code_bqr_1": normal_bank_code_db_bqr,
                    "payment_gateway_bqr_1": normal_payment_gateway_db_bqr,
                    "mid_bqr_1": normal_mid_db_bqr,
                    "tid_bqr_1": normal_tid_db_bqr,
                    "settle_status_bqr_1": normal_settlement_status_db_bqr,
                    "txn_type_bqr_1": normal_txn_type_db_bqr,

                    "txn_amt_bqr": amount_db_bqr,
                    "pmt_status_bqr": payment_status_db_bqr,
                    "pmt_state_bqr": payment_state_db_bqr,
                    "pmt_mode_bqr": payment_mode_db_bqr,
                    "acquirer_code_bqr": acquirer_code_db_bqr,
                    "bank_code_bqr": bank_code_db_bqr,
                    "payment_gateway_bqr": payment_gateway_db_bqr,
                    "mid_bqr": mid_db_bqr,
                    "tid_bqr": tid_db_bqr,
                    "settle_status_bqr": settlement_status_db_bqr,
                    "txn_type_bqr": txn_type_db_bqr,

                    "bqr_pmt_status_1": normal_bqr_status_db_bqr,
                    "bqr_pmt_state_1": normal_bqr_state_db_bqr,
                    "bqr_txn_amt_1": normal_bqr_amount_db_bqr,
                    "bqr_txn_type_1": normal_bqr_txn_type_db_bqr,
                    "bqr_terminal_info_id_1": normal_bqr_terminal_info_id_db_bqr,
                    "bqr_bank_code_1": normal_bqr_bank_code_db_bqr,
                    "bqr_merchant_config_id_1": normal_bqr_merchant_config_id_db_bqr,
                    "bqr_txn_primary_id_1": normal_bqr_txn_primary_id_db_bqr,
                    "bqr_merchant_pan_1": normal_bqr_merchant_pan_db_bqr,
                    "bqr_org_code_1": normal_bqr_org_code_db_bqr,

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

                    "p2p_status_bqr": db_p2p_request_status_bqr,
                    "p2p_txn_id_bqr": db_p2p_request_txn_id_bqr,
                    "p2p_status_bqr_1": db_p2p_request_status_bqr_1,
                    "p2p_txn_id_bqr_1": db_p2p_request_txn_id_bqr_1,

                    "txn_amt_upi_1": normal_amount_db_upi,
                    "pmt_status_upi_1": normal_payment_status_db_upi,
                    "pmt_state_upi_1": normal_payment_state_db_upi,
                    "pmt_mode_upi_1": normal_payment_mode_db_upi,
                    "acquirer_code_upi_1": normal_acquirer_code_db_upi,
                    "bank_code_upi_1": normal_bank_code_db_upi,
                    "payment_gateway_upi_1": normal_payment_gateway_db_upi,
                    "mid_upi_1": normal_mid_db_upi,
                    "tid_upi_1": normal_tid_db_upi,
                    "settle_status_upi_1": normal_settlement_status_db_upi,
                    "txn_type_upi_1": normal_txn_type_db_upi,

                    "txn_amt_upi": amount_db_upi,
                    "pmt_status_upi": payment_status_db_upi,
                    "pmt_state_upi": payment_state_db_upi,
                    "pmt_mode_upi": payment_mode_db_upi,
                    "acquirer_code_upi": acquirer_code_db_upi,
                    "bank_code_upi": bank_code_db_upi,
                    "payment_gateway_upi": payment_gateway_db_upi,
                    "mid_upi": mid_db_upi,
                    "tid_upi": tid_db_upi,
                    "settle_status_upi": settlement_status_db_upi,
                    "txn_type_upi": txn_type_db_upi,

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

                    "p2p_status_upi": db_p2p_request_status_upi,
                    "p2p_txn_id_upi": db_p2p_request_txn_id_upi,
                    "p2p_status_upi_1": db_p2p_request_status_upi_1,
                    "p2p_txn_id_upi_1": db_p2p_request_txn_id_upi_1,
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
def test_common_500_502_036():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Cancel_API_36
    Sub Feature Description: Sending payment notification with payment mode as BQR and cancel the notification using cancel API and do status API
    TC naming code description: 500: P2P, 502: P2P_BQR, 036: TC 036
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

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch terminal_info from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result['mid'].values[0]
        tid = result['tid'].values[0]
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

            amount = random.randint(1, 45)
            logger.info(f"Generated amount: {amount}")
            ext_ref_number = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number:  {ext_ref_number}")
            push_to = {"deviceId": ""+device_serial+"|ezetap_android"}

            # Start API for BHARATQR
            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount,
                "paymentMode": "BHARATQR",
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start}")

            request_id = resp_start['p2pRequestId']
            start_success = resp_start['success']

            sleep(2)

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

            # Cancel BQR pmt request
            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            resp_cancel_bqr = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P cancel API of BQR pmt request : {resp_cancel_bqr}")

            cancel_bqr_success = resp_cancel_bqr['success']

            payment_page = PaymentPage(app_driver)
            sleep(2)
            flow_success = payment_page.click_on_goto_homepage()

            # Check status of request after payment
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            resp_status_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P status API after BQR payment is : {resp_status_2}")

            after_cancel_success = resp_status_2['success']
            after_cancel_message_code = resp_status_2['messageCode']
            after_cancel_message = resp_status_2['message']
            after_cancel_realCode = resp_status_2['realCode']

            # Fetch values from DB table txn after payment
            query = "select * from txn where org_code='" + org_code + "' and external_ref = '" + ext_ref_number + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].values[0]
            txn_created_time = result['created_time'].values[0]

            if flow_success:
                pass
            else:
                raise Exception(f"Had to cancel BQR payment from device by clicking Back button")

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
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT FAILED",
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
            finally:
                pax_txn_history_page.click_back_Btn_transaction_details()
                pax_txn_history_page.click_back_Btn()
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

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

                    "cancel_bqr_success": True,

                    # Status after cancellation
                    "after_cancel_success": True,
                    "after_cancel_message_code": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "after_cancel_message": "PushToPay Notification has been Canceled from Billing/External System.",
                    "after_cancel_realCode": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "start_success": start_success,
                    "status_success": status_received_success,
                    "status_mssg": status_received_mssg,
                    "status_mssg_code": status_received_mssgcode,
                    "status_real_code": status_received_realcode,

                    "cancel_bqr_success": cancel_bqr_success,

                    # Status after cancellation
                    "after_cancel_success": after_cancel_success,
                    "after_cancel_message_code": after_cancel_message_code,
                    "after_cancel_message": after_cancel_message,
                    "after_cancel_realCode": after_cancel_realCode
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
                    "p2p_status_1": "CANCELED_FROM_EXTERNAL_SYSTEM",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from p2p_request where id='" + str(request_id) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_p2p_request_status_1 = result['status'].values[0]

                actual_db_values = {
                    "p2p_status_1": db_p2p_request_status_1,
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