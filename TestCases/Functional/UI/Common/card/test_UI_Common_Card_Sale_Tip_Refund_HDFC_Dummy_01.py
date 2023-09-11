import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
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
def test_common_100_115_01_010():
    """
    Sub Feature Code: UI_Common_Card_Sale_Tip_Refund_Api_Txn_HDFC_Dummy_EMVCTLS_VISA_DebitCard_Without_pin_476173
    Sub Feature Description: Performing the EMVCTLS sale tip refund Api transaction via HDFC Dummy PG using VISA Debit
    card having 16 digit PAN length without pin (bin:476173)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 01: Sale+Tip, 010: TC010
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].values[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result['id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details(api_name='org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["tipEnabled"] = "true"
        api_details["RequestBody"]["settings"]["tipPercentage"] = "10"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for tip option to be enabled and setting tip "
                     f"percentage 10 :  {response}")

        query = f"select bank_code from bin_info where bin='476173'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

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
            amount = random.randint(10, 300)
            max_tip_amount = int((amount * 10) / 100)
            tip_amount = random.randint(1, max_tip_amount)
            total_amount = amount + tip_amount
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_tip_and_amount_and_order_number_and_device_serial_for_card(amt=amount,
                                                                                       order_number=order_id,
                                                                                       tip_amt=tip_amount,
                                                                                       device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered tip_amount is : {tip_amount}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card_with_tip(amount=amount, order_id=order_id,
                                                                 tip_amt=tip_amount, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info(f"Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : CTLS_VISA_DEBIT_476173")
            card_page.select_cardtype(text="CTLS_VISA_DEBIT_476173")
            logger.debug(f"Selected the card type as : CTLS_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details(api_name='Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details  : {api_details} ")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Settlement api is : {settle_response}")

            query = f"select id from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn id from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details(api_name='Offline_Refund', request_body={
                "amount": total_amount,
                "originalTransactionId": txn_id,
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API details  : {api_details} ")
            refund_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {refund_response}")
            refund_txn_id = refund_response.get('txnId')
            logger.debug(f"From response fetch txn_id : {refund_txn_id}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch txn details for original txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table for original txn : {result}")
            total_amount_txn = result['amount'].values[0]
            logger.debug(f"Query result, amount : {total_amount_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, acquirer_code : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, settlement_status : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Query result, status : {pmt_status}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Query result, issuer_code : {issuer_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type : {txn_type}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Query result, state : {pmt_state}")
            bank_name = result['bank_name'].values[0]
            logger.debug(f"Query result, bank_name : {bank_name}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, payment_gateway : {payment_gateway}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Query result, batch_number : {batch_number}")
            amount_additional = result['amount_additional'].values[0]
            logger.debug(f"Query result, amount_additional : {amount_additional}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Query result, payment_card_brand : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, payment_card_type : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Query result, card_last_four_digit : {card_last_four_digit}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode : {payment_mode}")
            amount_original = result['amount_original'].values[0]
            logger.debug(f"Query result, amount_original : {amount_original}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Query result, merchant_name : {merchant_name}")
            pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Query result, payment_card_bin : {pmt_card_bin}")
            terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Query result, terminal_info_id : {terminal_info_id_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Query result, mid : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Query result, tid : {tid_txn}")
            device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial : {device_serial_txn}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Query result, order_id : {order_id_txn}")
            card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Query result, card_txn_type : {card_txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code_txn}")

            query = f"select * from txn where id = '{refund_txn_id}'"
            logger.debug(f"Query to fetch txn details for refund txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table for refund txn : {result}")
            refund_total_amount_txn = result['amount'].values[0]
            logger.debug(f"Query result, amount : {refund_total_amount_txn}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time : {refund_created_time}")
            refund_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, acquirer_code : {refund_acquirer_code}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code : {refund_auth_code}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name : {refund_payer_name}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {refund_rrn}")
            refund_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, settlement_status : {refund_settle_status}")
            refund_pmt_status = result['status'].values[0]
            logger.debug(f"Query result, status : {refund_pmt_status}")
            refund_issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Query result, issuer_code : {refund_issuer_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type : {refund_txn_type}")
            refund_pmt_state = result['state'].values[0]
            logger.debug(f"Query result, state : {refund_pmt_state}")
            refund_bank_name = result['bank_name'].values[0]
            logger.debug(f"Query result, bank_name : {refund_bank_name}")
            refund_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, payment_gateway : {refund_payment_gateway}")
            refund_batch_number = result['batch_number'].values[0]
            logger.debug(f"Query result, batch_number : {refund_batch_number}")
            refund_amount_additional = result['amount_additional'].values[0]
            logger.debug(f"Query result, amount_additional : {refund_amount_additional}")
            refund_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Query result, payment_card_brand : {refund_pmt_card_brand}")
            refund_pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, payment_card_type : {refund_pmt_card_type}")
            refund_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Query result, card_last_four_digit : {refund_card_last_four_digit}")
            refund_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode : {refund_payment_mode}")
            refund_amount_original = result['amount_original'].values[0]
            logger.debug(f"Query result, amount_original : {refund_amount_original}")
            refund_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Query result, merchant_name : {refund_merchant_name}")
            refund_pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Query result, payment_card_bin : {refund_pmt_card_bin}")
            refund_terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Query result, terminal_info_id : {refund_terminal_info_id_txn}")
            refund_mid_txn = result['mid'].values[0]
            logger.debug(f"Query result, mid : {refund_mid_txn}")
            refund_tid_txn = result['tid'].values[0]
            logger.debug(f"Query result, tid : {refund_tid_txn}")
            refund_device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial : {refund_device_serial_txn}")
            refund_order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Query result, order_id : {refund_order_id_txn}")
            refund_card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Query result, card_txn_type : {refund_card_txn_type}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {refund_org_code_txn}")
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
                date_time = date_time_converter.to_app_format(posting_date_db=created_time)
                refund_date_and_time = date_time_converter.to_app_format(posting_date_db=refund_created_time)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(total_amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "customer_name": "L3TEST",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_time,
                    "device_serial": device_serial,
                    "batch_number": batch_number,
                    "tip_amt": "{:,.2f}".format(tip_amount),
                    "card_type_desc": "*0453 CTLS",
                    "mid": mid,
                    "tid": tid,
                    "txn_amt_2": "{:,.2f}".format(total_amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": refund_txn_id,
                    "pmt_status_2": "REFUNDED",
                    "rr_number_2": refund_rrn,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "customer_name_2": "L3TEST",
                    "settle_status_2": "PENDING",
                    "auth_code_2": refund_auth_code,
                    "date_2": refund_date_and_time,
                    "device_serial_2": device_serial,
                    "batch_number_2": refund_batch_number,
                    "card_type_desc_2": "*0453 CTLS",
                    "mid_2": mid,
                    "tid_2": tid
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.info(f"reseting the app_driver to login again in the MPOSX application")
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the txn : {txn_id}, {app_batch_number}")
                app_tip_amt = txn_history_page.fetch_tip_amt_text()
                logger.info(f"Fetching tip_amt from txn history for the txn : {txn_id}, {app_tip_amt}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the txn : {txn_id}, {app_card_type_desc}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_refund = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {refund_txn_id}, {app_amount_refund}")
                app_order_id_refund = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {refund_txn_id}, {app_order_id_refund}")
                app_payment_msg_refund = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {refund_txn_id}, {app_payment_msg_refund}")
                app_payment_mode_refund = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {refund_txn_id}, {app_payment_mode_refund}")
                app_payment_status_refund = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {refund_txn_id}, {app_payment_status_refund}")
                app_txn_id_refund = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {refund_txn_id}, {app_txn_id_refund}")
                app_customer_name_refund = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {refund_txn_id}, {app_customer_name_refund}")
                app_date_time_refund = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {refund_txn_id}, {app_date_time_refund}")
                app_settle_status_refund = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the txn : {refund_txn_id}, {app_settle_status_refund}")
                app_rrn_refund = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {refund_txn_id}, {app_rrn_refund}")
                app_auth_code_refund = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {refund_txn_id}, {app_auth_code_refund}")
                app_device_serial_refund = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the txn : {refund_txn_id}, {app_device_serial_refund}")
                app_batch_number_refund = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the txn : {refund_txn_id}, {app_batch_number_refund}")
                app_card_type_desc_refund = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the txn : {refund_txn_id}, {app_card_type_desc_refund}")
                app_mid_refund = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {refund_txn_id}, {app_mid_refund}")
                app_tid_refund = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {refund_txn_id}, {app_tid_refund}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": app_payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "customer_name": app_customer_name,
                    "settle_status": app_settle_status,
                    "auth_code": app_auth_code,
                    "date": app_date_time,
                    "device_serial": app_device_serial,
                    "batch_number": app_batch_number,
                    "tip_amt": app_tip_amt.split(' ')[1],
                    "card_type_desc": app_card_type_desc,
                    "mid": app_mid,
                    "tid": app_tid,
                    "txn_amt_2": app_amount_refund.split(' ')[1],
                    "pmt_mode_2": app_payment_mode_refund,
                    "txn_id_2": app_txn_id_refund,
                    "pmt_status_2": app_payment_status_refund.split(':')[1],
                    "rr_number_2": app_rrn_refund,
                    "order_id_2": app_order_id_refund,
                    "pmt_msg_2": app_payment_msg_refund,
                    "customer_name_2": app_customer_name_refund,
                    "settle_status_2": app_settle_status_refund,
                    "auth_code_2": app_auth_code_refund,
                    "date_2": app_date_time_refund,
                    "device_serial_2": app_device_serial_refund,
                    "batch_number_2": app_batch_number_refund,
                    "card_type_desc_2": app_card_type_desc_refund,
                    "mid_2": app_mid_refund,
                    "tid_2": app_tid_refund
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
                date_time = date_time_converter.db_datetime(date_from_db=created_time)
                refund_date_and_time = date_time_converter.db_datetime(date_from_db=refund_created_time)
                expected_api_values = {
                    "txn_amt": float(total_amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "rrn": rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "org_code": org_code,
                    "tip_amt": float(tip_amount),
                    "batch_number": batch_number,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "date": date_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "CTLS",
                    "amt_original": float(amount),
                    "auth_code": auth_code,
                    "card_last_four_digit": "0453",
                    "customer_name": "L3TEST/CARD1045",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "L3TEST/CARD1045",
                    "pmt_card_bin": "476173",
                    "card_type": "VISA",
                    "display_pan": "0453",
                    "name_on_card": "L3TEST/CARD1045",
                    "txn_amt_2": float(total_amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "mid_2": mid,
                    "tid_2": tid,
                    "acquirer_code_2": "HDFC",
                    "settle_status_2": "PENDING",
                    "rrn_2": refund_rrn,
                    "issuer_code_2": None,
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "tip_amt_2": float(0.0),
                    "batch_number_2": refund_batch_number,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "date_2": refund_date_and_time,
                    "device_serial_2": None,
                    "card_txn_type_desc_2": "CTLS",
                    "amt_original_2": float(total_amount),
                    "auth_code_2": refund_auth_code,
                    "card_last_four_digit_2": "0453",
                    "customer_name_2": "L3TEST/CARD1045",
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": merchant_name,
                    "payer_name_2": "L3TEST/CARD1045",
                    "pmt_card_bin_2": "476173",
                    "card_type_2": "VISA",
                    "display_pan_2": "0453",
                    "name_on_card_2": "L3TEST/CARD1045"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for transaction list : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_original = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_original}")
                api_amount = response_original.get('amount')
                logger.debug(f"From response_original fetch amount : {api_amount}")
                api_payment_mode = response_original.get('paymentMode')
                logger.debug(f"From response_original fetch payment_mode : {api_payment_mode}")
                api_payment_status = response_original.get('status')
                logger.debug(f"From response_original fetch payment_status : {api_payment_status}")
                api_payment_state = response_original.get('states')[0]
                logger.debug(f"From response_original fetch payment_state : {api_payment_state}")
                api_mid = response_original.get('mid')
                logger.debug(f"From response_original fetch mid : {api_mid}")
                api_tid = response_original.get('tid')
                logger.debug(f"From response_original fetch tid : {api_tid}")
                api_acquirer_code = response_original.get('acquirerCode')
                logger.debug(f"From response_original fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response_original.get('settlementStatus')
                logger.debug(f"From response_original fetch settlement_status : {api_settle_status}")
                api_rrn = response_original.get('rrNumber')
                logger.debug(f"From response_original fetch rrn : {api_rrn}")
                api_issuer_code = response_original.get('issuerCode')
                logger.debug(f"From response_original fetch issuer_code : {api_issuer_code}")
                api_txn_type = response_original.get('txnType')
                logger.debug(f"From response_original fetch txn_type : {api_txn_type}")
                api_org_code = response_original.get('orgCode')
                logger.debug(f"From response_original fetch org_code : {api_org_code}")
                api_tip_amt = response_original.get('amountAdditional')
                logger.debug(f"From response_original fetch tip_amt : {api_tip_amt}")
                api_batch_number = response_original.get('batchNumber')
                logger.debug(f"From response_original fetch batch_number : {api_batch_number}")
                api_pmt_card_brand = response_original.get('paymentCardBrand')
                logger.debug(f"From response_original fetch payment_card_brand : {api_pmt_card_brand}")
                api_pmt_card_type = response_original.get('paymentCardType')
                logger.debug(f"From response_original fetch payment_card_type : {api_pmt_card_type}")
                api_date_time = response_original.get('createdTime')
                logger.debug(f"From response_original fetch date_time : {api_date_time}")
                api_device_serial = response_original.get('deviceSerial')
                logger.debug(f"From response_original fetch device_serial : {api_device_serial}")
                api_card_txn_type_desc = response_original.get('cardTxnTypeDesc')
                logger.debug(f"From response_original fetch card_txn_type_desc : {api_card_txn_type_desc}")
                api_amount_original = response_original.get('amountOriginal')
                logger.debug(f"From response_original fetch amount_original : {api_amount_original}")
                api_customer_name = response_original.get('customerName')
                logger.debug(f"From response_original fetch customer_name : {api_customer_name}")
                api_payer_name = response_original.get('payerName')
                logger.debug(f"From response_original fetch payer_name : {api_payer_name}")
                api_merchant_name = response_original.get('merchantName')
                logger.debug(f"From response_original fetch merchant_name : {api_merchant_name}")
                api_card_last_four_digit = response_original.get('cardLastFourDigit')
                logger.debug(f"From response_original fetch card_last_four_digit : {api_card_last_four_digit}")
                api_ext_ref_number = response_original.get('externalRefNumber')
                logger.debug(f"From response_original fetch external_ref_number : {api_ext_ref_number}")
                api_pmt_card_bin = response_original.get('paymentCardBin')
                logger.debug(f"From response_original fetch payment_card_bin : {api_pmt_card_bin}")
                api_name_on_card = response_original.get('nameOnCard')
                logger.debug(f"From response_original fetch name_on_card : {api_name_on_card}")
                api_display_pan = response_original.get('displayPAN')
                logger.debug(f"From response_original fetch display_pan : {api_display_pan}")
                api_auth_code = response_original.get('authCode')
                logger.debug(f"From response_original fetch auth_code : {api_auth_code}")
                api_card_type = response_original.get('cardType')
                logger.debug(f"From response_original fetch card_type : {api_card_type}")

                response_refund = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn is : {response_refund}")
                api_amount_refund = response_refund.get('amount')
                logger.debug(f"From response_refund fetch amount : {api_amount_refund}")
                api_payment_mode_refund = response_refund.get('paymentMode')
                logger.debug(f"From response_refund fetch payment_mode : {api_payment_mode_refund}")
                api_payment_status_refund = response_refund.get('status')
                logger.debug(f"From response_refund fetch payment_status : {api_payment_status_refund}")
                api_payment_state_refund = response_refund.get('states')[0]
                logger.debug(f"From response_refund fetch payment_state : {api_payment_state_refund}")
                api_mid_refund = response_refund.get('mid')
                logger.debug(f"From response_refund fetch mid : {api_mid_refund}")
                api_tid_refund = response_refund.get('tid')
                logger.debug(f"From response_refund fetch tid : {api_tid_refund}")
                api_acquirer_code_refund = response_refund.get('acquirerCode')
                logger.debug(f"From response_refund fetch acquirer_code : {api_acquirer_code_refund}")
                api_settle_status_refund = response_refund.get('settlementStatus')
                logger.debug(f"From response_refund fetch settlement_status : {api_settle_status_refund}")
                api_rrn_refund = response_refund.get('rrNumber')
                logger.debug(f"From response_refund fetch rrn : {api_rrn_refund}")
                api_issuer_code_refund = response_refund.get('issuerCode')
                logger.debug(f"From response_refund fetch issuer_code : {api_issuer_code_refund}")
                api_txn_type_refund = response_refund.get('txnType')
                logger.debug(f"From response_refund fetch txn_type : {api_txn_type_refund}")
                api_org_code_refund = response_refund.get('orgCode')
                logger.debug(f"From response_refund fetch org_code : {api_org_code_refund}")
                api_tip_amt_refund = response_refund.get('amountAdditional')
                logger.debug(f"From response_refund fetch tip_amt : {api_tip_amt_refund}")
                api_batch_number_refund = response_refund.get('batchNumber')
                logger.debug(f"From response_refund fetch batch_number : {api_batch_number_refund}")
                api_pmt_card_brand_refund = response_refund.get('paymentCardBrand')
                logger.debug(f"From response_refund fetch payment_card_brand : {api_pmt_card_brand_refund}")
                api_pmt_card_type_refund = response_refund.get('paymentCardType')
                logger.debug(f"From response_refund fetch payment_card_type : {api_pmt_card_type_refund}")
                api_date_time_refund = response_refund.get('createdTime')
                logger.debug(f"From response_refund fetch date_time : {api_date_time_refund}")
                api_device_serial_refund = response_refund.get('deviceSerial')
                logger.debug(f"From response_refund fetch device_serial : {api_device_serial_refund}")
                api_card_txn_type_desc_refund = response_refund.get('cardTxnTypeDesc')
                logger.debug(f"From response_refund fetch card_txn_type_desc : {api_card_txn_type_desc_refund}")
                api_amount_original_refund = response_refund.get('amountOriginal')
                logger.debug(f"From response_refund fetch amount_original : {api_amount_original_refund}")
                api_customer_name_refund = response_refund.get('customerName')
                logger.debug(f"From response_refund fetch customer_name : {api_customer_name_refund}")
                api_payer_name_refund = response_refund.get('payerName')
                logger.debug(f"From response_refund fetch payer_name : {api_payer_name_refund}")
                api_merchant_name_refund = response_refund.get('merchantName')
                logger.debug(f"From response_refund fetch merchant_name : {api_merchant_name_refund}")
                api_card_last_four_digit_refund = response_refund.get('cardLastFourDigit')
                logger.debug(f"From response_refund fetch card_last_four_digit : {api_card_last_four_digit_refund}")
                api_ext_ref_number_refund = response_refund.get('externalRefNumber')
                logger.debug(f"From response_refund fetch external_ref_number : {api_ext_ref_number_refund}")
                api_pmt_card_bin_refund = response_refund.get('paymentCardBin')
                logger.debug(f"From response_refund fetch payment_card_bin : {api_pmt_card_bin_refund}")
                api_name_on_card_refund = response_refund.get('nameOnCard')
                logger.debug(f"From response_refund fetch name_on_card : {api_name_on_card_refund}")
                api_display_pan_refund = response_refund.get('displayPAN')
                logger.debug(f"From response_refund fetch display_pan : {api_display_pan_refund}")
                api_auth_code_refund = response_refund.get('authCode')
                logger.debug(f"From response_refund fetch auth_code : {api_auth_code_refund}")
                api_card_type_refund = response_refund.get('cardType')
                logger.debug(f"From response_refund fetch card_type : {api_card_type_refund}")

                actual_api_values = {
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_status": api_payment_status,
                    "pmt_state": api_payment_state,
                    "mid": api_mid,
                    "tid": api_tid,
                    "acquirer_code": api_acquirer_code,
                    "settle_status": api_settle_status,
                    "rrn": api_rrn,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "org_code": api_org_code,
                    "tip_amt": api_tip_amt,
                    "batch_number": api_batch_number,
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
                    "card_txn_type_desc": api_card_txn_type_desc,
                    "amt_original": api_amount_original,
                    "auth_code": api_auth_code,
                    "card_last_four_digit": api_card_last_four_digit,
                    "customer_name": api_customer_name,
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "payer_name": api_payer_name,
                    "pmt_card_bin": api_pmt_card_bin,
                    "card_type": api_card_type,
                    "display_pan": api_display_pan,
                    "name_on_card": api_name_on_card,
                    "txn_amt_2": api_amount_refund,
                    "pmt_mode_2": api_payment_mode_refund,
                    "pmt_status_2": api_payment_status_refund,
                    "pmt_state_2": api_payment_state_refund,
                    "mid_2": api_mid_refund,
                    "tid_2": api_tid_refund,
                    "acquirer_code_2": api_acquirer_code_refund,
                    "settle_status_2": api_settle_status_refund,
                    "rrn_2": api_rrn_refund,
                    "issuer_code_2": api_issuer_code_refund,
                    "txn_type_2": api_txn_type_refund,
                    "org_code_2": api_org_code_refund,
                    "tip_amt_2": api_tip_amt_refund,
                    "batch_number_2": api_batch_number_refund,
                    "pmt_card_brand_2": api_pmt_card_brand,
                    "pmt_card_type_2": api_pmt_card_type_refund,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_refund),
                    "device_serial_2": api_device_serial_refund,
                    "card_txn_type_desc_2": api_card_txn_type_desc_refund,
                    "amt_original_2": api_amount_original_refund,
                    "auth_code_2": api_auth_code_refund,
                    "card_last_four_digit_2": api_card_last_four_digit_refund,
                    "customer_name_2": api_customer_name_refund,
                    "ext_ref_number_2": api_ext_ref_number_refund,
                    "merchant_name_2": api_merchant_name_refund,
                    "payer_name_2": api_payer_name_refund,
                    "pmt_card_bin_2": api_pmt_card_bin_refund,
                    "card_type_2": api_card_type_refund,
                    "display_pan_2": api_display_pan_refund,
                    "name_on_card_2": api_name_on_card_refund
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
                    "txn_amt": float(total_amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": "L3TEST/CARD1045",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "txn_type": "CHARGE",
                    "settle_status": "SETTLED",
                    "tip_amt": float(tip_amount),
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "amt_original": float(amount),
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "476173",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "91",
                    "card_last_four_digit": "0453",
                    "customer_name": "L3TEST/CARD1045",
                    "txn_amt_2": float(total_amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": None,
                    "payer_name_2": "L3TEST/CARD1045",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "txn_type_2": "REFUND",
                    "settle_status_2": "PENDING",
                    "tip_amt_2": float(0.0),
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "amt_original_2": float(total_amount),
                    "device_serial_2": None,
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "476173",
                    "terminal_info_id_2": terminal_info_id,
                    "card_txn_type_2": "91",
                    "card_last_four_digit_2": "0453",
                    "customer_name_2": "L3TEST/CARD1045"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": total_amount_txn,
                    "pmt_mode": payment_mode,
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "payer_name": payer_name,
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "pmt_gateway": payment_gateway,
                    "txn_type": txn_type,
                    "settle_status": settle_status,
                    "tip_amt": amount_additional,
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "amt_original": amount_original,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "terminal_info_id": terminal_info_id_txn,
                    "card_txn_type": card_txn_type,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name,
                    "txn_amt_2": refund_total_amount_txn,
                    "pmt_mode_2": refund_payment_mode,
                    "pmt_status_2": refund_pmt_status,
                    "pmt_state_2": refund_pmt_state,
                    "acquirer_code_2": refund_acquirer_code,
                    "issuer_code_2": refund_issuer_code_txn,
                    "payer_name_2": refund_payer_name,
                    "mid_2": refund_mid_txn,
                    "tid_2": refund_tid_txn,
                    "pmt_gateway_2": refund_payment_gateway,
                    "txn_type_2": refund_txn_type,
                    "settle_status_2": refund_settle_status,
                    "tip_amt_2": refund_amount_additional,
                    "pmt_card_brand_2": refund_pmt_card_brand,
                    "pmt_card_type_2": refund_pmt_card_type,
                    "amt_original_2": refund_amount_original,
                    "device_serial_2": refund_device_serial_txn,
                    "order_id_2": refund_order_id_txn,
                    "org_code_2": refund_org_code_txn,
                    "pmt_card_bin_2": refund_pmt_card_bin,
                    "terminal_info_id_2": refund_terminal_info_id_txn,
                    "card_txn_type_2": refund_card_txn_type,
                    "card_last_four_digit_2": refund_card_last_four_digit,
                    "customer_name_2": refund_customer_name
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
                date_time = date_time_converter.to_portal_format(created_date_db=created_time)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                expected_portal_values = {
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(total_amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_time,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(total_amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "auth_code_2": refund_auth_code,
                    "rrn_2": refund_rrn,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[1]['Transaction ID']
                logger.info(
                    f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[1]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_auth_code = transaction_details[1]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")
                portal_rrn = transaction_details[1]['RR Number']
                logger.info(
                    f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[1]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[1]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[1]['Username']
                logger.info(
                    f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")

                portal_date_time_refund = transaction_details[0]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time_refund}")
                portal_txn_id_refund = transaction_details[0]['Transaction ID']
                logger.info(
                    f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id_refund}")
                portal_total_amount_refund = transaction_details[0]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount_refund}")
                portal_auth_code_refund = transaction_details[0]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code_refund}")
                portal_rrn_refund = transaction_details[0]['RR Number']
                logger.info(
                    f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn_refund}")
                portal_txn_type_refund = transaction_details[0]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type_refund}")
                portal_txn_status_refund = transaction_details[0]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status_refund}")
                portal_user_refund = transaction_details[0]['Username']
                logger.info(
                    f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user_refund}")

                actual_portal_values = {
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "auth_code": portal_auth_code,
                    "rrn": portal_rrn,
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type_2": portal_txn_type_refund,
                    "txn_amt_2": portal_total_amount_refund.split(' ')[1],
                    "username_2": portal_user_refund,
                    "txn_id_2": portal_txn_id_refund,
                    "auth_code_2": portal_auth_code_refund,
                    "rrn_2": portal_rrn_refund,
                    "date_time_2": portal_date_time_refund,
                    "pmt_status_2": portal_txn_status_refund
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=refund_created_time)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(total_amount),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": refund_rrn,
                    "AUTH CODE": refund_auth_code,
                    "CARD TYPE": "VISA",
                    "BATCH NO": refund_batch_number,
                    "TID": tid,
                    "payment_option": "REFUND"
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=refund_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
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
def test_common_100_115_01_011():
    """
    Sub Feature Code: UI_Common_Card_Sale_Tip_Refund_Api_Txn_HDFC_Dummy_EMVCTLS_MASTER_DebitCard_Without_pin_222360
    Sub Feature Description: Performing the EMVCTLS sale tip refund Api transaction via HDFC Dummy PG using MASTER Debit
    card having 16 digit PAN length without pin (bin:222360)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 01: Sale+Tip, 011: TC011
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].values[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result['id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details(api_name='org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["tipEnabled"] = "true"
        api_details["RequestBody"]["settings"]["tipPercentage"] = "10"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for tip option to be enabled and setting tip "
                     f"percentage 10 :  {response}")

        query = f"select bank_code from bin_info where bin='222360'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

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
            amount = random.randint(10, 300)
            max_tip_amount = int((amount * 10) / 100)
            tip_amount = random.randint(1, max_tip_amount)
            total_amount = amount + tip_amount
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_tip_and_amount_and_order_number_and_device_serial_for_card(amt=amount,
                                                                                       order_number=order_id,
                                                                                       tip_amt=tip_amount,
                                                                                       device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered tip_amount is : {tip_amount}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card_with_tip(amount=amount, order_id=order_id,
                                                                 tip_amt=tip_amount, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info(f"Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : CTLS_MASTER_DEBIT_222360")
            card_page.select_cardtype(text="CTLS_MASTER_DEBIT_222360")
            logger.debug(f"Selected the card type as : CTLS_MASTER_DEBIT_222360")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details(api_name='Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details  : {api_details} ")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Settlement api is : {settle_response}")

            query = f"select id from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn id from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details(api_name='Offline_Refund', request_body={
                "amount": total_amount,
                "originalTransactionId": txn_id,
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API details  : {api_details} ")
            refund_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {refund_response}")
            refund_txn_id = refund_response.get('txnId')
            logger.debug(f"From response fetch txn_id : {refund_txn_id}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch txn details for original txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table for original txn : {result}")
            total_amount_txn = result['amount'].values[0]
            logger.debug(f"Query result, amount : {total_amount_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, acquirer_code : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, settlement_status : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Query result, status : {pmt_status}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Query result, issuer_code : {issuer_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type : {txn_type}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Query result, state : {pmt_state}")
            bank_name = result['bank_name'].values[0]
            logger.debug(f"Query result, bank_name : {bank_name}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, payment_gateway : {payment_gateway}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Query result, batch_number : {batch_number}")
            amount_additional = result['amount_additional'].values[0]
            logger.debug(f"Query result, amount_additional : {amount_additional}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Query result, payment_card_brand : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, payment_card_type : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Query result, card_last_four_digit : {card_last_four_digit}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode : {payment_mode}")
            amount_original = result['amount_original'].values[0]
            logger.debug(f"Query result, amount_original : {amount_original}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Query result, merchant_name : {merchant_name}")
            pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Query result, payment_card_bin : {pmt_card_bin}")
            terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Query result, terminal_info_id : {terminal_info_id_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Query result, mid : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Query result, tid : {tid_txn}")
            device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial : {device_serial_txn}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Query result, order_id : {order_id_txn}")
            card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Query result, card_txn_type : {card_txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code_txn}")

            query = f"select * from txn where id = '{refund_txn_id}'"
            logger.debug(f"Query to fetch txn details for refund txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table :{result}")
            logger.debug(f"Fetching result from txn table for refund txn : {result}")
            refund_total_amount_txn = result['amount'].values[0]
            logger.debug(f"Query result, amount : {refund_total_amount_txn}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time : {refund_created_time}")
            refund_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, acquirer_code : {refund_acquirer_code}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code : {refund_auth_code}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name : {refund_payer_name}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {refund_rrn}")
            refund_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, settlement_status : {refund_settle_status}")
            refund_pmt_status = result['status'].values[0]
            logger.debug(f"Query result, status : {refund_pmt_status}")
            refund_issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Query result, issuer_code : {refund_issuer_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type : {refund_txn_type}")
            refund_pmt_state = result['state'].values[0]
            logger.debug(f"Query result, state : {refund_pmt_state}")
            refund_bank_name = result['bank_name'].values[0]
            logger.debug(f"Query result, bank_name : {refund_bank_name}")
            refund_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, payment_gateway : {refund_payment_gateway}")
            refund_batch_number = result['batch_number'].values[0]
            logger.debug(f"Query result, batch_number : {refund_batch_number}")
            refund_amount_additional = result['amount_additional'].values[0]
            logger.debug(f"Query result, amount_additional : {refund_amount_additional}")
            refund_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Query result, payment_card_brand : {refund_pmt_card_brand}")
            refund_pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, payment_card_type : {refund_pmt_card_type}")
            refund_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Query result, card_last_four_digit : {refund_card_last_four_digit}")
            refund_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode : {refund_payment_mode}")
            refund_amount_original = result['amount_original'].values[0]
            logger.debug(f"Query result, amount_original : {refund_amount_original}")
            refund_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Query result, merchant_name : {refund_merchant_name}")
            refund_pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Query result, payment_card_bin : {refund_pmt_card_bin}")
            refund_terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Query result, terminal_info_id : {refund_terminal_info_id_txn}")
            refund_mid_txn = result['mid'].values[0]
            logger.debug(f"Query result, mid : {refund_mid_txn}")
            refund_tid_txn = result['tid'].values[0]
            logger.debug(f"Query result, tid : {refund_tid_txn}")
            refund_device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial : {refund_device_serial_txn}")
            refund_order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Query result, order_id : {refund_order_id_txn}")
            refund_card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Query result, card_txn_type : {refund_card_txn_type}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {refund_org_code_txn}")

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
                date_time = date_time_converter.to_app_format(posting_date_db=created_time)
                refund_date_and_time = date_time_converter.to_app_format(posting_date_db=refund_created_time)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(total_amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_time,
                    "device_serial": device_serial,
                    "batch_number": batch_number,
                    "tip_amt": "{:,.2f}".format(tip_amount),
                    "card_type_desc": "*0011 CTLS",
                    "mid": mid,
                    "tid": tid,
                    "txn_amt_2": "{:,.2f}".format(total_amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": refund_txn_id,
                    "pmt_status_2": "REFUNDED",
                    "rr_number_2": refund_rrn,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "settle_status_2": "PENDING",
                    "auth_code_2": refund_auth_code,
                    "date_2": refund_date_and_time,
                    "device_serial_2": device_serial,
                    "batch_number_2": refund_batch_number,
                    "card_type_desc_2": "*0011 CTLS",
                    "mid_2": mid,
                    "tid_2": tid
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.info(f"reseting the app_driver to login again in the MPOSX application")
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the txn : {txn_id}, {app_batch_number}")
                app_tip_amt = txn_history_page.fetch_tip_amt_text()
                logger.info(f"Fetching tip_amt from txn history for the txn : {txn_id}, {app_tip_amt}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the txn : {txn_id}, {app_card_type_desc}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_refund = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {refund_txn_id}, {app_amount_refund}")
                app_order_id_refund = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {refund_txn_id}, {app_order_id_refund}")
                app_payment_msg_refund = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {refund_txn_id}, {app_payment_msg_refund}")
                app_payment_mode_refund = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {refund_txn_id}, {app_payment_mode_refund}")
                app_payment_status_refund = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {refund_txn_id}, {app_payment_status_refund}")
                app_txn_id_refund = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {refund_txn_id}, {app_txn_id_refund}")
                app_date_time_refund = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {refund_txn_id}, {app_date_time_refund}")
                app_settle_status_refund = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the txn : {refund_txn_id}, {app_settle_status_refund}")
                app_rrn_refund = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {refund_txn_id}, {app_rrn_refund}")
                app_auth_code_refund = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {refund_txn_id}, {app_auth_code_refund}")
                app_device_serial_refund = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the txn : {refund_txn_id}, {app_device_serial_refund}")
                app_batch_number_refund = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the txn : {refund_txn_id}, {app_batch_number_refund}")
                app_card_type_desc_refund = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the txn : {refund_txn_id}, {app_card_type_desc_refund}")
                app_mid_refund = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {refund_txn_id}, {app_mid_refund}")
                app_tid_refund = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {refund_txn_id}, {app_tid_refund}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": app_payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settle_status,
                    "auth_code": app_auth_code,
                    "date": app_date_time,
                    "device_serial": app_device_serial,
                    "batch_number": app_batch_number,
                    "tip_amt": app_tip_amt.split(' ')[1],
                    "card_type_desc": app_card_type_desc,
                    "mid": app_mid,
                    "tid": app_tid,
                    "txn_amt_2": app_amount_refund.split(' ')[1],
                    "pmt_mode_2": app_payment_mode_refund,
                    "txn_id_2": app_txn_id_refund,
                    "pmt_status_2": app_payment_status_refund.split(':')[1],
                    "rr_number_2": app_rrn_refund,
                    "order_id_2": app_order_id_refund,
                    "pmt_msg_2": app_payment_msg_refund,
                    "settle_status_2": app_settle_status_refund,
                    "auth_code_2": app_auth_code_refund,
                    "date_2": app_date_time_refund,
                    "device_serial_2": app_device_serial_refund,
                    "batch_number_2": app_batch_number_refund,
                    "card_type_desc_2": app_card_type_desc_refund,
                    "mid_2": app_mid_refund,
                    "tid_2": app_tid_refund
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
                date_time = date_time_converter.db_datetime(date_from_db=created_time)
                refund_date_and_time = date_time_converter.db_datetime(date_from_db=refund_created_time)
                expected_api_values = {
                    "txn_amt": float(total_amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "rrn": rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "org_code": org_code,
                    "tip_amt": float(tip_amount),
                    "batch_number": batch_number,
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "DEBIT",
                    "date": date_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "CTLS",
                    "amt_original": float(amount),
                    "auth_code": auth_code,
                    "card_last_four_digit": "0011",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "222360",
                    "card_type": "MasterCard",
                    "display_pan": "0011",
                    "txn_amt_2": float(total_amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "mid_2": mid,
                    "tid_2": tid,
                    "acquirer_code_2": "HDFC",
                    "settle_status_2": "PENDING",
                    "rrn_2": refund_rrn,
                    "issuer_code_2": None,
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "tip_amt_2": float(0.0),
                    "batch_number_2": refund_batch_number,
                    "pmt_card_brand_2": "MASTER_CARD",
                    "pmt_card_type_2": "DEBIT",
                    "date_2": refund_date_and_time,
                    "device_serial_2": None,
                    "card_txn_type_desc_2": "CTLS",
                    "amt_original_2": float(total_amount),
                    "auth_code_2": refund_auth_code,
                    "card_last_four_digit_2": "0011",
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": merchant_name,
                    "pmt_card_bin_2": "222360",
                    "card_type_2": "MasterCard",
                    "display_pan_2": "0011",
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for transaction list : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_original = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_original}")
                api_amount = response_original.get('amount')
                logger.debug(f"From response_original fetch amount : {api_amount}")
                api_payment_mode = response_original.get('paymentMode')
                logger.debug(f"From response_original fetch payment_mode : {api_payment_mode}")
                api_payment_status = response_original.get('status')
                logger.debug(f"From response_original fetch payment_status : {api_payment_status}")
                api_payment_state = response_original.get('states')[0]
                logger.debug(f"From response_original fetch payment_state : {api_payment_state}")
                api_mid = response_original.get('mid')
                logger.debug(f"From response_original fetch mid : {api_mid}")
                api_tid = response_original.get('tid')
                logger.debug(f"From response_original fetch tid : {api_tid}")
                api_acquirer_code = response_original.get('acquirerCode')
                logger.debug(f"From response_original fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response_original.get('settlementStatus')
                logger.debug(f"From response_original fetch settlement_status : {api_settle_status}")
                api_rrn = response_original.get('rrNumber')
                logger.debug(f"From response_original fetch rrn : {api_rrn}")
                api_issuer_code = response_original.get('issuerCode')
                logger.debug(f"From response_original fetch issuer_code : {api_issuer_code}")
                api_txn_type = response_original.get('txnType')
                logger.debug(f"From response_original fetch txn_type : {api_txn_type}")
                api_org_code = response_original.get('orgCode')
                logger.debug(f"From response_original fetch org_code : {api_org_code}")
                api_tip_amt = response_original.get('amountAdditional')
                logger.debug(f"From response_original fetch tip_amt : {api_tip_amt}")
                api_batch_number = response_original.get('batchNumber')
                logger.debug(f"From response_original fetch batch_number : {api_batch_number}")
                api_pmt_card_brand = response_original.get('paymentCardBrand')
                logger.debug(f"From response_original fetch payment_card_brand : {api_pmt_card_brand}")
                api_pmt_card_type = response_original.get('paymentCardType')
                logger.debug(f"From response_original fetch payment_card_type : {api_pmt_card_type}")
                api_date_time = response_original.get('createdTime')
                logger.debug(f"From response_original fetch date_time : {api_date_time}")
                api_device_serial = response_original.get('deviceSerial')
                logger.debug(f"From response_original fetch device_serial : {api_device_serial}")
                api_card_txn_type_desc = response_original.get('cardTxnTypeDesc')
                logger.debug(f"From response_original fetch card_txn_type_desc : {api_card_txn_type_desc}")
                api_amount_original = response_original.get('amountOriginal')
                logger.debug(f"From response_original fetch amount_original : {api_amount_original}")
                api_merchant_name = response_original.get('merchantName')
                logger.debug(f"From response_original fetch merchant_name : {api_merchant_name}")
                api_card_last_four_digit = response_original.get('cardLastFourDigit')
                logger.debug(f"From response_original fetch card_last_four_digit : {api_card_last_four_digit}")
                api_ext_ref_number = response_original.get('externalRefNumber')
                logger.debug(f"From response_original fetch external_ref_number : {api_ext_ref_number}")
                api_pmt_card_bin = response_original.get('paymentCardBin')
                logger.debug(f"From response_original fetch payment_card_bin : {api_pmt_card_bin}")
                api_display_pan = response_original.get('displayPAN')
                logger.debug(f"From response_original fetch display_pan : {api_display_pan}")
                api_auth_code = response_original.get('authCode')
                logger.debug(f"From response_original fetch auth_code : {api_auth_code}")
                api_card_type = response_original.get('cardType')
                logger.debug(f"From response_original fetch card_type : {api_card_type}")

                response_refund = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn is : {response_refund}")
                api_amount_refund = response_refund.get('amount')
                logger.debug(f"From response_refund fetch amount : {api_amount_refund}")
                api_payment_mode_refund = response_refund.get('paymentMode')
                logger.debug(f"From response_refund fetch payment_mode : {api_payment_mode_refund}")
                api_payment_status_refund = response_refund.get('status')
                logger.debug(f"From response_refund fetch payment_status : {api_payment_status_refund}")
                api_payment_state_refund = response_refund.get('states')[0]
                logger.debug(f"From response_refund fetch payment_state : {api_payment_state_refund}")
                api_mid_refund = response_refund.get('mid')
                logger.debug(f"From response_refund fetch mid : {api_mid_refund}")
                api_tid_refund = response_refund.get('tid')
                logger.debug(f"From response_refund fetch tid : {api_tid_refund}")
                api_acquirer_code_refund = response_refund.get('acquirerCode')
                logger.debug(f"From response_refund fetch acquirer_code : {api_acquirer_code_refund}")
                api_settle_status_refund = response_refund.get('settlementStatus')
                logger.debug(f"From response_refund fetch settlement_status : {api_settle_status_refund}")
                api_rrn_refund = response_refund.get('rrNumber')
                logger.debug(f"From response_refund fetch rrn : {api_rrn_refund}")
                api_issuer_code_refund = response_refund.get('issuerCode')
                logger.debug(f"From response_refund fetch issuer_code : {api_issuer_code_refund}")
                api_txn_type_refund = response_refund.get('txnType')
                logger.debug(f"From response_refund fetch txn_type : {api_txn_type_refund}")
                api_org_code_refund = response_refund.get('orgCode')
                logger.debug(f"From response_refund fetch org_code : {api_org_code_refund}")
                api_tip_amt_refund = response_refund.get('amountAdditional')
                logger.debug(f"From response_refund fetch tip_amt : {api_tip_amt_refund}")
                api_batch_number_refund = response_refund.get('batchNumber')
                logger.debug(f"From response_refund fetch batch_number : {api_batch_number_refund}")
                api_pmt_card_brand_refund = response_refund.get('paymentCardBrand')
                logger.debug(f"From response_refund fetch payment_card_brand : {api_pmt_card_brand_refund}")
                api_pmt_card_type_refund = response_refund.get('paymentCardType')
                logger.debug(f"From response_refund fetch payment_card_type : {api_pmt_card_type_refund}")
                api_date_time_refund = response_refund.get('createdTime')
                logger.debug(f"From response_refund fetch date_time : {api_date_time_refund}")
                api_device_serial_refund = response_refund.get('deviceSerial')
                logger.debug(f"From response_refund fetch device_serial : {api_device_serial_refund}")
                api_card_txn_type_desc_refund = response_refund.get('cardTxnTypeDesc')
                logger.debug(f"From response_refund fetch card_txn_type_desc : {api_card_txn_type_desc_refund}")
                api_amount_original_refund = response_refund.get('amountOriginal')
                logger.debug(f"From response_refund fetch amount_original : {api_amount_original_refund}")
                api_merchant_name_refund = response_refund.get('merchantName')
                logger.debug(f"From response_refund fetch merchant_name : {api_merchant_name_refund}")
                api_card_last_four_digit_refund = response_refund.get('cardLastFourDigit')
                logger.debug(f"From response_refund fetch card_last_four_digit : {api_card_last_four_digit_refund}")
                api_ext_ref_number_refund = response_refund.get('externalRefNumber')
                logger.debug(f"From response_refund fetch external_ref_number : {api_ext_ref_number_refund}")
                api_pmt_card_bin_refund = response_refund.get('paymentCardBin')
                logger.debug(f"From response_refund fetch payment_card_bin : {api_pmt_card_bin_refund}")
                api_display_pan_refund = response_refund.get('displayPAN')
                logger.debug(f"From response_refund fetch display_pan : {api_display_pan_refund}")
                api_auth_code_refund = response_refund.get('authCode')
                logger.debug(f"From response_refund fetch auth_code : {api_auth_code_refund}")
                api_card_type_refund = response_refund.get('cardType')
                logger.debug(f"From response_refund fetch card_type : {api_card_type_refund}")

                actual_api_values = {
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_status": api_payment_status,
                    "pmt_state": api_payment_state,
                    "mid": api_mid,
                    "tid": api_tid,
                    "acquirer_code": api_acquirer_code,
                    "settle_status": api_settle_status,
                    "rrn": api_rrn,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "org_code": api_org_code,
                    "tip_amt": api_tip_amt,
                    "batch_number": api_batch_number,
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
                    "card_txn_type_desc": api_card_txn_type_desc,
                    "amt_original": api_amount_original,
                    "auth_code": api_auth_code,
                    "card_last_four_digit": api_card_last_four_digit,
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "pmt_card_bin": api_pmt_card_bin,
                    "card_type": api_card_type,
                    "display_pan": api_display_pan,
                    "txn_amt_2": api_amount_refund,
                    "pmt_mode_2": api_payment_mode_refund,
                    "pmt_status_2": api_payment_status_refund,
                    "pmt_state_2": api_payment_state_refund,
                    "mid_2": api_mid_refund,
                    "tid_2": api_tid_refund,
                    "acquirer_code_2": api_acquirer_code_refund,
                    "settle_status_2": api_settle_status_refund,
                    "rrn_2": api_rrn_refund,
                    "issuer_code_2": api_issuer_code_refund,
                    "txn_type_2": api_txn_type_refund,
                    "org_code_2": api_org_code_refund,
                    "tip_amt_2": api_tip_amt_refund,
                    "batch_number_2": api_batch_number_refund,
                    "pmt_card_brand_2": api_pmt_card_brand,
                    "pmt_card_type_2": api_pmt_card_type_refund,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_refund),
                    "device_serial_2": api_device_serial_refund,
                    "card_txn_type_desc_2": api_card_txn_type_desc_refund,
                    "amt_original_2": api_amount_original_refund,
                    "auth_code_2": api_auth_code_refund,
                    "card_last_four_digit_2": api_card_last_four_digit_refund,
                    "ext_ref_number_2": api_ext_ref_number_refund,
                    "merchant_name_2": api_merchant_name_refund,
                    "pmt_card_bin_2": api_pmt_card_bin_refund,
                    "card_type_2": api_card_type_refund,
                    "display_pan_2": api_display_pan_refund,
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
                    "txn_amt": float(total_amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": None,
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "txn_type": "CHARGE",
                    "settle_status": "SETTLED",
                    "tip_amt": float(tip_amount),
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "DEBIT",
                    "amt_original": float(amount),
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "222360",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "91",
                    "card_last_four_digit": "0011",
                    "customer_name": None,
                    "txn_amt_2": float(total_amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": None,
                    "payer_name_2": None,
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "txn_type_2": "REFUND",
                    "settle_status_2": "PENDING",
                    "tip_amt_2": float(0.0),
                    "pmt_card_brand_2": "MASTER_CARD",
                    "pmt_card_type_2": "DEBIT",
                    "amt_original_2": float(total_amount),
                    "device_serial_2": None,
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "222360",
                    "terminal_info_id_2": terminal_info_id,
                    "card_txn_type_2": "91",
                    "card_last_four_digit_2": "0011",
                    "customer_name_2": None
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": total_amount_txn,
                    "pmt_mode": payment_mode,
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "payer_name": payer_name,
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "pmt_gateway": payment_gateway,
                    "txn_type": txn_type,
                    "settle_status": settle_status,
                    "tip_amt": amount_additional,
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "amt_original": amount_original,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "terminal_info_id": terminal_info_id_txn,
                    "card_txn_type": card_txn_type,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name,
                    "txn_amt_2": refund_total_amount_txn,
                    "pmt_mode_2": refund_payment_mode,
                    "pmt_status_2": refund_pmt_status,
                    "pmt_state_2": refund_pmt_state,
                    "acquirer_code_2": refund_acquirer_code,
                    "issuer_code_2": refund_issuer_code_txn,
                    "payer_name_2": refund_payer_name,
                    "mid_2": refund_mid_txn,
                    "tid_2": refund_tid_txn,
                    "pmt_gateway_2": refund_payment_gateway,
                    "txn_type_2": refund_txn_type,
                    "settle_status_2": refund_settle_status,
                    "tip_amt_2": refund_amount_additional,
                    "pmt_card_brand_2": refund_pmt_card_brand,
                    "pmt_card_type_2": refund_pmt_card_type,
                    "amt_original_2": refund_amount_original,
                    "device_serial_2": refund_device_serial_txn,
                    "order_id_2": refund_order_id_txn,
                    "org_code_2": refund_org_code_txn,
                    "pmt_card_bin_2": refund_pmt_card_bin,
                    "terminal_info_id_2": refund_terminal_info_id_txn,
                    "card_txn_type_2": refund_card_txn_type,
                    "card_last_four_digit_2": refund_card_last_four_digit,
                    "customer_name_2": refund_customer_name
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
                date_time = date_time_converter.to_portal_format(created_date_db=created_time)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                expected_portal_values = {
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(total_amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_time,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(total_amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "auth_code_2": refund_auth_code,
                    "rrn_2": refund_rrn,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[1]['Transaction ID']
                logger.info(
                    f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[1]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_auth_code = transaction_details[1]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")
                portal_rrn = transaction_details[1]['RR Number']
                logger.info(
                    f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[1]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[1]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[1]['Username']
                logger.info(
                    f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")

                portal_date_time_refund = transaction_details[0]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time_refund}")
                portal_txn_id_refund = transaction_details[0]['Transaction ID']
                logger.info(
                    f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id_refund}")
                portal_total_amount_refund = transaction_details[0]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount_refund}")
                portal_auth_code_refund = transaction_details[0]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code_refund}")
                portal_rrn_refund = transaction_details[0]['RR Number']
                logger.info(
                    f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn_refund}")
                portal_txn_type_refund = transaction_details[0]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type_refund}")
                portal_txn_status_refund = transaction_details[0]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status_refund}")
                portal_user_refund = transaction_details[0]['Username']
                logger.info(
                    f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user_refund}")

                actual_portal_values = {
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "auth_code": portal_auth_code,
                    "rrn": portal_rrn,
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type_2": portal_txn_type_refund,
                    "txn_amt_2": portal_total_amount_refund.split(' ')[1],
                    "username_2": portal_user_refund,
                    "txn_id_2": portal_txn_id_refund,
                    "auth_code_2": portal_auth_code_refund,
                    "rrn_2": portal_rrn_refund,
                    "date_time_2": portal_date_time_refund,
                    "pmt_status_2": portal_txn_status_refund
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=refund_created_time)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(total_amount),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": refund_rrn,
                    "AUTH CODE": refund_auth_code,
                    "CARD TYPE": "MasterCard",
                    "BATCH NO": refund_batch_number,
                    "TID": tid,
                    "payment_option": "REFUND"
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=refund_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
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
def test_common_100_115_01_012():
    """
    Sub Feature Code: UI_Common_Card_Sale_Tip_Refund_Api_Txn_HDFC_Dummy_EMVCTLS_RUPAY_DebitCard_Without_pin_608326
    Sub Feature Description: Performing the EMVCTLS sale tip refund Api transaction via HDFC Dummy PG using RUPAY Debit
    card having 16 digit PAN length without pin (bin:608326)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 01: Sale+Tip, 012: TC012
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].values[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result['id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details(api_name='org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["tipEnabled"] = "true"
        api_details["RequestBody"]["settings"]["tipPercentage"] = "10"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for tip option to be enabled and setting tip "
                     f"percentage 10 :  {response}")

        query = f"select bank_code from bin_info where bin='608326'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

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
            amount = random.randint(10, 300)
            max_tip_amount = int((amount * 10) / 100)
            tip_amount = random.randint(1, max_tip_amount)
            total_amount = amount + tip_amount
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_tip_and_amount_and_order_number_and_device_serial_for_card(amt=amount,
                                                                                       order_number=order_id,
                                                                                       tip_amt=tip_amount,
                                                                                       device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered tip_amount is : {tip_amount}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card_with_tip(amount=amount, order_id=order_id,
                                                                 tip_amt=tip_amount, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info(f"Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : CTLS_RUPAY_DEBIT_608326")
            card_page.select_cardtype(text="CTLS_RUPAY_DEBIT_608326")
            logger.debug(f"Selected the card type as : CTLS_RUPAY_DEBIT_608326")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details(api_name='Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details  : {api_details} ")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Settlement api is : {settle_response}")

            query = f"select id from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn id from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details(api_name='Offline_Refund', request_body={
                "amount": total_amount,
                "originalTransactionId": txn_id,
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API details  : {api_details} ")
            refund_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {refund_response}")
            refund_txn_id = refund_response.get('txnId')
            logger.debug(f"From response fetch txn_id : {refund_txn_id}")

            query = f"select * from txn where org_code = '{org_code}' And id = '{txn_id}'"
            logger.debug(f"Query to fetch txn details for original txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table for original txn : {result}")
            total_amount_txn = result['amount'].values[0]
            logger.debug(f"Query result, amount : {total_amount_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, acquirer_code : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, settlement_status : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Query result, status : {pmt_status}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Query result, issuer_code : {issuer_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type : {txn_type}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Query result, state : {pmt_state}")
            bank_name = result['bank_name'].values[0]
            logger.debug(f"Query result, bank_name : {bank_name}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, payment_gateway : {payment_gateway}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Query result, batch_number : {batch_number}")
            amount_additional = result['amount_additional'].values[0]
            logger.debug(f"Query result, amount_additional : {amount_additional}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Query result, payment_card_brand : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, payment_card_type : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Query result, card_last_four_digit : {card_last_four_digit}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode : {payment_mode}")
            amount_original = result['amount_original'].values[0]
            logger.debug(f"Query result, amount_original : {amount_original}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Query result, merchant_name : {merchant_name}")
            pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Query result, payment_card_bin : {pmt_card_bin}")
            terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Query result, terminal_info_id : {terminal_info_id_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Query result, mid : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Query result, tid : {tid_txn}")
            device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial : {device_serial_txn}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Query result, order_id : {order_id_txn}")
            card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Query result, card_txn_type : {card_txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code_txn}")

            query = f"select * from txn where org_code = '{org_code}' And id = '{refund_txn_id}'"
            logger.debug(f"Query to fetch txn details for refund txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table for refund txn : {result}")
            refund_total_amount_txn = result['amount'].values[0]
            logger.debug(f"Query result, amount : {refund_total_amount_txn}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time : {refund_created_time}")
            refund_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, acquirer_code : {refund_acquirer_code}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code : {refund_auth_code}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name : {refund_payer_name}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {refund_rrn}")
            refund_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, settlement_status : {refund_settle_status}")
            refund_pmt_status = result['status'].values[0]
            logger.debug(f"Query result, status : {refund_pmt_status}")
            refund_issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Query result, issuer_code : {refund_issuer_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type : {refund_txn_type}")
            refund_pmt_state = result['state'].values[0]
            logger.debug(f"Query result, state : {refund_pmt_state}")
            refund_bank_name = result['bank_name'].values[0]
            logger.debug(f"Query result, bank_name : {refund_bank_name}")
            refund_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, payment_gateway : {refund_payment_gateway}")
            refund_batch_number = result['batch_number'].values[0]
            logger.debug(f"Query result, batch_number : {refund_batch_number}")
            refund_amount_additional = result['amount_additional'].values[0]
            logger.debug(f"Query result, amount_additional : {refund_amount_additional}")
            refund_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Query result, payment_card_brand : {refund_pmt_card_brand}")
            refund_pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, payment_card_type : {refund_pmt_card_type}")
            refund_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Query result, card_last_four_digit : {refund_card_last_four_digit}")
            refund_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode : {refund_payment_mode}")
            refund_amount_original = result['amount_original'].values[0]
            logger.debug(f"Query result, amount_original : {refund_amount_original}")
            refund_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Query result, merchant_name : {refund_merchant_name}")
            refund_pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Query result, payment_card_bin : {refund_pmt_card_bin}")
            refund_terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Query result, terminal_info_id : {refund_terminal_info_id_txn}")
            refund_mid_txn = result['mid'].values[0]
            logger.debug(f"Query result, mid : {refund_mid_txn}")
            refund_tid_txn = result['tid'].values[0]
            logger.debug(f"Query result, tid : {refund_tid_txn}")
            refund_device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial : {refund_device_serial_txn}")
            refund_order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Query result, order_id : {refund_order_id_txn}")
            refund_card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Query result, refund_card_txn_type : {refund_card_txn_type}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {refund_org_code_txn}")

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
                date_time = date_time_converter.to_app_format(posting_date_db=created_time)
                refund_date_and_time = date_time_converter.to_app_format(posting_date_db=refund_created_time)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(total_amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "customer_name": "RUPAY CARD IMAGE 01",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_time,
                    "device_serial": device_serial,
                    "batch_number": batch_number,
                    "tip_amt": "{:,.2f}".format(tip_amount),
                    "card_type_desc": "*0017 CTLS",
                    "mid": mid,
                    "tid": tid,
                    "txn_amt_2": "{:,.2f}".format(total_amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": refund_txn_id,
                    "pmt_status_2": "REFUNDED",
                    "rr_number_2": refund_rrn,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "customer_name_2": "RUPAY CARD IMAGE 01",
                    "settle_status_2": "PENDING",
                    "auth_code_2": refund_auth_code,
                    "date_2": refund_date_and_time,
                    "device_serial_2": device_serial,
                    "batch_number_2": refund_batch_number,
                    "card_type_desc_2": "*0017 CTLS",
                    "mid_2": mid,
                    "tid_2": tid
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.info(f"reseting the app_driver to login again in the MPOSX application")
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the txn : {txn_id}, {app_batch_number}")
                app_tip_amt = txn_history_page.fetch_tip_amt_text()
                logger.info(f"Fetching tip_amt from txn history for the txn : {txn_id}, {app_tip_amt}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the txn : {txn_id}, {app_card_type_desc}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_refund = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {refund_txn_id}, {app_amount_refund}")
                app_order_id_refund = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {refund_txn_id}, {app_order_id_refund}")
                app_payment_msg_refund = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {refund_txn_id}, {app_payment_msg_refund}")
                app_payment_mode_refund = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {refund_txn_id}, {app_payment_mode_refund}")
                app_payment_status_refund = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {refund_txn_id}, {app_payment_status_refund}")
                app_txn_id_refund = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {refund_txn_id}, {app_txn_id_refund}")
                app_customer_name_refund = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {refund_txn_id}, {app_customer_name_refund}")
                app_date_time_refund = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {refund_txn_id}, {app_date_time_refund}")
                app_settle_status_refund = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settle_status from txn history for the txn : {refund_txn_id}, {app_settle_status_refund}")
                app_rrn_refund = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching app_rrn_refund from txn history for the txn : {refund_txn_id}, {app_rrn_refund}")
                app_auth_code_refund = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {refund_txn_id}, {app_auth_code_refund}")
                app_device_serial_refund = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the txn : {refund_txn_id}, {app_device_serial_refund}")
                app_batch_number_refund = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the txn : {refund_txn_id}, {app_batch_number_refund}")
                app_card_type_desc_refund = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the txn : {refund_txn_id}, {app_card_type_desc_refund}")
                app_mid_refund = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {refund_txn_id}, {app_mid_refund}")
                app_tid_refund = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {refund_txn_id}, {app_tid_refund}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": app_payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "customer_name": app_customer_name,
                    "settle_status": app_settle_status,
                    "auth_code": app_auth_code,
                    "date": app_date_time,
                    "device_serial": app_device_serial,
                    "batch_number": app_batch_number,
                    "tip_amt": app_tip_amt.split(' ')[1],
                    "card_type_desc": app_card_type_desc,
                    "mid": app_mid,
                    "tid": app_tid,
                    "txn_amt_2": app_amount_refund.split(' ')[1],
                    "pmt_mode_2": app_payment_mode_refund,
                    "txn_id_2": app_txn_id_refund,
                    "pmt_status_2": app_payment_status_refund.split(':')[1],
                    "rr_number_2": app_rrn_refund,
                    "order_id_2": app_order_id_refund,
                    "pmt_msg_2": app_payment_msg_refund,
                    "customer_name_2": app_customer_name_refund,
                    "settle_status_2": app_settle_status_refund,
                    "auth_code_2": app_auth_code_refund,
                    "date_2": app_date_time_refund,
                    "device_serial_2": app_device_serial_refund,
                    "batch_number_2": app_batch_number_refund,
                    "card_type_desc_2": app_card_type_desc_refund,
                    "mid_2": app_mid_refund,
                    "tid_2": app_tid_refund
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
                date_time = date_time_converter.db_datetime(date_from_db=created_time)
                refund_date_and_time = date_time_converter.db_datetime(date_from_db=refund_created_time)
                expected_api_values = {
                    "txn_amt": float(total_amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "rrn": rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "org_code": org_code,
                    "tip_amt": float(tip_amount),
                    "batch_number": batch_number,
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "date": date_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "CTLS",
                    "amt_original": float(amount),
                    "auth_code": auth_code,
                    "card_last_four_digit": "0017",
                    "customer_name": "RUPAY CARD IMAGE 01      /",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "RUPAY CARD IMAGE 01      /",
                    "pmt_card_bin": "608326",
                    "card_type": "RUPAY",
                    "display_pan": "0017",
                    "name_on_card": "RUPAY CARD IMAGE 01      /",
                    "txn_amt_2": float(total_amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "mid_2": mid,
                    "tid_2": tid,
                    "acquirer_code_2": "HDFC",
                    "settle_status_2": "PENDING",
                    "rrn_2": refund_rrn,
                    "issuer_code_2": None,
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "tip_amt_2": float(0.0),
                    "batch_number_2": refund_batch_number,
                    "pmt_card_brand_2": "RUPAY",
                    "pmt_card_type_2": "DEBIT",
                    "date_2": refund_date_and_time,
                    "device_serial_2": None,
                    "card_txn_type_desc_2": "CTLS",
                    "amt_original_2": float(total_amount),
                    "auth_code_2": refund_auth_code,
                    "card_last_four_digit_2": "0017",
                    "customer_name_2": "RUPAY CARD IMAGE 01      /",
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": merchant_name,
                    "payer_name_2": "RUPAY CARD IMAGE 01      /",
                    "pmt_card_bin_2": "608326",
                    "card_type_2": "RUPAY",
                    "display_pan_2": "0017",
                    "name_on_card_2": "RUPAY CARD IMAGE 01      /"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for transaction list : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_original = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_original}")
                api_amount = response_original.get('amount')
                logger.debug(f"From response_original fetch amount : {api_amount}")
                api_payment_mode = response_original.get('paymentMode')
                logger.debug(f"From response_original fetch payment_mode : {api_payment_mode}")
                api_payment_status = response_original.get('status')
                logger.debug(f"From response_original fetch payment_status : {api_payment_status}")
                api_payment_state = response_original.get('states')[0]
                logger.debug(f"From response_original fetch payment_state : {api_payment_state}")
                api_mid = response_original.get('mid')
                logger.debug(f"From response_original fetch mid : {api_mid}")
                api_tid = response_original.get('tid')
                logger.debug(f"From response_original fetch tid : {api_tid}")
                api_acquirer_code = response_original.get('acquirerCode')
                logger.debug(f"From response_original fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response_original.get('settlementStatus')
                logger.debug(f"From response_original fetch settlement_status : {api_settle_status}")
                api_rrn = response_original.get('rrNumber')
                logger.debug(f"From response_original fetch rrn : {api_rrn}")
                api_issuer_code = response_original.get('issuerCode')
                logger.debug(f"From response_original fetch issuer_code : {api_issuer_code}")
                api_txn_type = response_original.get('txnType')
                logger.debug(f"From response_original fetch txn_type : {api_txn_type}")
                api_org_code = response_original.get('orgCode')
                logger.debug(f"From response_original fetch org_code : {api_org_code}")
                api_tip_amt = response_original.get('amountAdditional')
                logger.debug(f"From response_original fetch tip_amt : {api_tip_amt}")
                api_batch_number = response_original.get('batchNumber')
                logger.debug(f"From response_original fetch batch_number : {api_batch_number}")
                api_pmt_card_brand = response_original.get('paymentCardBrand')
                logger.debug(f"From response_original fetch payment_card_brand : {api_pmt_card_brand}")
                api_pmt_card_type = response_original.get('paymentCardType')
                logger.debug(f"From response_original fetch payment_card_type : {api_pmt_card_type}")
                api_date_time = response_original.get('createdTime')
                logger.debug(f"From response_original fetch date_time : {api_date_time}")
                api_device_serial = response_original.get('deviceSerial')
                logger.debug(f"From response_original fetch device_serial : {api_device_serial}")
                api_card_txn_type_desc = response_original.get('cardTxnTypeDesc')
                logger.debug(f"From response_original fetch card_txn_type_desc : {api_card_txn_type_desc}")
                api_amount_original = response_original.get('amountOriginal')
                logger.debug(f"From response_original fetch amount_original : {api_amount_original}")
                api_customer_name = response_original.get('customerName')
                logger.debug(f"From response_original fetch customer_name : {api_customer_name}")
                api_payer_name = response_original.get('payerName')
                logger.debug(f"From response_original fetch payer_name : {api_payer_name}")
                api_merchant_name = response_original.get('merchantName')
                logger.debug(f"From response_original fetch merchant_name : {api_merchant_name}")
                api_card_last_four_digit = response_original.get('cardLastFourDigit')
                logger.debug(f"From response_original fetch card_last_four_digit : {api_card_last_four_digit}")
                api_ext_ref_number = response_original.get('externalRefNumber')
                logger.debug(f"From response_original fetch external_ref_number : {api_ext_ref_number}")
                api_pmt_card_bin = response_original.get('paymentCardBin')
                logger.debug(f"From response_original fetch payment_card_bin : {api_pmt_card_bin}")
                api_name_on_card = response_original.get('nameOnCard')
                logger.debug(f"From response_original fetch _name_on_card : {api_name_on_card}")
                api_display_pan = response_original.get('displayPAN')
                logger.debug(f"From response_original fetch display_pan : {api_display_pan}")
                api_auth_code = response_original.get('authCode')
                logger.debug(f"From response_original fetch auth_code : {api_auth_code}")
                api_card_type = response_original.get('cardType')
                logger.debug(f"From response_original fetch card_type : {api_card_type}")

                response_refund = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn is : {response_refund}")
                api_amount_refund = response_refund.get('amount')
                logger.debug(f"From response_refund fetch amount : {api_amount_refund}")
                api_payment_mode_refund = response_refund.get('paymentMode')
                logger.debug(f"From response_refund fetch payment_mode : {api_payment_mode_refund}")
                api_payment_status_refund = response_refund.get('status')
                logger.debug(f"From response_refund fetch payment_status : {api_payment_status_refund}")
                api_payment_state_refund = response_refund.get('states')[0]
                logger.debug(f"From response_refund fetch payment_state : {api_payment_state_refund}")
                api_mid_refund = response_refund.get('mid')
                logger.debug(f"From response_refund fetch mid : {api_mid_refund}")
                api_tid_refund = response_refund.get('tid')
                logger.debug(f"From response_refund fetch tid : {api_tid_refund}")
                api_acquirer_code_refund = response_refund.get('acquirerCode')
                logger.debug(f"From response_refund fetch acquirer_code : {api_acquirer_code_refund}")
                api_settle_status_refund = response_refund.get('settlementStatus')
                logger.debug(f"From response_refund fetch settlement_status : {api_settle_status_refund}")
                api_rrn_refund = response_refund.get('rrNumber')
                logger.debug(f"From response_refund fetch rrn : {api_rrn_refund}")
                api_issuer_code_refund = response_refund.get('issuerCode')
                logger.debug(f"From response_refund fetch issuer_code : {api_issuer_code_refund}")
                api_txn_type_refund = response_refund.get('txnType')
                logger.debug(f"From response_refund fetch txn_type : {api_txn_type_refund}")
                api_org_code_refund = response_refund.get('orgCode')
                logger.debug(f"From response_refund fetch org_code : {api_org_code_refund}")
                api_tip_amt_refund = response_refund.get('amountAdditional')
                logger.debug(f"From response_refund fetch tip_amt : {api_tip_amt_refund}")
                api_batch_number_refund = response_refund.get('batchNumber')
                logger.debug(f"From response_refund fetch batch_number : {api_batch_number_refund}")
                api_pmt_card_brand_refund = response_refund.get('paymentCardBrand')
                logger.debug(f"From response_refund fetch payment_card_brand : {api_pmt_card_brand_refund}")
                api_pmt_card_type_refund = response_refund.get('paymentCardType')
                logger.debug(f"From response_refund fetch payment_card_type : {api_pmt_card_type_refund}")
                api_date_time_refund = response_refund.get('createdTime')
                logger.debug(f"From response_refund fetch date_time : {api_date_time_refund}")
                api_device_serial_refund = response_refund.get('deviceSerial')
                logger.debug(f"From response_refund fetch device_serial : {api_device_serial_refund}")
                api_card_txn_type_desc_refund = response_refund.get('cardTxnTypeDesc')
                logger.debug(f"From response_refund fetch card_txn_type_desc : {api_card_txn_type_desc_refund}")
                api_amount_original_refund = response_refund.get('amountOriginal')
                logger.debug(f"From response_refund fetch amount_original : {api_amount_original_refund}")
                api_customer_name_refund = response_refund.get('customerName')
                logger.debug(f"From response_refund fetch customer_name : {api_customer_name_refund}")
                api_payer_name_refund = response_refund.get('payerName')
                logger.debug(f"From response_refund fetch payer_name : {api_payer_name_refund}")
                api_merchant_name_refund = response_refund.get('merchantName')
                logger.debug(f"From response_refund fetch merchant_name : {api_merchant_name_refund}")
                api_card_last_four_digit_refund = response_refund.get('cardLastFourDigit')
                logger.debug(f"From response_refund fetch card_last_four_digit : {api_card_last_four_digit_refund}")
                api_ext_ref_number_refund = response_refund.get('externalRefNumber')
                logger.debug(f"From response_refund fetch external_ref_number : {api_ext_ref_number_refund}")
                api_pmt_card_bin_refund = response_refund.get('paymentCardBin')
                logger.debug(f"From response_refund fetch payment_card_bin : {api_pmt_card_bin_refund}")
                api_name_on_card_refund = response_refund.get('nameOnCard')
                logger.debug(f"From response_refund fetch name_on_card : {api_name_on_card_refund}")
                api_display_pan_refund = response_refund.get('displayPAN')
                logger.debug(f"From response_refund fetch display_pan : {api_display_pan_refund}")
                api_auth_code_refund = response_refund.get('authCode')
                logger.debug(f"From response_refund fetch auth_code : {api_auth_code_refund}")
                api_card_type_refund = response_refund.get('cardType')
                logger.debug(f"From response_refund fetch card_type : {api_card_type_refund}")

                actual_api_values = {
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_status": api_payment_status,
                    "pmt_state": api_payment_state,
                    "mid": api_mid,
                    "tid": api_tid,
                    "acquirer_code": api_acquirer_code,
                    "settle_status": api_settle_status,
                    "rrn": api_rrn,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "org_code": api_org_code,
                    "tip_amt": api_tip_amt,
                    "batch_number": api_batch_number,
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
                    "card_txn_type_desc": api_card_txn_type_desc,
                    "amt_original": api_amount_original,
                    "auth_code": api_auth_code,
                    "card_last_four_digit": api_card_last_four_digit,
                    "customer_name": api_customer_name,
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "payer_name": api_payer_name,
                    "pmt_card_bin": api_pmt_card_bin,
                    "card_type": api_card_type,
                    "display_pan": api_display_pan,
                    "name_on_card": api_name_on_card,
                    "txn_amt_2": api_amount_refund,
                    "pmt_mode_2": api_payment_mode_refund,
                    "pmt_status_2": api_payment_status_refund,
                    "pmt_state_2": api_payment_state_refund,
                    "mid_2": api_mid_refund,
                    "tid_2": api_tid_refund,
                    "acquirer_code_2": api_acquirer_code_refund,
                    "settle_status_2": api_settle_status_refund,
                    "rrn_2": api_rrn_refund,
                    "issuer_code_2": api_issuer_code_refund,
                    "txn_type_2": api_txn_type_refund,
                    "org_code_2": api_org_code_refund,
                    "tip_amt_2": api_tip_amt_refund,
                    "batch_number_2": api_batch_number_refund,
                    "pmt_card_brand_2": api_pmt_card_brand,
                    "pmt_card_type_2": api_pmt_card_type_refund,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_refund),
                    "device_serial_2": api_device_serial_refund,
                    "card_txn_type_desc_2": api_card_txn_type_desc_refund,
                    "amt_original_2": api_amount_original_refund,
                    "auth_code_2": api_auth_code_refund,
                    "card_last_four_digit_2": api_card_last_four_digit_refund,
                    "customer_name_2": api_customer_name_refund,
                    "ext_ref_number_2": api_ext_ref_number_refund,
                    "merchant_name_2": api_merchant_name_refund,
                    "payer_name_2": api_payer_name_refund,
                    "pmt_card_bin_2": api_pmt_card_bin_refund,
                    "card_type_2": api_card_type_refund,
                    "display_pan_2": api_display_pan_refund,
                    "name_on_card_2": api_name_on_card_refund
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
                    "txn_amt": float(total_amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": "RUPAY CARD IMAGE 01      /",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "txn_type": "CHARGE",
                    "settle_status": "SETTLED",
                    "tip_amt": float(tip_amount),
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "amt_original": float(amount),
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "608326",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "91",
                    "card_last_four_digit": "0017",
                    "customer_name": "RUPAY CARD IMAGE 01      /",
                    "txn_amt_2": float(total_amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": None,
                    "payer_name_2": "RUPAY CARD IMAGE 01      /",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "txn_type_2": "REFUND",
                    "settle_status_2": "PENDING",
                    "tip_amt_2": float(0.0),
                    "pmt_card_brand_2": "RUPAY",
                    "pmt_card_type_2": "DEBIT",
                    "amt_original_2": float(total_amount),
                    "device_serial_2": None,
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "608326",
                    "terminal_info_id_2": terminal_info_id,
                    "card_txn_type_2": "91",
                    "card_last_four_digit_2": "0017",
                    "customer_name_2": "RUPAY CARD IMAGE 01      /"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": total_amount_txn,
                    "pmt_mode": payment_mode,
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "payer_name": payer_name,
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "pmt_gateway": payment_gateway,
                    "txn_type": txn_type,
                    "settle_status": settle_status,
                    "tip_amt": amount_additional,
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "amt_original": amount_original,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "terminal_info_id": terminal_info_id_txn,
                    "card_txn_type": card_txn_type,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name,
                    "txn_amt_2": refund_total_amount_txn,
                    "pmt_mode_2": refund_payment_mode,
                    "pmt_status_2": refund_pmt_status,
                    "pmt_state_2": refund_pmt_state,
                    "acquirer_code_2": refund_acquirer_code,
                    "issuer_code_2": refund_issuer_code_txn,
                    "payer_name_2": refund_payer_name,
                    "mid_2": refund_mid_txn,
                    "tid_2": refund_tid_txn,
                    "pmt_gateway_2": refund_payment_gateway,
                    "txn_type_2": refund_txn_type,
                    "settle_status_2": refund_settle_status,
                    "tip_amt_2": refund_amount_additional,
                    "pmt_card_brand_2": refund_pmt_card_brand,
                    "pmt_card_type_2": refund_pmt_card_type,
                    "amt_original_2": refund_amount_original,
                    "device_serial_2": refund_device_serial_txn,
                    "order_id_2": refund_order_id_txn,
                    "org_code_2": refund_org_code_txn,
                    "pmt_card_bin_2": refund_pmt_card_bin,
                    "terminal_info_id_2": refund_terminal_info_id_txn,
                    "card_txn_type_2": refund_card_txn_type,
                    "card_last_four_digit_2": refund_card_last_four_digit,
                    "customer_name_2": refund_customer_name
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
                date_time = date_time_converter.to_portal_format(created_date_db=created_time)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                expected_portal_values = {
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(total_amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_time,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(total_amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "auth_code_2": refund_auth_code,
                    "rrn_2": refund_rrn,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[1]['Transaction ID']
                logger.info(
                    f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[1]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_auth_code = transaction_details[1]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")
                portal_rrn = transaction_details[1]['RR Number']
                logger.info(
                    f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[1]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[1]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[1]['Username']
                logger.info(
                    f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")

                portal_date_time_refund = transaction_details[0]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time_refund}")
                portal_txn_id_refund = transaction_details[0]['Transaction ID']
                logger.info(
                    f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id_refund}")
                portal_total_amount_refund = transaction_details[0]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount_refund}")
                portal_auth_code_refund = transaction_details[0]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code_refund}")
                portal_rrn_refund = transaction_details[0]['RR Number']
                logger.info(
                    f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn_refund}")
                portal_txn_type_refund = transaction_details[0]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type_refund}")
                portal_txn_status_refund = transaction_details[0]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status_refund}")
                portal_user_refund = transaction_details[0]['Username']
                logger.info(
                    f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user_refund}")

                actual_portal_values = {
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "auth_code": portal_auth_code,
                    "rrn": portal_rrn,
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type_2": portal_txn_type_refund,
                    "txn_amt_2": portal_total_amount_refund.split(' ')[1],
                    "username_2": portal_user_refund,
                    "txn_id_2": portal_txn_id_refund,
                    "auth_code_2": portal_auth_code_refund,
                    "rrn_2": portal_rrn_refund,
                    "date_time_2": portal_date_time_refund,
                    "pmt_status_2": portal_txn_status_refund
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=refund_created_time)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "SALE AMOUNT:": "Rs." + "{:,.2f}".format(total_amount),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": refund_rrn,
                    "AUTH CODE": refund_auth_code,
                    "CARD TYPE": "RUPAY",
                    "BATCH NO": refund_batch_number,
                    "TID": tid,
                    "payment_option": "REFUND"
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=refund_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
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