import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, ResourceAssigner, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_110_052():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Success_Via_BQRV4_UPI_Success_Callback_MultiAcc_HDFC_MINTOAK
    Sub Feature Description: Multi Account - Performing a Authorized Txn using BQRV4_UPI Success callback for HDFC_MINTOAK
    TC naming code description: 100: Payment Method 110: MultiAcc_BQR, 052: TC052
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

        query = f"select org_code from org_employee where username='{str(app_username)}'"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username, portal_pw=portal_password,
                                                           bank_code_bqr='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(org_code=org_code,
                                                                                       portal_un=portal_username,
                                                                                       portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code}
                                                  )
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch details from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        terminal_info_id = result["terminal_info_id"].values[0]
        bqr_mc_id = result["id"].values[0]
        bqr_m_pan = result["merchant_pan"].values[0]
        bqr_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched bqr_acc_label_id : {bqr_acc_label_id}")
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")
        upi_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched upi_acc_label_id : {upi_acc_label_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and app_password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(431, 500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}'"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query fetched result is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generated mtxnId: {mtxn_id}")
            issuer_ref_number = str(random.randint(10000000, 99999999))
            logger.debug(f"Generated : {issuer_ref_number}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")

            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetched auth code from txn table: {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetched rrn from txn table: {rrn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetched created time from txn table: {created_time}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {label_ids}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"Fetched amount from txn table: {amount_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"Fetched payment mode from txn table: {payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"Fetched payment status from txn table: {payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"Fetched payment_state from txn table: {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"Fetched acquirer_code from txn table: {acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetched bank name from txn table: {bank_name_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"Fetched mid from txn table: {mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"Fetched tid from txn table: {tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"Fetched payment gateway from txn table: {payment_gateway_db}")
            rr_number_db = result["rr_number"].values[0]
            logger.debug(f"Fetched rrn from txn table: {acquirer_code_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"Fetched settlement status from txn table: {settlement_status_db}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetched posting date from txn table: {posting_date}")

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "msg": app_payment_msg,
                    "date": app_date_and_time
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
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "account_label": str(account_label_name)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password}
                                                          )
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"fetched status from api : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"fetched amount from api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"fetched payment mode from api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"fetched payment state from api : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"fetched rrn from api : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"fetched settle status from api : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"fetched issuer code from api : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"fetched acquirer code from api : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"fetched org code from api : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"fetched mid from api : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"fetched tid from api : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"fetched txn type from api : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"fetched date from api : {date_api}")
                account_label_name_api = response["accountLabel"]
                logger.debug(f"fetched account label from api : {account_label_name_api}")

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
                    "date": date_time_converter.db_datetime(posting_date),
                    "account_label": str(account_label_name_api)
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
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_name": "HDFC Bank",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "MINTOAK",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "upi_pmt_status": "AUTHORIZED",
                    "upi_txn_type": "PAY_BQR",
                    "upi_mc_id": upi_mc_id,
                    "upi_bank_code": "HDFC_MINTOAK",
                    "upi_acc_label_id": str(upi_acc_label_id),
                    "bqr_acc_label_id": str(bqr_acc_label_id),
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"fetched upi status from db : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"fetched upi txn type from db : {upi_txn_type_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"fetched upi mc id from db : {upi_mc_id_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"fetched upi bank code from db : {upi_bank_code_db}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_name": bank_name_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rr_number_db,
                    "settle_status": settlement_status_db,
                    "upi_pmt_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_acc_label_id": str(label_ids),
                    "bqr_acc_label_id": str(label_ids),
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn),
                    "acc_label": str(account_label_name)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code_portal = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                labels = transaction_details[0]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "acc_label": labels
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }
                receipt_validator.perform_charge_slip_validations(txn_id, {
                    "username": app_username,
                    "password": app_password}, expected_charge_slip_values)
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
def test_common_100_110_053():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Failed_Via_BQRV4_UPI_Failed_Callback_MultiAcc_HDFC_MINTOAK
    Sub Feature Description: Multi Account - Performing a Failed Txn using BQRV4_UPI Failed callback for HDFC_MINTOAK
    TC naming code description: 100: Payment Method 110: MultiAcc_BQR, 053: TC053
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

        query = f"select org_code from org_employee where username='{str(app_username)}'"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username, portal_pw=portal_password,
                                                           bank_code_bqr='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(org_code=org_code,
                                                                                       portal_un=portal_username,
                                                                                       portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code}
                                                  )
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        terminal_info_id = result["terminal_info_id"].values[0]
        bqr_mc_id = result["id"].values[0]
        bqr_m_pan = result["merchant_pan"].values[0]
        bqr_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched bqr_acc_label_id : {bqr_acc_label_id}")
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")
        upi_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched upi_acc_label_id : {upi_acc_label_id}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and app_password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(450, 500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}'"
            logger.debug(f"Query to fetch data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query fetched result is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating mtxn_id : {mtxn_id}")
            issuer_ref_number = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating issuer_ref_number : {issuer_ref_number}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_failed')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")

            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetched auth code from txn table: {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetched rrn from txn table: {rrn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetched created time from txn table: {created_time}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {label_ids}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"Fetched amount from txn table: {amount_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"Fetched payment mode from txn table: {payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"Fetched payment status from txn table: {payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"Fetched payment_state from txn table: {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"Fetched acquirer_code from txn table: {acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetched bank name from txn table: {bank_name_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"Fetched mid from txn table: {mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"Fetched tid from txn table: {tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"Fetched payment gateway from txn table: {payment_gateway_db}")
            rr_number_db = result["rr_number"].values[0]
            logger.debug(f"Fetched rrn from txn table: {acquirer_code_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"Fetched settlement status from txn table: {settlement_status_db}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetched posting date from txn table: {posting_date}")

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "msg": "PAYMENT FAILED",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                payment_page.click_on_back_btn()
                home_page.click_on_back_btn_enter_amt_page()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "msg": app_payment_msg,
                    "date": app_date_and_time
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
                # --------------------------------------------------------------------------------------------
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "account_label": str(account_label_name)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password}
                                                          )
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetched status from api : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Fetched amount from api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetched payment mode from api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetched state from api : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetched rrn from api : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetched settlement status from api : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetched isuer code from api : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetched acquirer code from api : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetched org code from api : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetched mid from api : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetched tid from api : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetched txn type from api : {txn_type_api}")
                account_label_name_api = response["accountLabel"]
                logger.debug(f"Fetched account label from api : {account_label_name_api}")

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
                    "date": date_time_converter.db_datetime(posting_date),
                    "account_label": str(account_label_name_api)
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
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_name": "HDFC Bank",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "MINTOAK",
                    "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "upi_pmt_status": "FAILED",
                    "upi_txn_type": "PAY_BQR",
                    "upi_mc_id": upi_mc_id,
                    "upi_bank_code": "HDFC_MINTOAK",
                    "upi_acc_label_id": str(upi_acc_label_id),
                    "bqr_acc_label_id": str(bqr_acc_label_id),
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"Fetched upi status from db : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetched upi txn type from db : {upi_txn_type_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"Fetched upi mc id from db : {upi_mc_id_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetched upi bank code from db : {upi_bank_code_db}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_name": bank_name_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rr_number_db,
                    "settle_status": settlement_status_db,
                    "upi_pmt_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_acc_label_id": str(label_ids),
                    "bqr_acc_label_id": str(label_ids),
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn),
                    "acc_label": str(account_label_name)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code_portal = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                labels = transaction_details[0]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "acc_label": labels
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
