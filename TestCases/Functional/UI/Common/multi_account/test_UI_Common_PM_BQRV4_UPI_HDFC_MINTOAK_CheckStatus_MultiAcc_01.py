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
def test_common_100_110_054():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Success_Via_SA_CheckStatus_MultiAcc_HDFC_MINTOAK
    Sub Feature Description: Multi Account - Verification of a successful BQRV4 upi txn via HDFC_MINTOAK using SA check status
    TC naming code description: 100: Payment Method 110: MultiAcc_BQR, 054: TC054
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
                                                           portal_un=portal_username, portal_pw=portal_password,
                                                           payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"query to fetch bqr config data for current merchant : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
        mid = result["mid"].values[0]
        logger.debug(f"fetched bqr_acc_label_id : {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"fetched tid : {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"fetched terminal_info_id : {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"fetched bqr_mc_id : {bqr_mc_id}")
        bqr_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched bqr_acc_label_id : {bqr_acc_label_id}")

        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id from database for current merchant: {upi_mc_id}")
        upi_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched upi_acc_label_id : {upi_acc_label_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ----------------------------------------PreConditions(Completed)-------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            amount = random.randint(401, 500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Clicking on proceed to home page button on the Payment successful screen on the MPOS")
            payment_page.click_on_proceed_homepage()
            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching Transaction ID from txn: {txn_id}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching RRN from txn: {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching Customer Name from txn: {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching Payer Name from txn: {payer_name}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching Auth Code from txn: {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching Posting Date from txn: {created_time}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {label_ids}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

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
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
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
                date = date_time_converter.db_datetime(created_time)
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
                    "order_id": order_id,
                    "accountLabel": str(account_label_name)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
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
                account_label_name_api = response["accountLabel"]
                logger.debug(
                    f"Details from Original TXN: status:{status_api}, amount:{amount_api}, org_code_api:{org_code_api}, payment mode:{payment_mode_api}, state:{state_api}, settlement status:{settlement_status_api}, issuer code:{issuer_code_api}, acquirer code:{acquirer_code_api}, account_label_name_api:{account_label_name_api}, mid:{mid_api}, tid:{tid_api}, txn type:{txn_type_api}, date:{date_api}")

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
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "accountLabel": str(account_label_name_api)
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
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "MINTOAK",
                    "upi_txn_type": "PAY_BQR",
                    "upi_bank_code": "HDFC_MINTOAK",
                    "rrn": rrn,
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "bqr_pmt_status": "INITIATED BY UPI",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "upi_acc_label_id": str(upi_acc_label_id),
                    "bqr_acc_label_id": str(bqr_acc_label_id)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                logger.debug(f"Fetching details from the database for Transaction ID: {txn_id}")
                status_db = result["status"].values[0]
                logger.debug(f"Fetching Payment Status: {status_db}")
                payment_mode_db = result["payment_mode"].values[0]
                logger.debug(f"Fetching Payment Mode: {payment_mode_db}")
                amount_db = float(result["amount"].values[0])
                logger.debug(f"Fetching Amount: {amount_db}")
                state_db = result["state"].values[0]
                logger.debug(f"Fetching Payment State: {state_db}")
                payment_gateway_db = result["payment_gateway"].values[0]
                logger.debug(f"Fetching Payment Gateway: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].values[0]
                logger.debug(f"Fetching Acquirer Code: {acquirer_code_db}")
                bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code: {bank_code_db}")
                settlement_status_db = result["settlement_status"].values[0]
                logger.debug(f"Fetching Settlement Status: {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching TID: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching MID: {mid_db}")
                order_id_db = result['external_ref'].values[0]
                logger.debug(f"Fetching OrderID: {order_id_db}")
                rrn_db = result['rr_number'].values[0]
                logger.debug(f"Fetching RRN: {rrn_db}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"Status:{upi_status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"txn type:{upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Bank code:{upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"MC ID:{upi_mc_id_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Fetching details from bharatqr_txn table for ID {txn_id}:")
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                logger.debug(f"Payment status : {bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"State: {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].values[0])
                logger.debug(f"Amount: {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Transaction Type: {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Terminal Info ID: {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Bank Code: {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Merchant Config ID: {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Transaction Primary ID: {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Org code: {bqr_org_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "rrn": rrn_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "order_id": order_id_db,
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "upi_acc_label_id": str(label_ids),
                    "bqr_acc_label_id": str(label_ids)
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
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": rrn,
                    "acc_label": account_label_name
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Date and Time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"Transaction ID: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Total Amount: {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Auth Code (Portal): {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"RR Number: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"Transaction Type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"Status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"Username: {username}")
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
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
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
                    'AUTH CODE': "" if auth_code is None else auth_code
                }
                receipt_validator.perform_charge_slip_validations(txn_id,
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
def test_common_100_110_055():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Failed_Via_SA_CheckStatus_MultiAcc_HDFC_MINTOAK
    Sub Feature Description: Multi Account - Verification of a failed BQRV4_UPI txn via HDFC_MINTOAK using SA check status
    TC naming code description: 100: Payment Method 110: MultiAcc_BQR, 055: TC055
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

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"query to fetch bqr config data for current merchant : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
        mid = result["mid"].values[0]
        logger.debug(f"MID: {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"TID: {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"Terminal Info ID: {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"BQR MC ID: {bqr_mc_id}")
        bqr_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched bqr_acc_label_id : {bqr_acc_label_id}")

        query = f"select * from upi_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        upi_acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"fetched upi_acc_label_id : {upi_acc_label_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            amount = random.randint(301, 310)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Clicking on proceed to home page button on the Payment successful screen on the MPOS")
            payment_page.click_on_proceed_homepage()
            payment_page.click_on_back_btn()
            payment_page.click_on_back_btn_in_enter_amt_window()

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching details from the txn table:")
            txn_id = result['id'].values[0]
            logger.debug(f"Transaction ID: {txn_id}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"RRN: {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Auth Code: {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Posting Date: {created_time}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {label_ids}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

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
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching app_rrn from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "order_id": order_id,
                    "accountLabel": str(account_label_name)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                logger.debug(f"Details from Original TXN:")
                status_api = response["status"]
                logger.debug(f"status:{status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"amount:{amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment mode:{payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state:{state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement status:{settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer code:{issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer code:{acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api:{org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"mid:{mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid:{tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn type:{txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"date:{date_api}")
                order_id_api = response["orderNumber"]
                logger.debug(f"Order ID:{order_id_api}")
                account_label_name_api = response["accountLabel"]
                logger.debug(f"account_label_name_api:{account_label_name_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "accountLabel": str(account_label_name_api)
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
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "upi_txn_status": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "MINTOAK",
                    "upi_txn_type": "PAY_BQR",
                    "upi_bank_code": "HDFC_MINTOAK",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "bqr_pmt_status": "INITIATED BY UPI", "bqr_pmt_state": "FAILED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "upi_acc_label_id": str(upi_acc_label_id),
                    "bqr_acc_label_id": str(bqr_acc_label_id)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                logger.debug(f"Fetching Payment Status from txn table: {status_db}")
                payment_mode_db = result["payment_mode"].values[0]
                logger.debug(f"Fetching Payment Mode from txn table: {payment_mode_db}")
                amount_db = float(result["amount"].values[0])
                logger.debug(f"Fetching Amount from txn table: {amount_db}")
                state_db = result["state"].values[0]
                logger.debug(f"Fetching Payment State from txn table: {state_db}")
                payment_gateway_db = result["payment_gateway"].values[0]
                logger.debug(f"Fetching Payment Gateway from txn table: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].values[0]
                logger.debug(f"Fetching Acquirer Code from txn table: {acquirer_code_db}")
                bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bank_code_db from txn table: {bank_code_db}")
                settlement_status_db = result["settlement_status"].values[0]
                logger.debug(f"Fetching Settlement Status from txn table: {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching TID from txn table: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching MID from txn table: {mid_db}")
                order_id_db = result['external_ref'].values[0]
                logger.debug(f"Fetching Order ID from txn table: {order_id_db}")

                logger.debug(f"Fetching details from the database for Transaction ID: {txn_id}")
                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"Fetching Status from upi_txn table: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type from upi_txn table: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from upi_txn table: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching MC ID from upi_txn table: {upi_mc_id_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                logger.debug(f"Fetching details from BharatQR transaction table for ID {txn_id}:")
                bqr_status_db = result["status_desc"].values[0]
                logger.debug(f"Fetching bqr_status_db from bharatqr_txn table: {bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching State from bharatqr_txn table: {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].values[0])
                logger.debug(f"Fetching Amount from bharatqr_txn table: {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type from bharatqr_txn table: {bqr_txn_type_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching Terminal Info ID from bharatqr_txn table: {brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from bharatqr_txn table: {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching Merchant Config ID from bharatqr_txn table: {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching Transaction Primary ID from bharatqr_txn table: {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching Org Code from bharatqr_txn table: {bqr_org_code_db}")

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
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "upi_acc_label_id": str(label_ids),
                    "bqr_acc_label_id": str(label_ids)
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
                    "pmt_state": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else rrn,
                    "acc_label": account_label_name
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                logger.debug(f"Portal details for transaction:")
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Date and Time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"Transaction ID: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Total Amount: {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Auth Code (Portal): {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"RR Number: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"Transaction Type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"Status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"Username: {username}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")

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
@pytest.mark.chargeSlipVal
def test_common_100_110_056():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Success_Via_SA_CheckStatus_with_2nd_label_MultiAcc_HDFC_Mintoak
    Sub Feature Description: Multi Account - Performing a successful BQRV4_UPI txn via HDFC_MINTOAK using SA check status via second account (ex:acc2 label)
    TC naming code description: 100: Payment Method, 110: MultiAcc_BQR, 056: TC056
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
                                                           payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(org_code=org_code,
                                                                                       portal_un=portal_username,
                                                                                       portal_pw=portal_password)
        account_label_name = account_labels['name2']
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code}
                                                  )
        api_details["RequestBody"]["settings"] = {"defaultAccount": f"{account_label_name}"}
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting defaultAccount is : {response}")

        query = f"select * from bharatqr_merchant_config where status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"query to fetch bqr config data for current merchant : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"result : {result}, for the query : {query}")
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
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            amount = random.randint(450, 500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Clicking on proceed to home page button on the Payment successful screen on the MPOS")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}'"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            rrn = result['rr_number'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            auth_code = result['auth_code'].values[0]
            created_time = result['created_time'].values[0]
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"fetched label_ids from txn table is : {label_ids}")
            logger.debug(f"Fetching txn_id, rrn, cust name, payer name, authcode and posting date from the txn table :"
                         f"{txn_id}, {rrn}, {customer_name}, {payer_name}, {auth_code}, {created_time}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

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
                date = date_time_converter.db_datetime(created_time)
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
                    "order_id": order_id,
                    "accountLabel": str(account_label_name)
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
                logger.debug(f"Fetched settle status from api : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetched issuer code from api : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetched acquirer from api : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetched org code from api : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetched mid from api : {mid_api}")
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                logger.debug(f"Fetched tid from api : {tid_api}")
                date_api = response["createdTime"]
                logger.debug(f"Fetched date from api : {date_api}")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetched order id from api : {order_id_api}")
                account_label_name_api = response["accountLabel"]
                logger.debug(f"Fetched account label name from api : {account_label_name_api}")

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
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "accountLabel": str(account_label_name_api)
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
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "MINTOAK",
                    "upi_txn_type": "PAY_BQR",
                    "upi_bank_code": "HDFC_MINTOAK",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "bqr_pmt_status": "Success",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "upi_acc_label_id": str(upi_acc_label_id),
                    "bqr_acc_label_id": str(bqr_acc_label_id),
                    "rrn": str(rrn_api)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                logger.debug(f"Fetched status from db : {status_db}")
                payment_mode_db = result["payment_mode"].values[0]
                logger.debug(f"Fetched payment mode from db : {payment_mode_db}")
                amount_db = float(result["amount"].values[0])
                logger.debug(f"Fetched amount from db : {amount_db}")
                state_db = result["state"].values[0]
                logger.debug(f"Fetched state from db : {state_db}")
                payment_gateway_db = result["payment_gateway"].values[0]
                logger.debug(f"Fetched payment gateway from db : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].values[0]
                logger.debug(f"Fetched acquirer code from db : {acquirer_code_db}")
                bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetched bank code from db : {bank_code_db}")
                settlement_status_db = result["settlement_status"].values[0]
                logger.debug(f"Fetched settlement status from db : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetched tid from db : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetched mid from db : {mid_db}")
                order_id_db = result['external_ref'].values[0]
                logger.debug(f"Fetched order id from db : {order_id_db}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"Fetched upi status from db : {status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetched upi txn type from db : {status_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetched upi bank code from db : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"Fetched upi mc id from db : {upi_mc_id_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_code"].values[0]
                logger.debug(f"Fetched bqr status from db : {bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetched bqr state from db : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].values[0])
                logger.debug(f"Fetched bqr amount from db : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetched bqr txn type from db : {bqr_txn_type_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetched bqr terminal info id from db : {brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetched bqr bank code from db : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetched bqr merchant config id from db : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetched bqr txn primary id from db : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetched bqr org code from db : {bqr_org_code_db}")

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
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "upi_acc_label_id": str(label_ids),
                    "bqr_acc_label_id": str(label_ids),
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
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": rrn,
                    "acc_label": account_label_name
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
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
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
                    'AUTH CODE': "" if auth_code is None else auth_code
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
