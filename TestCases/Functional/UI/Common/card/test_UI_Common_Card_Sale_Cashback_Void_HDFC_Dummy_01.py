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
from Utilities import Validator, ConfigReader, DBProcessor, ResourceAssigner, date_time_converter, APIProcessor, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_02_005():
    """
    Sub Feature Code: UI_Common_Card_Sale_Cashback_Void_HDFC_Dummy_EMVCTLS_VISA_DebitCard_Without_Pin_476173
    Sub Feature Description:  Performing the EMVCTLS sale cashback voided transaction via HDFC Dummy PG using VISA Debit card having 16 digit
     PAN length without pin (bin: 476173)
    TC naming code description: 100: Payment Method, 115: CARD, 02: Sale+Cash@Pos, 005: TC005
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

        query = f"select org_code from org_employee where username='{app_username}'"
        logger.debug(f"Query to fetch org_code from the org_employee table  : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status='ACTIVE' and acquirer_code=" \
                f"'HDFC' and payment_gateway='DUMMY'"
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetching result for terminal info table  {org_code} : {result}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"fetching device serial from terminal info table {org_code} : {device_serial}")
        mid = result["mid"].iloc[0]
        logger.debug(f"fetching mid from terminal info table {org_code} : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"fetching tid from terminal info table {org_code} : {tid}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"fetching terminal info id from terminal info table {org_code} : {terminal_info_id}")

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
        logger.debug(f"Response received for setting preconditions for cash back option to be enabled : {response}")

        query = f"select bank_code from bin_info where bin='476173'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code_info = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code_info}")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            cashback_amount = (random.randint(1, 5)) * 100  # For cash@pos with sale, amount should be multiple of 100's
            sale_amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.click_cash_at_pos()
            home_page.click_cash_at_pos_with_sale_switch()
            home_page.enter_cash_at_pos_amount(amount=cashback_amount)
            home_page.enter_cash_at_pos_sale_amount(amount=sale_amount)
            logger.debug(f"Entered cashback amount is : {cashback_amount}")
            logger.debug(f"Entered sale amount is : {sale_amount}")
            home_page.click_pay_now_button()
            home_page.enter_order_number_and_device_serial_for_card(order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered order id is : {order_id}")
            logger.debug(f"Entered device serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting card type as : CTLS_VISA_DEBIT_476173")
            card_page.select_cardtype("CTLS_VISA_DEBIT_476173")
            logger.debug(f"Selected card type as : CTLS_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_transaction_by_order_id(order_id=order_id)
            txn_history_page.click_on_void_card_txn()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for the txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {created_time}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table : {batch_number}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name}")
            amount_db = int(result['amount'].values[0])
            logger.debug(f"Fetching amount from the txn table : {amount_db}")
            cash_back_amt_db = int(result['amount_cash_back'].iloc[0])
            logger.debug(f"fetched cash_back_amt from txn table is : {cash_back_amt_db}")
            sale_amt_db = int(result['amount_original'].iloc[0])
            logger.debug(f"fetched sale_amt from txn table is : {sale_amt_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table : {payment_mode_db}")
            payment_status_db = result['status'].values[0]
            logger.debug(f"Fetching payment_status from the txn table : {payment_status_db}")
            payment_state_db = result['state'].values[0]
            logger.debug(f"Fetching payment_state from the txn table : {payment_state_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table : {acquirer_code_db}")
            bank_name_db = result['bank_name'].values[0]
            logger.debug(f"Fetching bank_name from the txn table : {bank_name_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table : {payment_gateway_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table : {payment_card_type_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table : {org_code_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].iloc[0]
            logger.debug(f"Fetching customer name from txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].iloc[0]
            logger.debug(f"Fetching payer name from txn table : {payer_name_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment card bin from txn table : {payment_card_bin_db}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {posting_date}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id=testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            date_and_time = date_time_converter.to_app_format(posting_date_db=posting_date)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "txn_amt": "{:.2f}".format(cashback_amount+sale_amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "L3TEST",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*0453 CTLS",
                    "cash_back_amount": "{:.2f}".format(cashback_amount),
                    "sale_amount": "{:.2f}".format(sale_amount),
                    "device_serial": device_serial,
                    "order_id": order_id
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                txn_history_page = TransHistoryPage(driver=app_driver)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching app_txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching app_amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching app_settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching app_payment_msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching app_date_and_time from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching app_rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching app_auth_code from txn history for the txn : {txn_id}, {app_auth_code}")
                app_batch_no = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching app_batch_no from txn history for the txn : {txn_id}, {app_batch_no}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching app_customer_name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching app_card_type_desc from txn history for the txn : {txn_id}, {app_card_type_desc}")
                app_cash_amount = txn_history_page.fetch_cash_amt_text()
                logger.info(f"Fetching app_cash_amount from txn history for the txn : {txn_id}, {app_cash_amount}")
                app_sale_amount = txn_history_page.fetch_sale_amt_text()
                logger.info(f"Fetching app_sale_amount from txn history for the txn : {txn_id}, {app_sale_amount}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {txn_id}, {app_order_id}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rr_number": app_rrn,
                    "auth_code": app_auth_code,
                    "customer_name": app_customer_name,
                    "batch_number": app_batch_no,
                    "mid": app_mid,
                    "tid": app_tid,
                    "card_type_desc": app_card_type_desc,
                    "cash_back_amount": app_cash_amount.split(' ')[1],
                    "sale_amount": app_sale_amount.split(' ')[1],
                    "device_serial": app_device_serial,
                    "order_id": app_order_id
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                expected_api_values = {
                    "pmt_status": "VOIDED",
                    "txn_amt": float(cashback_amount + sale_amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "VOIDED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code_info,
                    "txn_type": "CASH_BACK",
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
                    "card_txn_type": "CTLS",
                    "cash_back_amt": cashback_amount,
                    "sale_amt": sale_amount,
                    "batch_number": batch_number,
                    "card_last_four_digit": "0453",
                    "customer_name": "L3TEST/CARD1045",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_code_db,
                    "payer_name": "L3TEST/CARD1045",
                    "pmt_card_bin": "476173",
                    "card_type": "VISA",
                    "card_txn_type_desc": "CTLS",
                    "display_pan": "0453",
                    "name_on_card": "L3TEST/CARD1045"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from response : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from response : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from response : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from response : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from response : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from response : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from response : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from response : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from response : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from response : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching transaction type from response : {txn_type_api}")
                auth_code_api = response["authCode"]
                logger.debug(f"Fetching auth code from response : {auth_code_api}")
                date_and_time_api_response = response["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api_response}")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"Fetching device serial from response : {device_serial_api}")
                username_api = response["username"]
                logger.debug(f"Fetching username from response : {username_api}")
                txn_id_api = response["txnId"]
                logger.debug(f"Fetching transaction id from response : {txn_id_api}")
                payment_card_brand_api = response["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response : {payment_card_brand_api}")
                payment_card_type_api = response["paymentCardType"]
                logger.debug(f"Fetching payment card type from response : {payment_card_type_api}")
                card_txn_type_api = response["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response : {card_txn_type_api}")
                cash_back_amt_api = response["amountCashBack"]
                logger.debug(f"Fetching cash back amt from response : {cash_back_amt_api}")
                sale_amt_api = response["amountOriginal"]
                logger.debug(f"Fetching sale amt from response : {sale_amt_api}")
                batch_number_api = response["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                customer_name_api = response["customerName"]
                logger.debug(f"Fetching customer name from response : {customer_name_api}")
                ext_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Fetching external Ref number from response : {ext_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payer_name_api = response["payerName"]
                logger.debug(f"Fetching payer name from response : {payer_name_api}")
                pmt_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {pmt_card_bin_api}")
                card_type_api = response["cardType"]
                logger.debug(f"Fetching pmt card type from response : {card_type_api}")
                card_txn_type_desc_api = response["cardTxnTypeDesc"]
                logger.debug(f"Fetching pmt card txn type desc from response : {card_txn_type_desc_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Fetching display PAN from response : {display_pan_api}")
                name_on_card_api = response["nameOnCard"]
                logger.debug(f"Fetching name on card from response : {name_on_card_api}")

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
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api_response),
                    "device_serial": device_serial_api,
                    "username": username_api,
                    "txn_id": txn_id_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_txn_type": card_txn_type_api,
                    "cash_back_amt": cash_back_amt_api,
                    "sale_amt": sale_amt_api,
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "customer_name": customer_name_api,
                    "ext_ref_number": ext_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "payer_name": payer_name_api,
                    "pmt_card_bin": pmt_card_bin_api,
                    "card_type": card_type_api,
                    "card_txn_type_desc": card_txn_type_desc_api,
                    "display_pan": display_pan_api,
                    "name_on_card": name_on_card_api
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "txn_amt": cashback_amount + sale_amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "pmt_state": "VOIDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "cash_back_amt": cashback_amount,
                    "sale_amt": sale_amount,
                    "pmt_card_bin": "476173",
                    "order_id": order_id,
                    "issuer_code": issuer_code_info,
                    "org_code": org_code,
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CASH_BACK",
                    "card_txn_type": "91",
                    "card_last_four_digit": "0453",
                    "customer_name": "L3TEST/CARD1045",
                    "payer_name": "L3TEST/CARD1045"
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
                    "cash_back_amt": cash_back_amt_db,
                    "sale_amt": sale_amt_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "order_id": order_id_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "customer_name": customer_name_db,
                    "payer_name": payer_name_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=created_time)
                expected_portal_values = {
                    "pmt_status": "VOIDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(cashback_amount + sale_amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_and_time_portal
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password, order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"Fetching transaction id from portal : {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split(' ')
                logger.debug(f"Fetching amount from portal : {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth code from portal : {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rrn from portal : {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"Fetching transaction type from portal : {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"Fetching status from portal : {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"Fetching username from portal : {username}")
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Fetching date and time from portal : {date_time}")

                actual_portal_values = {
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + "{:.2f}".format(sale_amount),
                    "CASH PAID:": "Rs." + "{:.2f}".format(cashback_amount),
                    "TOTAL AMOUNT:": "Rs." + "{:.2f}".format(sale_amount + cashback_amount),
                    "AUTH CODE": auth_code,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "VOID SALE CASH BACK",
                    "BATCH NO": batch_number,
                    "TID": tid
                }
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_Id=testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_02_006():
    """
    Sub Feature Code: UI_Common_Card_Sale_Cashback_Void_HDFC_Dummy_EMVCTLS_VISA_CreditCard_Without_Pin_417666
    Sub Feature Description: Performing the EMVCTLS Sale Cashback void transaction via HDFC Dummy PG using VISA Credit card having
     16 digit PAN length without pin (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 02: Sale+Cash@Pos, 006: TC006
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

        query = f"select org_code from org_employee where username='{app_username}'"
        logger.debug(f"Query to fetch org_code from the org_employee table  : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status='ACTIVE' and acquirer_code=" \
                f"'HDFC' and payment_gateway='DUMMY'"
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetching result for terminal info table  {org_code} : {result}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"fetching device serial from terminal info table {org_code} : {device_serial}")
        mid = result["mid"].iloc[0]
        logger.debug(f"fetching mid from terminal info table {org_code} : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"fetching tid from terminal info table {org_code} : {tid}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"fetching terminal info id from terminal info table {org_code} : {terminal_info_id}")

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
        logger.debug(f"Response received for setting preconditions for cash back option to be enabled : {response}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code_info = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code_info}")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            cashback_amount = (random.randint(1, 5)) * 100  # For cash@pos with sale, amount should be multiple of 100's
            sale_amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.click_cash_at_pos()
            home_page.click_cash_at_pos_with_sale_switch()
            home_page.enter_cash_at_pos_amount(amount=cashback_amount)
            home_page.enter_cash_at_pos_sale_amount(amount=sale_amount)
            logger.debug(f"Entered cashback amount is : {cashback_amount}")
            logger.debug(f"Entered sale amount is : {sale_amount}")
            home_page.click_pay_now_button()
            home_page.enter_order_number_and_device_serial_for_card(order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered order id is : {order_id}")
            logger.debug(f"Entered device serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype("CTLS_VISA_CREDIT_417666")
            logger.debug(f"Selected card type as : CTLS_VISA_CREDIT_417666")
            payment_page.click_on_proceed_homepage()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_transaction_by_order_id(order_id=order_id)
            txn_history_page.click_on_void_card_txn()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for the txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {created_time}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table : {batch_number}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name}")
            amount_db = int(result['amount'].values[0])
            logger.debug(f"Fetching amount from the txn table : {amount_db}")
            cash_back_amt_db = int(result['amount_cash_back'].iloc[0])
            logger.debug(f"fetched cash_back_amt from txn table is : {cash_back_amt_db}")
            sale_amt_db = int(result['amount_original'].iloc[0])
            logger.debug(f"fetched sale_amt from txn table is : {sale_amt_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table : {payment_mode_db}")
            payment_status_db = result['status'].values[0]
            logger.debug(f"Fetching payment_status from the txn table : {payment_status_db}")
            payment_state_db = result['state'].values[0]
            logger.debug(f"Fetching payment_state from the txn table : {payment_state_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table : {acquirer_code_db}")
            bank_name_db = result['bank_name'].values[0]
            logger.debug(f"Fetching bank_name from the txn table : {bank_name_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table : {payment_gateway_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table : {payment_card_type_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table : {org_code_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching payment card bin from txn table : {payment_card_bin_db}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {posting_date}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id=testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            date_and_time = date_time_converter.to_app_format(posting_date_db=posting_date)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "txn_amt": "{:.2f}".format(cashback_amount+sale_amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*0018 CTLS",
                    "cash_back_amount": "{:.2f}".format(cashback_amount),
                    "sale_amount": "{:.2f}".format(sale_amount),
                    "device_serial": device_serial,
                    "order_id": order_id
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                txn_history_page = TransHistoryPage(driver=app_driver)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching app_txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching app_amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching app_settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching app_payment_msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching app_date_and_time from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching app_rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching app_auth_code from txn history for the txn : {txn_id}, {app_auth_code}")
                app_batch_no = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching app_batch_no from txn history for the txn : {txn_id}, {app_batch_no}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching app_card_type_desc from txn history for the txn : {txn_id}, {app_card_type_desc}")
                app_cash_amount = txn_history_page.fetch_cash_amt_text()
                logger.info(f"Fetching app_cash_amount from txn history for the txn : {txn_id}, {app_cash_amount}")
                app_sale_amount = txn_history_page.fetch_sale_amt_text()
                logger.info(f"Fetching app_sale_amount from txn history for the txn : {txn_id}, {app_sale_amount}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {txn_id}, {app_order_id}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rr_number": app_rrn,
                    "auth_code": app_auth_code,
                    "batch_number": app_batch_no,
                    "mid": app_mid,
                    "tid": app_tid,
                    "card_type_desc": app_card_type_desc,
                    "cash_back_amount": app_cash_amount.split(' ')[1],
                    "sale_amount": app_sale_amount.split(' ')[1],
                    "device_serial": app_device_serial,
                    "order_id": app_order_id
                }

                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                expected_api_values = {
                    "pmt_status": "VOIDED",
                    "txn_amt": float(cashback_amount + sale_amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "VOIDED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code_info,
                    "txn_type": "CASH_BACK",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "CTLS",
                    "cash_back_amt": cashback_amount,
                    "sale_amt": sale_amount,
                    "batch_number": batch_number,
                    "card_last_four_digit": "0018",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_code_db,
                    "pmt_card_bin": "417666",
                    "card_type": "VISA",
                    "card_txn_type_desc": "CTLS",
                    "display_pan": "0018"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from response : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from response : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from response : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from response : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from response : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from response : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from response : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from response : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from response : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from response : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching transaction type from response : {txn_type_api}")
                auth_code_api = response["authCode"]
                logger.debug(f"Fetching auth code from response : {auth_code_api}")
                date_and_time_api_response = response["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api_response}")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"Fetching device serial from response : {device_serial_api}")
                username_api = response["username"]
                logger.debug(f"Fetching username from response : {username_api}")
                txn_id_api = response["txnId"]
                logger.debug(f"Fetching transaction id from response : {txn_id_api}")
                payment_card_brand_api = response["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response : {payment_card_brand_api}")
                payment_card_type_api = response["paymentCardType"]
                logger.debug(f"Fetching payment card type from response : {payment_card_type_api}")
                card_txn_type_api = response["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response : {card_txn_type_api}")
                cash_back_amt_api = response["amountCashBack"]
                logger.debug(f"Fetching cash back amt from response : {cash_back_amt_api}")
                sale_amt_api = response["amountOriginal"]
                logger.debug(f"Fetching sale amt from response : {sale_amt_api}")
                batch_number_api = response["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                ext_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Fetching external Ref number from response : {ext_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                pmt_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {pmt_card_bin_api}")
                card_type_api = response["cardType"]
                logger.debug(f"Fetching pmt card type from response : {card_type_api}")
                card_txn_type_desc_api = response["cardTxnTypeDesc"]
                logger.debug(f"Fetching pmt card txn type desc from response : {card_txn_type_desc_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Fetching display PAN from response : {display_pan_api}")

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
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api_response),
                    "device_serial": device_serial_api,
                    "username": username_api,
                    "txn_id": txn_id_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_txn_type": card_txn_type_api,
                    "cash_back_amt": cash_back_amt_api,
                    "sale_amt": sale_amt_api,
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "ext_ref_number": ext_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "pmt_card_bin": pmt_card_bin_api,
                    "card_type": card_type_api,
                    "card_txn_type_desc": card_txn_type_desc_api,
                    "display_pan": display_pan_api
                }

                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "txn_amt": cashback_amount + sale_amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "pmt_state": "VOIDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "cash_back_amt": cashback_amount,
                    "sale_amt": sale_amount,
                    "pmt_card_bin": "417666",
                    "order_id": order_id,
                    "issuer_code": issuer_code_info,
                    "org_code": org_code,
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CASH_BACK",
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
                    "device_serial": device_serial_db,
                    "merchant_code": merchant_code_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "cash_back_amt": cash_back_amt_db,
                    "sale_amt": sale_amt_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "order_id": order_id_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=created_time)
                expected_portal_values = {
                    "pmt_status": "VOIDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(cashback_amount + sale_amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_and_time_portal
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password, order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"Fetching transaction id from portal : {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split(' ')
                logger.debug(f"Fetching amount from portal : {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth code from portal : {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rrn from portal : {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"Fetching transaction type from portal : {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"Fetching status from portal : {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"Fetching username from portal : {username}")
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Fetching date and time from portal : {date_time}")

                actual_portal_values = {
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + "{:.2f}".format(sale_amount),
                    "CASH PAID:": "Rs." + "{:.2f}".format(cashback_amount),
                    "TOTAL AMOUNT:": "Rs." + "{:.2f}".format(sale_amount + cashback_amount),
                    "AUTH CODE": auth_code,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "VOID SALE CASH BACK",
                    "BATCH NO": batch_number,
                    "TID": tid
                }
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id=testcase_id, exception_caught=e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_Id=testcase_id)