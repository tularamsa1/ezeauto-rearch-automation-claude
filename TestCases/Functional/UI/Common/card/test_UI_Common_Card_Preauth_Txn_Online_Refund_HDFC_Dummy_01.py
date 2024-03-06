import random
import re
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.mpos.app_online_refund_page import RefundPage
from PageFactory.sa.app_card_page import CardPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_03_017():
    """
    Sub Feature Code: UI_Common_Card_Preauth_Txn_Confirm_Online_Refund_Txn_HDFC_Dummy_VISA_CreditCard_without_pin_417666
    Sub Feature Description: Performing the preauth txn confirm refund online transaction via HDFC Dummy PG using VISA
    Credit card  (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 03: PreAuth, 017: TC017
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["onlineRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["preAuthOption"] = "1"
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(1, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.click_on_pre_auth()
            home_page.enter_amt_order_no_and_device_serial_for_pre_auth(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype(text="CTLS_VISA_CREDIT_417666")
            logger.debug(f"selected the card type as : CTLS_VISA_CREDIT_417666")
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on txn popup for preauth")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_back_btn_in_enter_amt_window()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            original_txn_id = result['id'].values[0]
            logger.debug(f"Fetching original txn_id value from the txn table : {original_txn_id}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=original_txn_id)
            txn_history_page.click_on_confirm_pre_auth()
            logger.debug(f"Clicked on confirm pre_auth button")
            txn_history_page.click_on_confirmation_btn_for_amt(amount=amount)
            logger.debug(f"Entered the confirm pre_auth amount")
            card_page = CardPage(app_driver)
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on confirm pre_auth popup")
            txn_history_page.click_back_Btn_transaction_details()
            txn_history_page.click_back_Btn()

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")

            home_page.perform_online_refund(password=app_password, card_last_four_digit=card_last_four_digit_db, device_serial=device_serial)
            logger.debug(f"to refund selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype(text="CTLS_VISA_CREDIT_417666")
            logger.debug(f"to refund selected the card type as : CTLS_VISA_CREDIT_417666")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where id='{original_txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for original txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for original txn : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for original txn : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for original txn : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for original txn : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for original txn : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for original txn : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for original txn : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for original txn : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for original txn : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for original txn : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for original txn : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for original txn : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table for original txn : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for original txn : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for original txn : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for original txn : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for original txn : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for original txn : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table for original txn : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for original txn : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for original txn : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for original txn : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for original txn : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for original txn : {card_txn_type_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for original txn : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table for original txn: {posting_date}")

            query = f"select * from txn where orig_txn_id='{original_txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for confirm preauth : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            cnf_preauth_txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table, for confirm preauth : {cnf_preauth_txn_id} ")
            cnf_preauth_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for confirm preauth : {cnf_preauth_auth_code}")
            cnf_preauth_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for confirm preauth : {cnf_preauth_created_time}")
            cnf_preauth_amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for confirm preauth : {cnf_preauth_amount_db}")
            cnf_preauth_payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for confirm preauth : {cnf_preauth_payment_mode_db}")
            cnf_preauth_payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for confirm preauth : {cnf_preauth_payment_status_db}")
            cnf_preauth_payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for confirm preauth : {cnf_preauth_payment_state_db}")
            cnf_preauth_acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for confirm preauth : {cnf_preauth_acquirer_code_db}")
            cnf_preauth_mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for confirm preauth : {cnf_preauth_mid_db}")
            cnf_preauth_tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for confirm preauth : {cnf_preauth_tid_db}")
            cnf_preauth_payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for confirm preauth : {cnf_preauth_payment_gateway_db}")
            cnf_preauth_rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for confirm preauth : {cnf_preauth_rrn}")
            cnf_preauth_settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for confirm preauth : {cnf_preauth_settlement_status_db}")
            cnf_preauth_device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table for confirm preauth : {cnf_preauth_device_serial_db}")
            cnf_preauth_merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for confirm preauth : {cnf_preauth_merchant_code_db}")
            cnf_preauth_payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for confirm preauth : {cnf_preauth_payment_card_brand_db}")
            cnf_preauth_payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn tablefor confirm preauth  : {cnf_preauth_payment_card_type_db}")
            cnf_preauth_batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for confirm preauth : {cnf_preauth_batch_number_db}")
            cnf_preauth_payment_card_type = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table, for confirm preauth : {cnf_preauth_payment_card_type}")
            cnf_preauth_order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for confirm preauth : {cnf_preauth_order_id_db}")
            cnf_preauth_issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table for confirm preauth : {cnf_preauth_issuer_code_db}")
            cnf_preauth_org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for confirm preauth : {cnf_preauth_org_code_db}")
            cnf_preauth_payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for confirm preauth : {cnf_preauth_payment_card_bin_db}")
            cnf_preauth_terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for confirm preauth : {cnf_preauth_terminal_info_id_db}")
            cnf_preauth_txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for confirm preauth : {cnf_preauth_txn_type_db}")
            cnf_preauth_card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for confirm preauth : {cnf_preauth_card_txn_type_db}")
            cnf_preauth_card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(
                f"Fetching card last four digit from txn table, for confirm preauth : {cnf_preauth_card_last_four_digit_db}")
            cnf_preauth_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for confirm preauth : {cnf_preauth_merchant_name}")
            cnf_preauth_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table for confirm preauth: {cnf_preauth_posting_date}")

            query = f"select * from txn where org_code='{org_code}' and orig_txn_id = '{cnf_preauth_txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for refunded txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            refund_txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table, for refunded txn : {refund_txn_id} ")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table, for refunded txn : {refund_auth_code}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table, for refunded txn : {refund_created_time}")
            refund_amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table, for refunded txn : {refund_amount_db}")
            refund_payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table, for refunded txn : {refund_payment_mode_db}")
            refund_payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table, for refunded txn : {refund_payment_status_db}")
            refund_payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table, for refunded txn : {refund_payment_state_db}")
            refund_acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table, for refunded txn : {refund_acquirer_code_db}")
            refund_mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table, for refunded txn : {refund_mid_db}")
            refund_tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table, for refunded txn : {refund_tid_db}")
            refund_payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table, for refunded txn : {refund_payment_gateway_db}")
            refund_rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table, for refunded txn : {refund_rrn}")
            refund_settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table, for refunded txn : {refund_settlement_status_db}")
            refund_device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table, for refunded txn : {refund_device_serial_db}")
            refund_merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table, for refunded txn : {refund_merchant_code_db}")
            refund_payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table, for refunded txn : {refund_payment_card_brand_db}")
            refund_payment_card_type = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table, for refunded txn : {refund_payment_card_type}")
            refund_batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table, for refunded txn : {refund_batch_number_db}")
            refund_order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table, for refunded txn : {refund_order_id_db}")
            refund_issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table, for refunded txn : {refund_issuer_code_db}")
            refund_org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table, for refunded txn : {refund_org_code_db}")
            refund_payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table, for refunded txn : {refund_payment_card_bin_db}")
            refund_terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table, for refunded txn : {refund_terminal_info_id_db}")
            refund_txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table, for refunded txn : {refund_txn_type_db}")
            refund_card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table, for refunded txn : {refund_card_txn_type_db}")
            refund_card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table, for refunded txn : {refund_card_last_four_digit_db}")
            refund_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table, for refunded txn : {refund_merchant_name}")
            refund_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table for refunded txn: {refund_posting_date}")
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
                # --------------------------------------------------------------------------------------------
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=posting_date)
                cnf_date_and_time_app = date_time_converter.to_app_format(posting_date_db=cnf_preauth_posting_date)
                refund_date_and_time_app = date_time_converter.to_app_format(posting_date_db=refund_posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": original_txn_id,
                    "pmt_status": "CNF_PRE_AUTH",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "card_type_desc": "*0018 CTLS",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": cnf_preauth_txn_id,
                    "pmt_status_2": "AUTHORIZED REFUNDED",
                    "rrn_2": str(cnf_preauth_rrn),
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "settle_status_2": "SETTLED",
                    "auth_code_2": cnf_preauth_auth_code,
                    "date_2": cnf_date_and_time_app,
                    "device_serial_2": cnf_preauth_device_serial_db,
                    "mid_2": cnf_preauth_mid_db,
                    "tid_2": cnf_preauth_tid_db,
                    "batch_number_2": cnf_preauth_batch_number_db,
                    "card_type_desc_2": "*0018 CTLS",
                    "txn_amt_3": "{:,.2f}".format(amount),
                    "pmt_mode_3": "CARD",
                    "txn_id_3": refund_txn_id,
                    "pmt_status_3": "REFUNDED",
                    "rrn_3": refund_rrn,
                    "order_id_3": order_id,
                    "pmt_msg_3": "REFUND SUCCESSFUL",
                    "settle_status_3": "PENDING",
                    "auth_code_3": refund_auth_code,
                    "date_3": refund_date_and_time_app,
                    "device_serial_3": device_serial,
                    "mid_3": refund_mid_db,
                    "tid_3": refund_tid_db,
                    "batch_number_3": refund_batch_number_db,
                    "card_type_desc_3": "*0018 CTLS",

                    "or_device_serial": device_serial,
                    "or_amount": "{:,.2f}".format(amount),
                    "or_card_type_desc": "*0018 CTLS",
                    "or_date_time": cnf_date_and_time_app,
                    "or_status": "AUTHORIZED_REFUNDED",
                    "or_auth_code_name": cnf_preauth_auth_code,
                    "or_mid": cnf_preauth_mid_db,
                    "or_tid": cnf_preauth_tid_db,
                    "or_rrn": cnf_preauth_rrn,
                    "or_batch_number": cnf_preauth_batch_number_db,
                    "or_ref1": cnf_preauth_order_id_db,
                    "or_device_serial_2": device_serial,
                    "or_amount_2": "{:,.2f}".format(amount),
                    "or_card_type_desc_2": "*0018 CTLS",
                    "or_date_time_2": refund_date_and_time_app,
                    "or_status_2": "REFUNDED",
                    "or_ref3_2": device_serial,
                    "or_auth_code_name_2": refund_auth_code,
                    "or_mid_2": refund_mid_db,
                    "or_tid_2": refund_tid_db,
                    "or_rrn_2": refund_rrn,
                    "or_batch_number_2": refund_batch_number_db,
                    "or_ref1_2": refund_order_id_db,
                    "or_device_serial_3": device_serial,
                    "or_amount_3": "{:,.2f}".format(amount),
                    "or_card_type_desc_3": "*0018 CTLS",
                    "or_date_time_3": date_and_time_app,
                    "or_status_3": "CNF_PRE_AUTH",
                    "or_auth_code_name_3": auth_code,
                    "or_mid_3": mid_db,
                    "or_tid_3": tid_db,
                    "or_rrn_3": rrn,
                    "or_batch_number_3": batch_number_db,
                    "or_ref1_3": order_id_db
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                refund_page = RefundPage(driver=app_driver)
                online_refund_txn_data = refund_page.capture_online_refund_txn_data(password=app_password,
                                                                                    card_last_four_digit=card_last_four_digit_db,
                                                                                    customer_name=None,
                                                                                    txn_type="preauth")
                logger.debug(f"captured transaction data from refund page: {online_refund_txn_data}")
                or_amount = re.search(r'[0-9,\.]+', online_refund_txn_data["or_amount"].split(" ")[0])
                or_amount = or_amount.group()
                or_amount_2 = re.search(r'[0-9,\.]+', online_refund_txn_data["or_amount_2"].split(" ")[0])
                or_amount_2 = or_amount_2.group()
                or_amount_3 = re.search(r'[0-9,\.]+', online_refund_txn_data["or_amount_3"].split(" ")[0])
                or_amount_3 = or_amount_3.group()

                home_page.wait_for_home_page_load()
                GlobalVariables.bool_validate_multiple_txns = False
                home_page.click_on_history()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=original_txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching payment mode from txn history for the txn : {original_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the txn : {original_txn_id}, {payment_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(
                    f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(
                    f"Fetching txn payment msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the txn : {original_txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(
                    f"Fetching date_time from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for the txn : {original_txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the txn : {original_txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the txn : {original_txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the txn : {original_txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the txn : {original_txn_id}, {app_card_type_desc}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=cnf_preauth_txn_id)
                app_amount_cnf_preauth = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {cnf_preauth_txn_id}, {app_amount_cnf_preauth}")
                payment_mode_cnf_preauth = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {payment_mode_cnf_preauth}")
                app_txn_id_cnf_preauth = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_txn_id_cnf_preauth}")
                payment_status_cnf_preauth = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {payment_status_cnf_preauth}")
                app_rrn_cnf_preauth = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_rrn_cnf_preauth}")
                app_order_id_cnf_preauth = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_order_id_cnf_preauth}")
                app_payment_msg_cnf_preauth = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_payment_msg_cnf_preauth}")
                app_settlement_status_cnf_preauth = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_settlement_status_cnf_preauth}")
                app_auth_code_cnf_preauth = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_auth_code_cnf_preauth}")
                app_date_and_time_cnf_preauth = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_date_and_time_cnf_preauth}")
                app_device_serial_cnf_preauth = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_device_serial_cnf_preauth}")
                app_mid_cnf_preauth = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_mid_cnf_preauth}")
                app_tid_cnf_preauth = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_tid_cnf_preauth}")
                app_batch_number_cnf_preauth = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for confirm preauth txn : {cnf_preauth_txn_id}, {app_batch_number_cnf_preauth}")
                app_card_type_desc_cnf_preauth = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for confirm preauth txn : {cnf_preauth_txn_id}, {app_card_type_desc_cnf_preauth}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history, for refunded txn : {refund_txn_id}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history, for refunded txn : {refund_txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history, for refunded txn : {refund_txn_id}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history, for refunded txn : {refund_txn_id}, {payment_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history, for refunded txn : {refund_txn_id}, {app_rrn_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history, for refunded txn : {refund_txn_id}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history, for refunded txn : {refund_txn_id}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history, for refunded txn : {refund_txn_id}, {app_settlement_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for refunded txn : {refund_txn_id}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for refunded txn : {refund_txn_id}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for refunded txn : {refund_txn_id}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for refunded txn : {refund_txn_id}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for refunded txn : {refund_txn_id}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for refunded txn : {refund_txn_id}, {app_batch_number_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for refunded txn : {refund_txn_id}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rrn": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "txn_amt_2": app_amount_cnf_preauth.split(' ')[1],
                    "pmt_mode_2": payment_mode_cnf_preauth,
                    "txn_id_2": app_txn_id_cnf_preauth,
                    "pmt_status_2": payment_status_cnf_preauth.split(':')[1],
                    "rrn_2": app_rrn_cnf_preauth,
                    "order_id_2": app_order_id_cnf_preauth,
                    "pmt_msg_2": app_payment_msg_cnf_preauth,
                    "settle_status_2": app_settlement_status_cnf_preauth,
                    "auth_code_2": app_auth_code_cnf_preauth,
                    "date_2": app_date_and_time_cnf_preauth,
                    "device_serial_2": app_device_serial_cnf_preauth,
                    "mid_2": app_mid_cnf_preauth,
                    "tid_2": app_tid_cnf_preauth,
                    "batch_number_2": app_batch_number_cnf_preauth,
                    "card_type_desc_2": app_card_type_desc_cnf_preauth,
                    "txn_amt_3": app_amount_2.split(' ')[1],
                    "pmt_mode_3": payment_mode_2,
                    "txn_id_3": app_txn_id_2,
                    "pmt_status_3": payment_status_2.split(':')[1],
                    "rrn_3": app_rrn_2,
                    "order_id_3": app_order_id_2,
                    "pmt_msg_3": app_payment_msg_2,
                    "settle_status_3": app_settlement_status_2,
                    "auth_code_3": app_auth_code_2,
                    "date_3": app_date_and_time_2,
                    "device_serial_3": app_device_serial_2,
                    "mid_3": app_mid_2,
                    "tid_3": app_tid_2,
                    "batch_number_3": app_batch_number_2,
                    "card_type_desc_3": app_card_type_desc_2,

                    "or_device_serial": online_refund_txn_data["or_device_serial"],
                    "or_amount": or_amount,
                    "or_card_type_desc": online_refund_txn_data["or_card_type_desc"],
                    "or_date_time": online_refund_txn_data["or_date_time"],
                    "or_status": online_refund_txn_data["or_status"],
                    "or_auth_code_name": online_refund_txn_data["or_auth_code_name"],
                    "or_mid": online_refund_txn_data["or_mid"],
                    "or_tid": online_refund_txn_data["or_tid"],
                    "or_rrn": online_refund_txn_data["or_rrn"],
                    "or_batch_number": online_refund_txn_data["or_batch_number"],
                    "or_ref1": online_refund_txn_data["or_ref1"],
                    "or_device_serial_2": online_refund_txn_data["or_device_serial_2"],
                    "or_amount_2": or_amount_2,
                    "or_card_type_desc_2": online_refund_txn_data["or_card_type_desc_2"],
                    "or_date_time_2": online_refund_txn_data["or_date_time_2"],
                    "or_status_2": online_refund_txn_data["or_status_2"],
                    "or_ref3_2": online_refund_txn_data["or_ref3_2"],
                    "or_auth_code_name_2": online_refund_txn_data["or_auth_code_name_2"],
                    "or_mid_2": online_refund_txn_data["or_mid_2"],
                    "or_tid_2": online_refund_txn_data["or_tid_2"],
                    "or_rrn_2": online_refund_txn_data["or_rrn_2"],
                    "or_batch_number_2": online_refund_txn_data["or_batch_number_2"],
                    "or_ref1_2": online_refund_txn_data["or_ref1_2"],
                    "or_device_serial_3": online_refund_txn_data["or_device_serial_3"],
                    "or_amount_3": or_amount_3,
                    "or_card_type_desc_3": online_refund_txn_data["or_card_type_desc_3"],
                    "or_date_time_3": online_refund_txn_data["or_date_time_3"],
                    "or_status_3": online_refund_txn_data["or_status_3"],
                    "or_auth_code_name_3": online_refund_txn_data["or_auth_code_name_3"],
                    "or_mid_3": online_refund_txn_data["or_mid_3"],
                    "or_tid_3": online_refund_txn_data["or_tid_3"],
                    "or_rrn_3": online_refund_txn_data["or_rrn_3"],
                    "or_batch_number_3": online_refund_txn_data["or_batch_number_3"],
                    "or_ref1_3": online_refund_txn_data["or_ref1_3"]
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                cnf_date_and_time_api = date_time_converter.db_datetime(date_from_db=cnf_preauth_created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=refund_created_time)
                expected_api_values = {
                    "pmt_status": "CNF_PRE_AUTH",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "PRE_AUTH",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "CTLS",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0018",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "display_pan": "0018",
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "REFUNDED",
                    "rrn_2": str(cnf_preauth_rrn),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "CONF_PRE_AUTH",
                    "auth_code_2": cnf_preauth_auth_code,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": cnf_date_and_time_api,
                    "username_2": app_username,
                    "txn_id_2": cnf_preauth_txn_id,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "card_txn_type_2": "CTLS",
                    "batch_number_2": cnf_preauth_batch_number_db,
                    "card_last_four_digit_2": "0018",
                    "external_ref_2": order_id,
                    "merchant_name_2": cnf_preauth_merchant_name,
                    "pmt_card_bin_2": "417666",
                    "display_pan_2": "0018",
                    "device_serial_2": device_serial,
                    "pmt_status_3": "REFUNDED",
                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "CARD",
                    "pmt_state_3": "AUTHORIZED",
                    "rrn_3": str(refund_rrn),
                    "settle_status_3": "PENDING",
                    "acquirer_code_3": "HDFC",
                    "txn_type_3": "REFUND",
                    "auth_code_3": refund_auth_code,
                    "mid_3": mid,
                    "tid_3": tid,
                    "org_code_3": org_code,
                    "date_3": date_and_time_api_2,
                    "username_3": app_username,
                    "txn_id_3": refund_txn_id,
                    "pmt_card_brand_3": "VISA",
                    "pmt_card_type_3": "CREDIT",
                    "card_txn_type_3": "CTLS",
                    "batch_number_3": refund_batch_number_db,
                    "card_last_four_digit_3": "0018",
                    "external_ref_3": order_id,
                    "merchant_name_3": refund_merchant_name,
                    "pmt_card_bin_3": "417666",
                    "display_pan_3": "0018",
                    "issuer_code_3": issuer_code,
                    "device_serial_3": device_serial
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status from response : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount from response : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode from response : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state from response : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn from response : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement status from response : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer code from response : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org code from response : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid from response : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid from response : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction type from response : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth code from response : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device serial from response : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username from response : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction id from response : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment card type from response : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {payment_card_bin_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN from response : {display_pan_api}")

                response_cnf_preauth = [x for x in response["txns"] if x["txnId"] == cnf_preauth_txn_id][0]
                logger.debug(f"Response after filtering data of cnf preauth txn is : {response_cnf_preauth}")
                cnf_preauth_status_api = response_cnf_preauth["status"]
                logger.debug(f"Fetching status from response for cnf preauth txn : {cnf_preauth_status_api}")
                cnf_preauth_amount_api = float(response_cnf_preauth["amount"])
                logger.debug(f"Fetching amount from response for cnf preauth txn : {cnf_preauth_amount_api}")
                cnf_preauth_payment_mode_api = response_cnf_preauth["paymentMode"]
                logger.debug(f"Fetching payment mode from response for cnf preauth txn : {cnf_preauth_payment_mode_api}")
                cnf_preauth_state_api = response_cnf_preauth["states"][0]
                logger.debug(f"Fetching state from response for cnf preauth txn : {cnf_preauth_state_api}")
                cnf_preauth_rrn_api = response_cnf_preauth["rrNumber"]
                logger.debug(f"Fetching rrn from response for cnf preauth txn : {cnf_preauth_rrn_api}")
                cnf_preauth_settlement_status_api = response_cnf_preauth["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for cnf preauth txn : {cnf_preauth_settlement_status_api}")
                cnf_preauth_acquirer_code_api = response_cnf_preauth["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for cnf preauth txn : {cnf_preauth_acquirer_code_api}")
                cnf_preauth_org_code_api = response_cnf_preauth["orgCode"]
                logger.debug(f"Fetching org code from response for cnf preauth txn : {cnf_preauth_org_code_api}")
                cnf_preauth_mid_api = response_cnf_preauth["mid"]
                logger.debug(f"Fetching mid from response for cnf preauth txn : {cnf_preauth_mid_api}")
                cnf_preauth_tid_api = response_cnf_preauth["tid"]
                logger.debug(f"Fetching tid from response for cnf preauth txn : {cnf_preauth_tid_api}")
                cnf_preauth_txn_type_api = response_cnf_preauth["txnType"]
                logger.debug(f"Fetching transaction type from response for cnf preauth txn : {cnf_preauth_txn_type_api}")
                cnf_preauth_auth_code_api = response_cnf_preauth["authCode"]
                logger.debug(f"Fetching auth code from response for cnf preauth txn : {cnf_preauth_auth_code_api}")
                cnf_preauth_date_and_time_api = response_cnf_preauth["createdTime"]
                logger.debug(f"Fetching date and time from response for cnf preauth txn : {cnf_preauth_date_and_time_api}")
                cnf_preauth_device_serial_api = response_cnf_preauth["deviceSerial"]
                logger.debug(f"Fetching device serial from response for cnf preauth txn : {cnf_preauth_device_serial_api}")
                cnf_preauth_username_api = response_cnf_preauth["username"]
                logger.debug(f"Fetching username from response for cnf preauth txn : {cnf_preauth_username_api}")
                cnf_preauth_txn_id_api = response_cnf_preauth["txnId"]
                logger.debug(f"Fetching transaction id from response for cnf preauth txn : {cnf_preauth_txn_id_api}")
                cnf_preauth_payment_card_brand_api = response_cnf_preauth["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for cnf preauth txn : {cnf_preauth_payment_card_brand_api}")
                cnf_preauth_payment_card_type_api = response_cnf_preauth["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for cnf preauth txn : {cnf_preauth_payment_card_type_api}")
                cnf_preauth_card_txn_type_api = response_cnf_preauth["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for cnf preauth txn : {cnf_preauth_card_txn_type_api}")
                cnf_preauth_batch_number_api = response_cnf_preauth["batchNumber"]
                logger.debug(f"Fetching batch number from response for cnf preauth txn : {cnf_preauth_batch_number_api}")
                cnf_preauth_card_last_four_digit_api = response_cnf_preauth["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for cnf preauth txn : {cnf_preauth_card_last_four_digit_api}")
                cnf_preauth_external_ref_number_api = response_cnf_preauth["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for cnf preauth txn : {cnf_preauth_external_ref_number_api}")
                cnf_preauth_merchant_name_api = response_cnf_preauth["merchantName"]
                logger.debug(f"Fetching merchant name from response for cnf preauth txn : {cnf_preauth_merchant_name_api}")
                cnf_preauth_payment_card_bin_api = response_cnf_preauth["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for cnf preauth txn : {cnf_preauth_payment_card_bin_api}")
                cnf_preauth_display_pan_api = response_cnf_preauth["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for cnf preauth txn : {cnf_preauth_display_pan_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status from response for refunded txn : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount from response for refunded txn : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment mode from response for refunded txn : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state from response for refunded txn : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn from response for refunded txn : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for refunded txn : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for refunded txn : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org code from response for refunded txn : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid from response for refunded txn : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid from response for refunded txn : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction type from response for refunded txn : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth code from response for refunded txn : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date and time from response for refunded txn : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username from response for refunded txn : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction id from response for refunded txn : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for refunded txn : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for refunded txn : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for refunded txn : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch number from response for refunded txn : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for refunded txn : {card_last_four_digit_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for refunded txn : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant name from response for refunded txn : {merchant_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for refunded txn : {payment_card_bin_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for refunded txn : {display_pan_api_2}")
                device_serial_api_2 = response_2["deviceSerial"]
                logger.debug(f"Fetching device serial from response for refunded txn : {device_serial_api_2}")
                issuer_code_api_2 = response_2["issuerCode"]
                logger.debug(f"Fetching issuer code from response for refunded txn : {issuer_code_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "device_serial": device_serial_api,
                    "username": username_api,
                    "txn_id": txn_id_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_txn_type": card_txn_type_api,
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "external_ref": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "display_pan": display_pan_api,
                    "pmt_status_2": cnf_preauth_status_api,
                    "txn_amt_2": cnf_preauth_amount_api,
                    "pmt_mode_2": cnf_preauth_payment_mode_api,
                    "pmt_state_2": cnf_preauth_state_api,
                    "rrn_2": str(cnf_preauth_rrn_api),
                    "settle_status_2": cnf_preauth_settlement_status_api,
                    "acquirer_code_2": cnf_preauth_acquirer_code_api,
                    "txn_type_2": cnf_preauth_txn_type_api,
                    "auth_code_2": cnf_preauth_auth_code_api,
                    "mid_2": cnf_preauth_mid_api,
                    "tid_2": cnf_preauth_tid_api,
                    "org_code_2": cnf_preauth_org_code_api,
                    "date_2": date_time_converter.from_api_to_datetime_format(cnf_preauth_date_and_time_api),
                    "username_2": cnf_preauth_username_api,
                    "txn_id_2": cnf_preauth_txn_id_api,
                    "pmt_card_brand_2": cnf_preauth_payment_card_brand_api,
                    "pmt_card_type_2": cnf_preauth_payment_card_type_api,
                    "card_txn_type_2": cnf_preauth_card_txn_type_api,
                    "batch_number_2": cnf_preauth_batch_number_api,
                    "card_last_four_digit_2": cnf_preauth_card_last_four_digit_api,
                    "external_ref_2": cnf_preauth_external_ref_number_api,
                    "merchant_name_2": cnf_preauth_merchant_name_api,
                    "pmt_card_bin_2": cnf_preauth_payment_card_bin_api,
                    "display_pan_2": cnf_preauth_display_pan_api,
                    "device_serial_2": cnf_preauth_device_serial_api,
                    "pmt_status_3": status_api_2,
                    "txn_amt_3": amount_api_2,
                    "pmt_mode_3": payment_mode_api_2,
                    "pmt_state_3": state_api_2,
                    "rrn_3": str(rrn_api_2),
                    "settle_status_3": settlement_status_api_2,
                    "acquirer_code_3": acquirer_code_api_2,
                    "txn_type_3": txn_type_api_2,
                    "auth_code_3": auth_code_api_2,
                    "mid_3": mid_api_2,
                    "tid_3": tid_api_2,
                    "org_code_3": org_code_api_2,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_3": username_api_2,
                    "txn_id_3": txn_id_api_2,
                    "pmt_card_brand_3": payment_card_brand_api_2,
                    "pmt_card_type_3": payment_card_type_api_2,
                    "card_txn_type_3": card_txn_type_api_2,
                    "batch_number_3": batch_number_api_2,
                    "card_last_four_digit_3": card_last_four_digit_api_2,
                    "external_ref_3": external_ref_number_api_2,
                    "merchant_name_3": merchant_name_api_2,
                    "pmt_card_bin_3": payment_card_bin_api_2,
                    "display_pan_3": display_pan_api_2,
                    "issuer_code_3": issuer_code_api_2,
                    "device_serial_3": device_serial_api_2
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "txn_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "CNF_PRE_AUTH",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "PRE_AUTH",
                    "card_txn_type": "91",
                    "card_last_four_digit": "0018",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "SETTLED",
                    "device_serial_2": device_serial,
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "417666",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "CONF_PRE_AUTH",
                    "card_txn_type_2": "91",
                    "card_last_four_digit_2": "0018",
                    "txn_amt_3": amount,
                    "pmt_mode_3": "CARD",
                    "pmt_status_3": "REFUNDED",
                    "pmt_state_3": "AUTHORIZED",
                    "acquirer_code_3": "HDFC",
                    "mid_3": mid,
                    "tid_3": tid,
                    "pmt_gateway_3": "DUMMY",
                    "settle_status_3": "PENDING",
                    "device_serial_3": device_serial,
                    "merchant_code_3": org_code,
                    "pmt_card_brand_3": "VISA",
                    "pmt_card_type_3": "CREDIT",
                    "order_id_3": order_id,
                    "issuer_code_3": issuer_code,
                    "org_code_3": org_code,
                    "pmt_card_bin_3": "417666",
                    "terminal_info_id_3": terminal_info_id,
                    "txn_type_3": "REFUND",
                    "card_txn_type_3": "91",
                    "card_last_four_digit_3": "0018",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "device_serial": device_serial_db,
                    "merchant_code": merchant_code_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "order_id": order_id_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "txn_amt_2": cnf_preauth_amount_db,
                    "pmt_mode_2": cnf_preauth_payment_mode_db,
                    "pmt_status_2": cnf_preauth_payment_status_db,
                    "pmt_state_2": cnf_preauth_payment_state_db,
                    "acquirer_code_2": cnf_preauth_acquirer_code_db,
                    "mid_2": cnf_preauth_mid_db,
                    "tid_2": cnf_preauth_tid_db,
                    "pmt_gateway_2": cnf_preauth_payment_gateway_db,
                    "settle_status_2": cnf_preauth_settlement_status_db,
                    "device_serial_2": cnf_preauth_device_serial_db,
                    "merchant_code_2": cnf_preauth_merchant_code_db,
                    "pmt_card_brand_2": cnf_preauth_payment_card_brand_db,
                    "pmt_card_type_2": cnf_preauth_payment_card_type,
                    "order_id_2": cnf_preauth_order_id_db,
                    "org_code_2": cnf_preauth_org_code_db,
                    "pmt_card_bin_2": cnf_preauth_payment_card_bin_db,
                    "terminal_info_id_2": cnf_preauth_terminal_info_id_db,
                    "txn_type_2": cnf_preauth_txn_type_db,
                    "card_txn_type_2": cnf_preauth_card_txn_type_db,
                    "card_last_four_digit_2": cnf_preauth_card_last_four_digit_db,
                    "txn_amt_3": refund_amount_db,
                    "pmt_mode_3": refund_payment_mode_db,
                    "pmt_status_3": refund_payment_status_db,
                    "pmt_state_3": refund_payment_state_db,
                    "acquirer_code_3": refund_acquirer_code_db,
                    "mid_3": refund_mid_db,
                    "tid_3": refund_tid_db,
                    "pmt_gateway_3": refund_payment_gateway_db,
                    "settle_status_3": refund_settlement_status_db,
                    "device_serial_3": refund_device_serial_db,
                    "merchant_code_3": refund_merchant_code_db,
                    "pmt_card_brand_3": refund_payment_card_brand_db,
                    "pmt_card_type_3": refund_payment_card_type,
                    "order_id_3": refund_order_id_db,
                    "issuer_code_3": refund_issuer_code_db,
                    "org_code_3": refund_org_code_db,
                    "pmt_card_bin_3": refund_payment_card_bin_db,
                    "terminal_info_id_3": refund_terminal_info_id_db,
                    "txn_type_3": refund_txn_type_db,
                    "card_txn_type_3": refund_card_txn_type_db,
                    "card_last_four_digit_3": refund_card_last_four_digit_db,
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=created_time)
                date_and_time_portal_cnf = date_time_converter.to_portal_format(created_date_db=cnf_preauth_created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                expected_portal_values = {
                    "pmt_status": "CNF_PRE_AUTH",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_and_time_portal,
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": cnf_preauth_txn_id,
                    "auth_code_2": cnf_preauth_auth_code,
                    "rrn_2": cnf_preauth_rrn,
                    "date_time_2": date_and_time_portal_cnf,
                    "pmt_status_3": "REFUNDED",
                    "pmt_type_3": "CARD",
                    "txn_amt_3": "{:,.2f}".format(amount),
                    "username_3": app_username,
                    "txn_id_3": refund_txn_id,
                    "auth_code_3": refund_auth_code,
                    "rrn_3": refund_rrn,
                    "date_time_3": date_and_time_portal_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                date_time = transaction_details[2]['Date & Time']
                transaction_id = transaction_details[2]['Transaction ID']
                total_amount = transaction_details[2]['Total Amount'].split()
                auth_code_portal = transaction_details[2]['Auth Code']
                rr_number = transaction_details[2]['RR Number']
                transaction_type = transaction_details[2]['Type']
                status = transaction_details[2]['Status']
                username = transaction_details[2]['Username']

                date_time_2 = transaction_details[1]['Date & Time']
                transaction_id_2 = transaction_details[1]['Transaction ID']
                total_amount_2 = transaction_details[1]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[1]['Auth Code']
                rr_number_2 = transaction_details[1]['RR Number']
                transaction_type_2 = transaction_details[1]['Type']
                status_2 = transaction_details[1]['Status']
                username_2 = transaction_details[1]['Username']

                date_time_3 = transaction_details[0]['Date & Time']
                transaction_id_3 = transaction_details[0]['Transaction ID']
                total_amount_3 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_3 = transaction_details[0]['Auth Code']
                rr_number_3 = transaction_details[0]['RR Number']
                transaction_type_3 = transaction_details[0]['Type']
                status_3 = transaction_details[0]['Status']
                username_3 = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2,
                    "pmt_status_3": str(status_3),
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "auth_code_3": auth_code_portal_3,
                    "rrn_3": rr_number_3,
                    "date_time_3": date_time_3
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=refund_posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(refund_rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "AUTH CODE": refund_auth_code,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": refund_batch_number_db,
                    "TID": tid
                }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                chargeslip_val_result = receipt_validator.perform_charge_slip_validations(txn_id=refund_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)

                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values_2 = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "AUTH CODE": auth_code,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "SALE",
                    "BATCH NO": batch_number_db,
                    "TID": tid
                }
                logger.debug(f"expected_charge_slip_values for original txn : {expected_charge_slip_values_2}")
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id=original_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values_2)

                if chargeslip_val_result and chargeslip_val_result_2:
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
def test_common_100_115_03_018():
    """
    Sub Feature Code: UI_Common_Card_Preauth_Txn_Confirm_Online_Refund_Txn_HDFC_Dummy_MASTER_CreditCard_without_pin_541333
    Sub Feature Description: Performing the preauth txn confirm refund online transaction via HDFC Dummy PG using MASTER
    Credit card  (bin: 541333)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 03: PreAuth, 018: TC018
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select bank_code from bin_info where bin='541333'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["onlineRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["preAuthOption"] = "1"
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(1, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.click_on_pre_auth()
            home_page.enter_amt_order_no_and_device_serial_for_pre_auth(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : CTLS_MASTER_CREDIT_541333")
            card_page.select_cardtype(text="CTLS_MASTER_CREDIT_541333")
            logger.debug(f"selected the card type as : CTLS_MASTER_CREDIT_541333")
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on txn popup for preauth")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_back_btn_in_enter_amt_window()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            original_txn_id = result['id'].values[0]
            logger.debug(f"Fetching original txn_id value from the txn table : {original_txn_id}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=original_txn_id)
            txn_history_page.click_on_confirm_pre_auth()
            logger.debug(f"Clicked on confirm pre_auth button")
            txn_history_page.click_on_confirmation_btn_for_amt(amount=amount)
            logger.debug(f"Entered the confirm pre_auth amount")
            card_page = CardPage(app_driver)
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on confirm pre_auth popup")
            txn_history_page.click_back_Btn_transaction_details()
            txn_history_page.click_back_Btn()

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")

            home_page.perform_online_refund(password=app_password, card_last_four_digit=card_last_four_digit_db, device_serial=device_serial)
            logger.debug(f"to refund selecting the card type as : CTLS_MASTER_CREDIT_541333")
            card_page.select_cardtype(text="CTLS_MASTER_CREDIT_541333")
            logger.debug(f"to refund selected the card type as : CTLS_MASTER_CREDIT_541333")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where id='{original_txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for original txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for original txn : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for original txn : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for original txn : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for original txn : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for original txn : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for original txn : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for original txn : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for original txn : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for original txn : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for original txn : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for original txn : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for original txn : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table for original txn : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for original txn : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for original txn : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for original txn : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for original txn : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for original txn : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table for original txn : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for original txn : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for original txn : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for original txn : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for original txn : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for original txn : {card_txn_type_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table for original txn : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for original txn : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for original txn : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table for original txn : {posting_date}")

            query = f"select * from txn where orig_txn_id='{original_txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for confirm preauth : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            cnf_preauth_txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table, for confirm preauth : {cnf_preauth_txn_id} ")
            cnf_preauth_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for confirm preauth : {cnf_preauth_auth_code}")
            cnf_preauth_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for confirm preauth : {cnf_preauth_created_time}")
            cnf_preauth_amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for confirm preauth : {cnf_preauth_amount_db}")
            cnf_preauth_payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for confirm preauth : {cnf_preauth_payment_mode_db}")
            cnf_preauth_payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for confirm preauth : {cnf_preauth_payment_status_db}")
            cnf_preauth_payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for confirm preauth : {cnf_preauth_payment_state_db}")
            cnf_preauth_acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for confirm preauth : {cnf_preauth_acquirer_code_db}")
            cnf_preauth_mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for confirm preauth : {cnf_preauth_mid_db}")
            cnf_preauth_tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for confirm preauth : {cnf_preauth_tid_db}")
            cnf_preauth_payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for confirm preauth : {cnf_preauth_payment_gateway_db}")
            cnf_preauth_rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for confirm preauth : {cnf_preauth_rrn}")
            cnf_preauth_settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for confirm preauth : {cnf_preauth_settlement_status_db}")
            cnf_preauth_device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table for confirm preauth : {cnf_preauth_device_serial_db}")
            cnf_preauth_merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for confirm preauth : {cnf_preauth_merchant_code_db}")
            cnf_preauth_payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for confirm preauth : {cnf_preauth_payment_card_brand_db}")
            cnf_preauth_payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn tablefor confirm preauth  : {cnf_preauth_payment_card_type_db}")
            cnf_preauth_batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for confirm preauth : {cnf_preauth_batch_number_db}")
            cnf_preauth_payment_card_type = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table, for confirm preauth : {cnf_preauth_payment_card_type}")
            cnf_preauth_order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for confirm preauth : {cnf_preauth_order_id_db}")
            cnf_preauth_issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table for confirm preauth : {cnf_preauth_issuer_code_db}")
            cnf_preauth_org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for confirm preauth : {cnf_preauth_org_code_db}")
            cnf_preauth_payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for confirm preauth : {cnf_preauth_payment_card_bin_db}")
            cnf_preauth_terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for confirm preauth : {cnf_preauth_terminal_info_id_db}")
            cnf_preauth_txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for confirm preauth : {cnf_preauth_txn_type_db}")
            cnf_preauth_card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for confirm preauth : {cnf_preauth_card_txn_type_db}")
            cnf_preauth_card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(
                f"Fetching card last four digit from txn table, for confirm preauth : {cnf_preauth_card_last_four_digit_db}")
            cnf_preauth_customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table for confirm preauth : {cnf_preauth_customer_name_db}")
            cnf_preauth_payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for confirm preauth : {cnf_preauth_payer_name_db}")
            cnf_preauth_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for confirm preauth : {cnf_preauth_merchant_name}")
            cnf_preauth_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table for confirm preauth: {cnf_preauth_posting_date}")

            query = f"select * from txn where org_code='{org_code}' and orig_txn_id = '{cnf_preauth_txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for refunded txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            refund_txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table, for refunded txn : {refund_txn_id} ")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table, for refunded txn : {refund_auth_code}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table, for refunded txn : {refund_created_time}")
            refund_amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table, for refunded txn : {refund_amount_db}")
            refund_payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table, for refunded txn : {refund_payment_mode_db}")
            refund_payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table, for refunded txn : {refund_payment_status_db}")
            refund_payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table, for refunded txn : {refund_payment_state_db}")
            refund_acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table, for refunded txn : {refund_acquirer_code_db}")
            refund_mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table, for refunded txn : {refund_mid_db}")
            refund_tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table, for refunded txn : {refund_tid_db}")
            refund_payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table, for refunded txn : {refund_payment_gateway_db}")
            refund_rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table, for refunded txn : {refund_rrn}")
            refund_settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table, for refunded txn : {refund_settlement_status_db}")
            refund_device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table, for refunded txn : {refund_device_serial_db}")
            refund_merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table, for refunded txn : {refund_merchant_code_db}")
            refund_payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table, for refunded txn : {refund_payment_card_brand_db}")
            refund_payment_card_type = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table, for refunded txn : {refund_payment_card_type}")
            refund_batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table, for refunded txn : {refund_batch_number_db}")
            refund_order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table, for refunded txn : {refund_order_id_db}")
            refund_issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table, for refunded txn : {refund_issuer_code_db}")
            refund_org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table, for refunded txn : {refund_org_code_db}")
            refund_payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table, for refunded txn : {refund_payment_card_bin_db}")
            refund_terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table, for refunded txn : {refund_terminal_info_id_db}")
            refund_txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table, for refunded txn : {refund_txn_type_db}")
            refund_card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table, for refunded txn : {refund_card_txn_type_db}")
            refund_card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table, for refunded txn : {refund_card_last_four_digit_db}")
            refund_customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table, for refunded txn : {refund_customer_name_db}")
            refund_payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table, for refunded txn : {refund_payer_name_db}")
            refund_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table, for refunded txn : {refund_merchant_name}")
            refund_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table for refunded txn: {refund_posting_date}")
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
                # --------------------------------------------------------------------------------------------
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=posting_date)
                cnf_date_and_time_app = date_time_converter.to_app_format(posting_date_db=cnf_preauth_posting_date)
                refund_date_and_time_app = date_time_converter.to_app_format(posting_date_db=refund_posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": original_txn_id,
                    "pmt_status": "CNF_PRE_AUTH",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "MASTERCARD",
                    "card_type_desc": "*1034 CTLS",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": cnf_preauth_txn_id,
                    "pmt_status_2": "AUTHORIZED REFUNDED",
                    "rrn_2": str(cnf_preauth_rrn),
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "settle_status_2": "SETTLED",
                    "auth_code_2": cnf_preauth_auth_code,
                    "date_2": cnf_date_and_time_app,
                    "device_serial_2": cnf_preauth_device_serial_db,
                    "mid_2": cnf_preauth_mid_db,
                    "tid_2": cnf_preauth_tid_db,
                    "batch_number_2": cnf_preauth_batch_number_db,
                    "customer_name_2": "MASTERCARD",
                    "card_type_desc_2": "*1034 CTLS",
                    "txn_amt_3": "{:,.2f}".format(amount),
                    "pmt_mode_3": "CARD",
                    "txn_id_3": refund_txn_id,
                    "pmt_status_3": "REFUNDED",
                    "rrn_3": refund_rrn,
                    "order_id_3": order_id,
                    "pmt_msg_3": "REFUND SUCCESSFUL",
                    "settle_status_3": "PENDING",
                    "auth_code_3": refund_auth_code,
                    "date_3": refund_date_and_time_app,
                    "device_serial_3": device_serial,
                    "mid_3": refund_mid_db,
                    "tid_3": refund_tid_db,
                    "batch_number_3": refund_batch_number_db,
                    "customer_name_3": "MASTERCARD",
                    "card_type_desc_3": "*1034 CTLS",

                    "or_device_serial": device_serial,
                    "or_amount": "{:,.2f}".format(amount),
                    "or_card_type_desc": "*1034 CTLS",
                    "or_date_time": cnf_date_and_time_app,
                    "or_status": "AUTHORIZED_REFUNDED",
                    "or_auth_code_name": cnf_preauth_auth_code,
                    "or_mid": cnf_preauth_mid_db,
                    "or_tid": cnf_preauth_tid_db,
                    "or_rrn": cnf_preauth_rrn,
                    "or_batch_number": cnf_preauth_batch_number_db,
                    "or_customer_name": cnf_preauth_customer_name_db,
                    "or_ref1": cnf_preauth_order_id_db,
                    "or_device_serial_2": device_serial,
                    "or_amount_2": "{:,.2f}".format(amount),
                    "or_card_type_desc_2": "*1034 CTLS",
                    "or_date_time_2": refund_date_and_time_app,
                    "or_status_2": "REFUNDED",
                    "or_ref3_2": device_serial,
                    "or_auth_code_name_2": refund_auth_code,
                    "or_mid_2": refund_mid_db,
                    "or_tid_2": refund_tid_db,
                    "or_rrn_2": refund_rrn,
                    "or_batch_number_2": refund_batch_number_db,
                    "or_customer_name_2": refund_customer_name_db,
                    "or_ref1_2": refund_order_id_db,
                    "or_device_serial_3": device_serial,
                    "or_amount_3": "{:,.2f}".format(amount),
                    "or_card_type_desc_3": "*1034 CTLS",
                    "or_date_time_3": date_and_time_app,
                    "or_status_3": "CNF_PRE_AUTH",
                    "or_auth_code_name_3": auth_code,
                    "or_mid_3": mid_db,
                    "or_tid_3": tid_db,
                    "or_rrn_3": rrn,
                    "or_batch_number_3": batch_number_db,
                    "or_customer_name_3": customer_name_db,
                    "or_ref1_3": order_id_db
                }
                logger.debug(f"expected_app_values: {expected_app_values}")
                refund_page = RefundPage(driver=app_driver)
                online_refund_txn_data = refund_page.capture_online_refund_txn_data(password=app_password,
                                                                                    card_last_four_digit=card_last_four_digit_db,
                                                                                    customer_name=customer_name_db,
                                                                                    txn_type="preauth")
                logger.debug(f"captured transaction data from refund page: {online_refund_txn_data}")
                or_amount = re.search(r'[0-9,\.]+', online_refund_txn_data["or_amount"].split(" ")[0])
                or_amount = or_amount.group()
                or_amount_2 = re.search(r'[0-9,\.]+', online_refund_txn_data["or_amount_2"].split(" ")[0])
                or_amount_2 = or_amount_2.group()
                or_amount_3 = re.search(r'[0-9,\.]+', online_refund_txn_data["or_amount_3"].split(" ")[0])
                or_amount_3 = or_amount_3.group()

                home_page.wait_for_home_page_load()
                GlobalVariables.bool_validate_multiple_txns = False
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=original_txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching payment mode from txn history for the txn : {original_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the txn : {original_txn_id}, {payment_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(
                    f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(
                    f"Fetching txn payment msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the txn : {original_txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(
                    f"Fetching date_time from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for the txn : {original_txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the txn : {original_txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the txn : {original_txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the txn : {original_txn_id}, {app_batch_number}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the txn : {original_txn_id}, {app_customer_name}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the txn : {original_txn_id}, {app_card_type_desc}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=cnf_preauth_txn_id)
                app_amount_cnf_preauth = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {cnf_preauth_txn_id}, {app_amount_cnf_preauth}")
                payment_mode_cnf_preauth = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {payment_mode_cnf_preauth}")
                app_txn_id_cnf_preauth = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_txn_id_cnf_preauth}")
                payment_status_cnf_preauth = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {payment_status_cnf_preauth}")
                app_rrn_cnf_preauth = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_rrn_cnf_preauth}")
                app_order_id_cnf_preauth = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_order_id_cnf_preauth}")
                app_payment_msg_cnf_preauth = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_payment_msg_cnf_preauth}")
                app_settlement_status_cnf_preauth = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_settlement_status_cnf_preauth}")
                app_auth_code_cnf_preauth = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_auth_code_cnf_preauth}")
                app_date_and_time_cnf_preauth = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_date_and_time_cnf_preauth}")
                app_device_serial_cnf_preauth = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_device_serial_cnf_preauth}")
                app_mid_cnf_preauth = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_mid_cnf_preauth}")
                app_tid_cnf_preauth = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for confirm preauth txn : {cnf_preauth_txn_id}, {app_tid_cnf_preauth}")
                app_batch_number_cnf_preauth = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for confirm preauth txn : {cnf_preauth_txn_id}, {app_batch_number_cnf_preauth}")
                app_customer_name_cnf_preauth = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for confirm preauth txn : {cnf_preauth_txn_id}, {app_customer_name_cnf_preauth}")
                app_card_type_desc_cnf_preauth = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for confirm preauth txn : {cnf_preauth_txn_id}, {app_card_type_desc_cnf_preauth}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history, for refunded txn : {refund_txn_id}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history, for refunded txn : {refund_txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history, for refunded txn : {refund_txn_id}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history, for refunded txn : {refund_txn_id}, {payment_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history, for refunded txn : {refund_txn_id}, {app_rrn_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history, for refunded txn : {refund_txn_id}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history, for refunded txn : {refund_txn_id}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history, for refunded txn : {refund_txn_id}, {app_settlement_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for refunded txn : {refund_txn_id}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for refunded txn : {refund_txn_id}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for refunded txn : {refund_txn_id}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for refunded txn : {refund_txn_id}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for refunded txn : {refund_txn_id}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for refunded txn : {refund_txn_id}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for refunded txn : {refund_txn_id}, {app_customer_name_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for refunded txn : {refund_txn_id}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rrn": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_number,
                    "customer_name": app_customer_name,
                    "card_type_desc": app_card_type_desc,
                    "txn_amt_2": app_amount_cnf_preauth.split(' ')[1],
                    "pmt_mode_2": payment_mode_cnf_preauth,
                    "txn_id_2": app_txn_id_cnf_preauth,
                    "pmt_status_2": payment_status_cnf_preauth.split(':')[1],
                    "rrn_2": app_rrn_cnf_preauth,
                    "order_id_2": app_order_id_cnf_preauth,
                    "pmt_msg_2": app_payment_msg_cnf_preauth,
                    "settle_status_2": app_settlement_status_cnf_preauth,
                    "auth_code_2": app_auth_code_cnf_preauth,
                    "date_2": app_date_and_time_cnf_preauth,
                    "device_serial_2": app_device_serial_cnf_preauth,
                    "mid_2": app_mid_cnf_preauth,
                    "tid_2": app_tid_cnf_preauth,
                    "batch_number_2": app_batch_number_cnf_preauth,
                    "customer_name_2": app_customer_name_cnf_preauth,
                    "card_type_desc_2": app_card_type_desc_cnf_preauth,
                    "txn_amt_3": app_amount_2.split(' ')[1],
                    "pmt_mode_3": payment_mode_2,
                    "txn_id_3": app_txn_id_2,
                    "pmt_status_3": payment_status_2.split(':')[1],
                    "rrn_3": app_rrn_2,
                    "order_id_3": app_order_id_2,
                    "pmt_msg_3": app_payment_msg_2,
                    "settle_status_3": app_settlement_status_2,
                    "auth_code_3": app_auth_code_2,
                    "date_3": app_date_and_time_2,
                    "device_serial_3": app_device_serial_2,
                    "mid_3": app_mid_2,
                    "tid_3": app_tid_2,
                    "batch_number_3": app_batch_number_2,
                    "customer_name_3": app_customer_name_2,
                    "card_type_desc_3": app_card_type_desc_2,

                    "or_device_serial": online_refund_txn_data["or_device_serial"],
                    "or_amount": or_amount,
                    "or_card_type_desc": online_refund_txn_data["or_card_type_desc"],
                    "or_date_time": online_refund_txn_data["or_date_time"],
                    "or_status": online_refund_txn_data["or_status"],
                    "or_auth_code_name": online_refund_txn_data["or_auth_code_name"],
                    "or_mid": online_refund_txn_data["or_mid"],
                    "or_tid": online_refund_txn_data["or_tid"],
                    "or_rrn": online_refund_txn_data["or_rrn"],
                    "or_batch_number": online_refund_txn_data["or_batch_number"],
                    "or_customer_name": online_refund_txn_data["or_customer_name"],
                    "or_ref1": online_refund_txn_data["or_ref1"],
                    "or_device_serial_2": online_refund_txn_data["or_device_serial_2"],
                    "or_amount_2": or_amount_2,
                    "or_card_type_desc_2": online_refund_txn_data["or_card_type_desc_2"],
                    "or_date_time_2": online_refund_txn_data["or_date_time_2"],
                    "or_status_2": online_refund_txn_data["or_status_2"],
                    "or_ref3_2": online_refund_txn_data["or_ref3_2"],
                    "or_auth_code_name_2": online_refund_txn_data["or_auth_code_name_2"],
                    "or_mid_2": online_refund_txn_data["or_mid_2"],
                    "or_tid_2": online_refund_txn_data["or_tid_2"],
                    "or_rrn_2": online_refund_txn_data["or_rrn_2"],
                    "or_batch_number_2": online_refund_txn_data["or_batch_number_2"],
                    "or_customer_name_2": online_refund_txn_data["or_customer_name_2"],
                    "or_ref1_2": online_refund_txn_data["or_ref1_2"],
                    "or_device_serial_3": online_refund_txn_data["or_device_serial_3"],
                    "or_amount_3": or_amount_3,
                    "or_card_type_desc_3": online_refund_txn_data["or_card_type_desc_3"],
                    "or_date_time_3": online_refund_txn_data["or_date_time_3"],
                    "or_status_3": online_refund_txn_data["or_status_3"],
                    "or_auth_code_name_3": online_refund_txn_data["or_auth_code_name_3"],
                    "or_mid_3": online_refund_txn_data["or_mid_3"],
                    "or_tid_3": online_refund_txn_data["or_tid_3"],
                    "or_rrn_3": online_refund_txn_data["or_rrn_3"],
                    "or_batch_number_3": online_refund_txn_data["or_batch_number_3"],
                    "or_customer_name_3": online_refund_txn_data["or_customer_name_3"],
                    "or_ref1_3": online_refund_txn_data["or_ref1_3"]
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                cnf_date_and_time_api = date_time_converter.db_datetime(date_from_db=cnf_preauth_created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=refund_created_time)
                expected_api_values = {
                    "pmt_status": "CNF_PRE_AUTH",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "PRE_AUTH",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "CTLS",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "1034",
                    "customer_name": "MASTERCARD/CARDHOLDER",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "MASTERCARD/CARDHOLDER",
                    "pmt_card_bin": "541333",
                    "name_on_card": "MASTERCARD/CARDHOLDER",
                    "display_pan": "1034",
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "REFUNDED",
                    "rrn_2": str(cnf_preauth_rrn),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "CONF_PRE_AUTH",
                    "auth_code_2": cnf_preauth_auth_code,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": cnf_date_and_time_api,
                    "username_2": app_username,
                    "txn_id_2": cnf_preauth_txn_id,
                    "pmt_card_brand_2": "MASTER_CARD",
                    "pmt_card_type_2": "CREDIT",
                    "card_txn_type_2": "CTLS",
                    "batch_number_2": cnf_preauth_batch_number_db,
                    "card_last_four_digit_2": "1034",
                    "customer_name_2": "MASTERCARD/CARDHOLDER",
                    "external_ref_2": order_id,
                    "merchant_name_2": cnf_preauth_merchant_name,
                    "payer_name_2": "MASTERCARD/CARDHOLDER",
                    "pmt_card_bin_2": "541333",
                    "name_on_card_2": "MASTERCARD/CARDHOLDER",
                    "display_pan_2": "1034",
                    "device_serial_2": device_serial,
                    "pmt_status_3": "REFUNDED",
                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "CARD",
                    "pmt_state_3": "AUTHORIZED",
                    "rrn_3": str(refund_rrn),
                    "settle_status_3": "PENDING",
                    "acquirer_code_3": "HDFC",
                    "txn_type_3": "REFUND",
                    "auth_code_3": refund_auth_code,
                    "mid_3": mid,
                    "tid_3": tid,
                    "org_code_3": org_code,
                    "date_3": date_and_time_api_2,
                    "username_3": app_username,
                    "txn_id_3": refund_txn_id,
                    "pmt_card_brand_3": "MASTER_CARD",
                    "pmt_card_type_3": "CREDIT",
                    "card_txn_type_3": "CTLS",
                    "batch_number_3": refund_batch_number_db,
                    "card_last_four_digit_3": "1034",
                    "customer_name_3": "MASTERCARD/CARDHOLDER",
                    "external_ref_3": order_id,
                    "merchant_name_3": refund_merchant_name,
                    "payer_name_3": "MASTERCARD/CARDHOLDER",
                    "pmt_card_bin_3": "541333",
                    "name_on_card_3": "MASTERCARD/CARDHOLDER",
                    "display_pan_3": "1034",
                    "issuer_code_3": issuer_code,
                    "device_serial_3": device_serial
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status from response : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount from response : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode from response : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state from response : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn from response : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement status from response : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer code from response : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org code from response : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid from response : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid from response : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction type from response : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth code from response : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device serial from response : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username from response : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction id from response : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment card type from response : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer name from response : {customer_name_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer name from response : {payer_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {payment_card_bin_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name on card from response : {name_on_card_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN from response : {display_pan_api}")

                response_cnf_preauth = [x for x in response["txns"] if x["txnId"] == cnf_preauth_txn_id][0]
                logger.debug(f"Response after filtering data of cnf preauth txn is : {response_cnf_preauth}")
                cnf_preauth_status_api = response_cnf_preauth["status"]
                logger.debug(f"Fetching status from response for cnf preauth txn : {cnf_preauth_status_api}")
                cnf_preauth_amount_api = float(response_cnf_preauth["amount"])
                logger.debug(f"Fetching amount from response for cnf preauth txn : {cnf_preauth_amount_api}")
                cnf_preauth_payment_mode_api = response_cnf_preauth["paymentMode"]
                logger.debug(f"Fetching payment mode from response for cnf preauth txn : {cnf_preauth_payment_mode_api}")
                cnf_preauth_state_api = response_cnf_preauth["states"][0]
                logger.debug(f"Fetching state from response for cnf preauth txn : {cnf_preauth_state_api}")
                cnf_preauth_rrn_api = response_cnf_preauth["rrNumber"]
                logger.debug(f"Fetching rrn from response for cnf preauth txn : {cnf_preauth_rrn_api}")
                cnf_preauth_settlement_status_api = response_cnf_preauth["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for cnf preauth txn : {cnf_preauth_settlement_status_api}")
                cnf_preauth_acquirer_code_api = response_cnf_preauth["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for cnf preauth txn : {cnf_preauth_acquirer_code_api}")
                cnf_preauth_org_code_api = response_cnf_preauth["orgCode"]
                logger.debug(f"Fetching org code from response for cnf preauth txn : {cnf_preauth_org_code_api}")
                cnf_preauth_mid_api = response_cnf_preauth["mid"]
                logger.debug(f"Fetching mid from response for cnf preauth txn : {cnf_preauth_mid_api}")
                cnf_preauth_tid_api = response_cnf_preauth["tid"]
                logger.debug(f"Fetching tid from response for cnf preauth txn : {cnf_preauth_tid_api}")
                cnf_preauth_txn_type_api = response_cnf_preauth["txnType"]
                logger.debug(f"Fetching transaction type from response for cnf preauth txn : {cnf_preauth_txn_type_api}")
                cnf_preauth_auth_code_api = response_cnf_preauth["authCode"]
                logger.debug(f"Fetching auth code from response for cnf preauth txn : {cnf_preauth_auth_code_api}")
                cnf_preauth_date_and_time_api = response_cnf_preauth["createdTime"]
                logger.debug(f"Fetching date and time from response for cnf preauth txn : {cnf_preauth_date_and_time_api}")
                cnf_preauth_device_serial_api = response_cnf_preauth["deviceSerial"]
                logger.debug(f"Fetching device serial from response for cnf preauth txn : {cnf_preauth_device_serial_api}")
                cnf_preauth_username_api = response_cnf_preauth["username"]
                logger.debug(f"Fetching username from response for cnf preauth txn : {cnf_preauth_username_api}")
                cnf_preauth_txn_id_api = response_cnf_preauth["txnId"]
                logger.debug(f"Fetching transaction id from response for cnf preauth txn : {cnf_preauth_txn_id_api}")
                cnf_preauth_payment_card_brand_api = response_cnf_preauth["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for cnf preauth txn : {cnf_preauth_payment_card_brand_api}")
                cnf_preauth_payment_card_type_api = response_cnf_preauth["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for cnf preauth txn : {cnf_preauth_payment_card_type_api}")
                cnf_preauth_card_txn_type_api = response_cnf_preauth["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for cnf preauth txn : {cnf_preauth_card_txn_type_api}")
                cnf_preauth_batch_number_api = response_cnf_preauth["batchNumber"]
                logger.debug(f"Fetching batch number from response for cnf preauth txn : {cnf_preauth_batch_number_api}")
                cnf_preauth_card_last_four_digit_api = response_cnf_preauth["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for cnf preauth txn : {cnf_preauth_card_last_four_digit_api}")
                cnf_preauth_customer_name_api = response_cnf_preauth["customerName"]
                logger.debug(f"Fetching customer name from response for cnf preauth txn : {cnf_preauth_customer_name_api}")
                cnf_preauth_external_ref_number_api = response_cnf_preauth["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for cnf preauth txn : {cnf_preauth_external_ref_number_api}")
                cnf_preauth_merchant_name_api = response_cnf_preauth["merchantName"]
                logger.debug(f"Fetching merchant name from response for cnf preauth txn : {cnf_preauth_merchant_name_api}")
                cnf_preauth_payer_name_api = response_cnf_preauth["payerName"]
                logger.debug(f"Fetching payer name from response for cnf preauth txn : {cnf_preauth_payer_name_api}")
                cnf_preauth_payment_card_bin_api = response_cnf_preauth["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for cnf preauth txn : {cnf_preauth_payment_card_bin_api}")
                cnf_preauth_name_on_card_api = response_cnf_preauth["nameOnCard"]
                logger.debug(f"Fetching name on card from response for cnf preauth txn : {cnf_preauth_name_on_card_api}")
                cnf_preauth_display_pan_api = response_cnf_preauth["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for cnf preauth txn : {cnf_preauth_display_pan_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status from response for refunded txn : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount from response for refunded txn : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment mode from response for refunded txn : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state from response for refunded txn : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn from response for refunded txn : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for refunded txn : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for refunded txn : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org code from response for refunded txn : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid from response for refunded txn : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid from response for refunded txn : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction type from response for refunded txn : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth code from response for refunded txn : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date and time from response for refunded txn : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username from response for refunded txn : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction id from response for refunded txn : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for refunded txn : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for refunded txn : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for refunded txn : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch number from response for refunded txn : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for refunded txn : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer name from response for refunded txn : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for refunded txn : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant name from response for refunded txn : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer name from response for refunded txn : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for refunded txn : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name on card from response for refunded txn : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for refunded txn : {display_pan_api_2}")
                device_serial_api_2 = response_2["deviceSerial"]
                logger.debug(f"Fetching device serial from response for refunded txn : {device_serial_api_2}")
                issuer_code_api_2 = response_2["issuerCode"]
                logger.debug(f"Fetching issuer code from response for refunded txn : {issuer_code_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "device_serial": device_serial_api,
                    "username": username_api,
                    "txn_id": txn_id_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_txn_type": card_txn_type_api,
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "customer_name": customer_name_api,
                    "external_ref": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "payer_name": payer_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "name_on_card": name_on_card_api,
                    "display_pan": display_pan_api,
                    "pmt_status_2": cnf_preauth_status_api,
                    "txn_amt_2": cnf_preauth_amount_api,
                    "pmt_mode_2": cnf_preauth_payment_mode_api,
                    "pmt_state_2": cnf_preauth_state_api,
                    "rrn_2": str(cnf_preauth_rrn_api),
                    "settle_status_2": cnf_preauth_settlement_status_api,
                    "acquirer_code_2": cnf_preauth_acquirer_code_api,
                    "txn_type_2": cnf_preauth_txn_type_api,
                    "auth_code_2": cnf_preauth_auth_code_api,
                    "mid_2": cnf_preauth_mid_api,
                    "tid_2": cnf_preauth_tid_api,
                    "org_code_2": cnf_preauth_org_code_api,
                    "date_2": date_time_converter.from_api_to_datetime_format(cnf_preauth_date_and_time_api),
                    "username_2": cnf_preauth_username_api,
                    "txn_id_2": cnf_preauth_txn_id_api,
                    "pmt_card_brand_2": cnf_preauth_payment_card_brand_api,
                    "pmt_card_type_2": cnf_preauth_payment_card_type_api,
                    "card_txn_type_2": cnf_preauth_card_txn_type_api,
                    "batch_number_2": cnf_preauth_batch_number_api,
                    "card_last_four_digit_2": cnf_preauth_card_last_four_digit_api,
                    "customer_name_2": cnf_preauth_customer_name_api,
                    "external_ref_2": cnf_preauth_external_ref_number_api,
                    "merchant_name_2": cnf_preauth_merchant_name_api,
                    "payer_name_2": cnf_preauth_payer_name_api,
                    "pmt_card_bin_2": cnf_preauth_payment_card_bin_api,
                    "name_on_card_2": cnf_preauth_name_on_card_api,
                    "display_pan_2": cnf_preauth_display_pan_api,
                    "device_serial_2": cnf_preauth_device_serial_api,
                    "pmt_status_3": status_api_2,
                    "txn_amt_3": amount_api_2,
                    "pmt_mode_3": payment_mode_api_2,
                    "pmt_state_3": state_api_2,
                    "rrn_3": str(rrn_api_2),
                    "settle_status_3": settlement_status_api_2,
                    "acquirer_code_3": acquirer_code_api_2,
                    "txn_type_3": txn_type_api_2,
                    "auth_code_3": auth_code_api_2,
                    "mid_3": mid_api_2,
                    "tid_3": tid_api_2,
                    "org_code_3": org_code_api_2,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_3": username_api_2,
                    "txn_id_3": txn_id_api_2,
                    "pmt_card_brand_3": payment_card_brand_api_2,
                    "pmt_card_type_3": payment_card_type_api_2,
                    "card_txn_type_3": card_txn_type_api_2,
                    "batch_number_3": batch_number_api_2,
                    "card_last_four_digit_3": card_last_four_digit_api_2,
                    "customer_name_3": customer_name_api_2,
                    "external_ref_3": external_ref_number_api_2,
                    "merchant_name_3": merchant_name_api_2,
                    "payer_name_3": payer_name_api_2,
                    "pmt_card_bin_3": payment_card_bin_api_2,
                    "name_on_card_3": name_on_card_api_2,
                    "display_pan_3": display_pan_api_2,
                    "issuer_code_3": issuer_code_api_2,
                    "device_serial_3": device_serial_api_2
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "txn_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "CNF_PRE_AUTH",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "541333",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "PRE_AUTH",
                    "card_txn_type": "91",
                    "card_last_four_digit": "1034",
                    "customer_name": "MASTERCARD/CARDHOLDER",
                    "payer_name": "MASTERCARD/CARDHOLDER",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "SETTLED",
                    "device_serial_2": device_serial,
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "MASTER_CARD",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "541333",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "CONF_PRE_AUTH",
                    "card_txn_type_2": "91",
                    "card_last_four_digit_2": "1034",
                    "customer_name_2": "MASTERCARD/CARDHOLDER",
                    "payer_name_2": "MASTERCARD/CARDHOLDER",
                    "txn_amt_3": amount,
                    "pmt_mode_3": "CARD",
                    "pmt_status_3": "REFUNDED",
                    "pmt_state_3": "AUTHORIZED",
                    "acquirer_code_3": "HDFC",
                    "mid_3": mid,
                    "tid_3": tid,
                    "pmt_gateway_3": "DUMMY",
                    "settle_status_3": "PENDING",
                    "device_serial_3": device_serial,
                    "merchant_code_3": org_code,
                    "pmt_card_brand_3": "MASTER_CARD",
                    "pmt_card_type_3": "CREDIT",
                    "order_id_3": order_id,
                    "issuer_code_3": issuer_code,
                    "org_code_3": org_code,
                    "pmt_card_bin_3": "541333",
                    "terminal_info_id_3": terminal_info_id,
                    "txn_type_3": "REFUND",
                    "card_txn_type_3": "91",
                    "card_last_four_digit_3": "1034",
                    "customer_name_3": "MASTERCARD/CARDHOLDER",
                    "payer_name_3": "MASTERCARD/CARDHOLDER"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "device_serial": device_serial_db,
                    "merchant_code": merchant_code_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "order_id": order_id_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "customer_name": customer_name_db,
                    "payer_name": payer_name_db,
                    "txn_amt_2": cnf_preauth_amount_db,
                    "pmt_mode_2": cnf_preauth_payment_mode_db,
                    "pmt_status_2": cnf_preauth_payment_status_db,
                    "pmt_state_2": cnf_preauth_payment_state_db,
                    "acquirer_code_2": cnf_preauth_acquirer_code_db,
                    "mid_2": cnf_preauth_mid_db,
                    "tid_2": cnf_preauth_tid_db,
                    "pmt_gateway_2": cnf_preauth_payment_gateway_db,
                    "settle_status_2": cnf_preauth_settlement_status_db,
                    "device_serial_2": cnf_preauth_device_serial_db,
                    "merchant_code_2": cnf_preauth_merchant_code_db,
                    "pmt_card_brand_2": cnf_preauth_payment_card_brand_db,
                    "pmt_card_type_2": cnf_preauth_payment_card_type,
                    "order_id_2": cnf_preauth_order_id_db,
                    "org_code_2": cnf_preauth_org_code_db,
                    "pmt_card_bin_2": cnf_preauth_payment_card_bin_db,
                    "terminal_info_id_2": cnf_preauth_terminal_info_id_db,
                    "txn_type_2": cnf_preauth_txn_type_db,
                    "card_txn_type_2": cnf_preauth_card_txn_type_db,
                    "card_last_four_digit_2": cnf_preauth_card_last_four_digit_db,
                    "customer_name_2": cnf_preauth_customer_name_db,
                    "payer_name_2": cnf_preauth_payer_name_db,
                    "txn_amt_3": refund_amount_db,
                    "pmt_mode_3": refund_payment_mode_db,
                    "pmt_status_3": refund_payment_status_db,
                    "pmt_state_3": refund_payment_state_db,
                    "acquirer_code_3": refund_acquirer_code_db,
                    "mid_3": refund_mid_db,
                    "tid_3": refund_tid_db,
                    "pmt_gateway_3": refund_payment_gateway_db,
                    "settle_status_3": refund_settlement_status_db,
                    "device_serial_3": refund_device_serial_db,
                    "merchant_code_3": refund_merchant_code_db,
                    "pmt_card_brand_3": refund_payment_card_brand_db,
                    "pmt_card_type_3": refund_payment_card_type,
                    "order_id_3": refund_order_id_db,
                    "issuer_code_3": refund_issuer_code_db,
                    "org_code_3": refund_org_code_db,
                    "pmt_card_bin_3": refund_payment_card_bin_db,
                    "terminal_info_id_3": refund_terminal_info_id_db,
                    "txn_type_3": refund_txn_type_db,
                    "card_txn_type_3": refund_card_txn_type_db,
                    "card_last_four_digit_3": refund_card_last_four_digit_db,
                    "customer_name_3": refund_customer_name_db,
                    "payer_name_3": refund_payer_name_db
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=created_time)
                date_and_time_portal_cnf = date_time_converter.to_portal_format(created_date_db=cnf_preauth_created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                expected_portal_values = {
                    "pmt_status": "CNF_PRE_AUTH",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_and_time_portal,
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": cnf_preauth_txn_id,
                    "auth_code_2": cnf_preauth_auth_code,
                    "rrn_2": cnf_preauth_rrn,
                    "date_time_2": date_and_time_portal_cnf,
                    "pmt_status_3": "REFUNDED",
                    "pmt_type_3": "CARD",
                    "txn_amt_3": "{:,.2f}".format(amount),
                    "username_3": app_username,
                    "txn_id_3": refund_txn_id,
                    "auth_code_3": refund_auth_code,
                    "rrn_3": refund_rrn,
                    "date_time_3": date_and_time_portal_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                date_time = transaction_details[2]['Date & Time']
                transaction_id = transaction_details[2]['Transaction ID']
                total_amount = transaction_details[2]['Total Amount'].split()
                auth_code_portal = transaction_details[2]['Auth Code']
                rr_number = transaction_details[2]['RR Number']
                transaction_type = transaction_details[2]['Type']
                status = transaction_details[2]['Status']
                username = transaction_details[2]['Username']

                date_time_2 = transaction_details[1]['Date & Time']
                transaction_id_2 = transaction_details[1]['Transaction ID']
                total_amount_2 = transaction_details[1]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[1]['Auth Code']
                rr_number_2 = transaction_details[1]['RR Number']
                transaction_type_2 = transaction_details[1]['Type']
                status_2 = transaction_details[1]['Status']
                username_2 = transaction_details[1]['Username']

                date_time_3 = transaction_details[0]['Date & Time']
                transaction_id_3 = transaction_details[0]['Transaction ID']
                total_amount_3 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_3 = transaction_details[0]['Auth Code']
                rr_number_3 = transaction_details[0]['RR Number']
                transaction_type_3 = transaction_details[0]['Type']
                status_3 = transaction_details[0]['Status']
                username_3 = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2,
                    "pmt_status_3": str(status_3),
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "auth_code_3": auth_code_portal_3,
                    "rrn_3": rr_number_3,
                    "date_time_3": date_time_3
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=refund_posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "MasterCard",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(refund_rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "AUTH CODE": refund_auth_code,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": refund_batch_number_db,
                    "TID": tid
                }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                chargeslip_val_result = receipt_validator.perform_charge_slip_validations(txn_id=refund_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)

                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values_2 = {
                    "CARD TYPE": "MasterCard",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "AUTH CODE": auth_code,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "SALE",
                    "BATCH NO": batch_number_db,
                    "TID": tid
                }
                logger.debug(f"expected_charge_slip_values for original txn : {expected_charge_slip_values_2}")
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id=original_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                    }, expected_details=expected_charge_slip_values_2)

                if chargeslip_val_result and chargeslip_val_result_2:
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
