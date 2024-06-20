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
def test_common_100_102_416():
    """
    Sub Feature Code: Tid_dep_UI_Common_BQRV4_UPI_Amount_Mismatch_Via_Pure_UPI_Success_Callback_HDFC_MINTOAK
    Sub Feature Description: Tid dep - Performing a amount mismatch using pure upi success callback via  HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQRV4, 416: TC416
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
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"bank_code='HDFC_MINTOAK'"
        logger.debug(f"Query to fetch details from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        terminal_info_id = result["terminal_info_id"].values[0]
        bqr_mc_id = result["id"].values[0]
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        query = f"select device_serial from terminal_info where tid = '{str(tid)}'"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

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

            amount = random.randint(251, 300)
            logger.debug(f"initiating BQR qr for the amount of {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating BQR qr for the order id {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })
            response = APIProcessor.send_request(api_details)
            txn_id = response["txnId"]
            order_id = response["externalRefNumber"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            new_amt = amount + 1
            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].values[0]
            logger.debug(f"Fetching Txn_id data base : Txn_id : {txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating random mtxn_id: {mtxn_id}")
            issuer_ref_number = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating random issuer_ref_number: {issuer_ref_number}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = new_amt
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

            query = f"select * from invalid_pg_request where request_id ='{txn_id}'"
            logger.debug(f"query to fetch data from the invalid_pg_request table : {query}")
            result = DBProcessor.getValueFromDB(query)
            ipr_txn_id = result['txn_id'].values[0]
            logger.debug(f"captured txn_id from invalid_pg_request table is : {ipr_txn_id}")
            ipr_payment_mode = result["payment_mode"].values[0]
            logger.debug(f"captured payment_mode from invalid_pg_request : {ipr_payment_mode}")
            ipr_bank_code = result["bank_code"].values[0]
            logger.debug(f"captured bank_code from invalid_pg_request : {ipr_bank_code}")
            ipr_org_code = result["org_code"].values[0]
            logger.debug(f"captured org_code from invalid_pg_request : {ipr_org_code}")
            ipr_amount = result["amount"].values[0]
            logger.debug(f"captured txn_amount from invalid_pg_request : {ipr_amount}")
            ipr_rrn = result["rrn"].values[0]
            logger.debug(f"captured rrn from invalid_pg_request : {ipr_rrn}")
            ipr_mid = result["mid"].values[0]
            logger.debug(f"captured mid from invalid_pg_request : {ipr_mid}")
            ipr_tid = result["tid"].values[0]
            logger.debug(f"captured tid from invalid_pg_request : {ipr_tid}")
            ipr_config_id = result["config_id"].values[0]
            logger.debug(f"captured config_id from invalid_pg_request : {ipr_config_id}")
            ipr_vpa = result["vpa"].values[0]
            logger.debug(f"captured vpa from invalid_pg_request : {ipr_vpa}")
            ipr_pg_merchant_id = result["pg_merchant_id"].values[0]
            logger.debug(f"captured pg_merchant_id from invalid_pg_request : {ipr_pg_merchant_id}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch data from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from txn table for txnId: {txn_id}")

            query = f"select * from txn where id = '{ipr_txn_id}'"
            logger.debug(f"Query to fetch data from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"captured org_code from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"captured txn_type from txn table is : {txn_type}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"captured posting_date from txn table is : {posting_date}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"captured external_ref from txn table is : {external_ref}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from db: {auth_code}")
            status_db = result["status"].values[0]
            logger.debug(f"Fetching status from db: {status_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"Fetching payment mode from db: {payment_mode_db}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"Fetching amount from db: {amount_db}")
            state_db = result["state"].values[0]
            logger.debug(f"Fetching state from db: {state_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment gateway from db: {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"Fetching acquirer code from db: {acquirer_code_db}")
            bank_code_db = result["bank_code"].values[0]
            logger.debug(f"Fetching bank code from db: {bank_code_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"Fetching settlement status from db: {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid from db: {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid from db: {mid_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from db: {rrn_db}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from db: {created_time}")

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
                    "pmt_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "txn_id": ipr_txn_id,
                    "txn_amt": "{:.2f}".format(new_amt),
                    "rrn": str(ipr_rrn),
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(ipr_txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {ipr_txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {ipr_txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {ipr_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {ipr_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {ipr_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {ipr_txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time,
                }
                logger.debug(f"actualAppValues: {actual_app_values}")

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
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": new_amt, "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED",
                    "rrn": str(ipr_rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == ipr_txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        org_code_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        date_api = elements["postingDate"]

                actual_api_values = {
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
                    "pmt_status": "UPG_AUTHORIZED",
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_mode": "UPI",
                    "txn_amt": new_amt,
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "MINTOAK",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "HDFC_MINTOAK",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "HDFC",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn_db),
                    "ipr_txn_amt": new_amt,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_config_id": upi_mc_id,
                    "device_serial": str(device_serial)
                }
                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{ipr_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"Fetching upi status from api for txn_id {ipr_txn_id} : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching upi txn type from api for txn_id {ipr_txn_id} : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching upi bank code from api for txn_id {ipr_txn_id} : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching upi mc id from api for txn_id {ipr_txn_id} : {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_config_id": ipr_config_id,
                    "device_serial": str(device_serial_db)
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(new_amt)}.00",
                    "username": "EZETAP",
                    "txn_id": ipr_txn_id,
                    "rrn": str(ipr_rrn),
                    "auth_code": "-" if auth_code is None else auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)
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
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
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
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_417():
    """
    Sub Feature Code:Tid_dep_UI_Common_BQRV4_UPI_Success_Callback_After_QR_Expiry_Auto_Refund_Disabled_HDFC_MINTOAK
    Sub Feature Description: Tid dep - Performing a pure upi success callback via HDFC_MINTOAK after expiry the qr when auto refund is disabled
    TC naming code description: 100: Payment Method, 102: BQR, 417: TC417
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

        query = f"select org_code from org_employee where username='{app_username}';"
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
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where " \
                f"org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        logger.debug("Fetching details from bharatqr_merchant_config table for current merchant:")
        logger.debug(f"Fetching MID: {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching TID: {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"Fetching Terminal Info ID: {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"Fetching BQR MC ID: {bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching BQR M PAN: {bqr_m_pan}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        query = f"select device_serial from terminal_info where tid = '{tid}';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ----------------------------------------PreConditions(Completed)--------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(251, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating BQR qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            logger.info("Waiting for QR to get expired")
            time.sleep(75)

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating mtxn_id : {mtxn_id}")
            rrn = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating issuer_ref_number : {rrn}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch transaction data from database : {query}")
            logger.debug("Fetching details from txn table for current merchant:")
            result = DBProcessor.getValueFromDB(query)
            posting_date = result['created_time'].values[0]
            logger.debug(f"Fetching posting_date from txn table: {posting_date}")
            status_db = result["status"].values[0]
            logger.debug(f"Fetching Status from txn table: {status_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"Fetching Payment Mode from txn table: {payment_mode_db}")
            amount_db = float(result["amount"].values[0])
            logger.debug(f"Fetching Amount from txn table: {amount_db}")
            state_db = result["state"].values[0]
            logger.debug(f"Fetching State from txn table: {state_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"Fetching Payment Gateway from txn table: {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"Fetching Acquirer Code from txn table: {acquirer_code_db}")
            bank_code_db = result["bank_code"].values[0]
            logger.debug(f"Fetching Bank Code from txn table: {bank_code_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"Fetching Settlement Status from txn table: {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching TID from txn table: {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching MID from txn table: {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching Device Serial from txn table: {device_serial_db}")
            order_id_db = result['external_ref'].values[0]
            logger.debug(f"Fetching Order ID from txn table: {order_id_db}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table: {auth_code}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result['id'].values[0]
            logger.debug(f"Fetching txn_id_new from txn table: {txn_id_new}")
            rrn_new = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_new from txn table: {rrn_new}")

            query = f"select * from txn where id = '{txn_id_new}';"
            logger.debug(f"Query to fetch transaction data from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug("Fetching details from txn table for current merchant:")
            posting_date_new = result['created_time'].values[0]
            logger.debug(f"Fetching posting_date_new from txn table: {posting_date_new}")
            status_db_new = result["status"].values[0]
            logger.debug(f"Fetching Status from txn table: {status_db_new}")
            payment_mode_db_new = result["payment_mode"].values[0]
            logger.debug(f"Fetching Payment Mode from txn table: {payment_mode_db_new}")
            amount_db_new = float(result["amount"].values[0])
            logger.debug(f"Fetching Amount from txn table: {amount_db_new}")
            state_db_new = result["state"].values[0]
            logger.debug(f"Fetching State from txn table: {state_db_new}")
            payment_gateway_db_new = result["payment_gateway"].values[0]
            logger.debug(f"Fetching Payment Gateway from txn table: {payment_gateway_db_new}")
            acquirer_code_db_new = result["acquirer_code"].values[0]
            logger.debug(f"Fetching Acquirer Code from txn table: {acquirer_code_db_new}")
            bank_code_db_new = result["bank_code"].values[0]
            logger.debug(f"Fetching Bank Code from txn table: {bank_code_db_new}")
            settlement_status_db_new = result["settlement_status"].values[0]
            logger.debug(f"Fetching Settlement Status from txn table: {settlement_status_db_new}")
            order_id_db_new = result['external_ref'].values[0]
            logger.debug(f"Fetching Order ID from txn table: {order_id_db_new}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table: {auth_code_2}")

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
                date_and_time_new = date_time_converter.to_app_format(posting_date_new)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "STATUS:EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "STATUS:AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_new,
                    "rrn_2": rrn_new,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_new
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
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
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id_new}, {app_rrn_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id_2}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2,
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": app_rrn_2,
                    "settle_status_2": app_settlement_status_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "date_2": app_date_and_time_2
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
                date_2 = date_time_converter.db_datetime(posting_date_new)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "order_id": order_id,
                    "txn_type": "CHARGE", "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount_db_new), "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "rrn_2": rrn_new,
                    "order_id_2": order_id_db_new,
                    "txn_type_2": "CHARGE",
                    "date_2": date_2,
                    "device_serial": str(device_serial)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response_list = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response_list["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]
                device_serial_api = response["deviceSerial"]
                order_id_api = response["orderNumber"]
                logger.debug(
                    f"API Details for original txn : status:{status_api}, amount:{amount_api}, payment mode:{payment_mode_api}, state:{state_api}, settlement status:{settlement_status_api}, issuer code:{issuer_code_api}, acquirer code:{acquirer_code_api}, org code:{org_code_api}, mid:{mid_api}, tid:{tid_api}, txn type:{txn_type_api}, date:{date_api}")

                response = [x for x in response_list["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_2 = response["status"]
                amount_api_2 = float(response["amount"])
                payment_mode_api_2 = response["paymentMode"]
                state_api_2 = response["states"][0]
                settlement_status_api_2 = response["settlementStatus"]
                issuer_code_api_2 = response["issuerCode"]
                acquirer_code_api_2 = response["acquirerCode"]
                txn_type_api_2 = response["txnType"]
                date_api_2 = response["createdTime"]
                order_id_api_2 = response["orderNumber"]
                rrn_api_2 = response["rrNumber"]
                logger.debug(
                    f"API Details for original txn : status:{status_api_2}, amount:{amount_api_2}, payment mode:{payment_mode_api_2}, state:{state_api_2}, settlement status:{settlement_status_api_2}, issuer code:{issuer_code_api_2}, acquirer code:{acquirer_code_api_2}, txn type:{txn_type_api_2}, date:{date_api_2}")

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "order_id": order_id_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2, "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "order_id_2": order_id_api_2,
                    "rrn_2": rrn_api_2,
                    "txn_type_2": txn_type_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "device_serial": str(device_serial_api)
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
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "order_id": order_id,
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "rrn": rrn_new,
                    "pmt_gateway": "MINTOAK",
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "device_serial": str(device_serial)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                logger.debug("Fetching details from bharatqr_txn table:")
                logger.debug(f"Fetching TXN ID from bharatqr_txn table: {txn_id}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching State from bharatqr_txn table: {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].values[0])
                logger.debug(f"Fetching Amount from bharatqr_txn table: {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching TXN Type from bharatqr_txn table: {bqr_txn_type_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching Terminal Info ID from bharatqr_txn table: {brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from bharatqr_txn table: {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching Merchant Config ID from bharatqr_txn table: {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching TXN Primary ID from bharatqr_txn table: {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching Org Code from bharatqr_txn table: {bqr_org_code_db}")

                actual_db_values = {
                    "pmt_status": status_db_new,
                    "pmt_state": state_db_new,
                    "pmt_mode": payment_mode_db_new,
                    "txn_amt": amount_db_new,
                    "settle_status": settlement_status_db_new,
                    "order_id": order_id_db_new,
                    "acquirer_code": acquirer_code_db_new,
                    "bank_code": bank_code_db_new,
                    "pmt_gateway": payment_gateway_db_new,
                    "mid": mid_db,
                    "tid": tid_db,
                    "rrn": rrn_new,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "device_serial": str(device_serial_db)
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
                date_and_time_portal = date_time_converter.to_portal_format(posting_date)
                date_and_time_portal_new = date_time_converter.to_portal_format(posting_date_new)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": '-' if auth_code is None else auth_code,
                    "date_time_2": date_and_time_portal_new,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount_db_new)}0",
                    "rrn_2": rrn_new,
                    "txn_id_2": txn_id_new,
                    "auth_code_2": '-' if auth_code_2 is None else auth_code_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                logger.debug("For Second TXN:")
                date_time_2 = transaction_details[0]['Date & Time']
                logger.debug(f"Date and Time: {date_time_2}")
                transaction_id_2 = transaction_details[0]['Transaction ID']
                logger.debug(f"Transaction ID: {transaction_id_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Total Amount: {total_amount_2}")
                transaction_type_2 = transaction_details[0]['Type']
                logger.debug(f"Transaction Type: {transaction_type_2}")
                status_2 = transaction_details[0]['Status']
                logger.debug(f"Status: {status_2}")
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                logger.debug(f"Auth Code Portal: {auth_code_portal_2}")
                rrn_portal_2 = transaction_details[0]['RR Number']
                logger.debug(f"RR Number: {rrn_portal_2}")

                logger.debug("Portal details for first TXN:")
                date_time = transaction_details[1]['Date & Time']
                logger.debug(f"Date and Time: {date_time}")
                transaction_id = transaction_details[1]['Transaction ID']
                logger.debug(f"Transaction ID: {transaction_id}")
                total_amount = transaction_details[1]['Total Amount'].split()
                logger.debug(f"Total Amount: {total_amount}")
                transaction_type = transaction_details[1]['Type']
                logger.debug(f"Transaction Type: {transaction_type}")
                status = transaction_details[1]['Status']
                logger.debug(f"Status: {status}")
                username = transaction_details[1]['Username']
                logger.debug(f"Username: {username}")
                auth_code_portal = transaction_details[1]['Auth Code']
                logger.debug(f"Auth Code Portal: {auth_code_portal}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal_2,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rrn_portal_2,
                    "auth_code_2": auth_code_portal_2,
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
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
def test_common_100_102_418():
    """
    Sub Feature Code: Tid_dep_UI_Common_BQRV4_UPI_Success_Two_Callback_Before_QR_Expiry_Auto_Refund_Disabled_HDFC_MINTOAK
    Sub Feature Description: Tid Dep - Performing a pure upi success two callback via tid dep HDFC_MINTOAK when auto refund is disabled
    TC naming code description:
    100: Payment Method,
    102: BQRV4,
    418: TC418
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

        query = f"select org_code from org_employee where username='{app_username}';"
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

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        logger.debug(f"Fetching MID from bharatqr_merchant_config for current merchant: {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching TID from bharatqr_merchant_config for current merchant: {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(
            f"Fetching Terminal Info ID from bharatqr_merchant_config for current merchant: {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"Fetching BQR MC ID from bharatqr_merchant_config for current merchant: {bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching BQR M PAN from bharatqr_merchant_config for current merchant: {bqr_m_pan}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where " \
                "org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select device_serial from terminal_info where tid = '{tid}';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)----------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-----------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = float(random.randint(251, 300))
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            txn_id = response["txnId"]
            order_id = response["externalRefNumber"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result, Txn_id_expired : {txn_id}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device serial from txn table:{device_serial_db}")

            logger.debug(f"preparing data to perform the encryption generation for first callback")
            mtxn_id_first = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"mtxn ID generated:{mtxn_id_first}")
            rrn = str(random.randint(10000000, 99999999))
            logger.debug(f"issuer_ref_number_first generated:{rrn}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id_first
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing first callback for mintoak")

            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id the DB after first callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_first = result['id'].values[0]
            logger.debug(f"Fetching txn_id_first from txn table:{txn_id_first}")
            created_date_first = result['created_time'].values[0]
            logger.debug(f"Fetching created_date_first from txn table:{created_date_first}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table:{auth_code}")

            logger.debug(f"preparing data to perform the encryption generation for second callback")
            mtxn_id_second = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"mtxn_id generated:{mtxn_id_second}")
            rrn_2 = str(random.randint(10000000, 99999999))
            logger.debug(f"issuer_ref_number_second generated:{rrn_2}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id_second
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn_2
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for mintoak_encryption_callback API  is : {response}")
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

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id the DB after first callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_second = result['id'].values[0]
            logger.debug(f"Fetching txn_id_second from txn table:{txn_id_second}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table:{auth_code_2}")
            created_date_second = result['created_time'].values[0]
            logger.debug(f"Fetching created_date_second from txn table:{created_date_second}")

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
        # -----------------------------------------Start of App Validation------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_date_first)
                date_and_time_2 = date_time_converter.to_app_format(created_date_second)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id_first,
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_second,
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(txn_id_first)
                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_first}, {payment_status_new}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_first}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_first}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_first}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_first}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_first}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_first}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_first}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_first}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_second)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_second}, {payment_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_second}, {app_date_and_time_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_second}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_second}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_second}, {app_amount_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_second}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_second}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_second}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_second}, {app_rrn_2}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status_new.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "settle_status_2": app_settlement_status_2,
                    "order_id_2": app_order_id_2,
                    "payment_msg_2": app_payment_msg_2,
                    "date_2": app_date_and_time_2
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
                date = date_time_converter.db_datetime(created_date_first)
                date_2 = date_time_converter.db_datetime(created_date_second)
                expected_api_values = {
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "date": date,
                    "order_id": order_id,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": "CHARGE",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_2,
                    "order_id_2": order_id,
                    "device_serial": str(device_serial)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response_list = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response_list["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                device_serial_api = response["deviceSerial"]
                logger.debug(
                    f"API Details for original txn : org code:{org_code_api}, mid:{mid_api}, tid:{tid_api},  device serial:{device_serial_api}")

                response = [x for x in response_list["txns"] if x["txnId"] == txn_id_first][0]
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
                order_id_api = response["orderNumber"]
                logger.debug(
                    f"API Details for new txn : status:{status_api}, amount:{amount_api}, payment mode:{payment_mode_api}, state:{state_api}, settlement status:{settlement_status_api}, issuer code:{issuer_code_api}, acquirer code:{acquirer_code_api}, org code:{org_code_api}, mid:{mid_api}, tid:{tid_api}, txn type:{txn_type_api}, date:{date_api}")

                response = [x for x in response_list["txns"] if x["txnId"] == txn_id_second][0]
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
                date_api_2 = response["createdTime"]
                order_id_api_2 = response["orderNumber"]
                logger.debug(
                    f"API Details for new txn : status:{status_api_2}, amount:{amount_api_2}, payment mode:{payment_mode_api_2}, state:{state_api_2}, settlement status:{settlement_status_api_2}, issuer code:{issuer_code_api_2}, acquirer code:{acquirer_code_api_2}, org code:{org_code_api_2}, mid:{mid_api_2}, tid:{tid_api_2}, txn type:{txn_type_api_2}, date:{date_api_2}")

                actual_api_values = {
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "order_id_2": order_id_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "device_serial": str(device_serial_api)
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
                    "mid": mid,
                    "tid": tid,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "MINTOAK",
                    "upi_txn_type": "PAY_BQR",
                    "upi_bank_code": "HDFC_MINTOAK",
                    "bqr_status_db": "INITIATED BY UPI",
                    "upi_mc_id": upi_mc_id,
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "bank_code_2": "HDFC",
                    "payment_gateway_2": "MINTOAK",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "HDFC_MINTOAK",
                    "upi_mc_id_2": upi_mc_id,
                    "rrn_2": str(rrn_2),
                    "mid_2": mid,
                    "tid_2": tid,
                    "order_id_2": order_id,
                    "device_serial": str(device_serial)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                mid_db = result["mid"].values[0]
                tid_db = result["tid"].values[0]
                logger.debug(f"MID from txn table:{mid_db}, TID from txn table:{tid_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                logger.debug(f"Fetching details from bharatqr_txn table for txn ID: {txn_id}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching txn primary ID from bharatqr_txn table: {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching org code from bharatqr_txn table: {bqr_org_code_db}")
                bqr_status_db = result['status_desc'].values[0]
                logger.debug(f"Fetching bqr_status_db from bharatqr_txn table: {bqr_status_db}")

                query = f"select * from txn where id='{txn_id_first}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                logger.debug(f"Fetching status from txn table for first callback: {status_db}")
                payment_mode_db = result["payment_mode"].values[0]
                logger.debug(f"Fetching payment mode from txn table for first callback: {payment_mode_db}")
                amount_db = float(result["amount"].values[0])
                logger.debug(f"Fetching amount from txn table for first callback: {amount_db}")
                state_db = result["state"].values[0]
                logger.debug(f"Fetching state from txn table for first callback: {state_db}")
                payment_gateway_db = result["payment_gateway"].values[0]
                logger.debug(f"Fetching payment gateway from txn table for first callback: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].values[0]
                logger.debug(f"Fetching acquirer code from txn table for first callback: {acquirer_code_db}")
                bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bank code from txn table for first callback: {bank_code_db}")
                settlement_status_db = result["settlement_status"].values[0]
                logger.debug(f"Fetching settlement status from txn table for first callback: {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching TID from txn table for first callback: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching MID from txn table for first callback: {mid_db}")
                order_id_db = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from txn table for first callback: {order_id_db}")
                rrn_db = result['rr_number'].values[0]
                logger.debug(f"Fetching rrn from txn table for first callback: {rrn_db}")

                query = f"select * from upi_txn where txn_id='{txn_id_first}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"Fetching status from upi_txn table for first callback: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching transaction type from upi_txn table for first callback: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bank code from upi_txn table for first callback: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching MC ID from upi_txn table for first callback: {upi_mc_id_db}")

                query = f"select * from txn where id='{txn_id_second}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result["status"].values[0]
                logger.debug(f"Fetching status from txn table for second callback: {status_db_2}")
                payment_mode_db_2 = result["payment_mode"].values[0]
                logger.debug(f"Fetching payment mode from txn table for second callback: {payment_mode_db_2}")
                amount_db_2 = float(result["amount"].values[0])
                logger.debug(f"Fetching amount from txn table for second callback: {amount_db_2}")
                state_db_2 = result["state"].values[0]
                logger.debug(f"Fetching state from txn table for second callback: {state_db_2}")
                payment_gateway_db_2 = result["payment_gateway"].values[0]
                logger.debug(f"Fetching payment gateway from txn table for second callback: {payment_gateway_db_2}")
                acquirer_code_db_2 = result["acquirer_code"].values[0]
                logger.debug(f"Fetching acquirer code from txn table for second callback: {acquirer_code_db_2}")
                bank_code_db_2 = result["bank_code"].values[0]
                logger.debug(f"Fetching bank code from txn table for second callback: {bank_code_db_2}")
                settlement_status_db_2 = result["settlement_status"].values[0]
                logger.debug(f"Fetching settlement status from txn table for second callback: {settlement_status_db_2}")
                tid_db_2 = result['tid'].values[0]
                logger.debug(f"Fetching TID from txn table for second callback: {tid_db_2}")
                mid_db_2 = result['mid'].values[0]
                logger.debug(f"Fetching MID from txn table for second callback: {mid_db_2}")
                order_id_db_2 = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from txn table for second callback: {order_id_db_2}")
                rrn_db_2 = result['rr_number'].values[0]
                logger.debug(f"Fetching rrn from txn table for second callback: {rrn_db_2}")

                query = f"select * from upi_txn where txn_id='{txn_id_second}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].values[0]
                logger.debug(f"Fetching status from TXN table for second callback: {upi_status_db_2}")
                upi_txn_type_db_2 = result["txn_type"].values[0]
                logger.debug(f"Fetching transaction type from TXN table for second callback: {upi_txn_type_db_2}")
                upi_bank_code_db_2 = result["bank_code"].values[0]
                logger.debug(f"Fetching bank code from TXN table for second callback: {upi_bank_code_db_2}")
                upi_mc_id_db_2 = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching MC ID from TXN table for second callback: {upi_mc_id_db_2}")

                actual_db_values = {
                    "mid": mid_db,
                    "tid": tid_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "bqr_status_db": bqr_status_db,
                    "rrn": rrn_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "order_id": order_id_db,
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt_2": amount_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "rrn_2": rrn_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "payment_gateway_2": payment_gateway_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "order_id_2": order_id_db_2,
                    "device_serial": str(device_serial_db)
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_first)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_second)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id_first,
                    "rrn": str(rrn),
                    "auth_code": '-' if auth_code is None else auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_second,
                    "rrn_2": str(rrn_2),
                    "auth_code_2": '-' if auth_code_2 is None else auth_code_2,
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                auth_code_portal = transaction_details[1]['Auth Code']

                logger.debug(f"Fetching Portal details for second TXN:")
                logger.debug(f"Date and time: {date_time}")
                logger.debug(f"Auth code portal: {auth_code_portal}")
                logger.debug(f"Transaction ID: {transaction_id}")
                logger.debug(f"Total amount: {total_amount}")
                logger.debug(f"RR number: {rr_number}")
                logger.debug(f"Transaction type: {transaction_type}")
                logger.debug(f"Status: {status}")
                logger.debug(f"Username: {username}")

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                auth_code_portal_2 = transaction_details[0]['Auth Code']

                logger.debug(f"Auth code portal: {auth_code_portal_2}")
                logger.debug(f"Fetching Portal details for third TXN:")
                logger.debug(f"Date and time: {date_time_2}")
                logger.debug(f"Transaction ID: {transaction_id_2}")
                logger.debug(f"Total amount: {total_amount_2}")
                logger.debug(f"RR number: {rr_number_2}")
                logger.debug(f"Transaction type: {transaction_type_2}")
                logger.debug(f"Status: {status_2}")
                logger.debug(f"Username: {username_2}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": str(rr_number),
                    "auth_code": auth_code_portal,

                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": str(rr_number_2),
                    "auth_code_2": auth_code_portal_2
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_date_first)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }
                receipt_validator.perform_charge_slip_validations(txn_id_first,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
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
def test_common_100_102_419():
    """
    Sub Feature Code: Tid_Dep_UI_Common_BQRV4_UPI_Two_Callback_After_QR_Expiry_Auto_Refund_Disabled_HDFC_MINTOAK
    Sub Feature Description: Tid Dep - Performing a pure upi two callback via HDFC_MINTOAK after expiry the qr when auto refund is disabled
    TC naming code description:
    100: Payment Method,
    102: BQRV4,
    419: TC419
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

        query = f"select org_code from org_employee where username='{app_username}';"
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

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where " \
                f"org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        logger.debug(f"Fetching mid from database for current merchant: {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching tid from database for current merchant: {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"Fetching terminal_info_id from database for current merchant: {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"Fetching bqr_mc_id from database for current merchant: {bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching bqr_m_pan from database for current merchant: {bqr_m_pan}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")
        mid = result['mid'].values[0]
        logger.debug(f"mid from upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"tid from upi_merchant_config table : {tid}")

        query = f"select device_serial from terminal_info where tid = '{tid}';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

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

            amount = float(random.randint(251, 300))
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            txn_id = response["txnId"]
            order_id = response["externalRefNumber"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result, Txn_id : {txn_id}")
            created_date = result['created_time'].values[0]
            logger.debug(f"created_date:{created_date}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"device_serial:{device_serial_db}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"auth_code:{auth_code}")

            time.sleep(75)

            logger.debug(f"preparing data to perform the encryption generation for first callback")
            mtxn_id_first = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating mtxnID : {mtxn_id_first}")
            issuer_ref_number_first = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating issuer_ref_number_first : {issuer_ref_number_first}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id_first
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number_first
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing first callback for mintoak")

            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id the DB after first callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_first = result['id'].values[0]
            logger.debug(f"Txn ID after First callback : {txn_id_first}")
            created_date_first = result['created_time'].values[0]
            logger.debug(f"created_date:{created_date_first}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"auth_code:{auth_code_2}")

            logger.debug(f"preparing data to perform the encryption generation for second callback")
            mtxn_id_second = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating mtxnID : {mtxn_id_second}")
            issuer_ref_number_second = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating issuer_ref_number_second : {issuer_ref_number_second}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id_second
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number_second
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for mintoak_encryption_callback API  is : {response}")
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

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id the DB after first callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_second = result['id'].values[0]
            logger.debug(f"Txn ID after Second callback : {txn_id_second}")
            created_date_second = result['created_time'].values[0]
            logger.debug(f"created_date_second:{created_date_second}")
            auth_code_3 = result['auth_code'].values[0]
            logger.debug(f"auth_code:{auth_code_3}")

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
                date_and_time = date_time_converter.to_app_format(created_date)
                date_and_time_new_2 = date_time_converter.to_app_format(created_date_first)
                date_and_time_new_3 = date_time_converter.to_app_format(created_date_second)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_first,
                    "rrn_2": str(issuer_ref_number_first),
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_new_2,
                    "pmt_mode_3": "UPI",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": "{:.2f}".format(amount),
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_second,
                    "rrn_3": str(issuer_ref_number_second),
                    "order_id_3": order_id,
                    "payment_msg_3": "PAYMENT SUCCESSFUL",
                    "date_3": date_and_time_new_3
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
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

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_first)
                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_first}, {payment_status_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_first}, {app_date_and_time_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_first}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_first}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_first}, {app_amount_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_first}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_first}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_first}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching app_rrn_new from txn history for the txn : {txn_id_first}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_second)
                payment_status_new_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_second}, {payment_status_new_3}")
                app_date_and_time_new_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_second}, {app_date_and_time_new_3}")
                payment_mode_new_3 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id_second}, {payment_mode_new_3}")
                app_txn_id_new_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_second}, {app_txn_id_new_3}")
                app_amount_new_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_second}, {app_amount_new_3}")
                app_settlement_status_new_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_second}, {app_settlement_status_new_3}")
                app_payment_msg_new_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_second}, {app_payment_msg_new_3}")
                app_order_id_new_3 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {txn_id_second}, {app_order_id_new_3}")
                app_rrn_new_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching app_rrn_new from txn history for the txn : {txn_id_second}, {app_rrn_new_3}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "msg": app_payment_msg, "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new,
                    "pmt_status_2": payment_status_new.split(':')[1],
                    "txn_amt_2": app_amount_new.split(' ')[1],
                    "txn_id_2": app_txn_id_new,
                    "rrn_2": str(app_rrn_new),
                    "settle_status_2": app_settlement_status_new,
                    "order_id_2": app_order_id_new,
                    "payment_msg_2": app_payment_msg_new,
                    "date_2": app_date_and_time_new,
                    "pmt_mode_3": payment_mode_new_3,
                    "pmt_status_3": payment_status_new_3.split(':')[1],
                    "txn_amt_3": app_amount_new_3.split(' ')[1],
                    "txn_id_3": app_txn_id_new_3,
                    "rrn_3": str(app_rrn_new_3),
                    "settle_status_3": app_settlement_status_new_3,
                    "order_id_3": app_order_id_new_3,
                    "payment_msg_3": app_payment_msg_new_3,
                    "date_3": app_date_and_time_new_3
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
                date = date_time_converter.db_datetime(created_date)
                date_new = date_time_converter.db_datetime(created_date_first)
                date_new_3 = date_time_converter.db_datetime(created_date_second)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(issuer_ref_number_first),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": "CHARGE",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_new,
                    "order_id_2": order_id,
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "UPI",
                    "pmt_state_3": "SETTLED",
                    "rrn_3": str(issuer_ref_number_second),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "issuer_code_3": "HDFC",
                    "txn_type_3": "CHARGE",
                    "mid_3": mid,
                    "tid_3": tid,
                    "org_code_3": org_code,
                    "date_3": date_new_3,
                    "order_id_3": order_id,
                    "device_serial": str(device_serial)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response_list = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response_list["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]
                device_serial_api = response["deviceSerial"]
                logger.debug(
                    f"API Details for original txn : status:{status_api}, amount:{amount_api}, payment mode:{payment_mode_api}, state:{state_api}, settlement status:{settlement_status_api}, issuer code:{issuer_code_api}, acquirer code:{acquirer_code_api}, org code:{org_code_api}, mid:{mid_api}, tid:{tid_api}, txn type:{txn_type_api}, date:{date_api}, device serial:{device_serial_api}")

                response = [x for x in response_list["txns"] if x["txnId"] == txn_id_first][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new = response["status"]
                amount_api_new = float(response["amount"])
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                org_code_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                date_api_new = response["createdTime"]
                order_id_api_new = response["orderNumber"]
                logger.debug(
                    f"API Details for new txn : status:{status_api_new}, amount:{amount_api_new}, payment mode:{payment_mode_api_new}, state:{state_api_new}, settlement status:{settlement_status_api_new}, issuer code:{issuer_code_api_new}, acquirer code:{acquirer_code_api_new}, org code:{org_code_api_new}, mid:{mid_api_new}, tid:{tid_api_new}, txn type:{txn_type_api_new}, date:{date_api_new}")

                response = [x for x in response_list["txns"] if x["txnId"] == txn_id_second][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_3 = response["status"]
                amount_api_new_3 = float(response["amount"])
                payment_mode_api_new_3 = response["paymentMode"]
                state_api_new_3 = response["states"][0]
                rrn_api_new_3 = response["rrNumber"]
                settlement_status_api_new_3 = response["settlementStatus"]
                issuer_code_api_new_3 = response["issuerCode"]
                acquirer_code_api_new_3 = response["acquirerCode"]
                org_code_api_new_3 = response["orgCode"]
                mid_api_new_3 = response["mid"]
                tid_api_new_3 = response["tid"]
                txn_type_api_new_3 = response["txnType"]
                date_api_new_3 = response["createdTime"]
                order_id_api_new_3 = response["orderNumber"]
                logger.debug(
                    f"API Details for new txn : status:{status_api_new_3}, amount:{amount_api_new_3}, payment mode:{payment_mode_api_new_3}, state:{state_api_new_3}, settlement status:{settlement_status_api_new_3}, issuer code:{issuer_code_api_new_3}, acquirer code:{acquirer_code_api_new_3}, org code:{org_code_api_new_3}, mid:{mid_api_new_3}, tid:{tid_api_new_3}, txn type:{txn_type_api_new_3}, date:{date_api_new_3}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new,
                    "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "rrn_2": str(rrn_api_new),
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "issuer_code_2": issuer_code_api_new,
                    "txn_type_2": txn_type_api_new,
                    "mid_2": mid_api_new,
                    "tid_2": tid_api_new,
                    "org_code_2": org_code_api_new,
                    "order_id_2": order_id_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new),
                    "pmt_status_3": status_api_new_3,
                    "txn_amt_3": amount_api_new_3,
                    "pmt_mode_3": payment_mode_api_new_3,
                    "pmt_state_3": state_api_new_3,
                    "rrn_3": str(rrn_api_new_3),
                    "settle_status_3": settlement_status_api_new_3,
                    "acquirer_code_3": acquirer_code_api_new_3,
                    "issuer_code_3": issuer_code_api_new_3,
                    "txn_type_3": txn_type_api_new_3,
                    "mid_3": mid_api_new_3,
                    "tid_3": tid_api_new_3,
                    "org_code_3": org_code_api_new_3,
                    "order_id_3": order_id_api_new_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_new_3),
                    "device_serial": str(device_serial_api)
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
                    "pmt_mode": "BHARATQR",
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "acquirer_code": "HDFC",
                    "bank_name": "HDFC Bank",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "MINTOAK",
                    "settle_status": "FAILED",
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "rrn_2": str(issuer_ref_number_first),
                    "bank_code_2": "HDFC",
                    "payment_gateway_2": "MINTOAK",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "HDFC_MINTOAK",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "order_id_2": order_id,
                    "pmt_status_3": "AUTHORIZED",
                    "pmt_state_3": "SETTLED",
                    "pmt_mode_3": "UPI",
                    "txn_amt_3": float(amount),
                    "upi_txn_status_3": "AUTHORIZED",
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "bank_code_3": "HDFC",
                    "rrn_3": str(issuer_ref_number_second),
                    "payment_gateway_3": "MINTOAK",
                    "upi_txn_type_3": "PAY_BQR",
                    "upi_bank_code_3": "HDFC_MINTOAK",
                    "upi_mc_id_3": upi_mc_id,
                    "mid_3": mid,
                    "tid_3": tid,
                    "order_id_3": order_id,
                    "device_serial": str(device_serial)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].values[0])
                logger.debug("Fetching Amount from txn table: {amount_db}")
                payment_mode_db = result["payment_mode"].values[0]
                logger.debug("Fetching Payment Mode from txn table: {payment_mode_db}")
                payment_status_db = result["status"].values[0]
                logger.debug("Fetching Status from txn table: {payment_status_db}")
                payment_state_db = result["state"].values[0]
                logger.debug("Fetching State from txn table: {payment_state_db}")
                acquirer_code_db = result["acquirer_code"].values[0]
                logger.debug("Fetching Acquirer Code from txn table: {acquirer_code_db}")
                bank_name_db = result["bank_name"].values[0]
                logger.debug("Fetching Bank Name from txn table: {bank_name_db}")
                mid_db = result["mid"].values[0]
                logger.debug("Fetching MID from txn table: {mid_db}")
                tid_db = result["tid"].values[0]
                logger.debug("Fetching TID from txn table: {tid_db}")
                payment_gateway_db = result["payment_gateway"].values[0]
                logger.debug("Fetching Payment Gateway from txn table: {payment_gateway_db}")
                settlement_status_db = result["settlement_status"].values[0]
                logger.debug("Fetching Settlement Status from txn table: {settlement_status_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                logger.debug(f"Fetching details from bharatqr_txn table for txn ID: {txn_id}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching state from bharatqr_txn table: {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].values[0])
                logger.debug(f"Fetching amount from bharatqr_txn table: {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching txn type from bharatqr_txn table: {bqr_txn_type_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching terminal info ID from bharatqr_txn table: {brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bank code from bharatqr_txn table: {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching merchant config from bharatqr_txn table: {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching txn primary ID from bharatqr_txn table: {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching org code from bharatqr_txn table: {bqr_org_code_db}")

                query = f"select * from txn where id='{txn_id_first}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new_2 = result["status"].values[0]
                logger.debug(f"Fetching Status from txn table: {status_db_new_2}")
                payment_mode_db_new_2 = result["payment_mode"].values[0]
                logger.debug(f"Fetching payment mode from txn table: {payment_mode_db_new_2}")
                amount_db_new_2 = float(result["amount"].values[0])
                logger.debug(f"Fetching Amount from txn table: {amount_db_new_2}")
                state_db_new_2 = result["state"].values[0]
                logger.debug(f"Fetching State from txn table: {state_db_new_2}")
                payment_gateway_db_new_2 = result["payment_gateway"].values[0]
                logger.debug(f"Fetching Payment Gateway from txn table: {payment_gateway_db_new_2}")
                acquirer_code_db_new_2 = result["acquirer_code"].values[0]
                logger.debug(f"Fetching Acquirer Code from txn table: {acquirer_code_db_new_2}")
                bank_code_db_new_2 = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from txn table: {bank_code_db_new_2}")
                settlement_status_db_new_2 = result["settlement_status"].values[0]
                logger.debug(f"Fetching Settlement Status from txn table: {settlement_status_db_new_2}")
                tid_db_new_2 = result['tid'].values[0]
                logger.debug(f"Fetching TID from txn table: {tid_db_new_2}")
                mid_db_new_2 = result['mid'].values[0]
                logger.debug(f"Fetching MID from txn table: {mid_db_new_2}")
                order_id_db_new_2 = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from txn table: {order_id_db_new_2}")
                rrn_db_2 = result['rr_number'].values[0]
                logger.debug(f"Fetching rrn from txn table: {rrn_db_2}")

                query = f"select * from upi_txn where txn_id='{txn_id_first}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_2 = result["status"].values[0]
                logger.debug(f"Fetching Status from upi_txn table: {upi_status_db_new_2}")
                upi_txn_type_db_new_2 = result["txn_type"].values[0]
                logger.debug(f"Fetching txn type from upi_txn table: {upi_txn_type_db_new_2}")
                upi_bank_code_db_new_2 = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank code from upi_txn table: {upi_bank_code_db_new_2}")
                upi_mc_id_db_new_2 = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching MC ID from upi_txn table: {upi_mc_id_db_new_2}")

                query = f"select * from txn where id='{txn_id_second}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new_3 = result["status"].values[0]
                logger.debug(f"Fetching Status from txn table: {status_db_new_3}")
                payment_mode_db_new_3 = result["payment_mode"].values[0]
                logger.debug(f"Fetching payment mode from txn table: {payment_mode_db_new_3}")
                amount_db_new_3 = float(result["amount"].values[0])
                logger.debug(f"Fetching Amount from txn table: {amount_db_new_3}")
                state_db_new_3 = result["state"].values[0]
                logger.debug(f"Fetching State from txn table: {state_db_new_3}")
                payment_gateway_db_new_3 = result["payment_gateway"].values[0]
                logger.debug(f"Fetching Payment Gateway from txn table: {payment_gateway_db_new_3}")
                acquirer_code_db_new_3 = result["acquirer_code"].values[0]
                logger.debug(f"Fetching Acquirer Code from txn table: {acquirer_code_db_new_3}")
                bank_code_db_new_3 = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from txn table: {bank_code_db_new_3}")
                settlement_status_db_new_3 = result["settlement_status"].values[0]
                logger.debug(f"Fetching Settlement Status from txn table: {settlement_status_db_new_3}")
                tid_db_new_3 = result['tid'].values[0]
                logger.debug(f"Fetching TID from txn table: {tid_db_new_3}")
                mid_db_new_3 = result['mid'].values[0]
                logger.debug(f"Fetching MID from txn table: {mid_db_new_3}")
                order_id_db_new_3 = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from txn table: {order_id_db_new_3}")
                rrn_db_3 = result['rr_number'].values[0]
                logger.debug(f"Fetching rrn from txn table: {rrn_db_3}")

                query = f"select * from upi_txn where txn_id='{txn_id_second}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_3 = result["status"].values[0]
                logger.debug(f"Fetching Status from upi_txn table: {upi_status_db_new_3}")
                upi_txn_type_db_new_3 = result["txn_type"].values[0]
                logger.debug(f"Fetching Txn Type from upi_txn table: {upi_txn_type_db_new_3}")
                upi_bank_code_db_new_3 = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from upi_txn table: {upi_bank_code_db_new_3}")
                upi_mc_id_db_new_3 = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching MC ID from upi_txn table: {upi_mc_id_db_new_3}")

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
                    "settle_status": settlement_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "upi_txn_status_2": upi_status_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "bank_code_2": bank_code_db_new_2,
                    "rrn_2": rrn_db_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "mid_2": mid_db_new_2,
                    "tid_2": tid_db_new_2,
                    "order_id_2": order_id_db_new_2,
                    "pmt_status_3": status_db_new_3,
                    "pmt_state_3": state_db_new_3,
                    "pmt_mode_3": payment_mode_db_new_3,
                    "txn_amt_3": amount_db_new_3,
                    "upi_txn_status_3": upi_status_db_new_3,
                    "settle_status_3": settlement_status_db_new_3,
                    "acquirer_code_3": acquirer_code_db_new_3,
                    "bank_code_3": bank_code_db_new_3,
                    "payment_gateway_3": payment_gateway_db_new_3,
                    "rrn_3": rrn_db_3,
                    "upi_txn_type_3": upi_txn_type_db_new_3,
                    "upi_bank_code_3": upi_bank_code_db_new_3,
                    "upi_mc_id_3": upi_mc_id_db_new_3,
                    "mid_3": mid_db_new_3,
                    "tid_3": tid_db_new_3,
                    "order_id_3": order_id_db_new_3,
                    "device_serial": str(device_serial_db)
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_first)
                date_and_time_portal_3 = date_time_converter.to_portal_format(created_date_second)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": '-' if auth_code is None else auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_first,
                    "rrn_2": str(issuer_ref_number_first),
                    "auth_code_2": '-' if auth_code_2 is None else auth_code_2,

                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "AUTHORIZED",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": "{:.2f}".format(amount),
                    "username_3": app_username,
                    "txn_id_3": txn_id_second,
                    "rrn_3": str(issuer_ref_number_second),
                    "auth_code_3": '-' if auth_code_3 is None else auth_code_3,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[2]['Date & Time']
                logger.debug(f"Fetching from portal - Date Time: {date_time}")
                transaction_id = transaction_details[2]['Transaction ID']
                logger.debug(f"Fetching from portal - Transaction ID: {transaction_id}")
                total_amount = transaction_details[2]['Total Amount'].split()
                logger.debug(f"Fetching from portal - Total Amount: {total_amount}")
                transaction_type = transaction_details[2]['Type']
                logger.debug(f"Fetching from portal - Transaction Type: {transaction_type}")
                status = transaction_details[2]['Status']
                logger.debug(f"Fetching from portal - Status: {status}")
                username = transaction_details[2]['Username']
                logger.debug(f"Fetching from portal - Username: {username}")
                auth_code_portal = transaction_details[1]['Auth Code']
                logger.debug(f"For Second TXN - Fetching from portal - Auth Code: {auth_code_portal}")

                date_time_2 = transaction_details[1]['Date & Time']
                logger.debug(f"For Second TXN - Fetching from portal - Date Time: {date_time_2}")
                transaction_id_2 = transaction_details[1]['Transaction ID']
                logger.debug(f"For Second TXN - Fetching from portal - Transaction ID: {transaction_id_2}")
                total_amount_2 = transaction_details[1]['Total Amount'].split()
                logger.debug(f"For Second TXN - Fetching from portal - Total Amount: {total_amount_2}")
                rr_number_2 = transaction_details[1]['RR Number']
                logger.debug(f"For Second TXN - Fetching from portal - RR Number: {rr_number_2}")
                transaction_type_2 = transaction_details[1]['Type']
                logger.debug(f"For Second TXN - Fetching from portal - Transaction Type: {transaction_type_2}")
                status_2 = transaction_details[1]['Status']
                logger.debug(f"For Second TXN - Fetching from portal - Status: {status_2}")
                username_2 = transaction_details[1]['Username']
                logger.debug(f"For Second TXN - Fetching from portal - Username: {username_2}")
                auth_code_portal_2 = transaction_details[1]['Auth Code']
                logger.debug(f"For Second TXN - Fetching from portal - Auth Code: {auth_code_portal_2}")

                date_time_3 = transaction_details[0]['Date & Time']
                logger.debug(f"For third TXN - Fetching from portal - Date Time: {date_time_3}")
                transaction_id_3 = transaction_details[0]['Transaction ID']
                logger.debug(f"For third TXN - Fetching from portal - Transaction ID: {transaction_id_3}")
                total_amount_3 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"For third TXN - Fetching from portal - Total Amount: {total_amount_3}")
                rr_number_3 = transaction_details[0]['RR Number']
                logger.debug(f"For third TXN - Fetching from portal - RR Number: {rr_number_3}")
                transaction_type_3 = transaction_details[0]['Type']
                logger.debug(f"For third TXN - Fetching from portal - Transaction Type: {transaction_type_3}")
                status_3 = transaction_details[0]['Status']
                logger.debug(f"For third TXN - Fetching from portal - Status: {status_3}")
                username_3 = transaction_details[0]['Username']
                logger.debug(f"For third TXN - Fetching from portal - Username: {username_3}")
                auth_code_portal_3 = transaction_details[1]['Auth Code']
                logger.debug(f"For Second TXN - Fetching from portal - Auth Code: {auth_code_portal_3}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,

                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": str(rr_number_2),
                    "auth_code_2": auth_code_portal_2,

                    "date_time_3": date_time_3,
                    "pmt_state_3": str(status_3),
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "rrn_3": str(rr_number_3),
                    "auth_code_3": auth_code_portal_3,

                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_date_first)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(issuer_ref_number_first),
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code_2 is None else auth_code_2
                }
                receipt_validator.perform_charge_slip_validations(txn_id_first,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
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
