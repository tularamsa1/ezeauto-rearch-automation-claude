import random
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_113_015():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_StaticQR_Callback_Success_Via_HDFC_MINTOAK_MultiAcc_ActiveLabel
    Sub Feature Description: Multi Account - Verifying a Static QR BQR success callback via HDFC_MINTOAK when label is active
    TC naming code description: 100: Payment Method, 113: MultiAcc_StaticQR, 015: TC015
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table: {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(org_code,
                                                                                       portal_un=portal_username,
                                                                                       portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetching account_label_name : {account_label_name}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' and bank_code = 'HDFC_MINTOAK' and " \
                f"acc_label_id=(select id from label where name='{account_label_name}' and org_code ='{org_code}')"
        logger.debug(f"query to fetch data from bharatqr_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
        mid = result["mid"].values[0]
        logger.debug(f"Value of mid from bqr_merchant_config table: {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Value of tid from bqr_merchant_config table: {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"Value of terminal_info_id from bqr_merchant_config table: {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"Value of bqr_mc_id from bharatqr_merchant_config table: {bqr_mc_id}")
        bqr_mc_pan = str(result["merchant_pan"].values[0])
        logger.debug(f"Value of bqr_merchant_pan from bharatqr_merchant_config table: {bqr_mc_pan}")
        bqr_acc_label_id = str(result['acc_label_id'].values[0])
        logger.debug(f"Value of bqr_acc_label_id from bharatqr_merchant_config table: {bqr_acc_label_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(251, 300)
            logger.info(f"Generated random amount is: {amount}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the bqr static qr generation : {response}")
            publish_id = response["publishId"]
            logger.debug(f"Fetching publish_id from the bqr static qr generate api, publish_id : {publish_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            txn_id = "231129064936760E" + str(random.randint(10000000, 999999999))
            logger.info(f"Generated txn_id is: {txn_id}")
            m_txn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.info(f"Generated m_txn_id is: {m_txn_id}")
            rrn = str(random.randint(10000000, 99999999))
            logger.info(f"Generated rrn is: {rrn}")

            logger.debug(f"Performing encryption api call")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = m_txn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"
            api_details_encryption['RequestBody']['payload']['description'] = "Static QR"
            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")

            logger.debug(f"Performing callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for confirming mintoak callback is: {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{str(org_code)}' and rr_number = '{str(rrn)}' order by " \
                    f"created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_db = result['id'].values[0]
            logger.debug(f"Fetching txn_id from txn table: {txn_id_db}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table: {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table: {payer_name}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table: {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table: {auth_code}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.info(f"Fetching label_ids from txn table: {label_ids}")
            status_db = result["status"].values[0]
            logger.info(f"Fetching status from txn table: {status_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
            amount_db = int(result["amount"].values[0])
            logger.info(f"Fetching amount from txn table: {amount_db}")
            state_db = result["state"].values[0]
            logger.info(f"Fetching state from txn table: {state_db}")
            external_ref_db = result["external_ref"].values[0]
            logger.info(f"Fetching external reference number from txn table: {external_ref_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
            bank_code_db = result["bank_code"].values[0]
            logger.info(f"Fetching bank code from txn table: {bank_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.info(f"Fetching bank name from txn table: {bank_name_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            rrn_db = result["rr_number"].values[0]
            logger.info(f"Fetching rrn from txn table: {rrn_db}")
            txn_type_db = result["txn_type"].values[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].values[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].values[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_msg_db = str(result['error_message'].values[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

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
        # -----------------------------------------Start of App Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id_db,
                    "rrn": rrn,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info("Logging in to the app")
                login_page.perform_login(app_username, app_password)
                logger.info("Waiting for Home Page to load")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.info("Clicking on transaction history")
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("Clicking on transaction according to txn id")
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_db)
                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                txn_id_app = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn id from txn history for the txn :, {txn_id_app}")
                status_app = transactions_history_page.fetch_txn_status_text().replace('STATUS:', '')
                logger.info(f"Fetching status from txn history for the txn : {status_app}")
                settlement_status_app = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {settlement_status_app}")
                rrn_app = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {rrn_app}")
                date_and_time_app = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {date_and_time_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "date": date_and_time_app
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": external_ref_db,
                    "accountLabel": account_label_name,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_db][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response: {status_api}")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response: {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api response: {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response: {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response: {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response: {txn_type_api}")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response: {order_id_api}")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response: {date_api}")
                account_label_name_api = response["accountLabel"]
                logger.debug(f"Fetching account label name from api response: {account_label_name_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": rrn_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "order_id": order_id_api,
                    "accountLabel": account_label_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "BHARATQR",
                    "txn_amt": amount,
                    "payer_name": payer_name,
                    "error_msg": "None",
                    "bank_name": "HDFC Bank",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "MINTOAK",
                    "rrn": str(rrn),
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "acc_label_id": bqr_acc_label_id,
                    "bqr_pmt_status": "Success",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_txn_primary_id": txn_id_db,
                    "bqr_rrn": str(rrn),
                    "bqr_org_code": org_code,
                    "bqr_txn_type": "STATIC_QR",
                    "bqr_bank_code": "HDFC",
                    "bqr_mc_id": bqr_mc_id
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from bharatqr_txn where id='{txn_id_db}';"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                logger.debug(f"Fetching bqr_status from bharatqr_txn table : {bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching bqr_state from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = int(result["txn_amount"].values[0])
                logger.debug(f"Fetching bqr_amount from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching bqr_txn_type from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching bqr_terminal_info_id from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bqr_bank_code from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_mc_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching bqr_mc_id from bharatqr_txn table : {bqr_mc_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching bqr_txn_primary_id from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching bqr_org_code from bharatqr_txn table : {bqr_org_code_db}")
                bqr_mc_pan_db = str(result['merchant_pan'].values[0])
                logger.debug(f"Fetching bqr_merchant_pan_number from bharatqr_txn table : {bqr_mc_pan_db}")
                bqr_rrn_db = result['rrn'].values[0]
                logger.debug(f"Fetching rrn from bharatqr_txn table: {bqr_rrn_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "payer_name": payer_name,
                    "error_msg": error_msg_db,
                    "bank_name": bank_name_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "acc_label_id": label_ids,
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_rrn": str(bqr_rrn_db),
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_mc_id": bqr_mc_id_db
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
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id_db,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn),
                    "acct_label": account_label_name
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref_db)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"Fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal {username_portal}")
                labels_portal = transaction_details[0]['Labels']
                logger.info(f"Fetching labels from portal {labels_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal,
                    "acct_label": labels_portal,
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
                    'PAID BY:': 'BHARATQR',
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id_db, {"username": app_username,
                                                                              "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_113_016():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_StaticQR_Callback_Success_Via_HDFC_MINTOAK_MultiAcc_InactiveLabel
    Sub Feature Description: Multi Account - Verifying a Static QR BQR success callback via HDFC_MINTOAK when label is Inactive
    TC naming code description: 100: Payment Method, 113: MultiAcc_StaticQR, 016: TC016
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table: {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(org_code,
                                                                                       portal_un=portal_username,
                                                                                       portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetching account_label_name : {account_label_name}")

        setting_value = '{"name":"' + f"{account_label_name}" + '","status":"ACTIVE"}'
        setting_value_inactive = '{"name":"' + f"{account_label_name}" + '","status":"INACTIVE"}'
        query = f"select * from account_labels where org_code='{org_code}' and setting_value='{setting_value}';"
        logger.debug(f"Query to fetch account_labels_id from the account_labels table: {query}")
        result = DBProcessor.getValueFromDB(query)
        account_labels_id = result['id'].values[0]
        logger.debug(f"Fetching account_labels_id from account_labels table: {account_labels_id}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' and bank_code = 'HDFC_MINTOAK' and " \
                f"acc_label_id=(select id from label where name='{account_label_name}' and org_code ='{org_code}')"
        logger.debug(f"query to fetch data from bharatqr_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
        mid = result["mid"].values[0]
        logger.debug(f"Value of mid from bqr_merchant_config table: {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Value of tid from bqr_merchant_config table: {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"Value of terminal_info_id from bqr_merchant_config table: {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"Value of bqr_mc_id from bharatqr_merchant_config table: {bqr_mc_id}")
        bqr_mc_pan = str(result["merchant_pan"].values[0])
        logger.debug(f"Value of bqr_merchant_pan from bharatqr_merchant_config table: {bqr_mc_pan}")
        bqr_acc_label_id = str(result['acc_label_id'].values[0])
        logger.debug(f"Value of bqr_acc_label_id from bharatqr_merchant_config table: {bqr_acc_label_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(251, 300)
            logger.info(f"Generated random amount is: {amount}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": mid,
                "tid": tid,
                "merchantPan": bqr_mc_pan,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the bqr static qr generation : {response}")
            publish_id = response["publishId"]
            logger.debug(f"Fetching publish_id from the bqr static qr generate api, publish_id : {publish_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            txn_id = "231129064936760E" + str(random.randint(10000000, 999999999))
            logger.info(f"Generated txn_id is: {txn_id}")
            m_txn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.info(f"Generated m_txn_id is: {m_txn_id}")
            rrn = str(random.randint(10000000, 99999999))
            logger.info(f"Generated rrn is: {rrn}")

            query = f"update account_labels set setting_value='{setting_value_inactive}' where id='{account_labels_id}';"
            logger.debug(
                f"query : {query}, to make setting_value : {setting_value}, inactive for org_code : {org_code}")
            DBProcessor.setValueToDB(query)
            api_details = DBProcessor.get_api_details('DB Refresh', request_body={
                "username": portal_username,
                "password": portal_password
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting precondition DB refresh is : {response}")

            logger.debug(f"Performing encryption api call")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = m_txn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"
            api_details_encryption['RequestBody']['payload']['description'] = "Static QR"
            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")

            logger.debug(f"Performing callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for confirming mintoak callback is: {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{str(org_code)}' and rr_number = '{str(rrn)}' order by " \
                    f"created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_db = result['id'].values[0]
            logger.debug(f"Fetching txn_id from txn table: {txn_id_db}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table: {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table: {payer_name}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table: {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table: {auth_code}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.info(f"Fetching label_ids from txn table: {label_ids}")
            status_db = result["status"].values[0]
            logger.info(f"Fetching status from txn table: {status_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
            amount_db = int(result["amount"].values[0])
            logger.info(f"Fetching amount from txn table: {amount_db}")
            state_db = result["state"].values[0]
            logger.info(f"Fetching state from txn table: {state_db}")
            external_ref_db = result["external_ref"].values[0]
            logger.info(f"Fetching external reference number from txn table: {external_ref_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
            bank_code_db = result["bank_code"].values[0]
            logger.info(f"Fetching bank code from txn table: {bank_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.info(f"Fetching bank name from txn table: {bank_name_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            rrn_db = result["rr_number"].values[0]
            logger.info(f"Fetching rrn from txn table: {rrn_db}")
            txn_type_db = result["txn_type"].values[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].values[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].values[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_msg_db = str(result['error_message'].values[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

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
        # -----------------------------------------Start of App Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id_db,
                    "rrn": rrn,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info("Logging in to the app")
                login_page.perform_login(app_username, app_password)
                logger.info("Waiting for Home Page to load")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.info("Clicking on transaction history")
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("Clicking on transaction according to txn id")
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_db)
                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                txn_id_app = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn id from txn history for the txn :, {txn_id_app}")
                status_app = transactions_history_page.fetch_txn_status_text().replace('STATUS:', '')
                logger.info(f"Fetching status from txn history for the txn : {status_app}")
                settlement_status_app = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {settlement_status_app}")
                rrn_app = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {rrn_app}")
                date_and_time_app = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {date_and_time_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "date": date_and_time_app
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": external_ref_db,
                    "accountLabel": account_label_name,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_db][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response: {status_api}")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response: {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api response: {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response: {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response: {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response: {txn_type_api}")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response: {order_id_api}")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response: {date_api}")
                account_label_name_api = response["accountLabel"]
                logger.debug(f"Fetching account label name from api response: {account_label_name_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": rrn_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "order_id": order_id_api,
                    "accountLabel": account_label_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "BHARATQR",
                    "txn_amt": amount,
                    "payer_name": payer_name,
                    "error_msg": "None",
                    "bank_name": "HDFC Bank",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "MINTOAK",
                    "rrn": str(rrn),
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "acc_label_id": bqr_acc_label_id,
                    "bqr_pmt_status": "Success",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_txn_primary_id": txn_id_db,
                    "bqr_rrn": str(rrn),
                    "bqr_org_code": org_code,
                    "bqr_txn_type": "STATIC_QR",
                    "bqr_bank_code": "HDFC",
                    "bqr_mc_id": bqr_mc_id
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from bharatqr_txn where id='{txn_id_db}';"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                logger.debug(f"Fetching bqr_status from bharatqr_txn table : {bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching bqr_state from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = int(result["txn_amount"].values[0])
                logger.debug(f"Fetching bqr_amount from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching bqr_txn_type from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching bqr_terminal_info_id from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bqr_bank_code from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_mc_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching bqr_mc_id from bharatqr_txn table : {bqr_mc_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching bqr_txn_primary_id from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching bqr_org_code from bharatqr_txn table : {bqr_org_code_db}")
                bqr_mc_pan_db = str(result['merchant_pan'].values[0])
                logger.debug(f"Fetching bqr_merchant_pan_number from bharatqr_txn table : {bqr_mc_pan_db}")
                bqr_rrn_db = result['rrn'].values[0]
                logger.debug(f"Fetching rrn from bharatqr_txn table: {bqr_rrn_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "payer_name": payer_name,
                    "error_msg": error_msg_db,
                    "bank_name": bank_name_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "acc_label_id": label_ids,
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_rrn": str(bqr_rrn_db),
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_mc_id": bqr_mc_id_db
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
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id_db,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn),
                    "acct_label": account_label_name
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref_db)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"Fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal {username_portal}")
                labels_portal = transaction_details[0]['Labels']
                logger.info(f"Fetching labels from portal {labels_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal,
                    "acct_label": labels_portal,
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
                    'PAID BY:': 'BHARATQR',
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id_db, {"username": app_username,
                                                                              "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            query = f"update account_labels set setting_value='{setting_value}' where id='{account_labels_id}';"
            logger.debug(f"query : {query} to make setting_value : {setting_value}, active for org_code : {org_code}")
        except Exception as e:
            logger.exception(f"exception occurred : {e}")
            query = f"update account_labels set setting_value='{setting_value}' " \
                    f"where setting_value='{setting_value_inactive}' and org_code='{org_code}';"
            logger.debug(f"query : {query} to make setting_value : {setting_value}, active for org_code : {org_code}")
        DBProcessor.setValueToDB(query)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        Configuration.executeFinallyBlock(testcase_id)
