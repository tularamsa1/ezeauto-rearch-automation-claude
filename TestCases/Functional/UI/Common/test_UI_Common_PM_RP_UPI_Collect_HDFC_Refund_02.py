import sys
import time
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from PageFactory.portal_remotePayPage import remotePayTxnPage
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
def test_common_100_103_046():
    """
    Sub Feature Code: UI_Common_PM_RP_Pure_upi_collect_two_times_partial_refund_HDFC
    Sub Feature Description: Verification of a remote pay two times partial refund for upi collect txn
    TC naming code description:
    100: Payment Method
    103: RemotePay
    044: TC046
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 300
            partial_refunded_amount = 150
            full_refund_amount = 150
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            paymentLinkUrl = response['paymentLink']
            externalRef = response.get('externalRefNumber')
            payment_intent_id = response.get('paymentIntentId')
            ui_driver.get(paymentLinkUrl)
            remotePayUpiCollectTxn = remotePayTxnPage(ui_driver)
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

            query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_upi_mc_id = result['id'].values[0]
            logger.debug(f"Fetching original_upi_mc_id from db query : {original_upi_mc_id} ")
            original_mid = result['mid'].values[0]
            logger.debug(f"Fetching original_mid from db query : {original_mid} ")
            original_tid = result['tid'].values[0]
            logger.debug(f"Fetching original_tid from db query : {original_tid} ")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "'"
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

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": partial_refunded_amount,
                                                                    "originalTransactionId": str(original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(
                original_txn_id) + "'"
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

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": full_refund_amount,
                                                                    "originalTransactionId": str(original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api when refund amount is greater than original amount : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(
                original_txn_id) + "' order by created_time limit 1"
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
                    "txn_amt": str(amount)+".00",
                    "txn_amt_2": str(partial_refunded_amount)+".00",
                    "customer_name": original_customer_name,
                    "refund_customer_name": original_customer_name,
                    "payer_name": original_payer_name,
                    "refund_payer_name": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "refund_pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(original_rrn),
                    "refund_rrn": str(partially_refunded_rrn),
                    "auth_code": original_auth_code,
                    "refund_auth_code": partially_refunded_auth_code,
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
                    "full_refund_auth_code": fully_refunded_auth_code
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
                logger.debug(f"Fetching txn_id from txn history for the txn : {partially_refunded_txn_id}, {app_rrn_refunded}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {partially_refunded_txn_id}, {app_date_and_time}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_auth_code_refunded = transactions_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {partially_refunded_txn_id}, {app_auth_code_refunded}")
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
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {original_txn_id}, {app_auth_code_original}")
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
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_original}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(fully_refunded_txn_id)
                fully_refunded_app_rrn = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {fully_refunded_txn_id}, {fully_refunded_app_rrn}")
                fully_refunded_app_auth_code = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {fully_refunded_txn_id}, {fully_refunded_app_auth_code}")
                fully_refunded_app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {fully_refunded_app_payment_status}")
                fully_refunded_app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {fully_refunded_app_payment_mode}")
                fully_refunded_app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {fully_refunded_app_txn_id}")
                fully_refunded_app_payment_amt = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {fully_refunded_app_payment_amt}")
                fully_refunded_app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {fully_refunded_app_settlement_status}")
                fully_refunded_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {fully_refunded_payment_msg}")
                fully_refunded_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {fully_refunded_txn_id}, {fully_refunded_customer_name}")

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
                    "auth_code": app_auth_code_original,
                    "refund_auth_code": app_auth_code_refunded,
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
                    "full_refund_auth_code": fully_refunded_app_auth_code
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
                    "original_acquirer_code": "HDFC",
                    "original_issuer_code": "HDFC",
                    "original_txn_type": original_txn_type,
                    "original_mid": original_mid,
                    "original_tid": original_tid,
                    "original_org_code": original_org_code_txn,
                    "refunded_acquirer_code": "HDFC",
                    # "issuer_code_refunded": "HDFC",
                    "refunded_txn_type": partially_refunded_txn_type,
                    "refunded_mid": original_mid,
                    "refunded_tid": original_tid,
                    "refunded_org_code": original_org_code_txn,
                    "refund_auth_code": partially_refunded_auth_code,
                    "original_auth_code": original_auth_code,
                    "date": date,

                    "fully_refunded_pmt_status": "REFUNDED",
                    "fully_refunded_pmt_state": "REFUNDED",
                    "fully_refunded_pmt_mode": "UPI",
                    "fully_refunded_settle_status": "SETTLED",
                    "fully_refunded_amt": str(full_refund_amount),
                    "fully_refunded_customer_name": original_customer_name,
                    "fully_refunded_payer_name": original_payer_name,
                    "fully_refunded_rrn": str(fully_refunded_rrn),
                    "fully_refunded_acquirer_code": "HDFC",
                    "fully_refunded_txn_type": fully_refunded_txn_type,
                    "fully_refunded_mid": original_mid,
                    "fully_refunded_tid": original_tid,
                    "fully_refunded_org_code": original_org_code_txn,
                    "fully_refund_auth_code": fully_refunded_auth_code,

                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
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

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": partially_refunded_txn_id})
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
                # issuer_code_api_refunded = response["issuerCode"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                auth_code_api_refunded = response["authCode"]
                date_api_refunded = response["postingDate"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": fully_refunded_txn_id})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                api_status_full_refund = response["status"]
                api_amount_full_refund = int(response["amount"])
                api_payment_mode_full_refund = response["paymentMode"]
                api_rrn__full_refund = response["rrNumber"]
                api_state_full_refund = response["states"][0]
                api_settlement_status_full_refund = response["settlementStatus"]
                # issuer_code_api_refunded = response["issuerCode"]
                api_acquirer_code_full_refund = response["acquirerCode"]
                api_org_code_full_refund = response["orgCode"]
                api_mid_full_refund = response["mid"]
                api_tid_full_refund = response["tid"]
                api_txn_type_full_refund = response["txnType"]
                api_auth_code_full_refund = response["authCode"]
                api_date_full_refund = response["postingDate"]
                api_customer_name_full_refund = response["customerName"]
                api_payer_name_full_refund = response["payerName"]

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
                    # "issuer_code_refunded": issuer_code_api_refunded,
                    "refunded_txn_type": txn_type_api_refunded,
                    "refunded_mid": mid_api_refunded, "refunded_tid": tid_api_refunded,
                    "refunded_org_code": org_code_api_refunded,
                    "refund_auth_code": auth_code_api_refunded,
                    "original_auth_code": auth_code_api_original,
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
                    "fully_refund_auth_code": api_auth_code_full_refund,
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
                    "original_acquirer_code": "HDFC",
                    "refunded_acquirer_code": "HDFC",
                    "original_bank_code": "HDFC",
                    "bank_code_refunded": "HDFC",
                    # "original_pmt_gateway": "HDFC",
                    # "refunded_pmt_gateway": "HDFC",
                    "original_upi_txn_type": "COLLECT",
                    "refunded_upi_txn_type": "REFUND",
                    "original_upi_bank_code": "HDFC",
                    "refunded_upi_bank_code": "HDFC",
                    "original_upi_mc_id": original_upi_mc_id,
                    "refunded_upi_mc_id": original_upi_mc_id,
                    "original_mid": original_mid,
                    "original_tid": original_tid,
                    "refund_mid": original_mid,
                    "refund_tid": original_tid,


                    "fully_refunded_pmt_status": "REFUNDED",
                    "fully_refunded_pmt_state": "REFUNDED",
                    "fully_refunded_pmt_mode": "UPI",
                    "fully_refunded_amt": full_refund_amount,
                    "fully_refunded_upi_txn_status": "REFUND",
                    "fully_refunded_settle_status": "SETTLED",
                    "fully_refunded_acquirer_code": "HDFC",
                    "fully_refunded_upi_txn_type": "REFUND",
                    "fully_refunded_upi_bank_code": "HDFC",
                    "fully_refunded_upi_mc_id": original_upi_mc_id,
                    "fully_refund_mid": original_mid,
                    "fully_refund_tid": original_tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + partially_refunded_txn_id + "'"
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

                query = "select * from upi_txn where txn_id='" + partially_refunded_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                bank_code_db_refunded = result["bank_code"].iloc[0]

                query = "select * from txn where id='" + original_txn_id + "'"
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

                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + fully_refunded_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_full_refund = result["status"].iloc[0]
                payment_mode_db_full_refund = result["payment_mode"].iloc[0]
                amount_db_full_refund = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_full_refund = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_full_refund = result["acquirer_code"].iloc[0]
                settlement_status_db_full_refund = result["settlement_status"].iloc[0]
                tid_db_full_refund = result['tid'].values[0]
                mid_db_full_refund = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + fully_refunded_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_full_refund = result["status"].iloc[0]
                upi_txn_type_db_full_refund = result["txn_type"].iloc[0]
                upi_bank_code_db_full_refund = result["bank_code"].iloc[0]
                upi_mc_id_db_full_refund = result["upi_mc_id"].iloc[0]
                bank_code_db_full_refund = result["bank_code"].iloc[0]

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
                    # "original_pmt_gateway": payment_gateway_db_original,
                    # "refunded_pmt_gateway": payment_gateway_db_refunded,
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
                expected_portal_values = {"refunded_pmt_state": "Refunded", "original_pmt_mode": "UPI",
                                          "original_pmt_amt": str(amount),
                                          "original_pmt_state": "Authorized Refunded",
                                          "Amount Original": str(partial_refunded_amount), "refunded_pmt_mode": "UPI"}

                logger.debug(f"expected_portal_values : {expected_portal_values} for the testcase_id {testcase_id}")

                driver_ui = TestSuiteSetup.initialize_portal_driver()

                login_page_portal = PortalLoginPage(driver_ui)

                logger.info(f"Logging in Portal using username : {portal_username}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(driver_ui)
                home_page_portal.search_merchant_name(str(org_code))
                logger.info(f"Switching to merchant : {org_code}")
                home_page_portal.click_switch_button(org_code)
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(driver_ui)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(partially_refunded_txn_id)
                portal_txn_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amt = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(original_txn_id)
                portal_txn_type_original = portal_values_dict['Type']
                portal_status_original = portal_values_dict['Status']
                portal_amt_original = portal_values_dict['Total Amount']
                portal_username_original = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")

                actual_portal_values = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                        "Payment amount": str(portal_amt.split('.')[1]),
                                        "Payment Status Original": portal_status_original,
                                        "Amount Original": str(portal_amt_original.split('.')[1]),
                                        "Payment Mode Original": portal_txn_type_original}

                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(partially_refunded_posting_date)
                expected_chargeslip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(partially_refunded_rrn),
                                              'BASE AMOUNT:': "Rs." + str(partial_refunded_amount) + ".00",
                                              'date': txn_date,
                                              'time': txn_time,
                                              'AUTH CODE': partially_refunded_auth_code}

                logger.debug(
                    f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(partially_refunded_txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_chargeslip_values)


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

    #     if (ConfigReader.read_config("Validations", "app_validation")) == "True":
    #         logger.info(f"Started APP validation for the test case : {testcase_id}")
    #         try:
    #             expected_app_values = {"refunded_txn_status": "STATUS:REFUNDED",
    #                                    "refunded_txn_mode": "UPI",
    #                                    "refunded_txn_id": txn_id_refunded,
    #                                    "refunded_txn_amt": str(amount),
    #                                    "original_txn_status": "STATUS:AUTHORIZED_REFUNDED",
    #                                    "original_txn_mode": "UPI",
    #                                    "original_txn_id": txn_id_original,
    #                                    "original_txn_amt": str(amount),
    #                                    "original_txn_rrn": str(rrn_original)
    #                                    }
    #             logger.debug(f"expected_app_values: {expected_app_values}")
    #             app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
    #             loginPage = LoginPage(app_driver)
    #             loginPage.perform_login(app_username, app_password)
    #             homePage = HomePage(app_driver)
    #             homePage.wait_for_navigation_to_load()
    #             homePage.check_home_page_logo()
    #             homePage.wait_for_home_page_load()
    #             homePage.click_on_history()
    #
    #             transactions_history_page = TransHistoryPage(app_driver)
    #             transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)
    #
    #             app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
    #             logger.debug(
    #                 f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
    #             app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
    #             logger.debug(
    #                 f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
    #             app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
    #             logger.debug(
    #                 f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
    #             app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
    #             logger.debug(
    #                 f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
    #
    #             transactions_history_page.click_back_Btn_transaction_details()
    #             transactions_history_page.click_on_transaction_by_txn_id(txn_id_original)
    #
    #             app_rrn_original = transactions_history_page.fetch_RRN_text()
    #             logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_original}")
    #             app_payment_status_original = transactions_history_page.fetch_txn_status_text()
    #             logger.debug(
    #                 f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
    #             app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
    #             logger.debug(
    #                 f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
    #                 f"Mode = {app_payment_mode_original}")
    #             app_txn_id_original = transactions_history_page.fetch_txn_id_text()
    #             logger.debug(
    #                 f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
    #             app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
    #             logger.debug(
    #                 f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
    #
    #             actual_app_values = {"refunded_txn_status": app_payment_status_refunded,
    #                                  "refunded_txn_mode": app_payment_mode_refunded,
    #                                  "refunded_txn_id": app_txn_id_refunded,
    #                                  "refunded_txn_amt": str(app_payment_amt_refunded),
    #                                  "original_txn_status": app_payment_status_original,
    #                                  "original_txn_mode": app_payment_mode_original,
    #                                  "original_txn_id": txn_id_original,
    #                                  "original_txn_amt": str(app_payment_amt_original),
    #                                  "original_txn_rrn": str(app_rrn_original)
    #                                  }
    #             logger.debug(f"actual_app_values : {actual_app_values} for the test case {testcase_id}")
    #             Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
    #         except Exception as e:
    #             Configuration.perform_app_val_exception(testcase_id, e)
    #             logger.info(f"Completed APP validation for the test case : {testcase_id}")
    #
    #     # -----------------------------------------End of App Validation---------------------------------------
    #
    #     # -----------------------------------------Start of API Validation------------------------------------
    #     if (ConfigReader.read_config("Validations", "api_validation")) == "True":
    #         logger.info(f"Started API validation for the test case : {testcase_id}")
    #         try:
    #             expected_api_values = {"refunded_txn_status": "REFUNDED",
    #                                    "refunded_txn_amt": amount,
    #                                    "refunded_txn_mode": "UPI",
    #                                    "original_txn_status": "AUTHORIZED_REFUNDED",
    #                                    "original_txn_amt": amount,
    #                                    "original_txn_mode": "UPI",
    #                                    "original_txn_rrn": str(rrn_original)
    #                                    }
    #             logger.debug(f"expected_api_values : {expected_api_values} for the test case {testcase_id}")
    #
    #             api_details = DBProcessor.get_api_details('txnDetails',
    #                                                       request_body={"username": app_username, "password": app_password,
    #                                                                     "txnId": txn_id_original})
    #             logger.debug(f"API DETAILS for original txn : {api_details}")
    #             response = APIProcessor.send_request(api_details)
    #             logger.debug(f"Response received for transaction details api is : {response}")
    #             logger.debug(f"response : {response}")
    #             status_api_original = response["status"]
    #             amount_api_original = int(response["amount"])
    #             payment_mode_api_original = response["paymentMode"]
    #             rrn_api_original = response["rrNumber"]
    #
    #             api_details = DBProcessor.get_api_details('txnDetails',
    #                                                       request_body={"username": app_username, "password": app_password,
    #                                                                     "txnId": txn_id_refunded})
    #             logger.debug(f"API DETAILS for original txn : {api_details}")
    #             response = APIProcessor.send_request(api_details)
    #             logger.debug(f"Response received for transaction details api is : {response}")
    #             print(response)
    #             status_api_refunded = response["status"]
    #             amount_api_refunded = int(response["amount"])
    #             payment_mode_api_refunded = response["paymentMode"]
    #
    #             logger.debug(
    #                 f"Fetching Transaction status of refunded txn from transaction api : {status_api_refunded}")
    #             logger.debug(
    #                 f"Fetching Transaction amount of refunded txn from transaction api : {amount_api_refunded}")
    #             logger.debug(
    #                 f"Fetching Transaction payment of refunded txn mode from transaction api : {payment_mode_api_refunded}")
    #             logger.debug(
    #                 f"Fetching Transaction status of original txn from transaction api : {status_api_original}")
    #             logger.debug(
    #                 f"Fetching Transaction amount of original txn from transaction api : {amount_api_original}")
    #             logger.debug(
    #                 f"Fetching Transaction payment of original txn mode from transaction api : {payment_mode_api_original}")
    #
    #             actual_api_values = {"refunded_txn_status": status_api_refunded,
    #                                  "refunded_txn_amt": amount_api_refunded,
    #                                  "refunded_txn_mode": payment_mode_api_refunded,
    #                                  "original_txn_status": status_api_original,
    #                                  "original_txn_amt": amount_api_original,
    #                                  "original_txn_mode": payment_mode_api_original,
    #                                  "original_txn_rrn": str(rrn_api_original)
    #                                  }
    #             logger.debug(f"actual_api_values : {actual_api_values} for the test case {testcase_id}")
    #
    #             Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
    #         except Exception as e:
    #             Configuration.perform_api_val_exception(testcase_id, e)
    #         logger.info(f"Completed API validation for the test case : {testcase_id}")
    #
    #     # -----------------------------------------End of API Validation---------------------------------------
    #
    #     # -----------------------------------------Start of DB Validation--------------------------------------
    #     if (ConfigReader.read_config("Validations", "db_validation")) == "True":
    #         logger.info(f"Started DB validation for the test case : {testcase_id}")
    #         try:
    #             expected_db_values = {"refunded_txn_status": "REFUNDED",
    #                                   "refunded_txn_mode": "UPI",
    #                                   "refunded_txn_amt": amount,
    #                                   "original_txn_status": "AUTHORIZED_REFUNDED",
    #                                   "original_txn_amt": amount,
    #                                   "original_txn_mode": "UPI",
    #                                   "refunded_upi_txn_status": "REFUNDED",
    #                                   "refunded_upi_txn_bank_code": "HDFC",
    #                                   "refunded_upi_txn_type": "REFUND",
    #                                   "original_upi_txn_status": "AUTHORIZED_REFUNDED",
    #                                   "original_upi_txn_bank_code": "HDFC",
    #                                   "original_upi_txn_type": "COLLECT",
    #                                   }
    #
    #             logger.debug(f"expected_db_values : {expected_db_values} for the test case {testcase_id}")
    #
    #             query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_refunded + "'"
    #             logger.debug(f"DB query to fetch status, amount, payment mode and external reference from DB : {query}")
    #             logger.debug(f"Query : {query}")
    #             result = DBProcessor.getValueFromDB(query)
    #             logger.debug(f"Fetching Query result from DB : {result} ")
    #             status_db_refunded = result["status"].iloc[0]
    #             payment_mode_db_refunded = result["payment_mode"].iloc[0]
    #             amount_db_refunded = int(result["amount"].iloc[0])
    #             logger.debug(f"Fetching Transaction status from DB : {status_db_refunded} ")
    #             logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_refunded} ")
    #             logger.debug(f"Fetching Transaction amount from DB : {amount_db_refunded} ")
    #
    #             query = "select status,bank_code,txn_type from upi_txn where txn_id='" + txn_id_refunded + "'"
    #             logger.debug(f"Query to fetch data from upi_txn table : {query}")
    #             result = DBProcessor.getValueFromDB(query)
    #             logger.debug(f"Query result : {result}")
    #             upi_status_db_refunded = result["status"].iloc[0]
    #             upi_bank_code_db_refunded = result["bank_code"].iloc[0]
    #             upi_txn_type_db_refunded = result["txn_type"].iloc[0]
    #
    #             query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_original + "'"
    #             logger.debug(
    #                 f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
    #             logger.debug(f"Query : {query}")
    #             result = DBProcessor.getValueFromDB(query)
    #             logger.debug(f"Fetching Query result from DB of original txn : {result} ")
    #             status_db_original = result["status"].iloc[0]
    #             payment_mode_db_original = result["payment_mode"].iloc[0]
    #             amount_db_original = int(result["amount"].iloc[0])
    #             logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
    #             logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
    #             logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
    #
    #             query = "select status,bank_code,txn_type from upi_txn where txn_id='" + txn_id_original + "'"
    #             logger.debug(f"Query to fetch data from upi_txn table : {query}")
    #             result = DBProcessor.getValueFromDB(query)
    #             logger.debug(f"Query result : {result}")
    #             upi_status_db_original = result["status"].iloc[0]
    #             upi_bank_code_db_original = result["bank_code"].iloc[0]
    #             upi_txn_type_db_original = result["txn_type"].iloc[0]
    #
    #             actual_db_values = {"refunded_txn_status": status_db_refunded,
    #                                 "refunded_txn_mode": payment_mode_db_refunded,
    #                                 "refunded_txn_amt": amount_db_refunded,
    #                                 "original_txn_status": status_db_original,
    #                                 "original_txn_amt": amount_db_original,
    #                                 "original_txn_mode": payment_mode_db_original,
    #                                 "refunded_upi_txn_status": upi_status_db_refunded,
    #                                 "refunded_upi_txn_bank_code": upi_bank_code_db_refunded,
    #                                 "refunded_upi_txn_type": upi_txn_type_db_refunded,
    #                                 "original_upi_txn_status": upi_status_db_original,
    #                                 "original_upi_txn_bank_code": upi_bank_code_db_original,
    #                                 "original_upi_txn_type": upi_txn_type_db_original,
    #                                 }
    #             logger.debug(f"actual_db_values : {actual_db_values} for the test case {testcase_id}")
    #
    #             Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
    #         except Exception as e:
    #             Configuration.perform_db_val_exception(testcase_id, e)
    #         logger.info(f"Completed DB validation for the test case : {testcase_id}")
    #
    #     # -----------------------------------------End of DB Validation---------------------------------------
    #
    #     # -----------------------------------------Start of Portal Validation---------------------------------
    #     if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
    #         logger.info(f"Started Portal validation for the test case : {testcase_id}")
    #         try:
    #             expected_portal_values = {}
    #
    #             actual_portal_values = {}
    #
    #             Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
    #                                             actualPortal=actual_portal_values)
    #         except Exception as e:
    #             ReportProcessor.capture_ss_when_portal_val_exe_failed()
    #             print("Portal Validation failed due to exception - " + str(e))
    #             logger.exception(f"Portal Validation failed due to exception : {e}")
    #             GlobalVariables.bool_val_exe = False
    #             GlobalVariables.str_portal_val_result = 'Fail'
    #         logger.info(f"Completed Portal validation for the test case : {testcase_id}")
    #
    #     # -----------------------------------------End of Portal Validation---------------------------------------
    #
    #     # -----------------------------------------Start of ChargeSlip Validation---------------------------------
    #     if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
    #         logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
    #         try:
    #             date = datetime.today().strftime('%Y-%m-%d')
    #             expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
    #                                'RRN': str(rrn_original),
    #                                'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
    #             receipt_validator.perform_charge_slip_validations(txn_id_original,
    #                                                               {"username": app_username, "password": app_password},
    #                                                               expected_values)
    #
    #         except Exception as e:
    #             Configuration.perform_charge_slip_val_exception(testcase_id, e)
    #         logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
    #
    #     # -----------------------------------------End of ChargeSlip Validation---------------------------------------
    #     GlobalVariables.time_calc.validation.end()
    #     logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
    #     logger.info(f"Completed Validation for the test case : {testcase_id}")
    #         # -------------------------------------------End of Validation---------------------------------------------
    # finally:
    #     Configuration.executeFinallyBlock(testcase_id)
    #
    #
    #


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_076():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Collect_Refund_Decimal_via_API_HDFC
    Sub Feature Description: Verification of a upi collect refund with decimal value using api for HDFC
    TC naming code description:
    100: Payment Method
    103: RemotePay
    076: TC076
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 299
            partial_refunded_amount = 149.5
            full_refund_amount = 149.5
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            paymentLinkUrl = response['paymentLink']
            ui_driver.get(paymentLinkUrl)
            remotePayUpiCollectTxn = remotePayTxnPage(ui_driver)
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

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "'"
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
            logger.debug(f"Fetching created_time from db query : {created_time_original} ")


            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_upi_mc_id = result['id'].values[0]
            logger.debug(f"Fetching original_upi_mc_id from db query : {original_upi_mc_id} ")
            original_mid = result['mid'].values[0]
            logger.debug(f"Fetching original_mid from db query : {original_mid} ")
            original_tid = result['tid'].values[0]
            logger.debug(f"Fetching original_tid from db query : {original_tid} ")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": partial_refunded_amount,
                                                                    "originalTransactionId": str(original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(
                original_txn_id) + "'"
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

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": full_refund_amount,
                                                                    "originalTransactionId": str(original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(
                f"Response received from refund api when refund amount is greater than original amount : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(
                original_txn_id) + "' order by created_time limit 1"
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
                original_date_and_time = date_time_converter.to_app_format(created_time_original)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED_REFUNDED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": original_txn_id,
                    "txn_id_2": partially_refunded_txn_id,
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_amt_2": "{:.2f}".format(partial_refunded_amount),
                    "customer_name": original_customer_name,
                    "customer_name_2": original_customer_name,
                    "payer_name": original_payer_name,
                    "payer_name_2": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(original_rrn),
                    "rrn_2": str(partially_refunded_rrn),
                    "auth_code": original_auth_code,
                    "auth_code_2": partially_refunded_auth_code,
                    "date_2": date_and_time,
                    "date": original_date_and_time,

                    "pmt_status_3": "STATUS:REFUNDED",
                    "pmt_mode_3": "UPI",
                    "settle_status_3": "SETTLED",
                    "txn_id_3": fully_refunded_txn_id,
                    "txn_amt_3": "{:.2f}".format(full_refund_amount),
                    "customer_name_3": original_customer_name,
                    "payer_name_3": original_payer_name,
                    "pmt_msg_3": "PAYMENT VOIDED/REFUNDED",
                    "rrn_3": str(fully_refunded_rrn),
                    "auth_code_3": fully_refunded_auth_code
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
                logger.debug(f"Fetching txn_id from txn history for the txn : {partially_refunded_txn_id}, {app_rrn_refunded}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {partially_refunded_txn_id}, {app_date_and_time}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_auth_code_refunded = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {partially_refunded_txn_id}, {app_auth_code_refunded}")
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

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {original_txn_id}, {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_original}")
                app_original_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id : {app_original_date_and_time}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(fully_refunded_txn_id)
                fully_refunded_app_rrn = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {fully_refunded_txn_id}, {fully_refunded_app_rrn}")
                fully_refunded_app_auth_code = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {fully_refunded_txn_id}, {fully_refunded_app_auth_code}")
                fully_refunded_app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {fully_refunded_app_payment_status}")
                fully_refunded_app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {fully_refunded_app_payment_mode}")
                fully_refunded_app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {fully_refunded_app_txn_id}")
                fully_refunded_app_payment_amt = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {fully_refunded_app_payment_amt}")
                fully_refunded_app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {fully_refunded_app_settlement_status}")
                fully_refunded_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {fully_refunded_payment_msg}")
                fully_refunded_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {fully_refunded_txn_id}, {fully_refunded_customer_name}")

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
                    "customer_name": original_customer_name,
                    "customer_name_2": original_customer_name,
                    "payer_name": original_payer_name,
                    "payer_name_2": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "rrn_2": str(app_rrn_refunded),
                    "auth_code": app_auth_code_original,
                    "auth_code_2": app_auth_code_refunded,
                    "date_2": app_date_and_time,
                    "date": app_original_date_and_time,

                    "pmt_status_3": fully_refunded_app_payment_status,
                    "pmt_mode_3": fully_refunded_app_payment_mode,
                    "settle_status_3": fully_refunded_app_settlement_status,
                    "txn_id_3": fully_refunded_app_txn_id,
                    "txn_amt_3":str(fully_refunded_app_payment_amt),
                    "customer_name_3": fully_refunded_customer_name,
                    "payer_name_3": original_payer_name,
                    "pmt_msg_3": fully_refunded_payment_msg,
                    "rrn_3": str(fully_refunded_app_rrn),
                    "auth_code_3": fully_refunded_app_auth_code
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

                refunded_date_time = date_time_converter.db_datetime(partially_refunded_posting_date)
                original_date_time = date_time_converter.db_datetime(created_time_original)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": str(amount),
                    "txn_amt_2": float(partial_refunded_amount),
                    "customer_name": original_customer_name,
                    "customer_name_2": original_customer_name,
                    "payer_name": original_payer_name,
                    "payer_name_2": original_payer_name,
                    "order_id": order_id,
                    "rrn": str(original_rrn),
                    "rrn_2": str(partially_refunded_rrn),
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": original_txn_type,
                    "mid": original_mid,
                    "tid": original_tid,
                    "org_code": original_org_code_txn,
                    "acquirer_code_2": "HDFC",
                    # "issuer_code_refunded": "HDFC",
                    "txn_type_2": partially_refunded_txn_type,
                    "mid_2": original_mid,
                    "tid_2": original_tid,
                    "org_code_2": original_org_code_txn,
                    "auth_code_2": partially_refunded_auth_code,
                    "auth_code": original_auth_code,
                    "date_2": refunded_date_time,
                    "date": original_date_time,

                    "pmt_status_3": "REFUNDED",
                    "pmt_state_3": "REFUNDED",
                    "pmt_mode_3": "UPI",
                    "settle_status_3": "SETTLED",
                    "txn_amt_3": float(full_refund_amount),
                    "customer_name_3": original_customer_name,
                    "payer_name_3": original_payer_name,
                    "rrn_3": str(fully_refunded_rrn),
                    "acquirer_code_3": "HDFC",
                    "txn_type_3": fully_refunded_txn_type,
                    "mid_3": original_mid,
                    "tid_3": original_tid,
                    "org_code_3": original_org_code_txn,
                    "auth_code_3": fully_refunded_auth_code,

                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
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
                date_api_original = response["postingDate"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": partially_refunded_txn_id})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = float(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                rrn_api_refunded = response["rrNumber"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                auth_code_api_refunded = response["authCode"]
                date_api_refunded = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": fully_refunded_txn_id})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                api_status_full_refund = response["status"]
                api_payment_mode_full_refund = response["paymentMode"]
                api_state_full_refund = response["states"][0]
                api_settlement_status_full_refund = response["settlementStatus"]
                api_acquirer_code_full_refund = response["acquirerCode"]
                api_org_code_full_refund = response["orgCode"]
                api_mid_full_refund = response["mid"]
                api_tid_full_refund = response["tid"]
                api_txn_type_full_refund = response["txnType"]
                api_auth_code_full_refund = response["authCode"]
                api_customer_name_full_refund = response["customerName"]
                api_payer_name_full_refund = response["payerName"]

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
                    "txn_amt_2": float(amount_api_refunded),
                    "customer_name": original_customer_name,
                    "customer_name_2": original_customer_name,
                    "payer_name": original_payer_name,
                    "payer_name_2": original_payer_name,
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
                    # "issuer_code_refunded": issuer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "auth_code_2": auth_code_api_refunded,
                    "auth_code": auth_code_api_original,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),

                    "pmt_status_3": api_status_full_refund,
                    "pmt_state_3": api_state_full_refund,
                    "pmt_mode_3": api_payment_mode_full_refund,
                    "settle_status_3": api_settlement_status_full_refund,
                    "txn_amt_3": float(full_refund_amount),
                    "customer_name_3": api_customer_name_full_refund,
                    "payer_name_3": api_payer_name_full_refund,
                    "rrn_3": str(fully_refunded_rrn),
                    "acquirer_code_3": api_acquirer_code_full_refund,
                    "txn_type_3": api_txn_type_full_refund,
                    "mid_3": api_mid_full_refund,
                    "tid_3": api_tid_full_refund,
                    "org_code_3": api_org_code_full_refund,
                    "auth_code_3": api_auth_code_full_refund,
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
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": float(partial_refunded_amount),
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "bank_code": "HDFC",
                    "bank_code_2": "HDFC",
                    # "original_pmt_gateway": "HDFC",
                    # "refunded_pmt_gateway": "HDFC",
                    "upi_txn_type": "COLLECT",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "HDFC",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id": original_upi_mc_id,
                    "upi_mc_id_2": original_upi_mc_id,
                    "mid": original_mid,
                    "tid": original_tid,
                    "mid_2": original_mid,
                    "tid_2": original_tid,

                    "pmt_status_3": "REFUNDED",
                    "pmt_state_3": "REFUNDED",
                    "pmt_mode_3": "UPI",
                    "txn_amt_3": float(full_refund_amount),
                    "upi_txn_status_3": "REFUND",
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "upi_txn_type_3": "REFUND",
                    "upi_bank_code_3": "HDFC",
                    "upi_mc_id_3": original_upi_mc_id,
                    "mid_3": original_mid,
                    "tid_3": original_tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + partially_refunded_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = float(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + partially_refunded_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                bank_code_db_refunded = result["bank_code"].iloc[0]

                query = "select * from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + fully_refunded_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_full_refund = result["status"].iloc[0]
                payment_mode_db_full_refund = result["payment_mode"].iloc[0]
                amount_db_full_refund = float(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_full_refund = result["state"].iloc[0]
                acquirer_code_db_full_refund = result["acquirer_code"].iloc[0]
                settlement_status_db_full_refund = result["settlement_status"].iloc[0]
                tid_db_full_refund = result['tid'].values[0]
                mid_db_full_refund = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + fully_refunded_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_txn_type_db_full_refund = result["txn_type"].iloc[0]
                upi_mc_id_db_full_refund = result["upi_mc_id"].iloc[0]
                bank_code_db_full_refund = result["bank_code"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": float(amount_db_refunded),
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db_original,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db_original,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db_original,
                    "bank_code_2": bank_code_db_refunded,
                    # "original_pmt_gateway": payment_gateway_db_original,
                    # "refunded_pmt_gateway": payment_gateway_db_refunded,
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

                    "pmt_status_3": status_db_full_refund,
                    "pmt_state_3": state_db_full_refund,
                    "pmt_mode_3": payment_mode_db_full_refund,
                    "txn_amt_3": float(amount_db_full_refund),
                    "upi_txn_status_3": upi_txn_type_db_full_refund,
                    "settle_status_3": settlement_status_db_full_refund,
                    "acquirer_code_3": acquirer_code_db_full_refund,
                    "upi_txn_type_3": upi_txn_type_db_full_refund,
                    "upi_bank_code_3": bank_code_db_full_refund,
                    "upi_mc_id_3": upi_mc_id_db_full_refund,
                    "mid_3": mid_db_full_refund,
                    "tid_3": tid_db_full_refund,
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
                expected_portal_values = {"refunded_pmt_state": "Refunded", "original_pmt_mode": "UPI",
                                          "original_pmt_amt": str(amount),
                                          "original_pmt_state": "Authorized Refunded",
                                          "Amount Original": str(partial_refunded_amount), "refunded_pmt_mode": "UPI"}

                logger.debug(f"expected_portal_values : {expected_portal_values} for the testcase_id {testcase_id}")

                driver_ui = TestSuiteSetup.initialize_portal_driver()

                login_page_portal = PortalLoginPage(driver_ui)

                logger.info(f"Logging in Portal using username : {portal_username}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(driver_ui)
                home_page_portal.search_merchant_name(str(org_code))
                logger.info(f"Switching to merchant : {org_code}")
                home_page_portal.click_switch_button(org_code)
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(driver_ui)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(
                    partially_refunded_txn_id)
                portal_txn_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amt = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(original_txn_id)
                portal_txn_type_original = portal_values_dict['Type']
                portal_status_original = portal_values_dict['Status']
                portal_amt_original = portal_values_dict['Total Amount']
                portal_username_original = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")

                actual_portal_values = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                        "Payment amount": str(portal_amt.split('.')[1]),
                                        "Payment Status Original": portal_status_original,
                                        "Amount Original": str(portal_amt_original.split('.')[1]),
                                        "Payment Mode Original": portal_txn_type_original}

                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(partially_refunded_posting_date)
                expected_chargeslip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(fully_refunded_rrn),
                                              'BASE AMOUNT:': "Rs." + str(full_refund_amount) + "0",
                                              'date': txn_date,
                                              'time': txn_time,
                                              'AUTH CODE': fully_refunded_auth_code}

                logger.debug(
                    f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(fully_refunded_txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_chargeslip_values)


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