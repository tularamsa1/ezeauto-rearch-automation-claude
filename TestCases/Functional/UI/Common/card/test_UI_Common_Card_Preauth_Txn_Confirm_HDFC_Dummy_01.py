import random
import sys
import time
import pytest
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.sa.app_card_page import CardPage
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, ResourceAssigner, date_time_converter, APIProcessor, receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_03_007():
    """
        Sub Feature Code: UI_Common_Card_Preauth_Txn_Confirm_Success_Txn_HDFC_Dummy_VISA_CreditCard_417666
        Sub Feature Description: Performing the preauth txn confirm success transaction via HDFC Dummy PG using VISA Credit card (bin : 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 03:PreAuth , 007: TC007
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
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
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid value from the terminal_info table : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid value from the terminal_info table : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id value from the terminal_info table : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["preAuthOption"] = "1"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received from preconditions when preauth is enabled : {response}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.click_on_pre_auth()
            logger.debug(f"Clicked on pre_auth")
            amount = random.randint(200, 500) # The amount range is not yet confirmed
            home_page.enter_amt_order_no_and_device_serial_for_pre_auth(amount, order_id, device_serial)
            logger.debug(f"Enter the amount, order_id and device serial for pre_auth txn : {amount}, {order_id}, {device_serial}")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype("CTLS_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : CTLS_VISA_CREDIT_417666")
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on txn popup for preauth")
            app_driver.back()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(app_driver)
            txn_history_page.click_on_transaction_by_order_id(order_id)
            txn_history_page.click_on_confirm_pre_auth()
            logger.debug(f"Clicked on confirm pre_auth button")

            pre_auth_amt = amount - 100
            logger.debug(f"Pre_auth amount for confirmation is : {pre_auth_amt}")
            txn_history_page.click_on_confirmation_btn_for_amt(pre_auth_amt)
            logger.debug(f"Entered the confirm pre_auth amount")
            card_page = CardPage(app_driver)
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on confirm pre_auth popup")

            query = f"select * from txn where org_code='{org_code}' and payment_mode='CARD' and device_serial='{device_serial}' and external_ref='{order_id}' order by created_time desc limit 1 ;"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching original txn_id value from the txn table : {original_txn_id}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id value from the txn table : {txn_id}")

            query = f"select * from txn where id='{original_txn_id}';"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth for first txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth for first txn : {result}")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table after confirm pre_auth for first txn : {txn_created_time}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table after confirm pre_auth for first txn : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table after confirm pre_auth for first txn : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table after confirm pre_auth for first txn : {batch_number}")
            amount_db = result['amount'].values[0]
            logger.debug(f"Fetching amount value from the txn table after confirm pre_auth for first txn : {amount_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode value from the txn table after confirm pre_auth for first txn : {payment_mode_db}")
            payment_status_db = result['status'].values[0]
            logger.debug(f"Fetching status value from the txn table after confirm pre_auth for first txn : {payment_status_db}")
            payment_state_db = result['state'].values[0]
            logger.debug(f"Fetching state value from the txn table after confirm pre_auth for first txn : {payment_state_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from the txn table after confirm pre_auth for first txn : {acquirer_code_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid value from the txn table after confirm pre_auth for first txn : {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid value from the txn table after confirm pre_auth for first txn : {tid_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from the txn table after confirm pre_auth for first txn : {payment_gateway_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status value from the txn table after confirm pre_auth for first txn : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the txn table after confirm pre_auth for first txn : {device_serial_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table after confirm pre_auth for first txn : {merchant_name}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table after confirm pre_auth for first txn : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table after confirm pre_auth for first txn : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table after confirm pre_auth for first txn : {payment_card_type_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table after confirm pre_auth for first txn : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table after confirm pre_auth for first txn : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table after confirm pre_auth for first txn : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table after confirm pre_auth for first txn : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table after confirm pre_auth for first txn : {card_last_four_digit_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table after confirm pre_auth for first txn : {org_code_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table after confirm pre_auth for first txn : {order_id_db}")

            payment_status = txn_history_page.fetch_txn_status_text()
            logger.info(f"Fetching payment status value from txn history for the txn : {original_txn_id}, {payment_status}")
            payment_mode = txn_history_page.fetch_txn_type_text()
            logger.info(f"Fetching payment mode value from txn history for the txn : {original_txn_id}, {payment_mode}")
            app_txn_id = txn_history_page.fetch_txn_id_text()
            logger.info(f"Fetching txn_id value from txn history for the txn : {original_txn_id}, {app_txn_id}")
            app_amount = txn_history_page.fetch_txn_amount_text()
            logger.info(f"Fetching amount value from txn history for the txn : {original_txn_id}, {app_amount}")
            app_settlement_status = txn_history_page.fetch_settlement_status_text()
            logger.info(f"Fetching settlement status value from txn history for the txn : {original_txn_id}, {app_settlement_status}")
            app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
            logger.info(f"Fetching payment msg value from txn history for the txn : {original_txn_id}, {app_payment_msg}")
            app_date_and_time = txn_history_page.fetch_date_time_text()
            logger.info(f"Fetching date and time value from txn history for the txn : {original_txn_id}, {app_date_and_time}")
            app_rrn = txn_history_page.fetch_RRN_text()
            logger.info(f"Fetching rrn value from txn history for the txn : {original_txn_id}, {app_rrn}")
            app_auth_code = txn_history_page.fetch_auth_code_text()
            logger.info(f"Fetching auth_cde value from txn history for the txn : {original_txn_id}, {app_auth_code}")
            app_batch_no = txn_history_page.fetch_batch_number_text()
            logger.info(f"Fetching batch number value from txn history for the txn : {original_txn_id}, {app_batch_no}")
            app_device_serial = txn_history_page.fetch_device_serial_text()
            logger.info(f"Fetching device serial from txn history for the txn : {original_txn_id}, {app_device_serial}")
            app_order_id = txn_history_page.fetch_order_id_text()
            logger.info(f"Fetching txn order id value from txn history for the txn : {original_txn_id}, {app_order_id}")
            app_mid = txn_history_page.fetch_mid_text()
            logger.info(f"Fetching mid value from txn history for the txn : {original_txn_id}, {app_mid}")
            app_tid = txn_history_page.fetch_tid_text()
            logger.info(f"Fetching tid value from txn history for the txn : {original_txn_id}, {app_tid}")
            app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
            logger.info(f"Fetching card type value from txn history for the txn : {original_txn_id}, {app_card_type_desc}")

            query = f"select * from txn where id='{txn_id}' ;"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth for second txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth for second txn : {result}")
            txn_created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table after confirm pre_auth for second txn : {txn_created_time_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table after confirm pre_auth for second txn : {rrn_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table after confirm pre_auth for second txn : {auth_code_2}")
            batch_number_2 = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table after confirm pre_auth for second txn : {batch_number_2}")
            amount_db_2 = result['amount'].values[0]
            logger.debug(f"Fetching amount value  from the txn table after confirm pre_auth for second txn : {amount_db_2}")
            amt_cash_back_db_2 = result['amount_cash_back'].values[0]
            logger.debug(f"Fetching amount_cash_back value from the txn table after confirm pre_auth for second txn : {amt_cash_back_db_2}")
            payment_mode_db_2 = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode value from the txn table after confirm pre_auth for second txn : {payment_mode_db_2}")
            payment_status_db_2 = result['status'].values[0]
            logger.debug(f"Fetching status value from the txn table after confirm pre_auth for second txn : {payment_status_db_2}")
            payment_state_db_2 = result['state'].values[0]
            logger.debug(f"Fetching state value from the txn table after confirm pre_auth for second txn : {payment_state_db_2}")
            acquirer_code_db_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from the txn table after confirm pre_auth for second txn : {acquirer_code_db_2}")
            payer_name_db_2 = result["payer_name"].iloc[0]
            logger.debug(f"Fetching payer_name value from the txn table after confirm pre_auth for second txn : {payer_name_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table after confirm pre_auth for second txn : {txn_type_db_2}")
            mid_db_2 = result['mid'].values[0]
            logger.debug(f"Fetching mid value from the txn table after confirm pre_auth for second txn : {mid_db_2}")
            tid_db_2 = result['tid'].values[0]
            logger.debug(f"Fetching tid value from the txn table after confirm pre_auth for second txn : {tid_db_2}")
            payment_gateway_db_2 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from the txn table after confirm pre_auth for second txn  : {payment_gateway_db_2}")
            settlement_status_db_2 = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status value from the txn table after confirm pre_auth for second txn : {settlement_status_db_2}")
            device_serial_db_2 = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the txn table after confirm pre_auth for second txn : {device_serial_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table after confirm pre_auth for second txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table after confirm pre_auth for second txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table after confirm pre_auth for second txn : {payment_card_type_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table after confirm pre_auth for second txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table after confirm pre_auth for second txn : {terminal_info_id_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table after confirm pre_auth for second txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table after confirm pre_auth for second txn : {card_last_four_digit_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table after confirm pre_auth for second txn : {org_code_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table after confirm pre_auth for second txn : {order_id_db_2}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------

        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of App Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(txn_created_time)
                date_and_time_2 = date_time_converter.to_app_format(txn_created_time_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": original_txn_id,
                    "pmt_status": "CNF_PRE_AUTH",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number,
                    "card_type_desc": "*0018 CTLS",

                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:,.2f}".format(pre_auth_amt),
                    "settle_status_2": "PENDING",
                    "txn_id_2": txn_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    "rr_number_2": rrn_2,
                    "auth_code_2": auth_code_2,
                    "device_serial_2": device_serial,
                    "batch_number_2": batch_number_2,
                    "order_id_2": order_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "card_type_desc_2": "*0018 CTLS"
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver.back()
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment status value from txn history for the txn : {txn_id}, {payment_status_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode value from txn history for the txn : {txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id value from txn history for the txn : {txn_id}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching amount value from txn history for the txn : {txn_id}, {app_amount_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status value from txn history for the txn : {txn_id}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching payment msg value from txn history for the txn : {txn_id}, {app_payment_msg_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time value from txn history for the txn : {txn_id}, {app_date_and_time_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn value from txn history for the txn : {txn_id}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_cde value from txn history for the txn : {txn_id}, {app_auth_code_2}")
                app_batch_no_2 = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch number value from txn history for the txn : {txn_id}, {app_batch_no_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the txn : {txn_id}, {app_device_serial_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id value from txn history for the txn : {txn_id}, {app_order_id_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid value from txn history for the txn : {txn_id}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid value from txn history for the txn : {txn_id}, {app_tid_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card type value from txn history for the txn : {txn_id}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_no,
                    "card_type_desc": app_card_type_desc,

                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "settle_status_2": app_settlement_status_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "date_2": app_date_and_time_2,
                    "rr_number_2": app_rrn_2,
                    "auth_code_2": app_auth_code_2,
                    "device_serial_2": app_device_serial_2,
                    "batch_number_2": app_batch_no_2,
                    "order_id_2": app_order_id_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "card_type_desc_2": app_card_type_desc_2
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
                expected_date_and_time_api = date_time_converter.db_datetime(txn_created_time)
                expected_date_and_time_api_2 = date_time_converter.db_datetime(txn_created_time_2)
                expected_api_values = {
                    "pmt_status": "CNF_PRE_AUTH",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "txn_type": "PRE_AUTH",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": expected_date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "CTLS",
                    "batch_number": batch_number,
                    "card_last_four_digit": "0018",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "display_pan": "0018",

                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(pre_auth_amt),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "CONF_PRE_AUTH",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_2,
                    "date_2": expected_date_and_time_api_2,
                    "device_serial_2": device_serial_db_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "card_txn_type_2": "CTLS",
                    "batch_number_2": batch_number_2,
                    "card_last_four_digit_2": "0018",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name,
                    "pmt_card_bin_2": "417666",
                    "display_pan_2": "0018"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_in_list = response["txns"]
                logger.debug(f"Response after filtering data of current txn is : {response_in_list}")
                for elements in response_in_list:
                    if elements["txnId"] == original_txn_id:
                        status_api = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for first txn : {status_api}")
                        amount_api = float(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for first txn : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for first txn : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for first txn : {state_api}")
                        rrn_api = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for first txn : {rrn_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for first txn : {settlement_status_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for first txn : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for first txn : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for first txn : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for first txn : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for first txn : {txn_type_api}")
                        auth_code_api = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for first txn : {auth_code_api}")
                        date_and_time_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for first txn : {date_and_time_api}")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for first txn : {device_serial_api}")
                        username_api = elements["username"]
                        logger.debug(f"Value of username obtained from txnlist api for first txn : {username_api}")
                        txn_id_api = elements["txnId"]
                        logger.debug(f"Value of txnId obtained from txnlist api for first txn : {txn_id_api}")
                        payment_card_brand_api = elements["paymentCardBrand"]
                        logger.debug(f"Value of paymentCardBrand obtained from txnlist api for first txn : {payment_card_brand_api}")
                        payment_card_type_api = elements["paymentCardType"]
                        logger.debug(f"Value of paymentCardType obtained from txnlist api for first txn : {payment_card_type_api}")
                        card_txn_type_api = elements["cardTxnTypeDesc"]
                        logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for first txn : {card_txn_type_api}")
                        batch_number_api = elements["batchNumber"]
                        logger.debug(f"Value of batchNumber obtained from txnlist api for first txn : {batch_number_api}")
                        card_last_four_digit_api = elements["cardLastFourDigit"]
                        logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for first txn : {card_last_four_digit_api}")
                        external_ref_number_api = elements["externalRefNumber"]
                        logger.debug(f"Value of externalRefNumber obtained from txnlist api for first txn : {external_ref_number_api}")
                        merchant_name_api = elements["merchantName"]
                        logger.debug(f"Value of merchantName obtained from txnlist api for first txn : {merchant_name_api}")
                        payment_card_bin_api = elements["paymentCardBin"]
                        logger.debug(f"Value of paymentCardBin obtained from txnlist api for first txn : {payment_card_bin_api}")
                        display_pan_api = elements["displayPAN"]
                        logger.debug(f"Value of displayPAN obtained from txnlist api for first txn : {display_pan_api}")

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api_new = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for second txn : {status_api_new}")
                        amount_api_new = float(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for second txn : {amount_api_new}")
                        payment_mode_api_new = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api second txn : {payment_mode_api_new}")
                        state_api_new = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for second txn : {state_api_new}")
                        rrn_api_new = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for second txn : {rrn_api_new}")
                        settlement_status_api_new = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for second txn : {settlement_status_api_new}")
                        acquirer_code_api_new = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for second txn : {acquirer_code_api_new}")
                        org_code_api_new = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for second txn : {org_code_api_new}")
                        mid_api_new = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for second txn : {mid_api_new}")
                        tid_api_new = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for second txn : {tid_api_new}")
                        txn_type_api_new = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for second txn : {txn_type_api_new}")
                        auth_code_api_new = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for second txn : {auth_code_api_new}")
                        date_and_time_api_new = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for second txn : {date_and_time_api_new}")
                        device_serial_api_new = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for second txn : {device_serial_api_new}")
                        username_api_new = elements["username"]
                        logger.debug(f"Value of username obtained from txnlist api for second txn : {username_api_new}")
                        txn_id_api_new = elements["txnId"]
                        logger.debug(f"Value of txnId obtained from txnlist api for second txn : {txn_id_api_new}")
                        payment_card_brand_api_new = elements["paymentCardBrand"]
                        logger.debug(f"Value of paymentCardBrand obtained from txnlist api for second txn : {payment_card_brand_api_new}")
                        payment_card_type_api_new = elements["paymentCardType"]
                        logger.debug(f"Value of paymentCardType obtained from txnlist api for second txn : {payment_card_type_api_new}")
                        card_txn_type_api_new = elements["cardTxnTypeDesc"]
                        logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for second txn : {card_txn_type_api_new}")
                        batch_number_api_new = elements["batchNumber"]
                        logger.debug(f"Value of batchNumber obtained from txnlist api for second txn : {batch_number_api_new}")
                        card_last_four_digit_api_new = elements["cardLastFourDigit"]
                        logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for second txn : {card_last_four_digit_api_new}")
                        external_ref_number_api_new = elements["externalRefNumber"]
                        logger.debug(f"Value of externalRefNumber obtained from txnlist api for second txn : {external_ref_number_api_new}")
                        merchant_name_api_new = elements["merchantName"]
                        logger.debug(f"Value of merchantName obtained from txnlist api for second txn : {merchant_name_api_new}")
                        payment_card_bin_api_new = elements["paymentCardBin"]
                        logger.debug(f"Value of paymentCardBin obtained from txnlist api for second txn : {payment_card_bin_api_new}")
                        display_pan_api_new = elements["displayPAN"]
                        logger.debug(f"Value of displayPAN obtained from txnlist api for second txn : {display_pan_api_new}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "mid": mid_api,
                    "txn_type": txn_type_api,
                    "tid": tid_api,
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

                    "pmt_status_2": status_api_new,
                    "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "rrn_2": str(rrn_api_new),
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "mid_2": mid_api_new,
                    "txn_type_2": txn_type_api_new,
                    "tid_2": tid_api_new,
                    "org_code_2": org_code_api_new,
                    "auth_code_2": auth_code_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_new),
                    "device_serial_2": device_serial_api_new,
                    "username_2": username_api_new,
                    "txn_id_2": txn_id_api_new,
                    "pmt_card_brand_2": payment_card_brand_api_new,
                    "pmt_card_type_2": payment_card_type_api_new,
                    "card_txn_type_2": card_txn_type_api_new,
                    "batch_number_2": batch_number_api_new,
                    "card_last_four_digit_2": card_last_four_digit_api_new,
                    "external_ref_2": external_ref_number_api_new,
                    "merchant_name_2": merchant_name_api_new,
                    "pmt_card_bin_2": payment_card_bin_api_new,
                    "display_pan_2": display_pan_api_new
                }

                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "txn_amt": float(amount),
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
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "PRE_AUTH",
                    "card_txn_type": "91",
                    "card_last_four_digit": "0018",

                    "txn_amt_2": float(pre_auth_amt),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
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
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,

                    "txn_amt_2": amount_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "pmt_status_2": payment_status_db_2,
                    "pmt_state_2": payment_state_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "device_serial_2": device_serial_db_2,
                    "merchant_code_2": merchant_code_db_2,
                    "pmt_card_brand_2": payment_card_brand_db_2,
                    "pmt_card_type_2": payment_card_type_db_2,
                    "order_id_2": order_id_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                }

                logger.debug(f"actual_db_values : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

        # -----------------------------------------Start of Portal Validation-------------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(txn_created_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal_2,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(pre_auth_amt),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code_2,
                    "rrn": rrn_2,

                    "date_time_2": date_and_time_portal,
                    "pmt_status_2": "CNF_PRE_AUTH",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": original_txn_id,
                    "auth_code_2": auth_code,
                    "rrn_2": rrn,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[1]['Date & Time']
                transaction_id_2 = transaction_details[1]['Transaction ID']
                total_amount_2 = transaction_details[1]['Total Amount'].replace(",", "").split()
                rr_number_2 = transaction_details[1]['RR Number']
                transaction_type_2 = transaction_details[1]['Type']
                status_2 = transaction_details[1]['Status']
                username_2 = transaction_details[1]['Username']
                auth_code_portal_2 = transaction_details[1]['Auth Code']

                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].replace(",", "").split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,

                    "date_time_2": date_time_2,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:

                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(txn_created_time_2)
                expected_charge_slip_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'BATCH NO': batch_number, 'CARD TYPE': 'VISA',
                    'payment_option': 'SALE', 'TID': tid,
                    'time': txn_time, 'AUTH CODE': str(auth_code)
                }
                chargeslip_val_result = receipt_validator.perform_charge_slip_validations(original_txn_id,{"username": app_username,"password": app_password},
                                                                                            expected_charge_slip_values)
                expected_charge_slip_values_2 = {
                    'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(pre_auth_amt) + ".00", 'date': txn_date_2,
                    'BATCH NO': batch_number, 'CARD TYPE': 'VISA',
                    'payment_option': 'SALE', 'TID': tid,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_2)
                }

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id,{"username": app_username,"password": app_password},
                                                                                            expected_charge_slip_values_2)
                if chargeslip_val_result and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)