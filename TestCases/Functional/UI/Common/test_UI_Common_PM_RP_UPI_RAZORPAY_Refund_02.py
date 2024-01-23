import random
import sys
import pytest
import time
from datetime import datetime
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from PageFactory.portal_remotePayPage import RemotePayTxnPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter, receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_266():
    """
    Sub Feature Code: UI_Common_PM_RP_Pure_upi_collect_two_times_partial_refund_RAZORPAY
    Sub Feature Description: Verification of a remote pay upi collect successful partial refund when refunded two times.
    Sub Feature Description: Verification of a remote pay successful partial refund when refunded two times.
    TC naming code description: 100: Payment Method, 103: RemotePay, 266: TC266
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
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(
            f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Query result, pgMerchantId : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id: {upi_mc_id}")
        upi_account_id = result['pgMerchantId'].values[0]
        logger.debug(f"upi account id from db is : {upi_account_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Query result, tid: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Query result, mid: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 3004
            logger.info(f"amount is : {amount}")
            partial_refunded_amount = 1502
            logger.info(f"partial_refund_amount is : {partial_refunded_amount}")
            full_refund_amount = 1502
            logger.info(f"full_refund_amount is : {full_refund_amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
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
            time.sleep(5)

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}'"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {original_txn_id} ")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching original_customer_name from db query : {original_customer_name} ")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching original_payer_name from db query : {original_payer_name} ")
            original_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching original_auth_code from db query : {original_auth_code} ")
            original_org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching original_org_code_txn from db query : {original_org_code_txn} ")
            original_rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching original_rrn from db query : {original_rrn} ")
            original_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching original_txn_type from db query : {original_txn_type} ")
            created_time_original = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_original from db query : {created_time_original} ")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": partial_refunded_amount,
                                                                    "originalTransactionId": str(original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id ='{str(original_txn_id)}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            partially_refunded_txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching partially_refunded_txn_id from db query : {partially_refunded_txn_id} ")
            partially_refunded_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching partially_refunded_auth_code from db query : {partially_refunded_auth_code} ")
            partially_refunded_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching partially_refunded_txn_type from db query : {partially_refunded_txn_type} ")
            partially_refunded_rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching partially_refunded_rrn from db query : {partially_refunded_rrn} ")
            partially_refunded_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching partially_refunded_posting_date from db query: {partially_refunded_posting_date} ")
            created_time_partially_refunded = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_partially_refunded from db query: {created_time_partially_refunded} ")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": full_refund_amount,
                                                                    "originalTransactionId": str(original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(
                f"Response received from refund api when refund amount is greater than original amount : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id ='{str(original_txn_id)}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of fully refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            fully_refunded_txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching fully_refunded_txn_id from db query : {fully_refunded_txn_id} ")
            fully_refunded_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching fully_refunded_auth_code from db query : {fully_refunded_auth_code} ")
            fully_refunded_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching fully_refunded_txn_type from db query : {fully_refunded_txn_type} ")
            fully_refunded_rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching fully_refunded_rrn from db query : {fully_refunded_rrn} ")
            fully_refunded_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching fully_refunded_posting_date from db query: {fully_refunded_posting_date} ")
            created_time_fully_refunded = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_fully_refunded from db query: {created_time_fully_refunded} ")

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
                date_and_time = date_time_converter.to_app_format(partially_refunded_posting_date)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED_REFUNDED",
                    "refund_pmt_status": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "refund_pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "refund_settle_status": "SETTLED",
                    "txn_id": original_txn_id,
                    "refund_txn_id": partially_refunded_txn_id,
                    "txn_amt": f"{amount:,}.00",
                    "txn_amt_2": f"{partial_refunded_amount:,}.00",
                    "customer_name": original_customer_name,
                    "refund_customer_name": original_customer_name,
                    "payer_name": original_payer_name,
                    "refund_payer_name": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "refund_pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(original_rrn),
                    "refund_rrn": str(partially_refunded_rrn),
                    "date": date_and_time,
                    "full_refund_pmt_status": "STATUS:REFUNDED",
                    "full_refund_pmt_mode": "UPI",
                    "full_refund_settle_status": "SETTLED",
                    "full_refund_txn_id": fully_refunded_txn_id,
                    "txn_amt_3": str(full_refund_amount),
                    "full_refund_customer_name": original_customer_name,
                    "full_refund_payer_name": original_payer_name,
                    "full_refund_pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "full_refund_rrn": str(fully_refunded_rrn),
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
                transactions_history_page.click_on_transaction_by_txn_id(partially_refunded_txn_id)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the refund txn : {app_rrn_refunded}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the refund txn : {app_date_and_time}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of refund txn from transaction history of MPOS app: {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching status msg of refund txn from transaction history of MPOS app: {payment_msg_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn :{app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching status msg of original txn from transaction history of MPOS app: {payment_msg_original}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(fully_refunded_txn_id)

                fully_refunded_app_rrn = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn: {fully_refunded_app_rrn}")
                fully_refunded_app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: {fully_refunded_app_payment_status}")
                fully_refunded_app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: {fully_refunded_app_payment_mode}")
                fully_refunded_app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: {fully_refunded_app_txn_id}")
                fully_refunded_app_payment_amt = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: {fully_refunded_app_payment_amt}")
                fully_refunded_app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: {fully_refunded_app_settlement_status}")
                fully_refunded_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching status msg of original txn from transaction history of MPOS app: {fully_refunded_payment_msg}")
                fully_refunded_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn: {fully_refunded_customer_name}")

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
                    "customer_name": original_customer_name,
                    "refund_customer_name": original_customer_name,
                    "payer_name": original_payer_name,
                    "refund_payer_name": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "refund_pmt_msg": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "refund_rrn": str(app_rrn_refunded),
                    "date": app_date_and_time,
                    "full_refund_pmt_status": fully_refunded_app_payment_status,
                    "full_refund_pmt_mode": fully_refunded_app_payment_mode,
                    "full_refund_settle_status": fully_refunded_app_settlement_status,
                    "full_refund_txn_id": fully_refunded_app_txn_id,
                    "txn_amt_3": str(full_refund_amount),
                    "full_refund_customer_name": fully_refunded_customer_name,
                    "full_refund_payer_name": original_payer_name,
                    "full_refund_pmt_msg": fully_refunded_payment_msg,
                    "full_refund_rrn": str(fully_refunded_app_rrn),
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
                date = date_time_converter.db_datetime(partially_refunded_posting_date)
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
                    "refunded_amt": str(partial_refunded_amount),
                    "original_customer_name": original_customer_name,
                    "refunded_customer_name": original_customer_name,
                    "original_payer_name": original_payer_name,
                    "refunded_payer_name": original_payer_name,
                    "original_order_id": order_id,
                    "original_rrn": str(original_rrn),
                    "refunded_rrn": str(partially_refunded_rrn),
                    "original_acquirer_code": "RAZORPAY",
                    "original_issuer_code": "RAZORPAY",
                    "original_txn_type": original_txn_type,
                    "original_mid": mid,
                    "original_tid": tid,
                    "original_org_code": original_org_code_txn,
                    "refunded_acquirer_code": "RAZORPAY",
                    "refunded_txn_type": partially_refunded_txn_type,
                    "refunded_mid": mid,
                    "refunded_tid": tid,
                    "refunded_org_code": original_org_code_txn,
                    "date": date,
                    "fully_refunded_pmt_status": "REFUNDED",
                    "fully_refunded_pmt_state": "REFUNDED",
                    "fully_refunded_pmt_mode": "UPI",
                    "fully_refunded_settle_status": "SETTLED",
                    "fully_refunded_amt": str(full_refund_amount),
                    "fully_refunded_customer_name": original_customer_name,
                    "fully_refunded_payer_name": original_payer_name,
                    "fully_refunded_rrn": str(fully_refunded_rrn),
                    "fully_refunded_acquirer_code": "RAZORPAY",
                    "fully_refunded_txn_type": fully_refunded_txn_type,
                    "fully_refunded_mid": mid,
                    "fully_refunded_tid": tid,
                    "fully_refunded_org_code": original_org_code_txn,

                }
                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")
                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status received for transaction details api is : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"Amount received for transaction details api is : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"Payment mode received for transaction details api is : {payment_mode_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"Settlement status received for transaction details api is :{settlement_status_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"Acquirer code received for transaction details api is : {acquirer_code_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code from api response for original txn is: {issuer_code_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"Txn Type received for transaction details api is : {txn_type_api_original}")
                rrn_api_original = response['rrNumber']
                logger.debug(f"rrn api original : {rrn_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state from api response for original txn is: {state_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code from api response for original txn is: {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid from api response for original txn is: {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid from api response for original txn is: {tid_api_original}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == partially_refunded_txn_id][0]
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status received for refund txn from api response is : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount received for refund txn from api response is : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode for refund txn from api response is : {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn received for refund txn from api response is : {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state received for refund txn from api response is : {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status received for refund txn from api response is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code received for refund txn from api response is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code received for refund txn from api response is : {org_code_api_refunded}")
                mid_api_refunded = response["mid"]
                logger.debug(f"mid received for refund txn from api response is : {mid_api_refunded}")
                tid_api_refunded = response["tid"]
                logger.debug(f"tid received for refund txn from api response is : {tid_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type received for refund txn from api response is : {txn_type_api_refunded}")
                date_api_refunded = response["postingDate"]
                logger.debug(f"date received for refund txn from api response is : {date_api_refunded}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == fully_refunded_txn_id][0]
                logger.debug(f"Response received for transaction details api is : {response}")
                api_status_full_refund = response["status"]
                logger.debug(f"status received for full refund txn from api response is : {api_status_full_refund}")
                api_payment_mode_full_refund = response["paymentMode"]
                logger.debug(f"payment_mode received for full refund txn from api response is : {api_payment_mode_full_refund}")
                api_state_full_refund = response["states"][0]
                logger.debug(f"state received for full refund txn from api response is : {api_state_full_refund}")
                api_settlement_status_full_refund = response["settlementStatus"]
                logger.debug(f"settlement status received for full refund txn from api response is : {api_settlement_status_full_refund}")
                api_acquirer_code_full_refund = response["acquirerCode"]
                logger.debug(f"acquirer_code received for full refund txn from api response is : {api_acquirer_code_full_refund}")
                api_org_code_full_refund = response["orgCode"]
                logger.debug(f"org_code received for full refund txn from api response is : {api_org_code_full_refund}")
                api_mid_full_refund = response["mid"]
                logger.debug(f"mid received for full refund txn from api response is : {api_mid_full_refund}")
                api_tid_full_refund = response["tid"]
                logger.debug(f"tid received for full refund txn from api response is : {api_tid_full_refund}")
                api_txn_type_full_refund = response["txnType"]
                logger.debug(f"txn type received for full refund txn from api response is : {api_txn_type_full_refund}")
                api_customer_name_full_refund = response["customerName"]
                logger.debug(f"customer name received for full refund txn from api response is : {api_customer_name_full_refund}")
                api_payer_name_full_refund = response["payerName"]
                logger.debug(f"payer name received for full refund txn from api response is : {api_payer_name_full_refund}")

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
                    "original_customer_name": original_customer_name,
                    "refunded_customer_name": original_customer_name,
                    "original_payer_name": original_payer_name,
                    "refunded_payer_name": original_payer_name,
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
                    "fully_refunded_pmt_status": api_status_full_refund,
                    "fully_refunded_pmt_state": api_state_full_refund,
                    "fully_refunded_pmt_mode": api_payment_mode_full_refund,
                    "fully_refunded_settle_status": api_settlement_status_full_refund,
                    "fully_refunded_amt": str(full_refund_amount),
                    "fully_refunded_customer_name": api_customer_name_full_refund,
                    "fully_refunded_payer_name": api_payer_name_full_refund,
                    "fully_refunded_rrn": str(fully_refunded_rrn),
                    "fully_refunded_acquirer_code": api_acquirer_code_full_refund,
                    "fully_refunded_txn_type": api_txn_type_full_refund,
                    "fully_refunded_mid": api_mid_full_refund,
                    "fully_refunded_tid": api_tid_full_refund,
                    "fully_refunded_org_code": api_org_code_full_refund,
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
                    "refunded_amt": partial_refunded_amount,
                    "original_upi_txn_status": "AUTHORIZED_REFUNDED",
                    "refunded_upi_txn_status": "REFUNDED",
                    "original_settle_status": "SETTLED",
                    "refunded_settle_status": "SETTLED",
                    "original_acquirer_code": "RAZORPAY",
                    "refunded_acquirer_code": "RAZORPAY",
                    "original_bank_code": "RAZORPAY",
                    "bank_code_refunded": "RAZORPAY_PSP",
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
                    "pmt_gateway": "RAZORPAY",
                    "refunded_pmt_gateway": "RAZORPAY",
                    "fully_refunded_pmt_status": "REFUNDED",
                    "fully_refunded_pmt_state": "REFUNDED",
                    "fully_refunded_pmt_mode": "UPI",
                    "fully_refunded_amt": full_refund_amount,
                    "fully_refunded_upi_txn_status": "REFUND",
                    "fully_refunded_settle_status": "SETTLED",
                    "fully_refunded_acquirer_code": "RAZORPAY",
                    "fully_refunded_upi_txn_type": "REFUND",
                    "fully_refunded_upi_bank_code": "RAZORPAY_PSP",
                    "fully_refunded_upi_mc_id": upi_mc_id,
                    "fully_refund_mid": mid,
                    "fully_refund_tid": tid,
                    "fully_refund_pmt_gateway": "RAZORPAY"
                }
                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = f"select * from txn where id='{partially_refunded_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_refunded} ")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_refunded} ")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_refunded} ")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_refunded} ")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_refunded} ")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_refunded} ")
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching payment_gateway from DB : {payment_gateway_db_refunded} ")
                tid_db_refunded = result['tid'].values[0]
                logger.debug(f"Fetching tid from DB : {tid_db_refunded} ")
                mid_db_refunded = result['mid'].values[0]
                logger.debug(f"Fetching mid from DB : {mid_db_refunded} ")

                query = f"select * from upi_txn where txn_id='{partially_refunded_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_refunded}")
                bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"fetched bank_code from upi_txn table is : {bank_code_db_refunded}")

                query = f"select * from txn where id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_original} ")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {acquirer_code_db_original} ")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code from DB : {bank_code_db_original} ")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_original} ")
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching payment_gateway from DB : {payment_gateway_db_original} ")
                tid_db_original = result['tid'].values[0]
                logger.debug(f"Fetching tid from DB : {tid_db_original} ")
                mid_db_original = result['mid'].values[0]
                logger.debug(f"Fetching mid from DB : {mid_db_original} ")

                query = f"select * from upi_txn where txn_id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_original}")

                query = f"select * from txn where id='{fully_refunded_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_full_refund = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_full_refund} ")
                payment_mode_db_full_refund = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_full_refund} ")
                amount_db_full_refund = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_full_refund} ")
                state_db_full_refund = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_full_refund} ")
                acquirer_code_db_full_refund = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {acquirer_code_db_full_refund} ")
                settlement_status_db_full_refund = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_full_refund} ")
                payment_gateway_db_full_refunded = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching payment_gateway from DB : {payment_gateway_db_full_refunded} ")
                tid_db_full_refund = result['tid'].values[0]
                logger.debug(f"Fetching tid from DB : {tid_db_full_refund} ")
                mid_db_full_refund = result['mid'].values[0]
                logger.debug(f"Fetching mid from DB : {mid_db_full_refund} ")

                query = f"select * from upi_txn where txn_id='{fully_refunded_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_txn_type_db_full_refund = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_full_refund}")
                bank_code_db_full_refund = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {bank_code_db_full_refund}")
                upi_mc_id_db_full_refund = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_full_refund}")

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
                    "bank_code_refunded": bank_code_db_refunded,
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
                    "pmt_gateway": payment_gateway_db_original,
                    "refunded_pmt_gateway": payment_gateway_db_refunded,
                    "fully_refunded_pmt_status": status_db_full_refund,
                    "fully_refunded_pmt_state": state_db_full_refund,
                    "fully_refunded_pmt_mode": payment_mode_db_full_refund,
                    "fully_refunded_amt": amount_db_full_refund,
                    "fully_refunded_upi_txn_status": upi_txn_type_db_full_refund,
                    "fully_refunded_settle_status": settlement_status_db_full_refund,
                    "fully_refunded_acquirer_code": acquirer_code_db_full_refund,
                    "fully_refunded_upi_txn_type": upi_txn_type_db_full_refund,
                    "fully_refunded_upi_bank_code": bank_code_db_full_refund,
                    "fully_refunded_upi_mc_id": upi_mc_id_db_full_refund,
                    "fully_refund_mid": mid_db_full_refund,
                    "fully_refund_tid": tid_db_full_refund,
                    "fully_refund_pmt_gateway": payment_gateway_db_full_refunded,
                }
                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_original = date_time_converter.to_portal_format(created_time_original)
                date_and_time_partially_refunded = date_time_converter.to_portal_format(created_time_partially_refunded)
                date_and_time_fully_refunded = date_time_converter.to_portal_format(created_time_fully_refunded)

                expected_portal_values = {
                    "date_time": date_and_time_original,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{amount:,}.00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "rrn": str(original_rrn),

                    "date_time_2": date_and_time_partially_refunded,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{partial_refunded_amount:,}.00",
                    "username_2": app_username,
                    "txn_id_2": partially_refunded_txn_id,
                    "rrn_2": str(partially_refunded_rrn),

                    "date_time_3": date_and_time_fully_refunded,
                    "pmt_state_3": "REFUNDED",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": f"{full_refund_amount:,}.00",
                    "username_3": app_username,
                    "txn_id_3": fully_refunded_txn_id,
                    "rrn_3": str(fully_refunded_rrn),
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_fully_refunded = transaction_details[0]['Date & Time']
                logger.debug(f"date_time for full refund txn from portal is: {date_time_fully_refunded}")
                transaction_id_fully_refunded = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id for full refund txn from portal is: {transaction_id_fully_refunded}")
                total_amount_fully_refunded = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount for full refund txn from portal is: {total_amount_fully_refunded}")
                rr_number_fully_refunded = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code for full refund txn from portal is: {rr_number_fully_refunded}")
                rr_number_full_refund_portal = transaction_details[0]['RR Number']
                logger.debug(f"rr_number for full refund txn from portal is: {rr_number_full_refund_portal}")
                transaction_type_fully_refunded = transaction_details[0]['Type']
                logger.debug(f"transaction_type for full refund txn from portal is: {transaction_type_fully_refunded}")
                status_fully_refunded = transaction_details[0]['Status']
                logger.debug(f"status for full refund txn from portal is: {status_fully_refunded}")
                username_fully_refunded = transaction_details[0]['Username']
                logger.debug(f"username for full refund txn from portal is: {username_fully_refunded}")

                date_time_refunded = transaction_details[1]['Date & Time']
                logger.debug(f"date_time for refund txn from portal is: {date_time_refunded}")
                transaction_id_refunded = transaction_details[1]['Transaction ID']
                logger.debug(f"transaction_id for refund txn from portal is: {transaction_id_refunded}")
                total_amount_refunded = transaction_details[1]['Total Amount'].split()
                logger.debug(f"total_amount for refund txn from portal is: {total_amount_refunded}")
                rr_number_refunded = transaction_details[1]['RR Number']
                logger.debug(f"rr_number for refund txn from portal is: {rr_number_refunded}")
                transaction_type_refunded = transaction_details[1]['Type']
                logger.debug(f"transaction_type for refund txn from portal is: {transaction_type_refunded}")
                status_refunded = transaction_details[1]['Status']
                logger.debug(f"status for refund txn from portal is: {status_refunded}")
                username_refunded = transaction_details[1]['Username']
                logger.debug(f"username for refund txn from portal is: {username_refunded}")

                original_date_time = transaction_details[2]['Date & Time']
                logger.debug(f"date_time from portal is: {original_date_time}")
                original_transaction_id = transaction_details[2]['Transaction ID']
                logger.debug(f"txn_id from portal is: {original_transaction_id}")
                original_total_amount = transaction_details[2]['Total Amount'].split()
                logger.debug(f"amount from portal is: {original_total_amount}")
                original_rr_number = transaction_details[2]['RR Number']
                logger.debug(f"rr_number from portal is: {original_rr_number}")
                original_transaction_type = transaction_details[2]['Type']
                logger.debug(f"transaction_type from portal is: {original_transaction_type}")
                original_status = transaction_details[2]['Status']
                logger.debug(f"status from portal is: {original_status}")
                original_username = transaction_details[2]['Username']
                logger.debug(f"username from portal is: {original_username}")

                actual_portal_values = {
                    "date_time": original_date_time,
                    "pmt_state": str(original_status),
                    "pmt_type": original_transaction_type,
                    "txn_amt": original_total_amount[1],
                    "username": original_username,
                    "txn_id": original_transaction_id,
                    "rrn": original_rr_number,

                    "date_time_2": date_time_refunded,
                    "pmt_state_2": str(status_refunded),
                    "pmt_type_2": transaction_type_refunded,
                    "txn_amt_2": total_amount_refunded[1],
                    "username_2": username_refunded,
                    "txn_id_2": transaction_id_refunded,
                    "rrn_2": rr_number_refunded,

                    "date_time_3": date_time_fully_refunded,
                    "pmt_state_3": str(status_fully_refunded),
                    "pmt_type_3": transaction_type_fully_refunded,
                    "txn_amt_3": total_amount_fully_refunded[1],
                    "username_3": username_fully_refunded,
                    "txn_id_3": transaction_id_fully_refunded,
                    "rrn_3": rr_number_fully_refunded,
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(partially_refunded_posting_date)
                expected_charge_slip_values = {'PAID BY:': 'UPI',
                                               'merchant_ref_no': 'Ref # ' + str(order_id),
                                               'RRN': str(partially_refunded_rrn),
                                               'BASE AMOUNT:': f"Rs.{partial_refunded_amount:,}.00",
                                               'date': txn_date,
                                               'time': txn_time,
                                               }
                logger.debug(
                    f"expected_charge_slip_values : {expected_charge_slip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(partially_refunded_txn_id,
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
def test_common_100_103_221():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Refund_By_API_Razorpay
    Sub Feature Description: Verification of a Remote Pay refund using api for Razorpay
    TC naming code description:
    100: Payment Method, 103: RemotePay, 221: TC221
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                "bank_code = 'RAZORPAY_PSP' and card_terminal_acquirer_code = 'NONE'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"upi merchant id from txn db : {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize(browser_type='firefox')
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

            amount = random.randint(2030, 3000)
            logger.info(f"amount is :{amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is :{order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = RemotePayTxnPage(ui_browser)
            logger.info("Clicking on UPI to start the txn.")
            rp_upi_txn.clickOnRemotePayUPI()
            logger.info("Launching UPI")
            rp_upi_txn.clickOnRemotePayLaunchUPI()
            rp_upi_txn.clickOnRemotePayCancelUPI()
            rp_upi_txn.clickOnRemotePayProceed()
            logger.info("UPI txn is completed.")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}'"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {created_time}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"acquirer_code_db from db : {acquirer_code_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"amount_db from db : {amount_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"bank_code_db from db : {bank_code_db}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"customer_name from db : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"payer_name from db : {payer_name}")
            external_ref_db = result['external_ref'].values[0]
            logger.debug(f"external_ref_db from db : {external_ref_db}")
            issuer_code_db = result['issuer_code'].values[0]
            logger.debug(f"issuer_code from db : {issuer_code_db}")
            mid = result['mid'].values[0]
            logger.debug(f"mid from db : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"tid from db : {tid}")
            org_code_db = result['org_code'].values[0]
            logger.debug(f"org_code_txn from db : {org_code_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway_db from db : {payment_gateway_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"payment_mode_db from db : {payment_mode_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"rrn_db from db : {rrn_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"settlement_status_db from db : {settlement_status_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"status_db from db : {status_db}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"txn_type from db : {txn_type}")
            state_db = result["state"].iloc[0]
            logger.debug(f"state_db from db : {state_db}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"txn_auth_code from db : {txn_auth_code}")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and " \
                    f"orig_txn_id ='{txn_id}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id_refunded from txn table is: {txn_id_refunded}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table is: {refund_auth_code}")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table is: {txn_type_refunded}")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn from txn table is: {rrn_refunded}")
            posting_date = result['created_time'].values[0]
            logger.debug(f"Fetching posting_date from txn table is: {posting_date}")
            created_time_refunded = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is: {created_time_refunded}")

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
                original_date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED_REFUNDED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(rrn_db),
                    "date": original_date_and_time,
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_refunded,
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "rrn_2": str(rrn_refunded),
                    "date_2": date_and_time,
                }
                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the refund txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the refund txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"payment_status_refunded from app txn details :{app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"payment_mode_refunded from app txn details :{app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"txn_id_refunded from app txn details : {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"payment_amt_refunded from app txn details : {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"settlement_status_refunded from app txn details : {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"payment_msg_refunded from app txn details : {payment_msg_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"rrn_original from app txn details :{app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"payment_status_original from app txn details : {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"payment_mode_original from app txn details :{app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"txn_id_original from app txn details : {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"payment_amt_original from app txn details : {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"settlement_status_original from app txn details : {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"payment_msg_original from app txn details : {payment_msg_original}")
                app_original_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"original_date_and_time from app txn details :{app_original_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_mode": app_payment_mode_original,
                    "settle_status": app_settlement_status_original,
                    "txn_id": app_txn_id_original,
                    "txn_amt": str(app_payment_amt_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "rrn": str(app_rrn_original),
                    "date": app_original_date_and_time,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn_2": str(app_rrn_refunded),
                    "date_2": app_date_and_time
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
                refunded_date_time = date_time_converter.db_datetime(posting_date)
                original_date_time = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "txn_amt": str(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_db),
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "SETTLED",
                    "txn_amt_2": str(amount),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": txn_type_refunded,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": refunded_date_time,
                    "date": original_date_time
                }
                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status received for transaction details api is : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"Amount received for transaction details api is : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"Payment mode received for transaction details api is : {payment_mode_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"Settlement status received for transaction details api is :{settlement_status_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"Acquirer code received for transaction details api is : {acquirer_code_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code from api response for original txn is: {issuer_code_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"Txn Type received for transaction details api is : {txn_type_api_original}")
                date_api_original = response["postingDate"]
                logger.debug(f"Date received for transaction details api is : {date_api_original}")
                rrn_api_original = response['rrNumber']
                logger.debug(f"rrn api original : {rrn_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state from api response for original txn is: {state_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code from api response for original txn is: {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid from api response for original txn is: {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid from api response for original txn is: {tid_api_original}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id_refunded})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status received for refund txn from api response is : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount received for refund txn from api response is : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode for refund txn from api response is : {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn received for refund txn from api response is : {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state received for refund txn from api response is : {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status received for refund txn from api response is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code received for refund txn from api response is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code received for refund txn from api response is : {org_code_api_refunded}")
                mid_api_refunded = response["mid"]
                logger.debug(f"mid received for refund txn from api response is : {mid_api_refunded}")
                tid_api_refunded = response["tid"]
                logger.debug(f"tid received for refund txn from api response is : {tid_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type received for refund txn from api response is : {txn_type_api_refunded}")
                date_api_refunded = response["postingDate"]
                logger.debug(f"date received for refund txn from api response is : {date_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_state": state_api_original,
                    "pmt_mode": payment_mode_api_original,
                    "settle_status": settlement_status_api_original,
                    "txn_amt": str(amount_api_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
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
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id
                }
                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = f"select * from txn where id='{txn_id_refunded}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_refunded} ")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_refunded} ")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_refunded} ")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_refunded} ")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {state_db_refunded} ")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_refunded} ")

                query = f"select * from upi_txn where txn_id='{txn_id_refunded}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_refunded}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_original} ")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {acquirer_code_db_original} ")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code from DB : {bank_code_db_original} ")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_original} ")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_original}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_state": state_db_original,
                    "pmt_mode": payment_mode_db_original,
                    "txn_amt": amount_db_original,
                    "upi_txn_status": upi_status_db_original,
                    "settle_status": settlement_status_db_original,
                    "acquirer_code": acquirer_code_db_original,
                    "bank_code": bank_code_db_original,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_mc_id": upi_mc_id_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                }
                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_refunded = date_time_converter.to_portal_format(created_time_refunded)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn_number": rrn_db,
                    "auth_code": "-" if txn_auth_code is None else txn_auth_code,
                    "date_time_2": date_and_time_portal_refunded,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "rrn_number_2": rrn_refunded,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time for refund txn from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id for refund txn from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount for refund txn from portal is: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code for refund txn from portal is: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number for refund txn from portal is: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type for refund txn from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status for refund txn from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username for refund txn from portal is: {username}")

                date_time_original = transaction_details[1]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time_original}")
                transaction_id_original = transaction_details[1]['Transaction ID']
                logger.debug(f"txn_id from portal is: {transaction_id_original}")
                total_amount_original = transaction_details[1]['Total Amount'].split()
                logger.debug(f"amount from portal is: {total_amount_original}")
                auth_code_original = transaction_details[1]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code_original}")
                rr_number_original = transaction_details[1]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number_original}")
                transaction_type_original = transaction_details[1]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type_original}")
                status_original = transaction_details[1]['Status']
                logger.debug(f"status from portal is: {status_original}")
                username_original = transaction_details[1]['Username']
                logger.debug(f"username from portal is: {username_original}")

                actual_portal_values = {
                    "date_time": date_time_original,
                    "pmt_state": str(status_original),
                    "pmt_type": transaction_type_original,
                    "txn_amt": total_amount_original[1],
                    "username": username_original,
                    "txn_id": transaction_id_original,
                    "rrn_number": rr_number_original,
                    "auth_code": auth_code_original,
                    "date_time_2": date_time,
                    "pmt_state_2": str(status),
                    "pmt_type_2": transaction_type,
                    "txn_amt_2": total_amount[1],
                    "username_2": username,
                    "txn_id_2": transaction_id,
                    "rrn_number_2": rr_number,
                    "auth_code_2": auth_code
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ------------------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation-----------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_charge_slip_values = {'PAID BY:': 'UPI',
                                               'merchant_ref_no': 'Ref # ' + str(order_id),
                                               'RRN': str(rrn_refunded),
                                               'BASE AMOUNT:': f"Rs.{amount:,}.00",
                                               'date': txn_date,
                                               'time': txn_time,
                                               'AUTH CODE': "" if refund_auth_code is None else refund_auth_code}
                logger.debug(
                    f"expected_charge_slip_values : {expected_charge_slip_values} for the testcase_id {testcase_id}")
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
def test_common_100_103_222():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Refund_Failed_Razorpay
    Sub Feature Description: Verification of a Remote Pay upi refund failed via Razorpay
    TC naming code description: 100: Payment Method, 103: RemotePay, 222: TC222
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'RAZORPAY_PSP' and card_terminal_acquirer_code = 'NONE'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"Fetched upi_mc_id is {upi_mc_id}")
        upi_account_id = result['pgMerchantId'].values[0]
        logger.info(f"Fetched upi_account_id is {upi_account_id}")

        TestSuiteSetup.launch_browser_and_context_initialize(browser_type='firefox')
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        msg = ''
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1401, 1499)
            logger.info(f"amount is :{amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is :{order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = RemotePayTxnPage(ui_browser)
            logger.info("Clicking on UPI to start the txn.")
            rp_upi_txn.clickOnRemotePayUPI()
            logger.info("Launching UPI")
            rp_upi_txn.clickOnRemotePayLaunchUPI()
            logger.info("UPI txn is completed.")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].values[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id}")

            query = f"select * from upi_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_ref = result['txn_ref'].values[0]
            logger.debug(f"txn ref from upi txn : {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.debug(f"txn ref3 from upi txn : {txn_ref_3}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = upi_account_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = order_id

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where id='{txn_id}';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {created_time}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"acquirer_code_db from db : {acquirer_code_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"amount_db from db : {amount_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"bank_code_db from db : {bank_code_db}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"customer_name from db : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"payer_name from db : {payer_name}")
            external_ref_db = result['external_ref'].values[0]
            logger.debug(f"external_ref_db from db : {external_ref_db}")
            issuer_code_db = result['issuer_code'].values[0]
            logger.debug(f"issuer_code from db : {issuer_code_db}")
            mid = result['mid'].values[0]
            logger.debug(f"mid from db : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"tid from db : {tid}")
            org_code_db = result['org_code'].values[0]
            logger.debug(f"org_code_txn from db : {org_code_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway_db from db : {payment_gateway_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"payment_mode_db from db : {payment_mode_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"rrn_db from db : {rrn_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"settlement_status_db from db : {settlement_status_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"status_db from db : {status_db}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"txn_type from db : {txn_type}")
            state_db = result["state"].iloc[0]
            logger.debug(f"state_db from db : {state_db}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"txn_auth_code from db : {txn_auth_code}")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and " \
                    f"orig_txn_id ='{txn_id}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id_refunded from txn table is: {txn_id_refunded}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table is: {refund_auth_code}")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table is: {txn_type_refunded}")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn from txn table is: {rrn_refunded}")
            posting_date = result['created_time'].values[0]
            logger.debug(f"Fetching posting_date from txn table is: {posting_date}")
            created_time_refunded = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is: {created_time_refunded}")

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
        # ----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(posting_date)
                original_date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn_db),
                    "date": original_date_and_time,
                    "pmt_status_2": "STATUS:FAILED",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "FAILED",
                    "txn_id_2": txn_id_refunded,
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "pmt_msg_2": "PAYMENT FAILED",
                    "rrn_2": str(rrn_refunded),
                    "date_2": date_and_time,
                }
                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the refund txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the refund txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"payment_status_refunded from app txn details :{app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"payment_mode_refunded from app txn details :{app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"txn_id_refunded from app txn details : {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"payment_amt_refunded from app txn details : {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"settlement_status_refunded from app txn details : {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"payment_msg_refunded from app txn details : {payment_msg_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"rrn_original from app txn details :{app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"payment_status_original from app txn details : {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"payment_mode_original from app txn details :{app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"txn_id_original from app txn details : {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"payment_amt_original from app txn details : {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"settlement_status_original from app txn details : {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"payment_msg_original from app txn details : {payment_msg_original}")
                app_original_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"original_date_and_time from app txn details :{app_original_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_mode": app_payment_mode_original,
                    "settle_status": app_settlement_status_original,
                    "txn_id": app_txn_id_original,
                    "txn_amt": str(app_payment_amt_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "rrn": str(app_rrn_original),
                    "date": app_original_date_and_time,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn_2": str(app_rrn_refunded),
                    "date_2": app_date_and_time
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
                refunded_date_time = date_time_converter.db_datetime(posting_date)
                original_date_time = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "txn_amt": str(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_db),
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "pmt_status_2": "FAILED",
                    "pmt_state_2": "FAILED",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "FAILED",
                    "txn_amt_2": str(amount),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": txn_type_refunded,
                    "org_code_2": org_code,
                    "date_2": refunded_date_time,
                    "date": original_date_time
                }
                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status received for transaction details api is : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"Amount received for transaction details api is : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"Payment mode received for transaction details api is : {payment_mode_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"Settlement status received for transaction details api is :{settlement_status_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"Acquirer code received for transaction details api is : {acquirer_code_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code from api response for original txn is: {issuer_code_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"Txn Type received for transaction details api is : {txn_type_api_original}")
                date_api_original = response["postingDate"]
                logger.debug(f"Date received for transaction details api is : {date_api_original}")
                rrn_api_original = response['rrNumber']
                logger.debug(f"rrn api original : {rrn_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state from api response for original txn is: {state_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code from api response for original txn is: {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid from api response for original txn is: {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid from api response for original txn is: {tid_api_original}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status received for refund txn from api response is : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount received for refund txn from api response is : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode for refund txn from api response is : {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn received for refund txn from api response is : {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state received for refund txn from api response is : {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status received for refund txn from api response is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code received for refund txn from api response is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code received for refund txn from api response is : {org_code_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type received for refund txn from api response is : {txn_type_api_refunded}")
                date_api_refunded = response["postingDate"]
                logger.debug(f"date received for refund txn from api response is : {date_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_state": state_api_original,
                    "pmt_mode": payment_mode_api_original,
                    "settle_status": settlement_status_api_original,
                    "txn_amt": str(amount_api_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "RAZORPAY_PSP",

                    "pmt_status_2": "FAILED",
                    "pmt_state_2": "FAILED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "FAILED",
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id
                }
                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = f"select * from txn where id='{txn_id_refunded}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_refunded} ")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_refunded} ")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_refunded} ")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_refunded} ")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {state_db_refunded} ")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_refunded} ")

                query = f"select * from upi_txn where txn_id='{txn_id_refunded}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_refunded}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_original} ")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {acquirer_code_db_original} ")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code from DB : {bank_code_db_original} ")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_original} ")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_original}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_state": state_db_original,
                    "pmt_mode": payment_mode_db_original,
                    "txn_amt": amount_db_original,
                    "upi_txn_status": upi_status_db_original,
                    "settle_status": settlement_status_db_original,
                    "acquirer_code": acquirer_code_db_original,
                    "bank_code": bank_code_db_original,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_mc_id": upi_mc_id_db_original,

                    "pmt_status_2": status_db_refunded,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                }
                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_refunded = date_time_converter.to_portal_format(created_time_refunded)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn_number": rrn_db,
                    "auth_code": "-" if txn_auth_code is None else txn_auth_code,
                    "date_time_2": date_and_time_portal_refunded,
                    "pmt_state_2": "FAILED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "rrn_number_2": rrn_refunded,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code
                }
                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time for refund txn from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id for refund txn from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount for refund txn from portal is: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code for refund txn from portal is: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number for refund txn from portal is: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type for refund txn from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status for refund txn from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username for refund txn from portal is: {username}")

                date_time_original = transaction_details[1]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time_original}")
                transaction_id_original = transaction_details[1]['Transaction ID']
                logger.debug(f"txn_id from portal is: {transaction_id_original}")
                total_amount_original = transaction_details[1]['Total Amount'].split()
                logger.debug(f"amount from portal is: {total_amount_original}")
                auth_code_original = transaction_details[1]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code_original}")
                rr_number_original = transaction_details[1]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number_original}")
                transaction_type_original = transaction_details[1]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type_original}")
                status_original = transaction_details[1]['Status']
                logger.debug(f"status from portal is: {status_original}")
                username_original = transaction_details[1]['Username']
                logger.debug(f"username from portal is: {username_original}")

                actual_portal_values = {
                    "date_time": date_time_original,
                    "pmt_state": str(status_original),
                    "pmt_type": transaction_type_original,
                    "txn_amt": total_amount_original[1],
                    "username": username_original,
                    "txn_id": transaction_id_original,
                    "rrn_number": rr_number_original,
                    "auth_code": auth_code_original,
                    "date_time_2": date_time,
                    "pmt_state_2": str(status),
                    "pmt_type_2": transaction_type,
                    "txn_amt_2": total_amount[1],
                    "username_2": username,
                    "txn_id_2": transaction_id,
                    "rrn_number_2": rr_number,
                    "auth_code_2": auth_code
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {'PAID BY:': 'UPI',
                                               'merchant_ref_no': 'Ref # ' + str(order_id),
                                               'RRN': str(rrn_db),
                                               'BASE AMOUNT:': f"Rs.{amount:,}.00",
                                               'date': txn_date,
                                               'time': txn_time,
                                               'AUTH CODE': "" if refund_auth_code is None else refund_auth_code}
                logger.debug(
                    f"expected_charge_slip_values : {expected_charge_slip_values} for the testcase_id {testcase_id}")
                receipt_validator.perform_charge_slip_validations(txn_id,
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
def test_common_100_103_223():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Refund_Posted_Razorpay
    Sub Feature Description: Verification of a Remote Pay upi refund posted via Razorpay
    TC naming code description: 100: Payment Method, 103: RemotePay, 223: TC223
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'RAZORPAY_PSP' and card_terminal_acquirer_code = 'NONE'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"Fetched upi_mc_id is {upi_mc_id}")
        upi_account_id = result['pgMerchantId'].values[0]
        logger.info(f"Fetched upi_account_id is {upi_account_id}")

        TestSuiteSetup.launch_browser_and_context_initialize(browser_type='firefox')
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        msg = ''
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1201, 1299)
            logger.info(f"amount is :{amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is :{order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = RemotePayTxnPage(ui_browser)
            logger.info("Clicking on UPI to start the txn.")
            rp_upi_txn.clickOnRemotePayUPI()
            logger.info("Launching UPI")
            rp_upi_txn.clickOnRemotePayLaunchUPI()
            logger.info("UPI txn is completed.")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}'"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].values[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id}")

            query = f"select * from upi_txn where txn_id='{txn_id}'"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_ref = result['txn_ref'].values[0]
            logger.info(f"txn_ref is: {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.info(f"txn_ref_3 is: {txn_ref_3}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = upi_account_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = order_id

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {created_time}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"acquirer_code_db from db : {acquirer_code_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"amount_db from db : {amount_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"bank_code_db from db : {bank_code_db}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"customer_name from db : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"payer_name from db : {payer_name}")
            external_ref_db = result['external_ref'].values[0]
            logger.debug(f"external_ref_db from db : {external_ref_db}")
            issuer_code_db = result['issuer_code'].values[0]
            logger.debug(f"issuer_code from db : {issuer_code_db}")
            mid = result['mid'].values[0]
            logger.debug(f"mid from db : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"tid from db : {tid}")
            org_code_db = result['org_code'].values[0]
            logger.debug(f"org_code_txn from db : {org_code_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway_db from db : {payment_gateway_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"payment_mode_db from db : {payment_mode_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"rrn_db from db : {rrn_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"settlement_status_db from db : {settlement_status_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"status_db from db : {status_db}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"txn_type from db : {txn_type}")
            state_db = result["state"].iloc[0]
            logger.debug(f"state_db from db : {state_db}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"txn_auth_code from db : {txn_auth_code}")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and " \
                    f"orig_txn_id ='{txn_id}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id_refunded from txn table is: {txn_id_refunded}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table is: {refund_auth_code}")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table is: {txn_type_refunded}")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn from txn table is: {rrn_refunded}")
            posting_date = result['created_time'].values[0]
            logger.debug(f"Fetching posting_date from txn table is: {posting_date}")
            created_time_refunded = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is: {created_time_refunded}")

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
                original_date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn_db),
                    "date": original_date_and_time,
                    "pmt_status_2": "STATUS:REFUND_POSTED",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "REVPENDING",
                    "txn_id_2": txn_id_refunded,
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "pmt_msg_2": "REFUND PENDING",
                    "rrn_2": str(rrn_refunded),
                    "date_2": date_and_time,
                }
                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"payment_status_refunded from app txn details :{app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"payment_mode_refunded from app txn details :{app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"txn_id_refunded from app txn details : {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"payment_amt_refunded from app txn details : {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"settlement_status_refunded from app txn details : {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"payment_msg_refunded from app txn details : {payment_msg_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"rrn_original from app txn details :{app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"payment_status_original from app txn details : {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"payment_mode_original from app txn details :{app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"txn_id_original from app txn details : {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"payment_amt_original from app txn details : {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"settlement_status_original from app txn details : {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"payment_msg_original from app txn details : {payment_msg_original}")
                app_original_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"original_date_and_time from app txn details :{app_original_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_mode": app_payment_mode_original,
                    "settle_status": app_settlement_status_original,
                    "txn_id": app_txn_id_original,
                    "txn_amt": str(app_payment_amt_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "rrn": str(app_rrn_original),
                    "date": app_original_date_and_time,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn_2": str(app_rrn_refunded),
                    "date_2": app_date_and_time
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
                refunded_date_time = date_time_converter.db_datetime(posting_date)
                original_date_time = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "txn_amt": str(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_db),
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "REVPENDING",
                    "txn_amt_2": str(amount),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": txn_type_refunded,
                    "org_code_2": org_code,
                    "date_2": refunded_date_time,
                    "date": original_date_time
                }
                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status received for transaction details api is : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"Amount received for transaction details api is : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"Payment mode received for transaction details api is : {payment_mode_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"Settlement status received for transaction details api is :{settlement_status_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"Acquirer code received for transaction details api is : {acquirer_code_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code from api response for original txn is: {issuer_code_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"Txn Type received for transaction details api is : {txn_type_api_original}")
                date_api_original = response["postingDate"]
                logger.debug(f"Date received for transaction details api is : {date_api_original}")
                rrn_api_original = response['rrNumber']
                logger.debug(f"rrn api original : {rrn_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state from api response for original txn is: {state_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code from api response for original txn is: {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid from api response for original txn is: {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid from api response for original txn is: {tid_api_original}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status received for refund txn from api response is : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount received for refund txn from api response is : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode for refund txn from api response is : {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn received for refund txn from api response is : {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state received for refund txn from api response is : {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status received for refund txn from api response is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code received for refund txn from api response is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code received for refund txn from api response is : {org_code_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type received for refund txn from api response is : {txn_type_api_refunded}")
                date_api_refunded = response["postingDate"]
                logger.debug(f"date received for refund txn from api response is : {date_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_state": state_api_original,
                    "pmt_mode": payment_mode_api_original,
                    "settle_status": settlement_status_api_original,
                    "txn_amt": str(amount_api_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "REFUND_POSTED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id
                }
                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = f"select * from txn where id='{txn_id_refunded}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_refunded} ")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_refunded} ")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_refunded} ")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_refunded} ")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {state_db_refunded} ")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_refunded} ")

                query = f"select * from upi_txn where txn_id='{txn_id_refunded}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_refunded}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_original} ")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {acquirer_code_db_original} ")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code from DB : {bank_code_db_original} ")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_original} ")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_original}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_state": state_db_original,
                    "pmt_mode": payment_mode_db_original,
                    "txn_amt": amount_db_original,
                    "upi_txn_status": upi_status_db_original,
                    "settle_status": settlement_status_db_original,
                    "acquirer_code": acquirer_code_db_original,
                    "bank_code": bank_code_db_original,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_mc_id": upi_mc_id_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                }
                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_refunded = date_time_converter.to_portal_format(created_time_refunded)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn_number": rrn_db,
                    "auth_code": "-" if txn_auth_code is None else txn_auth_code,
                    "date_time_2": date_and_time_portal_refunded,
                    "pmt_state_2": "REFUND_POSTED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "rrn_number_2": rrn_refunded,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code
                }
                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time for refund txn from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id for refund txn from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount for refund txn from portal is: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code for refund txn from portal is: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number for refund txn from portal is: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type for refund txn from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status for refund txn from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username for refund txn from portal is: {username}")

                date_time_original = transaction_details[1]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time_original}")
                transaction_id_original = transaction_details[1]['Transaction ID']
                logger.debug(f"txn_id from portal is: {transaction_id_original}")
                total_amount_original = transaction_details[1]['Total Amount'].split()
                logger.debug(f"amount from portal is: {total_amount_original}")
                auth_code_original = transaction_details[1]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code_original}")
                rr_number_original = transaction_details[1]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number_original}")
                transaction_type_original = transaction_details[1]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type_original}")
                status_original = transaction_details[1]['Status']
                logger.debug(f"status from portal is: {status_original}")
                username_original = transaction_details[1]['Username']
                logger.debug(f"username from portal is: {username_original}")

                actual_portal_values = {
                    "date_time": date_time_original,
                    "pmt_state": str(status_original),
                    "pmt_type": transaction_type_original,
                    "txn_amt": total_amount_original[1],
                    "username": username_original,
                    "txn_id": transaction_id_original,
                    "rrn_number": rr_number_original,
                    "auth_code": auth_code_original,
                    "date_time_2": date_time,
                    "pmt_state_2": str(status),
                    "pmt_type_2": transaction_type,
                    "txn_amt_2": total_amount[1],
                    "username_2": username,
                    "txn_id_2": transaction_id,
                    "rrn_number_2": rr_number,
                    "auth_code_2": auth_code
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(rrn_db),
                                              'BASE AMOUNT:': f"Rs.{amount:,}.00",
                                              'date': txn_date,
                                              'time': txn_time,
                                              'AUTH CODE': "" if refund_auth_code is None else refund_auth_code}

                logger.debug(
                    f"expected_charge_slip_values : {expected_charge_slip_values} for the testcase_id {testcase_id}")
                receipt_validator.perform_charge_slip_validations(txn_id,
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
def test_common_100_103_224():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_partial_Refund_Razorpay
    Sub Feature Description: Verification of a Remote Pay upi partial refund via Razorpay
    TC naming code description: 100: Payment Method, 103: RemotePay, 224: TC224
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'RAZORPAY_PSP' and card_terminal_acquirer_code = 'NONE'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"Fetched upi_mc_id is {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize(browser_type='firefox')
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

            amount = 2600
            logger.info(f"amount is :{amount}")
            refund_amount = 1600
            logger.info(f"refund_amount is :{refund_amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is :{order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = RemotePayTxnPage(ui_browser)
            logger.info("Clicking on UPI to start the txn.")
            rp_upi_txn.clickOnRemotePayUPI()
            logger.info("Launching UPI")
            rp_upi_txn.clickOnRemotePayLaunchUPI()
            rp_upi_txn.clickOnRemotePayCancelUPI()
            rp_upi_txn.clickOnRemotePayProceed()
            logger.info("UPI txn is completed.")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}'"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].values[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id}")

            query = f"select * from upi_txn where txn_id='{txn_id}'"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {created_time}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"acquirer_code_db from db : {acquirer_code_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"amount_db from db : {amount_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"bank_code_db from db : {bank_code_db}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"customer_name from db : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"payer_name from db : {payer_name}")
            external_ref_db = result['external_ref'].values[0]
            logger.debug(f"external_ref_db from db : {external_ref_db}")
            issuer_code_db = result['issuer_code'].values[0]
            logger.debug(f"issuer_code from db : {issuer_code_db}")
            mid = result['mid'].values[0]
            logger.debug(f"mid from db : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"tid from db : {tid}")
            org_code_db = result['org_code'].values[0]
            logger.debug(f"org_code_txn from db : {org_code_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway_db from db : {payment_gateway_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"payment_mode_db from db : {payment_mode_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"rrn_db from db : {rrn_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"settlement_status_db from db : {settlement_status_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"status_db from db : {status_db}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"txn_type from db : {txn_type}")
            state_db = result["state"].iloc[0]
            logger.debug(f"state_db from db : {state_db}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"txn_auth_code from db : {txn_auth_code}")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": refund_amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id ='{str(txn_id)}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id_refunded from txn table is: {txn_id_refunded}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table is: {refund_auth_code}")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table is: {txn_type_refunded}")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn from txn table is: {rrn_refunded}")
            posting_date = result['created_time'].values[0]
            logger.debug(f"Fetching posting_date from txn table is: {posting_date}")
            created_time_refunded = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is: {created_time_refunded}")

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
                original_date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn_db),
                    "date": original_date_and_time,
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_refunded,
                    "txn_amt_2": "{:,.2f}".format(refund_amount),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "rrn_2": str(rrn_refunded),
                    "date_2": date_and_time,
                }
                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"payment_status_refunded from app txn details :{app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"payment_mode_refunded from app txn details :{app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"txn_id_refunded from app txn details : {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"payment_amt_refunded from app txn details : {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"settlement_status_refunded from app txn details : {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"payment_msg_refunded from app txn details : {payment_msg_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"rrn_original from app txn details :{app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"payment_status_original from app txn details : {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"payment_mode_original from app txn details :{app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"txn_id_original from app txn details : {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"payment_amt_original from app txn details : {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"settlement_status_original from app txn details : {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"payment_msg_original from app txn details : {payment_msg_original}")
                app_original_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"original_date_and_time from app txn details :{app_original_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_mode": app_payment_mode_original,
                    "settle_status": app_settlement_status_original,
                    "txn_id": app_txn_id_original,
                    "txn_amt": str(app_payment_amt_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "rrn": str(app_rrn_original),
                    "date": app_original_date_and_time,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn_2": str(app_rrn_refunded),
                    "date_2": app_date_and_time
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
                refunded_date_time = date_time_converter.db_datetime(posting_date)
                original_date_time = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "txn_amt": str(amount),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_db),
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,

                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "SETTLED",
                    "txn_amt_2": str(refund_amount),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": txn_type_refunded,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": refunded_date_time,
                    "date": original_date_time
                }
                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status received for transaction details api is : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"Amount received for transaction details api is : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"Payment mode received for transaction details api is : {payment_mode_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"Settlement status received for transaction details api is :{settlement_status_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"Acquirer code received for transaction details api is : {acquirer_code_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code from api response for original txn is: {issuer_code_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"Txn Type received for transaction details api is : {txn_type_api_original}")
                date_api_original = response["postingDate"]
                logger.debug(f"Date received for transaction details api is : {date_api_original}")
                rrn_api_original = response['rrNumber']
                logger.debug(f"rrn api original : {rrn_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state from api response for original txn is: {state_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code from api response for original txn is: {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid from api response for original txn is: {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid from api response for original txn is: {tid_api_original}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status received for refund txn from api response is : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount received for refund txn from api response is : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode for refund txn from api response is : {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn received for refund txn from api response is : {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state received for refund txn from api response is : {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status received for refund txn from api response is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code received for refund txn from api response is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code received for refund txn from api response is : {org_code_api_refunded}")
                mid_api_refunded = response["mid"]
                logger.debug(f"mid received for refund txn from api response is : {mid_api_refunded}")
                tid_api_refunded = response["tid"]
                logger.debug(f"tid received for refund txn from api response is : {tid_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type received for refund txn from api response is : {txn_type_api_refunded}")
                date_api_refunded = response["postingDate"]
                logger.debug(f"date received for refund txn from api response is : {date_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_state": state_api_original,
                    "pmt_mode": payment_mode_api_original,
                    "settle_status": settlement_status_api_original,
                    "txn_amt": str(amount_api_original),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),

                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name,
                    "payer_name_2": payer_name,
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "RAZORPAY_PSP",

                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": refund_amount,
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id
                }
                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = f"select * from txn where id='{txn_id_refunded}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_refunded} ")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_refunded} ")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_refunded} ")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_refunded} ")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {state_db_refunded} ")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_refunded} ")

                query = f"select * from upi_txn where txn_id='{txn_id_refunded}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_refunded}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_original} ")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code from DB : {acquirer_code_db_original} ")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code from DB : {bank_code_db_original} ")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status from DB : {settlement_status_db_original} ")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db_original}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_state": state_db_original,
                    "pmt_mode": payment_mode_db_original,
                    "txn_amt": amount_db_original,
                    "upi_txn_status": upi_status_db_original,
                    "settle_status": settlement_status_db_original,
                    "acquirer_code": acquirer_code_db_original,
                    "bank_code": bank_code_db_original,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_mc_id": upi_mc_id_db_original,

                    "pmt_status_2": status_db_refunded,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                }
                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_refunded = date_time_converter.to_portal_format(created_time_refunded)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn_number": rrn_db,
                    "auth_code": "-" if txn_auth_code is None else txn_auth_code,
                    "date_time_2": date_and_time_portal_refunded,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(refund_amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "rrn_number_2": rrn_refunded,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code
                }
                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time for refund txn from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id for refund txn from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount for refund txn from portal is: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code for refund txn from portal is: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number for refund txn from portal is: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type for refund txn from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status for refund txn from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username for refund txn from portal is: {username}")

                date_time_original = transaction_details[1]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time_original}")
                transaction_id_original = transaction_details[1]['Transaction ID']
                logger.debug(f"txn_id from portal is: {transaction_id_original}")
                total_amount_original = transaction_details[1]['Total Amount'].split()
                logger.debug(f"amount from portal is: {total_amount_original}")
                auth_code_original = transaction_details[1]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code_original}")
                rr_number_original = transaction_details[1]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number_original}")
                transaction_type_original = transaction_details[1]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type_original}")
                status_original = transaction_details[1]['Status']
                logger.debug(f"status from portal is: {status_original}")
                username_original = transaction_details[1]['Username']
                logger.debug(f"username from portal is: {username_original}")

                actual_portal_values = {
                    "date_time": date_time_original,
                    "pmt_state": str(status_original),
                    "pmt_type": transaction_type_original,
                    "txn_amt": total_amount_original[1],
                    "username": username_original,
                    "txn_id": transaction_id_original,
                    "rrn_number": rr_number_original,
                    "auth_code": auth_code_original,
                    "date_time_2": date_time,
                    "pmt_state_2": str(status),
                    "pmt_type_2": transaction_type,
                    "txn_amt_2": total_amount[1],
                    "username_2": username,
                    "txn_id_2": transaction_id,
                    "rrn_number_2": rr_number,
                    "auth_code_2": auth_code
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(rrn_db),
                                              'BASE AMOUNT:': f"Rs.{amount:,}.00",
                                              'date': txn_date,
                                              'time': txn_time,
                                              'AUTH CODE': "" if refund_auth_code is None else refund_auth_code}

                logger.debug(
                    f"expected_charge_slip_values : {expected_charge_slip_values} for the testcase_id {testcase_id}")
                receipt_validator.perform_charge_slip_validations(txn_id,
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