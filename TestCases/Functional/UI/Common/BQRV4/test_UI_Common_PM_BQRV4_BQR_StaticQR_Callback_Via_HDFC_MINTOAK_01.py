import random
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, ResourceAssigner, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_108_041():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_StaticQR_Callback_Success_AutoRefund_Disabled_Via_HDFC_MINTOAK
    Sub Feature Description: Verifying a BQR success callback via HDFC_MINTOAK when autorefund is disabled
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 041: TC041
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

        query = f"select * from org_employee where username='{str(app_username)}'"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund disabled is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_id = result['id'].values[0]
        logger.info(f"fetched config id is : {db_bqr_config_id}")
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_config_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")
        db_bqr_config_terminal_info_id = result["terminal_info_id"].values[0]
        logger.info(f"fetched terminal_info_id is : {db_bqr_config_terminal_info_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username=portal_username,
                                                                          portal_password=portal_password,
                                                                          org_code=org_code)

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid
            })
            response = APIProcessor.send_request(api_details)
            res_generateqr_mid = response["mid"]
            res_generateqr_tid = response["tid"]
            logger.debug(f"Response received for static_qrcode_generate_HDFC_MINTOAK api is : {response}")

            amount = random.randint(251, 300)
            logger.debug(f"generated random amount is : {amount}")
            logger.debug(f"preparing data to perform the encryption generation")
            txn_id = "231129064936760E" + str(random.randint(10000000, 999999999))
            logger.debug(f"Generating random txn_id: {txn_id}")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating random mtxn_id: {mtxn_id}")
            rrn = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating random rrn: {rrn}")

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = db_bqr_config_tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
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
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": db_bqr_config_tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{str(org_code)}' and rr_number = '{str(rrn)}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            db_txn_id = result["id"].values[0]
            logger.debug(f"Fetching txn_id from txn table : {db_txn_id}")
            db_txn_amount = result["amount"].values[0]
            logger.debug(f"Fetching amount from txn table : {db_txn_amount}")
            db_txn_bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching bank code from txn table : {db_txn_bank_code}")
            db_txn_username = result["username"].values[0]
            logger.debug(f"Fetching username from txn table : {db_txn_username}")
            db_txn_tid = result["tid"].values[0]
            logger.debug(f"Fetching tid from txn table : {db_txn_tid}")
            db_txn_mid = result["mid"].values[0]
            logger.debug(f"Fetching mid from txn table : {db_txn_mid}")
            db_txn_payment_mode = result["payment_mode"].values[0]
            logger.debug(f"Fetching payment mode from txn table : {db_txn_payment_mode}")
            db_txn_external_ref = result["external_ref"].values[0]
            logger.debug(f"Fetching external ref from txn table : {db_txn_external_ref}")
            db_txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table : {db_txn_created_time}")
            db_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from txn table : {db_rrn}")
            db_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {db_auth_code}")
            db_settlement_status = result["settlement_status"].values[0]
            logger.debug(f"Fetching settlement status from txn table : {db_settlement_status}")
            db_payment_status = result["status"].values[0]
            logger.debug(f"Fetching payment status from txn table : {db_payment_status}")

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
                date_and_time = date_time_converter.to_app_format(db_txn_created_time)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": db_txn_id,
                    "rrn": str(rrn),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(db_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {db_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {db_txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {db_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {db_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {db_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {db_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {db_txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {db_txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "pmt_msg": app_payment_msg,
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
                date = date_time_converter.db_datetime(db_txn_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password}
                                                          )
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == db_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api : {date_api}")

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
                    "amount": amount,
                    "bank_code": "HDFC",
                    "status": "AUTHORIZED",
                    "username": app_username,
                    "tid": res_generateqr_tid,
                    "mid": res_generateqr_mid,
                    "pmt_mode": "BHARATQR",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "bqr_pmt_status": "Success",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "STATIC_QR",
                    "bqr_terminal_info_id": db_bqr_config_terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": db_bqr_config_id,
                    "bqr_txn_primary_id": db_txn_id,
                    "bqr_rrn": str(rrn),
                    "bqr_org_code": org_code
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from bharatqr_txn where id='{db_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                logger.debug(f"Fetching txn_status from db : {bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching state from db : {bqr_state_db}")
                bqr_amount_db = int(result["txn_amount"].values[0])
                logger.debug(f"Fetching amount from db : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching txn_type from db : {bqr_txn_type_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching terminal info id from db : {brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bank code from db : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching merchant config id from db : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching txn_primary id from db : {bqr_txn_primary_id_db}")
                bqr_merchant_pan_db = result["merchant_pan"].values[0]
                logger.debug(f"Fetching merchant pan from db : {bqr_merchant_pan_db}")
                bqr_rrn_db = result['rrn'].values[0]
                logger.debug(f"Fetching rrn from db : {bqr_rrn_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching org_code from db : {bqr_org_code_db}")

                actual_db_values = {
                    "amount": db_txn_amount,
                    "bank_code": db_txn_bank_code,
                    "status": db_payment_status,
                    "username": db_txn_username,
                    "tid": db_txn_tid,
                    "mid": db_txn_mid,
                    "pmt_mode": db_txn_payment_mode,
                    "rrn": db_rrn,
                    "settle_status": db_settlement_status,
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db
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
                date_and_time_portal = date_time_converter.to_portal_format(db_txn_created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": db_txn_id,
                    "rrn": str(rrn),
                    "auth_code": "-" if db_auth_code is None else db_auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         db_txn_external_ref)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(db_txn_created_time)
                expected_values = {
                    'PAID BY:': 'BHARATQR',
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    "AUTH CODE": "" if db_auth_code is None else db_auth_code
                }
                receipt_validator.perform_charge_slip_validations(db_txn_id, {
                    "username": app_username,
                    "password": app_password}, expected_values)
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
@pytest.mark.portalVal
def test_common_100_108_042():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_StaticQR_Callback_Failed_AutoRefund_Disabled_Via_HDFC_MINTOAK
    Sub Feature Description: Verifying a BQR failed callback via HDFC_MINTOAK when autorefund is disabled
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 042: TC042
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

        query = f"select * from org_employee where username='{str(app_username)}'"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username, portal_pw=portal_password,
                                                           payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund disabled is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_id = result['id'].values[0]
        logger.info(f"fetched config id is : {db_bqr_config_id}")
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_config_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")
        db_bqr_config_terminal_info_id = result["terminal_info_id"].values[0]
        logger.info(f"fetched terminal_info_id is : {db_bqr_config_terminal_info_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username=portal_username,
                                                                          portal_password=portal_password,
                                                                          org_code=org_code)

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)----------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid
            })
            response = APIProcessor.send_request(api_details)
            res_generateqr_mid = response["mid"]
            res_generateqr_tid = response["tid"]
            logger.debug(f"Response received for static_qrcode_generate_HDFC_MINTOAK api is : {response}")

            amount = random.randint(251, 300)
            logger.debug(f"generated random amount is : {amount}")

            logger.debug(f"preparing data to perform the encryption generation")
            txn_id = "231129064936760E" + str(random.randint(10000000, 999999999))
            logger.debug(f"Generating random txn_id: {txn_id}")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating random mtxn_id: {mtxn_id}")
            rrn = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating random rrn: {rrn}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_failed')
            api_details_encryption['RequestBody']['terminalId'] = db_bqr_config_tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
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
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": db_bqr_config_tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{str(org_code)}' and rr_number = '{str(rrn)}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            db_txn_id = result["id"].values[0]
            logger.debug(f"Fetching txn_id from txn table : {db_txn_id}")
            db_txn_amount = result["amount"].values[0]
            logger.debug(f"Fetching amount from txn table : {db_txn_amount}")
            db_txn_bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching bank code from txn table : {db_txn_bank_code}")
            db_txn_username = result["username"].values[0]
            logger.debug(f"Fetching username from txn table : {db_txn_username}")
            db_txn_tid = result["tid"].values[0]
            logger.debug(f"Fetching tid from txn table : {db_txn_tid}")
            db_txn_mid = result["mid"].values[0]
            logger.debug(f"Fetching mid from txn table : {db_txn_mid}")
            db_txn_payment_mode = result["payment_mode"].values[0]
            logger.debug(f"Fetching payment mode from txn table : {db_txn_payment_mode}")
            db_txn_external_ref = result["external_ref"].values[0]
            logger.debug(f"Fetching external ref from txn table : {db_txn_external_ref}")
            db_txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table : {db_txn_created_time}")
            db_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from txn table : {db_rrn}")
            db_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {db_auth_code}")
            db_settlement_status = result["settlement_status"].values[0]
            logger.debug(f"Fetching settlement status from txn table : {db_settlement_status}")
            db_payment_status = result["status"].values[0]
            logger.debug(f"Fetching payment status from txn table : {db_payment_status}")

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
                date_and_time = date_time_converter.to_app_format(db_txn_created_time)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "FAILED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "FAILED",
                    "txn_id": db_txn_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(db_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {db_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {db_txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {db_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {db_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {db_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {db_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {db_txn_id}, {app_payment_msg}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "pmt_msg": app_payment_msg,
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
                date = date_time_converter.db_datetime(db_txn_created_time)
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == db_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api : {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api : {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
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
                    "amount": amount,
                    "bank_code": "HDFC",
                    "status": "FAILED",
                    "username": app_username,
                    "tid": res_generateqr_tid,
                    "mid": res_generateqr_mid,
                    "payment_mode": "BHARATQR",
                    "rrn": rrn,
                    "settle_status": "FAILED",
                    "bqr_pmt_status": "Failed",
                    "bqr_pmt_state": "FAILED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "STATIC_QR",
                    "bqr_terminal_info_id": db_bqr_config_terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": db_bqr_config_id,
                    "bqr_txn_primary_id": db_txn_id,
                    "bqr_rrn": str(rrn),
                    "bqr_org_code": org_code
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from bharatqr_txn where id='{db_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                logger.debug(f"Fetching status from db : {bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching state from db : {bqr_state_db}")
                bqr_amount_db = int(result["txn_amount"].values[0])
                logger.debug(f"Fetching amount from db : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching txn type from db : {bqr_txn_type_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching terminal info id from db : {brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bank code from db : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching merchant config id from db : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching txn primary id from db : {bqr_txn_primary_id_db}")
                bqr_merchant_pan_db = result["merchant_pan"].values[0]
                logger.debug(f"Fetching merchant pan from db : {bqr_merchant_pan_db}")
                bqr_rrn_db = result['rrn'].values[0]
                logger.debug(f"Fetching rrn from db : {bqr_rrn_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching org code from db : {bqr_org_code_db}")

                actual_db_values = {
                    "amount": db_txn_amount,
                    "bank_code": db_txn_bank_code,
                    "status": db_payment_status,
                    "username": db_txn_username,
                    "tid": db_txn_tid,
                    "mid": db_txn_mid,
                    "payment_mode": db_txn_payment_mode,
                    "rrn": db_rrn,
                    "settle_status": db_settlement_status,
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db
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
                date_and_time_portal = date_time_converter.to_portal_format(db_txn_created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "FAILED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": db_txn_id,
                    "rrn": str(rrn),
                    "auth_code": "-" if db_auth_code is None else db_auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         db_txn_external_ref)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
def test_common_100_108_043():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_StaticQR_Duplicate_Callback_Via_HDFC
    Sub Feature Description: Verifying duplicate Callback case for BQR with same rrn and same txn ref  not to create new txn
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 043: Testcase ID
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from bharatqr_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_id = result['id'].values[0]
        logger.info(f"fetched config id is : {db_bqr_config_id}")
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_config_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid
            })
            response = APIProcessor.send_request(api_details)
            res_generateqr_publish_id = response["publishId"]
            logger.debug(f"Response received for static_qrcode_generate_hdfc_mintoak api is : {response}")

            rrn = random.randint(11111110, 99999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = 'RID' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")
            amount = random.randint(251, 300)
            logger.debug(f"generated random amount is : {amount}")
            status = "SUCCESS"
            logger.debug(f"Payment status is : {status}")
            status_code = "00"
            logger.debug(f"Status code is : {status_code}")

            logger.debug(
                f"replacing the publish_id with {res_generateqr_publish_id}, amount with {amount}.00, ref_id with {ref_id}, statusCode with {status_code}, status with {status}  and rrn with {rrn} in the curl_data")

            logger.debug(f"preparing data to perform the encryption generation")
            txn_id = "231129064936760E" + str(random.randint(10000000, 999999999))
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            rrn = str(random.randint(10000000, 99999999))
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = db_bqr_config_tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"
            api_details_encryption['RequestBody']['payload']['description'] = "Static QR"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": db_bqr_config_tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            logger.debug(
                f"encryptedData received for second mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": db_bqr_config_tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for second callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for second callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '" + str(
                rrn) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            db_txn_id = result["id"].values[0]
            logger.debug(f"Fetching Txn ID from txn table: {db_txn_id}")
            db_txn_amount = result["amount"].values[0]
            logger.debug(f"Fetching Amount from txn table: {db_txn_amount}")
            db_org_code = result["org_code"].values[0]
            logger.debug(f"Fetching Org Code from txn table: {db_org_code}")
            db_txn_bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching Bank Code from txn table: {db_txn_bank_code}")
            db_txn_username = result["username"].values[0]
            logger.debug(f"Fetching db_txn_username from txn table: {db_txn_username}")
            db_txn_tid = result["tid"].values[0]
            logger.debug(f"Fetching db_txn_tid from txn table: {db_txn_tid}")
            db_txn_mid = result["mid"].values[0]
            logger.debug(f"Fetching db_txn_mid from txn table: {db_txn_mid}")
            db_txn_payment_mode = result["payment_mode"].values[0]
            logger.debug(f"Fetching Payment Mode from txn table: {db_txn_payment_mode}")
            txn_created_time = result["created_time"].values[0]
            logger.debug(f"Fetching created_time from txn table: {txn_created_time}")
            db_txn_auth_code = result["auth_code"].values[0]
            logger.debug(f"Fetching auth_code from txn table: {db_txn_auth_code}")
            db_txn_rrn = result["rr_number"].values[0]
            logger.debug(f"Fetching db_txn_rrn from txn table: {db_txn_rrn}")
            db_txn_ref = result["external_ref"].values[0]
            logger.debug(f"Fetching external_ref from txn table: {db_txn_ref}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '" + str(
                rrn) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            db_txn_id_2 = result["id"].values[0]
            logger.debug(f"Fetching Txn ID from txn table: {db_txn_id_2}")
            db_txn_amount_2 = result["amount"].values[0]
            logger.debug(f"Fetching Amount from txn table: {db_txn_amount_2}")
            db_txn_bank_code_2 = result["bank_code"].values[0]
            logger.debug(f"Fetching Bank Code from txn table: {db_txn_bank_code_2}")
            db_org_code_2 = result["org_code"].values[0]
            logger.debug(f"Fetching Org Code from txn table: {db_org_code}")
            db_txn_username_2 = result["username"].values[0]
            logger.debug(f"Fetching db_txn_username from txn table: {db_txn_username_2}")
            db_txn_tid_2 = result["tid"].values[0]
            logger.debug(f"Fetching db_txn_tid from txn table: {db_txn_tid_2}")
            db_txn_mid_2 = result["mid"].values[0]
            logger.debug(f"Fetching db_txn_mid from txn table: {db_txn_mid_2}")
            db_txn_payment_mode_2 = result["payment_mode"].values[0]
            logger.debug(f"Fetching Payment Mode from txn table: {db_txn_payment_mode_2}")

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
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "txn_id": db_txn_id,
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "rrn": str(db_txn_rrn),
                    "pmt_msg": "PAYMENT SUCCESSFUL"
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(db_txn_id_2)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Payment Status: {payment_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Payment Message: {app_payment_msg_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Payment Mode: {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Transaction ID: {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Amount: {app_amount_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Settlement Status: {app_settlement_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"RRN: {app_rrn_2}")

                actual_app_values = {
                    "pmt_mode": payment_mode_2,
                    "txn_id": app_txn_id_2,
                    "pmt_status": payment_status_2.split(':')[1],
                    "txn_amt": app_amount_2.split(' ')[1],
                    "rrn": str(app_rrn_2),
                    "settle_status": app_settlement_status_2,
                    "pmt_msg": app_payment_msg_2
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
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response1 = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response1}")

                response = [x for x in response1["txns"] if x["txnId"] == db_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                logger.debug(
                    f"API Details for original txn : status:{status_api}, amount:{amount_api}, payment mode:{payment_mode_api}, state:{state_api}, settlement status:{settlement_status_api}, issuer code:{issuer_code_api}, acquirer code:{acquirer_code_api}, org code:{org_code_api}, mid:{mid_api}, tid:{tid_api}, txn type:{txn_type_api}")

                response = [x for x in response1["txns"] if x["txnId"] == db_txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_2 = response["status"]
                amount_api_2 = float(response["amount"])
                payment_mode_api_2 = response["paymentMode"]
                state_api_2 = response["states"][0]
                rrn_api_2 = response["rrNumber"]
                settlement_status_api_2 = response["settlementStatus"]
                issuer_code_api_2 = response["issuerCode"]
                acquirer_code_api_2 = response["acquirerCode"]
                org_code_api_2 = response["orgCode"]
                mid_api_2 = response["mid"]
                tid_api_2 = response["tid"]
                txn_type_api_2 = response["txnType"]
                logger.debug(
                    f"API Details for original txn : status:{status_api_2}, amount:{amount_api_2}, payment mode:{payment_mode_api_2}, state:{state_api_2}, settlement status:{settlement_status_api_2}, issuer code:{issuer_code_api_2}, acquirer code:{acquirer_code_api_2}, org code:{org_code_api_2}, mid:{mid_api_2}, tid:{tid_api_2}, txn type:{txn_type_api_2}")

                expected_api_values = {
                    "txn_id": db_txn_id,
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "txn_id": db_txn_id_2,
                    "pmt_status": status_api_2,
                    "txn_amt": amount_api_2,
                    "pmt_mode": payment_mode_api_2,
                    "pmt_state": state_api_2,
                    "rrn": str(rrn_api_2),
                    "settle_status": settlement_status_api_2,
                    "acquirer_code": acquirer_code_api_2,
                    "issuer_code": issuer_code_api_2,
                    "mid": mid_api_2,
                    "tid": tid_api_2,
                    "txn_type": txn_type_api_2,
                    "org_code": org_code_api_2
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
                query = f"select * from bharatqr_txn where id='{db_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                logger.debug(f"Fetching status from bharatqr_txn table: {bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching State from bharatqr_txn table: {bqr_state_db}")
                bqr_amount_db = int(result["txn_amount"].values[0])
                logger.debug(f"Fetching Amount from bharatqr_txn table: {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type from bharatqr_txn table: {bqr_txn_type_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching terminal_info_id from bharatqr_txn table: {brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from bharatqr_txn table: {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching Merchant Config from bharatqr_txn table: {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching Transaction Primary ID from bharatqr_txn table: {bqr_txn_primary_id_db}")
                bqr_merchant_pan_db = result["merchant_pan"].values[0]
                logger.debug(f"Fetching merchant_pan from bharatqr_txn table rrn: {bqr_merchant_pan_db}")
                bqr_rrn_db = result['rrn'].values[0]
                logger.debug(f"Fetching RRN from bharatqr_txn table rrn: {bqr_rrn_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching Org Code from bharatqr_txn table: {bqr_org_code_db}")

                query = f"select * from bharatqr_txn where id='{db_txn_id_2}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_2 = result["status_desc"].values[0]
                logger.debug(f"Fetching status_desc from bqr txn table: {bqr_status_db_2}")
                bqr_state_db_2 = result["state"].values[0]
                logger.debug(f"Fetching State from bqr txn table: {bqr_state_db}")
                bqr_amount_db_2 = int(result["txn_amount"].values[0])
                logger.debug(f"Fetching Amount from bqr txn table: {bqr_amount_db}")
                bqr_txn_type_db_2 = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type from bqr txn table: {bqr_txn_type_db}")
                brq_terminal_info_id_db_2 = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching terminal_info_id from bqr txn table: {brq_terminal_info_id_db_2}")
                bqr_bank_code_db_2 = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from bqr txn table: {bqr_bank_code_db}")
                bqr_merchant_config_id_db_2 = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching Merchant Config from bqr txn table: {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db_2 = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching Transaction Primary ID from bqr txn table: {bqr_txn_primary_id_db}")
                bqr_merchant_pan_db_2 = result["merchant_pan"].values[0]
                logger.debug(f"Fetching merchant_pan_db from bqr txn table: {bqr_merchant_pan_db_2}")
                bqr_rrn_db_2 = result['rrn'].values[0]
                logger.debug(f"Fetching RRN from bqr txn table rrn: {bqr_rrn_db}")
                bqr_org_code_db_2 = result['org_code'].values[0]
                logger.debug(f"Fetching Org Code from bqr txn table: {bqr_org_code_db}")

                expected_db_values = {
                    "txn_amt": db_txn_amount,
                    "pmt_mode": db_txn_payment_mode,
                    "pmt_status": bqr_status_db,
                    "pmt_state": bqr_state_db,
                    "mid": db_txn_mid,
                    "tid": db_txn_tid,
                    "bank_code": db_txn_bank_code,
                    "org_code": db_org_code,
                    "username": db_txn_username,
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": str(bqr_rrn_db),
                    "bqr_org_code": bqr_org_code_db
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": db_txn_amount_2,
                    "pmt_mode": db_txn_payment_mode_2,
                    "pmt_status": bqr_status_db_2,
                    "pmt_state": bqr_state_db_2,
                    "mid": db_txn_mid_2,
                    "tid": db_txn_tid_2,
                    "bank_code": db_txn_bank_code_2,
                    "org_code": db_org_code_2,
                    "username": db_txn_username_2,
                    "bqr_pmt_status": bqr_status_db_2,
                    "bqr_pmt_state": bqr_state_db_2,
                    "bqr_txn_amt": bqr_amount_db_2,
                    "bqr_txn_type": bqr_txn_type_db_2,
                    "bqr_terminal_info_id": brq_terminal_info_id_db_2,
                    "bqr_bank_code": bqr_bank_code_db_2,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db_2,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db_2,
                    "bqr_merchant_pan": bqr_merchant_pan_db_2,
                    "bqr_rrn": str(bqr_rrn_db_2),
                    "bqr_org_code": bqr_org_code_db_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": db_txn_id,
                    "auth_code": "-" if db_txn_auth_code is None else db_txn_auth_code,
                    "rrn": "-" if db_txn_rrn is None else db_txn_rrn
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, db_txn_ref)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Date and time from portal: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"Transaction ID from portal: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Amount from portal: {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Auth Code from portal: {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number from portal: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"Transaction Type from portal: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"Status from portal: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"Username from portal: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number
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
