import random
import sys
import time
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_LoginPage import LoginPage
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.sa.app_card_page import CardPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_287():
    """
        Sub Feature Code: UI_Common_Mpos_Refund_From_POS_Validate_Full_Refund_Card_EMV_VISA_DEBIT_476173
        Sub Feature Description: Verify that the user can perform a full refund for Card transactions using the Refund from POS feature (bin:476173)
        TC naming code description:  100: Payment Method, 115: CARD_UI, 287: TC287
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
        logger.debug(f"Query to fetch data from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid value from terminal_info table : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid value from the terminal_info table : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id value from terminal_info table : {terminal_info_id}")

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
        api_details["RequestBody"]["settings"]["maxRefund"] = '0'
        logger.debug(f"API details for org_settings_update : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received after enabling maximum refund settings : {response}")

        query = f"select bank_code from bin_info where bin='476173'"
        logger.debug(f"Query to fetch bank_code value from bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(600, 2000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount : {amount}, order_id : {order_id}, and device_serial : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_VISA_DEBIT_476173")
            card_page.select_cardtype(text="EMV_VISA_DEBIT_476173")
            logger.debug(f"Selected the card type as : EMV_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details for settlement : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")
            settle_success = settle_response['success']
            logger.debug(f"Fetching success value after settlement is : {settle_success}")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result obtained for txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table : {txn_id} ")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
            logger.debug(f"Clicking on refund button on app side")
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side")
            payment_page.click_on_refund_full_amt()
            logger.debug(f"Clicked on refund full amount")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button and refunded full amount")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm the refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for original txn : {txn_id} : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from txn table for original txn : {txn_id} : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for original txn : {txn_id} : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from value from txn table for original txn : {txn_id} : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for original txn : {txn_id} : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for original txn : {txn_id} : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for original txn : {txn_id} : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for original txn : {txn_id} : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for original txn : {txn_id} : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for original txn : {txn_id} : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for original txn : {txn_id} : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for original txn : {txn_id} : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for original txn : {txn_id} : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for original txn : {txn_id} : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for original txn : {txn_id} : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for original txn : {txn_id} : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for original txn : {txn_id} : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for original txn : {txn_id} : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for original txn : {txn_id} : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for original txn : {txn_id} : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for original txn : {txn_id} : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for original txn : {txn_id} : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for original txn : {txn_id} : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for original txn : {txn_id} : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for original txn : {txn_id} : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for original txn : {txn_id} : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for original txn : {txn_id} : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for original txn : {txn_id} : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for original txn : {txn_id} : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for original txn : {txn_id} : {posting_date}")

            query = ("select * from txn where org_code = '" + str(org_code) +
                     "' AND external_ref = '" + str(order_id) + "' order by created_time desc limit 1")
            logger.debug(f"Query to fetch data from txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for refund txn : {result}")
            txn_id_2 = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table for refund txn : {txn_id_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for refund txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for refund txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from txn table for refund txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for refund txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for refund txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for refund txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for refund txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for refund txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for refund txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for refund txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table fro refund txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for refund txn : {settlement_status_db_2}")
            device_serial_db_2 = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for refund txn : {device_serial_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for refund txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for refund txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for refund txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for refund txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for refund txn : {order_id_db_2}")
            issuer_code_db_2 = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for refund txn : {issuer_code_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for refund txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for refund txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for refund txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for refund txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for refund txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for refund txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for refund txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for refund txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for refund txn : {merchant_name_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for refund txn : {posting_date_2}")

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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=posting_date)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=posting_date_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "REFUND SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "L3TEST",
                    "card_type_desc": "*0250 EMV",

                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "L3TEST",
                    "card_type_desc_2": "*0250 EMV"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
                logger.debug(f"Logged into the MPOS after restarting with username : {app_username} and password : {app_password}")
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for original_txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for original_txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for original_txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for original_txn : {txn_id}, {payment_status}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for original_txn : {txn_id}, {app_card_type_desc}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for original_txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for original_txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for original_txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for original_txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for original_txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for original_txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for original_txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for original_txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for original_txn: {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for original_txn : {txn_id}, {app_batch_number}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for original_txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for refunded txn : {txn_id_2}, {payment_status_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for refunded txn : {txn_id_2}, {app_card_type_desc_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for refunded txn : {txn_id_2}, {app_rrn_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for refunded txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for refunded txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for refunded txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for refunded txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for refunded txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for refunded txn : {txn_id_2}, {app_customer_name_2}")

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

                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "card_txn_type": "EMV",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "L3TEST/CARD0025",
                    "pmt_card_bin": "476173",
                    "name_on_card": "L3TEST/CARD0025",
                    "display_pan": "0250",

                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "card_txn_type_2": "EMV",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "L3TEST/CARD0025",
                    "pmt_card_bin_2": "476173",
                    "name_on_card_2": "L3TEST/CARD0025",
                    "display_pan_2": "0250"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status value from original txn_id : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount value from original txn_id : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode value from original txn_id : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state value from original txn_id : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn value from original txn_id : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from original txn_id : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer_code value from original txn_id : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from original txn_id : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org_code value from original txn_id : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid value from original txn_id : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid value from original txn_id : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction_type value from original txn_id : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth_code value from original txn_id : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date_and_time value from original txn_id : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device_serial value from original txn_id : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username value from original txn_id : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction_id value from original txn_id : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from original txn_id : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from original txn_id : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn_type value from original txn_id : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch_number value from original txn_id : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from original txn_id : {card_last_four_digit_api}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer_name value from original txn_id : {customer_name_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from original txn_id : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant_name value from original txn_id : {merchant_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer_name value from original txn_id : {payer_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from original txn_id : {payment_card_bin_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from original txn_id : {name_on_card_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN value from original txn_id : {display_pan_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status value from refunded txn_id : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount value from refunded txn_id : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment_mode value from refunded txn_id : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state value from refunded txn_id : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn value from refunded txn_id : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from refunded txn_id : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from refunded txn_id : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org_code value from refunded txn_id : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid value from refunded txn_id : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid value from refunded txn_id : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction_type value from refunded txn_id : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth_code value from refunded txn_id : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date_and_time value from refunded txn_id : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username value from refunded txn_id : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction_id value from refunded txn_id : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from refunded txn_id : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from refunded txn_id : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card_txn_type value from refunded txn_id : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch_no value from refunded txn_id : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from refunded txn_id  : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer_name value from refunded txn_id : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from refunded txn_id : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant_name value from refunded txn_id : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer_name value from refunded txn_id : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from refunded txn_id : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from refunded txn_id : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN value from refunded txn_id : {display_pan_api_2}")

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

                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2
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
                    "txn_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "476173",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "payer_name": "L3TEST/CARD0025",

                    "txn_amt_2": amount,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "device_serial_2": device_serial,
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "order_id_2": order_id,
                    "issuer_code_2": None,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "476173",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "02",
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "payer_name_2": "L3TEST/CARD0025"
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
                    "issuer_code_2": issuer_code_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2
                }
                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date_2)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn_2),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "AUTH CODE": auth_code_2,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": batch_number_db_2,
                    "CARD": "XXXX-XXXX-XXXX-0250 EMV",
                    "TID": tid
                }
                logger.info(f"expected_charge_slip_values : {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_288():
    """
        Sub Feature Code: UI_Common_Mpos_Refund_From_POS_Validate_Partial_Refund_Card_EMV_VISA_DEBIT_476173
        Sub Feature Description: Verify the user can perform a partial refund for Card transactions using Refund from POS (bin:476173)
        TC naming code description:  100: Payment Method, 115: CARD_UI, 288: TC288
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
        logger.debug(f"Query to fetch data from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid value from terminal_info table : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid value from the terminal_info table :  {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id value from terminal_info table : {terminal_info_id}")

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
        api_details["RequestBody"]["settings"]["maxRefund"] = '0'
        logger.debug(f"API details : {api_details}")
        logger.debug(f"API details for org_settings_update : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received after enabling maximum refund settings : {response}")

        query = f"select bank_code from bin_info where bin='476173'"
        logger.debug(f"Query to fetch bank_code value from bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(600, 2000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount : {amount}, order_id : {order_id}, and device_serial : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_VISA_DEBIT_476173")
            card_page.select_cardtype(text="EMV_VISA_DEBIT_476173")
            logger.debug(f"Selected the card type as : EMV_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details for settlement : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")
            settle_success = settle_response['success']
            logger.debug(f"Fetching success value after settlement is : {settle_success}")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result obtained for txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table : {txn_id} ")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
            logger.debug(f"Clicking on refund button on app side")
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side")
            manually_enter_amt = amount - 100
            logger.debug(f"Manually entered amount : {manually_enter_amt}")
            logger.debug(f"Clicking on refund amount manually radio button")
            payment_page.click_on_refund_amt_manually()
            logger.debug(f"Clicked on refund amount manually radio button")
            payment_page.enter_refund_amt_manually(amount=manually_enter_amt)
            logger.debug(f"Entered amount manually for refund amount manually : {manually_enter_amt}")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button and refunded full amount")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm the refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for original txn : {txn_id} : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from txn table for original txn : {txn_id} : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for original txn : {txn_id} : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from value from txn table for original txn : {txn_id} : {amount_db}")
            original_amt_db = int(result["amount_original"].iloc[0])
            logger.debug(f"Fetching amount_original from value from txn table for original txn : {original_amt_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for original txn : {txn_id} : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for original txn : {txn_id} : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for original txn : {txn_id} : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for original txn : {txn_id} : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for original txn : {txn_id} : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for original txn : {txn_id} : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for original txn : {txn_id} : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for original txn : {txn_id} : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for original txn : {txn_id} : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for original txn : {txn_id} : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for original txn : {txn_id} : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for original txn : {txn_id} : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for original txn : {txn_id} : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for original txn : {txn_id} : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for original txn : {txn_id} : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for original txn : {txn_id} : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for original txn : {txn_id} : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for original txn : {txn_id} : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for original txn : {txn_id} : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for original txn : {txn_id} : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for original txn : {txn_id} : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for original txn : {txn_id} : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for original txn : {txn_id} : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for original txn : {txn_id} : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for original txn : {txn_id} : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for original txn : {txn_id} : {posting_date}")

            query = ("select * from txn where org_code = '" + str(org_code) +
                     "' AND external_ref = '" + str(order_id) + "' order by created_time desc limit 1")
            logger.debug(f"Query to fetch data from txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for refund txn : {result}")
            txn_id_2 = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table for refund txn : {txn_id_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for refund txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for refund txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from txn table for refund txn : {amount_db_2}")
            original_amt_db_2 = int(result["amount_original"].iloc[0])
            logger.debug(f"Fetching amount_original from txn table for refund txn : {original_amt_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for refund txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for refund txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for refund txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for refund txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for refund txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for refund txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for refund txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table fro refund txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for refund txn : {settlement_status_db_2}")
            device_serial_db_2 = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for refund txn : {device_serial_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for refund txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for refund txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for refund txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for refund txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for refund txn : {order_id_db_2}")
            issuer_code_db_2 = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for refund txn : {issuer_code_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for refund txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for refund txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for refund txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for refund txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for refund txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for refund txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for refund txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for refund txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for refund txn : {merchant_name_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for refund txn : {posting_date_2}")

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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=posting_date)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=posting_date_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "PARTIALLY REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "original_amt": "{:,.0f}".format(amount),
                    "refunded_amt": "{:,.0f}".format(manually_enter_amt),
                    "balance_amt": "{:,.0f}".format(amount - manually_enter_amt),
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "L3TEST",
                    "card_type_desc": "*0250 EMV",

                    "txn_amt_2": "{:,.2f}".format(manually_enter_amt),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "L3TEST",
                    "card_type_desc_2": "*0250 EMV"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
                logger.debug(f"Logged into the MPOS after restarting with username : {app_username} and password : {app_password}")
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for original_txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for original_txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for original_txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for original_txn : {txn_id}, {payment_status}")
                app_original_amt = txn_history_page.fetch_original_amt_text()
                logger.debug(f"Fetching original_amt from txn history for original_txn : {txn_id}, {app_original_amt}")
                app_refunded_amt = txn_history_page.fetch_refunded_amt_text()
                logger.debug(f"Fetching refunded_amt from txn history for original_txn : {txn_id}, {app_refunded_amt}")
                app_balance_amt = txn_history_page.fetch_balance_amt_text()
                logger.debug(f"Fetching balance_amt from txn history for original_txn : {txn_id}, {app_balance_amt}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for original_txn : {txn_id}, {app_customer_name}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for original_txn : {txn_id}, {app_date_and_time}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for original_txn : {txn_id}, {app_card_type_desc}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for original_txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for original_txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for original_txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for original_txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for original_txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for original_txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for original_txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for original_txn: {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for original_txn : {txn_id}, {app_batch_number}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for refunded txn : {txn_id_2}, {payment_status_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for refunded txn : {txn_id_2}, {app_card_type_desc_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for refunded txn : {txn_id_2}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for refunded txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for refunded txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for refunded txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for refunded txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for refunded txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for refunded txn : {txn_id_2}, {app_customer_name_2}")

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
                    "original_amt": app_original_amt.split('₹')[1],
                    "refunded_amt": app_refunded_amt.split('₹')[1],
                    "balance_amt": app_balance_amt.split('₹')[1],
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_number,
                    "customer_name": app_customer_name,
                    "card_type_desc": app_card_type_desc,

                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "original_amt": float(amount),
                    "total_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "card_txn_type": "EMV",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "L3TEST/CARD0025",
                    "pmt_card_bin": "476173",
                    "name_on_card": "L3TEST/CARD0025",
                    "display_pan": "0250",

                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(manually_enter_amt),
                    "original_amt_2": float(manually_enter_amt),
                    "total_amt_2": float(manually_enter_amt),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "card_txn_type_2": "EMV",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "L3TEST/CARD0025",
                    "pmt_card_bin_2": "476173",
                    "name_on_card_2": "L3TEST/CARD0025",
                    "display_pan_2": "0250"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status value from original txn_id : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount value from original txn_id : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode value from original txn_id : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state value from original txn_id : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn value from original txn_id : {rrn_api}")
                original_amount_api = float(response_1["amount"])
                logger.debug(f"Fetching original_amount value from original txn_id : {original_amount_api}")
                total_amt_api = float(response_1["totalAmount"])
                logger.debug(f"Fetching total_amount value from original txn_id : {total_amt_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from original txn_id : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer_code value from original txn_id : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from original txn_id : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org_code value from original txn_id : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid value from original txn_id : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid value from original txn_id : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction_type value from original txn_id : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth_code value from original txn_id : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date_and_time value from original txn_id : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device_serial value from original txn_id : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username value from original txn_id : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction_id value from original txn_id : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from original txn_id : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from original txn_id : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn_type value from original txn_id : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch_number value from original txn_id : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from original txn_id : {card_last_four_digit_api}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer_name value from original txn_id : {customer_name_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from original txn_id : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant_name value from original txn_id : {merchant_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer_name value from original txn_id : {payer_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from original txn_id : {payment_card_bin_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from original txn_id : {name_on_card_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN value from original txn_id : {display_pan_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status value from refunded txn_id : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount value from refunded txn_id : {amount_api_2}")
                original_amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching original_amount value from refunded txn_id : {original_amount_api_2}")
                total_amt_api_2 = float(response_2["totalAmount"])
                logger.debug(f"Fetching total_amount value from refunded txn_id : {total_amt_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment_mode value from refunded txn_id : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state value from refunded txn_id : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn value from refunded txn_id : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from refunded txn_id : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from refunded txn_id : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org_code value from refunded txn_id : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid value from refunded txn_id : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid value from refunded txn_id : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction_type value from refunded txn_id : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth_code value from refunded txn_id : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date_and_time value from refunded txn_id : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username value from refunded txn_id : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction_id value from refunded txn_id : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from refunded txn_id : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from refunded txn_id : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card_txn_type value from refunded txn_id : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch_no value from refunded txn_id : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from refunded txn_id  : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer_name value from refunded txn_id : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from refunded txn_id : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant_name value from refunded txn_id : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer_name value from refunded txn_id : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from refunded txn_id : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from refunded txn_id : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN value from refunded txn_id : {display_pan_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "original_amt": original_amount_api,
                    "total_amt": total_amt_api,
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

                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "original_amt_2": original_amount_api_2,
                    "total_amt_2": total_amt_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2
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
                    "txn_amt": amount,
                    "original_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "476173",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "payer_name": "L3TEST/CARD0025",

                    "txn_amt_2": manually_enter_amt,
                    "original_amt_2": manually_enter_amt,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "device_serial_2": device_serial,
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "order_id_2": order_id,
                    "issuer_code_2": None,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "476173",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "02",
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "payer_name_2": "L3TEST/CARD0025"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "original_amt": original_amt_db,
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

                    "txn_amt_2": amount_db_2,
                    "original_amt_2": original_amt_db_2,
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
                    "issuer_code_2": issuer_code_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2
                }
                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date_2)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn_2),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(manually_enter_amt),
                    "AUTH CODE": auth_code_2,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": batch_number_db_2,
                    "CARD": "XXXX-XXXX-XXXX-0250 EMV",
                    "TID": tid
                }
                logger.info(f"expected_charge_slip_values : {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_289():
    """
        Sub Feature Code: UI_Common_Mpos_Refund_From_POS_Check_Card_Max_refund_Adjustment_EMV_VISA_DEBIT_476173
                                                    (OR)
        UI_Common_Mpos_Refund_From_POS_Confirm_Partial_Refund_Card_Setting_On_EMV_VISA_DEBIT_476173
                                                    (OR)
        UI_Common_Mpos_Refund_From_POS_Allow_Refunds_Partially_Refunded_Card_EMV_VISA_DEBIT_476173

        Sub Feature Description: Verify the maximum refundable amount changes for Card payment mode based on the 'Maximum refund allowed' setting (bin: 476173)
                                                    (OR)
        Verify the user can do a partial Card refund when the 'Maximum refund allowed' setting is ON (bin: 476173)
                                                    (OR)
        Verify the user can initiate and complete a refund for partially refunded transactions (bin: 476173)

        TC naming code description:  100: Payment Method, 115: CARD_UI, 289: TC289
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
        logger.debug(f"Query to fetch data from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid value from terminal_info table : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid value from the terminal_info table :  {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id value from terminal_info table : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        #Enter the maximum_refund_value amount
        max_refund_value = "9"

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["maxRefund"] = max_refund_value
        logger.debug(f"API details for org_settings_update : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received after enabling maximum refund settings : {response}")

        query = f"select bank_code from bin_info where bin='476173'"
        logger.debug(f"Query to fetch bank_code value from bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        query = f"select * from setting where org_code='{org_code}' and setting_name='maxRefund'"
        logger.debug(f"Query to fetch data from the setting table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from setting table : {result}")
        setting_value_db = int(result['setting_value'].values[0])
        logger.debug(f"Fetching setting value from setting table is : {setting_value_db}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(600, 2000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is: {amount},{order_id},{device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_VISA_DEBIT_476173")
            card_page.select_cardtype(text="EMV_VISA_DEBIT_476173")
            logger.debug(f"Selected the card type as : EMV_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details for settlement : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")
            settle_success = settle_response['success']
            logger.debug(f"Fetching success value after settlement is : {settle_success}")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result obtained for txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table : {txn_id} ")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
            logger.debug(f"Clicking on refund button on app side")
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side")
            manually_enter_amt = amount - 100
            logger.debug(f"Manually entered amount : {manually_enter_amt}")
            logger.debug(f"Clicking on refund amount manually radio button")
            payment_page.click_on_refund_amt_manually()
            logger.debug(f"Clicked on refund amount manually radio button")
            logger.debug(f"Entering amount manually for refund amount manually : {manually_enter_amt}")
            payment_page.enter_refund_amt_manually(amount=manually_enter_amt)
            logger.debug(f"Entered amount manually for refund amount manually")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button and refunded full amount")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm the refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for original txn : {txn_id} : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from txn table for original txn : {txn_id} : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for original txn : {txn_id} : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from value from txn table for original txn : {txn_id} : {amount_db}")
            original_amt_db = int(result["amount_original"].iloc[0])
            logger.debug(f"Fetching amount_original from value from txn table for original txn : {original_amt_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for original txn : {txn_id} : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for original txn : {txn_id} : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for original txn : {txn_id} : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for original txn : {txn_id} : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for original txn : {txn_id} : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for original txn : {txn_id} : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for original txn : {txn_id} : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for original txn : {txn_id} : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for original txn : {txn_id} : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for original txn : {txn_id} : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for original txn : {txn_id} : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for original txn : {txn_id} : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for original txn : {txn_id} : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for original txn : {txn_id} : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for original txn : {txn_id} : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for original txn : {txn_id} : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for original txn : {txn_id} : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for original txn : {txn_id} : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for original txn : {txn_id} : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for original txn : {txn_id} : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for original txn : {txn_id} : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for original txn : {txn_id} : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for original txn : {txn_id} : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for original txn : {txn_id} : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for original txn : {txn_id} : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for original txn : {txn_id} : {posting_date}")

            query = ("select * from txn where org_code = '" + str(org_code) +
                     "' AND external_ref = '" + str(order_id) + "' order by created_time desc limit 1")
            logger.debug(f"Query to fetch data from txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for refund txn : {result}")
            txn_id_2 = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table for refund txn : {txn_id_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for refund txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for refund txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from txn table for refund txn : {amount_db_2}")
            original_amt_db_2 = int(result["amount_original"].iloc[0])
            logger.debug(f"Fetching amount_original from txn table for refund txn : {original_amt_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for refund txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for refund txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for refund txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for refund txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for refund txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for refund txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for refund txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table fro refund txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for refund txn : {settlement_status_db_2}")
            device_serial_db_2 = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for refund txn : {device_serial_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for refund txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for refund txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for refund txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for refund txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for refund txn : {order_id_db_2}")
            issuer_code_db_2 = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for refund txn : {issuer_code_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for refund txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for refund txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for refund txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for refund txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for refund txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for refund txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for refund txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for refund txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for refund txn : {merchant_name_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for refund txn : {posting_date_2}")

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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=posting_date)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=posting_date_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "PARTIALLY REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "original_amt": "{:,.0f}".format(amount),
                    "refunded_amt": "{:,.0f}".format(manually_enter_amt),
                    "balance_amt": "{:,.2f}".format((amount - manually_enter_amt) + (amount * (setting_value_db / 100))),
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "L3TEST",
                    "card_type_desc": "*0250 EMV",

                    "txn_amt_2": "{:,.2f}".format(manually_enter_amt),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "L3TEST",
                    "card_type_desc_2": "*0250 EMV"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
                logger.debug(f"Logged into the MPOS after restarting with username : {app_username} and password : {app_password}")
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for original_txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for original_txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for original_txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for original_txn : {txn_id}, {payment_status}")
                app_original_amt = txn_history_page.fetch_original_amt_text()
                logger.debug(f"Fetching original_amt from txn history for original_txn : {txn_id}, {app_original_amt}")
                app_refunded_amt = txn_history_page.fetch_refunded_amt_text()
                logger.debug(f"Fetching refunded_amt from txn history for original_txn : {txn_id}, {app_refunded_amt}")
                app_balance_amt = txn_history_page.fetch_balance_amt_text()
                logger.debug(f"Fetching balance_amt from txn history for original_txn : {txn_id}, {app_balance_amt}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for original_txn : {txn_id}, {app_customer_name}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for original_txn : {txn_id}, {app_date_and_time}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for original_txn : {txn_id}, {app_card_type_desc}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for original_txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for original_txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for original_txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for original_txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for original_txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for original_txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for original_txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for original_txn: {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for original_txn : {txn_id}, {app_batch_number}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for refunded txn : {txn_id_2}, {payment_status_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for refunded txn : {txn_id_2}, {app_card_type_desc_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for refunded txn : {txn_id_2}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for refunded txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for refunded txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for refunded txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for refunded txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for refunded txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for refunded txn : {txn_id_2}, {app_customer_name_2}")

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
                    "original_amt": app_original_amt.split('₹')[1],
                    "refunded_amt": app_refunded_amt.split('₹')[1],
                    "balance_amt": app_balance_amt.split('₹')[1],
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_number,
                    "customer_name": app_customer_name,
                    "card_type_desc": app_card_type_desc,

                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "original_amt": float(amount),
                    "total_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "card_txn_type": "EMV",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "L3TEST/CARD0025",
                    "pmt_card_bin": "476173",
                    "name_on_card": "L3TEST/CARD0025",
                    "display_pan": "0250",

                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(manually_enter_amt),
                    "original_amt_2": float(manually_enter_amt),
                    "total_amt_2": float(manually_enter_amt),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "card_txn_type_2": "EMV",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "L3TEST/CARD0025",
                    "pmt_card_bin_2": "476173",
                    "name_on_card_2": "L3TEST/CARD0025",
                    "display_pan_2": "0250"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status value from original txn_id : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount value from original txn_id : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode value from original txn_id : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state value from original txn_id : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn value from original txn_id : {rrn_api}")
                original_amount_api = float(response_1["amount"])
                logger.debug(f"Fetching original_amount value from original txn_id : {original_amount_api}")
                total_amt_api = float(response_1["totalAmount"])
                logger.debug(f"Fetching total_amount value from original txn_id : {total_amt_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from original txn_id : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer_code value from original txn_id : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from original txn_id : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org_code value from original txn_id : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid value from original txn_id : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid value from original txn_id : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction_type value from original txn_id : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth_code value from original txn_id : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date_and_time value from original txn_id : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device_serial value from original txn_id : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username value from original txn_id : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction_id value from original txn_id : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from original txn_id : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from original txn_id : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn_type value from original txn_id : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch_number value from original txn_id : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from original txn_id : {card_last_four_digit_api}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer_name value from original txn_id : {customer_name_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from original txn_id : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant_name value from original txn_id : {merchant_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer_name value from original txn_id : {payer_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from original txn_id : {payment_card_bin_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from original txn_id : {name_on_card_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN value from original txn_id : {display_pan_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status value from refunded txn_id : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount value from refunded txn_id : {amount_api_2}")
                original_amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching original_amount value from refunded txn_id : {original_amount_api_2}")
                total_amt_api_2 = float(response_2["totalAmount"])
                logger.debug(f"Fetching total_amount value from refunded txn_id : {total_amt_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment_mode value from refunded txn_id : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state value from refunded txn_id : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn value from refunded txn_id : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from refunded txn_id : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from refunded txn_id : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org_code value from refunded txn_id : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid value from refunded txn_id : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid value from refunded txn_id : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction_type value from refunded txn_id : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth_code value from refunded txn_id : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date_and_time value from refunded txn_id : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username value from refunded txn_id : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction_id value from refunded txn_id : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from refunded txn_id : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from refunded txn_id : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card_txn_type value from refunded txn_id : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch_no value from refunded txn_id : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from refunded txn_id  : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer_name value from refunded txn_id : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from refunded txn_id : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant_name value from refunded txn_id : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer_name value from refunded txn_id : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from refunded txn_id : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from refunded txn_id : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN value from refunded txn_id : {display_pan_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "original_amt": original_amount_api,
                    "total_amt": total_amt_api,
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

                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "original_amt_2": original_amount_api_2,
                    "total_amt_2": total_amt_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2
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
                    "txn_amt": amount,
                    "original_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "476173",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "payer_name": "L3TEST/CARD0025",

                    "txn_amt_2": manually_enter_amt,
                    "original_amt_2": manually_enter_amt,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "device_serial_2": device_serial,
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "order_id_2": order_id,
                    "issuer_code_2": None,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "476173",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "02",
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "payer_name_2": "L3TEST/CARD0025"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "original_amt": original_amt_db,
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

                    "txn_amt_2": amount_db_2,
                    "original_amt_2": original_amt_db_2,
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
                    "issuer_code_2": issuer_code_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2
                }
                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date_2)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn_2),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(manually_enter_amt),
                    "AUTH CODE": auth_code_2,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": batch_number_db_2,
                    "CARD": "XXXX-XXXX-XXXX-0250 EMV",
                    "TID": tid
                }
                logger.info(f"expected_charge_slip_values : {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_290():
    """
        Sub Feature Code: UI_Common_Mpos_Refund_From_POS_Confirm_Full_Refund_Card_Setting_On_EMV_VISA_DEBIT_476173
        Sub Feature Description: Verify the user can do a full Card refund when the 'Maximum refund allowed' setting is ON (bin:476173)
        TC naming code description:  100: Payment Method, 115: CARD_UI, 290: TC290
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
        logger.debug(f"Query to fetch data from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid value from terminal_info table : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid value from the terminal_info table :  {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id value from terminal_info table : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        #Enter the maximum_refund_value amount
        max_refund_value = "9"

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["maxRefund"] = max_refund_value
        logger.debug(f"API details for org_settings_update : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received after enabling maximum refund settings : {response}")

        query = f"select bank_code from bin_info where bin='476173'"
        logger.debug(f"Query to fetch bank_code value from bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        query = f"select * from setting where org_code='{org_code}' and setting_name='maxRefund'"
        logger.debug(f"Query to fetch data from the setting table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from setting table : {result}")
        setting_value_db = int(result['setting_value'].values[0])
        logger.debug(f"Fetching setting value from setting table is : {setting_value_db}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(600, 2000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount : {amount}, order_id : {order_id}, and device_serial : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_VISA_DEBIT_476173")
            card_page.select_cardtype(text="EMV_VISA_DEBIT_476173")
            logger.debug(f"Selected the card type as : EMV_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details for settlement : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")
            settle_success = settle_response['success']
            logger.debug(f"Fetching success value after settlement is : {settle_success}")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result obtained for txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table : {txn_id} ")

            cal_for_max_per = round(amount * (setting_value_db / 100),2)
            logger.debug(f"calculation_for_max_percentage is : {cal_for_max_per} ")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
            logger.debug(f"Clicking on refund button on app side")
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side")
            payment_page.click_on_refund_full_amt()
            logger.debug(f"Clicked on refund full amount")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button and refunded full amount")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm the refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for original txn : {txn_id} : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from txn table for original txn : {txn_id} : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for original txn : {txn_id} : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from value from txn table for original txn : {txn_id} : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for original txn : {txn_id} : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(
                f"Fetching payment status value from txn table for original txn : {txn_id} : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(
                f"Fetching payment state value from txn table for original txn : {txn_id} : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(
                f"Fetching acquirer code value from txn table for original txn : {txn_id} : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for original txn : {txn_id} : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for original txn : {txn_id} : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(
                f"Fetching payment gateway value from txn table for original txn : {txn_id} : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for original txn : {txn_id} : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(
                f"Fetching settlement status value from txn table for original txn : {txn_id} : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(
                f"Fetching device serial value from txn table for original txn : {txn_id} : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(
                f"Fetching merchant code value from txn table for original txn : {txn_id} : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(
                f"Fetching payment card brand value from txn table for original txn : {txn_id} : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(
                f"Fetching payment card type value from txn table for original txn : {txn_id} : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for original txn : {txn_id} : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for original txn : {txn_id} : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for original txn : {txn_id} : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for original txn : {txn_id} : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(
                f"Fetching card bin number value from txn table for original txn : {txn_id} : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(
                f"Fetching terminal info id value from txn table for original txn : {txn_id} : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for original txn : {txn_id} : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(
                f"Fetching card txn type value from txn table for original txn : {txn_id} : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(
                f"Fetching card last four digit value from txn table for original txn : {txn_id} : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(
                f"Fetching customer name value from txn table for original txn : {txn_id} : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for original txn : {txn_id} : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for original txn : {txn_id} : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for original txn : {txn_id} : {posting_date}")

            query = ("select * from txn where org_code = '" + str(org_code) +
                     "' AND external_ref = '" + str(order_id) + "' order by created_time desc limit 1")
            logger.debug(f"Query to fetch data from txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for refund txn : {result}")
            txn_id_2 = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table for refund txn : {txn_id_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for refund txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for refund txn : {created_time_2}")
            amount_db_2 = float(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from txn table for refund txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for refund txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for refund txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for refund txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for refund txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for refund txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for refund txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for refund txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table fro refund txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for refund txn : {settlement_status_db_2}")
            device_serial_db_2 = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for refund txn : {device_serial_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for refund txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for refund txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for refund txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for refund txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for refund txn : {order_id_db_2}")
            issuer_code_db_2 = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for refund txn : {issuer_code_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for refund txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for refund txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for refund txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for refund txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for refund txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for refund txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for refund txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for refund txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for refund txn : {merchant_name_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for refund txn : {posting_date_2}")

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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=posting_date)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=posting_date_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "REFUND SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "L3TEST",
                    "card_type_desc": "*0250 EMV",

                    "txn_amt_2": "{:,.2f}".format(cal_for_max_per + int(amount)),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "L3TEST",
                    "card_type_desc_2": "*0250 EMV"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
                logger.debug(f"Logged into the MPOS after restarting with username : {app_username} and password : {app_password}")
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for original_txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for original_txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for original_txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for original_txn : {txn_id}, {payment_status}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for original_txn : {txn_id}, {app_card_type_desc}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for original_txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for original_txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for original_txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for original_txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for original_txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for original_txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for original_txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for original_txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for original_txn: {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for original_txn : {txn_id}, {app_batch_number}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for original_txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for refunded txn : {txn_id_2}, {payment_status_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for refunded txn : {txn_id_2}, {app_card_type_desc_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for refunded txn : {txn_id_2}, {app_rrn_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for refunded txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for refunded txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for refunded txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for refunded txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for refunded txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for refunded txn : {txn_id_2}, {app_customer_name_2}")

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

                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "card_txn_type": "EMV",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "L3TEST/CARD0025",
                    "pmt_card_bin": "476173",
                    "name_on_card": "L3TEST/CARD0025",
                    "display_pan": "0250",

                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": cal_for_max_per + int(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "card_txn_type_2": "EMV",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "L3TEST/CARD0025",
                    "pmt_card_bin_2": "476173",
                    "name_on_card_2": "L3TEST/CARD0025",
                    "display_pan_2": "0250"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status value from original txn_id : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount value from original txn_id : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode value from original txn_id : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state value from original txn_id : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn value from original txn_id : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from original txn_id : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer_code value from original txn_id : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from original txn_id : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org_code value from original txn_id : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid value from original txn_id : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid value from original txn_id : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction_type value from original txn_id : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth_code value from original txn_id : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date_and_time value from original txn_id : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device_serial value from original txn_id : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username value from original txn_id : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction_id value from original txn_id : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from original txn_id : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from original txn_id : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn_type value from original txn_id : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch_number value from original txn_id : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from original txn_id : {card_last_four_digit_api}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer_name value from original txn_id : {customer_name_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from original txn_id : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant_name value from original txn_id : {merchant_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer_name value from original txn_id : {payer_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from original txn_id : {payment_card_bin_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from original txn_id : {name_on_card_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN value from original txn_id : {display_pan_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status value from refunded txn_id : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount value from refunded txn_id : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment_mode value from refunded txn_id : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state value from refunded txn_id : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn value from refunded txn_id : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from refunded txn_id : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from refunded txn_id : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org_code value from refunded txn_id : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid value from refunded txn_id : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid value from refunded txn_id : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction_type value from refunded txn_id : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth_code value from refunded txn_id : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date_and_time value from refunded txn_id : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username value from refunded txn_id : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction_id value from refunded txn_id : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from refunded txn_id : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from refunded txn_id : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card_txn_type value from refunded txn_id : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch_no value from refunded txn_id : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from refunded txn_id  : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer_name value from refunded txn_id : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from refunded txn_id : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant_name value from refunded txn_id : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer_name value from refunded txn_id : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from refunded txn_id : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from refunded txn_id : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN value from refunded txn_id : {display_pan_api_2}")

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

                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2
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
                    "txn_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "476173",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "payer_name": "L3TEST/CARD0025",

                    "txn_amt_2": float(cal_for_max_per + int(amount)),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "device_serial_2": device_serial,
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "order_id_2": order_id,
                    "issuer_code_2": None,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "476173",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "02",
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "payer_name_2": "L3TEST/CARD0025"
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
                    "issuer_code_2": issuer_code_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2
                }
                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date_2)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn_2),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(cal_for_max_per + int(amount)),
                    "AUTH CODE": auth_code_2,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": batch_number_db_2,
                    "CARD": "XXXX-XXXX-XXXX-0250 EMV",
                    "TID": tid
                }
                logger.info(f"expected_charge_slip_values : {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_291():
    """
        Sub Feature Code: UI_Common_Mpos_Refund_From_POS_Permit_Multiple_Partial_Refunds_Card_EMV_VISA_DEBIT_476173
        Sub Feature Description: Verify the user can initiate multiple partial refunds for a single transaction (bin:476173)
        TC naming code description:  100: Payment Method, 115: CARD_UI, 291: TC291
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
        logger.debug(f"Query to fetch data from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid value from terminal_info table : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid value from the terminal_info table :  {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial value from the terminal_info table : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id value from terminal_info table : {terminal_info_id}")

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
        api_details["RequestBody"]["settings"]["maxRefund"] = '0'
        logger.debug(f"API details : {api_details}")
        logger.debug(f"API details for org_settings_update : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received after enabling maximum refund settings : {response}")

        query = f"select bank_code from bin_info where bin='476173'"
        logger.debug(f"Query to fetch bank_code value from bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = 500
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount, order_id and device_serial is: {amount},{order_id},{device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_VISA_DEBIT_476173")
            card_page.select_cardtype(text="EMV_VISA_DEBIT_476173")
            logger.debug(f"selected the card type as : EMV_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received from settlement api for original amount : {settle_response}")
            settle_success = settle_response['success']
            logger.debug(f"Fetching success value after settlement for original amount  : {settle_success}")

            time.sleep(3)
            logger.debug(f"Waiting for 3 secs after orginal txn is completed")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result obatined for txn table for original txn amount : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table for original txn amount : {txn_id} ")
            rr_number = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rr_number value from txn table for original txn amount : {rr_number} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for original txn : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for original txn : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from value from txn table for original txn : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for original txn : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for original txn : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for original txn : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for original txn : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for original txn : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for original txn : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for original txn : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for original txn : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for original txn : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for original txn : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for original txn : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for original txn : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for original txn : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for original txn : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for original txn : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for original txn : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for original txn : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for original txn : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for original txn : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for original txn : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for original txn : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for original txn : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for original txn : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for original txn : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for original txn : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for original txn : {posting_date}")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
            logger.debug(f"Clicking on refund button on app side for original_txn_id")
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side for original_txn_id")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side for original_txn_id")
            manually_enter_amt_2 = 300
            logger.debug(f"Manually entering the first refund amount is : {manually_enter_amt_2}")
            logger.debug(f"Clicking on refund amount manually radio button for first refund")
            payment_page.click_on_refund_amt_manually()
            logger.debug(f"Click on refund amount manually radio button for first refund")
            logger.debug(f"Entering amount manually for first refund")
            payment_page.enter_refund_amt_manually(amount=manually_enter_amt_2)
            logger.debug(f"Entered amount manually for for first refund")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button for first refund")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm for first refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button after first refund")
            time.sleep(5)
            logger.debug(f"waiting for 5 secs")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicking on txn history back button after first refund")

            time.sleep(3)
            logger.debug(f"Waiting for 3 secs after first refund txn is completed")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table for first refund : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result obatined for txn table for first refund : {result}")
            txn_id_2 = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table for first refund : {txn_id_2} ")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for first refund txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for first refund txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from txn table for first refund txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for first refund txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for first refund txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for first refund txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for first refund txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for first refund txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for first refund txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for first refund txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for first refund txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for first refund txn : {settlement_status_db_2}")
            device_serial_db_2 = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for first refund txn : {device_serial_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for first refund txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for first refund txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for first refund txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for first refund txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for first refund txn : {order_id_db_2}")
            issuer_code_db_2 = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for first refund txn : {issuer_code_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for first refund txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for first refund txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for first refund txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for first refund txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for first refund txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for first refund txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for first refund txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for first refund txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for first refund txn : {merchant_name_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for first refund txn : {posting_date_2}")

            home_page.click_on_history()
            logger.debug(f"Clicked on txn history back button to filter the second refund amount")
            txn_history_page.re_login_to_app(username=app_username, password=app_password) #####This line is due to session expiry
            txn_history_page.click_on_transaction_by_amount(amount = amount)
            logger.debug(f"Filtered the second refund txn")
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side for second refund ")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side for second refund")
            manually_enter_amt_3 = 150
            logger.debug(f"Manually entering the second refund amount is : {manually_enter_amt_3}")
            logger.debug(f"Clicking on refund amount manually radio button for second refund")
            payment_page.click_on_refund_amt_manually()
            logger.debug(f"Click on refund amount manually radio button for second refund")
            logger.debug(f"Entering amount manually for second refund")
            payment_page.enter_refund_amt_manually(amount=manually_enter_amt_3)
            logger.debug(f"Entered amount manually for for second refund")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button for second refund")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm for second refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button after second refund")
            time.sleep(5)
            logger.debug(f"waiting for 5 secs for second refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicking on txn history back button after second refund")

            time.sleep(3)
            logger.debug(f"Waiting for 3 secs after second refund txn is completed")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table for second refund : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result obatined for txn table for second refund : {result}")
            txn_id_3 = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table for second refund : {txn_id_3} ")
            auth_code_3 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for second refund txn : {auth_code_3}")
            created_time_3 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for second refund txn : {created_time_3}")
            amount_db_3 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from txn table for second refund txn : {amount_db_3}")
            payment_mode_db_3 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for second refund txn : {payment_mode_db_3}")
            payment_status_db_3 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for second refund txn : {payment_status_db_3}")
            payment_state_db_3 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for second refund txn : {payment_state_db_3}")
            acquirer_code_db_3 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for second refund txn : {acquirer_code_db_3}")
            mid_db_3 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for second refund txn : {mid_db_3}")
            tid_db_3 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for second refund txn : {tid_db_3}")
            payment_gateway_db_3 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for second refund txn : {payment_gateway_db_3}")
            rrn_3 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for second refund txn : {rrn_3}")
            settlement_status_db_3 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for second refund txn : {settlement_status_db_3}")
            device_serial_db_3 = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for second refund txn : {device_serial_db_3}")
            merchant_code_db_3 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for second refund txn : {merchant_code_db_3}")
            payment_card_brand_db_3 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for second refund txn : {payment_card_brand_db_3}")
            payment_card_type_db_3 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for second refund txn : {payment_card_type_db_3}")
            batch_number_db_3 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for second refund txn : {batch_number_db_3}")
            order_id_db_3 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for second refund txn : {order_id_db_3}")
            issuer_code_db_3 = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for second refund txn : {issuer_code_db_3}")
            org_code_db_3 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for second refund txn : {org_code_db_3}")
            payment_card_bin_db_3 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for second refund txn : {payment_card_bin_db_3}")
            terminal_info_id_db_3 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for second refund txn : {terminal_info_id_db_3}")
            txn_type_db_3 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for second refund txn : {txn_type_db_3}")
            card_txn_type_db_3 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for second refund txn : {card_txn_type_db_3}")
            card_last_four_digit_db_3 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for second refund txn : {card_last_four_digit_db_3}")
            customer_name_db_3 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for second refund txn : {customer_name_db_3}")
            payer_name_db_3 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for second refund txn : {payer_name_db_3}")
            merchant_name_3 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for second refund txn : {merchant_name_3}")
            posting_date_3 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for second refund txn : {posting_date_3}")

            home_page.click_on_history()
            logger.debug(f"Clicked on txn history back button to filter the third refund amount")
            txn_history_page.re_login_to_app(username=app_username, password=app_password) #####This line is due to session expiry
            txn_history_page.click_on_transaction_by_rrn(rrn = rr_number)
            logger.debug(f"Filtered the third refund txn")
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side for third refund ")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side for third refund")
            manually_enter_amt_4 = 50
            logger.debug(f"Manually entering the second refund amount is : {manually_enter_amt_4}")
            logger.debug(f"Clicking on refund amount manually radio button for third refund")
            payment_page.click_on_refund_amt_manually()
            logger.debug(f"Click on refund amount manually radio button for third refund")
            logger.debug(f"Entering amount manually for third refund")
            payment_page.enter_refund_amt_manually(amount=manually_enter_amt_4)
            logger.debug(f"Entered amount manually for for third refund")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button for third refund")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm for third refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button after third refund")
            time.sleep(5)
            logger.debug(f"waiting for 5 secs for third refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicking on txn history back button after third refund")

            time.sleep(3)
            logger.debug(f"Waiting for 3 secs after third refund txn is completed")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table for third refund : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result obatined for txn table for third refund : {result}")
            txn_id_4 = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table for third refund : {txn_id_4} ")
            auth_code_4  = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for third refund txn : {auth_code_4}")
            created_time_4 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for third refund txn : {created_time_4}")
            amount_db_4 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from txn table for third refund txn : {amount_db_4}")
            payment_mode_db_4 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for third refund txn : {payment_mode_db_4}")
            payment_status_db_4 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for third refund txn : {payment_status_db_4}")
            payment_state_db_4 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for third refund txn : {payment_state_db_4}")
            acquirer_code_db_4 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for third refund txn : {acquirer_code_db_4}")
            mid_db_4 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for third refund txn : {mid_db_4}")
            tid_db_4 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for third refund txn : {tid_db_4}")
            payment_gateway_db_4 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for third refund txn : {payment_gateway_db_4}")
            rrn_4 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for third refund txn : {rrn_4}")
            settlement_status_db_4 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for third refund txn : {settlement_status_db_4}")
            device_serial_db_4 = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for third refund txn : {device_serial_db_4}")
            merchant_code_db_4 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for third refund txn : {merchant_code_db_4}")
            payment_card_brand_db_4 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for third refund txn : {payment_card_brand_db_4}")
            payment_card_type_db_4 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for third refund txn : {payment_card_type_db_4}")
            batch_number_db_4 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for third refund txn : {batch_number_db_4}")
            order_id_db_4 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for third refund txn : {order_id_db_4}")
            issuer_code_db_4 = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for third refund txn : {issuer_code_db_4}")
            org_code_db_4 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for third refund txn : {org_code_db_4}")
            payment_card_bin_db_4 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for third refund txn : {payment_card_bin_db_4}")
            terminal_info_id_db_4 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for third refund txn : {terminal_info_id_db_4}")
            txn_type_db_4 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for third refund txn : {txn_type_db_4}")
            card_txn_type_db_4 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for third refund txn : {card_txn_type_db_4}")
            card_last_four_digit_db_4 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for third refund txn : {card_last_four_digit_db_4}")
            customer_name_db_4 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for third refund txn : {customer_name_db_4}")
            payer_name_db_4 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for third refund txn : {payer_name_db_4}")
            merchant_name_4 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for third refund txn : {merchant_name_4}")
            posting_date_4 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for third refund txn : {posting_date_4}")

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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=posting_date)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=posting_date_2)
                date_and_time_app_3 = date_time_converter.to_app_format(posting_date_db=posting_date_3)
                date_and_time_app_4 = date_time_converter.to_app_format(posting_date_db=posting_date_4)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "REFUND SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "L3TEST",
                    "card_type_desc": "*0250 EMV",

                    "txn_amt_2": "{:,.2f}".format(manually_enter_amt_2),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id_db_2,
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial_db_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "L3TEST",
                    "card_type_desc_2": "*0250 EMV",

                    "txn_amt_3": "{:,.2f}".format(manually_enter_amt_3),
                    "pmt_mode_3": "CARD",
                    "txn_id_3": txn_id_3,
                    "pmt_status_3": "REFUNDED",
                    "rrn_3": str(rrn_3),
                    "order_id_3": order_id_db_3,
                    "pmt_msg_3": "REFUND SUCCESSFUL",
                    "settle_status_3": "PENDING",
                    "auth_code_3": auth_code_3,
                    "date_3": date_and_time_app_3,
                    "device_serial_3": device_serial_db_3,
                    "mid_3": mid,
                    "tid_3": tid,
                    "batch_number_3": batch_number_db_3,
                    "customer_name_3": "L3TEST",
                    "card_type_desc_3": "*0250 EMV",

                    "txn_amt_4": "{:,.2f}".format(manually_enter_amt_4),
                    "pmt_mode_4": "CARD",
                    "txn_id_4": txn_id_4,
                    "pmt_status_4": "REFUNDED",
                    "rrn_4": str(rrn_4),
                    "order_id_4": order_id_db_4,
                    "pmt_msg_4": "REFUND SUCCESSFUL",
                    "settle_status_4": "PENDING",
                    "auth_code_4": auth_code_4,
                    "date_4": date_and_time_app_4,
                    "device_serial_4": device_serial_db_4,
                    "mid_4": mid,
                    "tid_4": tid,
                    "batch_number_4": batch_number_db_4,
                    "customer_name_4": "L3TEST",
                    "card_type_desc_4": "*0250 EMV"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login(username=app_username, password=app_password)
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for original_txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for original_txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for original_txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for original_txn : {txn_id}, {payment_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for original_txn : {txn_id}, {app_customer_name}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for original_txn : {txn_id}, {app_date_and_time}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for original_txn : {txn_id}, {app_card_type_desc}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for original_txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for original_txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for original_txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for original_txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for original_txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for original_txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for original_txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for original_txn: {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for original_txn : {txn_id}, {app_batch_number}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for first refund txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for first refund txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for first refund txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for first refund txn : {txn_id_2}, {payment_status_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for first refund txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for first refund txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for first refund txn : {txn_id_2}, {app_settlement_status_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc from txn history for first refund txn : {txn_id_2}, {app_card_type_desc_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for first refund txn : {txn_id_2}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for first refund txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for first refund txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for first refund txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for first refund txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for first refund txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for first refund txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for first refund txn : {txn_id_2}, {app_customer_name_2}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id_3)
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for second refund txn : {txn_id_3}, {app_amount_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for second refund txn : {txn_id_3}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for second refund txn: {txn_id_3}, {app_txn_id_3}")
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for second refund txn : {txn_id_3}, {payment_status_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for second refund txn  : {txn_id_3}, {app_order_id_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for second refund txn  : {txn_id_3}, {app_payment_msg_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for second refund txn : {txn_id_3}, {app_settlement_status_3}")
                app_card_type_desc_3 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc from txn history from txn history : {txn_id_3}, {app_card_type_desc_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for second refund txn : {txn_id_3}, {app_rrn_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for second refund txn : {txn_id_3}, {app_auth_code_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for second refund txn : {txn_id_3}, {app_date_and_time_3}")
                app_device_serial_3 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for second refund txn : {txn_id_3}, {app_device_serial_3}")
                app_mid_3 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for second refund txn : {txn_id_3}, {app_mid_3}")
                app_tid_3 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for second refund txn : {txn_id_3}, {app_tid_3}")
                app_batch_number_3 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for second refund txn : {txn_id_3}, {app_batch_number_3}")
                app_customer_name_3 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for second refund txn : {txn_id_3}, {app_customer_name_3}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id_4)
                app_amount_4 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for third refund txn : {txn_id_4}, {app_amount_4}")
                payment_mode_4 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for third refund txn : {txn_id_4}, {payment_mode_4}")
                app_txn_id_4 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for third refund txn: {txn_id_4}, {app_txn_id_4}")
                payment_status_4 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for third refund txn : {txn_id_4}, {payment_status_4}")
                app_order_id_4 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for third refund txn  : {txn_id_4}, {app_order_id_4}")
                app_payment_msg_4 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for third refund txn  : {txn_id_4}, {app_payment_msg_4}")
                app_settlement_status_4 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for third refund txn : {txn_id_4}, {app_settlement_status_4}")
                app_card_type_desc_4 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc from txn history from third refund txn : {txn_id_4}, {app_card_type_desc_4}")
                app_rrn_4 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for third refund txn : {txn_id_4}, {app_rrn_4}")
                app_auth_code_4 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for third refund txn : {txn_id_4}, {app_auth_code_4}")
                app_date_and_time_4 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for third refund txn : {txn_id_4}, {app_date_and_time_4}")
                app_device_serial_4 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for third refund txn : {txn_id_4}, {app_device_serial_4}")
                app_mid_4 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for third refund txn : {txn_id_4}, {app_mid_4}")
                app_tid_4 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for third refund txn : {txn_id_4}, {app_tid_4}")
                app_batch_number_4 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for third refund txn : {txn_id_4}, {app_batch_number_4}")
                app_customer_name_4 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for third refund txn : {txn_id_4}, {app_customer_name_4}")

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

                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
                    "card_type_desc_2": app_card_type_desc_2,

                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "pmt_mode_3": payment_mode_3,
                    "txn_id_3": app_txn_id_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "rrn_3": app_rrn_3,
                    "order_id_3": app_order_id_3,
                    "pmt_msg_3": app_payment_msg_3,
                    "settle_status_3": app_settlement_status_3,
                    "auth_code_3": app_auth_code_3,
                    "date_3": app_date_and_time_3,
                    "device_serial_3": app_device_serial_3,
                    "mid_3": app_mid_3,
                    "tid_3": app_tid_3,
                    "batch_number_3": app_batch_number_3,
                    "customer_name_3": app_customer_name_3,
                    "card_type_desc_3": app_card_type_desc_3,

                    "txn_amt_4": app_amount_4.split(' ')[1],
                    "pmt_mode_4": payment_mode_4,
                    "txn_id_4": app_txn_id_4,
                    "pmt_status_4": payment_status_4.split(':')[1],
                    "rrn_4": app_rrn_4,
                    "order_id_4": app_order_id_4,
                    "pmt_msg_4": app_payment_msg_4,
                    "settle_status_4": app_settlement_status_4,
                    "auth_code_4": app_auth_code_4,
                    "date_4": app_date_and_time_4,
                    "device_serial_4": app_device_serial_4,
                    "mid_4": app_mid_4,
                    "tid_4": app_tid_4,
                    "batch_number_4": app_batch_number_4,
                    "customer_name_4": app_customer_name_4,
                    "card_type_desc_4": app_card_type_desc_4
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                date_and_time_api_3 = date_time_converter.db_datetime(date_from_db=created_time_3)
                date_and_time_api_4 = date_time_converter.db_datetime(date_from_db=created_time_4)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "original_amt": float(amount),
                    "total_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "card_txn_type": "EMV",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "L3TEST/CARD0025",
                    "pmt_card_bin": "476173",
                    "name_on_card": "L3TEST/CARD0025",
                    "display_pan": "0250",

                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(manually_enter_amt_2),
                    "original_amt_2": float(manually_enter_amt_2),
                    "total_amt_2": float(manually_enter_amt_2),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "card_txn_type_2": "EMV",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "L3TEST/CARD0025",
                    "pmt_card_bin_2": "476173",
                    "name_on_card_2": "L3TEST/CARD0025",
                    "display_pan_2": "0250",

                    "pmt_status_3": "REFUNDED",
                    "txn_amt_3": float(manually_enter_amt_3),
                    "pmt_mode_3": "CARD",
                    "pmt_state_3": "AUTHORIZED",
                    "rrn_3": str(rrn_3),
                    "settle_status_3": "PENDING",
                    "acquirer_code_3": "HDFC",
                    "txn_type_3": "REFUND",
                    "auth_code_3": auth_code_3,
                    "mid_3": mid,
                    "tid_3": tid,
                    "org_code_3": org_code,
                    "date_3": date_and_time_api_3,
                    "username_3": app_username,
                    "txn_id_3": txn_id_3,
                    "pmt_card_brand_3": "VISA",
                    "pmt_card_type_3": "DEBIT",
                    "card_txn_type_3": "EMV",
                    "batch_number_3": batch_number_db_3,
                    "card_last_four_digit_3": "0250",
                    "customer_name_3": "L3TEST/CARD0025",
                    "external_ref_3": order_id,
                    "merchant_name_3": merchant_name_3,
                    "payer_name_3": "L3TEST/CARD0025",
                    "pmt_card_bin_3": "476173",
                    "name_on_card_3": "L3TEST/CARD0025",
                    "display_pan_3": "0250",

                    "pmt_status_4": "REFUNDED",
                    "txn_amt_4": float(manually_enter_amt_4),
                    "pmt_mode_4": "CARD",
                    "pmt_state_4": "AUTHORIZED",
                    "rrn_4": str(rrn_4),
                    "settle_status_4": "PENDING",
                    "acquirer_code_4": "HDFC",
                    "txn_type_4": "REFUND",
                    "auth_code_4": auth_code_4,
                    "mid_4": mid,
                    "tid_4": tid,
                    "org_code_4": org_code,
                    "date_4": date_and_time_api_4,
                    "username_4": app_username,
                    "txn_id_4": txn_id_4,
                    "pmt_card_brand_4": "VISA",
                    "pmt_card_type_4": "DEBIT",
                    "card_txn_type_4": "EMV",
                    "batch_number_4": batch_number_db_4,
                    "card_last_four_digit_4": "0250",
                    "customer_name_4": "L3TEST/CARD0025",
                    "external_ref_4": order_id,
                    "merchant_name_4": merchant_name_4,
                    "payer_name_4": "L3TEST/CARD0025",
                    "pmt_card_bin_4": "476173",
                    "name_on_card_4": "L3TEST/CARD0025",
                    "display_pan_4": "0250"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status value from original txn_id : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount value from original txn_id : {amount_api}")
                original_amount_api = float(response_1["amount"])
                logger.debug(f"Fetching original_amt value from original txn_id : {original_amount_api}")
                total_amt_api = float(response_1["totalAmount"])
                logger.debug(f"Fetching total_amt value from original txn_id : {total_amt_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode value from original txn_id : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state value from original txn_id : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn value from original txn_id : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from original txn_id : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer_code value from original txn_id : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from original txn_id : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org_code value from original txn_id : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid value from original txn_id : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid value from original txn_id : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction_type value from original txn_id : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth_code value from original txn_id : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date_and_time value from original txn_id : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device_serial value from original txn_id : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username value from original txn_id : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction_id value from original txn_id : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from original txn_id : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from original txn_id : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn_type value from original txn_id : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch_number value from original txn_id : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from original txn_id : {card_last_four_digit_api}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer_name value from original txn_id : {customer_name_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from original txn_id : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant_name value from original txn_id : {merchant_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer_name value from original txn_id : {payer_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from original txn_id : {payment_card_bin_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from original txn_id : {name_on_card_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN value from original txn_id : {display_pan_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data for second refund txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status value from second refund txn_id : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount value from second refund txn_id : {amount_api_2}")
                original_amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching original_amt value from second refund txn_id : {original_amount_api_2}")
                total_amt_api_2 = float(response_2["totalAmount"])
                logger.debug(f"Fetching total_amt value from second refund txn_id : {total_amt_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment_mode value from second refund txn_id : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state value from second refund txn_id : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn value from second refund txn_id : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from second refund txn_id : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from second refund txn_id : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org_code value from second refund txn_id : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid value from second refund txn_id : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid value from second refund txn_id : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction_type value from second refund txn_id : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth_code value from second refund txn_id : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date_and_time value from second refund txn_id : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username value from second refund txn_id : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction_id value from second refund txn_id : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from second refund txn_id : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from second refund txn_id : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card_txn_type value from second refund txn_id : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch_no value from second refund txn_id : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from second refund txn_id  : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer_name value from second refund txn_id : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from second refund txn_id : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant_name value from second refund txn_id : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer_name value from second refund txn_id : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from second refund txn_id : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from second refund txn_id : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN value from second refund txn_id : {display_pan_api_2}")

                response_3 = [x for x in response["txns"] if x["txnId"] == txn_id_3][0]
                logger.debug(f"Response after filtering data for third refund txn is : {response_3}")
                status_api_3 = response_3["status"]
                logger.debug(f"Fetching status value from third refund txn_id : {status_api_3}")
                amount_api_3 = float(response_3["amount"])
                logger.debug(f"Fetching amount value from third refund txn_id : {amount_api_3}")
                original_amount_api_3 = float(response_3["amount"])
                logger.debug(f"Fetching original_amt value from third refund txn_id : {original_amount_api_3}")
                total_amt_api_3 = float(response_3["totalAmount"])
                logger.debug(f"Fetching total_amt value from third refund txn_id : {total_amt_api_3}")
                payment_mode_api_3 = response_3["paymentMode"]
                logger.debug(f"Fetching payment_mode value from third refund txn_id : {payment_mode_api_3}")
                state_api_3 = response_3["states"][0]
                logger.debug(f"Fetching state value from third refund txn_id : {state_api_3}")
                rrn_api_3 = response_3["rrNumber"]
                logger.debug(f"Fetching rrn value from third refund txn_id : {rrn_api_3}")
                settlement_status_api_3 = response_3["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from third refund txn_id : {settlement_status_api_3}")
                acquirer_code_api_3 = response_3["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from third refund txn_id : {acquirer_code_api_3}")
                org_code_api_3 = response_3["orgCode"]
                logger.debug(f"Fetching org_code value from third refund txn_id : {org_code_api_3}")
                mid_api_3 = response_3["mid"]
                logger.debug(f"Fetching mid value from third refund txn_id : {mid_api_3}")
                tid_api_3 = response_3["tid"]
                logger.debug(f"Fetching tid value from third refund txn_id : {tid_api_3}")
                txn_type_api_3 = response_3["txnType"]
                logger.debug(f"Fetching transaction_type value from third refund txn_id : {txn_type_api_3}")
                auth_code_api_3 = response_3["authCode"]
                logger.debug(f"Fetching auth_code value from third refund txn_id : {auth_code_api_3}")
                date_and_time_api_3 = response_3["createdTime"]
                logger.debug(f"Fetching date_and_time value from third refund txn_id : {date_and_time_api_3}")
                username_api_3 = response_3["username"]
                logger.debug(f"Fetching username value from third refund txn_id : {username_api_3}")
                txn_id_api_3 = response_3["txnId"]
                logger.debug(f"Fetching transaction_id value from third refund txn_id : {txn_id_api_3}")
                payment_card_brand_api_3 = response_3["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from third refund txn_id : {payment_card_brand_api_3}")
                payment_card_type_api_3 = response_3["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from third refund txn_id : {payment_card_type_api_3}")
                card_txn_type_api_3 = response_3["cardTxnTypeDesc"]
                logger.debug(f"Fetching card_txn_type value from third refund txn_id : {card_txn_type_api_3}")
                batch_number_api_3 = response_3["batchNumber"]
                logger.debug(f"Fetching batch_no value from third refund txn_id : {batch_number_api_3}")
                card_last_four_digit_api_3 = response_3["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from third refund txn_id  : {card_last_four_digit_api_3}")
                customer_name_api_3 = response_3["customerName"]
                logger.debug(f"Fetching customer_name value from third refund txn_id : {customer_name_api_3}")
                external_ref_number_api_3 = response_3["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from third refund txn_id : {external_ref_number_api_3}")
                merchant_name_api_3 = response_3["merchantName"]
                logger.debug(f"Fetching merchant_name value from third refund txn_id : {merchant_name_api_3}")
                payer_name_api_3 = response_3["payerName"]
                logger.debug(f"Fetching payer_name value from third refund txn_id : {payer_name_api_3}")
                payment_card_bin_api_3 = response_3["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from third refund txn_id : {payment_card_bin_api_3}")
                name_on_card_api_3 = response_3["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from third refund txn_id : {name_on_card_api_3}")
                display_pan_api_3 = response_3["displayPAN"]
                logger.debug(f"Fetching display_PAN value from third refund txn_id : {display_pan_api_3}")

                response_4 = [x for x in response["txns"] if x["txnId"] == txn_id_4][0]
                logger.debug(f"Response after filtering data for third refund txn is : {response_4}")
                status_api_4 = response_4["status"]
                logger.debug(f"Fetching status value from third refund txn_id : {status_api_4}")
                amount_api_4 = float(response_4["amount"])
                logger.debug(f"Fetching amount value from third refund txn_id : {amount_api_4}")
                original_amount_api_4 = float(response_4["amount"])
                logger.debug(f"Fetching original_amt value from third refund txn_id : {original_amount_api_4}")
                total_amt_api_4 = float(response_4["totalAmount"])
                logger.debug(f"Fetching total_amt value from third refund txn_id : {total_amt_api_4}")
                payment_mode_api_4 = response_4["paymentMode"]
                logger.debug(f"Fetching payment_mode value from third refund txn_id : {payment_mode_api_4}")
                state_api_4 = response_4["states"][0]
                logger.debug(f"Fetching state value from third refund txn_id : {state_api_4}")
                rrn_api_4 = response_4["rrNumber"]
                logger.debug(f"Fetching rrn value from third refund txn_id : {rrn_api_4}")
                settlement_status_api_4 = response_4["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from third refund txn_id : {settlement_status_api_4}")
                acquirer_code_api_4 = response_4["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from third refund txn_id : {acquirer_code_api_4}")
                org_code_api_4 = response_4["orgCode"]
                logger.debug(f"Fetching org_code value from third refund txn_id : {org_code_api_4}")
                mid_api_4 = response_4["mid"]
                logger.debug(f"Fetching mid value from third refund txn_id : {mid_api_4}")
                tid_api_4 = response_4["tid"]
                logger.debug(f"Fetching tid value from third refund txn_id : {tid_api_4}")
                txn_type_api_4 = response_4["txnType"]
                logger.debug(f"Fetching transaction_type value from third refund txn_id : {txn_type_api_4}")
                auth_code_api_4 = response_4["authCode"]
                logger.debug(f"Fetching auth_code value from third refund txn_id : {auth_code_api_4}")
                date_and_time_api_4 = response_4["createdTime"]
                logger.debug(f"Fetching date_and_time value from third refund txn_id : {date_and_time_api_4}")
                username_api_4 = response_4["username"]
                logger.debug(f"Fetching username value from third refund txn_id : {username_api_4}")
                txn_id_api_4 = response_4["txnId"]
                logger.debug(f"Fetching transaction_id value from third refund txn_id : {txn_id_api_4}")
                payment_card_brand_api_4 = response_4["paymentCardBrand"]
                logger.debug(f"Fetching payment_card_brand value from third refund txn_id : {payment_card_brand_api_4}")
                payment_card_type_api_4 = response_4["paymentCardType"]
                logger.debug(f"Fetching payment_card_type value from third refund txn_id : {payment_card_type_api_4}")
                card_txn_type_api_4 = response_4["cardTxnTypeDesc"]
                logger.debug(f"Fetching card_txn_type value from third refund txn_id : {card_txn_type_api_4}")
                batch_number_api_4 = response_4["batchNumber"]
                logger.debug(f"Fetching batch_no value from third refund txn_id : {batch_number_api_4}")
                card_last_four_digit_api_4 = response_4["cardLastFourDigit"]
                logger.debug(f"Fetching card_last_four_digit value from third refund txn_id  : {card_last_four_digit_api_4}")
                customer_name_api_4 = response_4["customerName"]
                logger.debug(f"Fetching customer_name value from third refund txn_id : {customer_name_api_4}")
                external_ref_number_api_4 = response_4["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from third refund txn_id : {external_ref_number_api_4}")
                merchant_name_api_4 = response_4["merchantName"]
                logger.debug(f"Fetching merchant_name value from third refund txn_id : {merchant_name_api_4}")
                payer_name_api_4 = response_4["payerName"]
                logger.debug(f"Fetching payer_name value from third refund txn_id : {payer_name_api_4}")
                payment_card_bin_api_4 = response_4["paymentCardBin"]
                logger.debug(f"Fetching payment_card_bin value from third refund txn_id : {payment_card_bin_api_4}")
                name_on_card_api_4 = response_4["nameOnCard"]
                logger.debug(f"Fetching name_on_card value from third refund txn_id : {name_on_card_api_4}")
                display_pan_api_4 = response_4["displayPAN"]
                logger.debug(f"Fetching display_PAN value from third refund txn_id : {display_pan_api_4}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "original_amt": original_amount_api,
                    "total_amt": total_amt_api,
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

                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "original_amt_2": original_amount_api_2,
                    "total_amt_2": total_amt_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2,

                    "pmt_status_3": status_api_3,
                    "txn_amt_3": amount_api_3,
                    "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_3,
                    "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "txn_type_3": txn_type_api_3,
                    "auth_code_3": auth_code_api_3,
                    "mid_3": mid_api_3,
                    "tid_3": tid_api_3,
                    "org_code_3": org_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_and_time_api_3),
                    "username_3": username_api_3,
                    "txn_id_3": txn_id_api_3,
                    "pmt_card_brand_3": payment_card_brand_api_3,
                    "pmt_card_type_3": payment_card_type_api_3,
                    "card_txn_type_3": card_txn_type_api_3,
                    "batch_number_3": batch_number_api_3,
                    "card_last_four_digit_3": card_last_four_digit_api_3,
                    "customer_name_3": customer_name_api_3,
                    "external_ref_3": external_ref_number_api_3,
                    "merchant_name_3": merchant_name_api_3,
                    "payer_name_3": payer_name_api_3,
                    "pmt_card_bin_3": payment_card_bin_api_3,
                    "name_on_card_3": name_on_card_api_3,
                    "display_pan_3": display_pan_api_3,

                    "pmt_status_4": status_api_4,
                    "txn_amt_4": amount_api_4,
                    "pmt_mode_4": payment_mode_api_4,
                    "pmt_state_4": state_api_4,
                    "rrn_4": str(rrn_api_4),
                    "settle_status_4": settlement_status_api_4,
                    "acquirer_code_4": acquirer_code_api_4,
                    "txn_type_4": txn_type_api_4,
                    "auth_code_4": auth_code_api_4,
                    "mid_4": mid_api_4,
                    "tid_4": tid_api_4,
                    "org_code_4": org_code_api_4,
                    "date_4": date_time_converter.from_api_to_datetime_format(date_and_time_api_4),
                    "username_4": username_api_4,
                    "txn_id_4": txn_id_api_4,
                    "pmt_card_brand_4": payment_card_brand_api_4,
                    "pmt_card_type_4": payment_card_type_api_4,
                    "card_txn_type_4": card_txn_type_api_4,
                    "batch_number_4": batch_number_api_4,
                    "card_last_four_digit_4": card_last_four_digit_api_4,
                    "customer_name_4": customer_name_api_4,
                    "external_ref_4": external_ref_number_api_4,
                    "merchant_name_4": merchant_name_api_4,
                    "payer_name_4": payer_name_api_4,
                    "pmt_card_bin_4": payment_card_bin_api_4,
                    "name_on_card_4": name_on_card_api_4,
                    "display_pan_4": display_pan_api_4
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
                    "txn_amt": amount,
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
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "476173",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "payer_name": "L3TEST/CARD0025",

                    "txn_amt_2": manually_enter_amt_2,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "device_serial_2": device_serial,
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "order_id_2": order_id,
                    "issuer_code_2": None,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "476173",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "02",
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "payer_name_2": "L3TEST/CARD0025",

                    "txn_amt_3": manually_enter_amt_3,
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
                    "pmt_card_type_3": "DEBIT",
                    "order_id_3": order_id,
                    "issuer_code_3": None,
                    "org_code_3": org_code,
                    "pmt_card_bin_3": "476173",
                    "terminal_info_id_3": terminal_info_id,
                    "txn_type_3": "REFUND",
                    "card_txn_type_3": "02",
                    "card_last_four_digit_3": "0250",
                    "customer_name_3": "L3TEST/CARD0025",
                    "payer_name_3": "L3TEST/CARD0025",

                    "txn_amt_4": manually_enter_amt_4,
                    "pmt_mode_4": "CARD",
                    "pmt_status_4": "REFUNDED",
                    "pmt_state_4": "AUTHORIZED",
                    "acquirer_code_4": "HDFC",
                    "mid_4": mid,
                    "tid_4": tid,
                    "pmt_gateway_4": "DUMMY",
                    "settle_status_4": "PENDING",
                    "device_serial_4": device_serial,
                    "merchant_code_4": org_code,
                    "pmt_card_brand_4": "VISA",
                    "pmt_card_type_4": "DEBIT",
                    "order_id_4": order_id,
                    "issuer_code_4": None,
                    "org_code_4": org_code,
                    "pmt_card_bin_4": "476173",
                    "terminal_info_id_4": terminal_info_id,
                    "txn_type_4": "REFUND",
                    "card_txn_type_4": "02",
                    "card_last_four_digit_4": "0250",
                    "customer_name_4": "L3TEST/CARD0025",
                    "payer_name_4": "L3TEST/CARD0025"
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
                    "issuer_code_2": issuer_code_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2,

                    "txn_amt_3": amount_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "pmt_status_3": payment_status_db_3,
                    "pmt_state_3": payment_state_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "pmt_gateway_3": payment_gateway_db_3,
                    "settle_status_3": settlement_status_db_3,
                    "device_serial_3": device_serial_db_3,
                    "merchant_code_3": merchant_code_db_3,
                    "pmt_card_brand_3": payment_card_brand_db_3,
                    "pmt_card_type_3": payment_card_type_db_3,
                    "order_id_3": order_id_db_3,
                    "issuer_code_3": issuer_code_db_3,
                    "org_code_3": org_code_db_3,
                    "pmt_card_bin_3": payment_card_bin_db_3,
                    "terminal_info_id_3": terminal_info_id_db_3,
                    "txn_type_3": txn_type_db_3,
                    "card_txn_type_3": card_txn_type_db_3,
                    "card_last_four_digit_3": card_last_four_digit_db_3,
                    "customer_name_3": customer_name_db_3,
                    "payer_name_3": payer_name_db_3,

                    "txn_amt_4": amount_db_4,
                    "pmt_mode_4": payment_mode_db_4,
                    "pmt_status_4": payment_status_db_4,
                    "pmt_state_4": payment_state_db_4,
                    "acquirer_code_4": acquirer_code_db_4,
                    "mid_4": mid_db_4,
                    "tid_4": tid_db_4,
                    "pmt_gateway_4": payment_gateway_db_4,
                    "settle_status_4": settlement_status_db_4,
                    "device_serial_4": device_serial_db_4,
                    "merchant_code_4": merchant_code_db_4,
                    "pmt_card_brand_4": payment_card_brand_db_4,
                    "pmt_card_type_4": payment_card_type_db_4,
                    "order_id_4": order_id_db_4,
                    "issuer_code_4": issuer_code_db_4,
                    "org_code_4": org_code_db_4,
                    "pmt_card_bin_4": payment_card_bin_db_4,
                    "terminal_info_id_4": terminal_info_id_db_4,
                    "txn_type_4": txn_type_db_4,
                    "card_txn_type_4": card_txn_type_db_4,
                    "card_last_four_digit_4": card_last_four_digit_db_4,
                    "customer_name_4": customer_name_db_4,
                    "payer_name_4": payer_name_db_4
                }
                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)