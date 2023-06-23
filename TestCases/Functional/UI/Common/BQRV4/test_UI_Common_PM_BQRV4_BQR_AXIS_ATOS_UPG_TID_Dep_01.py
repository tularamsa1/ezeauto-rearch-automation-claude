import random
import sys
from datetime import datetime

import pytest

from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
def test_common_100_102_294():
    """
    Sub Feature code: TID_Dep_UI_Common_BQRV4_BQR_Callback_Amount_Mismatch_AXIS_ATOS
    Sub Feature Description: TID Dep - Verification of a BQR amount missmatch upon callback via AXIS_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 294: TC294
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')
        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='BHARATQR' and acquirer_code='AXIS' and payment_gateway='ATOS';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='AXIS'"
        result = DBProcessor.getValueFromDB(query)

        merchant_config_id = result["id"].iloc[0]
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        merchant_pan = result['merchant_pan'].values[0]
        vtid = result["virtual_tid"].iloc[0]

        query = "select device_serial from terminal_info where tid = '" + str(vtid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetching device_serial : {device_serial}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(301, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)

            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching txn_id, posting date from the txn table :{txn_id}, {created_time}")

            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id ='"+txn_id+"';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            provide_ref_id = result["provider_ref_id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            amount = amount+1

            api_details = DBProcessor.get_api_details('callback_Bqr_AXIS',
                                                      request_body={"primary_id": provide_ref_id,
                                                                    "secondary_id":provide_ref_id,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no":rrn,
                                                                    "mid":mid, "mpan": merchant_pan,
                                                                    "settlement_amount": str(amount)
                                                                    }
                                                      )
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for BQR call back : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + provide_ref_id + "';")
            logger.debug(f"query to fetch data from the invalid_pg_request table : {query}")
            result = DBProcessor.getValueFromDB(query)
            ipr_txn_id = result['txn_id'].iloc[0]
            logger.debug(f"txn_id from invalid_pg_request table is : {ipr_txn_id}")

            ipr_payment_mode = result["payment_mode"].iloc[0]
            ipr_auth_code = result["auth_code"].iloc[0]
            ipr_bank_code = result["bank_code"].iloc[0]
            ipr_org_code = result["org_code"].iloc[0]
            ipr_amount = result["amount"].iloc[0]
            ipr_rrn = result["rrn"].iloc[0]
            ipr_mid = result["mid"].iloc[0]
            ipr_tid = result["tid"].iloc[0]
            ipr_config_id = result["config_id"].iloc[0]
            ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
            ipr_error_message = result["error_message"].iloc[0]
            logger.debug(f"ipr_error_message from invalid_pg_request : {ipr_error_message}")

            query = "select * from txn where id = '" + ipr_txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : created_time : {created_time}")
            status_db = result["status"].iloc[0]
            payment_mode_db = result["payment_mode"].iloc[0]
            amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
            state_db = result["state"].iloc[0]
            payment_gateway_db = result["payment_gateway"].iloc[0]
            acquirer_code_db = result["acquirer_code"].iloc[0]
            bank_code_db = result["bank_code"].iloc[0]
            settlement_status_db = result["settlement_status"].iloc[0]
            tid_db = result['tid'].values[0]
            mid_db = result['mid'].values[0]

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch pending txn details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            status_db_1 = result["status"].iloc[0]
            payment_mode_db_1 = result["payment_mode"].iloc[0]
            amount_db_1 = int(result["amount"].iloc[0])
            state_db_1 = result["state"].iloc[0]
            payment_gateway_db_1 = result["payment_gateway"].iloc[0]
            acquirer_code_db_1 = result["acquirer_code"].iloc[0]
            bank_code_db_1 = result["bank_code"].iloc[0]
            settlement_status_db_1 = result["settlement_status"].iloc[0]
            tid_db_1 = result['tid'].values[0]
            mid_db_1 = result['mid'].values[0]
            device_serial_db_1 = result['device_serial'].values[0]

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
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": ipr_txn_id,
                    "rrn": str(rrn),
                    "order_id": external_ref,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,

                    "pmt_mode_1": "BHARAT QR",
                    "pmt_status_1": "PENDING",
                    "txn_amt_1": str(amount-1) + ".00",
                    "settle_status_1": "PENDING",
                    "order_id_1": order_id,
                    "pmt_msg_1": "PAYMENT PENDING",
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                logger.info("resetting the app")

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
                txn_history_page.click_on_transaction_by_txn_id(ipr_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {ipr_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {ipr_txn_id}, {app_date_and_time}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {ipr_txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {ipr_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {ipr_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {ipr_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {ipr_txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {ipr_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status_1}")
                app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_1}")
                payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode_1}")
                app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id_1}")
                app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount_1}")
                app_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status_1}")
                app_payment_msg_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg_1}")
                app_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id_1}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,

                    "pmt_mode_1": payment_mode_1,
                    "pmt_status_1": payment_status_1.split(':')[1],
                    "txn_amt_1": app_amount_1.split(' ')[1],
                    "settle_status_1": app_settlement_status_1,
                    "order_id_1": app_order_id_1,
                    "pmt_msg_1": app_payment_msg_1,
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
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": amount, "pmt_mode": "BHARATQR",
                    "pmt_state": "UPG_AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "auth_code": auth_code,
                    "date": date,

                    "pmt_status_1": "PENDING",
                    "txn_amt_1": amount-1,
                    "pmt_mode_1": "BHARATQR",
                    "pmt_state_1": "PENDING",
                    "settle_status_1": "PENDING",
                    "acquirer_code_1": "AXIS",
                    "issuer_code_1": "AXIS",
                    "txn_type_1": txn_type,
                    "mid_1": mid,
                    "tid_1": tid,
                    "org_code_1": org_code_txn,
                    "device_serial_1": str(device_serial)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_ipr = [x for x in response["txns"] if x["txnId"] == ipr_txn_id][0]
                logger.debug(f"Response after filtering data of authorized txn is : {response_ipr}")

                status_api = response_ipr["status"]
                amount_api = float(response_ipr["amount"])
                payment_mode_api = response_ipr["paymentMode"]
                state_api = response_ipr["states"][0]
                rrn_api = response_ipr["rrNumber"]
                settlement_status_api = response_ipr["settlementStatus"]
                issuer_code_api = response_ipr["issuerCode"]
                acquirer_code_api = response_ipr["acquirerCode"]
                orgCode_api = response_ipr["orgCode"]
                mid_api = response_ipr["mid"]
                tid_api = response_ipr["tid"]
                txn_type_api = response_ipr["txnType"]
                auth_code_api = response_ipr["authCode"]
                date_api = response_ipr["createdTime"]

                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api_1 = response_1["status"]
                amount_api_1 = float(response_1["amount"])
                payment_mode_api_1 = response_1["paymentMode"]
                state_api_1 = response_1["states"][0]
                settlement_status_api_1 = response_1["settlementStatus"]
                issuer_code_api_1 = response_1["issuerCode"]
                acquirer_code_api_1 = response_1["acquirerCode"]
                orgCode_api_1 = response_1["orgCode"]
                mid_api_1 = response_1["mid"]
                tid_api_1 = response_1["tid"]
                txn_type_api_1 = response_1["txnType"]
                device_serial_api_1 = response_1["deviceSerial"]

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
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),

                    "pmt_status_1": status_api_1,
                    "txn_amt_1": amount_api_1, "pmt_mode_1": payment_mode_api_1,
                    "pmt_state_1": state_api_1,
                    "settle_status_1": settlement_status_api_1,
                    "acquirer_code_1": acquirer_code_api_1,
                    "issuer_code_1": issuer_code_api_1,
                    "txn_type_1": txn_type_api_1, "mid_1": mid_api_1, "tid_1": tid_api_1,
                    "org_code_1": orgCode_api_1,
                    "device_serial_1": str(device_serial_api_1)
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "ATOS",
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_status_code": "SUCCESS",
                    "bqr_pmt_state": "UPG_AUTHORIZED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "UNKNOWN",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": ipr_txn_id,
                    "bqr_merchant_pan": merchant_pan,
                    "bqr_rrn": rrn,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "AXIS",
                    "ipr_pmt_mode": "BHARATQR",
                    "ipr_bank_code": "AXIS",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_config_id": merchant_config_id,
                    "ipr_pg_merchant_id": merchant_pan,
                    "ipr_error_msg": "Actual =" + str(amount) + " Expected =" + str(amount - 1) + ".00",

                    "pmt_status_1": "PENDING",
                    "pmt_state_1": "PENDING",
                    "pmt_mode_1": "BHARATQR",
                    "txn_amt_1": amount-1,
                    "settle_status_1": "PENDING",
                    "acquirer_code_1": "AXIS",
                    "bank_code_1": "AXIS",
                    "pmt_gateway_1": "ATOS",
                    "mid_1": mid,
                    "tid_1": tid,
                    "bqr_pmt_status_code_1": None,
                    "bqr_pmt_state_1": "PENDING",
                    "bqr_txn_amt_1": amount-1,
                    "bqr_txn_type_1": "DYNAMIC_QR",
                    "bqr_terminal_info_id_1": terminal_info_id,
                    "bqr_merchant_config_id_1": merchant_config_id,
                    "bqr_txn_primary_id_1": txn_id,
                    "bqr_org_code_1": org_code,
                    "bqr_bank_code_1": "AXIS",
                    "device_serial_1": str(device_serial)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + ipr_txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_txn_amt_db = result["txn_amount"].iloc[0]
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result["rrn"].iloc[0]
                bqr_org_code_db = result["org_code"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data pending txn from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db_1 = result["status_code"].iloc[0]
                bqr_state_db_1 = result["state"].iloc[0]
                bqr_txn_amt_db_1 = result["txn_amount"].iloc[0]
                bqr_txn_type_db_1 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_1 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_1 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_1 = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db_1 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_1 = result["org_code"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bqr_pmt_status_code": bqr_status_code_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_auth_code": ipr_auth_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                    "ipr_error_msg": ipr_error_message,

                    "pmt_status_1": status_db_1,
                    "pmt_state_1": state_db_1,
                    "pmt_mode_1": payment_mode_db_1,
                    "txn_amt_1": amount_db_1,
                    "settle_status_1": settlement_status_db_1,
                    "acquirer_code_1": acquirer_code_db_1,
                    "bank_code_1": bank_code_db_1,
                    "pmt_gateway_1": payment_gateway_db_1,
                    "mid_1": mid_db_1,
                    "tid_1": tid_db_1,
                    "bqr_pmt_status_code_1": bqr_status_code_db_1,
                    "bqr_pmt_state_1": bqr_state_db_1,
                    "bqr_txn_amt_1": bqr_txn_amt_db_1,
                    "bqr_txn_type_1": bqr_txn_type_db_1,
                    "bqr_terminal_info_id_1": bqr_terminal_info_id_db_1,
                    "bqr_merchant_config_id_1": bqr_merchant_config_id_db_1,
                    "bqr_txn_primary_id_1": bqr_transaction_primary_id_db_1,
                    "bqr_org_code_1": bqr_org_code_db_1,
                    "bqr_bank_code_1": bqr_bank_code_db_1,
                    "device_serial_1": device_serial_db_1
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
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": "EZETAP",
                    "txn_id": ipr_txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code_portal = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']

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