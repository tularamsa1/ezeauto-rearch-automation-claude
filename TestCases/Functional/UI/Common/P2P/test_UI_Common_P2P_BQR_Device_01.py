import string
import sys
from time import sleep
import pytest
import random
from Configuration import testsuite_teardown, Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.PAX_TransHistoryPage import PaxTransHistoryPage
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, date_time_converter, ConfigReader, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
def test_common_500_502_016():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Kill_App_With_Autologin_16
    Sub Feature Description: Kill the app and check P2P connection after relaunching the app, enabling autologin and do BQR txn
    TC naming code description: 500: P2P, 502: P2P_BQR, 016: TC 016
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
                raise Exception("Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.info(f"P2P notification message on device is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification message mismatch on device. Actual P2P notification : {actual_notification}")

            app_driver.back()

            app_driver.terminate_app("com.ezetap.basicapp")
            logger.debug(f"Killed the app")

            app_driver.activate_app("com.ezetap.basicapp")
            logger.debug(f"Relaunched the app")

            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"Logged in to the app again after relaunching")
            logger.info(f"Loaded home page again after relaunching")

            # Checking redis connection after relaunching the app
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server after relaunching the app")

            # Checking P2P notification after relaunching the app
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification after relaunching the app")
            try:
                actual_notification2 = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception("Exception in locating P2P notification on device after relaunching the app")

            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification2 == expected_notification:
                logger.info(f"P2P notification message on device after relaunching the app is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device after relaunching the app. Actual notification : {actual_notification2}")

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
            payment_page.is_payment_page_displayed_P2P()
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            logger.info(f"Clicked on back button")
            payment_page.click_on_transaction_cancel_yes()
            logger.info(f"Confirmed to cancel payment")
            sleep(2)
            payment_page.click_on_proceed_homepage()
            logger.info(f"Clicked on button to redirect to HomePage")

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

                actual_api_values = {
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
def test_common_500_502_017():
    """
    Sub Feature Code: UI_Common_P2P_BQR_Reconnect_Network_Success_Transaction_17
    Sub Feature Description: Turnoff network from device after receiving notification and do successful transaction after network is back
    TC naming code description: 500: P2P, 502: P2P_BQR, 017: TC017
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQR')
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

        query = "select * from bharatqr_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        bqr_config_mid_db = result['mid'].values[0]
        logger.info(f"from bharatqr_merchant_config, mid is : {bqr_config_mid_db}")
        bqr_config_tid_db = result['tid'].values[0]
        logger.info(f"from bharatqr_merchant_config, tid is : {bqr_config_tid_db}")
        bqr_config_id_db = result['id'].values[0]
        logger.info(f"from bharatqr_merchant_config, bqr_config_id is : {bqr_config_id_db}")
        bqr_terminal_info_id_db = result['terminal_info_id'].values[0]
        logger.info(f"from bharatqr_merchant_config, bqr_terminal_info_id_db is : {bqr_terminal_info_id_db}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"from bharatqr_merchant_config, db_bqr_config_merchant_pan is : {db_bqr_config_merchant_pan}")

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

            amount = random.randint(401, 999)
            logger.debug(f"amount random number is: {amount}")

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": app_key,
                "amount": amount,
                "paymentMode": "BHARATQR",
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

            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification2 == expected_notification:
                logger.info(f"P2P notification message on device after network reconnection is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device after network reconnection. Actual notification {actual_notification2}")

            app_driver.back()

            sleep(3)
            payment_page = PaymentPage(app_driver)
            payment_page.is_qrcode_displayed_P2P()
            payment_page.validate_upi_bqr_payment_screen()
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            payment_page.click_on_proceed_homepage()

            sleep(2)

            #check DB and status api after txn is done
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"After txn response obtained for Status api is : {response}")
            status_success_2 = response['success']
            logger.debug(f"After txn response obtained for Status api, status_success_2 is : {status_success_2}")
            status_message_code_2 = response['messageCode']
            logger.debug(f"After txn response obtained for Status api, status_message_code_2 is : {status_message_code_2}")
            status_message_2 = response['message']
            logger.debug(f"After txn response obtained for Status api, status_message_2 is : {status_message_2}")
            status_real_code_2 = response['realCode']
            logger.debug(f"After txn response obtained for Status api, status_real_code_2 is : {status_real_code_2}")
            status_username_2 = response['username']
            logger.debug(f"After txn response obtained for Status api, status_username_2 is : {status_username_2}")
            status_p2p_request_id_2 = response['p2pRequestId']
            logger.debug(f"After txn response obtained for Status api, status_p2p_request_id_2 is : {status_p2p_request_id_2}")
            status_txn_id = response['txnId']
            logger.debug(f"After txn response obtained for Status api, status_txn_id is : {status_txn_id}")

            # after txn
            query = "select * from txn where id='" + str(status_txn_id) + "';"
            logger.debug(f"Query to fetch details from DB table txn after BQR payment : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Query to fetch txn_created_time value is : {txn_created_time}")

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

        # -----------------------------------------Start of App Validation------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            date_and_time = date_time_converter.to_app_format(txn_created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": status_txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                sleep(2)
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(str(external_ref_num))

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {status_txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {status_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {status_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {status_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {status_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {status_txn_id}, {app_payment_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {status_txn_id}, {app_date_and_time}")

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
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": bqr_config_mid_db,
                    "tid": bqr_config_tid_db,
                    "org_code": org_code,
                    "date": date,
                    "start_success": True,
                    "status_success": True,
                    "status_msg": "Notification has been received on POS Device.",
                    "status_msg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",
                    "status_success_2": True,
                    "status_msg_code_2": "P2P_DEVICE_TXN_DONE",
                    "status_real_code_2": "P2P_DEVICE_TXN_DONE",
                    "status_msg_2": "Transaction done on device, Please look at Txn status.",
                    "status_username_2": app_username,
                    "status_req_id_2": start_p2p_request_id,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })

                response = APIProcessor.send_request(api_details)
                response = [x for x in response["txns"] if x["txnId"] == status_txn_id][0]
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

                actual_api_values = {
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
                    "txn_amt": float(amount),
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "BHARATQR",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "settle_status": "SETTLED",
                    "txn_type": "CHARGE",
                    "mid": bqr_config_mid_db,
                    "tid": bqr_config_tid_db,
                    "bqr_pmt_status": "Transaction Success",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_config_id_db,
                    "bqr_txn_primary_id": status_txn_id,
                    "bqr_merchant_pan": db_bqr_config_merchant_pan,
                    "bqr_org_code": org_code,
                    "p2p_status": "RECEIVED",
                    "p2p_status_2": "COMPLETED",
                    "p2p_txn_id": status_txn_id
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + status_txn_id + "';"
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

                query = "select * from bharatqr_txn where id='" + status_txn_id + "';"
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

                query = "select * from p2p_request where id='" + str(start_p2p_request_id) + "';"
                logger.debug(f"Query to fetch data from p2p_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result['status'].values[0]
                txn_id_db_2 = result['transactionId'].values[0]

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "pmt_mode": payment_mode_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
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
                    "p2p_status": status_db,
                    "p2p_status_2": status_db_2,
                    "p2p_txn_id": txn_id_db_2,
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