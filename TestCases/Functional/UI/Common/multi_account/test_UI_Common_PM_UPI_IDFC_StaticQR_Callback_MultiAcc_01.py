import random
import sys
from datetime import datetime
import pytest
from Configuration import testsuite_teardown, Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
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
def test_common_100_113_007():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Callback_Success_Via_IDFC_MultiAcc_ActiveLabel
    Sub Feature Description: Multi Account - Verifying  a upi success callback via IDFC for StaticQR when label is active
    TC naming code description:: 100: Payment method, 113: MultiAcc_StaticQR, 007: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get details from upi_merchant_config table
        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'IDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"

        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result : {result}")

        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")

        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")

        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        db_upi_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched acc_label_id : {db_upi_acc_label_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            res_generateqr_publish_id = response["publishId"]

            # Generate HMAC and MerchCreds
            amount = random.randint(201, 399)
            logger.debug(f"generated random amount is : {amount}")

            orig_cust_ref_id = random.randint(11111110, 99999999)

            logger.debug(f"generated random org_cust_ref_id is : {orig_cust_ref_id}")

            ResCode = "000"
            req_merch_creds = "fCef5gQC8s861hBigj+NX7QTY7HuNjbRncLxYnphVJA="
            req_hmac = "8066ac67ef88ea969f0ca50a2c5f43b9ac298ab761b94e778e25d015faaf89b6"

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body={
                "MerchantCredential": req_merch_creds,
                "ResCode": ResCode,
                "HMAC": req_hmac,
                "Amount": amount,
                "PayeeVirAddr": db_upi_config_vpa,
                "MerchantID": db_upi_config_mid,
                "OrgCustRefId": orig_cust_ref_id,
                "OrgTxnRefId": res_generateqr_publish_id,
                "TerminalID": db_upi_config_tid, })
            response1 = APIProcessor.send_request(api_details)
            logger.debug(f"First response received for hmac_merch_cred api is : {response}")
            response_merch_creds = response1.text.replace("\n", "")

            sub_string1 = "MerchantCreds="
            sub_string2 = "HMAC="

            index1 = response_merch_creds.index(sub_string1)
            index2 = response_merch_creds.index(sub_string2)
            generated_merch_creds = response_merch_creds[index1 + len(sub_string1): index2]
            logger.debug(f"Generated MerchCreds is : {generated_merch_creds}")

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body=
            {"MerchantCredential": generated_merch_creds,
             "ResCode": ResCode,
             "HMAC": req_hmac,
             "Amount": amount,
             "PayeeVirAddr": db_upi_config_vpa,
             "MerchantID": db_upi_config_mid,
             "OrgCustRefId": orig_cust_ref_id,
             "OrgTxnRefId": res_generateqr_publish_id,
             "TerminalID": db_upi_config_tid, })
            response2 = APIProcessor.send_request(api_details)
            response_hmac = response2.text

            res = response_hmac.split('HMAC=', 1)
            generated_hmac = res[1]

            logger.debug(f"Second response received : {str(response_hmac)}")
            logger.debug(f"Value of HMAC is : {generated_hmac}")

            req_payload3 = {
                "MerchantCredential": generated_merch_creds,
                "ResCode": ResCode,
                "HMAC": generated_hmac,
                "Amount": amount,
                "PayeeVirAddr": db_upi_config_vpa,
                "MerchantID": db_upi_config_mid,
                "OrgCustRefId": orig_cust_ref_id,
                "OrgTxnRefId": res_generateqr_publish_id,
                "TerminalID": db_upi_config_tid,
            }

            # UPI Callback
            api_details = DBProcessor.get_api_details('staticQR_UPI_IDFC_callback', request_body=req_payload3)
            response = APIProcessor.send_request(api_details)

            logger.debug(f"Response received for staticQR_UPI_IDFC_callback api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and rr_number = '" + str(
                orig_cust_ref_id) + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from txn table : {query}")

            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")

            txn_id = result["id"].iloc[0]
            logger.debug(f"fetched id from txn table is : {txn_id}")
            txn_type = result["txn_type"].iloc[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            txn_amt = result["amount"].iloc[0]
            logger.debug(f"fetched amount from txn table is : {txn_amt}")
            txn_bank_code = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {txn_bank_code}")
            txn_issuer_code = result["issuer_code"].iloc[0]
            logger.debug(f"fetched issuer_code from txn table is : {txn_issuer_code}")
            txn_username = result["username"].iloc[0]
            logger.debug(f"fetched username from txn table is : {txn_username}")
            txn_tid = result["tid"].iloc[0]
            logger.debug(f"fetched tid from txn table is : {txn_tid}")
            txn_mid = result["mid"].iloc[0]
            logger.debug(f"fetched mid from txn table is : {txn_mid}")
            txn_acquirer_code = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {txn_acquirer_code}")
            txn_pmt_mode = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {txn_pmt_mode}")
            txn_pmt_status = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {txn_pmt_status}")
            txn_pmt_state = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {txn_pmt_state}")
            txn_settle_status = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {txn_settle_status}")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {txn_created_time}")
            txn_label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {txn_label_ids}")

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
                date_and_time = date_time_converter.to_app_format(txn_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(orig_cust_ref_id),
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
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

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
                date = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(orig_cust_ref_id),
                    "settle_status": "SETTLED",
                    "acquirer_code": "IDFC",
                    "issuer_code": "IDFC",
                    "txn_type": txn_type,
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date,
                    "account_label": str(account_label_name)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])
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
                date_api = response["createdTime"]
                account_label_name_api = response["accountLabel"]

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
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
                    "txn_amt": amount,
                    "txn_type": "CHARGE",
                    "bank_code": "IDFC",
                    "issuer_code": "IDFC",
                    "username": app_username,
                    "tid": db_upi_config_tid,
                    "mid": db_upi_config_mid,
                    "acquirer_code": "IDFC",
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "upi_customer_ref": str(orig_cust_ref_id),
                    "upi_org_code": org_code,
                    "upi_status": "AUTHORIZED",
                    "upi_additional_field1": res_generateqr_publish_id,
                    "upi_additional_field2": res_generateqr_publish_id,
                    "upi_mc_id": db_upi_config_id,
                    "upi_resp_code": "000",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "IDFC",
                    "acc_label_id": str(db_upi_acc_label_id),
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id = '" + str(txn_id) + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")

                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_additional_field1 = result["additional_field1"].iloc[0]
                upi_additional_field2 = result["additional_field2"].iloc[0]
                upi_resp_code = result["resp_code"].iloc[0]
                upi_customer_ref = result["customer_ref"].iloc[0]
                upi_org_code = result["org_code"].iloc[0]
                upi_bank_code = result["bank_code"].iloc[0]
                upi_status = result["status"].iloc[0]
                upi_txn_type = result["txn_type"].iloc[0]
                upi_upi_mc_id = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "txn_amt": txn_amt,
                    "txn_type": txn_type,
                    "bank_code": txn_bank_code,
                    "issuer_code": txn_issuer_code,
                    "username": txn_username,
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "acquirer_code": txn_acquirer_code,
                    "pmt_mode": txn_pmt_mode,
                    "pmt_status": txn_pmt_status,
                    "pmt_state": txn_pmt_state,
                    "settle_status": txn_settle_status,
                    "upi_customer_ref": upi_customer_ref,
                    "upi_org_code": upi_org_code,
                    "upi_status": upi_status,
                    "upi_additional_field1": upi_additional_field1,
                    "upi_additional_field2": upi_additional_field2,
                    "upi_mc_id": upi_upi_mc_id,
                    "upi_resp_code": upi_resp_code,
                    "upi_txn_type": upi_txn_type,
                    "upi_bank_code": upi_bank_code,
                    "acc_label_id": str(txn_label_ids),
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
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                actual_portal_values = {}
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                expected_values = {
                    'PAID BY:': 'UPI', 'RRN': str(orig_cust_ref_id), 'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date, 'time': txn_time,
                }
                receipt_validator.perform_charge_slip_validations(txn_id, {
                    "username": app_username, "password": app_password}, expected_values)
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
def test_common_100_113_008():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Callback_Success_Via_IDFC_MultiAcc_InactiveLabel
    Sub Feature Description: Multi Account - Verifying  a upi success callback via IDFC for StaticQR when label is inactive
    TC naming code description:: 100: Payment method, 113: MultiAcc_StaticQR, 008: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")

        setting_value = '{"name":"' + f"{account_label_name}" + '","status":"ACTIVE"}'
        setting_value_inactive = '{"name":"' + f"{account_label_name}" + '","status":"INACTIVE"}'
        query = f"select * from account_labels where org_code='{org_code}' and setting_value='{setting_value}';"
        logger.debug(f"Query to fetch account_labels data from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        account_labels_id = result['id'].values[0]
        logger.debug(f"Query result, account_labels_id : {account_labels_id}")
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get details from upi_merchant_config table
        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'IDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"

        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result : {result}")

        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")

        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")

        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        db_upi_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched acc_label_id : {db_upi_acc_label_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            res_generateqr_publish_id = response["publishId"]

            # Generate HMAC and MerchCreds
            amount = random.randint(201, 399)
            logger.debug(f"generated random amount is : {amount}")

            orig_cust_ref_id = random.randint(11111110, 99999999)

            logger.debug(f"generated random org_cust_ref_id is : {orig_cust_ref_id}")

            ResCode = "000"
            req_merch_creds = "fCef5gQC8s861hBigj+NX7QTY7HuNjbRncLxYnphVJA="
            req_hmac = "8066ac67ef88ea969f0ca50a2c5f43b9ac298ab761b94e778e25d015faaf89b6"

            query = f"update account_labels set setting_value='{setting_value_inactive}' where id='{account_labels_id}';"
            logger.debug(
                f"query : {query}, to make setting_value : {setting_value}, inactive for org_code : {org_code}")
            DBProcessor.setValueToDB(query)
            api_details = DBProcessor.get_api_details('DB Refresh', request_body={
                "username": portal_username, "password": portal_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for DB refresh is : {response}")

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body={
                "MerchantCredential": req_merch_creds,
                "ResCode": ResCode,
                "HMAC": req_hmac,
                "Amount": amount,
                "PayeeVirAddr": db_upi_config_vpa,
                "MerchantID": db_upi_config_mid,
                "OrgCustRefId": orig_cust_ref_id,
                "OrgTxnRefId": res_generateqr_publish_id,
                "TerminalID": db_upi_config_tid, })
            response1 = APIProcessor.send_request(api_details)
            logger.debug(f"First response received for hmac_merch_cred api is : {response}")
            response_merch_creds = response1.text.replace("\n", "")

            sub_string1 = "MerchantCreds="
            sub_string2 = "HMAC="

            index1 = response_merch_creds.index(sub_string1)
            index2 = response_merch_creds.index(sub_string2)
            generated_merch_creds = response_merch_creds[index1 + len(sub_string1): index2]
            logger.debug(f"Generated MerchCreds is : {generated_merch_creds}")

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body=
            {"MerchantCredential": generated_merch_creds,
             "ResCode": ResCode,
             "HMAC": req_hmac,
             "Amount": amount,
             "PayeeVirAddr": db_upi_config_vpa,
             "MerchantID": db_upi_config_mid,
             "OrgCustRefId": orig_cust_ref_id,
             "OrgTxnRefId": res_generateqr_publish_id,
             "TerminalID": db_upi_config_tid, })
            response2 = APIProcessor.send_request(api_details)
            response_hmac = response2.text

            res = response_hmac.split('HMAC=', 1)
            generated_hmac = res[1]

            logger.debug(f"Second response received : {str(response_hmac)}")
            logger.debug(f"Value of HMAC is : {generated_hmac}")

            req_payload3 = {
                "MerchantCredential": generated_merch_creds,
                "ResCode": ResCode,
                "HMAC": generated_hmac,
                "Amount": amount,
                "PayeeVirAddr": db_upi_config_vpa,
                "MerchantID": db_upi_config_mid,
                "OrgCustRefId": orig_cust_ref_id,
                "OrgTxnRefId": res_generateqr_publish_id,
                "TerminalID": db_upi_config_tid,
            }

            # UPI Callback
            api_details = DBProcessor.get_api_details('staticQR_UPI_IDFC_callback', request_body=req_payload3)
            response = APIProcessor.send_request(api_details)

            logger.debug(f"Response received for staticQR_UPI_IDFC_callback api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and rr_number = '" + str(
                orig_cust_ref_id) + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from txn table : {query}")

            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")

            txn_id = result["id"].iloc[0]
            logger.debug(f"fetched id from txn table is : {txn_id}")
            txn_type = result["txn_type"].iloc[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            txn_amt = result["amount"].iloc[0]
            logger.debug(f"fetched amount from txn table is : {txn_amt}")
            txn_bank_code = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {txn_bank_code}")
            txn_issuer_code = result["issuer_code"].iloc[0]
            logger.debug(f"fetched issuer_code from txn table is : {txn_issuer_code}")
            txn_username = result["username"].iloc[0]
            logger.debug(f"fetched username from txn table is : {txn_username}")
            txn_tid = result["tid"].iloc[0]
            logger.debug(f"fetched tid from txn table is : {txn_tid}")
            txn_mid = result["mid"].iloc[0]
            logger.debug(f"fetched mid from txn table is : {txn_mid}")
            txn_acquirer_code = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {txn_acquirer_code}")
            txn_pmt_mode = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {txn_pmt_mode}")
            txn_pmt_status = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {txn_pmt_status}")
            txn_pmt_state = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {txn_pmt_state}")
            txn_settle_status = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {txn_settle_status}")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {txn_created_time}")
            txn_label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {txn_label_ids}")

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
                date_and_time = date_time_converter.to_app_format(txn_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(orig_cust_ref_id),
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
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

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
                date = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(orig_cust_ref_id),
                    "settle_status": "SETTLED",
                    "acquirer_code": "IDFC",
                    "issuer_code": "IDFC",
                    "txn_type": txn_type,
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date,
                    "account_label": str(account_label_name)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])
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
                date_api = response["createdTime"]
                account_label_name_api = response["accountLabel"]

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
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
                    "txn_amt": amount,
                    "txn_type": "CHARGE",
                    "bank_code": "IDFC",
                    "issuer_code": "IDFC",
                    "username": app_username,
                    "tid": db_upi_config_tid,
                    "mid": db_upi_config_mid,
                    "acquirer_code": "IDFC",
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "upi_customer_ref": str(orig_cust_ref_id),
                    "upi_org_code": org_code,
                    "upi_status": "AUTHORIZED",
                    "upi_additional_field1": res_generateqr_publish_id,
                    "upi_additional_field2": res_generateqr_publish_id,
                    "upi_mc_id": db_upi_config_id,
                    "upi_resp_code": "000",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "IDFC",
                    "acc_label_id": str(db_upi_acc_label_id),
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id = '" + str(txn_id) + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")

                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_additional_field1 = result["additional_field1"].iloc[0]
                upi_additional_field2 = result["additional_field2"].iloc[0]
                upi_resp_code = result["resp_code"].iloc[0]
                upi_customer_ref = result["customer_ref"].iloc[0]
                upi_org_code = result["org_code"].iloc[0]
                upi_bank_code = result["bank_code"].iloc[0]
                upi_status = result["status"].iloc[0]
                upi_txn_type = result["txn_type"].iloc[0]
                upi_upi_mc_id = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "txn_amt": txn_amt,
                    "txn_type": txn_type,
                    "bank_code": txn_bank_code,
                    "issuer_code": txn_issuer_code,
                    "username": txn_username,
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "acquirer_code": txn_acquirer_code,
                    "pmt_mode": txn_pmt_mode,
                    "pmt_status": txn_pmt_status,
                    "pmt_state": txn_pmt_state,
                    "settle_status": txn_settle_status,
                    "upi_customer_ref": upi_customer_ref,
                    "upi_org_code": upi_org_code,
                    "upi_status": upi_status,
                    "upi_additional_field1": upi_additional_field1,
                    "upi_additional_field2": upi_additional_field2,
                    "upi_mc_id": upi_upi_mc_id,
                    "upi_resp_code": upi_resp_code,
                    "upi_txn_type": upi_txn_type,
                    "upi_bank_code": upi_bank_code,
                    "acc_label_id": str(txn_label_ids),
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
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                actual_portal_values = {}
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                expected_values = {
                    'PAID BY:': 'UPI', 'RRN': str(orig_cust_ref_id), 'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date, 'time': txn_time,
                }
                receipt_validator.perform_charge_slip_validations(txn_id, {
                    "username": app_username, "password": app_password}, expected_values)
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
