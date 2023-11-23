import random
import sys
import pytest
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.sa.app_card_page import CardPage
from PageFactory.sa.app_payment_page import PaymentPage
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
@pytest.mark.chargeSlipVal # Chargeslip validation is getting failed
def test_common_100_115_02_009():
    """
        Sub Feature Code: UI_Common_Card_Cash@pos_Success_Txn_Without_Sale_Via_HDFC_Dummy_EMVCTLS_VISA_CreditCard_Without_Pin_417666
        Sub Feature Description: Performing the EMVCTLS cash@pos success transaction without sale via HDFC Dummy PG using VISA Credit card without pin (bin : 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 02:Cash@Posh , 009: TC009
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

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["cashBackOption"] = "1"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions when cash back option is enabled: {response}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code value from the bin_info table : {issuer_code}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
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
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            random_number = random.randint(1, 9)  # For cash@pos without sale, the amount should be multiples of 100's.
            logger.debug(f"Randomly generated random_number is : {random_number} ")
            cash_amount = random_number * 100
            sale_amount = 0
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.click_cash_at_pos()
            logger.debug(f"Clicked on cash@pos button")
            home_page.enter_cash_at_pos_amount(cash_amount)
            logger.debug(f"Entered cash amount and sale amount for without sale : {cash_amount}, {sale_amount}")
            home_page.click_pay_now_button()
            logger.debug(f"Clicked on pay now button")
            home_page.enter_order_number_and_device_serial(order_id, device_serial)
            logger.debug(f"Entered order_id and device_serial : {order_id} , {device_serial} ")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype("CTLS_VISA_CREDIT_417666")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and payment_mode='CARD' and device_serial='{device_serial}' and external_ref='{order_id}' order by created_time desc limit 1 ;"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table : {txn_created_time}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id value from the txn table : {txn_id}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table : {batch_number}")
            amount_db = result['amount'].values[0]
            logger.debug(f"Fetching amount value from the txn table : {amount_db}")
            amt_cash_back_db = result['amount_cash_back'].values[0]
            logger.debug(f"Fetching amount_cash_back value from the txn table : {amt_cash_back_db}")
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
            sale_amt_db = result['amount_original'].values[0]
            logger.debug(f"Fetching amount_original value from the txn table : {sale_amt_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table : {payment_card_type_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer_code value from the txn table : {issuer_code_db}")
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
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer_name value from the txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer_name value from the txn table : {payer_name_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table : {org_code_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table : {order_id_db}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from the txn table : {posting_date}")

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
                date_and_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(cash_amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
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
                    "cash_amt": "{:,.2f}".format(cash_amount),
                    "sale_amt": "{:,.2f}".format(sale_amount)
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment status value from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode value from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id value from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching amount value from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status value from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching payment msg value from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time value from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn value from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_cde value from txn history for the txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id value from txn history for the txn : {txn_id}, {app_order_id}")
                app_batch_no = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch number value from txn history for the txn : {txn_id}, {app_batch_no}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid value from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid value from txn history for the txn : {txn_id}, {app_tid}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card type value from txn history for the txn : {txn_id}, {app_card_type_desc}")
                app_cash_amt = txn_history_page.fetch_cash_amt_text()
                logger.info(f"Fetching card amount value from txn history for the txn : {txn_id}, {app_cash_amt}")
                app_sale_amt = txn_history_page.fetch_sale_amt_text()
                logger.info(f"Fetching sale amount value from txn history for the txn : {txn_id}, {app_sale_amt}")

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
                    "cash_amt": app_cash_amt.split(' ')[1],
                    "sale_amt": app_sale_amt.split(' ')[1]
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(cash_amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CASH_OUT",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": expected_date_and_time_api,
                    "cash_amt": float(cash_amount),
                    "sale_amt": float(sale_amount),
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "CTLS",
                    "batch_number": batch_number,
                    "card_last_four_digit": "0018",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "display_pan": "0018"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Value of status obtained from txnlist api for cash@pos txn : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Value of amount obtained from txnlist api for cash@pos txn : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api for cash@pos txn : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Value of states obtained from txnlist api for cash@pos txn : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api for cash@pos txn : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api for cash@pos txn : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api for cash@pos txn : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api for cash@pos txn : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api for cash@pos txn : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Value of mid obtained from txnlist api for cash@pos txn : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Value of tid obtained from txnlist api for cash@pos txn : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api for cash@pos txn : {txn_type_api}")
                auth_code_api = response["authCode"]
                logger.debug(f"Value of authCode obtained from txnlist api for cash@pos txn : {auth_code_api}")
                date_and_time_api = response["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api for cash@pos txn : {date_and_time_api}")
                sale_amt_api = response["amountOriginal"]
                logger.debug(f"Value of amountOriginal obtained from txnlist api for cash@pos txn : {sale_amt_api}")
                cash_amt_api = response["amountCashBack"]
                logger.debug(f"Value of amountCashBack obtained from txnlist api for cash@pos txn : {cash_amt_api}")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"Value of deviceSerial obtained from txnlist api for cash@pos txn : {device_serial_api}")
                username_api = response["username"]
                logger.debug(f"Value of username obtained from txnlist api for cash@pos txn : {username_api}")
                txn_id_api = response["txnId"]
                logger.debug(f"Value of txnId obtained from txnlist api for cash@pos txn : {txn_id_api}")
                payment_card_brand_api = response["paymentCardBrand"]
                logger.debug(f"Value of paymentCardBrand obtained from txnlist api for cash@pos txn : {payment_card_brand_api}")
                payment_card_type_api = response["paymentCardType"]
                logger.debug(f"Value of paymentCardType obtained from txnlist api for cash@pos txn : {payment_card_type_api}")
                card_txn_type_api = response["cardTxnTypeDesc"]
                logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for cash@pos txn : {card_txn_type_api}")
                batch_number_api = response["batchNumber"]
                logger.debug(f"Value of batchNumber obtained from txnlist api for cash@pos txn : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for cash@pos txn : {card_last_four_digit_api}")
                external_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Value of externalRefNumber obtained from txnlist api for cash@pos txn : {external_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Value of merchantName obtained from txnlist api for cash@pos txn : {merchant_name_api}")
                payment_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Value of paymentCardBin obtained from txnlist api for cash@pos txn : {payment_card_bin_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Value of displayPAN obtained from txnlist api for cash@pos txn : {display_pan_api}")

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
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "cash_amt": cash_amt_api,
                    "sale_amt": sale_amt_api,
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
                    "display_pan": display_pan_api
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
                    "txn_amt": float(cash_amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "PENDING",
                    "cash_amt": float(cash_amount),
                    "sale_amt": float(sale_amount),
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CASH_OUT",
                    "card_txn_type": "91",
                    "card_last_four_digit": "0018"
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
                    "cash_amt": amt_cash_back_db,
                    "sale_amt": sale_amt_db,
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
                    "card_last_four_digit": card_last_four_digit_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(cash_amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                logger.info(f"Date and time value for chargeslip validation is: {txn_date},{txn_time}")
                expected_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'date': txn_date, 'time': txn_time,
                    'BATCH NO': batch_number,
                    'CARD TYPE': 'VISA',
                    'AUTH CODE': auth_code,
                    'payment_option': 'Cash Only',
                    "CASH PAID:": "Rs." + "{:,.2f}".format(cash_amount),
                    "TID": tid
                }

                receipt_validator.perform_charge_slip_validations(txn_id,{"username": app_username,
                                                                          "password": app_password},
                                                                  expected_values)
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal # Chargeslip validation is getting failed
def test_common_100_115_02_010():
    """
        Sub Feature Code: UI_Common_Card_Cash@pos_Void_HDFC_Dummy_EMVCTLS_VISA_CreditCard_Without_Pin_And_Without_Sale_417666
        Sub Feature Description: Performing the EMVCTLS cash@pos void transaction without sale via HDFC Dummy PG using VISA Credit card without pin (bin : 417666)
        TC naming code description: 100: Payment Method, 115: CARD_UI, 02:Cash@Posh , 010: TC010
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

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["cashBackOption"] = "1"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions when cash back option is enabled: {response}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for bin_info table : {result}")
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
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
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            random_number = random.randint(1, 9)  # For cash@pos with sale, amount should be multiple of 100's
            logger.debug(f"Randomly generated random_number is : {random_number} ")
            cash_amount = random_number * 100
            sale_amount = 0
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.click_cash_at_pos()
            logger.debug(f"Clicked on cash@pos button")
            home_page.enter_cash_at_pos_amount(cash_amount)
            logger.debug(f"Entered cash amount and sale amount for with sale : {cash_amount}, {sale_amount}")
            home_page.click_pay_now_button()
            logger.debug(f"Clicked on pay now button")
            home_page.enter_order_number_and_device_serial(order_id, device_serial)
            logger.debug(f"Entered order_id and device_serial : {order_id} , {device_serial} ")
            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype("CTLS_VISA_CREDIT_417666")
            logger.debug(f"Selected card type as CTLS_VISA_CREDIT_417666")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_proceed_homepage()

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1 "
            logger.debug(f"Query to fetch data from the txn table before void : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table before void : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table before void : {txn_id}")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id)
            txn_history_page.click_on_void_card_txn()
            logger.debug(f"Clicked on void button for cash@Pos without sale")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table : {txn_created_time}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table : {batch_number}")
            amount_db = result['amount'].values[0]
            logger.debug(f"Fetching amount value from the txn table : {amount_db}")
            amt_cash_back_db = result['amount_cash_back'].values[0]
            logger.debug(f"Fetching amount_cash_back value from the txn table : {amt_cash_back_db}")
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
            sale_amt_db = result['amount_original'].values[0]
            logger.debug(f"Fetching amount_original value from the txn table : {sale_amt_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant_code value from the txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment_card_brand value from the txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment_card_type value from the txn table : {payment_card_type_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer_code value from the txn table : {issuer_code_db}")
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
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer_name value from the txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer_name value from the txn table : {payer_name_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org_code value from the txn table : {org_code_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching external_ref value from the txn table : {order_id_db}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from the txn table : {posting_date}")

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
                date_and_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(cash_amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "VOIDED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number,
                    "card_type_desc": "*0018 CTLS",
                    "cash_amt": "{:,.2f}".format(cash_amount),
                    "sale_amt": "{:,.2f}".format(sale_amount)
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment status value from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode value from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id value from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching amount value from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status value from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching payment msg value from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time value from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn value from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_cde value from txn history for the txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id value from txn history for the txn : {txn_id}, {app_order_id}")
                app_batch_no = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch number value from txn history for the txn : {txn_id}, {app_batch_no}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid value from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid value from txn history for the txn : {txn_id}, {app_tid}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card type value from txn history for the txn : {txn_id}, {app_card_type_desc}")
                app_cash_amt = txn_history_page.fetch_cash_amt_text()
                logger.info(f"Fetching card amount value from txn history for the txn : {txn_id}, {app_cash_amt}")
                app_sale_amt = txn_history_page.fetch_sale_amt_text()
                logger.info(f"Fetching sale amount value from txn history for the txn : {txn_id}, {app_sale_amt}")

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
                    "cash_amt": app_cash_amt.split(' ')[1],
                    "sale_amt": app_sale_amt.split(' ')[1]
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
                expected_api_values = {
                    "pmt_status": "VOIDED",
                    "txn_amt": float(cash_amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "VOIDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CASH_OUT",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": expected_date_and_time_api,
                    "cash_amt": float(cash_amount),
                    "sale_amt": float(sale_amount),
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "CTLS",
                    "batch_number": batch_number,
                    "card_last_four_digit": "0018",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "display_pan": "0018"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Value of status obtained from txnlist api for cash@pos txn : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Value of amount obtained from txnlist api for cash@pos txn : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api for cash@pos txn : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Value of states obtained from txnlist api for cash@pos txn : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api for cash@pos txn : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api for cash@pos txn : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api for cash@pos txn : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api for cash@pos txn : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api for cash@pos txn : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Value of mid obtained from txnlist api for cash@pos txn : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Value of tid obtained from txnlist api for cash@pos txn : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api for cash@pos txn : {txn_type_api}")
                auth_code_api = response["authCode"]
                logger.debug(f"Value of authCode obtained from txnlist api for cash@pos txn : {auth_code_api}")
                date_and_time_api = response["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api for cash@pos txn : {date_and_time_api}")
                sale_amt_api = response["amountOriginal"]
                logger.debug(f"Value of amountOriginal obtained from txnlist api for cash@pos txn : {sale_amt_api}")
                cash_amt_api = response["amountCashBack"]
                logger.debug(f"Value of amountCashBack obtained from txnlist api for cash@pos txn : {cash_amt_api}")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"Value of deviceSerial obtained from txnlist api for cash@pos txn : {device_serial_api}")
                username_api = response["username"]
                logger.debug(f"Value of username obtained from txnlist api for cash@pos txn : {username_api}")
                txn_id_api = response["txnId"]
                logger.debug(f"Value of txnId obtained from txnlist api for cash@pos txn : {txn_id_api}")
                payment_card_brand_api = response["paymentCardBrand"]
                logger.debug(f"Value of paymentCardBrand obtained from txnlist api for cash@pos txn : {payment_card_brand_api}")
                payment_card_type_api = response["paymentCardType"]
                logger.debug(f"Value of paymentCardType obtained from txnlist api for cash@pos txn : {payment_card_type_api}")
                card_txn_type_api = response["cardTxnTypeDesc"]
                logger.debug(f"Value of cardTxnTypeDesc obtained from txnlist api for cash@pos txn : {card_txn_type_api}")
                batch_number_api = response["batchNumber"]
                logger.debug(f"Value of batchNumber obtained from txnlist api for cash@pos txn : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Value of cardLastFourDigit obtained from txnlist api for cash@pos txn : {card_last_four_digit_api}")
                external_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Value of externalRefNumber obtained from txnlist api for cash@pos txn : {external_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Value of merchantName obtained from txnlist api for cash@pos txn : {merchant_name_api}")
                payment_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Value of paymentCardBin obtained from txnlist api for cash@pos txn : {payment_card_bin_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Value of displayPAN obtained from txnlist api for cash@pos txn : {display_pan_api}")

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
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "cash_amt": cash_amt_api,
                    "sale_amt": sale_amt_api,
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
                    "display_pan": display_pan_api
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
                    "txn_amt": float(cash_amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "pmt_state": "VOIDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "cash_amt": float(cash_amount),
                    "sale_amt": float(sale_amount),
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CASH_OUT",
                    "card_txn_type": "91",
                    "card_last_four_digit": "0018"
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
                    "cash_amt": amt_cash_back_db,
                    "sale_amt": sale_amt_db,
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
                    "card_last_four_digit": card_last_four_digit_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "VOIDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(cash_amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                logger.info(f"Date and time value for chargeslip validation is: {txn_date},{txn_time}")
                expected_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'date': txn_date, 'time': txn_time,
                    'BATCH NO': batch_number,
                    'CARD TYPE': 'VISA',
                    'AUTH CODE': auth_code,
                    'payment_option': 'VOID CASH ONLY',
                    "TID": tid,
                    "CASH PAID:": "Rs." + "{:,.2f}".format(cash_amount)
                }

                receipt_validator.perform_charge_slip_validations(txn_id,{"username": app_username,
                                                                          "password": app_password},
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