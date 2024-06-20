import sys
import random
import pytest
from datetime import datetime
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities.execution_log_processor import EzeAutoLogger
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, receipt_validator, date_time_converter

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_313():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_BQR_Refund_API_Via_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_BQR Refund transaction through API via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 313: TC313
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(401, 1000)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")

            # hit the stop payment
            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR Stop Payment : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_time}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")

            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for payment refund is: {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch data from txn table after refund is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table after refund is : {result}")
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from txn table after refund is : {txn_id_refunded}")
            auth_code_refunded = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table after refund is : {auth_code_refunded}")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table after refund is : {rrn_refunded}")
            created_time_refunded = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table after refund is : {created_time_refunded}")
            status_db_new_2 = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table after refund is : {status_db_new_2}")
            payment_mode_db_new_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table after refund is : {payment_mode_db_new_2}")
            amount_db_new_2 = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table after refund is : {amount_db_new_2}")
            state_db_new_2 = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table after refund is : {state_db_new_2}")
            payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table after refund is : {payment_gateway_db_new_2}")
            acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table after refund is : {acquirer_code_db_new_2}")
            settlement_status_db_new_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table after refund is: {settlement_status_db_new_2}")
            tid_db_new_2 = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table after refund is: {tid_db_new_2}")
            mid_db_new_2 = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table after refund is : {mid_db_new_2}")
            order_id_db_new_2 = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table after refund is : {order_id_db_new_2}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                refund_date_and_time = date_time_converter.to_app_format(created_time_refunded)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED REFUNDED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "BHARAT QR",
                    "pmt_mode_2": "BHARAT QR",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": txn_id_refunded,
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_amt_2": "{:.2f}".format(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "pmt_msg": "REFUND SUCCESSFUL",
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "rrn": str(rrn),
                    "rrn_2": str(rrn_refunded),
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "date_2": refund_date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)
                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_customer_name_refunded = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_refunded}, {app_customer_name_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_customer_name_original = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_original}")
                app_order_id_original = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id_original}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name": app_customer_name_original,
                    "customer_name_2": app_customer_name_refunded,
                    "order_id": app_order_id_original,
                    "order_id_2": app_order_id_refunded,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "rrn_2": str(app_rrn_refunded),
                    "auth_code": app_auth_code_original,
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_refunded
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
                date_new = date_time_converter.db_datetime(created_time)
                date_new_2 = date_time_converter.db_datetime(created_time_refunded)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_new,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "REFUNDED",
                    "rrn_2": str(rrn_refunded),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "txn_type_2": "REFUND",
                    "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_new_2,
                    "order_id_2": order_id
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api}")
                amount_api = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Value of authCode obtained from txnlist api is : {auth_code_api}")
                date_api = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")
                order_id_api = response_1["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from txnlist api is : {order_id_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of refund txn api is : {response_2}")
                status_api_new_2 = response_2["status"]
                logger.debug(f"Value of status obtained from refund txnlist api is : {status_api_new_2}")
                amount_api_new_2 = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from refund txnlist api is : {amount_api_new_2}")
                payment_mode_api_new_2 = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from refund txnlist api is : {payment_mode_api_new_2}")
                state_api_new_2 = response_2["states"][0]
                logger.debug(f"Value of states obtained from refund txnlist api is : {state_api_new_2}")
                rrn_api_new_2 = response_2["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from refund txnlist api is : {rrn_api_new_2}")
                settlement_status_api_new_2 = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from refund txnlist api is : {settlement_status_api_new_2}")
                acquirer_code_api_new_2 = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from refund txnlist api is : {acquirer_code_api_new_2}")
                org_code_api_new_2 = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from refund txnlist api is : {org_code_api_new_2}")
                mid_api_new_2 = response_2["mid"]
                logger.debug(f"Value of mid obtained from refund txnlist api is : {mid_api_new_2}")
                tid_api_new_2 = response_2["tid"]
                logger.debug(f"Value of tid obtained from refund txnlist api is : {tid_api_new_2}")
                txn_type_api_new_2 = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from refund txnlist api is : {txn_type_api_new_2}")
                date_api_new_2 = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from refund txnlist api is : {date_api_new_2}")
                order_id_api_new_2 = response_2["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from refund txnlist api is : {order_id_api_new_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "device_serial": str(device_serial_api),
                    "pmt_status_2": status_api_new_2,
                    "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2,
                    "rrn_2": str(rrn_api_new_2),
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2,
                    "mid_2": mid_api_new_2,
                    "tid_2": tid_api_new_2,
                    "org_code_2": org_code_api_new_2,
                    "order_id_2": order_id_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2)
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
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "BHARATQR",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_code": "YES",
                    "payment_gateway": "ATOS",
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "bqr_pmt_status": "SUCCESS",
                    "bqr_pmt_state": "REFUNDED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "YES",
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": float(amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "payment_gateway_2": "ATOS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "order_id_2": order_id
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table for DB Validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table for DB Validation : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from txn table for DB validation : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Value of payment_mode obtained from txn table for DB validation : {payment_mode_db}")
                amount_db = float(result["amount"].iloc[0])
                logger.debug(f"Value of amount obtained from txn table for DB validation : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from txn table for DB validation : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Value of payment_gateway obtained from txn table for DB validation : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Value of acquirer_code obtained from txn table for DB validation : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from txn table for DB validation : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Value of settlement_status obtained from txn table for DB validation : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Value of tid obtained from txn table for DB validation : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Value of mid obtained from txn table for DB validation : {mid_db}")
                order_id_db = result['external_ref'].values[0]
                logger.debug(f"Value of external_ref obtained from txn table for DB validation : {order_id_db}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for DB validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for DB validation : {result}")
                bqr_status_db = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from bharatqr_txn table for DB validation : {bqr_status_db}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for DB validation : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for DB validation : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for DB validation : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for DB validation : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for DB validation : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for DB validation : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for DB validation : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for DB validation : {bqr_org_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "order_id": order_id_db,
                    "device_serial": str(device_serial_db),
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "mid_2": mid_db_new_2,
                    "tid_2": tid_db_new_2,
                    "order_id_2": order_id_db_new_2
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_refunded)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "rrn_2": rrn_refunded
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_refunded)
                expected_values = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn_refunded),'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date, 'time': txn_time
                                   }
                receipt_validator.perform_charge_slip_validations(txn_id_refunded,{"username": app_username,"password": app_password},
                                                                  expected_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

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
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_316():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_BQR_Refund_Posted_via_API_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_BQR Refund posted transaction through API via YES ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 316: TC316
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 555
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")

            # hit the stop payment
            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR Stop Payment : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_time}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")

            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "originalTransactionId": str(txn_id)
             })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for payment refund is: {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch data from txn table after refund is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table after refund is : {result}")
            txn_id_new_2 = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from txn table after refund is : {txn_id_new_2}")
            rrn_new_2 = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table after refund is : {rrn_new_2}")
            customer_name_new_2 = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table after refund is : {customer_name_new_2}")
            payer_name_new_2 = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table after refund is : {payer_name_new_2}")
            auth_code_new_2 = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table after refund is : {auth_code_new_2}")
            created_time_new_2 = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table after refund is : {created_time_new_2}")
            status_db_new_2 = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table after refund is : {status_db_new_2}")
            payment_mode_db_new_2 = result["payment_mode"].iloc[0]
            logger.debug( f"Value of payment_mode obtained from txn table after refund is : {payment_mode_db_new_2}")
            amount_db_new_2 = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table after refund is : {amount_db_new_2}")
            state_db_new_2 = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table after refund is : {state_db_new_2}")
            payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table after refund is : {payment_gateway_db_new_2}")
            acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table after refund is : {acquirer_code_db_new_2}")
            settlement_status_db_new_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table after refund is : {settlement_status_db_new_2}")
            order_id_db_new_2 = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table after refund is : {order_id_db_new_2}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_new_2)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "REFUND_POSTED",
                    "txn_amt_2": str(amount) + ".00",
                    "settle_status_2": "REVPENDING",
                    "txn_id_2": txn_id_new_2,
                    "rrn_2": str(rrn_new_2),
                    "customer_name_2": customer_name_new_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND PENDING",
                    "date_2": date_and_time_new_2
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new_2)
                payment_status_new_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new_2}, {payment_status_new_2}")
                app_date_and_time_new_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new_2}, {app_date_and_time_new_2}")
                payment_mode_new_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new_2}, {payment_mode_new_2}")
                app_txn_id_new_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_2}, {app_txn_id_new_2}")
                app_amount_new_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new_2}, {app_amount_new_2}")
                app_customer_name_new_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new_2}, {app_customer_name_new_2}")
                app_settlement_status_new_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_new_2}, {app_settlement_status_new_2}")
                app_payment_msg_new_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new_2}, {app_payment_msg_new_2}")
                app_order_id_new_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new_2}, {app_order_id_new_2}")
                app_rrn_new_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_2}, {app_rrn_new_2}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new_2,
                    "pmt_status_2": payment_status_new_2.split(':')[1],
                    "txn_amt_2": app_amount_new_2.split(' ')[1],
                    "txn_id_2": app_txn_id_new_2,
                    "rrn_2": str(app_rrn_new_2),
                    "customer_name_2": app_customer_name_new_2,
                    "settle_status_2": app_settlement_status_new_2,
                    "order_id_2": app_order_id_new_2,
                    "pmt_msg_2": app_payment_msg_new_2,
                    "date_2": app_date_and_time_new_2
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
                date_new = date_time_converter.db_datetime(created_time)
                date_new_2 = date_time_converter.db_datetime(created_time_new_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_new,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "REFUND_POSTED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "REFUND_INITIATED",
                    "rrn_2": str(rrn_new_2),
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "YES",
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "date_2": date_new_2,
                    "order_id_2": order_id
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api}")
                amount_api = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Value of authCode obtained from txnlist api is : {auth_code_api}")
                date_api = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")
                order_id_api = response_1["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from txnlist api is : {order_id_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_new_2][0]
                logger.debug(f"Response after filtering data of refund txn is : {response_2}")
                status_api_new_2 = response_2["status"]
                logger.debug(f"Value of status obtained from refund txn is : {status_api_new_2}")
                amount_api_new_2 = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from refund txn is : {amount_api_new_2}")
                payment_mode_api_new_2 = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from refund txn is : {payment_mode_api_new_2}")
                state_api_new_2 = response_2["states"][0]
                logger.debug(f"Value of states obtained from refund txn is : {state_api_new_2}")
                rrn_api_new_2 = response_2["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from refund txn is : {rrn_api_new_2}")
                settlement_status_api_new_2 = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from refund txn is : {settlement_status_api_new_2}")
                acquirer_code_api_new_2 = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from refund txn is : {acquirer_code_api_new_2}")
                org_code_api_new_2 = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from refund txn is : {org_code_api_new_2}")
                txn_type_api_new_2 = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from refund txn is : {txn_type_api_new_2}")
                date_api_new_2 = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from refund txn is : {date_api_new_2}")
                order_id_api_new_2 = response_2["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from refund txn is : {order_id_api_new_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "device_serial": str(device_serial_api),
                    "pmt_status_2": status_api_new_2,
                    "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2,
                    "rrn_2": str(rrn_api_new_2),
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2,
                    "org_code_2": org_code_api_new_2,
                    "order_id_2": order_id_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2)
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "BHARATQR",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_code": "YES",
                    "payment_gateway": "ATOS",
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "YES",
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": float(amount),
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "YES",
                    "payment_gateway_2": "ATOS",
                    "order_id_2": order_id
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table for DB Validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table for DB Validation : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from txn table for DB validation : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Value of payment_mode obtained from txn table for DB validation : {payment_mode_db}")
                amount_db = float(result["amount"].iloc[0])
                logger.debug(f"Value of amount obtained from txn table for DB validation : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from txn table for DB validation : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Value of payment_gateway obtained from txn table for DB validation : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Value of acquirer_code obtained from txn table for DB validation : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from txn table for DB validation : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Value of settlement_status obtained from txn table for DB validation : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Value of tid obtained from txn table for DB validation : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Value of mid obtained from txn table for DB validation : {mid_db}")
                order_id_db = result['external_ref'].values[0]
                logger.debug(f"Value of external_ref obtained from txn table for DB validation : {order_id_db}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table : {bqr_org_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "order_id": order_id_db,
                    "device_serial": str(device_serial_db),
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "order_id_2": order_id_db_new_2
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_new_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUND_POSTED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_new_2,
                    "rrn_2": rrn_new_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id),'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),'date': txn_date,
                    'time': txn_time, 'AUTH CODE': auth_code.strip()
                }
                receipt_validator.perform_charge_slip_validations(txn_id, {"username": app_username,
                                                                           "password": app_password},
                                                                  expected_charge_slip_values)

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

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
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_317():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_BQR_Refund_Failed_via_API_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_BQR Refund Failed transaction through API via YES ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 317: TC317
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 444
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")

            # hit the stop payment
            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR Stop Payment : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_time}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")

            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "originalTransactionId": str(txn_id)
             })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for payment refund is: {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch data from txn table after refund is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table after refund is : {result}")
            txn_id_new_2 = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from txn table after refund is : {txn_id_new_2}")
            rrn_new_2 = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table after refund is : {rrn_new_2}")
            customer_name_new_2 = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table after refund is : {customer_name_new_2}")
            auth_code_new_2 = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table after refund is : {auth_code_new_2}")
            created_time_new_2 = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table after refund is : {created_time_new_2}")
            status_db_new_2 = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table after refund is : {status_db_new_2}")
            payment_mode_db_new_2 = result["payment_mode"].iloc[0]
            logger.debug( f"Value of payment_mode obtained from txn table after refund is : {payment_mode_db_new_2}")
            amount_db_new_2 = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table after refund is : {amount_db_new_2}")
            state_db_new_2 = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table after refund is : {state_db_new_2}")
            payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table after refund is : {payment_gateway_db_new_2}")
            acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table after refund is : {acquirer_code_db_new_2}")
            settlement_status_db_new_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table after refund is : {settlement_status_db_new_2}")
            order_id_db_new_2 = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table after refund is : {order_id_db_new_2}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_new_2)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "FAILED",
                    "txn_amt_2": str(amount) + ".00",
                    "settle_status_2": "FAILED",
                    "txn_id_2": txn_id_new_2,
                    "customer_name_2": customer_name_new_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT FAILED",
                    "date_2": date_and_time_new_2
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new_2)
                payment_status_new_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new_2}, {payment_status_new_2}")
                app_date_and_time_new_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new_2}, {app_date_and_time_new_2}")
                payment_mode_new_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new_2}, {payment_mode_new_2}")
                app_txn_id_new_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_2}, {app_txn_id_new_2}")
                app_amount_new_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new_2}, {app_amount_new_2}")
                app_customer_name_new_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new_2}, {app_customer_name_new_2}")
                app_settlement_status_new_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_new_2}, {app_settlement_status_new_2}")
                app_payment_msg_new_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new_2}, {app_payment_msg_new_2}")
                app_order_id_new_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new_2}, {app_order_id_new_2}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new_2,
                    "pmt_status_2": payment_status_new_2.split(':')[1],
                    "txn_amt_2": app_amount_new_2.split(' ')[1],
                    "txn_id_2": app_txn_id_new_2,
                    "customer_name_2": app_customer_name_new_2,
                    "settle_status_2": app_settlement_status_new_2,
                    "order_id_2": app_order_id_new_2,
                    "pmt_msg_2": app_payment_msg_new_2,
                    "date_2": app_date_and_time_new_2
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation-------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_new = date_time_converter.db_datetime(created_time)
                date_new_2 = date_time_converter.db_datetime(created_time_new_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_new,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "FAILED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "FAILED",
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "YES",
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "date_2": date_new_2,
                    "order_id_2": order_id
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api}")
                amount_api = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Value of authCode obtained from txnlist api is : {auth_code_api}")
                date_api = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")
                order_id_api = response_1["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from txnlist api is : {order_id_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_new_2][0]
                logger.debug(f"Response after filtering data of refund txn is : {response_2}")
                status_api_new_2 = response_2["status"]
                logger.debug(f"Value of status obtained from refund txnlist api is  : {status_api_new_2}")
                amount_api_new_2 = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from refund txnlist api is : {amount_api_new_2}")
                payment_mode_api_new_2 = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from refund txnlist api is: {payment_mode_api_new_2}")
                state_api_new_2 = response_2["states"][0]
                logger.debug(f"Value of states obtained from refund txnlist api is : {state_api_new_2}")
                settlement_status_api_new_2 = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from refund txnlist api is : {settlement_status_api_new_2}")
                acquirer_code_api_new_2 = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from refund txnlist api is : {acquirer_code_api_new_2}")
                org_code_api_new_2 = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from refund txnlist api is: {org_code_api_new_2}")
                txn_type_api_new_2 = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from refund txnlist api is: {txn_type_api_new_2}")
                date_api_new_2 = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from refund txnlist api is : {date_api_new_2}")
                order_id_api_new_2 = response_2["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from refund txnlist api is : {order_id_api_new_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "order_id": order_id_api,
                    "device_serial": str(device_serial_api),
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2,
                    "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2,
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2,
                    "org_code_2": org_code_api_new_2,
                    "order_id_2": order_id_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2)
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "BHARATQR",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_code": "YES",
                    "payment_gateway": "ATOS",
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "YES",
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "FAILED",
                    "pmt_state_2": "FAILED",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": float(amount),
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "YES",
                    "payment_gateway_2": "ATOS",
                    "order_id_2": order_id
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table for DB Validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table for DB Validation : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from txn table for DB validation : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Value of payment_mode obtained from txn table for DB validation : {payment_mode_db}")
                amount_db = float(result["amount"].iloc[0])
                logger.debug(f"Value of amount obtained from txn table for DB validation : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from txn table for DB validation : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Value of payment_gateway obtained from txn table for DB validation : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Value of acquirer_code obtained from txn table for DB validation : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from txn table for DB validation : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Value of settlement_status obtained from txn table for DB validation : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Value of tid obtained from txn table for DB validation : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Value of mid obtained from txn table for DB validation : {mid_db}")
                order_id_db = result['external_ref'].values[0]
                logger.debug(f"Value of external_ref obtained from txn table for DB validation : {order_id_db}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table : {bqr_org_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "order_id": order_id_db,
                    "device_serial": str(device_serial_db),
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "order_id_2": order_id_db_new_2
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_new_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "FAILED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_new_2,
                    "rrn_2": rrn_new_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount), 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': auth_code.strip()
                }
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)