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
def test_common_100_108_038():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Callback_Success_AutoRefund_Disabled_Via_HDFC_MINTOAK
    Sub Feature Description: Verifying static qr upi success callback via HDFC_MINTOAK when autorefund is disabled
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 038: TC038
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
        db_bqr_conig_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_conig_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_config_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched merchantId is : {db_upi_config_merchant_id}")
        db_upi_mc_id = result['id'].values[0]
        logger.info(f"fetched id is : {db_upi_mc_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username=portal_username,
                                                                          portal_password=portal_password,
                                                                          org_code=org_code)

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

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_conig_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            res_generateqr_publish_id = response["publishId"]
            res_generateqr_mid = response["mid"]
            res_generateqr_tid = response["tid"]
            logger.debug(f"Response received for static_qrcode_generate_HDFC_MINTOAK api is : {response}")

            amount = random.randint(251, 300)
            logger.debug(f"generated random amount is : {amount}")

            logger.debug(f"preparing data to perform the encryption generation")
            txn_id = "231129064936760E" + str(random.randint(10000000, 999999999))
            logger.debug(f"Generating randon txn_id: {txn_id}")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating randon mtxn_id: {txn_id}")
            rrn = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating randon rrn: {rrn}")

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = db_bqr_conig_tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"
            api_details_encryption['RequestBody']['payload']['description'] = "Static QR"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")

            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": db_bqr_conig_tid,
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
            logger.debug(f"Fetching txn id from txn table : {db_txn_id}")
            db_txn_amount = result["amount"].values[0]
            logger.debug(f"Fetching amount from txn table : {db_txn_amount}")
            db_txn_bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching bank code from txn table : {db_txn_id}")
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
                    "pmt_mode": "UPI",
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
                # home_page.check_home_page_logo()
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
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
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
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_conig_tid,
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
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settle status from api : {settlement_status_api}")
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
                    "org_code": org_code,
                    "status": "AUTHORIZED",
                    "username": app_username,
                    "tid": res_generateqr_tid,
                    "mid": res_generateqr_mid,
                    "additional_field1": res_generateqr_publish_id,
                    "upi_mc_id": db_upi_mc_id,
                    "payment_mode": "UPI",
                    "resp_code": "Success",
                    "txn_type": "STATIC_QR",
                    "rrn": str(rrn)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id = '{str(db_txn_id)}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                db_upi_txn_additional_field1 = result["additional_field1"].values[0]
                logger.debug(f"Fetching upi_txn_additional_field1 from db : {db_upi_txn_additional_field1}")
                db_upi_txn_resp_code = result["resp_code"].values[0]
                logger.debug(f"Fetching upi_txn_resp_code from db : {db_upi_txn_resp_code}")
                db_upi_txn_org_code = result["org_code"].values[0]
                logger.debug(f"Fetching upi_txn_org_code from db : {db_upi_txn_org_code}")
                db_upi_txn_status = result["status"].values[0]
                logger.debug(f"Fetching upi_txn_status from db : {db_upi_txn_status}")
                db_upi_txn_txn_type = result["txn_type"].values[0]
                logger.debug(f"Fetching upi_txn_type from db : {db_upi_txn_txn_type}")
                db_upi_txn_upi_mc_id = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching upi_txn_mc_id from db : {db_upi_txn_upi_mc_id}")

                actual_db_values = {
                    "amount": db_txn_amount,
                    "bank_code": db_txn_bank_code,
                    "org_code": db_upi_txn_org_code,
                    "status": db_upi_txn_status,
                    "username": db_txn_username,
                    "tid": db_txn_tid,
                    "mid": db_txn_mid,
                    "upi_mc_id": db_upi_txn_upi_mc_id,
                    "additional_field1": db_upi_txn_additional_field1,
                    "payment_mode": db_txn_payment_mode,
                    "resp_code": db_upi_txn_resp_code,
                    "txn_type": db_upi_txn_txn_type,
                    "rrn": str(db_rrn)
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
                    "pmt_type": "UPI",
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
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    "AUTH CODE": "" if db_auth_code is None else db_auth_code
                }
                receipt_validator.perform_charge_slip_validations(db_txn_id, {
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
@pytest.mark.appVal
@pytest.mark.portalVal
def test_common_100_108_039():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Callback_Failed_AutoRefund_Disabled_Via_HDFC_MINTOAK
    Sub Feature Description: Verifying static qr upi failed callback via HDFC_MINTOAK when autorefund is disabled
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 039: TC039
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
        db_bqr_conig_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_conig_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_config_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched merchantId is : {db_upi_config_merchant_id}")
        db_upi_mc_id = result['id'].values[0]
        logger.info(f"fetched id is : {db_upi_mc_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username=portal_username,
                                                                          portal_password=portal_password,
                                                                          org_code=org_code)

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

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_conig_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            res_generateqr_publish_id = response["publishId"]
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
            api_details_encryption['RequestBody']['terminalId'] = db_bqr_conig_tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"
            api_details_encryption['RequestBody']['payload']['description'] = "Static QR"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")

            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": db_bqr_conig_tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{str(org_code)}' and rr_number = '" + str(
                rrn) + "'order by created_time desc limit 1"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            db_txn_id = result["id"].values[0]
            logger.debug(f"Fetching txn_id from txn table : {txn_id}")
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
            logger.debug(f"Fetching rrn from txn table : {rrn}")
            db_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {db_auth_code}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "FAILED",
                    "txn_id": db_txn_id,
                    "rrn": str(rrn),
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
                # home_page.check_home_page_logo()
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
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
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
                date = date_time_converter.db_datetime(db_txn_created_time)
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
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_conig_tid,
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
                    "org_code": org_code,
                    "status": "FAILED",
                    "username": app_username,
                    "tid": res_generateqr_tid,
                    "mid": res_generateqr_mid,
                    "additional_field1": res_generateqr_publish_id,
                    "upi_mc_id": db_upi_mc_id,
                    "payment_mode": "UPI",
                    "resp_code": "Failed",
                    "txn_type": "STATIC_QR",
                    "rrn": rrn
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id = '{str(db_txn_id)}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                db_upi_txn_additional_field1 = result["additional_field1"].values[0]
                logger.debug(f"Fetching upi additional field1 from db : {db_upi_txn_additional_field1}")
                db_upi_txn_resp_code = result["resp_code"].values[0]
                logger.debug(f"Fetching upi response code from db : {db_upi_txn_resp_code}")
                db_upi_txn_org_code = result["org_code"].values[0]
                logger.debug(f"Fetching upi org code from db : {db_upi_txn_org_code}")
                db_upi_txn_status = result["status"].values[0]
                logger.debug(f"Fetching upi txn status from db : {db_upi_txn_status}")
                db_upi_txn_txn_type = result["txn_type"].values[0]
                logger.debug(f"Fetching upi txn type from db : {db_upi_txn_txn_type}")
                db_upi_txn_upi_mc_id = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching upi mc id from db : {db_upi_txn_upi_mc_id}")

                actual_db_values = {
                    "amount": db_txn_amount,
                    "bank_code": db_txn_bank_code,
                    "org_code": db_upi_txn_org_code,
                    "status": db_upi_txn_status,
                    "username": db_txn_username,
                    "tid": db_txn_tid,
                    "mid": db_txn_mid,
                    "upi_mc_id": db_upi_txn_upi_mc_id,
                    "additional_field1": db_upi_txn_additional_field1,
                    "payment_mode": db_txn_payment_mode,
                    "resp_code": db_upi_txn_resp_code,
                    "txn_type": db_upi_txn_txn_type,
                    "rrn": db_rrn
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
                    "pmt_type": "UPI",
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
def test_common_100_108_040():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Duplicate_Callback_Via_HDFC_MINTOAK
    Sub Feature Description: Verifying static qr duplicate Callback case for UPI with same rrn and same txn ref  not to create new txn
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 040: Testcase ID
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
        db_bqr_conig_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_conig_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_config_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched merchantId is : {db_upi_config_merchant_id}")
        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched id is : {db_upi_config_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_bqr_config_id)

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_conig_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc_mintoak api is : {response}")
            res_generateqr_publish_id = response["publishId"]
            logger.debug(f"generated publish ID is : {res_generateqr_publish_id}")
            amount = random.randint(251, 300)
            logger.debug(f"generated random amount is : {amount}")

            logger.debug(f"preparing data to perform the encryption generation")
            txn_id = "231129064936760E" + str(random.randint(10000000, 999999999))
            logger.debug(f"txn_id generated : {txn_id}")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"mtxn_id generated : {mtxn_id}")
            rrn = str(random.randint(10000000, 99999999))
            logger.debug(f"rrn generated : {rrn}")

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = db_bqr_conig_tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"
            api_details_encryption['RequestBody']['payload']['description'] = "Static QR"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": db_bqr_conig_tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            logger.debug(f"encryptedData received for second mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": db_bqr_conig_tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for second callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for second callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}' order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            logger.debug(f"Fetching information from the database for the current transaction:")
            db_txn_id = result["id"].values[0]
            logger.debug(f"DB Transaction ID: {db_txn_id}")
            db_txn_auth_code = result["auth_code"].values[0]
            logger.debug(f"DB Transaction Auth Code: {db_txn_auth_code}")
            db_txn_amount = result["amount"].values[0]
            logger.debug(f"DB Transaction Amount: {db_txn_amount}")
            db_txn_bank_code = result["bank_code"].values[0]
            logger.debug(f"DB Transaction Bank Code: {db_txn_bank_code}")
            db_txn_username = result["username"].values[0]
            logger.debug(f"DB Transaction Username: {db_txn_username}")
            db_txn_tid = result["tid"].values[0]
            logger.debug(f"DB Transaction TID: {db_txn_tid}")
            db_txn_mid = result["mid"].values[0]
            logger.debug(f"DB Transaction MID: {db_txn_mid}")
            db_txn_payment_mode = result["payment_mode"].values[0]
            logger.debug(f"DB Transaction Payment Mode: {db_txn_payment_mode}")
            txn_created_time = result["created_time"].values[0]
            logger.debug(f"Transaction Created Time: {txn_created_time}")
            db_txn_rrn = result["rr_number"].values[0]
            logger.debug(f"DB Transaction RRN: {db_txn_rrn}")
            db_txn_ref = result["external_ref"].values[0]
            logger.debug(f"DB Transaction Reference: {db_txn_ref}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}' order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            db_txn_id_2 = result["id"].values[0]
            logger.debug(f"Fetching Transaction ID from txn table : {db_txn_id_2}")
            db_txn_amount_2 = result["amount"].values[0]
            logger.debug(f"Fetching Amount from txn table : {db_txn_amount_2}")
            db_txn_bank_code_2 = result["bank_code"].values[0]
            logger.debug(f"Fetching Bank Code from txn table : {db_txn_bank_code_2}")
            db_org_code_2 = result["org_code"].values[0]
            logger.debug(f"Fetching Organization Code from txn table : {db_org_code_2}")
            db_txn_username_2 = result["username"].values[0]
            logger.debug(f"Fetching Username from txn table : {db_txn_username_2}")
            db_txn_tid_2 = result["tid"].values[0]
            logger.debug(f"Fetching TID from txn table : {db_txn_tid_2}")
            db_txn_mid_2 = result["mid"].values[0]
            logger.debug(f"Fetching MID from txn table : {db_txn_mid_2}")
            db_txn_payment_mode_2 = result["payment_mode"].values[0]
            logger.debug(f"Fetching Payment Mode from txn table : {db_txn_payment_mode_2}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": db_txn_id,
                    "rrn": str(rrn),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
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
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(db_txn_id_2)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {db_txn_id_2}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {db_txn_id_2}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {db_txn_id_2}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {db_txn_id_2}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {db_txn_id_2}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {db_txn_id_2}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {db_txn_id_2}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching app_rrn from txn history for the txn : {db_txn_id_2}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg
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
                    f"status_api,status_api,payment_mode_api,state_api,rrn_api,settlement_status_api,issuer_code_api,acquirer_code_api,org_code_api,mid_api,tid_api,txn_type_api")
                logger.debug(
                    f"{status_api},{status_api},{payment_mode_api},{state_api},{rrn_api},{settlement_status_api},{issuer_code_api},{acquirer_code_api},{org_code_api},{mid_api},{tid_api},{txn_type_api}")

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
                    f"status_api_2,status_api_2,payment_mode_api_2,state_api_2,rrn_api_2,settlement_status_api_2,issuer_code_api_2,acquirer_code_api_2,org_code_api_2,mid_api_2,tid_api_2,txn_type_api_2")
                logger.debug(
                    f"{status_api_2},{status_api_2},{payment_mode_api_2},{state_api_2},{rrn_api_2},{settlement_status_api_2},{issuer_code_api_2},{acquirer_code_api_2},{org_code_api_2},{mid_api_2},{tid_api_2},{txn_type_api_2}")

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
                query = f"select * from upi_txn where txn_id = '{db_txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_txn_txn_ref = result["txn_ref"].values[0]
                logger.debug(f"Fetching Transaction Reference from upi_txn table: {upi_txn_txn_ref}")
                upi_txn_additional_field1 = result["additional_field1"].values[0]
                logger.debug(f"Fetching Additional Field 1 from upi_txn table: {upi_txn_additional_field1}")
                upi_txn_additional_field2 = result["additional_field2"].values[0]
                logger.debug(f"Fetching Additional Field 2 from upi_txn table: {upi_txn_additional_field2}")
                upi_txn_additional_field3 = result["additional_field3"].values[0]
                logger.debug(f"Fetching Additional Field 3 from upi_txn table: {upi_txn_additional_field3}")
                upi_txn_resp_code = result["resp_code"].values[0]
                logger.debug(f"Fetching Response Code from upi_txn table: {upi_txn_resp_code}")
                upi_txn_org_code = result["org_code"].values[0]
                logger.debug(f"Fetching Organization Code from upi_txn table: {upi_txn_org_code}")
                upi_txn_status = result["status"].values[0]
                logger.debug(f"Fetching Status from upi_txn table: {upi_txn_status}")
                upi_txn_type = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type from upi_txn table: {upi_txn_type}")

                query = f"select * from upi_txn where txn_id = '{db_txn_id_2}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_txn_txn_ref_2 = result["txn_ref"].values[0]
                logger.debug(f"Fetching Transaction Reference from upi_txn table: {upi_txn_txn_ref_2}")
                upi_txn_additional_field1_2 = result["additional_field1"].values[0]
                logger.debug(f"Fetching Additional Field 1 from upi_txn table: {upi_txn_additional_field1_2}")
                upi_txn_additional_field2_2 = result["additional_field2"].values[0]
                logger.debug(f"Fetching Additional Field 2 from upi_txn table: {upi_txn_additional_field2_2}")
                upi_txn_additional_field3_2 = result["additional_field3"].values[0]
                logger.debug(f"Fetching Additional Field 3 from upi_txn table: {upi_txn_additional_field3_2}")
                upi_txn_resp_code_2 = result["resp_code"].values[0]
                logger.debug(f"Fetching Response Code from upi_txn table: {upi_txn_resp_code_2}")
                upi_txn_org_code_2 = result["org_code"].values[0]
                logger.debug(f"Fetching Organization Code from upi_txn table: {upi_txn_org_code_2}")
                upi_txn_status_2 = result["status"].values[0]
                logger.debug(f"Fetching Status from upi_txn table: {upi_txn_status_2}")
                upi_txn_type_2 = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type from upi_txn table: {upi_txn_type_2}")

                expected_db_values = {
                    "amount": db_txn_amount,
                    "bank_code": db_txn_bank_code,
                    "org_code": org_code,
                    "username": db_txn_username,
                    "tid": db_txn_tid,
                    "mid": db_txn_mid,
                    "payment_mode": db_txn_payment_mode,
                    "upi_txn_ref": upi_txn_txn_ref,
                    "upi_additional_field1": upi_txn_additional_field1,
                    "upi_additional_field2": upi_txn_additional_field2,
                    "upi_additional_field3": upi_txn_additional_field3,
                    "upi_resp_code": upi_txn_resp_code,
                    "upi_org_code": upi_txn_org_code,
                    "upi_txn_status": upi_txn_status,
                    "upi_txn_type": upi_txn_type
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "amount": db_txn_amount_2,
                    "bank_code": db_txn_bank_code_2,
                    "org_code": db_org_code_2,
                    "username": db_txn_username_2,
                    "tid": db_txn_tid_2,
                    "mid": db_txn_mid_2,
                    "payment_mode": db_txn_payment_mode_2,
                    "upi_txn_ref": upi_txn_txn_ref_2,
                    "upi_additional_field1": upi_txn_additional_field1_2,
                    "upi_additional_field2": upi_txn_additional_field2_2,
                    "upi_additional_field3": upi_txn_additional_field3_2,
                    "upi_resp_code": upi_txn_resp_code_2,
                    "upi_org_code": upi_txn_org_code_2,
                    "upi_txn_status": upi_txn_status_2,
                    "upi_txn_type": upi_txn_type_2
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
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": db_txn_id_2,
                    "auth_code": '-' if db_txn_auth_code is None else db_txn_auth_code,
                    "rrn": '-' if db_txn_rrn is None else db_txn_rrn
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, db_txn_ref)
                logger.debug("Portal details for first TXN:")
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Date and Time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"Transaction ID: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Total Amount: {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code_portal: {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"Transaction Type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"Status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"Username: {username}")

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
