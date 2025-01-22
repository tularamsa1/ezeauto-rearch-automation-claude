import random
import sys
from datetime import datetime
from time import sleep
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_405():
    """
    Sub Feature Code: Tid_Dep_UI_Common_PM_BQRV4_BQR_Amount_Mismatch_Callback_HDFC_MINTOAK
    Sub Feature Description: Tid Dep - Verification of  a  BQR amount missmatch upon callback via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 405: TC405
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username, portal_pw=portal_password,
                                                           payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -------------------------------------PreConditions(Setup to be done for the test case)------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where " \
                f"org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        terminal_info_id = result["terminal_info_id"].values[0]
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        logger.debug(f"Fetching mid, tid from database for current merchant:{mid}, {tid}")
        bqr_mc_id = result["id"].values[0]
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select device_serial from terminal_info where tid = '{tid}';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -------------------------------------------PreConditions(Completed)-------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(251, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug("Generating QR using BQR QR generate APi")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for QR generation api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            issuer_ref_number = str(random.randint(10000000, 99999999))
            amount_2 = amount + 1

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount_2
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"

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
            logger.debug(f"Query to fetch txn details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table: {created_time}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table: {external_ref}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"fetched amount_db from txn table: {amount_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"fetched payment_mode_db from txn table: {payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"fetched payment_status_db from txn table: {payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"fetched payment_state_db from txn table: {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"fetched acquirer_code_db from txn table: {acquirer_code_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"fetched mid_db from txn table: {mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"fetched tid_db from txn table: {tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"fetched payment_gateway_db from txn table: {payment_gateway_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"fetched settlement_status_db from txn table: {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"fetched device_serial_db from txn table: {device_serial_db}")

            query = f"select * from invalid_pg_request where request_id ='{txn_id}';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_upg = result['txn_id'].values[0]
            logger.debug(f"fetched txn_id_upg from invalid_pg_request table: {txn_id_upg}")

            query = f"select * from txn where id = '{txn_id_upg}';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time_upg = result['created_time'].values[0]
            logger.debug(f"fetched created_time_upg from txn table: {created_time_upg}")
            rrn_upg = result['rr_number'].values[0]
            logger.debug(f"fetched rrn_upg from txn table: {rrn_upg}")
            auth_code_upg = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code_upg from txn table: {auth_code_upg}")
            external_ref_upg = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref_upg from txn table: {external_ref_upg}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_2 = date_time_converter.to_app_format(created_time_upg)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "STATUS:PENDING",
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "txn_amt": "{:.2f}".format(amount),
                    "pmt_msg": "PAYMENT PENDING",
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "STATUS:UPG_AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_upg,
                    "txn_amt_2": "{:.2f}".format(amount_2),
                    "rrn_2": str(rrn_upg),
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2
                }
                logger.debug(f"actualAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.wait_for_home_page_load()
                # homePage.check_home_page_logo()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
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
                txn_history_page.click_on_transaction_by_txn_id(txn_id_upg)
                app_payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_upg}, {app_payment_status_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_upg}, {app_date_and_time_new}")
                app_payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id_upg}, {app_payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_upg}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_upg}, {app_amount_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_upg}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_upg}, {app_payment_msg_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_upg}, {app_rrn_new}")

                actual_app_values = {
                    "pmt_status": app_payment_status,
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_status_2": app_payment_status_new,
                    "pmt_mode_2": app_payment_mode_new,
                    "txn_id_2": app_txn_id_new,
                    "txn_amt_2": str(app_amount_new).split(' ')[1],
                    "settle_status_2": app_settlement_status_new,
                    "pmt_msg_2": app_payment_msg_new,
                    "rrn_2": app_rrn_new,
                    "date_2": app_date_and_time_new
                }
                logger.debug(f"actualAppValues: {actual_app_values}")

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
                date = date_time_converter.db_datetime(created_time)
                date_2 = date_time_converter.db_datetime(created_time_upg)
                expected_api_values = {
                    "pmt_status": "PENDING",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "PENDING",
                    "settle_status": "PENDING",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "UPG_AUTHORIZED",
                    "txn_amt_2": float(amount_2),
                    "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "UPG_AUTHORIZED",
                    "rrn_2": str(rrn_upg),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": 'CHARGE',
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"Value of responseInList is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = float(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        org_code_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        date_api = elements["createdTime"]
                        device_serial_api = elements["deviceSerial"]

                for elements in responseInList:
                    if elements["txnId"] == txn_id_upg:
                        status_api_new = elements["status"]
                        amount_api_new = float(elements["amount"])
                        payment_mode_api_new = elements["paymentMode"]
                        state_api_new = elements["states"][0]
                        rrn_api_new = elements["rrNumber"]
                        settlement_status_api_new = elements["settlementStatus"]
                        issuer_code_api_new = elements["issuerCode"]
                        acquirer_code_api_new = elements["acquirerCode"]
                        org_code_api_new = elements["orgCode"]
                        mid_api_new = elements["mid"]
                        tid_api_new = elements["tid"]
                        txn_type_api_new = elements["txnType"]
                        date_api_new = elements["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "device_serial": str(device_serial_api),
                    "pmt_status_2": status_api_new, "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "issuer_code_2": issuer_code_api_new,
                    "txn_type_2": txn_type_api_new, "mid_2": mid_api_new, "tid_2": tid_api_new,
                    "org_code_2": org_code_api_new,
                    "rrn_2": rrn_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new)
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
                    "txn_amt": amount, "pmt_mode": "BHARATQR", "pmt_status": "PENDING",
                    "pmt_state": "PENDING", "acquirer_code": "HDFC",
                    "mid": mid, "tid": tid, "pmt_gateway": "MINTOAK",
                    "settle_status": "PENDING",
                    "bqr_pmt_state": "PENDING",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "UPG_AUTHORIZED",
                    "pmt_state_2": "UPG_AUTHORIZED",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": amount_2,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "bank_code_2": "HDFC",
                    "pmt_gateway_2": "MINTOAK",
                    "mid_2": mid,
                    "tid_2": tid,
                    "ipr_pmt_mode": "BHARATQR",
                    "ipr_bank_code": "HDFC",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn_upg),
                    "ipr_txn_amt": amount_2,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_config_id": bqr_mc_id,
                    "ipr_pg_merchant_id": bqr_m_pan,
                    "bqr_pmt_status_2": "Success", "bqr_pmt_state_2": "UPG_AUTHORIZED",
                    "bqr_txn_amt_2": amount_2,
                    "brq_terminal_info_id_2": terminal_info_id,
                    "bqr_bank_code_2": "HDFC",
                    "bqr_merchant_config_id_2": bqr_mc_id, "bqr_txn_primary_id_2": txn_id_upg,
                    "bqr_rrn_2": str(rrn_upg), "bqr_org_code_2": org_code
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db = result["state"].values[0]
                bqr_amount_db = result["txn_amount"].values[0]
                bqr_txn_type_db = result["txn_type"].values[0]
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                bqr_bank_code_db = result["bank_code"].values[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = f"select * from txn where id='{txn_id_upg}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].values[0]
                payment_mode_db_new = result["payment_mode"].values[0]
                amount_db_new = result["amount"].values[0]
                state_db_new = result["state"].values[0]
                payment_gateway_db_new = result["payment_gateway"].values[0]
                acquirer_code_db_new = result["acquirer_code"].values[0]
                bank_code_db_new = result["bank_code"].values[0]
                settlement_status_db_new = result["settlement_status"].values[0]
                tid_db_new = result['tid'].values[0]
                mid_db_new = result['mid'].values[0]

                query = f"select * from bharatqr_txn where id='{txn_id_upg}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_new = result["status_desc"].values[0]
                bqr_state_db_new = result["state"].values[0]
                bqr_amount_db_new = float(result["txn_amount"].values[0])
                brq_terminal_info_id_db_new = result["terminal_info_id"].values[0]
                bqr_bank_code_db_new = result["bank_code"].values[0]
                bqr_merchant_config_id_db_new = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].values[0]
                bqr_rrn_db_new = result['rrn'].values[0]
                bqr_org_code_db_new = result['org_code'].values[0]

                query = f"select * from invalid_pg_request where txn_id ='{txn_id_upg}';"
                logger.debug(f"query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                ipr_payment_mode = result["payment_mode"].values[0]
                ipr_bank_code = result["bank_code"].values[0]
                ipr_org_code = result["org_code"].values[0]
                ipr_amount = result["amount"].values[0]
                ipr_rrn = result["rrn"].values[0]
                ipr_mid = result["mid"].values[0]
                ipr_tid = result["tid"].values[0]
                ipr_config_id = result["config_id"].values[0]
                ipr_pg_merchant_id = result["pg_merchant_id"].values[0]

                actual_db_values = {
                    "txn_amt": amount_db, "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db, "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "device_serial": str(device_serial_db),
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_new,
                    "pmt_state_2": state_db_new,
                    "pmt_mode_2": payment_mode_db_new,
                    "txn_amt_2": amount_db_new,
                    "settle_status_2": settlement_status_db_new,
                    "acquirer_code_2": acquirer_code_db_new,
                    "bank_code_2": bank_code_db_new,
                    "pmt_gateway_2": payment_gateway_db_new,
                    "mid_2": mid_db_new,
                    "tid_2": tid_db_new,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                    "bqr_pmt_status_2": bqr_status_db_new, "bqr_pmt_state_2": bqr_state_db_new,
                    "bqr_txn_amt_2": bqr_amount_db_new,
                    "brq_terminal_info_id_2": brq_terminal_info_id_db_new,
                    "bqr_bank_code_2": bqr_bank_code_db_new,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_new,
                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_new,
                    "bqr_rrn_2": bqr_rrn_db_new, "bqr_org_code_2": bqr_org_code_db_new,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_upg)
                expected_portal_values = {
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "UPG_AUTHORIZED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": "{:.2f}".format(amount_2),
                    "username_2": "EZETAP",
                    "txn_id_2": txn_id_upg,
                    "auth_code_2": "-" if auth_code_upg is None else auth_code_upg,
                    "rrn_2": str(rrn_upg)
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref_upg)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
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
