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
def test_common_100_115_156():
    """
    Sub Feature Code: UI_Common_Card_Sale_PRIZM_EMV_VISA_DebitCard_With_Pin_428090
    Sub Feature Description: Performing the EMV sale transaction via PRIZM PG using VISA Debit card having
    16 digit PAN length with pin (bin: 428090)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 156: TC156
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
                "acquirer_code='AXIS' and payment_gateway='PRIZM_V2' "
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select bank_code from bin_info where bin='428090'"
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
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(600, 2000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_DEBIT_428090")
            logger.debug(f"selected the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")
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
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "RAJA",
                    "card_type_desc": "*0321 EMV with PIN"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for the txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the txn : {txn_id}, {app_batch_number}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the txn : {txn_id}, {app_customer_name}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the txn : {txn_id}, {app_card_type_desc}")

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
                    "card_type_desc": app_card_type_desc
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "AXIS",
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
                    "card_txn_type": "EMV with PIN",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0321",
                    "customer_name": "RAJA                     /",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "RAJA                     /",
                    "pmt_card_bin": "428090",
                    "name_on_card": "RAJA                     /",
                    "display_pan": "0321"
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
                date_and_time_api = response["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api}")
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
                batch_number_api = response["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                customer_name_api = response["customerName"]
                logger.debug(f"Fetching customer name from response : {customer_name_api}")
                external_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response : {external_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payer_name_api = response["payerName"]
                logger.debug(f"Fetching payer name from response : {payer_name_api}")
                payment_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {payment_card_bin_api}")
                name_on_card_api = response["nameOnCard"]
                logger.debug(f"Fetching name on card from response : {name_on_card_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Fetching display_PAN from response : {display_pan_api}")

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
                    "display_pan": display_pan_api
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "AXIS",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "PRIZM_V2",
                    "settle_status": "PENDING",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "428090",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "03",
                    "card_last_four_digit": "0321",
                    "customer_name": "RAJA                     /",
                    "payer_name": "RAJA                     /"
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
                    "payer_name": payer_name_db
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
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
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
                total_amount = transaction_details[0]['Total Amount'].split()
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "AUTH CODE": auth_code.strip(),
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "DEBIT SALE",
                    "BATCH NO": batch_number_db,
                    "TID": tid
                }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
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
def test_common_100_115_157():
    """
    Sub Feature Code: UI_Common_Card_Sale_PRIZM_EMV_RUPAY_DebitCard_With_Pin_608326
    Sub Feature Description: Performing the EMV sale transaction via PRIZM PG using RUPAY Debit card having
    16 digit PAN length with pin (bin: 608326)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 157: TC157
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

        query = f"select org_code, name from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='AXIS' and payment_gateway='PRIZM_V2' "
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(600, 2000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_WITH_PIN_RUPAY_DEBIT_608326")
            card_page.select_cardtype(text="EMV_WITH_PIN_RUPAY_DEBIT_608326")
            logger.debug(f"selected the card type as : EMV_WITH_PIN_RUPAY_DEBIT_608326")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")
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
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "RUPAY CARD IMAGE 01",
                    "card_type_desc": "*0017 EMV with PIN"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for the txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the txn : {txn_id}, {app_batch_number}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the txn : {txn_id}, {app_customer_name}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the txn : {txn_id}, {app_card_type_desc}")

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
                    "card_type_desc": app_card_type_desc
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "AXIS",
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
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "card_txn_type": "EMV with PIN",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0017",
                    "customer_name": "RUPAY CARD IMAGE 01      /",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "RUPAY CARD IMAGE 01      /",
                    "pmt_card_bin": "608326",
                    "name_on_card": "RUPAY CARD IMAGE 01      /",
                    "display_pan": "0017"
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
                date_and_time_api = response["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api}")
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
                batch_number_api = response["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                customer_name_api = response["customerName"]
                logger.debug(f"Fetching customer name from response : {customer_name_api}")
                external_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response : {external_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payer_name_api = response["payerName"]
                logger.debug(f"Fetching payer name from response : {payer_name_api}")
                payment_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {payment_card_bin_api}")
                name_on_card_api = response["nameOnCard"]
                logger.debug(f"Fetching name on card from response : {name_on_card_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Fetching display_PAN from response : {display_pan_api}")

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
                    "display_pan": display_pan_api
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "AXIS",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "PRIZM_V2",
                    "settle_status": "PENDING",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "608326",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "03",
                    "card_last_four_digit": "0017",
                    "customer_name": "RUPAY CARD IMAGE 01      /",
                    "payer_name": "RUPAY CARD IMAGE 01      /"
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
                    "payer_name": payer_name_db
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
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
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
                total_amount = transaction_details[0]['Total Amount'].split()
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "RUPAY",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "SALE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "AUTH CODE": auth_code.strip(),
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "SALE",
                    "BATCH NO": batch_number_db,
                    "TID": tid
                }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
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
def test_common_100_115_158():
    """
    Sub Feature Code: UI_Common_Card_Sale_PRIZM_EMV_VISA_DebitCard_Without_Pin_476173
    Sub Feature Description: Performing the EMV sale transaction via PRIZM PG using VISA Debit card having
    16 digit PAN length without pin (bin: 476173)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 158: TC158
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

        query = f"select org_code, name from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='AXIS' and payment_gateway='PRIZM_V2' "
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
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
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_VISA_DEBIT_476173")
            card_page.select_cardtype(text="EMV_VISA_DEBIT_476173")
            logger.debug(f"selected the card type as : EMV_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"fetching result for txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")
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
                expected_app_values = {
                    "txn_amt": str(amount) + ".00",
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "L3TEST",
                    "card_type_desc": "*0250 EMV"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for the txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the txn : {txn_id}, {app_batch_number}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the txn : {txn_id}, {app_customer_name}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the txn : {txn_id}, {app_card_type_desc}")

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
                    "card_type_desc": app_card_type_desc
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "AXIS",
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
                    "display_pan": "0250"
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
                date_and_time_api = response["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api}")
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
                batch_number_api = response["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                customer_name_api = response["customerName"]
                logger.debug(f"Fetching customer name from response : {customer_name_api}")
                external_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response : {external_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payer_name_api = response["payerName"]
                logger.debug(f"Fetching payer name from response : {payer_name_api}")
                payment_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {payment_card_bin_api}")
                name_on_card_api = response["nameOnCard"]
                logger.debug(f"Fetching name on card from response : {name_on_card_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Fetching display_PAN from response : {display_pan_api}")

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
                    "display_pan": display_pan_api
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "AXIS",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "PRIZM_V2",
                    "settle_status": "PENDING",
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
                    "payer_name": "L3TEST/CARD0025"
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
                    "payer_name": payer_name_db
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
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": f"{str(amount)}.00",
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
                total_amount = transaction_details[0]['Total Amount'].split()
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + str(amount) + ".00",
                    "AUTH CODE": auth_code.strip(),
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "DEBIT SALE",
                    "BATCH NO": batch_number_db,
                    "TID": tid
                }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
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
def test_common_100_115_159():
    """
    Sub Feature Code: UI_Common_Card_Sale_PRIZM_EMV_MASTER_DebitCard_Without_Pin_222360
    Sub Feature Description: Performing the EMV sale transaction via PRIZM PG using MASTER Debit card having
    16 digit PAN length without pin (bin: 222360)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 159: TC159
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

        query = f"select org_code, name from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='AXIS' and payment_gateway='PRIZM_V2' "
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
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
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_MASTER_DEBIT_222360")
            card_page.select_cardtype(text="EMV_MASTER_DEBIT_222360")
            logger.debug(f"selected the card type as : EMV_MASTER_DEBIT_222360")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn table : {result} ")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table : {merchant_name}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table : {payer_name_db}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")
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
                expected_app_values = {
                    "txn_amt": str(amount) + ".00",
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "card_type_desc": "*0078 EMV",
                    "customer_name": "MTIP14 MCD 13A"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for the txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the txn : {txn_id}, {app_card_type_desc}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the txn : {txn_id}, {app_customer_name}")

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
                    "customer_name": app_customer_name
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "AXIS",
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
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "DEBIT",
                    "card_txn_type": "EMV",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0078",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "222360",
                    "display_pan": "0078",
                    "customer_name": "MTIP14 MCD 13A",
                    "payer_name": "MTIP14 MCD 13A",
                    "name_on_card": "MTIP14 MCD 13A"
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
                date_and_time_api = response["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api}")
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
                batch_number_api = response["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                external_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response : {external_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payment_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {payment_card_bin_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Fetching display_PAN from response : {display_pan_api}")
                customer_name_api = response["customerName"]
                logger.debug(f"Fetching customer name from response : {customer_name_api}")
                payer_name_api = response["payerName"]
                logger.debug(f"Fetching payer name from response : {payer_name_api}")
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
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "name_on_card": name_on_card_api
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "AXIS",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "PRIZM_V2",
                    "settle_status": "PENDING",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "222360",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "card_last_four_digit": "0078",
                    "customer_name": "MTIP14 MCD 13A",
                    "payer_name": "MTIP14 MCD 13A"
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
                    "payer_name": payer_name_db
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": f"{str(amount)}.00",
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
                total_amount = transaction_details[0]['Total Amount'].split()
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "MasterCard",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + str(amount) + ".00",
                    "AUTH CODE": auth_code.strip(),
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "DEBIT SALE",
                    "BATCH NO": batch_number_db,
                    "TID": tid
                }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
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
def test_common_100_115_160():
    """
    Sub Feature Code: UI_Common_Card_Sale_PRIZM_EMV_RUPAY_DebitCard_Without_Pin_608326
    Sub Feature Description: Performing the EMV sale transaction via PRIZM PG using RUPAY Debit card having
    16 digit PAN length without pin (bin: 608326)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 160: TC160
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
                "acquirer_code='AXIS' and payment_gateway='PRIZM_V2' "
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_RUPAY_DEBIT_608326")
            card_page.select_cardtype(text="EMV_RUPAY_DEBIT_608326")
            logger.debug(f"selected the card type as : EMV_RUPAY_DEBIT_608326")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")
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
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "RUPAY CARD IMAGE 02",
                    "card_type_desc": "*0025 EMV"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for the txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the txn : {txn_id}, {app_batch_number}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the txn : {txn_id}, {app_customer_name}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the txn : {txn_id}, {app_card_type_desc}")

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
                    "card_type_desc": app_card_type_desc
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "AXIS",
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
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "card_txn_type": "EMV",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0025",
                    "customer_name": "RUPAY CARD IMAGE 02      /",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "RUPAY CARD IMAGE 02      /",
                    "pmt_card_bin": "608326",
                    "name_on_card": "RUPAY CARD IMAGE 02      /",
                    "display_pan": "0025"
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
                date_and_time_api = response["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api}")
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
                batch_number_api = response["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                customer_name_api = response["customerName"]
                logger.debug(f"Fetching customer name from response : {customer_name_api}")
                external_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response : {external_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payer_name_api = response["payerName"]
                logger.debug(f"Fetching payer name from response : {payer_name_api}")
                payment_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {payment_card_bin_api}")
                name_on_card_api = response["nameOnCard"]
                logger.debug(f"Fetching name on card from response : {name_on_card_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Fetching display_PAN from response : {display_pan_api}")

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
                    "display_pan": display_pan_api
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "AXIS",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "PRIZM_V2",
                    "settle_status": "PENDING",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "608326",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "card_last_four_digit": "0025",
                    "customer_name": "RUPAY CARD IMAGE 02      /",
                    "payer_name": "RUPAY CARD IMAGE 02      /"
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
                    "payer_name": payer_name_db
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
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
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
                total_amount = transaction_details[0]['Total Amount'].split()
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "RUPAY",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "SALE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "AUTH CODE": auth_code.strip(),
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "SALE",
                    "BATCH NO": batch_number_db,
                    "TID": tid
                }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
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
