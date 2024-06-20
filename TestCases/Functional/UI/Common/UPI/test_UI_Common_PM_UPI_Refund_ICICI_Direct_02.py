import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_101_308():
    """
    Sub Feature Code: UI_Common_PM_UPI_ICICI_Direct_Full_Refund_Via_Checkstatus
    Sub Feature Description: Perform UPI Successful and Full Refund Transactions via CheckStatus API for ICICI_DIRECT pg.
    TC naming code description: 100: Payment Method, 101: UPI, 308: TC308
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'ICICI_DIRECT';"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Value of pg_merchant_id from upi_merchant_config table is: {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Value of vpa from upi_merchant_config table is: {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table is: {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table is: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table is: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(501, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upi qr generate api : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the upi qr generate api, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for stop payment api is : {response}")

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")
            rrn = response['rrNumber']
            logger.debug(f"Fetching rrn from the payment status api, rrn : {rrn}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                        "username": app_username,
                        "password": app_password,
                        "amount": amount,
                        "originalTransactionId": txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            txn_id_refund = response['txnId']
            logger.info(f"Fetching txn id for refund txn: {txn_id_refund}")
            rrn_refund = response['rrNumber']
            logger.info(f"Fetching rrn for refund txn: {rrn_refund}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table is : {customer_name}")
            bank_name = result['bank_name'].values[0]
            logger.debug(f"Fetching bank name from txn table is : {bank_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org code from txn table is : {org_code_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table is : {auth_code}")
            status_db = result["status"].iloc[0]
            logger.info(f"Fetching status from txn table: {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.info(f"Fetching amount from txn table: {amount_db}")
            state_db = result["state"].iloc[0]
            logger.info(f"Fetching state from txn table: {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.info(f"Fetching bank code from txn table: {bank_code_db}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.info(f"Fetching bank name from txn table: {bank_name_db}")
            payer_name_db = result["payer_name"].iloc[0]
            logger.info(f"Fetching payer name from txn table: {payer_name_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            rrn_db = result["rr_number"].iloc[0]
            logger.info(f"Fetching rrn from txn table: {rrn_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].iloc[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].iloc[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_msg_db = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

            query = f"select * from txn where id = '{txn_id_refund}';"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            customer_name_refund = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from txn table is : {customer_name_refund}")
            payer_name_refund = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table is : {payer_name_refund}")
            org_code_txn_refund = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from txn table is : {org_code_txn_refund}")
            txn_type_refund = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table is : {txn_type_refund}")
            created_time_refund = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is : {created_time_refund}")
            auth_code_refund = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table is : {auth_code_refund}")
            status_db_refund = result["status"].iloc[0]
            logger.info(f"Fetching status from txn table: {status_db_refund}")
            payment_mode_db_refund = result["payment_mode"].iloc[0]
            logger.info(f"Fetching payment mode from txn table: {payment_mode_db_refund}")
            amount_db_refund = int(result["amount"].iloc[0])
            logger.info(f"Fetching amount from txn table: {amount_db_refund}")
            state_db_refund = result["state"].iloc[0]
            logger.info(f"Fetching state from txn table: {state_db_refund}")
            payment_gateway_db_refund = result["payment_gateway"].iloc[0]
            logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db_refund}")
            acquirer_code_db_refund = result["acquirer_code"].iloc[0]
            logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db_refund}")
            bank_code_db_refund = result["bank_code"].iloc[0]
            logger.info(f"Fetching bank code from txn table: {bank_code_db_refund}")
            bank_name_db_refund = result["bank_name"].iloc[0]
            logger.info(f"Fetching bank name from txn table: {bank_name_db_refund}")
            payer_name_db_refund = result["payer_name"].iloc[0]
            logger.info(f"Fetching payer name from txn table: {payer_name_db_refund}")
            settlement_status_db_refund = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db_refund}")
            rrn_db_refund = result["rr_number"].iloc[0]
            logger.info(f"Fetching rrn from txn table: {rrn_db_refund}")
            txn_type_db_refund = result["txn_type"].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db_refund}")
            tid_db_refund = result['tid'].values[0]
            logger.info(f"Fetching tid from txn table: {tid_db_refund}")
            mid_db_refund = result['mid'].values[0]
            logger.info(f"Fetching mid from txn table: {mid_db_refund}")
            error_msg_db_refund = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db_refund}")

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
        # -----------------------------------------Start of App Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_refund = date_time_converter.to_app_format(created_time_refund)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED REFUNDED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "date": date_and_time,

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "txn_id_2": txn_id_refund,
                    "rrn_2": rrn_refund,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "settle_status_2": "SETTLED",
                    "date_2": date_and_time_refund
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info("Performing Login")
                login_page.perform_login(app_username, app_password)
                logger.info("Waiting for Home Page to load")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.info("Clicking on history")
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("selecting txn by txn id")
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                order_id_app = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {order_id_app}")
                txn_id_app = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn id from txn history for the txn :, {txn_id_app}")
                status_app = transactions_history_page.fetch_txn_status_text().replace('STATUS:', '')
                logger.info(f"Fetching status from txn history for the txn : {status_app}")
                settlement_status_app = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {settlement_status_app}")
                rrn_app = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {rrn_app}")
                date_and_time_app = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {date_and_time_app}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refund)
                payment_msg_app_refund = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app_refund}")
                payment_type_app_refund = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app_refund}")
                txn_amount_app_refund = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app_refund}")
                order_id_app_refund = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {order_id_app_refund}")
                txn_id_app_refund = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn id from txn history for the txn :, {txn_id_app_refund}")
                status_app_refund = transactions_history_page.fetch_txn_status_text().replace('STATUS:', '')
                logger.info(f"Fetching status from txn history for the txn : {status_app_refund}")
                settlement_status_app_refund = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {settlement_status_app_refund}")
                rrn_app_refund = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {rrn_app_refund}")
                date_and_time_app_refund = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {date_and_time_app_refund}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "date": date_and_time_app,

                    "pmt_mode_2": payment_type_app_refund,
                    "pmt_status_2": status_app_refund,
                    "txn_amt_2": txn_amount_app_refund,
                    "txn_id_2": txn_id_app_refund,
                    "rrn_2": rrn_app_refund,
                    "order_id_2": order_id_app_refund,
                    "pmt_msg_2": payment_msg_app_refund,
                    "settle_status_2": settlement_status_app_refund,
                    "date_2": date_and_time_app_refund
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
                date = date_time_converter.db_datetime(created_time)
                refund_date = date_time_converter.db_datetime(created_time_refund)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "REFUNDED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": order_id,
                    "date": date,

                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "rrn_2": rrn_refund,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "txn_type_2": "REFUND",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "order_id_2": order_id,
                    "date_2": refund_date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                logger.debug(f"Fetching date from api response")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api response")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for refund txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_refund][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refund = response["status"]
                logger.debug(f"Fetching refund status from api response")
                amount_api_refund = response["amount"]
                logger.debug(f"Fetching refund amount from api response")
                payment_mode_api_refund = response["paymentMode"]
                logger.debug(f"Fetching refund payment mode from api response")
                state_api_refund = response["states"][0]
                logger.debug(f"Fetching refund state from api response")
                rrn_api_refund = response["rrNumber"]
                logger.debug(f"Fetching refund rrn from api response")
                settlement_status_api_refund = response["settlementStatus"]
                logger.debug(f"Fetching refund settlement status from api response")
                acquirer_code_api_refund = response["acquirerCode"]
                logger.debug(f"Fetching refund acquirer code from api response")
                org_code_api_refund = response["orgCode"]
                logger.debug(f"Fetching refund org code from api response")
                mid_api_refund = response["mid"]
                logger.debug(f"Fetching refund mid from api response")
                tid_api_refund = response["tid"]
                logger.debug(f"Fetching refund tid from api response")
                txn_type_api_refund = response["txnType"]
                logger.debug(f"Fetching refund txn type from api response")
                order_id_api_refund = response["orderNumber"]
                logger.debug(f"Fetching refund order number from api response")
                date_api_refund = response["createdTime"]
                logger.debug(f"Fetching refund date from api response")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": rrn_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),

                    "pmt_status_2": status_api_refund,
                    "txn_amt_2": amount_api_refund,
                    "pmt_mode_2": payment_mode_api_refund,
                    "pmt_state_2": state_api_refund,
                    "rrn_2": rrn_api_refund,
                    "settle_status_2": settlement_status_api_refund,
                    "acquirer_code_2": acquirer_code_api_refund,
                    "txn_type_2": txn_type_api_refund,
                    "mid_2": mid_api_refund,
                    "tid_2": tid_api_refund,
                    "org_code_2": org_code_api_refund,
                    "order_id_2": order_id_api_refund,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refund)
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
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "payer_name": payer_name,
                    "bank_name": "ICICI Bank",
                    "error_msg": "None",
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "rrn": rrn,
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,

                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "error_msg_2": "None",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "rrn_2": rrn_refund,
                    "txn_type_2": "REFUND",
                    "mid_2": mid,
                    "tid_2": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status  from upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type from upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code from upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from upi_txn table : {upi_mc_id_db}")

                query = f"select * from upi_txn where txn_id='{txn_id_refund}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refund = result["status"].iloc[0]
                logger.debug(f"Fetching refund upi_status_db from upi_txn table : {upi_status_db_refund}")
                upi_txn_type_db_refund = result["txn_type"].iloc[0]
                logger.debug(f"Fetching refund upi_txn_type from upi_txn table : {upi_txn_type_db_refund}")
                upi_bank_code_db_refund = result["bank_code"].iloc[0]
                logger.debug(f"Fetching refund upi_bank_code from upi_txn table : {upi_bank_code_db_refund}")
                upi_mc_id_db_refund = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching refund upi_mc_id from upi_txn table : {upi_mc_id_db_refund}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "payer_name": payer_name_db,
                    "bank_name": bank_name_db,
                    "error_msg": error_msg_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "rrn": rrn_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db,

                    "pmt_status_2": status_db_refund,
                    "pmt_state_2": state_db_refund,
                    "pmt_mode_2": payment_mode_db_refund,
                    "txn_amt_2": amount_db_refund,
                    "error_msg_2": error_msg_db_refund,
                    "settle_status_2": settlement_status_db_refund,
                    "acquirer_code_2": acquirer_code_db_refund,
                    "pmt_gateway_2": payment_gateway_db_refund,
                    "upi_txn_status_2": upi_status_db_refund,
                    "upi_txn_type_2": upi_txn_type_db_refund,
                    "upi_bank_code_2": upi_bank_code_db_refund,
                    "upi_mc_id_2": upi_mc_id_db_refund,
                    "rrn_2": rrn_db_refund,
                    "txn_type_2": txn_type_db_refund,
                    "mid_2": mid_db_refund,
                    "tid_2": tid_db_refund
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_refund = date_time_converter.to_portal_format(created_time_refund)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": rrn,

                    "date_time_2": date_and_time_portal_refund,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_refund,
                    "rrn_2": rrn_refund
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[1]['Date & Time']
                logger.info(f"Fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[1]['Transaction ID']
                logger.info(f"Fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[1]['Total Amount'].split()
                logger.debug(f"Fetching total amount from portal {total_amount_portal}")
                rr_number_portal = transaction_details[1]['RR Number']
                logger.debug(f"Fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[1]['Type']
                logger.info(f"Fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[1]['Status']
                logger.info(f"Fetching status {status_portal}")
                username_portal = transaction_details[1]['Username']
                logger.info(f"Fetching username from portal {username_portal}")

                date_time_portal_refund = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date time from portal {date_time_portal_refund}")
                transaction_id_portal_refund = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal {transaction_id_portal_refund}")
                total_amount_portal_refund = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total amount from portal {total_amount_portal_refund}")
                rr_number_portal_refund = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rr_number from portal {rr_number_portal_refund}")
                transaction_type_portal_refund = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal {transaction_type_portal_refund}")
                status_portal_refund = transaction_details[0]['Status']
                logger.info(f"Fetching status {status_portal_refund}")
                username_portal_refund = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal {username_portal_refund}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "rrn": rr_number_portal,

                    "date_time_2": date_time_portal_refund,
                    "pmt_state_2": status_portal_refund,
                    "pmt_type_2": transaction_type_portal_refund,
                    "txn_amt_2": total_amount_portal_refund[1],
                    "username_2": username_portal_refund,
                    "txn_id_2": transaction_id_portal_refund,
                    "rrn_2": rr_number_portal_refund
                }

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_refund)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn_refund),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code_refund is None else auth_code_refund
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id_refund, {"username": app_username,
                                                                "password": app_password}, expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation----------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)