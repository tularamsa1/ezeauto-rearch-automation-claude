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
def test_common_100_102_320():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_UPI_Refund_via_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_UPI Refund transaction via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 320: TC320
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

        query = "select * from upi_merchant_config where bank_code = 'YES' AND status = 'ACTIVE' AND org_code = '" + str(org_code) + "'; "
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from the upi_merchant_config table : vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : upi_mc_id : {upi_mc_id}")

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
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(301, 400)
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

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for UPI Stop Payment : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn}")
            posting_date = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {posting_date}")
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
            posting_date_refunded = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table after refund is : {posting_date_refunded}")
            status_db_refunded = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table after refund is  : {status_db_refunded}")
            payment_mode_db_refunded = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table after refund is : {payment_mode_db_refunded}")
            amount_db_refunded = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table after refund is  : {amount_db_refunded}")
            state_db_refunded = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table after refund is : {state_db_refunded}")
            payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table after refund is : {payment_gateway_db_refunded}")
            acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table after refund is : {acquirer_code_db_refunded}")
            settlement_status_db_refunded = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table after refund is : {settlement_status_db_refunded}")
            tid_db_refunded = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table after refund is : {tid_db_refunded}")
            mid_db_refunded = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table after refund is : {mid_db_refunded}")

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                refund_date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED REFUNDED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": txn_id_refunded,
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_amt_2": "{:.2f}".format(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
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
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_refunded}")

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
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching payment msg of original txn from transaction history of MPOS app: Txn Id = {payment_msg_original}")

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
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
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
                date = date_time_converter.db_datetime(posting_date)
                refund_date = date_time_converter.db_datetime(posting_date_refunded)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn),
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "acquirer_code_2": "YES",
                    "txn_type_2": "REFUND",
                    "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code": auth_code,
                    "date": date,
                    "date_2": refund_date,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api_original = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api_original}")
                amount_api_original = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api_original}")
                payment_mode_api_original = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api_original}")
                state_api_original = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api_original}")
                settlement_status_api_original = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api_original}")
                rrn_api_original = response_1["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api_original}")
                issuer_code_api_original = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api_original}")
                acquirer_code_api_original = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api_original}")
                org_code_api_original = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api_original}")
                mid_api_original = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api_original}")
                tid_api_original = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api_original}")
                txn_type_api_original = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api_original}")
                auth_code_api_original = response_1["authCode"]
                logger.debug(f"Value of authCode obtained from txnlist api is : {auth_code_api_original}")
                date_api_original = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api_original}")
                device_serial_api_original = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api_original}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of refund txn api is : {response_2}")
                status_api_refunded = response_2["status"]
                logger.debug(f"Value of status obtained from refund txnlist api is : {status_api_refunded}")
                amount_api_refunded = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from refund txnlist api is : {amount_api_refunded}")
                payment_mode_api_refunded = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from refund txnlist api is : {payment_mode_api_refunded}")
                state_api_refunded = response_2["states"][0]
                logger.debug(f"Value of states obtained from refund txnlist api is : {state_api_refunded}")
                rrn_api_refunded = response_2["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from refund txnlist api is : {rrn_api_refunded}")
                settlement_status_api_refunded = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from refund txnlist api is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from refund txnlist api is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from refund txnlist api is : {org_code_api_refunded}")
                mid_api_refunded = response_2["mid"]
                logger.debug(f"Value of mid obtained from refund txnlist api is : {mid_api_refunded}")
                tid_api_refunded = response_2["tid"]
                logger.debug(f"Value of tid obtained from refund txnlist api is : {tid_api_refunded}")
                txn_type_api_refunded = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from refund txnlist api is : {txn_type_api_refunded}")
                date_api_refunded = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from refund txnlist api is : {date_api_refunded}")
                order_id_api_refunded = response_2["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from refund txnlist api is : {order_id_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt": amount_api_original,
                    "txn_amt_2": amount_api_refunded,
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "auth_code": auth_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "device_serial": str(device_serial_api_original)
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
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "YES",
                    "acquirer_code_2": "YES",
                    "bank_code": "YES",
                    "pmt_gateway": "ATOS",
                    "pmt_gateway_2": "ATOS",
                    "upi_txn_type": "PAY_BQR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "YES",
                    "upi_bank_code_2": "YES",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on refund txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table based on refund txn_id : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table based on refund txn_id : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table based on refund txn_id : {upi_txn_type_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table based on refund txn_id : {upi_mc_id_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table based on refund txn_id : {upi_bank_code_db_refunded}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table for DB Validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table for DB Validation  : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from txn table for DB Validation : {status_db_original}")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"Value of payment_mode obtained from txn table for DB Validation : {payment_mode_db_original}")
                amount_db_original = float(result["amount"].iloc[0])
                logger.debug(f"Value of amount obtained from txn table for DB Validation : {amount_db_original}")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from txn table for DB Validation : {state_db_original}")
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                logger.debug(f"Value of payment_gateway obtained from txn table for DB Validation : {payment_gateway_db_original}")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"Value of acquirer_code obtained from txn table for DB Validation : {acquirer_code_db_original}")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from txn table for DB Validation : {bank_code_db_original}")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"Value of settlement_status obtained from txn table for DB Validation : {settlement_status_db_original}")
                tid_db_original = result['tid'].values[0]
                logger.debug(f"Value of tid obtained from txn table for DB Validation : {tid_db_original}")
                mid_db_original = result['mid'].values[0]
                logger.debug(f"Value of mid obtained from txn table for DB Validation : {mid_db_original}")

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table : {upi_txn_type_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table : {upi_mc_id_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table : {upi_bank_code_db_original}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db_original,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db_original,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db_original,
                    "pmt_gateway": payment_gateway_db_original,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id": upi_mc_id_db_original,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid": mid_db_original,
                    "tid": tid_db_original,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                    "device_serial": str(device_serial_db)
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation------------------------------------------

        # -----------------------------------------Start of Portal Validation------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(posting_date)
                date_and_time_portal_new = date_time_converter.to_portal_format(posting_date_refunded)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else rrn,
                    "date_time_2": date_and_time_portal_new,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "auth_code_2": "-" if auth_code_refunded is None else auth_code_refunded,
                    "rrn_2": "-" if rrn_refunded is None else rrn_refunded,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_new = transaction_details[0]['Date & Time']
                transaction_id_new = transaction_details[0]['Transaction ID']
                total_amount_new = transaction_details[0]['Total Amount'].split()
                auth_code_portal_new = transaction_details[0]['Auth Code']
                rr_number_new = transaction_details[0]['RR Number']
                transaction_type_new = transaction_details[0]['Type']
                status_new = transaction_details[0]['Status']
                username_new = transaction_details[0]['Username']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_new,
                    "pmt_state_2": str(status_new),
                    "pmt_type_2": transaction_type_new,
                    "txn_amt_2": total_amount_new[1],
                    "username_2": username_new,
                    "txn_id_2": transaction_id_new,
                    "auth_code_2": auth_code_portal_new,
                    "rrn_2": rr_number_new
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_refunded)
                expected_values = {'PAID BY:': 'UPI',
                                   'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn_refunded),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date,
                                   'time': txn_time
                                   }
                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": app_username, "password": app_password},
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