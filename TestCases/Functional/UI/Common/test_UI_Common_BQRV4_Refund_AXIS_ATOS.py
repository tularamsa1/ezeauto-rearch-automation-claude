import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_081():
    """
    :Description: Verification of a BQRV4 Refund transaction via AXIS_ATOS
    :Sub feature code: UI_Common_BQRV4_Refund_via_AXIS_ATOS_081
    :TC naming code description:100->Payment Method, 102->BQR, 062-> TC081
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'AXIS', portal_username, portal_password, 'BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select mid, tid, id from upi_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='AXIS'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        upi_mc_id = result["id"].iloc[0]

        logger.debug(f"Fetching mid, tid from database for current merchant:{mid}, {tid}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(301, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Amount and order id for this txn is: {amount}, {order_id}")
            logger.debug("Generating QR using BQR QR generate API")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Resonse recived for QR genration api is : {response}")
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            api_details = DBProcessor.get_api_details('stopPayment',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "orgCode":org_code ,"txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stop payment api is : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            rrn = result['rr_number'].iloc[0]
            posting_date = result['created_time'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching auth_code, rrn, posting_date, customer name and payer name from database for "
                         f"current merchant:{auth_code}, {rrn}, {posting_date}, {customer_name}, {payer_name}")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            auth_code_refunded = result['auth_code'].values[0]
            rrn_refunded = result['rr_number'].iloc[0]
            posting_date_refunded = result['created_time'].values[0]
            logger.debug(f"Fetching auth_code, rrn, txn_id, and posting date from database for "
                 f"current merchant:{auth_code_refunded}, {rrn_refunded}, {txn_id_refunded}, {posting_date_refunded}")

            # ------------------------------------------------------------------------------------------------
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
                    "pmt_status": "STATUS:AUTHORIZED_REFUNDED",
                    "refund_pmt_status": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "refund_pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "refund_settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "refund_txn_id": txn_id_refunded,
                    "txn_amt": str(amount),
                    "refund_txn_amt": str(amount),
                    "customer_name": customer_name,
                    "refund_customer_name": customer_name,
                    "payer_name": payer_name,
                    "refund_payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "refund_pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(rrn),
                    "refund_rrn": str(rrn_refunded),
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "refund_date": refund_date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_refunded}")
                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "refund_pmt_status": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "refund_pmt_mode": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "refund_settle_status": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "refund_txn_id": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "refund_txn_amt": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "refund_customer_name": customer_name,
                    "payer_name": payer_name,
                    "refund_payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "refund_pmt_msg": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "refund_rrn": str(app_rrn_refunded),
                    "auth_code": app_auth_code_original,
                    "date": app_date_and_time,
                    "refund_date": app_date_and_time_refunded
                }

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id {testcase_id}")
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
                    "refunded_pmt_status": "REFUNDED",
                    "original_pmt_state": "REFUNDED",
                    "refunded_pmt_state": "REFUNDED",
                    "original_pmt_mode": "UPI",
                    "refunded_pmt_mode": "UPI",
                    "original_settle_status": "SETTLED",
                    "refunded_settle_status": "SETTLED",
                    "original_amt": str(amount),
                    "refunded_amt": str(amount),
                    "original_customer_name": customer_name,
                    "refunded_customer_name": customer_name,
                    "original_payer_name": payer_name,
                    "refunded_payer_name": payer_name,
                    "original_order_id": order_id,
                    "original_rrn": str(rrn),
                    "refunded_rrn": str(rrn_refunded),
                    "original_acquirer_code": "AXIS",
                    "original_issuer_code": "AXIS",
                    "original_txn_type": "CHARGE",
                    "original_mid": mid, "original_tid": tid,
                    "original_org_code": org_code,
                    "refunded_acquirer_code": "AXIS",
                    "refunded_txn_type": "REFUND",
                    "refunded_mid": mid, "refunded_tid": tid,
                    "refunded_org_code": org_code,
                    "original_auth_code": auth_code,"date": date, "refunded_date": refund_date
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                    request_body={"username": app_username, "password": app_password,
                                                                        "txnId": txn_id})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]
                state_api_original = response["states"][0]
                settlement_status_api_original = response["settlementStatus"]
                issuer_code_api_original = response["issuerCode"]
                acquirer_code_api_original = response["acquirerCode"]
                org_code_api_original = response["orgCode"]
                mid_api_original = response["mid"]
                tid_api_original = response["tid"]
                txn_type_api_original = response["txnType"]
                auth_code_api_original = response["authCode"]
                date_api_original = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username, "password": app_password,
                                                                        "txnId": txn_id_refunded})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                rrn_api_refunded = response["rrNumber"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "refunded_pmt_status": status_api_refunded,
                    "original_pmt_state": state_api_original,
                    "refunded_pmt_state": state_api_refunded,
                    "original_pmt_mode": payment_mode_api_original,
                    "refunded_pmt_mode": payment_mode_api_refunded,
                    "original_settle_status": settlement_status_api_original,
                    "refunded_settle_status": settlement_status_api_refunded,
                    "original_amt": str(amount_api_original),
                    "refunded_amt": str(amount_api_refunded),
                    "original_customer_name": customer_name,
                    "refunded_customer_name": customer_name,
                    "original_payer_name": payer_name,
                    "refunded_payer_name": payer_name,
                    "original_order_id": order_id,
                    "original_rrn": str(rrn_api_original),
                    "refunded_rrn": str(rrn_api_refunded),
                    "original_acquirer_code": acquirer_code_api_original,
                    "original_issuer_code": issuer_code_api_original,
                    "original_txn_type": txn_type_api_original,
                    "original_mid": mid_api_original, "original_tid": tid_api_original,
                    "original_org_code": org_code_api_original,
                    "refunded_acquirer_code": acquirer_code_api_refunded,
                    "refunded_txn_type": txn_type_api_refunded,
                    "refunded_mid": mid_api_refunded, "refunded_tid": tid_api_refunded,
                    "refunded_org_code": org_code_api_refunded,
                    "original_auth_code": auth_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "refunded_date": date_time_converter.from_api_to_datetime_format(date_api_refunded)
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")
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
                    "refunded_pmt_status": "REFUNDED",
                    "refunded_pmt_state": "REFUNDED",
                    "original_pmt_state": "REFUNDED",
                    "original_pmt_mode": "UPI",
                    "refunded_pmt_mode": "UPI",
                    "original_amt": amount,
                    "refunded_amt": amount,
                    "original_upi_txn_status": "AUTHORIZED_REFUNDED",
                    "refunded_upi_txn_status": "REFUNDED",
                    "original_settle_status": "SETTLED",
                    "refunded_settle_status": "SETTLED",
                    "original_acquirer_code": "AXIS",
                    "refunded_acquirer_code": "AXIS",
                    "original_bank_code": "AXIS",
                    "original_pmt_gateway": "ATOS",
                    "refunded_pmt_gateway": "ATOS",
                    "original_upi_txn_type": "PAY_BQR",
                    "refunded_upi_txn_type": "REFUND",
                    "original_upi_bank_code": "AXIS",
                    "refunded_upi_bank_code": "AXIS",
                    "original_upi_mc_id": upi_mc_id,
                    "refunded_upi_mc_id": upi_mc_id,
                    "original_mid": mid,
                    "original_tid": tid,
                    "refund_mid": mid,
                    "refund_tid": tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "refunded_pmt_status": status_db_refunded,
                    "original_pmt_state": state_db_original,
                    "refunded_pmt_state": state_db_refunded,
                    "original_pmt_mode": payment_mode_db_original,
                    "refunded_pmt_mode": payment_mode_db_refunded,
                    "original_amt": amount_db_original,
                    "refunded_amt": amount_db_refunded,
                    "original_upi_txn_status": upi_status_db_original,
                    "refunded_upi_txn_status": upi_status_db_refunded,
                    "original_settle_status": settlement_status_db_original,
                    "refunded_settle_status": settlement_status_db_refunded,
                    "original_acquirer_code": acquirer_code_db_original,
                    "refunded_acquirer_code": acquirer_code_db_refunded,
                    "original_bank_code": bank_code_db_original,
                    "original_pmt_gateway": payment_gateway_db_original,
                    "refunded_pmt_gateway": payment_gateway_db_refunded,
                    "original_upi_txn_type": upi_txn_type_db_original,
                    "refunded_upi_txn_type": upi_txn_type_db_refunded,
                    "original_upi_bank_code": upi_bank_code_db_original,
                    "refunded_upi_bank_code": upi_bank_code_db_refunded,
                    "original_upi_mc_id": upi_mc_id_db_original,
                    "refunded_upi_mc_id": upi_mc_id_db_refunded,
                    "original_mid": mid_db_original,
                    "original_tid": tid_db_original,
                    "refund_mid": mid_db_refunded,
                    "refund_tid": tid_db_refunded,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                #
                # Write the test case Portal validation code block here. Set this to pass if not required.
                #
                actual_portal_values = {}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_refunded)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_refunded),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",  'date': txn_date,'time': txn_time}
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
