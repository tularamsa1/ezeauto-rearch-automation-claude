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
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_110_010():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Full_Refund_Via_API_MultiAcc_HDFC
    Sub Feature Description: Multi Account - Verification of a BQRV4_UPI full refund using api for HDFC
    TC naming code description: 100: Payment Method, 110: MultiAcc_BQR, 010: TC010
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"query to fetch bqr config data for current merchant : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        bqr_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched bqr_acc_label_id : {bqr_acc_label_id}")
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
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

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(201, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate_multiAcc', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id),
                "accountLabel": str(account_label_name)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the bqrGenerate : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            rrn = result['rr_number'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            auth_code = result['auth_code'].values[0]
            created_time = result['created_time'].values[0]
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {label_ids}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password, "amount": amount,
                "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")
            txn_id_new_2 = response["txnId"]
            logger.debug(f"Fetching refund_txn_id from the API_OUTPUT, refund_txn_id : {txn_id_new_2}")

            query = f"select * from txn where id = '{str(txn_id_new_2)}';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"result : {result}, for the query : {query}")
            rrn_new_2 = result['rr_number'].values[0]
            customer_name_new_2 = result['customer_name'].values[0]
            payer_name_new_2 = result['payer_name'].values[0]
            auth_code_new_2 = result['auth_code'].values[0]
            created_time_new_2 = result['created_time'].values[0]
            label_ids_new_2 = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {label_ids_new_2}")

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
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_new_2)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_new_2,
                    "rrn_2": str(rrn_new_2),
                    "customer_name_2": customer_name_new_2,
                    "payer_name_2": payer_name_new_2,
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "auth_code_2": auth_code_new_2,
                    "date_2": date_and_time_new_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
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
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new_2)
                payment_status_new_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new_2}, {payment_status_new_2}")
                app_date_and_time_new_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new_2}, {app_date_and_time_new_2}")
                app_auth_code_new_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new_2}, {app_auth_code_new_2}")
                payment_mode_new_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id_new_2}, {payment_mode_new_2}")
                app_txn_id_new_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_2}, {app_txn_id_new_2}")
                app_amount_new_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new_2}, {app_amount_new_2}")
                app_customer_name_new_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_new_2}, {app_customer_name_new_2}")
                app_settlement_status_new_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new_2}, {app_settlement_status_new_2}")
                app_payer_name_new_2 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {txn_id_new_2}, {app_payer_name_new_2}")
                app_payment_msg_new_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new_2}, {app_payment_msg_new_2}")
                app_order_id_new_2 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {txn_id_new_2}, {app_order_id_new_2}")
                app_rrn_new_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_2}, {app_rrn_new_2}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new_2,
                    "pmt_status_2": payment_status_new_2.split(':')[1],
                    "txn_amt_2": app_amount_new_2.split(' ')[1],
                    "txn_id_2": app_txn_id_new_2,
                    "rrn_2": str(app_rrn_new_2),
                    "customer_name_2": app_customer_name_new_2,
                    "settle_status_2": app_settlement_status_new_2,
                    "payer_name_2": app_payer_name_new_2,
                    "order_id_2": app_order_id_new_2,
                    "payment_msg_2": app_payment_msg_new_2,
                    "auth_code_2": app_auth_code_new_2,
                    "date_2": app_date_and_time_new_2
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
                date_new = date_time_converter.db_datetime(created_time)
                date_new_2 = date_time_converter.db_datetime(created_time_new_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "REFUNDED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE", "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_new,
                    "order_id": order_id,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED", "rrn_2": str(rrn_new_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND", "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_new_2,
                    "date_2": date_new_2,
                    "order_id_2": order_id,
                    "account_label": str(account_label_name),
                    "account_label_2": str(account_label_name),
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                txn_list_response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {txn_list_response}")
                response = [x for x in txn_list_response["txns"] if x["txnId"] == txn_id][0]
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
                date_api = response["createdTime"]
                order_id_api = response["orderNumber"]
                account_label_name_api = response["accountLabel"]

                # Fetching txn data from the same response for refunded txn
                response = [x for x in txn_list_response["txns"] if x["txnId"] == txn_id_new_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_2 = response["status"]
                amount_api_new_2 = float(response["amount"])
                payment_mode_api_new_2 = response["paymentMode"]
                state_api_new_2 = response["states"][0]
                rrn_api_new_2 = response["rrNumber"]
                settlement_status_api_new_2 = response["settlementStatus"]
                acquirer_code_api_new_2 = response["acquirerCode"]
                orgCode_api_new_2 = response["orgCode"]
                mid_api_new_2 = response["mid"]
                tid_api_new_2 = response["tid"]
                txn_type_api_new_2 = response["txnType"]
                auth_code_api_new_2 = response["authCode"]
                date_api_new_2 = response["createdTime"]
                order_id_api_new_2 = response["orderNumber"]
                account_label_name_api_2 = response["accountLabel"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2, "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2, "rrn_2": str(rrn_api_new_2),
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2, "mid_2": mid_api_new_2, "tid_2": tid_api_new_2,
                    "org_code_2": orgCode_api_new_2,
                    "auth_code_2": auth_code_api_new_2,
                    "order_id_2": order_id_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2),
                    "account_label": str(account_label_name_api),
                    "account_label_2": str(account_label_name_api_2),
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
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_type": "PAY_BQR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "bqr_pmt_status": "SUCCESS", "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "payment_gateway_2": "HDFC",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "order_id_2": order_id,
                    "upi_acc_label_id": str(upi_acc_label_id),
                    "upi_acc_label_id_2": str(upi_acc_label_id),
                    "bqr_acc_label_id": str(bqr_acc_label_id),
                    "bqr_acc_label_id_2": str(bqr_acc_label_id),
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = float(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                order_id_db = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from txn where id='" + txn_id_new_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new_2 = result["status"].iloc[0]
                payment_mode_db_new_2 = result["payment_mode"].iloc[0]
                amount_db_new_2 = float(result["amount"].iloc[0])
                state_db_new_2 = result["state"].iloc[0]
                payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
                settlement_status_db_new_2 = result["settlement_status"].iloc[0]
                tid_db_new_2 = result['tid'].values[0]
                mid_db_new_2 = result['mid'].values[0]
                order_id_db_new_2 = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_2 = result["status"].iloc[0]
                upi_txn_type_db_new_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_2 = result["upi_mc_id"].iloc[0]

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
                    "order_id": order_id_db,
                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
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
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "mid_2": mid_db_new_2,
                    "tid_2": tid_db_new_2,
                    "order_id_2": order_id_db_new_2,
                    "upi_acc_label_id": str(label_ids),
                    "upi_acc_label_id_2": str(label_ids_new_2),
                    "bqr_acc_label_id": str(label_ids),
                    "bqr_acc_label_id_2": str(label_ids_new_2),
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
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_time_new_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str(amount) + ".00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_new_2,
                    "auth_code_2": "-" if auth_code_new_2 is None else auth_code_new_2,
                    "rrn_2": "-" if rrn_new_2 is None else rrn_new_2,
                    "acc_label": account_label_name,
                    "acc_label_2": account_label_name
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                labels = transaction_details[1]['Labels']
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                labels_2 = transaction_details[0]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": str(total_amount_2[1]),
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "acc_label": labels,
                    "acc_label_2": labels_2
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_new_2)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_new_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': auth_code_new_2
                }
                receipt_validator.perform_charge_slip_validations(txn_id_new_2,
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
def test_common_100_110_011():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Partial_Refund_Via_API_MultiAcc_HDFC
    Sub Feature Description: Multi Account - Verification of a BQR 4_UPI partial refund using api for HDFC
    TC naming code description: 100: Payment Method, 110: MultiAcc_BQR, 011: TC011
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"query to fetch bqr config data for current merchant : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        bqr_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched bqr_acc_label_id : {bqr_acc_label_id}")
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
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

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(201, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate_multiAcc', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id),
                "accountLabel": str(account_label_name)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            rrn = result['rr_number'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            auth_code = result['auth_code'].values[0]
            created_date = result['created_time'].values[0]
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {label_ids}")

            amount_new_2 = amount - 100

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password, "amount": amount_new_2,
                "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")
            txn_id_new_2 = response["txnId"]
            logger.debug(f"Fetching refund_txn_id from the API_OUTPUT, refund_txn_id : {txn_id_new_2}")

            query = f"select * from txn where id = '{str(txn_id_new_2)}';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn_new_2 = result['rr_number'].values[0]
            customer_name_new_2 = result['customer_name'].values[0]
            payer_name_new_2 = result['payer_name'].values[0]
            auth_code_new_2 = result['auth_code'].values[0]
            created_date_new_2 = result['created_time'].values[0]
            label_ids_2 = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {label_ids_2}")

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
                date_and_time_new_2 = date_time_converter.to_app_format(created_date_new_2)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": "{:.2f}".format(amount_new_2),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_new_2,
                    "rrn_2": str(rrn_new_2),
                    "customer_name_2": customer_name_new_2,
                    "payer_name_2": payer_name_new_2,
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "auth_code_2": auth_code_new_2,
                    "date_2": date_and_time_new_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
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
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new_2)
                payment_status_new_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new_2}, {payment_status_new_2}")
                app_date_and_time_new_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new_2}, {app_date_and_time_new_2}")
                app_auth_code_new_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new_2}, {app_auth_code_new_2}")
                payment_mode_new_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id_new_2}, {payment_mode_new_2}")
                app_txn_id_new_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_2}, {app_txn_id_new_2}")
                app_amount_new_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new_2}, {app_amount_new_2}")
                app_customer_name_new_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_new_2}, {app_customer_name_new_2}")
                app_settlement_status_new_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new_2}, {app_settlement_status_new_2}")
                app_payer_name_new_2 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {txn_id_new_2}, {app_payer_name_new_2}")
                app_payment_msg_new_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new_2}, {app_payment_msg_new_2}")
                app_order_id_new_2 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {txn_id_new_2}, {app_order_id_new_2}")
                app_rrn_new_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_2}, {app_rrn_new_2}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new_2,
                    "pmt_status_2": payment_status_new_2.split(':')[1],
                    "txn_amt_2": app_amount_new_2.split(' ')[1],
                    "txn_id_2": app_txn_id_new_2,
                    "rrn_2": str(app_rrn_new_2),
                    "customer_name_2": app_customer_name_new_2,
                    "settle_status_2": app_settlement_status_new_2,
                    "payer_name_2": app_payer_name_new_2,
                    "order_id_2": app_order_id_new_2,
                    "payment_msg_2": app_payment_msg_new_2,
                    "auth_code_2": app_auth_code_new_2,
                    "date_2": app_date_and_time_new_2
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
                date_new = date_time_converter.db_datetime(created_date)
                date_new_2 = date_time_converter.db_datetime(created_date_new_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE", "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_new,
                    "order_id": order_id,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount_new_2), "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED", "rrn_2": str(rrn_new_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND", "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_new_2,
                    "date_2": date_new_2,
                    "order_id_2": order_id,
                    "account_label": str(account_label_name),
                    "account_label_2": str(account_label_name),
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                txn_list_response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {txn_list_response}")
                response = [x for x in txn_list_response["txns"] if x["txnId"] == txn_id][0]
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
                date_api = response["createdTime"]
                order_id_api = response["orderNumber"]
                account_label_name_api = response["accountLabel"]

                # Fetching txn data from the same response for refunded txn
                response = [x for x in txn_list_response["txns"] if x["txnId"] == txn_id_new_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_2 = response["status"]
                amount_api_new_2 = float(response["amount"])
                payment_mode_api_new_2 = response["paymentMode"]
                state_api_new_2 = response["states"][0]
                rrn_api_new_2 = response["rrNumber"]
                settlement_status_api_new_2 = response["settlementStatus"]
                acquirer_code_api_new_2 = response["acquirerCode"]
                orgCode_api_new_2 = response["orgCode"]
                mid_api_new_2 = response["mid"]
                tid_api_new_2 = response["tid"]
                txn_type_api_new_2 = response["txnType"]
                auth_code_api_new_2 = response["authCode"]
                date_api_new_2 = response["createdTime"]
                order_id_api_new_2 = response["orderNumber"]
                account_label_name_api_new_2 = response["accountLabel"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2, "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2, "rrn_2": str(rrn_api_new_2),
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2, "mid_2": mid_api_new_2, "tid_2": tid_api_new_2,
                    "org_code_2": orgCode_api_new_2,
                    "auth_code_2": auth_code_api_new_2,
                    "order_id_2": order_id_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2),
                    "account_label": str(account_label_name_api),
                    "account_label_2": str(account_label_name_api_new_2),
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
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "PAY_BQR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "bqr_pmt_status": "SUCCESS", "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount_new_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "payment_gateway_2": "HDFC",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "order_id_2": order_id,
                    "upi_acc_label_id": str(upi_acc_label_id),
                    "upi_acc_label_id_2": str(upi_acc_label_id),
                    "bqr_acc_label_id": str(bqr_acc_label_id),
                    "bqr_acc_label_id_2": str(bqr_acc_label_id),
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = float(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                order_id_db = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from txn where id='" + txn_id_new_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new_2 = result["status"].iloc[0]
                payment_mode_db_new_2 = result["payment_mode"].iloc[0]
                amount_db_new_2 = float(result["amount"].iloc[0])
                state_db_new_2 = result["state"].iloc[0]
                payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
                settlement_status_db_new_2 = result["settlement_status"].iloc[0]
                tid_db_new_2 = result['tid'].values[0]
                mid_db_new_2 = result['mid'].values[0]
                order_id_db_new_2 = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_2 = result["status"].iloc[0]
                upi_txn_type_db_new_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_2 = result["upi_mc_id"].iloc[0]

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
                    "order_id": order_id_db,
                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
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
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "mid_2": mid_db_new_2,
                    "tid_2": tid_db_new_2,
                    "order_id_2": order_id_db_new_2,
                    "upi_acc_label_id": str(label_ids),
                    "upi_acc_label_id_2": str(label_ids_2),
                    "bqr_acc_label_id": str(label_ids),
                    "bqr_acc_label_id_2": str(label_ids_2),
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
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_date_new_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str(amount_new_2) + ".00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_new_2,
                    "auth_code_2": "-" if auth_code_new_2 is None else auth_code_new_2,
                    "rrn_2": "-" if rrn_new_2 is None else rrn_new_2,
                    "acc_label": account_label_name,
                    "acc_label_2": account_label_name
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                labels = transaction_details[1]['Labels']
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                labels_2 = transaction_details[0]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": str(total_amount_2[1]),
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "acc_label": labels,
                    "acc_label_2": labels_2
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_date)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_date_new_2)
                expected_chargeslip_values_original = {'PAID BY:': 'UPI', 'AUTH CODE': auth_code,
                                                       'merchant_ref_no': 'Ref # ' + str(order_id),
                                                       'RRN': str(rrn), 'time': txn_time, 'date': txn_date,
                                                       'BASE AMOUNT:': "Rs." + str(amount) + ".00"}
                expected_chargeslip_values_refunded = {'PAID BY:': 'UPI', 'AUTH CODE': auth_code_new_2,
                                                       'merchant_ref_no': 'Ref # ' + str(order_id),
                                                       'RRN': str(rrn_new_2), 'time': txn_time_2, 'date': txn_date_2,
                                                       'BASE AMOUNT:': "Rs." + str(amount_new_2) + ".00"}
                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password},
                    expected_chargeslip_values_original)
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(
                    txn_id_new_2, {"username": app_username, "password": app_password},
                    expected_chargeslip_values_refunded)

                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

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
