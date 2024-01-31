import random
import sys
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter, receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_111_041():
    """
    Sub Feature Code: UI_Common_PM_Pure_RP_UPI_COLLECT_full_Refund_via_API_Razorpay
    Sub Feature Description: Multi Account - Performing a full RP_UPI_COLLECT refund using api for Razorpay
    TC naming code description:100: Payment Method, 111: MultiAcc_RemotePay, 041: TC041
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
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        account_label_name_2 = account_labels['name1']
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id : {upi_mc_id}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Query result, mid : {mid}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Query result, tid : {tid}")
        acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"Query result, acc_label_id : {acc_label_id}")
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

            amount = random.randint(1501, 1601)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount, "externalRefNumber": order_id, "username": app_username, "password": app_password,
                "accountLabel": str(account_label_name)})

            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            paymentLinkUrl = response['paymentLink']
            ui_browser.goto(paymentLinkUrl)
            remotePayUpiCollectTxn = RemotePayTxnPage(ui_browser)
            remotePayUpiCollectTxn.clickOnRemotePayUPI()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()
            remotePayUpiCollectTxn.clickOnRemotePayCancelUPI()
            remotePayUpiCollectTxn.clickOnRemotePayProceed()
            logger.info("UPI Collect txn is completed.")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}'"
            logger.debug(f"Query to fetch transaction details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_original = result["id"].iloc[0]
            logger.debug(f"Query result, txn_id_original : {txn_id_original}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name : {payer_name}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code : {auth_code}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code_txn : {org_code_txn}")
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"rrn_original: {rrn_original}")
            txn_type_original = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type_original : {txn_type_original}")
            label_ids_original = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"Query result, label_ids_original : {label_ids_original}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={"username": app_username,
                                                                                     "password": app_password,
                                                                                     "amount": amount,
                                                                                     "originalTransactionId": str(
                                                                                         txn_id_original)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id = '{str(txn_id_original)}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Query result, txn_id_refunded : {txn_id_refunded}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, refund_auth_code : {refund_auth_code}")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type_refunded : {txn_type_refunded}")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Query result, rrn_refunded : {rrn_refunded}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, posting_date : {posting_date}")
            label_ids_refunded = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"Query result, label_ids_refunded : {label_ids_refunded}")
            # -------------------------------------------------------------------------------------------------------
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
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED_REFUNDED",
                    "refund_pmt_status": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "refund_pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "refund_settle_status": "SETTLED",
                    "txn_id": txn_id_original,
                    "refund_txn_id": txn_id_refunded,
                    "txn_amt": "{:,.2f}".format(amount),
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "customer_name": customer_name,
                    "refund_customer_name": customer_name,
                    "payer_name": payer_name,
                    "refund_payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "refund_pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(rrn_original),
                    "refund_rrn": str(rrn_refunded),
                    "date": date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
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

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_original)
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
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "refund_customer_name": customer_name,
                    "payer_name": payer_name,
                    "refund_payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "refund_pmt_msg": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "refund_rrn": str(app_rrn_refunded),
                    "date": app_date_and_time
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
                    "original_rrn": str(rrn_original),
                    "refunded_rrn": str(rrn_refunded),
                    "original_acquirer_code": "RAZORPAY",
                    "original_issuer_code": "RAZORPAY",
                    "original_txn_type": txn_type_original,
                    "original_mid": mid, "original_tid": tid,
                    "original_org_code": org_code_txn,
                    "refunded_acquirer_code": "RAZORPAY",
                    "refunded_txn_type": txn_type_refunded,
                    "refunded_mid": mid, "refunded_tid": tid,
                    "refunded_org_code": org_code_txn,
                    "date": date,
                    "account_label": str(account_label_name),
                    "account_label_2": str(account_label_name)
                }
                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_original][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status_api_original: {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"amount_api_original: {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"payment_mode_api_original: {payment_mode_api_original}")
                rrn_api_original = response["rrNumber"]
                logger.debug(f"rrn_api_original: {rrn_api_original}")
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
                mid_api_original = response["mid"]
                logger.debug(f"mid_api_original: {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid_api_original: {tid_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"txn_type_api_original: {txn_type_api_original}")
                account_label_name_api_original = response["accountLabel"]
                logger.debug(f"account_label_name_api_original: {account_label_name_api_original}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status_api_refunded: {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount_api_refunded: {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode_api_refunded: {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn_api_refunded: {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state_api_refunded: {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status_api_refunded: {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_refunded: {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code_api_refunded: {org_code_api_refunded}")
                mid_api_refunded = response["mid"]
                logger.debug(f"mid_api_refunded: {mid_api_refunded}")
                tid_api_refunded = response["tid"]
                logger.debug(f"tid_api_refunded: {tid_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type_api_refunded: {txn_type_api_refunded}")
                date_api_refunded = response["postingDate"]
                logger.debug(f"date_api_refunded: {date_api_refunded}")
                account_label_name_api_refunded = response["accountLabel"]
                logger.debug(f"account_label_name_api_refunded: {account_label_name_api_refunded}")

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
                    "date": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "account_label": str(account_label_name_api_original),
                    "account_label_2": str(account_label_name_api_refunded)
                }
                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
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
                    "original_acquirer_code": "RAZORPAY",
                    "refunded_acquirer_code": "RAZORPAY",
                    "original_bank_code": "RAZORPAY",
                    "original_upi_txn_type": "COLLECT",
                    "refunded_upi_txn_type": "REFUND",
                    "original_upi_bank_code": "RAZORPAY_PSP",
                    "refunded_upi_bank_code": "RAZORPAY_PSP",
                    "original_upi_mc_id": upi_mc_id,
                    "refunded_upi_mc_id": upi_mc_id,
                    "original_mid": mid,
                    "original_tid": tid,
                    "refund_mid": mid,
                    "refund_tid": tid,
                    "acc_label_id": str(acc_label_id),
                    "acc_label_id_2": str(acc_label_id),
                    "pmt_gateway_original": "RAZORPAY",
                    "pmt_gateway_refund": "RAZORPAY"
                }
                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = f"select * from txn where id='{txn_id_refunded}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"status_db_refunded: {status_db_refunded}")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_refunded: {payment_mode_db_refunded}")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_refunded: {amount_db_refunded}")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"state_db_refunded: {state_db_refunded}")
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db_refunded: {payment_gateway_db_refunded}")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_refunded: {acquirer_code_db_refunded}")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_refunded: {settlement_status_db_refunded}")
                tid_db_refunded = result['tid'].values[0]
                logger.debug(f"tid_db_refunded: {tid_db_refunded}")
                mid_db_refunded = result['mid'].values[0]
                logger.debug(f"mid_db_refunded: {mid_db_refunded}")

                query = f"select * from upi_txn where txn_id='{txn_id_refunded}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"upi_status_db_refunded: {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db_refunded: {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_refunded: {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db_refunded: {upi_mc_id_db_refunded}")

                query = f"select * from txn where id='{txn_id_original}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"status_db_original: {status_db_original}")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_original: {payment_mode_db_original}")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_original: {amount_db_original}")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"state_db_original: {state_db_original}")
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db_original: {payment_gateway_db_original}")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_original: {acquirer_code_db_original}")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db_original: {bank_code_db_original}")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_original: {settlement_status_db_original}")
                tid_db_original = result['tid'].values[0]
                logger.debug(f"tid_db_original: {tid_db_original}")
                mid_db_original = result['mid'].values[0]
                logger.debug(f"mid_db_original: {mid_db_original}")

                query = f"select * from upi_txn where txn_id='{txn_id_original}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"upi_status_db_original: {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db_original: {upi_txn_type_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_original: {upi_bank_code_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db_original: {upi_mc_id_db_original}")

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
                    "acc_label_id": str(label_ids_original),
                    "acc_label_id_2": str(label_ids_refunded),
                    "pmt_gateway_original": payment_gateway_db_original,
                    "pmt_gateway_refund": payment_gateway_db_refunded
                }
                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(posting_date)
                date_and_time_portal_2 = date_time_converter.to_portal_format(posting_date)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id_original,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn_original),
                    "acc_label": account_label_name,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code,
                    "rrn_2": "-" if rrn_refunded is None else str(rrn_refunded),
                    "acc_label_2": account_label_name_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                logger.debug(f"date_time_2: {date_time_2}")
                transaction_id_2 = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id_2: {transaction_id_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount_2: {total_amount_2}")
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code_portal_2: {auth_code_portal_2}")
                rr_number_2 = transaction_details[0]['RR Number']
                logger.debug(f"rr_number_2: {rr_number_2}")
                transaction_type_2 = transaction_details[0]['Type']
                logger.debug(f"transaction_type_2: {transaction_type_2}")
                status_2 = transaction_details[0]['Status']
                logger.debug(f"status_2: {status_2}")
                username_2 = transaction_details[0]['Username']
                logger.debug(f"username_2: {username_2}")
                labels_2 = transaction_details[0]['Labels']
                logger.debug(f"labels_2: {labels_2}")
                date_time = transaction_details[1]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[1]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[1]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code_portal = transaction_details[1]['Auth Code']
                logger.debug(f"auth_code_portal: {auth_code_portal}")
                rr_number = transaction_details[1]['RR Number']
                logger.debug(f"rr_number: {rr_number}")
                transaction_type = transaction_details[1]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[1]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[1]['Username']
                logger.debug(f"username: {username}")
                labels = transaction_details[1]['Labels']
                logger.debug(f"labels: {labels}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "acc_label": labels,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "acc_label_2": labels_2

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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_charge_slip_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                               'RRN': str(rrn_refunded),
                                               'BASE AMOUNT:': f"Rs.{amount:,}.00",
                                               'date': txn_date, 'time': txn_time,
                                               }
                logger.debug(
                    f"expected_chargeslip_values : {expected_charge_slip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
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
def test_common_100_111_042():
    """
    Sub Feature Code: UI_Common_PM_Pure_RP_UPI_COLLECT_partial_Refund_via_API_MultiAcc_Razorpay
    Sub Feature Description: Performing a partial refund RP_UPI_COLLECT through api for Razorpay
    TC naming code description: 100: Payment Method, 111: RemotePay, 042: TC_042
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

        query = f"select org_code from org_employee where username='{str(app_username)}'"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name_1 = account_labels['name1']
        logger.info(f"account label name is : {account_label_name_1}")
        query = f"select * from upi_merchant_config where org_code = '{str(org_code)}' and status = 'ACTIVE' " \
                f"and bank_code = 'RAZORPAY_PSP' and acc_label_id=(select id from label where " \
                f"name='{account_label_name_1}' and org_code ='{org_code}');"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Value of pg_merchant_id from upi_merchant_config table: {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table: {upi_mc_id}")
        acc_label_id = str(result['acc_label_id'].values[0])
        logger.debug(f"Value of acc_label_id from upi_merchant_config table: {acc_label_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1700, 2000)
            logger.info(f"Generated amount is : {amount}")
            refund_amount = 1560
            logger.info(f"partial refund amount is : {refund_amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Your unique order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "accountLabel": str(account_label_name_1)
            })
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                response = APIProcessor.send_request(api_details)
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
                logger.info("Clicking and opening the link in the browser")
                ui_browser.goto(payment_link_url)
                rp_upi_txn = RemotePayTxnPage(ui_browser)
                rp_upi_txn.clickOnRemotePayUPI()
                rp_upi_txn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                rp_upi_txn.clickOnRemotePayUpiCollectAppSelection()
                rp_upi_txn.clickOnRemotePayUpiCollectId("abc")
                rp_upi_txn.clickOnRemotePayUpiCollectDropDown("okhdfc")
                rp_upi_txn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                logger.info("Clicking on Proceed")
                rp_upi_txn.clickOnRemotePayUpiCollectProceed()

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id)}' " \
                    f"order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn_id from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.info(f"Fetching original txn id: {txn_id}")

            query = f"select * from upi_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch txn ref and txn ref3 from the upi_txn table for the {org_code} is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            logger.info(f"Fetching txn ref is: {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.info(f"Fetching txn ref3 is: {txn_ref_3}")

            callback_rrn_number = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_rrn_number}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = callback_rrn_number

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature, 'Content-Type': 'application/json'}
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Results from txn query is: {result}")
            auth_code = result['auth_code'].values[0]
            logger.info(f"Fetching auth code from txn table : {auth_code}")
            posting_date = result['posting_date'].values[0]
            logger.info(f"Fetching posting date info from txn table : {posting_date}")
            created_time = result['created_time'].values[0]
            logger.info(f"Fetching created time from txn table : {created_time}")
            customer_name = result['customer_name'].values[0]
            logger.info(f"Fetching customer name from txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.info(f"Fetching payer name from txn table : {payer_name}")
            rrn_db = result['rr_number'].iloc[0]
            logger.info(f"Fetching rrn from txn table: {rrn_db}")
            status_db = result['status'].iloc[0]
            logger.info(f"Fetching status from txn table : {status_db}")
            state_db = result['state'].iloc[0]
            logger.info(f"Fetching state from txn table : {state_db}")
            txn_type_db = result['txn_type'].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            amount_db = int(result['amount'].iloc[0])
            logger.info(f"Fetching amount from txn table: {amount_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.info(f"Fetching bank code from txn table: {bank_code_db}")
            bank_name_db = result['bank_name'].iloc[0]
            logger.debug(f"Fetching bank name from txn table is : {bank_name_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
            payment_mode_db = result['payment_mode'].iloc[0]
            logger.info(f"Fetching payment mode from txn table : {payment_mode_db}")
            label_ids = str(result['label_ids'].iloc[0]).strip(',')
            logger.debug(f"Fetching label ids original from txn table: {label_ids}")
            mid_db = result['mid'].iloc[0]
            logger.info(f"Fetching mid from txn table : {mid_db}")
            tid_db = result['tid'].iloc[0]
            logger.info(f"Fetching tid from txn table : {tid_db}")
            payment_gateway_db = result['payment_gateway'].iloc[0]
            logger.info(f"Fetching payment gateway from txn table : {payment_gateway_db}")
            error_msg_db = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

            query = f"select * from payment_intent where org_code = '{str(org_code)}' and " \
                    f"external_ref = '{str(order_id)}' and payment_mode='UPI'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"Fetching payment intent id is : {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"Fetching payment intent status is: {intent_status}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username,
                "password": app_password,
                "amount": refund_amount,
                "originalTransactionId": txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for payment refund api is : {response}")
            rrn_refund = response['rrNumber']
            logger.info(f"Fetching rrn from refund api response: {rrn_refund}")
            customer_name_refund = response['customerName']
            logger.info(f"Fetching customer name from refund api response: {customer_name_refund}")
            payer_name_refund = response['payerName']
            logger.info(f"Fetching payer name from refund api response: {payer_name_refund}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and " \
                    f"orig_txn_id ='{txn_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch data of refunded txn from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refund = result["id"].values[0]
            logger.info(f"Fetching refunded txn id from txn table: {txn_id_refund}")
            auth_code_refund = result['auth_code'].values[0]
            logger.info(f"Fetching refunded txn auth code from txn table: {auth_code_refund}")
            created_time_refund = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is : {created_time_refund}")
            posting_date_refund = result['posting_date'].values[0]
            logger.info(f"Fetching refunded txn posting date from txn table: {posting_date_refund}")
            rrn_db_refund = result['rr_number'].iloc[0]
            logger.info(f"Fetching refunded txn rrn from txn table: {rrn_db_refund}")
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
            customer_name_db_refund = result["customer_name"].iloc[0]
            logger.info(f"Fetching customer name from txn table: {customer_name_db_refund}")
            payer_name_db_refund = result["payer_name"].iloc[0]
            logger.info(f"Fetching payer name from txn table: {payer_name_db_refund}")
            settlement_status_db_refund = result["settlement_status"].iloc[0]
            logger.info(f"Fetching refund settlement status from txn table: {settlement_status_db_refund}")
            org_code_refund_db = result['org_code'].iloc[0]
            logger.info(f"Fetching refunded txn org code from txn table: {org_code_refund_db}")
            txn_type_db_refund = result['txn_type'].iloc[0]
            logger.info(f"Fetching refunded txn type from txn table: {txn_type_db_refund}")
            label_ids_refund = str(result['label_ids'].iloc[0]).strip(',')
            logger.info(f"Fetching refunded txn label ids from txn table: {label_ids_refund}")
            mid_db_refund = result['mid'].iloc[0]
            logger.info(f"Fetching refund mid from txn table: {mid_db_refund}")
            tid_db_refund = result['tid'].iloc[0]
            logger.info(f"Fetching refund tid from txn table: {tid_db_refund}")
            error_msg_db_refund = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db_refund}")

            logger.info(f"Execution is completed for the test case : {testcase_id}")
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
            logger.info(f"Started app validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_refund = date_time_converter.to_app_format(created_time_refund)
                formatted_amount_app = "{:,.2f}".format(amount)
                formatted_amount_app_refund = "{:,.2f}".format(refund_amount)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": formatted_amount_app,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "rrn": str(callback_rrn_number),
                    "date": date_and_time,
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_refund,
                    "txn_amt_2": formatted_amount_app_refund,
                    "customer_name_2": customer_name_refund,
                    "payer_name_2": payer_name_refund,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "rrn_2": str(rrn_refund),
                    "date_2": date_and_time_refund
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info("Performing Login")
                login_page.perform_login(app_username, app_password)
                logger.info("Waiting for Home Page to load")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.info("Going to transaction history")
                home_page.click_on_history()
                transaction_history_page = TransHistoryPage(app_driver)
                logger.info("Clicking on transaction by txn id")
                transaction_history_page.click_on_transaction_by_txn_id(txn_id)

                rrn_app = transaction_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn for the txn : {rrn_app}")
                payment_status_app = transaction_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status of txn: {payment_status_app}")
                payment_mode_app = transaction_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode for txn : {payment_mode_app}")
                order_id_app = transaction_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id for txn in app : {order_id_app}")
                txn_id_app = transaction_history_page.fetch_txn_id_text()
                logger.info(f"Fetching transaction id of txn: {txn_id_app}")
                payment_amount_app = transaction_history_page.fetch_txn_amount_text().split()[1]
                logger.info(f"Fetching transaction amount of txn : {payment_amount_app}")
                settlement_status_app = transaction_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status of txn : {settlement_status_app}")
                payment_msg_app = transaction_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message of txn : {payment_msg_app}")
                customer_name_app = transaction_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer name for txn : {customer_name_app}")
                payer_name_app = transaction_history_page.fetch_payer_name_text()
                logger.info(f"Fetching payer name for txn : {payer_name_app}")
                date_app = transaction_history_page.fetch_date_time_text()
                logger.info(f"Fetching date for txn : {date_app}")

                logger.info("Going back to transactions list page")
                transaction_history_page.click_back_Btn_transaction_details()
                logger.info("Clicking on transaction by txn id for refund")
                transaction_history_page.click_on_transaction_by_txn_id(txn_id_refund)

                rrn_refund_app = transaction_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id for the refund txn : {rrn_refund_app}")
                date_refund_app = transaction_history_page.fetch_date_time_text()
                logger.info(f"Fetching date for the refund txn : {date_refund_app}")
                payment_status_refund_app = transaction_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status of refund txn: {payment_status_refund_app}")
                payment_mode_refund_app = transaction_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode for refund txn : {payment_mode_refund_app}")
                txn_id_refund_app = transaction_history_page.fetch_txn_id_text()
                logger.info(f"Fetching transaction id for refund txn : {txn_id_refund_app}")
                amount_refund_app = transaction_history_page.fetch_txn_amount_text().split()[1]
                logger.info(f"Fetching amount for refund txn : {amount_refund_app}")
                settlement_status_refund_app = transaction_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status for refund txn : {settlement_status_refund_app}")
                payment_msg_refund_app = transaction_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message for refund txn : {payment_msg_refund_app}")
                customer_name_refund_app = transaction_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer name for refund txn : {customer_name_refund_app}")
                payer_name_refund_app = transaction_history_page.fetch_payer_name_text()
                logger.info(f"Fetching payer name for refund txn : {payer_name_refund_app}")
                order_id_refund_app = transaction_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id for refund txn : {order_id_refund_app}")

                actual_app_values = {
                    "pmt_status": payment_status_app,
                    "pmt_mode": payment_mode_app,
                    "settle_status": settlement_status_app,
                    "txn_id": txn_id_app,
                    "txn_amt": formatted_amount_app,
                    "customer_name": customer_name_app,
                    "payer_name": payer_name_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "rrn": rrn_app,
                    "date": date_app,
                    "pmt_status_2": payment_status_refund_app,
                    "pmt_mode_2": payment_mode_refund_app,
                    "settle_status_2": settlement_status_refund_app,
                    "txn_id_2": txn_id_refund_app,
                    "txn_amt_2": formatted_amount_app_refund,
                    "customer_name_2": customer_name_refund_app,
                    "payer_name_2": payer_name_refund_app,
                    "order_id_2": order_id_refund_app,
                    "pmt_msg_2": payment_msg_refund_app,
                    "rrn_2": rrn_refund_app,
                    "date_2": date_refund_app
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "amt": amount,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "rrn": str(callback_rrn_number),
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "account_label": account_label_name_1,
                    "date": date,
                    "refunded_pmt_status_2": "REFUNDED",
                    "refunded_pmt_state_2": "REFUNDED",
                    "refunded_pmt_mode_2": "UPI",
                    "refunded_settle_status_2": "SETTLED",
                    "refunded_amt_2": refund_amount,
                    "refunded_customer_name_2": customer_name_refund,
                    "refunded_payer_name_2": payer_name_refund,
                    "order_id_2": order_id,
                    "refunded_rrn_2": str(rrn_refund),
                    "refunded_acquirer_code_2": "RAZORPAY",
                    "refunded_txn_type_2": "REFUND",
                    "refunded_mid_2": mid,
                    "refunded_tid_2": tid,
                    "refunded_org_code_2": org_code,
                    "account_label_2": account_label_name_1,
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
                response_refund = [x for x in response["txns"] if x["txnId"] == txn_id_refund][0]
                logger.debug(f"Response after filtering data of current txn is : {response_refund}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.info(f"Fetching status for txn from api {status_api}")
                txn_amount_api = int(response["amount"])
                logger.info(f"Fetching amount for txn from api {txn_amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.info(f"Fetching payment mode for txn from api {payment_mode_api}")
                state_api = response["states"][0]
                logger.info(f"Fetching state for txn from api {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.info(f"Fetching settlement status for txn from api {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.info(f"Fetching issuer code for txn from api {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.info(f"Fetching acquirer code for txn from api {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.info(f"Fetching org code for txn from api {org_code_api}")
                mid_api = response["mid"]
                logger.info(f"Fetching mid for txn from api {mid_api}")
                tid_api = response["tid"]
                logger.info(f"Fetching tid for txn from api {tid_api}")
                txn_type_api = response["txnType"]
                logger.info(f"Fetching txn type for txn from api {txn_type_api}")
                rrn_api = response["rrNumber"]
                logger.info(f"Fetching rrn for txn from api {rrn_api}")
                account_label_name_api = response["accountLabel"]
                logger.info(f"Fetching account label name for txn from api {account_label_name_api}")
                customer_name_api = response['customerName']
                logger.info(f"Fetching customer name for txn from api {customer_name_api}")
                payer_name_api = response['payerName']
                logger.info(f"Fetching payer name for txn from api {payer_name_api}")
                order_id_api = response['orderNumber']
                logger.info(f"Fetching order id for txn from api {order_id_api}")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response {date_api}")

                status_api_refund = response_refund["status"]
                logger.info(f"Fetching status for refund txn from api {status_api_refund}")
                txn_amount_api_refund = int(response_refund["amount"])
                logger.info(f"Fetching amount for refund txn from api {txn_amount_api_refund}")
                payment_mode_api_refund = response_refund["paymentMode"]
                logger.info(f"Fetching payment mode for refund txn from api {payment_mode_api_refund}")
                state_api_refund = response_refund["states"][0]
                logger.info(f"Fetching state for refund txn from api {state_api_refund}")
                settlement_status_api_refund = response_refund["settlementStatus"]
                logger.info(f"Fetching settlement status for refund txn from api {settlement_status_api_refund}")
                acquirer_code_api_refund = response_refund["acquirerCode"]
                logger.info(f"Fetching acquirer code for refund txn from api {acquirer_code_api_refund}")
                org_code_api_refund = response_refund["orgCode"]
                logger.info(f"Fetching org code for refund txn from api {org_code_api_refund}")
                mid_api_refund = response_refund["mid"]
                logger.info(f"Fetching mid for refund txn from api {mid_api_refund}")
                tid_api_refund = response_refund["tid"]
                logger.info(f"Fetching tid for refund txn from api {tid_api_refund}")
                txn_type_api_refund = response_refund["txnType"]
                logger.info(f"Fetching txn type for refund txn from api {txn_type_api_refund}")
                rrn_api_refund = response_refund["rrNumber"]
                logger.info(f"Fetching rrn for refund txn from api {rrn_api_refund}")
                account_label_name_api_refund = response_refund["accountLabel"]
                logger.info(f"Fetching account label name for refund txn from api {account_label_name_api_refund}")
                customer_name_api_refund = response_refund['customerName']
                logger.info(f"Fetching customer name for refund txn from api {customer_name_api_refund}")
                payer_name_api_refund = response_refund['payerName']
                logger.info(f"Fetching payer name for refund txn from api {payer_name_api_refund}")
                order_id_api_refund = response_refund['orderNumber']
                logger.info(f"Fetching order id for refund txn from api {order_id_api_refund}")
                date_api_refund = response_refund["createdTime"]
                logger.debug(f"Fetching refund date from api response {date_api_refund}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "pmt_state": state_api,
                    "pmt_mode": payment_mode_api,
                    "settle_status": settlement_status_api,
                    "amt": txn_amount_api,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "order_id": order_id_api,
                    "rrn": rrn_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "account_label": account_label_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "refunded_pmt_status_2": status_api_refund,
                    "refunded_pmt_state_2": state_api_refund,
                    "refunded_pmt_mode_2": payment_mode_api_refund,
                    "refunded_settle_status_2": settlement_status_api_refund,
                    "refunded_amt_2": txn_amount_api_refund,
                    "refunded_customer_name_2": customer_name_api_refund,
                    "refunded_payer_name_2": payer_name_api_refund,
                    "order_id_2": order_id_api_refund,
                    "refunded_rrn_2": rrn_api_refund,
                    "refunded_acquirer_code_2": acquirer_code_api_refund,
                    "refunded_txn_type_2": txn_type_api_refund,
                    "refunded_mid_2": mid_api_refund,
                    "refunded_tid_2": tid_api_refund,
                    "refunded_org_code_2": org_code_api_refund,
                    "account_label_2": account_label_name_api_refund,
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "payer_name": payer_name,
                    "bank_name": "razorpay supported acquirers",
                    "error_msg": "None",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "rrn": str(callback_rrn_number),
                    "txn_type": "REMOTE_PAY",
                    "intent_status": "COMPLETED",
                    "mid": mid,
                    "tid": tid,
                    "acc_label_id": str(acc_label_id),
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": refund_amount,
                    "payer_name_2": payer_name_refund,
                    "error_msg_2": "None",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id_2": upi_mc_id,
                    "rrn_2": rrn_refund,
                    "txn_type_2": "REFUND",
                    "mid_2": mid,
                    "tid_2": tid,
                    "acc_label_id_2": str(acc_label_id)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.info(f"Fetching upi status from upi txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.info(f"Fetching upi txn type from upi txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.info(f"Fetching upi bank code from upi txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.info(f"Fetching upi mc id from upi txn table : {upi_mc_id_db}")
                query = f"select * from upi_txn where txn_id='{txn_id_refund}'"
                logger.debug(f"Query to fetch refund txn data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refund = result["status"].iloc[0]
                logger.info(f"Fetching refund upi status from upi txn table : {upi_status_db_refund}")
                upi_txn_type_db_refund = result["txn_type"].iloc[0]
                logger.info(f"Fetching refund upi txn type from upi txn table : {upi_txn_type_db_refund}")
                upi_bank_code_db_refund = result["bank_code"].iloc[0]
                logger.info(f"Fetching refund upi bank code from upi txn table : {upi_bank_code_db_refund}")
                upi_mc_id_db_refund = result["upi_mc_id"].iloc[0]
                logger.info(f"Fetching refund upi mc id from upi txn table : {upi_mc_id_db_refund}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "payer_name": payer_name,
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
                    "intent_status": intent_status,
                    "mid": mid_db,
                    "tid": tid_db,
                    "acc_label_id": str(label_ids),
                    "pmt_status_2": status_db_refund,
                    "pmt_state_2": state_db_refund,
                    "pmt_mode_2": payment_mode_db_refund,
                    "txn_amt_2": amount_db_refund,
                    "payer_name_2": payer_name_db_refund,
                    "error_msg_2": error_msg_db_refund,
                    "settle_status_2": settlement_status_db_refund,
                    "acquirer_code_2": acquirer_code_db_refund,
                    "pmt_gateway_2": payment_gateway_db_refund,
                    "upi_txn_status_2": upi_status_db_refund,
                    "upi_txn_type_2": upi_txn_type_db_refund,
                    "upi_bank_code_2": upi_bank_code_db_refund,
                    "upi_mc_id_2": upi_mc_id_db_refund,
                    "rrn_2": str(rrn_db_refund),
                    "txn_type_2": txn_type_db_refund,
                    "mid_2": mid_db_refund,
                    "tid_2": tid_db_refund,
                    "acc_label_id_2": str(label_ids_refund)
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-----------------------------------------

        # -----------------------------------------Start of Portal Validation-----------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started portal validation for the test case : {testcase_id}")
            try:
                date_portal_1 = date_time_converter.to_portal_format(created_time)
                date_portal_2 = date_time_converter.to_portal_format(created_time_refund)
                formatted_amount_portal = "{:,.2f}".format(amount)
                formatted_amount_portal_refund = "{:,.2f}".format(refund_amount)
                expected_portal_values = {
                    "date_time": date_portal_1,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": formatted_amount_portal,
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": str(callback_rrn_number),
                    "acc_label": account_label_name_1,
                    "date_time_2": date_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": formatted_amount_portal_refund,
                    "username_2": app_username,
                    "txn_id_2": txn_id_refund,
                    "rrn_2": str(rrn_refund),
                    "acc_label_2": account_label_name_1
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_portal = transaction_details[1]['Date & Time']
                logger.info(f"Fetching date from portal : {date_portal}")
                txn_id_portal = transaction_details[1]['Transaction ID']
                logger.info(f"Fetching txn id from portal : {txn_id_portal}")
                txn_amount_portal = transaction_details[1]['Total Amount'].split()
                logger.info(f"Fetching txn amount from portal : {txn_amount_portal}")
                auth_code_portal = transaction_details[1]['Auth Code']
                logger.info(f"Fetching auth code from portal : {auth_code_portal}")
                rrn_portal = transaction_details[1]['RR Number']
                logger.info(f"Fetching rrn from portal : {rrn_portal}")
                txn_type_portal = transaction_details[1]['Type']
                logger.info(f"Fetching txn type from portal : {txn_type_portal}")
                status_portal = transaction_details[1]['Status']
                logger.info(f"Fetching status from portal : {status_portal}")
                username_portal = transaction_details[1]['Username']
                logger.info(f"Fetching username from portal : {username_portal}")
                labels_portal = transaction_details[1]['Labels']
                logger.info(f"Fetching labels from portal : {labels_portal}")

                date_portal_refund = transaction_details[0]['Date & Time']
                logger.info(f"Fetching refund txn date from portal : {date_portal_refund}")
                txn_id_portal_refund = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching refund txn id from portal : {txn_id_portal_refund}")
                txn_amount_portal_refund = transaction_details[0]['Total Amount'].split()
                logger.info(f"Fetching refund txn amount from portal : {txn_amount_portal_refund}")
                auth_code_portal_refund = transaction_details[0]['Auth Code']
                logger.info(f"Fetching refund txn auth code from portal : {auth_code_portal_refund}")
                rrn_portal_refund = transaction_details[0]['RR Number']
                logger.info(f"Fetching refund txn rrn from portal : {rrn_portal_refund}")
                txn_type_portal_refund = transaction_details[0]['Type']
                logger.info(f"Fetching refund txn type from portal : {txn_type_portal_refund}")
                status_portal_refund = transaction_details[0]['Status']
                logger.info(f"Fetching refund txn status from portal : {status_portal_refund}")
                username_portal_refund = transaction_details[0]['Username']
                logger.info(f"Fetching refund txn username from portal : {username_portal_refund}")
                labels_portal_refund = transaction_details[0]['Labels']
                logger.info(f"Fetching refund txn labels from portal : {labels_portal_refund}")

                actual_portal_values = {
                    "date_time": date_portal,
                    "pmt_state": str(status_portal),
                    "pmt_type": txn_type_portal,
                    "txn_amt": txn_amount_portal[1],
                    "username": username_portal,
                    "txn_id": txn_id_portal,
                    "rrn": rrn_portal,
                    "acc_label": labels_portal,
                    "date_time_2": date_portal_refund,
                    "pmt_state_2": str(status_portal_refund),
                    "pmt_type_2": txn_type_portal_refund,
                    "txn_amt_2": txn_amount_portal_refund[1],
                    "username_2": username_portal_refund,
                    "txn_id_2": txn_id_portal_refund,
                    "rrn_2": rrn_portal_refund,
                    "acc_label_2": labels_portal_refund
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
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
                    formatted_amount_charge_slip_refund = 'Rs.' + "{:,.2f}".format(refund_amount)
                    txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_refund)
                    expected_charge_slip_values = {
                        'PAID BY:': 'UPI',
                        'merchant_ref_no': 'Ref # ' + str(order_id),
                        'RRN': str(rrn_refund),
                        'BASE AMOUNT:': formatted_amount_charge_slip_refund,
                        'date': txn_date,
                        'time': txn_time,
                        'AUTH CODE': '' if auth_code_refund != "None" else auth_code_refund
                    }

                    logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                    receipt_validator.perform_charge_slip_validations(txn_id_refund, {"username": app_username,
                                                                                      "password": app_password},
                                                                      expected_charge_slip_values)

                except Exception as e:
                    Configuration.perform_charge_slip_val_exception(testcase_id, e)
                logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
            # -----------------------------------------End of ChargeSlip Validation------------------------------------

            GlobalVariables.time_calc.validation.end()
            logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
            logger.info(f"Completed Validation for the test case : {testcase_id}")
            # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
