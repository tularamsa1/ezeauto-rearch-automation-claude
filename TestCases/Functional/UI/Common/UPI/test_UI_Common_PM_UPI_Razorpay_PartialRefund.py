import sys
from datetime import datetime
import pytest
import random
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_288():
    """
    Sub Feature Code: UI_Common_PM_UPI_Partial_Refund_Via_API_Razorpay
    Sub Feature Description: Verification of  a pure UPI txn when Partial refund is performed via api for Razorpay
    TC naming code description: 100: Payment Method, 101: UPI, 288: TC288
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP'" \
                f" and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")

            amount = random.randint(1601, 1700)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Order id : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn_original = result['rr_number'].values[0]
            logger.debug(f"fetched rrn_original from txn table is : {rrn_original}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id_original = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id_original}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            refund_amount = amount - 100
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": refund_amount,
                                                                    "originalTransactionId": str(txn_id_original)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for refund api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and orig_txn_id = '{txn_id_original}' and external_ref='{order_id}'" \
                    f" order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            refund_rrn = result['rr_number'].iloc[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched refund_customer_name from txn table is : {refund_customer_name}")
            refund_txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id_refunded from txn table is : {refund_txn_id}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched refund_payer_name from txn table is : {refund_payer_name}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched refund_org_code_txn from txn table is : {refund_org_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")

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
                refund_date_and_time = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id_original,
                    "txn_id_2": refund_txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "txn_amt_2": "{:,.2f}".format(refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": refund_customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": refund_payer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(rrn_original),
                    "rrn_2": str(refund_rrn),
                    "date": date_and_time,
                    "date_2": refund_date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id : {testcase_id}")

                logger.info("resetting the app after sending the request for refund")
                app_driver.reset()

                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {refund_txn_id}, {app_rrn_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")

                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.debug(
                    f"Fetching order id from app transaction history: order Id = {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {txn_id_original}, {app_date_and_time}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")

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
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(
                    f"Fetching order id from app transaction history: order Id = {app_order_id}")

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
                    "order_id": app_order_id,
                    "order_id_2": app_order_id_refunded,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "rrn_2": str(app_rrn_refunded),
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_refunded
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
                date = date_time_converter.db_datetime(created_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": refund_customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": refund_payer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "rrn": str(rrn_original),
                    "rrn_2": str(refund_rrn),
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": refund_txn_type,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "date": date,
                    "date_2": refund_date,
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_original][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
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
                date_api_original = response["createdTime"]
                order_id_api_original = response["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
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
                order_id_api_refunded = response["orderNumber"]

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt": str(amount_api_original),
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original, "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded, "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": refund_amount,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "acquirer_code_2": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_type": "PAY_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]
                order_id_db_original = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]
                order_id_db_refunded = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
                    "order_id": order_id_db_original,
                    "order_id_2": order_id_db_refunded,
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
                    "upi_mc_id": upi_mc_id_db_original,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid": mid_db_original,
                    "tid": tid_db_original,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

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
                refund_date_and_time_portal = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id_original,
                    "rrn": rrn_original,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(refund_amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "rrn_2": refund_rrn
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
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
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": str(total_amount_2[1]),
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(refund_created_time)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(refund_rrn),
                    'BASE AMOUNT:': "Rs.{:,.2f}".format(refund_amount),
                    'date': txn_date,
                    'time': txn_time,
                }
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn_original),
                    'BASE AMOUNT:': "Rs.{:,.2f}".format(amount),
                    'date': txn_date_2,
                    'time': txn_time_2,
                }

                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(
                    txn_id_original, {"username": app_username, "password": app_password}, expected_charge_slip_values_2)
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(
                    refund_txn_id, {"username": app_username, "password": app_password}, expected_charge_slip_values_1)

                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_289():
    """
    Sub Feature Code: UI_Common_PM_UPI_Two_Times_Partial_Refund_Via_API_Amount_Greater_Than_Original_Amount_Razorpay
    Sub Feature Description: VVerification of a UPI partial refund via api when partial refund amount is greater than original amount for Razorpay
    TC naming code description:
    100: Payment Method
    101: UPI
    289: TC289
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP'" \
                f" and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")

            amount = 3100
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Order id : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status_refunded = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status_refunded}")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            org_code_txn = result['org_code'].values[0]
            rrn = result['rr_number'].iloc[0]
            txn_type = result['txn_type'].values[0]
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")

            refunded_amount = 1700
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": refunded_amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")
            greater_refund_amount = 1401
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": greater_refund_amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(
                f"Response received from refund api when refund amount is greater than original amount : {response}")
            api_error_message = response["errorMessage"]

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id ='{str(txn_id)}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            refund_txn_id = result["id"].iloc[0]
            refund_auth_code = result['auth_code'].values[0]
            refund_txn_type = result['txn_type'].values[0]
            refund_rrn = result['rr_number'].iloc[0]
            refund_created_date_time = result['created_time'].values[0]
            logger.debug(
                f"Fetching Transaction id, rrn from db query, txn_id : {refund_txn_id}, rrn : {refund_rrn} ")

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
                date_and_time = date_time_converter.to_app_format(created_date_time)
                refund_date_and_time = date_time_converter.to_app_format(refund_created_date_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": refund_txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "txn_amt_2": "{:,.2f}".format(refunded_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(rrn),
                    "refund_rrn": str(refund_rrn),
                    "date": date_and_time,
                    "date_2": refund_date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver.reset()
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {refund_txn_id}, {app_rrn_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")
                app_refund_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {refund_txn_id}, {app_refund_date_and_time}")
                app_refund_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {refund_txn_id}, {app_refund_order_id}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_original}")

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
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

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
                    "order_id": app_order_id,
                    "order_id_2": app_refund_order_id,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "refund_rrn": str(app_rrn_refunded),
                    "date": app_date_and_time,
                    "date_2": app_refund_date_and_time
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
                date_and_time = date_time_converter.db_datetime(created_date_time)
                refund_date_and_time = date_time_converter.db_datetime(refund_created_date_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(refunded_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "rrn": str(rrn),
                    "refunded_rrn": str(refund_rrn),
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": refund_txn_type,
                    "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "date": date_and_time,
                    "date_2": refund_date_and_time,
                    "err_msg": "Transaction declined. Amount entered is more than maximum allowed for the transaction. Maximum Allowed: 1400.00"
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api_original = elements["status"]
                        amount_api_original = int(elements["amount"])
                        payment_mode_api_original = elements["paymentMode"]
                        rrn_api_original = elements["rrNumber"]
                        state_api_original = elements["states"][0]
                        settlement_status_api_original = elements["settlementStatus"]
                        issuer_code_api_original = elements["issuerCode"]
                        acquirer_code_api_original = elements["acquirerCode"]
                        org_code_api_original = elements["orgCode"]
                        mid_api_original = elements["mid"]
                        tid_api_original = elements["tid"]
                        txn_type_api_original = elements["txnType"]
                        date_api_original = elements["createdTime"]
                        order_id_api_original = elements["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for new_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == refund_txn_id:
                        status_api_refunded = elements["status"]
                        amount_api_refunded = int(elements["amount"])
                        payment_mode_api_refunded = elements["paymentMode"]
                        rrn_api_refunded = elements["rrNumber"]
                        state_api_refunded = elements["states"][0]
                        settlement_status_api_refunded = elements["settlementStatus"]
                        acquirer_code_api_refunded = elements["acquirerCode"]
                        org_code_api_refunded = elements["orgCode"]
                        mid_api_refunded = elements["mid"]
                        tid_api_refunded = elements["tid"]
                        txn_type_api_refunded = elements["txnType"]
                        date_api_refunded = elements["createdTime"]
                        order_id_api_refunded = elements["orderNumber"]

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt": str(amount_api_original),
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn": str(rrn_api_original),
                    "refunded_rrn": str(rrn_api_refunded),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded, "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "err_msg": api_error_message
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": refunded_amount,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "acquirer_code_2": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "bank_code_2": "RAZORPAY_PSP",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_type": "PAY_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "order_id": order_id,
                    "order_id_2": order_id,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = f"select * from txn where id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                order_id_db_refunded = result['external_ref'].values[0]

                query = f"select * from upi_txn where txn_id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                bank_code_db_refunded = result["bank_code"].iloc[0]

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                order_id_db_original = result['external_ref'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

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
                    "bank_code_2": bank_code_db_refunded,
                    "pmt_gateway": payment_gateway_db_original,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id": upi_mc_id_db_original,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "order_id": order_id_db_original,
                    "order_id_2": order_id_db_refunded,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_date_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "rrn": str(rrn),
                    "txn_id": txn_id,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(refunded_amount),
                    "username_2": app_username,
                    "rrn_2": str(refund_rrn),
                    "txn_id_2": refund_txn_id,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                refunded_date_time = transaction_details[0]['Date & Time']
                refunded_transaction_id = transaction_details[0]['Transaction ID']
                refunded_total_amount = transaction_details[0]['Total Amount'].split()
                refunded_transaction_type = transaction_details[0]['Type']
                refunded_status = transaction_details[0]['Status']
                refunded_username = transaction_details[0]['Username']
                refunded_rrn = transaction_details[0]['RR Number']
                refunded_auth_code = transaction_details[0] ['Auth Code']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                rrn = transaction_details[1]['RR Number']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "rrn": rrn,
                    "txn_id": transaction_id,
                    "date_time_2": refunded_date_time,
                    "pmt_state_2": str(refunded_status),
                    "pmt_type_2": refunded_transaction_type,
                    "txn_amt_2": refunded_total_amount[1],
                    "username_2": str(refunded_username),
                    "rrn_2": refunded_rrn,
                    "txn_id_2": refunded_transaction_id,
                    "auth_code_2": refunded_auth_code
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                original_txn_date, original_txn_time = date_time_converter.to_chargeslip_format(created_date_time)
                refund_txn_date, refund_txn_time = date_time_converter.to_chargeslip_format(refund_created_date_time)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'date': refund_txn_date, 'time': refund_txn_time,
                    'BASE AMOUNT:': "Rs.{:,.2f}".format(refunded_amount),
                    'RRN': str(refund_rrn),
                }
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'date': original_txn_date,
                    'time': original_txn_time,
                    'BASE AMOUNT:': "Rs.{:,.2f}".format(amount),
                }
                charge_slip_val_result_1 = receipt_validator.perform_charge_slip_validations(
                    refund_txn_id, {"username": app_username, "password": app_password}, expected_charge_slip_values_1)
                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password}, expected_charge_slip_values_2)

                if charge_slip_val_result_1 and charge_slip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_290():
    """
    Sub Feature Code: UI_Common_PM_UPI_Two_Times_Successful_Partial_Refund_Via_API_Razorpay
    Sub Feature Description:  Verification of two times partial refund for upi txn via api for Razorpay
    TC naming code description: 100: Payment Method, 101: UPI, 290: TC290
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP'" \
                f" and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = 3500
            partial_refunded_amount = 1600
            full_refund_amount = 1900
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Order id : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status_refunded = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status_refunded}")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching original_customer_name from txn table : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching original_payer_name from txn table : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching original_auth_code from txn table : {auth_code} ")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching original_org_code_txn from txn table : {org_code_txn} ")
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching original_rrn from txn table : {rrn} ")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching original_txn_type from txn table : {txn_type} ")
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_date_time from txn table : {created_date_time} ")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": partial_refunded_amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")
            partial_refund_txn_id_1 = response["txnId"]
            logger.debug(
                f"Fetching txn_id from the response of paymentRefund api, partial_refund_txn_id_1 : {partial_refund_txn_id_1}")
            query = f"select * from txn where id = '{str(partial_refund_txn_id_1)}';"
            logger.debug(f"Query to fetch txn data of first partial refund from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            partial_refund_auth_code_1 = result['auth_code'].values[0]
            logger.debug(f"Fetching partial_refund_auth_code_1 from txn table : {partial_refund_auth_code_1} ")
            partial_refund_txn_type_1 = result['txn_type'].values[0]
            logger.debug(f"Fetching partial_refund_txn_type_1 from txn table : {partial_refund_txn_type_1} ")
            partial_refund_rrn_1 = result['rr_number'].iloc[0]
            logger.debug(f"Fetching partial_refund_rrn_1 from txn table : {partial_refund_rrn_1} ")
            partial_refund_created_date_time_1 = result['created_time'].values[0]
            logger.debug(
                f"Fetching partial_refund_created_date_time_1 from txn table : {partial_refund_created_date_time_1} ")
            partial_refund_customer_name_1 = result['customer_name'].values[0]
            logger.debug(f"Fetching partial_refund_customer_name_1 from txn table : {partial_refund_customer_name_1} ")
            partial_refund_payer_name_1 = result['payer_name'].values[0]
            logger.debug(f"Fetching partial_refund_payer_name_1 from txn table : {partial_refund_payer_name_1} ")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": full_refund_amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")
            partial_refund_txn_id_2 = response["txnId"]
            logger.debug(
                f"Fetching txn_id from the response of paymentRefund api, partial_refund_txn_id_2 : {partial_refund_txn_id_2}")

            query = f"select * from txn where id = '{str(partial_refund_txn_id_2)}';"
            logger.debug(f"Query to fetch txn data of first partial refund from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            partial_refund_auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching partial_refund_auth_code_2 from txn table : {partial_refund_auth_code_2} ")
            partial_refund_txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching partial_refund_txn_type_2 from txn table : {partial_refund_txn_type_2} ")
            partial_refund_rrn_2 = result['rr_number'].iloc[0]
            logger.debug(f"Fetching partial_refund_rrn_2 from txn table : {partial_refund_rrn_2} ")
            partial_refund_created_date_time_2 = result['created_time'].values[0]
            logger.debug(
                f"Fetching partial_refund_created_date_time_2 from txn table : {partial_refund_created_date_time_2} ")
            partial_refund_customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching partial_refund_customer_name_2 from txn table : {partial_refund_customer_name_2} ")
            partial_refund_payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching partial_refund_payer_name_2 from txn table : {partial_refund_payer_name_2} ")

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
                date_and_time = date_time_converter.to_app_format(created_date_time)
                partial_refund_date_and_time_1 = date_time_converter.to_app_format(partial_refund_created_date_time_1)
                partial_refund_date_and_time_2 = date_time_converter.to_app_format(partial_refund_created_date_time_2)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED_REFUNDED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_status_3": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "pmt_mode_3": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "settle_status_3": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": partial_refund_txn_id_1,
                    "txn_id_3": partial_refund_txn_id_2,
                    "txn_amt": "{:,.2f}".format(amount),
                    "txn_amt_2": "{:,.2f}".format(partial_refunded_amount),
                    "txn_amt_3": "{:,.2f}".format(full_refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": partial_refund_customer_name_1,
                    "customer_name_3": partial_refund_customer_name_2,
                    "payer_name": payer_name,
                    "payer_name_2": partial_refund_payer_name_1,
                    "payer_name_3": partial_refund_payer_name_2,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "order_id_3": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "pmt_msg_3": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(rrn),
                    "partial_refund_rrn_1": str(partial_refund_rrn_1),
                    "partial_refund_rrn_2": str(partial_refund_rrn_2),
                    "date": date_and_time,
                    "date_2": partial_refund_date_and_time_1,
                    "date_3": partial_refund_date_and_time_2,
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver.reset()
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(partial_refund_txn_id_1)
                app_payment_status_partial_refund_1 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_payment_status_partial_refund_1}")
                app_date_and_time_partial_refund_1 = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_date_and_time_partial_refund_1}")

                app_payment_mode_partial_refund_1 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_payment_mode_partial_refund_1}")
                app_txn_id_partial_refund_1 = txn_history_page.fetch_txn_id_text()
                logger.info(
                    f"Fetching txn_id from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_txn_id_partial_refund_1}")
                app_amount_partial_refund_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(
                    f"Fetching txn amount from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_amount_partial_refund_1}")
                app_customer_name_partial_refund_1 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_customer_name_partial_refund_1}")
                app_settlement_status_partial_refund_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_settlement_status_partial_refund_1}")
                app_payer_name_partial_refund_1 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_payer_name_partial_refund_1}")
                app_payment_msg_partial_refund_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_payment_msg_partial_refund_1}")
                app_order_id_partial_refund_1 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_order_id_partial_refund_1}")
                app_rrn_partial_refund_1 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_rrn_partial_refund_1}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(partial_refund_txn_id_2)
                app_payment_status_partial_refund_2 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_payment_status_partial_refund_2}")
                app_date_and_time_partial_refund_2 = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_date_and_time_partial_refund_2}")

                app_payment_mode_partial_refund_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_payment_mode_partial_refund_2}")
                app_txn_id_partial_refund_2 = txn_history_page.fetch_txn_id_text()
                logger.info(
                    f"Fetching txn_id from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_txn_id_partial_refund_2}")
                app_amount_partial_refund_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(
                    f"Fetching txn amount from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_amount_partial_refund_2}")
                app_customer_name_partial_refund_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_customer_name_partial_refund_2}")
                app_settlement_status_partial_refund_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_settlement_status_partial_refund_2}")
                app_payer_name_partial_refund_2 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_payer_name_partial_refund_2}")
                app_payment_msg_partial_refund_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_payment_msg_partial_refund_2}")
                app_order_id_partial_refund_2 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_order_id_partial_refund_2}")
                app_rrn_partial_refund_2 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_rrn_partial_refund_2}")

                actual_app_values = {
                    "pmt_status": app_payment_status,
                    "pmt_status_2": app_payment_status_partial_refund_1,
                    "pmt_status_3": app_payment_status_partial_refund_2,
                    "pmt_mode": app_payment_mode,
                    "pmt_mode_2": app_payment_mode_partial_refund_1,
                    "pmt_mode_3": app_payment_mode_partial_refund_2,
                    "settle_status": app_settlement_status,
                    "settle_status_2": app_settlement_status_partial_refund_1,
                    "settle_status_3": app_settlement_status_partial_refund_2,
                    "txn_id": app_txn_id,
                    "txn_id_2": app_txn_id_partial_refund_1,
                    "txn_id_3": app_txn_id_partial_refund_2,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "txn_amt_2": str(app_amount_partial_refund_1).split(' ')[1],
                    "txn_amt_3": str(app_amount_partial_refund_2).split(' ')[1],
                    "customer_name": app_customer_name,
                    "customer_name_2": app_customer_name_partial_refund_1,
                    "customer_name_3": app_customer_name_partial_refund_2,
                    "payer_name": app_payer_name,
                    "payer_name_2": app_payer_name_partial_refund_1,
                    "payer_name_3": app_payer_name_partial_refund_2,
                    "order_id": app_order_id,
                    "order_id_2": app_order_id_partial_refund_1,
                    "order_id_3": app_order_id_partial_refund_2,
                    "pmt_msg": app_payment_msg,
                    "pmt_msg_2": app_payment_msg_partial_refund_1,
                    "pmt_msg_3": app_payment_msg_partial_refund_2,
                    "rrn": str(app_rrn),
                    "partial_refund_rrn_1": str(app_rrn_partial_refund_1),
                    "partial_refund_rrn_2": str(app_rrn_partial_refund_2),
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_partial_refund_1,
                    "date_3": app_date_and_time_partial_refund_2,
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
                date_and_time = date_time_converter.db_datetime(created_date_time)
                partial_refund_date_and_time_1 = date_time_converter.db_datetime(partial_refund_created_date_time_1)
                partial_refund_date_and_time_2 = date_time_converter.db_datetime(partial_refund_created_date_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_status_3": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "pmt_mode_3": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "settle_status_3": "SETTLED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state_3": "REFUNDED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(partial_refunded_amount),
                    "txn_amt_3": str(full_refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": partial_refund_customer_name_1,
                    "customer_name_3": partial_refund_customer_name_2,
                    "payer_name": payer_name,
                    "payer_name_2": partial_refund_payer_name_1,
                    "payer_name_3": partial_refund_payer_name_2,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "order_id_3": order_id,
                    "rrn": str(rrn),
                    "partial_refund_rrn_1": str(partial_refund_rrn_1),
                    "partial_refund_rrn_2": str(partial_refund_rrn_2),
                    "date": date_and_time,
                    "date_2": partial_refund_date_and_time_1,
                    "date_3": partial_refund_date_and_time_2,
                    "acquirer_code": "RAZORPAY",
                    "acquirer_code_2": "RAZORPAY",
                    "acquirer_code_3": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "txn_type_2": partial_refund_txn_type_1,
                    "txn_type_3": partial_refund_txn_type_2,
                    "mid": mid, "tid": tid,
                    "mid_2": mid, "tid_2": tid,
                    "mid_3": mid, "tid_3": tid,
                    "org_code": org_code_txn,
                    "org_code_2": org_code_txn,
                    "org_code_3": org_code_txn,
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api_original = elements["status"]
                        amount_api_original = int(elements["amount"])
                        payment_mode_api_original = elements["paymentMode"]
                        rrn_api_original = elements["rrNumber"]
                        state_api_original = elements["states"][0]
                        settlement_status_api_original = elements["settlementStatus"]
                        issuer_code_api_original = elements["issuerCode"]
                        acquirer_code_api_original = elements["acquirerCode"]
                        org_code_api_original = elements["orgCode"]
                        mid_api_original = elements["mid"]
                        tid_api_original = elements["tid"]
                        txn_type_api_original = elements["txnType"]
                        date_api_original = elements["createdTime"]
                        order_id_api_original = elements["orderNumber"]
                        customer_name_api_original = elements["customerName"]
                        payer_name_api_original = elements["payerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for new_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == partial_refund_txn_id_1:
                        partial_refund_status_api_1 = elements["status"]
                        partial_refund_amount_api_1 = int(elements["amount"])
                        partial_refund_payment_mode_api_1 = elements["paymentMode"]
                        partial_refund_rrn_api_1 = elements["rrNumber"]
                        partial_refund_state_api_1 = elements["states"][0]
                        partial_refund_settle_status_api_1 = elements["settlementStatus"]
                        partial_refund_acquirer_code_api_1 = elements["acquirerCode"]
                        partial_refund_org_code_api_1 = elements["orgCode"]
                        partial_refund_mid_api_1 = elements["mid"]
                        partial_refund_tid_api_1 = elements["tid"]
                        partial_refund_txn_type_api_1 = elements["txnType"]
                        partial_refund_date_api_1 = elements["createdTime"]
                        partial_refund_order_id_api_1 = elements["orderNumber"]
                        partial_refund_customer_name_api_1 = elements["customerName"]
                        partial_refund_payer_name_api_1 = elements["payerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for new_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == partial_refund_txn_id_2:
                        partial_refund_status_api_2 = elements["status"]
                        partial_refund_amount_api_2 = int(elements["amount"])
                        partial_refund_payment_mode_api_2 = elements["paymentMode"]
                        partial_refund_rrn_api_2 = elements["rrNumber"]
                        partial_refund_state_api_2 = elements["states"][0]
                        partial_refund_settle_status_api_2 = elements["settlementStatus"]
                        partial_refund_acquirer_code_api_2 = elements["acquirerCode"]
                        partial_refund_org_code_api_2 = elements["orgCode"]
                        partial_refund_mid_api_2 = elements["mid"]
                        partial_refund_tid_api_2 = elements["tid"]
                        partial_refund_txn_type_api_2 = elements["txnType"]
                        partial_refund_date_api_2 = elements["createdTime"]
                        partial_refund_order_id_api_2 = elements["orderNumber"]
                        partial_refund_customer_name_api_2 = elements["customerName"]
                        partial_refund_payer_name_api_2 = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": partial_refund_status_api_1,
                    "pmt_status_3": partial_refund_status_api_2,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": partial_refund_payment_mode_api_1,
                    "pmt_mode_3": partial_refund_payment_mode_api_2,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": partial_refund_settle_status_api_1,
                    "settle_status_3": partial_refund_settle_status_api_2,
                    "pmt_state": state_api_original,
                    "pmt_state_2": partial_refund_state_api_1,
                    "pmt_state_3": partial_refund_state_api_2,
                    "txn_amt": str(amount_api_original),
                    "txn_amt_2": str(partial_refund_amount_api_1),
                    "txn_amt_3": str(partial_refund_amount_api_2),
                    "customer_name": customer_name_api_original,
                    "customer_name_2": partial_refund_customer_name_api_1,
                    "customer_name_3": partial_refund_customer_name_api_2,
                    "payer_name": payer_name_api_original,
                    "payer_name_2": partial_refund_payer_name_api_1,
                    "payer_name_3": partial_refund_payer_name_api_2,
                    "order_id": order_id_api_original,
                    "order_id_2": partial_refund_order_id_api_1,
                    "order_id_3": partial_refund_order_id_api_2,
                    "rrn": str(rrn_api_original),
                    "partial_refund_rrn_1": str(partial_refund_rrn_api_1),
                    "partial_refund_rrn_2": str(partial_refund_rrn_api_2),
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(partial_refund_date_api_1),
                    "date_3": date_time_converter.from_api_to_datetime_format(partial_refund_date_api_2),
                    "acquirer_code": acquirer_code_api_original,
                    "acquirer_code_2": partial_refund_acquirer_code_api_1,
                    "acquirer_code_3": partial_refund_acquirer_code_api_2,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "txn_type_2": partial_refund_txn_type_api_1,
                    "txn_type_3": partial_refund_txn_type_api_2,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "mid_2": partial_refund_mid_api_1,
                    "tid_2": partial_refund_tid_api_1,
                    "mid_3": partial_refund_mid_api_2,
                    "tid_3": partial_refund_tid_api_2,
                    "org_code": org_code_api_original,
                    "org_code_2": partial_refund_org_code_api_1,
                    "org_code_3": partial_refund_org_code_api_2,
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_status_3": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "pmt_mode_3": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "settle_status_3": "SETTLED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state_3": "REFUNDED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(partial_refunded_amount),
                    "txn_amt_3": str(full_refund_amount),
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_status_3": "REFUNDED",
                    "acquirer_code": "RAZORPAY",
                    "acquirer_code_2": "RAZORPAY",
                    "acquirer_code_3": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "pmt_gateway_3": "RAZORPAY",
                    "upi_txn_type": "PAY_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_txn_type_3": "REFUND",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_bank_code_3": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "upi_mc_id_3": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "mid_3": mid,
                    "tid_3": tid,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "order_id_3": order_id,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                order_id_db = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + partial_refund_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_status_db_1 = result["status"].iloc[0]
                partial_refund_payment_mode_db_1 = result["payment_mode"].iloc[0]
                partial_refund_amount_db_1 = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                partial_refund_state_db_1 = result["state"].iloc[0]
                partial_refund_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                partial_refund_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                partial_refund_settlement_status_db_1 = result["settlement_status"].iloc[0]
                partial_refund_tid_db_1 = result['tid'].values[0]
                partial_refund_mid_db_1 = result['mid'].values[0]
                partial_refund_order_id_db_1 = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + partial_refund_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_upi_status_db_1 = result["status"].iloc[0]
                partial_refund_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                partial_refund_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                partial_refund_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + partial_refund_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_status_db_2 = result["status"].iloc[0]
                partial_refund_payment_mode_db_2 = result["payment_mode"].iloc[0]
                partial_refund_amount_db_2 = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                partial_refund_state_db_2 = result["state"].iloc[0]
                partial_refund_payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                partial_refund_acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                partial_refund_settlement_status_db_2 = result["settlement_status"].iloc[0]
                partial_refund_tid_db_2 = result['tid'].values[0]
                partial_refund_mid_db_2 = result['mid'].values[0]
                partial_refund_order_id_db_2 = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + partial_refund_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_upi_status_db_2 = result["status"].iloc[0]
                partial_refund_upi_txn_type_db_2 = result["txn_type"].iloc[0]
                partial_refund_upi_bank_code_db_2 = result["bank_code"].iloc[0]
                partial_refund_upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_status_2": partial_refund_status_db_1,
                    "pmt_status_3": partial_refund_status_db_2,
                    "pmt_mode": payment_mode_db,
                    "pmt_mode_2": partial_refund_payment_mode_db_1,
                    "pmt_mode_3": partial_refund_payment_mode_db_2,
                    "settle_status": settlement_status_db,
                    "settle_status_2": partial_refund_settlement_status_db_1,
                    "settle_status_3": partial_refund_settlement_status_db_2,
                    "pmt_state": state_db,
                    "pmt_state_2": partial_refund_state_db_1,
                    "pmt_state_3": partial_refund_state_db_2,
                    "txn_amt": str(amount_db),
                    "txn_amt_2": str(partial_refund_amount_db_1),
                    "txn_amt_3": str(partial_refund_amount_db_2),
                    "upi_txn_status": upi_status_db,
                    "upi_txn_status_2": partial_refund_upi_status_db_1,
                    "upi_txn_status_3": partial_refund_upi_status_db_2,
                    "acquirer_code": acquirer_code_db,
                    "acquirer_code_2": partial_refund_acquirer_code_db_1,
                    "acquirer_code_3": partial_refund_acquirer_code_db_2,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "pmt_gateway_2": partial_refund_payment_gateway_db_1,
                    "pmt_gateway_3": partial_refund_payment_gateway_db_2,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_txn_type_2": partial_refund_upi_txn_type_db_1,
                    "upi_txn_type_3": partial_refund_upi_txn_type_db_2,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_bank_code_2": partial_refund_upi_bank_code_db_1,
                    "upi_bank_code_3": partial_refund_upi_bank_code_db_2,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_mc_id_2": partial_refund_upi_mc_id_db_1,
                    "upi_mc_id_3": partial_refund_upi_mc_id_db_2,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": partial_refund_mid_db_1,
                    "tid_2": partial_refund_tid_db_1,
                    "mid_3": partial_refund_mid_db_2,
                    "tid_3": partial_refund_tid_db_2,
                    "order_id": order_id_db,
                    "order_id_2": partial_refund_order_id_db_1,
                    "order_id_3": partial_refund_order_id_db_2,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(partial_refund_created_date_time_1)
                date_and_time_portal_3 = date_time_converter.to_portal_format(partial_refund_created_date_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(partial_refunded_amount),
                    "username_2": app_username,
                    "rrn_2": str(partial_refund_rrn_1),
                    "txn_id_2": partial_refund_txn_id_1,
                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "REFUNDED",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": "{:,.2f}".format(full_refund_amount),
                    "username_3": app_username,
                    "rrn_3": str(partial_refund_rrn_2),
                    "txn_id_3": partial_refund_txn_id_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                refunded_date_time = transaction_details[0]['Date & Time']
                refunded_transaction_id = transaction_details[0]['Transaction ID']
                refunded_total_amount = transaction_details[0]['Total Amount'].split()
                refunded_transaction_type = transaction_details[0]['Type']
                refunded_status = transaction_details[0]['Status']
                refunded_username = transaction_details[0]['Username']
                refunded_rrn = transaction_details[0]['RR Number']

                date_time_1 = transaction_details[1]['Date & Time']
                transaction_id_1 = transaction_details[1]['Transaction ID']
                total_amount_1 = transaction_details[1]['Total Amount'].split()
                transaction_type_1 = transaction_details[1]['Type']
                status_1 = transaction_details[1]['Status']
                username_1 = transaction_details[1]['Username']
                rrn_1 = transaction_details[1]['RR Number']

                date_time = transaction_details[2]['Date & Time']
                transaction_id = transaction_details[2]['Transaction ID']
                total_amount = transaction_details[2]['Total Amount'].split()
                transaction_type = transaction_details[2]['Type']
                status = transaction_details[2]['Status']
                username = transaction_details[2]['Username']
                rrn = transaction_details[2]['RR Number']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rrn,

                    "date_time_2": date_time_1,
                    "pmt_state_2": str(status_1),
                    "pmt_type_2": transaction_type_1,
                    "txn_amt_2": total_amount_1[1],
                    "username_2": username_1,
                    "rrn_2": rrn_1,
                    "txn_id_2": transaction_id_1,

                    "date_time_3": refunded_date_time,
                    "pmt_state_3": str(refunded_status),
                    "pmt_type_3": refunded_transaction_type,
                    "txn_amt_3": refunded_total_amount[1],
                    "username_3": str(refunded_username),
                    "rrn_3": refunded_rrn,
                    "txn_id_3": refunded_transaction_id
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                partial_refund_txn_date_1, partial_refund_txn_time_1 = date_time_converter.to_chargeslip_format(
                    partial_refund_created_date_time_1)
                partial_refund_txn_date_2, partial_refund_txn_time_2 = date_time_converter.to_chargeslip_format(
                    partial_refund_created_date_time_2)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'date': partial_refund_txn_date_1,
                    'time': partial_refund_txn_time_1,
                    'BASE AMOUNT:': "Rs.{:,.2f}".format(partial_refunded_amount),
                    'RRN': str(partial_refund_rrn_1),
                }
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'date': partial_refund_txn_date_2,
                    'time': partial_refund_txn_time_2,
                    'RRN': str(partial_refund_rrn_2),
                }
                charge_slip_val_result_1 = receipt_validator.perform_charge_slip_validations(
                    partial_refund_txn_id_1, {"username": app_username, "password": app_password},
                    expected_charge_slip_values_1)
                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(
                    partial_refund_txn_id_2, {"username": app_username, "password": app_password},
                    expected_charge_slip_values_2)

                if charge_slip_val_result_1 and charge_slip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_291():
    """
    Sub Feature Code: UI_Common_PM_UPI_Partial_Refund_In_Decimal_Via_API_Razorpay
    Sub Feature Description:   Verification of  a pure UPI txn when Partial refund is performed via api for Razorpay
    and the refunded amount will be in decimal place
    TC naming code description: 100: Payment Method, 101: UPI, 291: TC291
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP'" \
                f" and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(3100, 3500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Order id : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status_refunded = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status_refunded}")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching original_customer_name from txn table : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching original_payer_name from txn table : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching original_auth_code from txn table : {auth_code} ")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching original_org_code_txn from txn table : {org_code_txn} ")
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching original_rrn from txn table : {rrn} ")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching original_txn_type from txn table : {txn_type} ")
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_date_time from txn table : {created_date_time} ")

            refund_amount = amount - 1500.55
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": refund_amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")

            refund_txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the refund api response : {refund_txn_id}")
            refund_txn_type = response['txnType']
            logger.debug(f"Fetching txn_type from the refund api response : {refund_txn_type}")
            refund_rrn = response['rrNumber']
            logger.debug(f"Fetching rrn from the refund api response : {refund_rrn}")
            customer_name_refund = response['customerName']
            logger.debug(f"Fetching customer_name from the refund api response : {customer_name_refund}")
            payer_name_refund = response['payerName']
            logger.debug(f"Fetching payer_name from the refund api response : {payer_name_refund}")
            query = f"select * from txn where id = '{refund_txn_id}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching posting_date from the refund api response : {refund_created_time}")

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
                date_and_time = date_time_converter.to_app_format(created_date_time)
                refund_date_and_time = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": refund_txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "txn_amt_2": "{:,.2f}".format(refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name_refund,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name_refund,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(rrn),
                    "refund_rrn": str(refund_rrn),
                    # "auth_code": auth_code,
                    # "refund_auth_code": refund_auth_code,
                    "date": date_and_time,
                    "date_2": refund_date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver.reset()
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {refund_txn_id}, {app_rrn_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.debug(
                    f"Fetching order id from app transaction history: order Id = {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_original}")
                # app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                # logger.info(
                #     f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code_original}")
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
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(
                    f"Fetching order id from app transaction history: order Id = {app_order_id}")

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
                    "order_id": app_order_id,
                    "order_id_2": app_order_id_refunded,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "refund_rrn": str(app_rrn_refunded),
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_refunded
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
                date = date_time_converter.db_datetime(created_date_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "rrn": str(rrn),
                    "refunded_rrn": str(refund_rrn),
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": refund_txn_type,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "date": date,
                    "date_2": refund_date,
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
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
                # auth_code_api_original = response["authCode"]
                date_api_original = response["createdTime"]
                order_id_api_original = response["orderNumber"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": refund_txn_id})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = (response["amount"])
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
                order_id_api_refunded = response["orderNumber"]

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt": float(amount_api_original),
                    "txn_amt_2": float(amount_api_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn": str(rrn_api_original),
                    "refunded_rrn": str(rrn_api_refunded),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original, "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded, "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": float(refund_amount),
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "acquirer_code_2": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_type": "PAY_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = (
                result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]
                order_id_db_original = result['external_ref'].values[0]

                query = f"select * from upi_txn where txn_id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]
                order_id_db_refunded = result['external_ref'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
                    "order_id": order_id_db_original,
                    "order_id_2": order_id_db_refunded,
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "rrn": str(rrn),
                    "txn_id": txn_id,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(refund_amount),
                    "username_2": app_username,
                    "rrn_2": str(refund_rrn),
                    "txn_id_2": refund_txn_id
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                refunded_date_time = transaction_details[0]['Date & Time']
                refunded_transaction_id = transaction_details[0]['Transaction ID']
                refunded_total_amount = transaction_details[0]['Total Amount'].split()
                refunded_transaction_type = transaction_details[0]['Type']
                refunded_status = transaction_details[0]['Status']
                refunded_username = transaction_details[0]['Username']
                refunded_rrn = transaction_details[0]['RR Number']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                rrn = transaction_details[1]['RR Number']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "rrn": rrn,
                    "txn_id": transaction_id,
                    "date_time_2": refunded_date_time,
                    "pmt_state_2": str(refunded_status),
                    "pmt_type_2": refunded_transaction_type,
                    "txn_amt_2": refunded_total_amount[1],
                    "username_2": str(refunded_username),
                    "rrn_2": refunded_rrn,
                    "txn_id_2": refunded_transaction_id
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

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
                date = datetime.today().strftime('%Y-%m-%d')
                expected_chargeslip_values_original = {'PAID BY:': 'UPI',
                                                       'merchant_ref_no': 'Ref # ' + str(order_id),
                                                       'RRN': str(rrn),
                                                       'BASE AMOUNT:': "Rs.{:,.2f}".format(amount),
                                                       'date': date}
                expected_chargeslip_values_refunded = {'PAID BY:': 'UPI',
                                                       'merchant_ref_no': 'Ref # ' + str(order_id),
                                                       'RRN': str(refund_rrn),
                                                       'BASE AMOUNT:': "Rs.{:,.2f}".format(refund_amount),
                                                       'date': date}
                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password},
                    expected_chargeslip_values_original)
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(
                    refund_txn_id, {"username": app_username, "password": app_password},
                    expected_chargeslip_values_refunded)

                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'
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




