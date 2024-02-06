import random
import shutil
import sys
import time
import pytest
from datetime import datetime
from termcolor import colored
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_185():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_Partial_Refund_Razorpay
    Sub Feature Description: Verification of credit card txn partial refund using refund via api
    TC naming code description: 100: Payment Method, 103: CNP, 185: TC_185
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
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

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(200, 800)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={"amount": amount,
                                                                                          "externalRefNumber": order_id,
                                                                                          "username": app_username,
                                                                                          "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from api is: {response}")
            if not response['success']:
                raise Exception("Api could not initate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                logger.info("Enter Debit card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("4111 1111 1111 1111")
                remote_pay_txn.enterCreditCardExpiryMonth("12")
                remote_pay_txn.enterCreditCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.enter_otp("1111")
                remote_pay_txn.submit_otp()

                remote_pay_txn.wait_for_success_message()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected_message is:  {expected_message}")
            if success_message == expected_message:
                pass
            else:
                raise Exception("Success Message is not matching.")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"txn id from txn table : {original_txn_id}")
            original_amount_db = result['amount'].values[0]
            logger.debug(f"original amount from db : {original_amount_db}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            original_txn_type = result['txn_type'].values[0]

            query = f"select * from cnpware_txn where txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            original_acquirer_code_cnpware = result['acquirer_code'].values[0]
            logger.debug(f"original_acquirer_code_cnpware from cnpware_txn table : {original_acquirer_code_cnpware}")
            original_payment_flow_cnpware = result['payment_flow'].values[0]
            logger.debug(f"original_payment_flow from cnpware_txn table : {original_payment_flow_cnpware}")

            query = f"select * from cnp_txn where txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            state_cnp_txn_original = result['state'].values[0]
            logger.debug(f"Query result, state_cnp_txn_original : {state_cnp_txn_original}")

            amount_refund = 100
            api_details = DBProcessor.get_api_details('RemotePayRefund', request_body={"username": app_username,
                                                                                       "password": app_password,
                                                                                       "amount": amount_refund,
                                                                                       "originalTransactionId": str(
                                                                                           original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            txn_id_after_refund = response.get('txnId')
            logger.debug(f"Query result, txn_id_after_refund : {txn_id_after_refund}")

            query = f"select * from txn where orig_txn_id = '{original_txn_id}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch Txn details from the DB after refund: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_after_refund = result['id'].values[0]
            logger.debug(f"txn id from txn table after refund : {txn_id_after_refund}")
            amount_after_refund = result['amount'].values[0]
            logger.debug(f"amount from txn table after refund: {amount_after_refund}")
            state_after_refund = result['state'].values[0]
            logger.debug(f"state from txn table after refund: {state_after_refund}")
            status_after_refund = result['status'].values[0]
            logger.debug(f"status from txn table after refund: {status_after_refund}")
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway from txn table after refund: {payment_gateway_after_refund}")
            settlement_status_after_refund = result['settlement_status'].values[0]
            logger.debug(f"settlement_status from txn table after refund: {settlement_status_after_refund}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            order_id_after_refund = result['external_ref'].values[0]
            logger.debug(f"Order Id after refund : {refund_txn_type}")

            query = f"select * from cnpware_txn where txn_id='{txn_id_after_refund}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            amount_after_refund = result['amount'].values[0]
            logger.debug(f"amount from cnpware_txn table : {amount_after_refund}")
            state_after_refund = result['state'].values[0]
            logger.debug(f"state from cnpware_txn table : {state_after_refund}")
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway from cnpware_txn table : {payment_gateway_after_refund}")
            payment_flow_after_refund = result['payment_flow'].values[0]
            logger.debug(f"payment_flow from cnpware_txn table : {payment_flow_after_refund}")
            txn_type_after_refund = result['txn_type'].values[0]
            logger.debug(f" txn type after refund : {txn_type_after_refund}")

            query = f"select * from cnp_txn where txn_id='{txn_id_after_refund}';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            state_cnp_txn = result['state'].values[0]
            logger.debug(f"Query result, state_cnp_txn : {state_cnp_txn}")
            payment_mode_cnp_txn = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode_cnp_txn : {payment_mode_cnp_txn}")

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
                date_and_time_2 = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_mode": "PAY LINK",
                    "txn_id": original_txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,
                    "pmt_status_2": "STATUS:REFUND_POSTED",
                    "pmt_mode_2": "PAY LINK",
                    "txn_id_2": txn_id_after_refund,
                    "txn_amt_2": "{:,.2f}".format(amount_refund),
                    "order_id_2": order_id,
                    "msg_2": "REFUND PENDING",
                    "customer_name_2": txn_customer_name,
                    "settle_status_2": settlement_status_after_refund,
                    "date_2": date_and_time_2
                }
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_after_refund)

                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from  MPOS app: {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from MPOS app: {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from  MPOS app: {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from  MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status from MPOS app: {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from  MPOS app:  {payment_msg_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from app transaction history: order Id = {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status txn from MPOS app: {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode  txn from MPOS app:{app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from  MPOS app:  {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of original txn from  MPOS app: {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"settlement status of original txn from MPOS app:{app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from MPOS app: Txn Id = {app_txn_id_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from app transaction history: order Id = {app_order_id}")
                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_mode": app_payment_mode_original,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "msg": payment_msg_original,
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "order_id_2": app_order_id_refunded,
                    "msg_2": payment_msg_refunded,
                    "customer_name_2": txn_customer_name,
                    "settle_status_2": app_settlement_status_refunded,
                    "date_2": app_date_and_time_refunded
                }
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
                logger.info(f"Completed API validation for the test case : {testcase_id}")
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
                logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info(f"Started API validation for the test case : {testcase_id}")
                date = date_time_converter.db_datetime(created_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "settle_status": "SETTLED",
                    "txn_amt": str(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type,
                    "org_code": org_code_txn,
                    "auth_code": auth_code,
                    "date": date,
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode_2": "CNP",
                    "settle_status_2": "REVPENDING",
                    "txn_amt_2": str(amount_refund),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "order_id_2": order_id,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": refund_txn_type,
                    "org_code_2": org_code_txn,
                    "date_2": refund_date,
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status_api_original: {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"amount_api_original: {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"payment_mode_api_original: {payment_mode_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state_api_original: {state_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"settlement_status_api_original: {settlement_status_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code_api_original: {issuer_code_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_original: {acquirer_code_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code_api_original: {org_code_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"txn_type_api_original: {txn_type_api_original}")
                auth_code_api_original = response["authCode"]
                logger.debug(f"auth_code_api_original: {auth_code_api_original}")
                date_api_original = response["createdTime"]
                logger.debug(f"date_api_original: {date_api_original}")
                order_id_api_original = response["orderNumber"]
                logger.debug(f"order_id_api_original: {order_id_api_original}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_after_refund][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status_api_refunded: {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount_api_refunded: {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode_api_refunded: {payment_mode_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state_api_refunded: {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status_api_refunded: {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_refunded: {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code_api_refunded: {org_code_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type_api_refunded: {txn_type_api_refunded}")
                date_api_refunded = response["createdTime"]
                logger.debug(f"date_api_refunded: {date_api_refunded}")
                order_id_api_refunded = response["orderNumber"]
                logger.debug(f"order_id_api_refunded: {order_id_api_refunded}")
                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_state": state_api_original,
                    "pmt_mode": payment_mode_api_original,
                    "settle_status": settlement_status_api_original,
                    "txn_amt": str(amount_api_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id_api_original,
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "org_code": org_code_api_original,
                    "auth_code": auth_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "order_id_2": order_id_api_refunded,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
                }
                logger.debug(f"actualAPIValues: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                expected_db_values = {
                    "pmt_status": "REFUND_POSTED",
                    "pmt_state": "REFUND_INITIATED",
                    "pmt_mode": "CNP",
                    "txn_amt": str(amount) + ".0",
                    "order_id": order_id,
                    "cnp_txn_status": "SETTLED",
                    "settle_status": "REVPENDING",
                    "acquirer_code": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY",
                    "cnpware_pmt_flow": "REMOTEPAY",

                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode_2": "CNP",
                    "txn_amt_2": str(amount_refund) + ".0",
                    "order_id_2": order_id,
                    "cnp_txn_status_2": "REFUND_INITIATED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "HDFC",
                    "pmt_gateway_2": "RAZORPAY",
                    "cnpware_txn_type_2": "REFUND",
                    "cnpware_pmt_flow_2": "None",
                }
                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from txn where id = '{txn_id_after_refund}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                payment_mode_db = result['payment_mode'].values[0]
                logger.debug(f"paymentMode from txn table : {payment_mode_db}")
                state_db = result['state'].values[0]
                logger.debug(f"state from txn table : {state_db}")
                status_db = result['status'].values[0]
                logger.debug(f"status from txn table : {status_db}")
                acquirer_code_db = result['acquirer_code'].values[0]
                logger.debug(f"acquirer_code from txn table : {acquirer_code_db}")
                payment_gateway_db = result['payment_gateway'].values[0]
                logger.debug(f"payment_gateway from txn table : {payment_gateway_db}")
                settlement_status_db = result['settlement_status'].values[0]
                logger.debug(f"settlement_status from txn table : {settlement_status_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": str(original_amount_db),
                    "order_id": order_id,
                    "cnp_txn_status": state_cnp_txn_original,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "cnpware_txn_type": original_txn_type,
                    "cnpware_pmt_flow": original_payment_flow_cnpware,
                    "pmt_status_2": status_after_refund,
                    "pmt_state_2": state_after_refund,
                    "pmt_mode_2": payment_mode_cnp_txn,
                    "txn_amt_2": str(amount_after_refund),
                    "order_id_2": order_id_after_refund,
                    "cnp_txn_status_2": state_cnp_txn,
                    "settle_status_2": settlement_status_after_refund,
                    "acquirer_code_2": original_acquirer_code_cnpware,
                    "pmt_gateway_2": payment_gateway_after_refund,
                    "cnpware_txn_type_2": txn_type_after_refund,
                    "cnpware_pmt_flow_2": str(payment_flow_after_refund),
                }
                logger.debug(f"actualDBValues : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_refund = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "txn_id": original_txn_id,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "date_time_2": date_and_time_portal_refund,
                    "txn_id_2": txn_id_after_refund,
                    "pmt_state_2": "REFUND_POSTED",
                    "pmt_type_2": "CNP",
                    "txn_amt_2": "{:,.2f}".format(amount_refund),
                    "username_2": app_username
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                logger.debug(f"date_time_2: {date_time_2}")
                txn_id_portal_2 = transaction_details[0]['Transaction ID']
                logger.debug(f"txn_id_portal_2: {txn_id_portal_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount_2: {total_amount_2}")
                status_2 = transaction_details[0]['Status']
                logger.debug(f"status_2: {status_2}")
                username_2 = transaction_details[0]['Username']
                logger.debug(f"username_2: {username_2}")
                date_time = transaction_details[1]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                txn_id_portal = transaction_details[1]['Transaction ID']
                logger.debug(f"txn_id_portal: {txn_id_portal}")
                total_amount = transaction_details[1]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                transaction_type = transaction_details[1]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[1]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[1]['Username']
                logger.debug(f"username: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "date_time_2": date_time_2,
                    "txn_id_2": txn_id_portal_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of chargeslip Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {
                    "payment_option": "SALE",
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': f"Rs.{amount:,}.00",
                    'date': txn_date, 'time': txn_time,
                }
                logger.debug(
                    f"expected_chargeslip_values : {expected_charge_slip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(original_txn_id,
                                                                  {"username": app_username, "password": app_password},
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_186():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Success_Razorpay
    Sub Feature Description: Verification of a successful debit card txn via CNP link
    Sub Feature Code: UI_Common_PM_CNP_ChargeSlip_Val_debit_Card_Success_Razorpay
    Sub Feature Description: Verification of a charge slip validation for debit card txn via CNP link
    TC naming code description: 100: Payment Method, 103: CNP, 186: TC_186
    """
    expected_success_message = "Your payment is successfully completed! You may close the browser now."
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username, portal_pw=portal_password,
                                                               payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.info(f"response from api after payment initiating {response}")
            if not response['success']:
                raise Exception("Api could not initate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("4111 1111 1111 1111")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.enter_otp("1111")
                remote_pay_txn.submit_otp()
                remote_pay_txn.wait_for_success_message()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your success message is:  {success_message}")
                logger.info(f"Your expected success message is:  {expected_success_message}")
                if success_message == expected_success_message:
                    pass
                else:
                    raise Exception("Success messages are not matching.")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"txn_id from db : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"customer_name from db : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"settle_status from db  : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"auth_code fro db : {txn_auth_code}")
            txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"issuer_code fro  db : {txn_issuer_code}")
            txn_posting_date = result['posting_date'].values[0]
            logger.debug(f"posting date from db : {txn_posting_date}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.info(f"cnp_payment_flow from cnp_txn : {cnp_payment_flow}")

            query = f"select * from cnpware_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {txn_id}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['txn_id'].values[0]
            logger.debug(f"Query result from cnp_txn, Txn_id : {txn_id}")
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result from cnp_txn, org_code : {org_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, db date from db : {created_time}")

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
                date_and_time = date_time_converter.to_app_format(txn_posting_date)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "auth_code": txn_auth_code,
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {payment_status_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"txn settlement status from txn history for the txn : {payment_settlement_status}")

                payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {payment_auth_code}")
                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "order_id": payment_order_id,
                    "msg": payment_status_msg,
                    "customer_name": payment_customer_name,
                    "settle_status": payment_settlement_status,
                    "auth_code": payment_auth_code,
                    "date": app_date_and_time}

                logger.debug(f"actualAppValues: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                date = date_time_converter.db_datetime(txn_posting_date)
                logger.info(f"Started API validation for the test case : {testcase_id}")
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": cnp_txn_acquirer_code,
                    "settle_status": txn_settle_status,
                    "issuer_code": txn_issuer_code,
                    "txn_type": cnpware_txn_txn_type,
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"status_api: {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api: {amount_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api: {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api: {txn_type_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api: {org_code_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": "CNP",
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": acquirer_code_api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date}

                logger.debug(f"actualAPIValues: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": cnpware_payment_flow,
                    "pmt_intent_status": "COMPLETED"
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")
                query = f"select * from txn where id='{txn_id}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                pmt_status_db = result["status"].iloc[0]
                logger.debug(f"pmt_status_db: {pmt_status_db}")
                pmt_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"pmt_mode_db: {pmt_mode_db}")
                txn_amt_db = int(result["amount"].iloc[0])
                logger.debug(f"txn_amt_db: {txn_amt_db}")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settle_status_db: {settle_status_db}")
                pmt_state_db = result["state"].iloc[0]
                logger.debug(f"pmt_state_db: {pmt_state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db: {payment_gateway_db}")

                query = f"select * from payment_intent where id='{payment_intent_id}';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"payment_intent_status: {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": pmt_status_db,
                    "pmt_state": pmt_state_db,
                    "pmt_mode": pmt_mode_db,
                    "txn_amt": txn_amt_db,
                    "settle_status": settle_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status
                }

                logger.debug(f"actualDBValues : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "txn_id": txn_id,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    'auth_code': txn_auth_code
                }
                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                txn_id_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"txn_id_portal: {txn_id_portal}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code: {auth_code}")
                txn_type_portal = transaction_details[0]['Type']
                logger.debug(f"txn_type_portal: {txn_type_portal}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "pmt_state": str(status),
                    "pmt_type": txn_type_portal,
                    "txn_amt": total_amount[1],
                    "username": username,
                    'auth_code': auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_posting_date)
                expected_values = {
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    "time": txn_time,
                    "AUTH CODE": txn_auth_code}

                receipt_validator.perform_charge_slip_validations(txn_id,
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_187():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Failed_Razorpay
    Sub Feature Description: Verification debit card failed txn for Razorpay source pg
    TC naming code description: 100: Payment Method, 103: CNP, 187: TC_187
    """
    expected_failed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact " \
                              "support@ezetap.com for further clarifications."
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username, portal_pw=portal_password,
                                                               payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from cnp initiate api is: {response}")
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info("Enter Debit card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterDebitCardExpiryMonth("12")
                remote_pay_txn.enterDebitCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_failure_pmt_btn()

                actual_failed_message = str(remote_pay_txn.failedScreenMessage())
                logger.info(f"After txn message is:  : {actual_failed_message}")
                if expected_failed_message == actual_failed_message:
                    pass
                else:
                    print("Failed Message is not matching")

            query = f"select * from payment_intent where id='{payment_intent_id}'"
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            payment_intent_status = result["status"].iloc[0]

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, db date from db : {created_time}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")

            query = f"select rr_number from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_flow}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")

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
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount) + ".00",
                    "txn_id": txn_id,
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,
                    "order_id": order_id,
                    "msg": "PAYMENT FAILED",
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn :{payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn :{payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn :{app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn :{app_amount}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn :{payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {payment_settlement_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn :{payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {payment_status_msg}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "customer_name": payment_customer_name,
                    "settle_status": payment_settlement_status,
                    "date": app_date_and_time,
                    "order_id": payment_order_id,
                    "msg": payment_status_msg,
                }

                logger.debug(f"actualAppValues: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                date = date_time_converter.db_datetime(created_time)
                logger.info("Started API validation for the test case : test_common_100_103_008")
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "pmt_state": "FAILED",
                    "acquirer_code": "HDFC",
                    "settle_status": "FAILED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date
                }

                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api}")
                amount_api = response["amount"]
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction payment acquirer_code from transaction api : {acquirer_code_api} ")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching Transaction payment settlement_status from transaction api : {settlement_status_api} ")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching Transaction payment issuer_code from transaction api : {issuer_code_api} ")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching Transaction payment txn_type from transaction api : {txn_type_api} ")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching Transaction payment org_code from transaction api : {org_code_api} ")
                date_api = response["postingDate"]
                logger.debug(f"Fetching Transaction payment date from transaction api : {date_api} ")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": acquirer_code_api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }

                logger.debug(f"actualAPIValues: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Started DB validation for the test case : test_common_100_103_008")
                expected_db_values = {
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "FAILED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "ACTIVE"
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"amount_db: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db: {state_db}")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settle_status_db: {settle_status_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db: {payment_gateway_db}")

                query = f"select * from cnpware_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settle_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status
                }
                logger.debug(f"actualDBValues : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time,
                    "txn_id": txn_id,
                    "pmt_state": "FAILED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.debug(f"date_time_portal: {date_time_portal}")
                txn_id_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"txn_id_portal: {txn_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount_portal: {total_amount_portal}")
                txn_type_portal = transaction_details[0]['Type']
                logger.debug(f"txn_type_portal: {txn_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.debug(f"status_portal: {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.debug(f"username_portal: {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "txn_id": txn_id_portal,
                    "pmt_state": str(status_portal),
                    "pmt_type": txn_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
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
def test_common_100_103_188():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_After_Timeout_Razorpay
    Sub Feature Description: Verification of  debit card txn after timeout via CNP link
    TC naming code description: 100: Payment Method, 103: CNP, 188: TC_188
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        query = "update remotepay_setting set setting_value= '2' where setting_name='cnpTxnTimeoutDuration' " \
                "and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result for remote pay setting is: {result}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from cnp initiate api is: {response}")
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info("Enter Debit card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("4111 1111 1111 1111")
                remote_pay_txn.enterDebitCardExpiryMonth("12")
                remote_pay_txn.enterDebitCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.enter_otp("1111")

            query = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '" + str(
                org_code) + "';"
            logger.debug(f"Query to fetch max Attempts from the DB : {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"result : {result}")
                logger.debug(f"type of result: {type(result)}")
                org_setting_value = int(result['setting_value'].values[0])
                logger.info(f"Timeout for {org_code} is {org_setting_value}")
            except Exception as e:
                org_setting_value = None
                print(e)

            query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and " \
                     "org_code = 'EZETAP'"
            logger.debug(f"Timeout for Ezetap is : {query1}")
            try:
                default_value = DBProcessor.getValueFromDB(query1)
                setting_value = int(default_value['setting_value'].values[0])
                logger.info(f"max upi attempt is: {setting_value}")
            except NameError as e:
                setting_value = None
                print(e)
            except IndexError as e:
                setting_value = None
                print(e)
            except Exception as e:
                print(e)

            if org_setting_value:
                logger.info(f"Value for max upi attempt is: {org_setting_value} min.")
                time.sleep(10 + (org_setting_value * 60))
            else:
                logger.info(f"Value for Ezetap org is: {org_setting_value} min.")
                time.sleep(10 + (setting_value * 60))

            remote_pay_txn.submit_otp()

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, db date from db : {created_time}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]

            query = f"select * from cnpware_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")

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
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount) + ".00",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT FAILED",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn :{payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn :{payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn :{app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn :{app_amount}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn :{payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn :{payment_status_msg}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn :{payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn :{payment_settlement_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "order_id": payment_order_id,
                    "msg": payment_status_msg,
                    "customer_name": payment_customer_name,
                    "settle_status": payment_settlement_status,
                    "date": app_date_and_time
                }
                logger.debug(f"actualAppValues: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info("Started API validation for the test case : test_common_100_103_011")
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnp_pmt_card_type": "CREDIT",
                    "pmt_state": "TIME_OUT_PENDING",
                    "acquirer_code": "HDFC",
                    "settle_status": "FAILED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api}")
                amount_api = response["amount"]
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api}")
                payment_card_brand = response["paymentCardBrand"]
                logger.debug(f"Fetching Transaction payment Card Brand from transaction api : {payment_card_brand}")
                payment_card_type = response["paymentCardType"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {payment_card_type}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction payment acquirer_code from transaction api : {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching Transaction payment settlement_status from transaction api : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching Transaction payment issuer_code from transaction api : {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching Transaction payment txn_type from transaction api : {txn_type_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching Transaction payment org_code from transaction api : {org_code_api}")
                date_api = response["postingDate"]
                logger.debug(f"Fetching Transaction payment date from transaction api : {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": "CNP",
                    "cnp_pmt_card_brand": payment_card_brand,
                    "cnp_pmt_card_type": payment_card_type,
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": acquirer_code_api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }

                logger.debug(f"actualAPIValues: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Started DB validation for the test case : test_common_100_103_011")
                expected_db_values = {
                    "pmt_status": "FAILED",
                    "pmt_state": "TIME_OUT_PENDING",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "FAILED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "ACTIVE"
                }
                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"amount_db: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db: {state_db}")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settle_status_db: {settle_status_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db: {payment_gateway_db}")

                query = f"select * from payment_intent where id='{payment_intent_id}'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"payment_intent_status: {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settle_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status
                }
                logger.debug(f"actualDBValues : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "txn_id": txn_id,
                    "pmt_state": "FAILED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                txn_id_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"txn_id_portal: {txn_id_portal}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_189():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Refund_Razorpay
    Sub Feature Description: Verification of debit card txn refund using refund api
    TC naming code description: 100: Payment Method, 103: CNP, 189: TC_189
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
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

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1501, 2000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={"amount": amount,
                                                                                          "externalRefNumber": order_id,
                                                                                          "username": app_username,
                                                                                          "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from api is: {response}")
            if not response['success']:
                raise Exception("Api could not initate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info("Enter Debit card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enterDebitCardExpiryMonth("12")
                remote_pay_txn.enterDebitCardExpiryYear("2050")
                remote_pay_txn.enter_debit_card_cvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.enter_otp("1111")
                remote_pay_txn.submit_otp()

                remote_pay_txn.wait_for_success_message()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected_message is:  {expected_message}")
            if success_message == expected_message:
                pass
            else:
                raise Exception("Success Message is not matching.")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"txn id from txn table : {original_txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            original_txn_type = result['txn_type'].values[0]

            query = f"select * from cnpware_txn where txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            original_acquirer_code_cnpware = result['acquirer_code'].values[0]
            logger.debug(f"original_acquirer_code_cnpware from cnpware_txn table : {original_acquirer_code_cnpware}")
            original_payment_flow_cnpware = result['payment_flow'].values[0]
            logger.debug(f"original_payment_flow from cnpware_txn table : {original_payment_flow_cnpware}")

            query = f"select * from cnp_txn where txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            state_cnp_txn_original = result['state'].values[0]
            logger.debug(f"Query result, state_cnp_txn_original : {state_cnp_txn_original}")
            txn_card_type = result['payment_option'].values[0]
            logger.debug(f"txn card type from db : {txn_card_type}")

            api_details = DBProcessor.get_api_details('RemotePayRefund', request_body={"username": app_username,
                                                                                       "password": app_password,
                                                                                       "amount": amount,
                                                                                       "originalTransactionId": str(
                                                                                           original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            txn_id_after_refund = response.get('txnId')
            logger.debug(f"Query result, txn_id_after_refund : {txn_id_after_refund}")

            query = f"select * from txn where orig_txn_id = '{original_txn_id}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn details from the DB after refund: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_after_refund = result['id'].values[0]
            logger.debug(f"txn id from txn table after refund : {txn_id_after_refund}")
            amount_after_refund = result['amount'].values[0]
            logger.debug(f"amount from txn table after refund: {amount_after_refund}")
            state_after_refund = result['state'].values[0]
            logger.debug(f"state from txn table after refund: {state_after_refund}")
            status_after_refund = result['status'].values[0]
            logger.debug(f"status from txn table after refund: {status_after_refund}")
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway from txn table after refund: {payment_gateway_after_refund}")
            settlement_status_after_refund = result['settlement_status'].values[0]
            logger.debug(f"settlement_status from txn table after refund: {settlement_status_after_refund}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            order_id_after_refund = result['external_ref'].values[0]
            logger.debug(f"Order Id after refund : {refund_txn_type}")

            query = f"select * from cnpware_txn where txn_id='{txn_id_after_refund}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            txn_id_after_refund_cnpware = result['txn_id'].values[0]
            logger.debug(f"txn id from cnpware_txn table : {txn_id_after_refund_cnpware}")
            amount_after_refund = result['amount'].values[0]
            logger.debug(f"amount from cnpware_txn table : {amount_after_refund}")
            state_after_refund = result['state'].values[0]
            logger.debug(f"state from cnpware_txn table : {state_after_refund}")
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway from cnpware_txn table : {payment_gateway_after_refund}")
            payment_flow_after_refund = result['payment_flow'].values[0]
            logger.debug(f"payment_flow from cnpware_txn table : {payment_flow_after_refund}")
            txn_type_after_refund = result['txn_type'].values[0]
            logger.debug(f" txn type after refund : {txn_type_after_refund}")

            query = f"select * from cnp_txn where txn_id='{txn_id_after_refund}';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            state_cnp_txn = result['state'].values[0]
            logger.debug(f"Query result, state_cnp_txn : {state_cnp_txn}")
            payment_mode_cnp_txn = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode_cnp_txn : {payment_mode_cnp_txn}")

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
                date_and_time_2 = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_mode": "PAY LINK",
                    "txn_id": original_txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,
                    "pmt_status_2": "STATUS:REFUND_POSTED",
                    "pmt_mode_2": "PAY LINK",
                    "txn_id_2": txn_id_after_refund,
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "order_id_2": order_id,
                    "msg_2": "REFUND PENDING",
                    "customer_name_2": txn_customer_name,
                    "settle_status_2": settlement_status_after_refund,
                    "date_2": date_and_time_2
                }
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_after_refund)

                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn app history page : {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"app_payment_status_refunded from txn app history page  = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"app_payment_mode_refunded from txn app history page = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching app_txn_id_refunded from txn app history page = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching app_payment_amt_refunded from txn app history page ={app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching app_settlement_status_refunded from txn app history page = "
                             f"{app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching payment_msg_refunded from txn app history page = {payment_msg_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from app transaction history: order Id = {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching app_payment_status_original from txn app history page  = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching app_payment_mode_original from txn app history page  = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching app_txn_id_original from txn app history page = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching app_payment_amt_original from txn history page = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching app_settlement_status_original from txn app history page = "
                             f"{app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching payment_msg_original from txn app history page = {app_txn_id_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from app transaction history: order Id = {app_order_id}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_mode": app_payment_mode_original,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "msg": payment_msg_original,
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "order_id_2": app_order_id_refunded,
                    "msg_2": payment_msg_refunded,
                    "customer_name_2": txn_customer_name,
                    "settle_status_2": app_settlement_status_refunded,
                    "date_2": app_date_and_time_refunded
                }
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
                logger.info(f"Completed API validation for the test case : {testcase_id}")
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
                logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info(f"Started API validation for the test case : {testcase_id}")
                date = date_time_converter.db_datetime(created_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "settle_status": "SETTLED",
                    "txn_amt": str(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type,
                    "org_code": org_code_txn,
                    "auth_code": auth_code,
                    "date": date,

                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode_2": "CNP",
                    "settle_status_2": "REVPENDING",
                    "txn_amt_2": str(amount),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "order_id_2": order_id,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": refund_txn_type,
                    "org_code_2": org_code_txn,
                    "date_2": refund_date,
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status_api_original: {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"amount_api_original: {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"payment_mode_api_original: {payment_mode_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state_api_original: {state_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"settlement_status_api_original: {settlement_status_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code_api_original: {issuer_code_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_original: {acquirer_code_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code_api_original: {org_code_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"txn_type_api_original: {txn_type_api_original}")
                auth_code_api_original = response["authCode"]
                logger.debug(f"auth_code_api_original: {auth_code_api_original}")
                date_api_original = response["createdTime"]
                logger.debug(f"date_api_original: {date_api_original}")
                order_id_api_original = response["orderNumber"]
                logger.debug(f"order_id_api_original: {order_id_api_original}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_after_refund][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status_api_refunded: {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount_api_refunded: {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode_api_refunded: {payment_mode_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state_api_refunded: {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status_api_refunded: {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_refunded: {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code_api_refunded: {org_code_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type_api_refunded: {txn_type_api_refunded}")
                date_api_refunded = response["createdTime"]
                logger.debug(f"date_api_refunded: {date_api_refunded}")
                order_id_api_refunded = response["orderNumber"]
                logger.debug(f"order_id_api_refunded: {order_id_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_state": state_api_original,
                    "pmt_mode": payment_mode_api_original,
                    "settle_status": settlement_status_api_original,
                    "txn_amt": str(amount_api_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id_api_original,
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "org_code": org_code_api_original,
                    "auth_code": auth_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "order_id_2": order_id_api_refunded,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
                }
                logger.debug(f"actualAPIValues: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "order_id": order_id,
                    "cnp_txn_status": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "card_type": "CNP_DC",
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode_2": "CNP",
                    "txn_amt_2": amount,
                    "order_id_2": order_id,
                    "cnp_txn_status_2": "REFUND_INITIATED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "HDFC",
                    "pmt_gateway_2": "RAZORPAY",
                    "cnpware_txn_type_2": "REFUND",
                    "cnpware_pmt_flow_2": "None",
                }
                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from txn where id = '{str(original_txn_id)}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                amount_txn_db = result['amount'].values[0]
                logger.debug(f"amount from txn table : {amount_txn_db}")
                payment_mode_db = result['payment_mode'].values[0]
                logger.debug(f"paymentMode from txn table : {payment_mode_db}")
                state_db = result['state'].values[0]
                logger.debug(f"state from txn table : {state_db}")
                status_db = result['status'].values[0]
                logger.debug(f"status from txn table : {status_db}")
                acquirer_code_db = result['acquirer_code'].values[0]
                logger.debug(f"acquirer_code from txn table : {acquirer_code_db}")
                payment_gateway_db = result['payment_gateway'].values[0]
                logger.debug(f"payment_gateway from txn table : {payment_gateway_db}")
                settlement_status_db = result['settlement_status'].values[0]
                logger.debug(f"settlement_status from txn table : {settlement_status_db}")
                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_txn_db,
                    "order_id": order_id,
                    "cnp_txn_status": state_cnp_txn_original,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "cnpware_txn_type": original_txn_type,
                    "cnpware_pmt_flow": original_payment_flow_cnpware,
                    "card_type": txn_card_type,
                    "pmt_status_2": status_after_refund,
                    "pmt_state_2": state_after_refund,
                    "pmt_mode_2": payment_mode_cnp_txn,
                    "txn_amt_2": amount_after_refund,
                    "order_id_2": order_id_after_refund,
                    "cnp_txn_status_2": state_cnp_txn,
                    "settle_status_2": settlement_status_after_refund,
                    "acquirer_code_2": original_acquirer_code_cnpware,
                    "pmt_gateway_2": payment_gateway_after_refund,
                    "cnpware_txn_type_2": txn_type_after_refund,
                    "cnpware_pmt_flow_2": str(payment_flow_after_refund),
                }
                logger.debug(f"actualDBValues : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_refund = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "txn_id": original_txn_id,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "date_time_2": date_and_time_portal_refund,
                    "txn_id_2": txn_id_after_refund,
                    "pmt_state_2": "REFUND_POSTED",
                    "pmt_type_2": "CNP",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                logger.debug(f"date_time_2: {date_time_2}")
                txn_id_portal_2 = transaction_details[0]['Transaction ID']
                logger.debug(f"txn_id_portal_2: {txn_id_portal_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount_2: {total_amount_2}")
                status_2 = transaction_details[0]['Status']
                logger.debug(f"status_2: {status_2}")
                username_2 = transaction_details[0]['Username']
                logger.debug(f"username_2: {username_2}")
                date_time = transaction_details[1]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                txn_id_portal = transaction_details[1]['Transaction ID']
                logger.debug(f"txn_id_portal: {txn_id_portal}")
                total_amount = transaction_details[1]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                transaction_type = transaction_details[1]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[1]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[1]['Username']
                logger.debug(f"username: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "date_time_2": date_time_2,
                    "txn_id_2": txn_id_portal_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of chargeslip Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {
                    "payment_option": "SALE",
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': f"Rs.{amount:,}.00",
                    'date': txn_date, 'time': txn_time
                }
                logger.debug(
                    f"expected_charge_slip_values : {expected_charge_slip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(original_txn_id,
                                                                  {"username": app_username, "password": app_password},
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
