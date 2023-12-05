import random
import sys
from time import sleep
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
def test_common_100_115_024():
    """
    Sub Feature Code: UI_Common_Card_Sale_FDC_CTLS_WITH_PIN_RUPAY_DEBIT_608326
    Sub Feature Description:  Performing the EMV sale transaction via FDC PG using CTLS With Pin RUPAY Debit card
    having 16 digit PAN length with pin (bin: 608326)
    TC naming code description:  100: Payment Method, 115: CARD_UI, 024: TC024
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
                f"'ICICI' and payment_gateway='FDC'"
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
            logger.debug(f"selecting the card type as : CTLS_WITH_PIN_RUPAY_DEBIT_608326")
            card_page.select_cardtype("CTLS_WITH_PIN_RUPAY_DEBIT_608326")
            # sleep(2)
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code ='{str(org_code)}' AND payment_mode = 'CARD' AND device_serial" \
                    f"='{device_serial}' AND external_ref='{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
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
                         f"card_last_four_digit_db:{card_last_four_digit_db}, merchant_name:{merchant_name}, "
                         f"posting_date:{posting_date}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "RUPAY CARD IMAGE 01",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*0017 CTLS",
                    "order_id": order_id,
                    "device_serial": device_serial
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "ICICI",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "batch_number": batch_number,
                    "card_last_four_digit": "0017",
                    "customer_name": "RUPAY CARD IMAGE 01      /",
                    "device_serial": device_serial,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "RUPAY CARD IMAGE 01      /",
                    "pmt_card_bin": "608326",
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "card_type": "RUPAY",
                    "display_pan": "0017",
                    "name_on_card": "RUPAY CARD IMAGE 01      /"
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "ICICI",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "FDC",
                    "settle_status": "PENDING",
                    "order_id": order_id,
                    "device_serial": device_serial,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "608326",
                    "pmt_card_brand": "RUPAY",
                    "pmt_card_type": "DEBIT",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "91",
                    "customer_name": "RUPAY CARD IMAGE 01      /",
                    "payer_name": "RUPAY CARD IMAGE 01      /",
                    "card_last_four_digit": "0017"
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
                    "pmt_status": "AUTHORIZED",
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
                    'payment_option': 'DEBIT SALE', 'TID': tid_db
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
def test_common_100_115_025():
    """
    Sub Feature Code: UI_Common_Card_Sale_FDC_CTLS_VISA_CREDIT_417666
    Sub Feature Description:  Performing the EMV sale transaction via FDC PG using CTLS VISA Credit card
    having 16 digit PAN length without pin (bin: 417666)
    TC naming code description:  100: Payment Method, 115: CARD_UI, 025: TC025
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
                f"'ICICI' and payment_gateway='FDC'"
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
            logger.debug(f"selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype("CTLS_VISA_CREDIT_417666")
            # sleep(2)
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code ='{str(org_code)}' AND payment_mode = 'CARD' AND device_serial" \
                    f"='{device_serial}' AND external_ref='{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
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
                         f"card_last_four_digit_db:{card_last_four_digit_db}, merchant_name:{merchant_name}, "
                         f"posting_date:{posting_date}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    # "customer_name": "L3TEST",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*0018 CTLS",
                    "order_id": order_id,
                    "device_serial": device_serial
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)

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
                # app_customer_name = txn_history_page.fetch_customer_name_text()
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
                    # "customer_name": app_customer_name,
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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "ICICI",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "batch_number": batch_number,
                    "card_last_four_digit": "0018",
                    # "customer_name": "L3TEST/CARD1045",
                    "device_serial": device_serial,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    # "payer_name": "L3TEST/CARD1045",
                    "pmt_card_bin": "417666",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_type": "VISA",
                    "display_pan": "0018",
                    # "name_on_card": "L3TEST/CARD1045"
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
                # customer_name_api = response["customerName"]
                device_serial_api = response["deviceSerial"]
                external_ref_number_api = response["externalRefNumber"]
                merchant_name_api = response["merchantName"]
                # payer_name_api = response["payerName"]
                payment_card_bin_api = response["paymentCardBin"]
                payment_card_brand_api = response["paymentCardBrand"]
                payment_card_type_api = response["paymentCardType"]
                card_type_api = response["cardType"]
                display_pan_api = response["displayPAN"]
                # name_on_card_api = response["nameOnCard"]

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
                    # "customer_name": customer_name_api,
                    "device_serial": device_serial_api,
                    "ext_ref_number": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    # "payer_name": payer_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_type": card_type_api,
                    "display_pan": display_pan_api,
                    # "name_on_card": name_on_card_api
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "ICICI",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "FDC",
                    "settle_status": "PENDING",
                    "order_id": order_id,
                    "device_serial": device_serial,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "91",
                    # "customer_name": "L3TEST/CARD1045",
                    # "payer_name": "L3TEST/CARD1045",
                    "card_last_four_digit": "0018"
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
                    # "customer_name": customer_name,
                    # "payer_name": payer_name_db,
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
                    'payment_option': 'SALE', 'TID': tid_db
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
def test_common_100_115_026():
    """
    Sub Feature Code: UI_Common_Card_Sale_FDC_CTLS_MASTER_CREDIT_541333
    Sub Feature Description:  Performing the EMV sale transaction via FDC PG using CTLS MASTER Credit card
    having 16 digit PAN length without pin (bin: 541333)
    TC naming code description:  100: Payment Method, 115: CARD_UI, 026: TC026
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
                f"'ICICI' and payment_gateway='FDC'"
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

        query = f"select bank_code from bin_info where bin='541333'"
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
            logger.debug(f"selecting the card type as : CTLS_MASTER_CREDIT_541333")
            card_page.select_cardtype("CTLS_MASTER_CREDIT_541333")
            sleep(2)
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code ='{str(org_code)}' AND payment_mode = 'CARD' AND device_serial" \
                    f"='{device_serial}' AND external_ref='{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
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
                         f"card_last_four_digit_db:{card_last_four_digit_db}, merchant_name:{merchant_name}, "
                         f"posting_date:{posting_date}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "MASTERCARD",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*1034 CTLS",
                    "order_id": order_id,
                    "device_serial": device_serial
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "ICICI",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "batch_number": batch_number,
                    "card_last_four_digit": "1034",
                    "customer_name": "MASTERCARD/CARDHOLDER",
                    "device_serial": device_serial,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "MASTERCARD/CARDHOLDER",
                    "pmt_card_bin": "541333",
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "card_type": "MasterCard",
                    "display_pan": "1034",
                    "name_on_card": "MASTERCARD/CARDHOLDER"
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "ICICI",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "FDC",
                    "settle_status": "PENDING",
                    "order_id": order_id,
                    "device_serial": device_serial,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "541333",
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "91",
                    "customer_name": "MASTERCARD/CARDHOLDER",
                    "payer_name": "MASTERCARD/CARDHOLDER",
                    "card_last_four_digit": "1034"
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
                    "pmt_status": "AUTHORIZED",
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
                    'payment_option': 'SALE', 'TID': tid_db
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
def test_common_100_115_027():
    """
    Sub Feature Code: UI_Common_Card_Sale_FDC_CTLS_WITH_PIN_MASTER_CREDIT_541333
    Sub Feature Description:  Performing the EMV sale transaction via FDC PG using CTLS with pin MASTER Credit card
    having 16 digit PAN length with pin (bin: 541333)
    TC naming code description:  100: Payment Method, 115: CARD_UI, 027: TC027
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
                f"'ICICI' and payment_gateway='FDC'"
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

        query = f"select bank_code from bin_info where bin='541333'"
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
            logger.debug(f"selecting the card type as : CTLS_WITH_PIN_MASTER_CREDIT_541333")
            card_page.select_cardtype("CTLS_WITH_PIN_MASTER_CREDIT_541333")
            sleep(2)
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code ='{str(org_code)}' AND payment_mode = 'CARD' AND device_serial" \
                    f"='{device_serial}' AND external_ref='{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
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
                         f"card_last_four_digit_db:{card_last_four_digit_db}, merchant_name:{merchant_name}, "
                         f"posting_date:{posting_date}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "MASTERCARD",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*1034 CTLS",
                    "order_id": order_id,
                    "device_serial": device_serial
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "ICICI",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "batch_number": batch_number,
                    "card_last_four_digit": "1034",
                    "customer_name": "MASTERCARD/CARDHOLDER",
                    "device_serial": device_serial,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "MASTERCARD/CARDHOLDER",
                    "pmt_card_bin": "541333",
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "card_type": "MasterCard",
                    "display_pan": "1034",
                    "name_on_card": "MASTERCARD/CARDHOLDER"
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "ICICI",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "FDC",
                    "settle_status": "PENDING",
                    "order_id": order_id,
                    "device_serial": device_serial,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "541333",
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "91",
                    "customer_name": "MASTERCARD/CARDHOLDER",
                    "payer_name": "MASTERCARD/CARDHOLDER",
                    "card_last_four_digit": "1034"
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
                    "pmt_status": "AUTHORIZED",
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
                    'payment_option': 'SALE', 'TID': tid_db
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
def test_common_100_115_211():
    """
    Sub Feature Code: UI_Common_Card_Sale_FDC_EMV_VISA_DebitCard_Without_Pin_476173
    Sub Feature Description: Performing the EMV sale transaction via FDC PG using VISA Debit card having
    16 digit PAN length without pin (bin:476173)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 211: TC211
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
                "acquirer_code='ICICI' and payment_gateway='FDC'"
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
            amount = random.randint(1, 400)
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
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info(f"Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_VISA_DEBIT_476173")
            card_page.select_cardtype(text="EMV_VISA_DEBIT_476173")
            logger.debug(f"Selected the card type as : EMV_VISA_DEBIT_476173")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
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
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, payment_gateway : {payment_gateway}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Query result, batch_number : {batch_number}")
            total_amount = result['amount'].values[0]
            logger.debug(f"Query result, amount : {total_amount}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Query result, payment_card_brand : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, payment_card_type : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Query result, card_last_four_digit : {card_last_four_digit}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode : {payment_mode}")
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
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, posting_date : {posting_date}")
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
                date_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_time,
                    "device_serial": device_serial,
                    "batch_number": batch_number,
                    "card_type_desc": "*0250 EMV",
                    "mid": mid,
                    "tid": tid,
                    "customer_name": "L3TEST"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
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
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the txn : {txn_id}, {app_card_type_desc}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the txn : {txn_id}, {app_tid}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {txn_id}, {app_customer_name}")

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
                    "card_type_desc": app_card_type_desc,
                    "mid": app_mid,
                    "tid": app_tid,
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
                date_time = date_time_converter.db_datetime(date_from_db=created_time)
                expected_api_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "ICICI",
                    "settle_status": "PENDING",
                    "rrn": rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "org_code": org_code,
                    "batch_number": batch_number,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "date": date_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "EMV",
                    "auth_code": auth_code,
                    "card_last_four_digit": "0250",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "476173",
                    "card_type": "VISA",
                    "display_pan": "0250",
                    "customer_name": "L3TEST/CARD0025",
                    "payer_name": "L3TEST/CARD0025",
                    "name_on_card": "L3TEST/CARD0025"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount : {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode : {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status : {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state : {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid : {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid : {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status : {api_settle_status}")
                api_rrn = response.get('rrNumber')
                logger.debug(f"From response fetch rrn : {api_rrn}")
                api_issuer_code = response.get('issuerCode')
                logger.debug(f"From response fetch issuer_code : {api_issuer_code}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type : {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code : {api_org_code}")
                api_batch_number = response.get('batchNumber')
                logger.debug(f"From response fetch batch_number : {api_batch_number}")
                api_pmt_card_brand = response.get('paymentCardBrand')
                logger.debug(f"From response fetch payment_card_brand : {api_pmt_card_brand}")
                api_pmt_card_type = response.get('paymentCardType')
                logger.debug(f"From response fetch payment_card_type : {api_pmt_card_type}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time : {api_date_time}")
                api_device_serial = response.get('deviceSerial')
                logger.debug(f"From response fetch device_serial : {api_device_serial}")
                api_card_txn_type_desc = response.get('cardTxnTypeDesc')
                logger.debug(f"From response fetch card_txn_type_desc : {api_card_txn_type_desc}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name : {api_merchant_name}")
                api_card_last_four_digit = response.get('cardLastFourDigit')
                logger.debug(f"From response fetch card_last_four_digit : {api_card_last_four_digit}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number : {api_ext_ref_number}")
                api_pmt_card_bin = response.get('paymentCardBin')
                logger.debug(f"From response fetch payment_card_bin : {api_pmt_card_bin}")
                api_display_pan = response.get('displayPAN')
                logger.debug(f"From response fetch display_pan : {api_display_pan}")
                api_auth_code = response.get('authCode')
                logger.debug(f"From response fetch auth_code : {api_auth_code}")
                api_card_type = response.get('cardType')
                logger.debug(f"From response fetch card_type : {api_card_type}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name : {api_customer_name}")
                api_payer_name = response.get('payerName')
                logger.debug(f"From response fetch payer_name : {api_payer_name}")
                api_name_on_card = response.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card : {api_name_on_card}")

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
                    "batch_number": api_batch_number,
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
                    "card_txn_type_desc": api_card_txn_type_desc,
                    "auth_code": api_auth_code,
                    "card_last_four_digit": api_card_last_four_digit,
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "pmt_card_bin": api_pmt_card_bin,
                    "card_type": api_card_type,
                    "display_pan": api_display_pan,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "acquirer_code": "ICICI",
                    "issuer_code": issuer_code,
                    "payer_name": "L3TEST/CARD0025",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "FDC",
                    "txn_type": "CHARGE",
                    "settle_status": "PENDING",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "476173",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "02",
                    "card_last_four_digit": "0250",
                    "customer_name": "L3TEST/CARD0025"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": total_amount,
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
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "terminal_info_id": terminal_info_id_txn,
                    "card_txn_type": card_txn_type,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name
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
                expected_portal_values = {
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_time,
                    "pmt_status": "AUTHORIZED"
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[0]['Total Amount']
                logger.info(f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_auth_code = transaction_details[0]['Auth Code']
                logger.info(f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")
                portal_rrn = transaction_details[0]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[0]['Status']
                logger.info(f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")

                actual_portal_values = {
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "auth_code": portal_auth_code,
                    "rrn": portal_rrn,
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": rrn,
                    "AUTH CODE": str(auth_code).strip(),
                    "CARD TYPE": "VISA",
                    "BATCH NO": batch_number,
                    "TID": tid,
                    "payment_option": "DEBIT SALE"
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
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