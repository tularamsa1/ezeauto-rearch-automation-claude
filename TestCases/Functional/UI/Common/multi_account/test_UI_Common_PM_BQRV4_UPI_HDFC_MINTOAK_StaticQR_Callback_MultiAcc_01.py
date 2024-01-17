import sys
import random
import pytest
from Configuration import testsuite_teardown, Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, Validator, date_time_converter, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_113_017():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Callback_Success_Via_HDFC_MINTOAK_MultiAcc_ActiveLabel
    Sub Feature Description: Multi Account - Verifying static qr upi success callback via HDFC_MINTOAK when label is active
    TC naming code description: 100: Payment method, 113: MultiAcc_StaticQR, 017: Testcase ID
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

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_conig_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_conig_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_mc_id = result['id'].values[0]
        logger.info(f"fetched id is : {db_upi_mc_id}")
        db_upi_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched acc_label_id : {db_upi_acc_label_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------PreConditions(Completed)-----------------------------------------
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
            logger.debug(f"res_generateqr_publish_id:{res_generateqr_publish_id}")
            res_generateqr_mid = response["mid"]
            logger.debug(f"res_generateqr_mid:{res_generateqr_mid}")
            res_generateqr_tid = response["tid"]
            logger.debug(f"res_generateqr_tid:{res_generateqr_tid}")
            logger.debug(f"Response received for static_qrcode_generate_hdfc_mintoak api is : {response}")

            amount = random.randint(251, 300)
            logger.debug(f"generated random amount is : {amount}")

            logger.debug(f"preparing data to perform the encryption generation")
            txn_id = "231129064936760E" + str(random.randint(10000000, 999999999))
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            rrn = str(random.randint(10000000, 99999999))
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

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}' order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            logger.debug("Fetching details for transaction:")
            db_txn_id = result["id"].values[0]
            logger.debug(f"Fetching DB Transaction ID from txn table: {db_txn_id}")
            db_auth_code = result["auth_code"].values[0]
            logger.debug(f"Fetching DB Auth Code from txn table: {db_auth_code}")
            db_txn_amount = result["amount"].values[0]
            logger.debug(f"Fetching DB Transaction Amount from txn table: {db_txn_amount}")
            db_txn_bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching DB Transaction Bank Code from txn table: {db_txn_bank_code}")
            db_txn_username = result["username"].values[0]
            logger.debug(f"Fetching DB Transaction Username from txn table: {db_txn_username}")
            db_txn_tid = result["tid"].values[0]
            logger.debug(f"Fetching DB Transaction TID from txn table: {db_txn_tid}")
            db_txn_mid = result["mid"].values[0]
            logger.debug(f"Fetching DB Transaction MID from txn table: {db_txn_mid}")
            db_txn_payment_mode = result["payment_mode"].values[0]
            logger.debug(f"Fetching DB Transaction Payment Mode from txn table: {db_txn_payment_mode}")
            db_txn_external_ref = result["external_ref"].values[0]
            logger.debug(f"Fetching DB Transaction External Reference from txn table: {db_txn_external_ref}")
            db_txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching DB Transaction Created Time from txn table: {db_txn_created_time}")
            db_txn_label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"Fetching DB Transaction Label IDs from txn table: {db_txn_label_ids}")

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
                logger.info(f"Fetching app_rrn from txn history for the txn : {db_txn_id}, {app_rrn}")

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
                    "date": date,
                    "account_label": str(account_label_name)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == db_txn_id][0]
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
                date_api = response["createdTime"]
                account_label_name_api = response["accountLabel"]
                logger.debug(
                    f"status_api,status_api,payment_mode_api,state_api,rrn_api,settlement_status_api,issuer_code_api,acquirer_code_api,org_code_api,mid_api,tid_api,txn_type_api,date_api,account_label_name_api")
                logger.debug(
                    f"{status_api},{status_api},{payment_mode_api},{state_api},{rrn_api},{settlement_status_api},{issuer_code_api},{acquirer_code_api},{org_code_api},{mid_api},{tid_api},{txn_type_api},{date_api},{account_label_name_api}")

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
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
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
                    "acc_label_id": str(db_upi_acc_label_id),
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id = '{db_txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                db_upi_txn_additional_field1 = result["additional_field1"].values[0]
                logger.debug(
                    f"Fetching UPI Transaction Additional Field 1 from upi_txn table : {db_upi_txn_additional_field1}")
                db_upi_txn_resp_code = result["resp_code"].values[0]
                logger.debug(f"Fetching UPI Transaction Response Code from upi_txn table : {db_upi_txn_resp_code}")
                db_upi_txn_org_code = result["org_code"].values[0]
                logger.debug(f"Fetching UPI Transaction Organization Code from upi_txn table : {db_upi_txn_org_code}")
                db_upi_txn_status = result["status"].values[0]
                logger.debug(f"Fetching UPI Transaction Status from upi_txn table : {db_upi_txn_status}")
                db_upi_txn_txn_type = result["txn_type"].values[0]
                logger.debug(f"Fetching UPI Transaction Type from upi_txn table : {db_upi_txn_txn_type}")
                db_upi_txn_upi_mc_id = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching UPI Transaction UPI MC ID from upi_txn table : {db_upi_txn_upi_mc_id}")

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
                    "acc_label_id": str(db_txn_label_ids),
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
                    "auth_code": "-" if db_auth_code is None else db_auth_code,
                    "rrn": str(rrn),
                    "acc_label": account_label_name
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         db_txn_external_ref)
                logger.debug("Fetching Portal Details for Transaction:")
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
                labels = transaction_details[0]['Labels']
                logger.debug(f"Labels: {labels}")

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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(db_txn_created_time)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    "AUTH CODE": '' if db_auth_code is None else db_auth_code
                }
                receipt_validator.perform_charge_slip_validations(db_txn_id, {
                    "username": app_username, "password": app_password}, expected_charge_slip_values)
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
@pytest.mark.chargeSlipVal
def test_common_100_113_018():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Callback_Success_Via_HDFC_MINTOAK_MultiAcc_InactiveLabel
    Sub Feature Description: Multi Account - Verifying static qr upi success callback via HDFC_MINTOAK when label is inactive
    TC naming code description: 100: Payment method, 113: MultiAcc_StaticQR, 018: Testcase ID
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
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(org_code,
                                                                                       portal_un=portal_username,
                                                                                       portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")

        setting_value = '{"name":"' + f"{account_label_name}" + '","status":"ACTIVE"}'
        setting_value_inactive = '{"name":"' + f"{account_label_name}" + '","status":"INACTIVE"}'
        query = f"select * from account_labels where org_code='{org_code}' and setting_value='{setting_value}';"
        logger.debug(f"Query to fetch account_labels data from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        account_labels_id = result['id'].values[0]
        logger.debug(f"Query result, account_labels_id : {account_labels_id}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_conig_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_conig_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_config_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched merchantId is : {db_upi_config_merchant_id}")
        db_upi_mc_id = result['id'].values[0]
        logger.info(f"fetched id is : {db_upi_mc_id}")
        db_upi_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched acc_label_id : {db_upi_acc_label_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------PreConditions(Completed)-----------------------------------------
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
            logger.debug(f"res_generateqr_publish_id:{res_generateqr_publish_id}")
            res_generateqr_mid = response["mid"]
            logger.debug(f"res_generateqr_mid:{res_generateqr_mid}")
            res_generateqr_tid = response["tid"]
            logger.debug(f"res_generateqr_tid:{res_generateqr_tid}")
            logger.debug(f"Response received for static_qrcode_generate_hdfc_mintoak api is : {response}")
            amount = random.randint(251, 300)
            logger.debug(f"generated random amount is : {amount}")

            query = f"update account_labels set setting_value='{setting_value_inactive}' where id='{account_labels_id}';"
            logger.debug(
                f"query : {query}, to make setting_value : {setting_value}, inactive for org_code : {org_code}")
            DBProcessor.setValueToDB(query)
            api_details = DBProcessor.get_api_details('DB Refresh', request_body={
                "username": portal_username, "password": portal_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for DB refresh is : {response}")

            logger.debug(f"preparing data to perform the encryption generation")
            txn_id = "231129064936760E" + str(random.randint(10000000, 999999999))
            logger.debug(f"Generated Txn ID :{txn_id}")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generated mtxn_id :{mtxn_id}")
            rrn = str(random.randint(10000000, 99999999))
            logger.debug(f"Generated rrn :{rrn}")
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
            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}' order by created_time desc limit 1; "

            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            logger.debug("Fetching Transaction Details:")
            db_txn_id = result["id"].values[0]
            logger.debug(f"Fetching db_txn_id from txn table: {db_txn_id}")
            db_auth_code = result["auth_code"].values[0]
            logger.debug(f"Fetching db_auth_code from txn table: {db_auth_code}")
            db_txn_amount = result["amount"].values[0]
            logger.debug(f"Fetching db_txn_amount from txn table: {db_txn_amount}")
            db_txn_bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching db_txn_bank_code from txn table: {db_txn_bank_code}")
            db_txn_username = result["username"].values[0]
            logger.debug(f"Fetching db_txn_username from txn table: {db_txn_username}")
            db_txn_tid = result["tid"].values[0]
            logger.debug(f"Fetching db_txn_tid from txn table: {db_txn_tid}")
            db_txn_mid = result["mid"].values[0]
            logger.debug(f"Fetching db_txn_mid from txn table: {db_txn_mid}")
            db_txn_payment_mode = result["payment_mode"].values[0]
            logger.debug(f"Fetching db_txn_payment_mode from txn table: {db_txn_payment_mode}")
            db_txn_external_ref = result["external_ref"].values[0]
            logger.debug(f"Fetching db_txn_external_ref from txn table: {db_txn_external_ref}")
            db_txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching db_txn_created_time from txn table: {db_txn_created_time}")
            db_txn_label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"Fetching db_txn_label_ids from txn table: {db_txn_label_ids}")

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
                logger.info(f"Fetching app_rrn from txn history for the txn : {db_txn_id}, {app_rrn}")

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
                    "date": date,
                    "account_label": str(account_label_name)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == db_txn_id][0]
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
                date_api = response["createdTime"]
                account_label_name_api = response["accountLabel"]
                logger.debug(
                    f"status_api,status_api,payment_mode_api,state_api,rrn_api,settlement_status_api,issuer_code_api,acquirer_code_api,org_code_api,mid_api,tid_api,txn_type_api,date_api,account_label_name_api")
                logger.debug(
                    f"{status_api},{status_api},{payment_mode_api},{state_api},{rrn_api},{settlement_status_api},{issuer_code_api},{acquirer_code_api},{org_code_api},{mid_api},{tid_api},{txn_type_api},{date_api},{account_label_name_api}")

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
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
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
                    "acc_label_id": str(db_upi_acc_label_id),
                    "rrn": rrn
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id = '{db_txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                logger.debug("Fetching UPI Transaction Details:")
                db_upi_txn_additional_field1 = result["additional_field1"].values[0]
                logger.debug(
                    f"Fetching db_upi_txn_additional_field1 from upi_txn table: {db_upi_txn_additional_field1}")
                db_upi_txn_resp_code = result["resp_code"].values[0]
                logger.debug(f"Fetching db_upi_txn_resp_code from upi_txn table: {db_upi_txn_resp_code}")
                db_upi_txn_org_code = result["org_code"].values[0]
                logger.debug(f"Fetching db_upi_txn_org_code from upi_txn table: {db_upi_txn_org_code}")
                db_upi_txn_status = result["status"].values[0]
                logger.debug(f"Fetching db_upi_txn_status from upi_txn table: {db_upi_txn_status}")
                db_upi_txn_txn_type = result["txn_type"].values[0]
                logger.debug(f"Fetching db_upi_txn_txn_type from upi_txn table: {db_upi_txn_txn_type}")
                db_upi_txn_upi_mc_id = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching db_upi_txn_upi_mc_id from upi_txn table: {db_upi_txn_upi_mc_id}")

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
                    "acc_label_id": str(db_txn_label_ids),
                    "rrn": rrn
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
                    "auth_code": "-" if db_auth_code is None else db_auth_code,
                    "rrn": str(rrn),
                    "acc_label": account_label_name
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         db_txn_external_ref)
                logger.debug("Portal details for TXN:")
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
                labels = transaction_details[0]['Labels']
                logger.debug(f"Labels: {labels}")

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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(db_txn_created_time)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if db_auth_code is None else db_auth_code
                }
                receipt_validator.perform_charge_slip_validations(db_txn_id, {
                    "username": app_username, "password": app_password}, expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
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
            query = f"update account_labels set setting_value='{setting_value}' where setting_value='{setting_value_inactive}' and org_code='{org_code}';"
            logger.debug(f"query : {query} to make setting_value : {setting_value}, active for org_code : {org_code}")
        DBProcessor.setValueToDB(query)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username, "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        Configuration.executeFinallyBlock(testcase_id)
