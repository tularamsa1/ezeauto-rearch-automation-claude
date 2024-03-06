import random
import sys
import time
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
def test_common_100_115_183():
    """
    Sub Feature Code: UI_Common_Card_Void_HDFC_EMV_VISA_DEBIT_476173
    Sub Feature Description:  Performing the EMV void transaction via HDFC PG using EMV VISA Debit card having 16 digit
     PAN length with pin (bin: 476173)
    TC naming code description:  100: Payment Method, 115: CARD_UI, 183: TC0183
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

        query = f"select org_code, name from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code, name from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status='ACTIVE' and acquirer_code=" \
                f"'HDFC' and payment_gateway='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        device_serial = result["device_serial"].iloc[0]
        terminal_info_id = result["id"].iloc[0]
        logger.debug(
            f"fetched mid : {mid}, tid : {tid}, device_serial : {device_serial}, terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["cardPaymentEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select bank_code from bin_info where bin='476173'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
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
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(1, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount, order_id, device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(app_driver)
            logger.debug(f"selecting the card type as : CTLS_VISA_DEBIT_476173")
            card_page.select_cardtype("EMV_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for the txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            # voiding the txn
            home_page.wait_for_home_page_load()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
            txn_history_page.click_on_void_card_txn()

            time.sleep(3)
            logger.debug(f"Waiting for 3 secs to get data from txn table for void txn")

            query = f"select * from txn where org_code ='{str(org_code)}' AND payment_mode = 'CARD' AND device_serial" \
                    f"='{device_serial}' AND external_ref='{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from the txn for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            txn_created_time = result['created_time'].values[0]
            txn_id = result['id'].values[0]
            rrn = result['rr_number'].values[0]
            auth_code = result['auth_code'].values[0]
            batch_number = result['batch_number'].values[0]
            customer_name = result['customer_name'].values[0]
            amount_db = result['amount'].values[0]
            payment_mode_db = result['payment_mode'].values[0]
            payment_status_db = result['status'].values[0]
            payment_state_db = result['state'].values[0]
            acquirer_code_db = result['acquirer_code'].values[0]
            issuer_code_db = result['issuer_code'].values[0]
            payer_name_db = result['payer_name'].values[0]
            mid_db = result['mid'].values[0]
            tid_db = result['tid'].values[0]
            payment_gateway_db = result['payment_gateway'].values[0]
            settlement_status_db = result['settlement_status'].values[0]
            order_id_db = result['external_ref'].values[0]
            device_serial_db = result['external_ref2'].values[0]
            org_code_db = result['org_code'].values[0]
            payment_card_bin_db = result['payment_card_bin'].values[0]
            payment_card_brand_db = result['payment_card_brand'].values[0]
            payment_card_type_db = result['payment_card_type'].values[0]
            txn_type_db = result['txn_type'].values[0]
            card_txn_type_db = result['card_txn_type'].values[0]
            card_last_four_digit_db = result['card_last_four_digit'].values[0]
            merchant_name = result['merchant_name'].values[0]
            posting_date = result['posting_date'].values[0]

            logger.debug(f"txn_created_time:{txn_created_time}, txn_id:{txn_id}, rrn:{rrn}, auth_code:{auth_code}, "
                         f"batch_number:{batch_number}, customer_name:{customer_name}, amount_db:{amount_db}, "
                         f"payment_mode_db:{payment_mode_db}, payment_status_db:{payment_status_db}, payment_state_db:"
                         f"{payment_state_db}, acquirer_code_db:{acquirer_code_db}, issuer_code_db:{issuer_code_db}, "
                         f"payer_name_db:{payer_name_db}, mid_db:{mid_db}, tid_db:{tid_db}, payment_gateway_db:"
                         f"{payment_gateway_db}, settlement_status_db:{settlement_status_db}, order_id_db:{order_id_db}"
                         f", device_serial_db:{device_serial_db}, org_code_db:{org_code_db}, payment_card_bin_db:"
                         f"{payment_card_bin_db}, payment_card_brand_db:{payment_card_brand_db}, payment_card_type_db:"
                         f"{payment_card_type_db}, txn_type_db:{txn_type_db}, card_txn_type_db:{card_txn_type_db}, "
                         f"card_last_four_digit_db:{card_last_four_digit_db}, merchant_name:{merchant_name}, posting_date:{posting_date}")

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
            date_and_time = date_time_converter.to_app_format(posting_date)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "txn_amt": "{:.2f}".format(amount),
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
                    "card_type_desc": "*0250 EMV",
                    "order_id": order_id,
                    "device_serial": device_serial
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_status = txn_history_page.fetch_txn_status_text()
                payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_auth_code = txn_history_page.fetch_auth_code_text()
                app_batch_no = txn_history_page.fetch_batch_number_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_mid = txn_history_page.fetch_mid_text()
                app_tid = txn_history_page.fetch_tid_text()
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                app_order_id = txn_history_page.fetch_order_id_text()
                app_device_serial = txn_history_page.fetch_device_serial_text()

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
                    "order_id": app_order_id,
                    "device_serial": app_device_serial
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
                date_and_time = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {
                    "pmt_status": "VOIDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "VOIDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "batch_number": batch_number,
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "device_serial": device_serial,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "L3TEST/CARD0025",
                    "pmt_card_bin": "476173",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "card_type": "VISA",
                    "display_pan": "0250",
                    "name_on_card": "L3TEST/CARD0025"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_time_api = response["createdTime"]
                batch_number_api = response["batchNumber"]
                card_last_four_digit_api = response["cardLastFourDigit"]
                customer_name_api = response["customerName"]
                device_serial_api = response["deviceSerial"]
                external_ref_number_api = response["externalRefNumber"]
                merchant_name_api = response["merchantName"]
                payer_name_api = response["payerName"]
                payment_card_bin_api = response["paymentCardBin"]
                payment_card_brand_api = response["paymentCardBrand"]
                payment_card_type_api = response["paymentCardType"]
                card_type_api = response["cardType"]
                display_pan_api = response["displayPAN"]
                name_on_card_api = response["nameOnCard"]

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
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_time_api),
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "customer_name": customer_name_api,
                    "device_serial": device_serial_api,
                    "ext_ref_number": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "payer_name": payer_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_type": card_type_api,
                    "display_pan": display_pan_api,
                    "name_on_card": name_on_card_api
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "pmt_state": "VOIDED",
                    "acquirer_code": "HDFC",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "HDFC",
                    "settle_status": "SETTLED",
                    "order_id": order_id,
                    "device_serial": device_serial,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "476173",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "customer_name": "L3TEST/CARD0025",
                    "payer_name": "L3TEST/CARD0025",
                    "card_last_four_digit": "0250"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db, "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "order_id": order_id_db,
                    "device_serial": device_serial_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "terminal_info_id": terminal_info_id,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "customer_name": customer_name,
                    "payer_name": payer_name_db,
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
                    "txn_amt": "{:.2f}".format(amount),
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                    'AUTH CODE': str(auth_code).strip(), 'BATCH NO': str(batch_number), 'CARD TYPE': 'VISA',
                    'payment_option': 'VOID SALE', 'TID': tid_db
                }
                receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password}, expected_values)
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
def test_common_100_115_184():
    """
    Sub Feature Code: UI_Common_Card_Void_HDFC_EMV_WITH_PIN_VISA_DEBIT_428090
    Sub Feature Description:  Performing the EMV void transaction via HDFC PG using EMV With Pin VISA Debit card
    having 16 digit PAN length with pin (bin: 428090)
    TC naming code description:  100: Payment Method, 115: CARD_UI, 184: TC184
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

        query = f"select org_code, name from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code, name from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status='ACTIVE' and acquirer_code=" \
                f"'HDFC' and payment_gateway='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        device_serial = result["device_serial"].iloc[0]
        terminal_info_id = result["id"].iloc[0]
        logger.debug(
            f"fetched mid : {mid}, tid : {tid}, device_serial : {device_serial}, terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["cardPaymentEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select bank_code from bin_info where bin='428090'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
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
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(1, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount, order_id, device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(app_driver)
            logger.debug(f"selecting the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_DEBIT_428090")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for the txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            # voiding the txn
            home_page.wait_for_home_page_load()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
            txn_history_page.click_on_void_card_txn()

            time.sleep(3)
            logger.debug(f"Waiting for 3 secs to get data from txn table for void txn")

            query = f"select * from txn where org_code ='{str(org_code)}' AND payment_mode = 'CARD' AND device_serial" \
                    f"='{device_serial}' AND external_ref='{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from the txn for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            txn_created_time = result['created_time'].values[0]
            txn_id = result['id'].values[0]
            rrn = result['rr_number'].values[0]
            auth_code = result['auth_code'].values[0]
            batch_number = result['batch_number'].values[0]
            customer_name = result['customer_name'].values[0]
            amount_db = result['amount'].values[0]
            payment_mode_db = result['payment_mode'].values[0]
            payment_status_db = result['status'].values[0]
            payment_state_db = result['state'].values[0]
            acquirer_code_db = result['acquirer_code'].values[0]
            issuer_code_db = result['issuer_code'].values[0]
            payer_name_db = result['payer_name'].values[0]
            mid_db = result['mid'].values[0]
            tid_db = result['tid'].values[0]
            payment_gateway_db = result['payment_gateway'].values[0]
            settlement_status_db = result['settlement_status'].values[0]
            order_id_db = result['external_ref'].values[0]
            device_serial_db = result['external_ref2'].values[0]
            org_code_db = result['org_code'].values[0]
            payment_card_bin_db = result['payment_card_bin'].values[0]
            payment_card_brand_db = result['payment_card_brand'].values[0]
            payment_card_type_db = result['payment_card_type'].values[0]
            txn_type_db = result['txn_type'].values[0]
            card_txn_type_db = result['card_txn_type'].values[0]
            card_last_four_digit_db = result['card_last_four_digit'].values[0]
            merchant_name = result['merchant_name'].values[0]
            posting_date = result['posting_date'].values[0]

            logger.debug(f"txn_created_time:{txn_created_time}, txn_id:{txn_id}, rrn:{rrn}, auth_code:{auth_code}, "
                         f"batch_number:{batch_number}, customer_name:{customer_name}, amount_db:{amount_db}, "
                         f"payment_mode_db:{payment_mode_db}, payment_status_db:{payment_status_db}, payment_state_db:"
                         f"{payment_state_db}, acquirer_code_db:{acquirer_code_db}, issuer_code_db:{issuer_code_db}, "
                         f"payer_name_db:{payer_name_db}, mid_db:{mid_db}, tid_db:{tid_db}, payment_gateway_db:"
                         f"{payment_gateway_db}, settlement_status_db:{settlement_status_db}, order_id_db:{order_id_db}"
                         f", device_serial_db:{device_serial_db}, org_code_db:{org_code_db}, payment_card_bin_db:"
                         f"{payment_card_bin_db}, payment_card_brand_db:{payment_card_brand_db}, payment_card_type_db:"
                         f"{payment_card_type_db}, txn_type_db:{txn_type_db}, card_txn_type_db:{card_txn_type_db}, "
                         f"card_last_four_digit_db:{card_last_four_digit_db}, merchant_name:{merchant_name}, posting_date:{posting_date}")

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
            date_and_time = date_time_converter.to_app_format(posting_date)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "RAJA",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*0321 EMV with PIN",
                    "order_id": order_id,
                    "device_serial": device_serial
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_status = txn_history_page.fetch_txn_status_text()
                payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_auth_code = txn_history_page.fetch_auth_code_text()
                app_batch_no = txn_history_page.fetch_batch_number_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_mid = txn_history_page.fetch_mid_text()
                app_tid = txn_history_page.fetch_tid_text()
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                app_order_id = txn_history_page.fetch_order_id_text()
                app_device_serial = txn_history_page.fetch_device_serial_text()

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
                    "order_id": app_order_id,
                    "device_serial": app_device_serial
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
                date_and_time = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {
                    "pmt_status": "VOIDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "VOIDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "batch_number": batch_number,
                    "card_last_four_digit": "0321",
                    "customer_name": "RAJA                     /",
                    "device_serial": device_serial,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "RAJA                     /",
                    "pmt_card_bin": "428090",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "card_type": "VISA",
                    "display_pan": "0321",
                    "name_on_card": "RAJA                     /"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_time_api = response["createdTime"]
                batch_number_api = response["batchNumber"]
                card_last_four_digit_api = response["cardLastFourDigit"]
                customer_name_api = response["customerName"]
                device_serial_api = response["deviceSerial"]
                external_ref_number_api = response["externalRefNumber"]
                merchant_name_api = response["merchantName"]
                payer_name_api = response["payerName"]
                payment_card_bin_api = response["paymentCardBin"]
                payment_card_brand_api = response["paymentCardBrand"]
                payment_card_type_api = response["paymentCardType"]
                card_type_api = response["cardType"]
                display_pan_api = response["displayPAN"]
                name_on_card_api = response["nameOnCard"]

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
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_time_api),
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "customer_name": customer_name_api,
                    "device_serial": device_serial_api,
                    "ext_ref_number": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "payer_name": payer_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_type": card_type_api,
                    "display_pan": display_pan_api,
                    "name_on_card": name_on_card_api
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "pmt_state": "VOIDED",
                    "acquirer_code": "HDFC",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "HDFC",
                    "settle_status": "SETTLED",
                    "order_id": order_id,
                    "device_serial": device_serial,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "428090",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "03",
                    "customer_name": "RAJA                     /",
                    "payer_name": "RAJA                     /",
                    "card_last_four_digit": "0321"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db, "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "order_id": order_id_db,
                    "device_serial": device_serial_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "terminal_info_id": terminal_info_id,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "customer_name": customer_name,
                    "payer_name": payer_name_db,
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
                    "txn_amt": "{:.2f}".format(amount),
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                    'AUTH CODE': str(auth_code).strip(), 'BATCH NO': str(batch_number), 'CARD TYPE': 'VISA',
                    'payment_option': 'VOID SALE', 'TID': tid_db
                }
                receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password}, expected_values)
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
def test_common_100_115_185():
    """
    Sub Feature Code: UI_Common_Card_Void_HDFC_EMV_MASTER_DEBIT_222360
    Sub Feature Description:  Performing the EMV void transaction via HDFC PG using MASTER Debit card
    having 16 digit PAN length with pin (bin: 222360)
    TC naming code description:  100: Payment Method, 115: CARD_UI, 185: TC185
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

        query = f"select org_code, name from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code, name from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status='ACTIVE' and acquirer_code=" \
                f"'HDFC' and payment_gateway='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        device_serial = result["device_serial"].iloc[0]
        terminal_info_id = result["id"].iloc[0]
        logger.debug(
            f"fetched mid : {mid}, tid : {tid}, device_serial : {device_serial}, terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["cardPaymentEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select bank_code from bin_info where bin='222360'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
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
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(1, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount, order_id, device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(app_driver)
            logger.debug(f"selecting the card type as : EMV_MASTER_DEBIT_222360")
            card_page.select_cardtype("EMV_MASTER_DEBIT_222360")
            # sleep(2)
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for the txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            # voiding the txn
            home_page.wait_for_home_page_load()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
            txn_history_page.click_on_void_card_txn()

            time.sleep(3)
            logger.debug(f"Waiting for 3 secs to get data from txn table for void txn")

            query = f"select * from txn where org_code ='{str(org_code)}' AND payment_mode = 'CARD' AND device_serial" \
                    f"='{device_serial}' AND external_ref='{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            txn_created_time = result['created_time'].values[0]
            txn_id = result['id'].values[0]
            rrn = result['rr_number'].values[0]
            auth_code = result['auth_code'].values[0]
            batch_number = result['batch_number'].values[0]
            customer_name = result['customer_name'].values[0]
            amount_db = result['amount'].values[0]
            payment_mode_db = result['payment_mode'].values[0]
            payment_status_db = result['status'].values[0]
            payment_state_db = result['state'].values[0]
            acquirer_code_db = result['acquirer_code'].values[0]
            issuer_code_db = result['issuer_code'].values[0]
            payer_name_db = result['payer_name'].values[0]
            mid_db = result['mid'].values[0]
            tid_db = result['tid'].values[0]
            payment_gateway_db = result['payment_gateway'].values[0]
            settlement_status_db = result['settlement_status'].values[0]
            order_id_db = result['external_ref'].values[0]
            device_serial_db = result['external_ref2'].values[0]
            org_code_db = result['org_code'].values[0]
            payment_card_bin_db = result['payment_card_bin'].values[0]
            payment_card_brand_db = result['payment_card_brand'].values[0]
            payment_card_type_db = result['payment_card_type'].values[0]
            txn_type_db = result['txn_type'].values[0]
            card_txn_type_db = result['card_txn_type'].values[0]
            card_last_four_digit_db = result['card_last_four_digit'].values[0]
            merchant_name = result['merchant_name'].values[0]
            posting_date = result['posting_date'].values[0]

            logger.debug(f"txn_created_time:{txn_created_time}, txn_id:{txn_id}, rrn:{rrn}, auth_code:{auth_code}, "
                         f"batch_number:{batch_number}, customer_name:{customer_name}, amount_db:{amount_db}, "
                         f"payment_mode_db:{payment_mode_db}, payment_status_db:{payment_status_db}, payment_state_db:"
                         f"{payment_state_db}, acquirer_code_db:{acquirer_code_db}, issuer_code_db:{issuer_code_db}, "
                         f"payer_name_db:{payer_name_db}, mid_db:{mid_db}, tid_db:{tid_db}, payment_gateway_db:"
                         f"{payment_gateway_db}, settlement_status_db:{settlement_status_db}, order_id_db:{order_id_db}"
                         f", device_serial_db:{device_serial_db}, org_code_db:{org_code_db}, payment_card_bin_db:"
                         f"{payment_card_bin_db}, payment_card_brand_db:{payment_card_brand_db}, payment_card_type_db:"
                         f"{payment_card_type_db}, txn_type_db:{txn_type_db}, card_txn_type_db:{card_txn_type_db}, "
                         f"card_last_four_digit_db:{card_last_four_digit_db}, merchant_name:{merchant_name}, posting_date:{posting_date}")

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
            date_and_time = date_time_converter.to_app_format(posting_date)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "MTIP14 MCD 13A",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*0078 EMV",
                    "order_id": order_id,
                    "device_serial": device_serial
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_status = txn_history_page.fetch_txn_status_text()
                payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_auth_code = txn_history_page.fetch_auth_code_text()
                app_batch_no = txn_history_page.fetch_batch_number_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_mid = txn_history_page.fetch_mid_text()
                app_tid = txn_history_page.fetch_tid_text()
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                app_order_id = txn_history_page.fetch_order_id_text()
                app_device_serial = txn_history_page.fetch_device_serial_text()

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
                    "order_id": app_order_id,
                    "device_serial": app_device_serial
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
                date_and_time = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {
                    "pmt_status": "VOIDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "VOIDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "batch_number": batch_number,
                    "card_last_four_digit": "0078",
                    "customer_name": "MTIP14 MCD 13A",
                    "device_serial": device_serial,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "MTIP14 MCD 13A",
                    "pmt_card_bin": "222360",
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "DEBIT",
                    "card_type": "MasterCard",
                    "display_pan": "0078",
                    "name_on_card": "MTIP14 MCD 13A"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_time_api = response["createdTime"]
                batch_number_api = response["batchNumber"]
                card_last_four_digit_api = response["cardLastFourDigit"]
                customer_name_api = response["customerName"]
                device_serial_api = response["deviceSerial"]
                external_ref_number_api = response["externalRefNumber"]
                merchant_name_api = response["merchantName"]
                payer_name_api = response["payerName"]
                payment_card_bin_api = response["paymentCardBin"]
                payment_card_brand_api = response["paymentCardBrand"]
                payment_card_type_api = response["paymentCardType"]
                card_type_api = response["cardType"]
                display_pan_api = response["displayPAN"]
                name_on_card_api = response["nameOnCard"]

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
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_time_api),
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "customer_name": customer_name_api,
                    "device_serial": device_serial_api,
                    "ext_ref_number": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "payer_name": payer_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_type": card_type_api,
                    "display_pan": display_pan_api,
                    "name_on_card": name_on_card_api
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "pmt_state": "VOIDED",
                    "acquirer_code": "HDFC",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "HDFC",
                    "settle_status": "SETTLED",
                    "order_id": order_id,
                    "device_serial": device_serial,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "222360",
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "DEBIT",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "customer_name": "MTIP14 MCD 13A",
                    "payer_name": "MTIP14 MCD 13A",
                    "card_last_four_digit": "0078"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db, "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "order_id": order_id_db,
                    "device_serial": device_serial_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "terminal_info_id": terminal_info_id,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "customer_name": customer_name,
                    "payer_name": payer_name_db,
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
                    "txn_amt": "{:.2f}".format(amount),
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                    'AUTH CODE': str(auth_code).strip(), 'BATCH NO': str(batch_number), 'CARD TYPE': 'MasterCard',
                    'payment_option': 'VOID SALE', 'TID': tid_db
                }
                receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password}, expected_values)
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
def test_common_100_115_186():
    """
    Sub Feature Code: UI_Common_Card_Void_HDFC_EMV_WITH_PIN_VISA_CREDIT_417666
    Sub Feature Description:  Performing the void transaction via HDFC PG using EMV With Pin VISA Credit card
    having 16 digit PAN length with pin (bin: 417666)
    TC naming code description:  100: Payment Method, 115: CARD_UI, 186: TC186
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

        query = f"select org_code, name from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code, name from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status='ACTIVE' and acquirer_code=" \
                f"'HDFC' and payment_gateway='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        device_serial = result["device_serial"].iloc[0]
        terminal_info_id = result["id"].iloc[0]
        logger.debug(
            f"fetched mid : {mid}, tid : {tid}, device_serial : {device_serial}, terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["cardPaymentEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
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
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(1, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount, order_id, device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(app_driver)
            logger.debug(f"selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype("EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for the txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            # voiding the txn
            home_page.wait_for_home_page_load()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
            txn_history_page.click_on_void_card_txn()

            time.sleep(3)
            logger.debug(f"Waiting for 3 secs to get data from txn table for void txn")

            query = f"select * from txn where org_code ='{str(org_code)}' AND payment_mode = 'CARD' AND device_serial" \
                    f"='{device_serial}' AND external_ref='{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            txn_created_time = result['created_time'].values[0]
            txn_id = result['id'].values[0]
            rrn = result['rr_number'].values[0]
            auth_code = result['auth_code'].values[0]
            batch_number = result['batch_number'].values[0]
            customer_name = result['customer_name'].values[0]
            amount_db = result['amount'].values[0]
            payment_mode_db = result['payment_mode'].values[0]
            payment_status_db = result['status'].values[0]
            payment_state_db = result['state'].values[0]
            acquirer_code_db = result['acquirer_code'].values[0]
            issuer_code_db = result['issuer_code'].values[0]
            payer_name_db = result['payer_name'].values[0]
            mid_db = result['mid'].values[0]
            tid_db = result['tid'].values[0]
            payment_gateway_db = result['payment_gateway'].values[0]
            settlement_status_db = result['settlement_status'].values[0]
            order_id_db = result['external_ref'].values[0]
            device_serial_db = result['external_ref2'].values[0]
            org_code_db = result['org_code'].values[0]
            payment_card_bin_db = result['payment_card_bin'].values[0]
            payment_card_brand_db = result['payment_card_brand'].values[0]
            payment_card_type_db = result['payment_card_type'].values[0]
            txn_type_db = result['txn_type'].values[0]
            card_txn_type_db = result['card_txn_type'].values[0]
            card_last_four_digit_db = result['card_last_four_digit'].values[0]
            merchant_name = result['merchant_name'].values[0]
            posting_date = result['posting_date'].values[0]

            logger.debug(f"txn_created_time:{txn_created_time}, txn_id:{txn_id}, rrn:{rrn}, auth_code:{auth_code}, "
                         f"batch_number:{batch_number}, customer_name:{customer_name}, amount_db:{amount_db}, "
                         f"payment_mode_db:{payment_mode_db}, payment_status_db:{payment_status_db}, payment_state_db:"
                         f"{payment_state_db}, acquirer_code_db:{acquirer_code_db}, issuer_code_db:{issuer_code_db}, "
                         f"payer_name_db:{payer_name_db}, mid_db:{mid_db}, tid_db:{tid_db}, payment_gateway_db:"
                         f"{payment_gateway_db}, settlement_status_db:{settlement_status_db}, order_id_db:{order_id_db}"
                         f", device_serial_db:{device_serial_db}, org_code_db:{org_code_db}, payment_card_bin_db:"
                         f"{payment_card_bin_db}, payment_card_brand_db:{payment_card_brand_db}, payment_card_type_db:"
                         f"{payment_card_type_db}, txn_type_db:{txn_type_db}, card_txn_type_db:{card_txn_type_db}, "
                         f"card_last_four_digit_db:{card_last_four_digit_db}, merchant_name:{merchant_name}, posting_date:{posting_date}")

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
            date_and_time = date_time_converter.to_app_format(posting_date)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "txn_amt": "{:.2f}".format(amount),
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
                    "card_type_desc": "*0102 EMV with PIN",
                    "order_id": order_id,
                    "device_serial": device_serial
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_status = txn_history_page.fetch_txn_status_text()
                payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_auth_code = txn_history_page.fetch_auth_code_text()
                app_batch_no = txn_history_page.fetch_batch_number_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_mid = txn_history_page.fetch_mid_text()
                app_tid = txn_history_page.fetch_tid_text()
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                app_order_id = txn_history_page.fetch_order_id_text()
                app_device_serial = txn_history_page.fetch_device_serial_text()

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
                    "order_id": app_order_id,
                    "device_serial": app_device_serial
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
                date_and_time = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {
                    "pmt_status": "VOIDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "VOIDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "batch_number": batch_number,
                    "card_last_four_digit": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "device_serial": device_serial,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "L3TEST/CARD0010",
                    "pmt_card_bin": "417666",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_type": "VISA",
                    "display_pan": "0102",
                    "name_on_card": "L3TEST/CARD0010"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_time_api = response["createdTime"]
                batch_number_api = response["batchNumber"]
                card_last_four_digit_api = response["cardLastFourDigit"]
                customer_name_api = response["customerName"]
                device_serial_api = response["deviceSerial"]
                external_ref_number_api = response["externalRefNumber"]
                merchant_name_api = response["merchantName"]
                payer_name_api = response["payerName"]
                payment_card_bin_api = response["paymentCardBin"]
                payment_card_brand_api = response["paymentCardBrand"]
                payment_card_type_api = response["paymentCardType"]
                card_type_api = response["cardType"]
                display_pan_api = response["displayPAN"]
                name_on_card_api = response["nameOnCard"]

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
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_time_api),
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "customer_name": customer_name_api,
                    "device_serial": device_serial_api,
                    "ext_ref_number": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "payer_name": payer_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_type": card_type_api,
                    "display_pan": display_pan_api,
                    "name_on_card": name_on_card_api
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "pmt_state": "VOIDED",
                    "acquirer_code": "HDFC",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "HDFC",
                    "settle_status": "SETTLED",
                    "order_id": order_id,
                    "device_serial": device_serial,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "03",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "card_last_four_digit": "0102"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db, "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "order_id": order_id_db,
                    "device_serial": device_serial_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "terminal_info_id": terminal_info_id,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "customer_name": customer_name,
                    "payer_name": payer_name_db,
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
                    "txn_amt": "{:.2f}".format(amount),
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                    'AUTH CODE': str(auth_code).strip(), 'BATCH NO': str(batch_number), 'CARD TYPE': 'VISA',
                    'payment_option': 'VOID SALE', 'TID': tid_db
                }
                receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password}, expected_values)
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
def test_common_100_115_187():
    """
    Sub Feature Code: UI_Common_Card_Void_HDFC_EMV_RUPAY_DEBIT_608326
    Sub Feature Description:  Performing the EMV void transaction via HDFC PG using RUPAY Debit card
    having 16 digit PAN length with pin (bin: 608326)
    TC naming code description:  100: Payment Method, 115: CARD_UI, 014: TC014
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

        query = f"select org_code, name from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code, name from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status='ACTIVE' and acquirer_code=" \
                f"'HDFC' and payment_gateway='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result : {result}")
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        device_serial = result["device_serial"].iloc[0]
        terminal_info_id = result["id"].iloc[0]
        logger.debug(
            f"fetched mid : {mid}, tid : {tid}, device_serial : {device_serial}, terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["cardPaymentEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select bank_code from bin_info where bin='608326'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
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
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(1, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount, order_id, device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(app_driver)
            logger.debug(f"selecting the card type as : EMV_RUPAY_DEBIT_608326")
            card_page.select_cardtype("EMV_RUPAY_DEBIT_608326")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for the txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            # voiding the txn
            home_page.wait_for_home_page_load()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
            txn_history_page.click_on_void_card_txn()

            time.sleep(3)
            logger.debug(f"Waiting for 3 secs to get data from txn table for void txn")

            query = f"select * from txn where org_code ='{str(org_code)}' AND payment_mode = 'CARD' AND device_serial" \
                    f"='{device_serial}' AND external_ref='{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            txn_created_time = result['created_time'].values[0]
            txn_id = result['id'].values[0]
            rrn = result['rr_number'].values[0]
            auth_code = result['auth_code'].values[0]
            batch_number = result['batch_number'].values[0]
            customer_name = result['customer_name'].values[0]
            amount_db = result['amount'].values[0]
            payment_mode_db = result['payment_mode'].values[0]
            payment_status_db = result['status'].values[0]
            payment_state_db = result['state'].values[0]
            acquirer_code_db = result['acquirer_code'].values[0]
            issuer_code_db = result['issuer_code'].values[0]
            payer_name_db = result['payer_name'].values[0]
            mid_db = result['mid'].values[0]
            tid_db = result['tid'].values[0]
            payment_gateway_db = result['payment_gateway'].values[0]
            settlement_status_db = result['settlement_status'].values[0]
            order_id_db = result['external_ref'].values[0]
            device_serial_db = result['external_ref2'].values[0]
            org_code_db = result['org_code'].values[0]
            payment_card_bin_db = result['payment_card_bin'].values[0]
            payment_card_brand_db = result['payment_card_brand'].values[0]
            payment_card_type_db = result['payment_card_type'].values[0]
            txn_type_db = result['txn_type'].values[0]
            card_txn_type_db = result['card_txn_type'].values[0]
            card_last_four_digit_db = result['card_last_four_digit'].values[0]
            merchant_name = result['merchant_name'].values[0]
            posting_date = result['posting_date'].values[0]

            logger.debug(f"txn_created_time:{txn_created_time}, txn_id:{txn_id}, rrn:{rrn}, auth_code:{auth_code}, "
                         f"batch_number:{batch_number}, customer_name:{customer_name}, amount_db:{amount_db}, "
                         f"payment_mode_db:{payment_mode_db}, payment_status_db:{payment_status_db}, payment_state_db:"
                         f"{payment_state_db}, acquirer_code_db:{acquirer_code_db}, issuer_code_db:{issuer_code_db}, "
                         f"payer_name_db:{payer_name_db}, mid_db:{mid_db}, tid_db:{tid_db}, payment_gateway_db:"
                         f"{payment_gateway_db}, settlement_status_db:{settlement_status_db}, order_id_db:{order_id_db}"
                         f", device_serial_db:{device_serial_db}, org_code_db:{org_code_db}, payment_card_bin_db:"
                         f"{payment_card_bin_db}, payment_card_brand_db:{payment_card_brand_db}, payment_card_type_db:"
                         f"{payment_card_type_db}, txn_type_db:{txn_type_db}, card_txn_type_db:{card_txn_type_db}, "
                         f"card_last_four_digit_db:{card_last_four_digit_db}, merchant_name:{merchant_name}, posting_date:{posting_date}")

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
            date_and_time = date_time_converter.to_app_format(posting_date)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "RUPAY CARD IMAGE 02",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*0025 EMV",
                    "order_id": order_id,
                    "device_serial": device_serial
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_status = txn_history_page.fetch_txn_status_text()
                payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_auth_code = txn_history_page.fetch_auth_code_text()
                app_batch_no = txn_history_page.fetch_batch_number_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_mid = txn_history_page.fetch_mid_text()
                app_tid = txn_history_page.fetch_tid_text()
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                app_order_id = txn_history_page.fetch_order_id_text()
                app_device_serial = txn_history_page.fetch_device_serial_text()

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
                    "order_id": app_order_id,
                    "device_serial": app_device_serial
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
                date_and_time = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {
                    "pmt_status": "VOIDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "VOIDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "batch_number": batch_number,
                    "card_last_four_digit": "0025",
                    "customer_name": "RUPAY CARD IMAGE 02      /",
                    "device_serial": device_serial,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "RUPAY CARD IMAGE 02      /",
                    "pmt_card_bin": "608326",
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "card_type": "RUPAY",
                    "display_pan": "0025",
                    "name_on_card": "RUPAY CARD IMAGE 02      /"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_time_api = response["createdTime"]
                batch_number_api = response["batchNumber"]
                card_last_four_digit_api = response["cardLastFourDigit"]
                customer_name_api = response["customerName"]
                device_serial_api = response["deviceSerial"]
                external_ref_number_api = response["externalRefNumber"]
                merchant_name_api = response["merchantName"]
                payer_name_api = response["payerName"]
                payment_card_bin_api = response["paymentCardBin"]
                payment_card_brand_api = response["paymentCardBrand"]
                payment_card_type_api = response["paymentCardType"]
                card_type_api = response["cardType"]
                display_pan_api = response["displayPAN"]
                name_on_card_api = response["nameOnCard"]

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
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_time_api),
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "customer_name": customer_name_api,
                    "device_serial": device_serial_api,
                    "ext_ref_number": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "payer_name": payer_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_type": card_type_api,
                    "display_pan": display_pan_api,
                    "name_on_card": name_on_card_api
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "pmt_state": "VOIDED",
                    "acquirer_code": "HDFC",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "HDFC",
                    "settle_status": "SETTLED",
                    "order_id": order_id,
                    "device_serial": device_serial,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "608326",
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "02",
                    "customer_name": "RUPAY CARD IMAGE 02      /",
                    "payer_name": "RUPAY CARD IMAGE 02      /",
                    "card_last_four_digit": "0025"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db, "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "order_id": order_id_db,
                    "device_serial": device_serial_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "terminal_info_id": terminal_info_id,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "customer_name": customer_name,
                    "payer_name": payer_name_db,
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
                    "txn_amt": "{:.2f}".format(amount),
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn), 'SALE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                    'AUTH CODE': str(auth_code).strip(), 'BATCH NO': str(batch_number), 'CARD TYPE': 'RUPAY',
                    'payment_option': 'VOID SALE', 'TID': tid_db
                }
                receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password}, expected_values)
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