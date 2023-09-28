import random
import sys
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
def test_common_100_115_03_013():
    """
        Sub Feature Code: UI_Common_Card_Preauth_Txn_Confirm_Refund_Portal_API_Txn_HDFC_Dummy_VISA_CreditCard_41766
        Sub Feature Description: Performing the preauth txn confirm refund portal API transaction via HDFC Dummy PG using VISA Credit card (bin : 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 03:PreAuth , 013: TC013
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
        logger.debug(f"Response obtained when preauth is enabled in precondition settings : {response}")

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

            #The below query is to fetch the preauth txn details [because the authcode and rrn value will be overridden by the confirm pre_auth txn]
            query = f"select * from txn where org_code='{org_code}' and payment_mode='CARD' and device_serial='{device_serial}' and external_ref='{order_id}' order by created_time desc limit 1 ;"
            logger.debug(f"Query to fetch data from the txn table for first txn_id : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table for first txn_id : {result}")
            original_txn_id = result['id'].values[0]
            logger.debug(f"Fetching original txn_id from the txn table for first txn_id : {original_txn_id}")
            original_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table for first txn_id : {original_auth_code}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number value from the txn table for first txn_id : {original_rrn}")
            original_txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table for first txn_id : {original_txn_created_time}")

            txn_history_page.click_on_transaction_by_txn_id(original_txn_id)
            txn_history_page.click_on_confirm_pre_auth()
            logger.debug(f"Clicked on confirm pre_auth button")
            txn_history_page.click_on_confirmation_btn_for_amt(amount)
            logger.debug(f"Entered the confirm pre_auth amount")
            card_page = CardPage(app_driver)
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on confirm pre_auth popup")

            query = f"select * from txn where orig_txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching result for txn_id table : {result}")

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {response}")

            query = f"select * from txn where orig_txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth txn : {result}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table : {batch_number}")
            amount_db = result['amount'].values[0]
            logger.debug(f"Fetching amount value from the txn table : {amount_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode value from the txn table : {payment_mode_db}")
            payment_status_db = result['status'].values[0]
            logger.debug(f"Fetching status value from the txn table : {payment_status_db}")
            payment_state_db = result['state'].values[0]
            logger.debug(f"Fetching state value from the txn table : {payment_state_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from the txn table : {acquirer_code_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid value from the txn table : {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid value from the txn table : {tid_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from the txn table : {payment_gateway_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status value from the txn table : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the txn table : {device_serial_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table : {payment_card_type_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table : {card_last_four_digit_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table : {org_code_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table : {order_id_db}")

            api_details = DBProcessor.get_api_details('Offline_Refund', request_body={
                "password": app_password,
                "username": app_username,
                "amount": str(amount),
                "originalTransactionId": txn_id
            })
            logger.debug(f"API DETAILS for Offline_Refund : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for transaction list api is : {response}")
            refund_txn_id = response["txnId"]
            logger.debug(f"Fetching refund txn_id value after performing Offline_Refund : {refund_txn_id}")

            query = f"select * from txn where id='{txn_id}';"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth txn : {result}")
            txn_created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table after confirm pre_auth txn : {txn_created_time_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table after confirm pre_auth txn : {rrn_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table after confirm pre_auth txn : {auth_code_2}")
            batch_number_2 = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table after confirm pre_auth txn : {batch_number_2}")
            amount_db_2 = result['amount'].values[0]
            logger.debug(f"Fetching amount value from the txn table after confirm pre_auth txn : {amount_db_2}")
            amt_cash_back_db_2 = result['amount_cash_back'].values[0]
            logger.debug(f"Fetching amount_cash_back value from the txn table after confirm pre_auth txn : {amt_cash_back_db_2}")
            payment_mode_db_2 = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode value from the txn table after confirm pre_auth txn : {payment_mode_db_2}")
            payment_status_db_2 = result['status'].values[0]
            logger.debug(f"Fetching status value from the txn table after confirm pre_auth txn : {payment_status_db_2}")
            payment_state_db_2 = result['state'].values[0]
            logger.debug(f"Fetching state value from the txn table after confirm pre_auth txn : {payment_state_db_2}")
            acquirer_code_db_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from the txn table after confirm pre_auth txn : {acquirer_code_db_2}")
            mid_db_2 = result['mid'].values[0]
            logger.debug(f"Fetching mid value from the txn table after confirm pre_auth txn : {mid_db_2}")
            tid_db_2 = result['tid'].values[0]
            logger.debug(f"Fetching tid value from the txn table after confirm pre_auth txn : {tid_db_2}")
            payment_gateway_db_2 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from the txn table after confirm pre_auth txn : {payment_gateway_db_2}")
            settlement_status_db_2 = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status value from the txn table after confirm pre_auth txn : {settlement_status_db_2}")
            device_serial_db_2 = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the txn table after confirm pre_auth txn : {device_serial_db_2}")
            merchant_name_db_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table after confirm pre_auth txn : {merchant_name_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table after confirm pre_auth txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table after confirm pre_auth txn : {payment_card_type_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table after confirm pre_auth txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table after confirm pre_auth txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table after confirm pre_auth txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table after confirm pre_auth txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table after confirm pre_auth txn : {card_last_four_digit_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table after confirm pre_auth txn : {org_code_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table after confirm pre_auth txn : {order_id_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table after confirm pre_auth txn: {merchant_code_db_2}")

            query = f"select * from txn where id='{refund_txn_id}'"
            logger.debug(f"Query to fetch data from the txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table refund txn : {result}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table for refund txn : {refund_auth_code}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table for refund txn : {refund_created_time}")
            amount_db_3 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from the txn table for refund txn : {amount_db_3}")
            payment_mode_db_3 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment_mode value from the txn table for refund txn : {payment_mode_db_3}")
            payment_status_db_3 = result["status"].iloc[0]
            logger.debug(f"Fetching status value from the txn table for refund txn : {payment_status_db_3}")
            payment_state_db_3 = result["state"].iloc[0]
            logger.debug(f"Fetching state value from the txn table for refund txn : {payment_state_db_3}")
            acquirer_code_db_3 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer_code value from the txn table for refund txn : {acquirer_code_db_3}")
            mid_db_3 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from the txn table for refund txn : {mid_db_3}")
            tid_db_3 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from the txn table for refund txn : {tid_db_3}")
            payment_gateway_db_3 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment_gateway value from the txn table for refund txn : {payment_gateway_db_3}")
            refund_rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rr_number value from the txn table for refund txn : {refund_rrn}")
            merchant_code_db_3 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table for refund txn : {merchant_code_db_3}")
            payment_card_brand_db_3 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table for refund txn : {payment_card_brand_db_3}")
            settlement_status_db_3 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement_status value from the txn table for refund txn : {settlement_status_db_3}")
            payment_card_type_db_3 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table for refund txn : {payment_card_type_db_3}")
            batch_number_db_3 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch_number value from the txn table for refund txn : {batch_number_db_3}")
            order_id_db_3 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table for refund txn : {order_id_db_3}")
            org_code_db_3 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table for refund txn : {org_code_db_3}")
            payment_card_bin_db_3 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table for refund txn : {payment_card_bin_db_3}")
            terminal_info_id_db_3 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table for refund txn : {terminal_info_id_db_3}")
            txn_type_db_3 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table for refund txn : {txn_type_db_3}")
            card_txn_type_db_3 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table for refund txn : {card_txn_type_db_3}")
            card_last_four_digit_db_3 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table for refund txn : {card_last_four_digit_db_3}")

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

        #-----------------------------------------Start of App Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(original_txn_created_time)
                date_and_time_2 = date_time_converter.to_app_format(txn_created_time_2)
                date_and_time_3 = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": original_txn_id,
                    "pmt_status": "CNF_PRE_AUTH",
                    "rr_number": original_rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": original_auth_code,
                    "date": date_and_time,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number,
                    "card_type_desc": "*0018 CTLS",

                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id,
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "rr_number_2": rrn_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "settle_status_2": "SETTLED",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_2,
                    "card_type_desc_2": "*0018 CTLS",

                    "pmt_mode_3": "CARD",
                    "pmt_status_3": "REFUNDED",
                    "txn_amt_3": "{:,.2f}".format(amount),
                    "settle_status_3": "PENDING",
                    "txn_id_3": refund_txn_id,
                    "pmt_msg_3": "PAYMENT VOIDED/REFUNDED",
                    "date_3": date_and_time_3,
                    "rr_number_3": refund_rrn,
                    "auth_code_3": refund_auth_code,
                    "device_serial_3": device_serial,
                    "batch_number_3": batch_number_db_3,
                    "order_id_3": order_id,
                    "mid_3": mid,
                    "tid_3": tid,
                    "card_type_desc_3": "*0018 CTLS"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.info(f"Killing the app and relaunching the app")
                login_page.perform_login(username=app_username, password=app_password)
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment status value from txn history for the confirm preauth txn : {txn_id}, {payment_status_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode value from txn history for the confirm preauth txn : {txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id value from txn history for the confirm preauth txn : {txn_id}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching amount value from txn history for the confirm preauth txn : {txn_id}, {app_amount_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status value from txn history for the confirm preauth txn : {txn_id}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching payment msg value from txn history for the confirm preauth txn : {txn_id}, {app_payment_msg_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time value from txn history for the confirm preauth txn : {txn_id}, {app_date_and_time_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn value from txn history for the confirm preauth txn : {txn_id}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_cde value from txn history for the confirm preauth txn : {txn_id}, {app_auth_code_2}")
                app_batch_no_2 = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch number value from txn history for the confirm preauth txn : {txn_id}, {app_batch_no_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the confirm preauth txn : {txn_id}, {app_device_serial_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id value from txn history for the confirm preauth txn : {txn_id}, {app_order_id_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid value from txn history for the confirm preauth txn : {txn_id}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid value from txn history for the confirm preauth txn : {txn_id}, {app_tid_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card type value from txn history for the confirm preauth txn : {txn_id}, {app_card_type_desc_2}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the refund txn : {refund_txn_id}, {app_amount_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the refund txn : {refund_txn_id}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the refund txn : {refund_txn_id}, {app_txn_id_3}")
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the refund txn : {refund_txn_id}, {payment_status_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the refund txn : {refund_txn_id}, {app_rrn_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the refund txn : {refund_txn_id}, {app_order_id_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the refund txn : {refund_txn_id}, {app_payment_msg_3}")
                app_batch_no_3 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching txn batch no from txn history for the refund txn : {refund_txn_id}, {app_batch_no_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the refund txn : {refund_txn_id}, {app_settlement_status_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the refund txn : {refund_txn_id}, {app_auth_code_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the refund txn : {refund_txn_id}, {app_date_and_time_3}")
                app_device_serial_3 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the refund txn : {refund_txn_id}, {app_device_serial_3}")
                app_mid_3 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the refund txn : {refund_txn_id}, {app_mid_3}")
                app_tid_3 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the refund txn : {refund_txn_id}, {app_tid_3}")
                app_batch_number_3 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the refund txn : {refund_txn_id}, {app_batch_number_3}")
                app_card_type_desc_3 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the refund txn : {refund_txn_id}, {app_card_type_desc_3}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=original_txn_id)
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
                    "card_type_desc_2": app_card_type_desc_2,

                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "txn_id_3": app_txn_id_3,
                    "settle_status_3": app_settlement_status_3,
                    "pmt_msg_3": app_payment_msg_3,
                    "date_3": app_date_and_time_3,
                    "rr_number_3": app_rrn_3,
                    "auth_code_3": app_auth_code_3,
                    "device_serial_3": app_device_serial_3,
                    "batch_number_3": app_batch_no_3,
                    "order_id_3": app_order_id_3,
                    "mid_3": app_mid_3,
                    "tid_3": app_tid_3,
                    "card_type_desc_3": app_card_type_desc_3
                }

                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_date_and_time_api = date_time_converter.db_datetime(original_txn_created_time)
                expected_date_and_time_api_2 = date_time_converter.db_datetime(txn_created_time_2)
                expected_date_and_time_api_3 = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "CNF_PRE_AUTH",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(original_rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "txn_type": "PRE_AUTH",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": original_auth_code,
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

                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "CONF_PRE_AUTH",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_2,
                    "date_2": expected_date_and_time_api_2,
                    "device_serial_2": device_serial,
                    "username_2": app_username,
                    "txn_id_2": txn_id,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "card_txn_type_2": "CTLS",
                    "batch_number_2": batch_number,
                    "card_last_four_digit_2": "0018",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name,
                    "pmt_card_bin_2": "417666",
                    "display_pan_2": "0018",

                    "pmt_status_3": "REFUNDED",
                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "CARD",
                    "pmt_state_3": "AUTHORIZED",
                    "rrn_3": str(refund_rrn),
                    "settle_status_3": "PENDING",
                    "acquirer_code_3": "HDFC",
                    "txn_type_3": "REFUND",
                    "mid_3": mid,
                    "tid_3": tid,
                    "org_code_3": org_code,
                    "auth_code_3": refund_auth_code,
                    "date_3": expected_date_and_time_api_3,
                    "username_3": app_username,
                    "txn_id_3": refund_txn_id,
                    "pmt_card_brand_3": "VISA",
                    "pmt_card_type_3": "CREDIT",
                    "card_txn_type_3": "CTLS",
                    "batch_number_3": batch_number_db_3,
                    "card_last_four_digit_3": "0018",
                    "external_ref_3": order_id,
                    "merchant_name_3": merchant_name,
                    "pmt_card_bin_3": "417666",
                    "display_pan_3": "0018"
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
                        logger.debug(f"Value of status obtained from txnlist api for original txn : {status_api}")
                        amount_api = float(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for original txn : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for original txn : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for original txn : {state_api}")
                        rrn_api = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for original txn : {rrn_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for original txn : {settlement_status_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for original txn : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for original txn : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for original txn : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for original txn : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for original txn : {txn_type_api}")
                        auth_code_api = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for original txn : {auth_code_api}")
                        date_and_time_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for original txn : {date_and_time_api}")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for original txn : {device_serial_api}")
                        username_api = elements["username"]
                        logger.debug(f"Value of username obtained from txnlist api for original txn : {username_api}")
                        txn_id_api = elements["txnId"]
                        logger.debug(f"Value of txnId obtained from txnlist api for original txn : {txn_id_api}")
                        payment_card_brand_api = elements["paymentCardBrand"]
                        logger.debug(f"Value of paymentCardBrand obtained from txnlist api for original txn : {payment_card_brand_api}")
                        payment_card_type_api = elements["paymentCardType"]
                        logger.debug(f"Value of paymentCardType obtained from txnlist api for original txn : {payment_card_type_api}")
                        card_txn_type_api = elements["cardTxnTypeDesc"]
                        logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for original txn : {card_txn_type_api}")
                        batch_number_api = elements["batchNumber"]
                        logger.debug(f"Value of batchNumber obtained from txnlist api for original txn : {batch_number_api}")
                        card_last_four_digit_api = elements["cardLastFourDigit"]
                        logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for original txn : {card_last_four_digit_api}")
                        external_ref_number_api = elements["externalRefNumber"]
                        logger.debug(f"Value of externalRefNumber obtained from txnlist api for original txn : {external_ref_number_api}")
                        merchant_name_api = elements["merchantName"]
                        logger.debug(f"Value of merchantName obtained from txnlist api for original txn : {merchant_name_api}")
                        payment_card_bin_api = elements["paymentCardBin"]
                        logger.debug(f"Value of paymentCardBin obtained from txnlist api for original txn : {payment_card_bin_api}")
                        display_pan_api = elements["displayPAN"]
                        logger.debug(f"Value of displayPAN obtained from txnlist api for original txn : {display_pan_api}")

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api_2 = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for confirm preauth txn : {status_api_2}")
                        amount_api_2 = float(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for confirm preauth txn : {amount_api_2}")
                        payment_mode_api_2 = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api confirm preauth txn : {payment_mode_api_2}")
                        state_api_2 = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for confirm preauth txn : {state_api_2}")
                        rrn_api_2 = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for confirm preauth txn : {rrn_api_2}")
                        settlement_status_api_2 = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for confirm preauth txn : {settlement_status_api_2}")
                        acquirer_code_api_2 = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for confirm preauth txn : {acquirer_code_api_2}")
                        org_code_api_2 = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for confirm preauth txn : {org_code_api_2}")
                        mid_api_2 = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for confirm preauth txn : {mid_api_2}")
                        tid_api_2 = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for confirm preauth txn : {tid_api_2}")
                        txn_type_api_2 = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for confirm preauth txn : {txn_type_api_2}")
                        auth_code_api_2 = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for confirm preauth txn : {auth_code_api_2}")
                        date_and_time_api_2 = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for confirm preauth txn : {date_and_time_api_2}")
                        device_serial_api_2 = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for confirm preauth txn : {device_serial_api_2}")
                        username_api_2 = elements["username"]
                        logger.debug(f"Value of username obtained from txnlist api for confirm preauth txn : {username_api_2}")
                        txn_id_api_2 = elements["txnId"]
                        logger.debug(f"Value of txnId obtained from txnlist api for confirm preauth txn : {txn_id_api_2}")
                        payment_card_brand_api_2 = elements["paymentCardBrand"]
                        logger.debug(f"Value of paymentCardBrand obtained from txnlist api for confirm preauth txn : {payment_card_brand_api_2}")
                        payment_card_type_api_2 = elements["paymentCardType"]
                        logger.debug(f"Value of paymentCardType obtained from txnlist api for confirm preauth txn : {payment_card_type_api_2}")
                        card_txn_type_api_2 = elements["cardTxnTypeDesc"]
                        logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for confirm preauth txn : {card_txn_type_api_2}")
                        batch_number_api_2 = elements["batchNumber"]
                        logger.debug(f"Value of batchNumber obtained from txnlist api for confirm preauth txn : {batch_number_api_2}")
                        card_last_four_digit_api_2 = elements["cardLastFourDigit"]
                        logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for confirm preauth txn : {card_last_four_digit_api_2}")
                        external_ref_number_api_2 = elements["externalRefNumber"]
                        logger.debug(f"Value of externalRefNumber obtained from txnlist api for confirm preauth txn : {external_ref_number_api_2}")
                        merchant_name_api_2 = elements["merchantName"]
                        logger.debug(f"Value of merchantName obtained from txnlist api for confirm preauth txn : {merchant_name_api_2}")
                        payment_card_bin_api_2 = elements["paymentCardBin"]
                        logger.debug(f"Value of paymentCardBin obtained from txnlist api for confirm preauth txn : {payment_card_bin_api_2}")
                        display_pan_api_2 = elements["displayPAN"]
                        logger.debug(f"Value of displayPAN obtained from txnlist api for confirm preauth txn : {display_pan_api_2}")

                for elements in response_in_list:
                    if elements["txnId"] == refund_txn_id:
                        status_api_3 = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for refund txn : {status_api_2}")
                        amount_api_3 = float(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for refund txn : {amount_api_2}")
                        payment_mode_api_3 = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api refund txn : {payment_mode_api_2}")
                        state_api_3 = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for refund txn : {state_api_3}")
                        rrn_api_3 = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for refund txn : {rrn_api_3}")
                        settlement_status_api_3 = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for refund txn : {settlement_status_api_3}")
                        acquirer_code_api_3 = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for refund txn : {acquirer_code_api_3}")
                        org_code_api_3 = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for refund txn : {org_code_api_3}")
                        mid_api_3 = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for refund txn : {mid_api_3}")
                        tid_api_3 = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for refund txn : {tid_api_3}")
                        txn_type_api_3 = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for refund txn : {txn_type_api_3}")
                        auth_code_api_3 = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for refund txn : {auth_code_api_3}")
                        date_and_time_api_3 = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for refund txn : {date_and_time_api_3}")
                        username_api_3 = elements["username"]
                        logger.debug(f"Value of username obtained from txnlist api for refund txn : {username_api_3}")
                        txn_id_api_3 = elements["txnId"]
                        logger.debug(f"Value of txnId obtained from txnlist api for refund txn : {txn_id_api_3}")
                        payment_card_brand_api_3 = elements["paymentCardBrand"]
                        logger.debug(f"Value of paymentCardBrand obtained from txnlist api for refund txn : {payment_card_brand_api_3}")
                        payment_card_type_api_3 = elements["paymentCardType"]
                        logger.debug(f"Value of paymentCardType obtained from txnlist api for refund txn : {payment_card_type_api_3}")
                        card_txn_type_api_3 = elements["cardTxnTypeDesc"]
                        logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for refund txn : {card_txn_type_api_3}")
                        batch_number_api_3 = elements["batchNumber"]
                        logger.debug(f"Value of batchNumber obtained from txnlist api for refund txn : {batch_number_api_3}")
                        card_last_four_digit_api_3 = elements["cardLastFourDigit"]
                        logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for refund txn : {card_last_four_digit_api_3}")
                        external_ref_number_api_3 = elements["externalRefNumber"]
                        logger.debug(f"Value of externalRefNumber obtained from txnlist api for refund txn : {external_ref_number_api_3}")
                        merchant_name_api_3 = elements["merchantName"]
                        logger.debug(f"Value of merchantName obtained from txnlist api for refund txn : {merchant_name_api_3}")
                        payment_card_bin_api_3 = elements["paymentCardBin"]
                        logger.debug(f"Value of paymentCardBin obtained from txnlist api for refund txn : {payment_card_bin_api_3}")
                        display_pan_api_3 = elements["displayPAN"]
                        logger.debug(f"Value of displayPAN obtained from txnlist api for refund txn : {display_pan_api_3}")

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

                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "mid_2": mid_api_2,
                    "txn_type_2": txn_type_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "auth_code_2": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "device_serial_2": device_serial_api_2,
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "display_pan_2": display_pan_api_2,

                    "pmt_status_3": status_api_3,
                    "txn_amt_3": amount_api_3,
                    "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_3,
                    "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "mid_3": mid_api_3,
                    "txn_type_3": txn_type_api_3,
                    "tid_3": tid_api_3,
                    "org_code_3": org_code_api_3,
                    "auth_code_3": auth_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_and_time_api_3),
                    "username_3": username_api_3,
                    "txn_id_3": txn_id_api_3,
                    "pmt_card_brand_3": payment_card_brand_api_3,
                    "pmt_card_type_3": payment_card_type_api_3,
                    "card_txn_type_3": card_txn_type_api_3,
                    "batch_number_3": batch_number_api_3,
                    "card_last_four_digit_3": card_last_four_digit_api_3,
                    "external_ref_3": external_ref_number_api_3,
                    "merchant_name_3": merchant_name_api_3,
                    "pmt_card_bin_3": payment_card_bin_api_3,
                    "display_pan_3": display_pan_api_3
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
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
                    "txn_type": "CONF_PRE_AUTH",
                    "card_txn_type": "91",
                    "card_last_four_digit": "0018",

                    "txn_amt_2": float(amount),
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

                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "CARD",
                    "pmt_status_3": "REFUNDED",
                    "pmt_state_3": "AUTHORIZED",
                    "acquirer_code_3": "HDFC",
                    "mid_3": mid,
                    "tid_3": tid,
                    "pmt_gateway_3": "DUMMY",
                    "settle_status_3": "PENDING",
                    "merchant_code_3": org_code,
                    "pmt_card_brand_3": "VISA",
                    "pmt_card_type_3": "CREDIT",
                    "order_id_3": order_id,
                    "org_code_3": org_code,
                    "pmt_card_bin_3": "417666",
                    "terminal_info_id_3": terminal_info_id,
                    "txn_type_3": "REFUND",
                    "card_txn_type_3": "91",
                    "card_last_four_digit_3": "0018"
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

                    "txn_amt_3": amount_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "pmt_status_3": payment_status_db_3,
                    "pmt_state_3": payment_state_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "pmt_gateway_3": payment_gateway_db_3,
                    "settle_status_3": settlement_status_db_3,
                    "merchant_code_3": merchant_code_db_3,
                    "pmt_card_brand_3": payment_card_brand_db_3,
                    "pmt_card_type_3": payment_card_type_db_3,
                    "order_id_3": order_id_db_3,
                    "org_code_3": org_code_db_3,
                    "pmt_card_bin_3": payment_card_bin_db_3,
                    "terminal_info_id_3": terminal_info_id_db_3,
                    "txn_type_3": txn_type_db_3,
                    "card_txn_type_3": card_txn_type_db_3,
                    "card_last_four_digit_3": card_last_four_digit_db_3
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_db=txn_created_time_2)
                date_and_time_portal_3 = date_time_converter.to_portal_format(created_date_db=original_txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "REFUNDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": refund_txn_id,
                    "auth_code": refund_auth_code,
                    "rrn": refund_rrn,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id,
                    "auth_code_2": str(auth_code_2),
                    "rrn_2": rrn_2,

                    "date_time_3": date_and_time_portal_3,
                    "pmt_status_3": "CNF_PRE_AUTH",
                    "pmt_type_3": "CARD",
                    "txn_amt_3": "{:.2f}".format(amount),
                    "username_3": app_username,
                    "txn_id_3": original_txn_id,
                    "auth_code_3": str(original_auth_code),
                    "rrn_3": str(original_rrn),
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                date_time_3 = transaction_details[2]['Date & Time']
                transaction_id_3 = transaction_details[2]['Transaction ID']
                total_amount_3 = transaction_details[2]['Total Amount'].replace(",", "").split()
                rr_number_portal_3 = transaction_details[2]['RR Number']
                transaction_type_3 = transaction_details[2]['Type']
                status_3 = transaction_details[2]['Status']
                username_3 = transaction_details[2]['Username']
                auth_code_portal_3 = transaction_details[1]['Auth Code']

                date_time_2 = transaction_details[1]['Date & Time']
                transaction_id_2 = transaction_details[1]['Transaction ID']
                total_amount_2 = transaction_details[1]['Total Amount'].replace(",", "").split()
                rr_number_portal_2 = transaction_details[1]['RR Number']
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
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time,

                    "date_time_2": date_time_2,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_portal_2,

                    "date_time_3": date_time_3,
                    "pmt_status_3": str(status_3),
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "auth_code_3": auth_code_portal_3,
                    "rrn_3": rr_number_portal_3,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:

                txn_date, txn_time = date_time_converter.to_chargeslip_format(original_txn_created_time)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(txn_created_time_2)
                expected_charge_slip_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(original_rrn),
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date,
                    'BATCH NO': batch_number,
                    'CARD TYPE': 'VISA',
                    'payment_option': 'SALE',
                    'TID': tid,
                    'time': txn_time,
                    'AUTH CODE': str(original_auth_code)
                }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                chargeslip_val_result = receipt_validator.perform_charge_slip_validations(original_txn_id,{"username": app_username,"password": app_password},
                                                                                            expected_charge_slip_values)
                expected_charge_slip_values_2 = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date_2,
                    'BATCH NO': batch_number,
                    'CARD TYPE': 'VISA',
                    'payment_option': 'REFUND',
                    'TID': tid,
                    'time': txn_time_2,
                    'AUTH CODE': str(auth_code_2)
                }
                logger.debug(f"expected_charge_slip_values_2 : {expected_charge_slip_values_2}")
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
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_03_014():
    """
        Sub Feature Code: UI_Common_Card_Preauth_Txn_Confirm_Refund_Portal_API_Txn_HDFC_Dummy_MASTER_CreditCard_541333
        Sub Feature Description: Performing the preauth txn confirm refund portal API transaction via HDFC Dummy PG using MASTER Credit card (bin : 541333)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 03:PreAuth , 014: TC014
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
        logger.debug(f"Response obtained when preauth is enabled in precondition settings : {response}")

        query = f"select bank_code from bin_info where bin='541333'"
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
            logger.debug(f"Selecting the card type as : CTLS_MASTER_CREDIT_541333")
            card_page.select_cardtype("CTLS_MASTER_CREDIT_541333")
            logger.debug(f"Selected the card type as : CTLS_MASTER_CREDIT_541333")
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on txn popup for preauth")
            app_driver.back()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(app_driver)

            #The below query is to fetch the preauth txn details [because the authcode and rrn value will be overridden by the confirm pre_auth txn]
            query = f"select * from txn where org_code='{org_code}' and payment_mode='CARD' and device_serial='{device_serial}' and external_ref='{order_id}' order by created_time desc limit 1 ;"
            logger.debug(f"Query to fetch data from the txn table for first txn_id : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table for first txn_id : {result}")
            original_txn_id = result['id'].values[0]
            logger.debug(f"Fetching original txn_id from the txn table for first txn_id : {original_txn_id}")
            original_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table for first txn_id : {original_auth_code}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number value from the txn table for first txn_id : {original_rrn}")
            original_txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table for first txn_id : {original_txn_created_time}")

            txn_history_page.click_on_transaction_by_txn_id(original_txn_id)
            txn_history_page.click_on_confirm_pre_auth()
            logger.debug(f"Clicked on confirm pre_auth button")
            txn_history_page.click_on_confirmation_btn_for_amt(amount)
            logger.debug(f"Entered the confirm pre_auth amount")
            card_page = CardPage(app_driver)
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on confirm pre_auth popup")

            query = f"select * from txn where orig_txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching result for txn_id table : {result}")

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {response}")

            query = f"select * from txn where orig_txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth txn : {result}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table : {batch_number}")
            amount_db = result['amount'].values[0]
            logger.debug(f"Fetching amount value from the txn table : {amount_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode value from the txn table : {payment_mode_db}")
            payment_status_db = result['status'].values[0]
            logger.debug(f"Fetching status value from the txn table : {payment_status_db}")
            payment_state_db = result['state'].values[0]
            logger.debug(f"Fetching state value from the txn table : {payment_state_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from the txn table : {acquirer_code_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid value from the txn table : {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid value from the txn table : {tid_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from the txn table : {payment_gateway_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status value from the txn table : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the txn table : {device_serial_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table : {payment_card_type_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table : {card_last_four_digit_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table : {org_code_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table : {order_id_db}")

            api_details = DBProcessor.get_api_details('Offline_Refund', request_body={
                "password": app_password,
                "username": app_username,
                "amount": str(amount),
                "originalTransactionId": txn_id
            })
            logger.debug(f"API DETAILS for Offline_Refund : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for transaction list api is : {response}")
            refund_txn_id = response["txnId"]
            logger.debug(f"Fetching refund txn_id value after performing Offline_Refund : {refund_txn_id}")

            query = f"select * from txn where id='{txn_id}';"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth txn : {result}")
            txn_created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table after confirm pre_auth txn : {txn_created_time_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table after confirm pre_auth txn : {rrn_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table after confirm pre_auth txn : {auth_code_2}")
            batch_number_2 = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table after confirm pre_auth txn : {batch_number_2}")
            amount_db_2 = result['amount'].values[0]
            logger.debug(f"Fetching amount value from the txn table after confirm pre_auth txn : {amount_db_2}")
            amt_cash_back_db_2 = result['amount_cash_back'].values[0]
            logger.debug(f"Fetching amount_cash_back value from the txn table after confirm pre_auth txn : {amt_cash_back_db_2}")
            payment_mode_db_2 = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode value from the txn table after confirm pre_auth txn : {payment_mode_db_2}")
            payment_status_db_2 = result['status'].values[0]
            logger.debug(f"Fetching status value from the txn table after confirm pre_auth txn : {payment_status_db_2}")
            payment_state_db_2 = result['state'].values[0]
            logger.debug(f"Fetching state value from the txn table after confirm pre_auth txn : {payment_state_db_2}")
            acquirer_code_db_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from the txn table after confirm pre_auth txn : {acquirer_code_db_2}")
            mid_db_2 = result['mid'].values[0]
            logger.debug(f"Fetching mid value from the txn table after confirm pre_auth txn : {mid_db_2}")
            tid_db_2 = result['tid'].values[0]
            logger.debug(f"Fetching tid value from the txn table after confirm pre_auth txn : {tid_db_2}")
            payment_gateway_db_2 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from the txn table after confirm pre_auth txn : {payment_gateway_db_2}")
            settlement_status_db_2 = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status value from the txn table after confirm pre_auth txn : {settlement_status_db_2}")
            device_serial_db_2 = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial value from the txn table after confirm pre_auth txn : {device_serial_db_2}")
            merchant_name_db_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table after confirm pre_auth txn : {merchant_name_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table after confirm pre_auth txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table after confirm pre_auth txn : {payment_card_type_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table after confirm pre_auth txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table after confirm pre_auth txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table after confirm pre_auth txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table after confirm pre_auth txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table after confirm pre_auth txn : {card_last_four_digit_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table after confirm pre_auth txn : {org_code_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table after confirm pre_auth txn : {order_id_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table after confirm pre_auth txn: {merchant_code_db_2}")

            query = f"select * from txn where id='{refund_txn_id}'"
            logger.debug(f"Query to fetch data from the txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table refund txn : {result}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table for refund txn : {refund_auth_code}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table for refund txn : {refund_created_time}")
            amount_db_3 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from the txn table for refund txn : {amount_db_3}")
            payment_mode_db_3 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment_mode value from the txn table for refund txn : {payment_mode_db_3}")
            payment_status_db_3 = result["status"].iloc[0]
            logger.debug(f"Fetching status value from the txn table for refund txn : {payment_status_db_3}")
            payment_state_db_3 = result["state"].iloc[0]
            logger.debug(f"Fetching state value from the txn table for refund txn : {payment_state_db_3}")
            acquirer_code_db_3 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer_code value from the txn table for refund txn : {acquirer_code_db_3}")
            mid_db_3 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from the txn table for refund txn : {mid_db_3}")
            tid_db_3 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from the txn table for refund txn : {tid_db_3}")
            payment_gateway_db_3 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment_gateway value from the txn table for refund txn : {payment_gateway_db_3}")
            refund_rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rr_number value from the txn table for refund txn : {refund_rrn}")
            merchant_code_db_3 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table for refund txn : {merchant_code_db_3}")
            payment_card_brand_db_3 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table for refund txn : {payment_card_brand_db_3}")
            settlement_status_db_3 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement_status value from the txn table for refund txn : {settlement_status_db_3}")
            payment_card_type_db_3 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table for refund txn : {payment_card_type_db_3}")
            batch_number_db_3 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch_number value from the txn table for refund txn : {batch_number_db_3}")
            order_id_db_3 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table for refund txn : {order_id_db_3}")
            org_code_db_3 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table for refund txn : {org_code_db_3}")
            payment_card_bin_db_3 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment_card_bin value from the txn table for refund txn : {payment_card_bin_db_3}")
            terminal_info_id_db_3 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal_info_id value from the txn table for refund txn : {terminal_info_id_db_3}")
            txn_type_db_3 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn_type value from the txn table for refund txn : {txn_type_db_3}")
            card_txn_type_db_3 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card_txn_type value from the txn table for refund txn : {card_txn_type_db_3}")
            card_last_four_digit_db_3 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card_last_four_digit value from the txn table for refund txn : {card_last_four_digit_db_3}")

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

        #-----------------------------------------Start of App Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(original_txn_created_time)
                date_and_time_2 = date_time_converter.to_app_format(txn_created_time_2)
                date_and_time_3 = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": original_txn_id,
                    "pmt_status": "CNF_PRE_AUTH",
                    "rr_number": original_rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": original_auth_code,
                    "date": date_and_time,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number,
                    "card_type_desc": "*1034 CTLS",

                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id,
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "rr_number_2": rrn_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "settle_status_2": "SETTLED",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_2,
                    "card_type_desc_2": "*1034 CTLS",

                    "pmt_mode_3": "CARD",
                    "pmt_status_3": "REFUNDED",
                    "txn_amt_3": "{:,.2f}".format(amount),
                    "settle_status_3": "PENDING",
                    "txn_id_3": refund_txn_id,
                    "pmt_msg_3": "PAYMENT VOIDED/REFUNDED",
                    "date_3": date_and_time_3,
                    "rr_number_3": refund_rrn,
                    "auth_code_3": refund_auth_code,
                    "device_serial_3": device_serial,
                    "batch_number_3": batch_number_db_3,
                    "order_id_3": order_id,
                    "mid_3": mid,
                    "tid_3": tid,
                    "card_type_desc_3": "*1034 CTLS"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.info(f"Killing the app and relaunching the app")
                login_page.perform_login(username=app_username, password=app_password)
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment status value from txn history for the confirm preauth txn : {txn_id}, {payment_status_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode value from txn history for the confirm preauth txn : {txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id value from txn history for the confirm preauth txn : {txn_id}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching amount value from txn history for the confirm preauth txn : {txn_id}, {app_amount_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status value from txn history for the confirm preauth txn : {txn_id}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching payment msg value from txn history for the confirm preauth txn : {txn_id}, {app_payment_msg_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time value from txn history for the confirm preauth txn : {txn_id}, {app_date_and_time_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn value from txn history for the confirm preauth txn : {txn_id}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_cde value from txn history for the confirm preauth txn : {txn_id}, {app_auth_code_2}")
                app_batch_no_2 = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch number value from txn history for the confirm preauth txn : {txn_id}, {app_batch_no_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the confirm preauth txn : {txn_id}, {app_device_serial_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id value from txn history for the confirm preauth txn : {txn_id}, {app_order_id_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid value from txn history for the confirm preauth txn : {txn_id}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid value from txn history for the confirm preauth txn : {txn_id}, {app_tid_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card type value from txn history for the confirm preauth txn : {txn_id}, {app_card_type_desc_2}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the refund txn : {refund_txn_id}, {app_amount_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the refund txn : {refund_txn_id}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the refund txn : {refund_txn_id}, {app_txn_id_3}")
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the refund txn : {refund_txn_id}, {payment_status_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the refund txn : {refund_txn_id}, {app_rrn_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the refund txn : {refund_txn_id}, {app_order_id_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the refund txn : {refund_txn_id}, {app_payment_msg_3}")
                app_batch_no_3 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching txn batch no from txn history for the refund txn : {refund_txn_id}, {app_batch_no_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the refund txn : {refund_txn_id}, {app_settlement_status_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the refund txn : {refund_txn_id}, {app_auth_code_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the refund txn : {refund_txn_id}, {app_date_and_time_3}")
                app_device_serial_3 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the refund txn : {refund_txn_id}, {app_device_serial_3}")
                app_mid_3 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the refund txn : {refund_txn_id}, {app_mid_3}")
                app_tid_3 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the refund txn : {refund_txn_id}, {app_tid_3}")
                app_batch_number_3 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the refund txn : {refund_txn_id}, {app_batch_number_3}")
                app_card_type_desc_3 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the refund txn : {refund_txn_id}, {app_card_type_desc_3}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=original_txn_id)
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
                    "card_type_desc_2": app_card_type_desc_2,

                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "txn_id_3": app_txn_id_3,
                    "settle_status_3": app_settlement_status_3,
                    "pmt_msg_3": app_payment_msg_3,
                    "date_3": app_date_and_time_3,
                    "rr_number_3": app_rrn_3,
                    "auth_code_3": app_auth_code_3,
                    "device_serial_3": app_device_serial_3,
                    "batch_number_3": app_batch_no_3,
                    "order_id_3": app_order_id_3,
                    "mid_3": app_mid_3,
                    "tid_3": app_tid_3,
                    "card_type_desc_3": app_card_type_desc_3
                }

                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_date_and_time_api = date_time_converter.db_datetime(original_txn_created_time)
                expected_date_and_time_api_2 = date_time_converter.db_datetime(txn_created_time_2)
                expected_date_and_time_api_3 = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "CNF_PRE_AUTH",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(original_rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "txn_type": "PRE_AUTH",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": original_auth_code,
                    "date": expected_date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "CTLS",
                    "batch_number": batch_number,
                    "card_last_four_digit": "1034",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "541333",
                    "display_pan": "1034",

                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "CONF_PRE_AUTH",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_2,
                    "date_2": expected_date_and_time_api_2,
                    "device_serial_2": device_serial,
                    "username_2": app_username,
                    "txn_id_2": txn_id,
                    "pmt_card_brand_2": "MASTER_CARD",
                    "pmt_card_type_2": "CREDIT",
                    "card_txn_type_2": "CTLS",
                    "batch_number_2": batch_number,
                    "card_last_four_digit_2": "1034",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name,
                    "pmt_card_bin_2": "541333",
                    "display_pan_2": "1034",

                    "pmt_status_3": "REFUNDED",
                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "CARD",
                    "pmt_state_3": "AUTHORIZED",
                    "rrn_3": str(refund_rrn),
                    "settle_status_3": "PENDING",
                    "acquirer_code_3": "HDFC",
                    "txn_type_3": "REFUND",
                    "mid_3": mid,
                    "tid_3": tid,
                    "org_code_3": org_code,
                    "auth_code_3": refund_auth_code,
                    "date_3": expected_date_and_time_api_3,
                    "username_3": app_username,
                    "txn_id_3": refund_txn_id,
                    "pmt_card_brand_3": "MASTER_CARD",
                    "pmt_card_type_3": "CREDIT",
                    "card_txn_type_3": "CTLS",
                    "batch_number_3": batch_number_db_3,
                    "card_last_four_digit_3": "1034",
                    "external_ref_3": order_id,
                    "merchant_name_3": merchant_name,
                    "pmt_card_bin_3": "541333",
                    "display_pan_3": "1034"
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
                        logger.debug(f"Value of status obtained from txnlist api for original txn : {status_api}")
                        amount_api = float(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for original txn : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for original txn : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for original txn : {state_api}")
                        rrn_api = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for original txn : {rrn_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for original txn : {settlement_status_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for original txn : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for original txn : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for original txn : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for original txn : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for original txn : {txn_type_api}")
                        auth_code_api = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for original txn : {auth_code_api}")
                        date_and_time_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for original txn : {date_and_time_api}")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for original txn : {device_serial_api}")
                        username_api = elements["username"]
                        logger.debug(f"Value of username obtained from txnlist api for original txn : {username_api}")
                        txn_id_api = elements["txnId"]
                        logger.debug(f"Value of txnId obtained from txnlist api for original txn : {txn_id_api}")
                        payment_card_brand_api = elements["paymentCardBrand"]
                        logger.debug(f"Value of paymentCardBrand obtained from txnlist api for original txn : {payment_card_brand_api}")
                        payment_card_type_api = elements["paymentCardType"]
                        logger.debug(f"Value of paymentCardType obtained from txnlist api for original txn : {payment_card_type_api}")
                        card_txn_type_api = elements["cardTxnTypeDesc"]
                        logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for original txn : {card_txn_type_api}")
                        batch_number_api = elements["batchNumber"]
                        logger.debug(f"Value of batchNumber obtained from txnlist api for original txn : {batch_number_api}")
                        card_last_four_digit_api = elements["cardLastFourDigit"]
                        logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for original txn : {card_last_four_digit_api}")
                        external_ref_number_api = elements["externalRefNumber"]
                        logger.debug(f"Value of externalRefNumber obtained from txnlist api for original txn : {external_ref_number_api}")
                        merchant_name_api = elements["merchantName"]
                        logger.debug(f"Value of merchantName obtained from txnlist api for original txn : {merchant_name_api}")
                        payment_card_bin_api = elements["paymentCardBin"]
                        logger.debug(f"Value of paymentCardBin obtained from txnlist api for original txn : {payment_card_bin_api}")
                        display_pan_api = elements["displayPAN"]
                        logger.debug(f"Value of displayPAN obtained from txnlist api for original txn : {display_pan_api}")

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api_2 = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for confirm preauth txn : {status_api_2}")
                        amount_api_2 = float(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for confirm preauth txn : {amount_api_2}")
                        payment_mode_api_2 = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api confirm preauth txn : {payment_mode_api_2}")
                        state_api_2 = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for confirm preauth txn : {state_api_2}")
                        rrn_api_2 = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for confirm preauth txn : {rrn_api_2}")
                        settlement_status_api_2 = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for confirm preauth txn : {settlement_status_api_2}")
                        acquirer_code_api_2 = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for confirm preauth txn : {acquirer_code_api_2}")
                        org_code_api_2 = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for confirm preauth txn : {org_code_api_2}")
                        mid_api_2 = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for confirm preauth txn : {mid_api_2}")
                        tid_api_2 = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for confirm preauth txn : {tid_api_2}")
                        txn_type_api_2 = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for confirm preauth txn : {txn_type_api_2}")
                        auth_code_api_2 = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for confirm preauth txn : {auth_code_api_2}")
                        date_and_time_api_2 = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for confirm preauth txn : {date_and_time_api_2}")
                        device_serial_api_2 = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for confirm preauth txn : {device_serial_api_2}")
                        username_api_2 = elements["username"]
                        logger.debug(f"Value of username obtained from txnlist api for confirm preauth txn : {username_api_2}")
                        txn_id_api_2 = elements["txnId"]
                        logger.debug(f"Value of txnId obtained from txnlist api for confirm preauth txn : {txn_id_api_2}")
                        payment_card_brand_api_2 = elements["paymentCardBrand"]
                        logger.debug(f"Value of paymentCardBrand obtained from txnlist api for confirm preauth txn : {payment_card_brand_api_2}")
                        payment_card_type_api_2 = elements["paymentCardType"]
                        logger.debug(f"Value of paymentCardType obtained from txnlist api for confirm preauth txn : {payment_card_type_api_2}")
                        card_txn_type_api_2 = elements["cardTxnTypeDesc"]
                        logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for confirm preauth txn : {card_txn_type_api_2}")
                        batch_number_api_2 = elements["batchNumber"]
                        logger.debug(f"Value of batchNumber obtained from txnlist api for confirm preauth txn : {batch_number_api_2}")
                        card_last_four_digit_api_2 = elements["cardLastFourDigit"]
                        logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for confirm preauth txn : {card_last_four_digit_api_2}")
                        external_ref_number_api_2 = elements["externalRefNumber"]
                        logger.debug(f"Value of externalRefNumber obtained from txnlist api for confirm preauth txn : {external_ref_number_api_2}")
                        merchant_name_api_2 = elements["merchantName"]
                        logger.debug(f"Value of merchantName obtained from txnlist api for confirm preauth txn : {merchant_name_api_2}")
                        payment_card_bin_api_2 = elements["paymentCardBin"]
                        logger.debug(f"Value of paymentCardBin obtained from txnlist api for confirm preauth txn : {payment_card_bin_api_2}")
                        display_pan_api_2 = elements["displayPAN"]
                        logger.debug(f"Value of displayPAN obtained from txnlist api for confirm preauth txn : {display_pan_api_2}")

                for elements in response_in_list:
                    if elements["txnId"] == refund_txn_id:
                        status_api_3 = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for refund txn : {status_api_2}")
                        amount_api_3 = float(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for refund txn : {amount_api_2}")
                        payment_mode_api_3 = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api refund txn : {payment_mode_api_2}")
                        state_api_3 = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for refund txn : {state_api_3}")
                        rrn_api_3 = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for refund txn : {rrn_api_3}")
                        settlement_status_api_3 = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for refund txn : {settlement_status_api_3}")
                        acquirer_code_api_3 = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for refund txn : {acquirer_code_api_3}")
                        org_code_api_3 = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for refund txn : {org_code_api_3}")
                        mid_api_3 = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for refund txn : {mid_api_3}")
                        tid_api_3 = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for refund txn : {tid_api_3}")
                        txn_type_api_3 = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for refund txn : {txn_type_api_3}")
                        auth_code_api_3 = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for refund txn : {auth_code_api_3}")
                        date_and_time_api_3 = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for refund txn : {date_and_time_api_3}")
                        username_api_3 = elements["username"]
                        logger.debug(f"Value of username obtained from txnlist api for refund txn : {username_api_3}")
                        txn_id_api_3 = elements["txnId"]
                        logger.debug(f"Value of txnId obtained from txnlist api for refund txn : {txn_id_api_3}")
                        payment_card_brand_api_3 = elements["paymentCardBrand"]
                        logger.debug(f"Value of paymentCardBrand obtained from txnlist api for refund txn : {payment_card_brand_api_3}")
                        payment_card_type_api_3 = elements["paymentCardType"]
                        logger.debug(f"Value of paymentCardType obtained from txnlist api for refund txn : {payment_card_type_api_3}")
                        card_txn_type_api_3 = elements["cardTxnTypeDesc"]
                        logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for refund txn : {card_txn_type_api_3}")
                        batch_number_api_3 = elements["batchNumber"]
                        logger.debug(f"Value of batchNumber obtained from txnlist api for refund txn : {batch_number_api_3}")
                        card_last_four_digit_api_3 = elements["cardLastFourDigit"]
                        logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for refund txn : {card_last_four_digit_api_3}")
                        external_ref_number_api_3 = elements["externalRefNumber"]
                        logger.debug(f"Value of externalRefNumber obtained from txnlist api for refund txn : {external_ref_number_api_3}")
                        merchant_name_api_3 = elements["merchantName"]
                        logger.debug(f"Value of merchantName obtained from txnlist api for refund txn : {merchant_name_api_3}")
                        payment_card_bin_api_3 = elements["paymentCardBin"]
                        logger.debug(f"Value of paymentCardBin obtained from txnlist api for refund txn : {payment_card_bin_api_3}")
                        display_pan_api_3 = elements["displayPAN"]
                        logger.debug(f"Value of displayPAN obtained from txnlist api for refund txn : {display_pan_api_3}")

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

                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "mid_2": mid_api_2,
                    "txn_type_2": txn_type_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "auth_code_2": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "device_serial_2": device_serial_api_2,
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "display_pan_2": display_pan_api_2,

                    "pmt_status_3": status_api_3,
                    "txn_amt_3": amount_api_3,
                    "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_3,
                    "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "mid_3": mid_api_3,
                    "txn_type_3": txn_type_api_3,
                    "tid_3": tid_api_3,
                    "org_code_3": org_code_api_3,
                    "auth_code_3": auth_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_and_time_api_3),
                    "username_3": username_api_3,
                    "txn_id_3": txn_id_api_3,
                    "pmt_card_brand_3": payment_card_brand_api_3,
                    "pmt_card_type_3": payment_card_type_api_3,
                    "card_txn_type_3": card_txn_type_api_3,
                    "batch_number_3": batch_number_api_3,
                    "card_last_four_digit_3": card_last_four_digit_api_3,
                    "external_ref_3": external_ref_number_api_3,
                    "merchant_name_3": merchant_name_api_3,
                    "pmt_card_bin_3": payment_card_bin_api_3,
                    "display_pan_3": display_pan_api_3
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
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
                    "org_code": org_code,
                    "pmt_card_bin": "541333",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CONF_PRE_AUTH",
                    "card_txn_type": "91",
                    "card_last_four_digit": "1034",

                    "txn_amt_2": float(amount),
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

                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "CARD",
                    "pmt_status_3": "REFUNDED",
                    "pmt_state_3": "AUTHORIZED",
                    "acquirer_code_3": "HDFC",
                    "mid_3": mid,
                    "tid_3": tid,
                    "pmt_gateway_3": "DUMMY",
                    "settle_status_3": "PENDING",
                    "merchant_code_3": org_code,
                    "pmt_card_brand_3": "MASTER_CARD",
                    "pmt_card_type_3": "CREDIT",
                    "order_id_3": order_id,
                    "org_code_3": org_code,
                    "pmt_card_bin_3": "541333",
                    "terminal_info_id_3": terminal_info_id,
                    "txn_type_3": "REFUND",
                    "card_txn_type_3": "91",
                    "card_last_four_digit_3": "1034"
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

                    "txn_amt_3": amount_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "pmt_status_3": payment_status_db_3,
                    "pmt_state_3": payment_state_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "pmt_gateway_3": payment_gateway_db_3,
                    "settle_status_3": settlement_status_db_3,
                    "merchant_code_3": merchant_code_db_3,
                    "pmt_card_brand_3": payment_card_brand_db_3,
                    "pmt_card_type_3": payment_card_type_db_3,
                    "order_id_3": order_id_db_3,
                    "org_code_3": org_code_db_3,
                    "pmt_card_bin_3": payment_card_bin_db_3,
                    "terminal_info_id_3": terminal_info_id_db_3,
                    "txn_type_3": txn_type_db_3,
                    "card_txn_type_3": card_txn_type_db_3,
                    "card_last_four_digit_3": card_last_four_digit_db_3
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_db=txn_created_time_2)
                date_and_time_portal_3 = date_time_converter.to_portal_format(created_date_db=original_txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "REFUNDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": refund_txn_id,
                    "auth_code": refund_auth_code,
                    "rrn": refund_rrn,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_status_2": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id,
                    "auth_code_2": str(auth_code_2),
                    "rrn_2": rrn_2,

                    "date_time_3": date_and_time_portal_3,
                    "pmt_status_3": "CNF_PRE_AUTH",
                    "pmt_type_3": "CARD",
                    "txn_amt_3": "{:.2f}".format(amount),
                    "username_3": app_username,
                    "txn_id_3": original_txn_id,
                    "auth_code_3": str(original_auth_code),
                    "rrn_3": str(original_rrn),
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                date_time_3 = transaction_details[2]['Date & Time']
                transaction_id_3 = transaction_details[2]['Transaction ID']
                total_amount_3 = transaction_details[2]['Total Amount'].replace(",", "").split()
                rr_number_portal_3 = transaction_details[2]['RR Number']
                transaction_type_3 = transaction_details[2]['Type']
                status_3 = transaction_details[2]['Status']
                username_3 = transaction_details[2]['Username']
                auth_code_portal_3 = transaction_details[1]['Auth Code']

                date_time_2 = transaction_details[1]['Date & Time']
                transaction_id_2 = transaction_details[1]['Transaction ID']
                total_amount_2 = transaction_details[1]['Total Amount'].replace(",", "").split()
                rr_number_portal_2 = transaction_details[1]['RR Number']
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
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time,

                    "date_time_2": date_time_2,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_portal_2,

                    "date_time_3": date_time_3,
                    "pmt_status_3": str(status_3),
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "auth_code_3": auth_code_portal_3,
                    "rrn_3": rr_number_portal_3,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:

                txn_date, txn_time = date_time_converter.to_chargeslip_format(original_txn_created_time)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(txn_created_time_2)
                expected_charge_slip_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(original_rrn),
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date,
                    'BATCH NO': batch_number,
                    'CARD TYPE': 'MasterCard',
                    'payment_option': 'SALE',
                    'TID': tid,
                    'time': txn_time,
                    'AUTH CODE': str(original_auth_code)
                }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                chargeslip_val_result = receipt_validator.perform_charge_slip_validations(original_txn_id,{"username": app_username,"password": app_password},
                                                                                            expected_charge_slip_values)
                expected_charge_slip_values_2 = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date_2,
                    'BATCH NO': batch_number,
                    'CARD TYPE': 'MasterCard',
                    'payment_option': 'REFUND',
                    'TID': tid,
                    'time': txn_time_2,
                    'AUTH CODE': str(auth_code_2)
                }
                logger.debug(f"expected_charge_slip_values_2 : {expected_charge_slip_values_2}")
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
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)