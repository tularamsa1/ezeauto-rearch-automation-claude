import random
import sys
from datetime import datetime
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
def test_common_100_102_427():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_CheckStatus_HDFC_Same_Amount_Same_Order_ID
    Sub Feature Description:Perform BQRV4_BQR HDFC Successful Transactions Via CheckStatus Api with same amount and order ID.
    TC naming code description: 100: Payment Method, 102: BQR, 427: TC427
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC',
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
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        logger.debug(
            f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

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

            amount = random.randint(226, 1000)
            logger.debug(f"Generating random amount : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the bqrGenerate : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)
            })
            APIProcessor.send_request(api_details)

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")
            rrn = response['rrNumber']
            logger.debug(f"Fetching rrn from the payment status api, rrn : {rrn}")
            auth_code = response['authCode']
            logger.debug(f"Fetching auth code from the payment status api, auth_code : {auth_code}")

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id)}' ORDER BY created_time DESC limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            bank_name = result['bank_name'].values[0]
            logger.debug(f"fetched bank name from txn table is : {bank_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org code from txn table is : {org_code_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth code from txn table is : {auth_code}")

            logger.info(f"Initiating transaction with same amount: {amount} and order id: {order_id} as previous "
                        f"transaction")
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details_2 = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response_2 = APIProcessor.send_request(api_details_2)
            logger.debug(f"response received for the bqrGenerate : {response_2}")
            success_2 = response_2['success']
            logger.debug(f"Fetching success value from the API_OUTPUT : {success_2}")
            error_message = response_2['errorMessage']
            logger.debug(f"Fetching message from the API_OUTPUT : {error_message}")
            error_code = response_2['errorCode']
            logger.debug(f"Fetching real code from the API_OUTPUT : {error_code}")
            # ----------------------------------------------------------------------------------------------------------
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
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": str(order_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info("Performing Login")
                login_page.perform_login(app_username, app_password)
                logger.info("Waiting for Home Page to load")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                order_id_app = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {order_id_app}")
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
                auth_code_app = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth code from txn history for the txn : {auth_code_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "auth_code": auth_code_app,
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
                    "order_id": str(order_id),
                    "pmt_success_2": False,
                    "errorMessage": f"You have already made a similar payment for the same "
                                    f"Ref# {order_id} and amount {amount:.2f}. Please check"
                                    f" the status of the payment(s) made before you proceed.",
                    "errorCode": "EZETAP_0000033"
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
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
                    "order_id": str(order_id_api),
                    "pmt_success_2": success_2,
                    "errorMessage": error_message,
                    "errorCode": error_code
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
                    "bqr_txn_state": "SETTLED",
                    "bank_name": "HDFC Bank",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "rrn": rrn,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_bank_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id = '{str(txn_id)}';"
                logger.debug(f"Query to fetch txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                logger.info(f"Fetching status from txn table: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.info(f"Fetching amount from txn table: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.info(f"Fetching state from txn table: {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.info(f"Fetching bank code from txn table: {bank_code_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.info(f"Fetching bank name from txn table: {bank_name_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
                rrn_db = result["rr_number"].iloc[0]
                logger.info(f"Fetching rrn from txn table: {rrn_db}")
                txn_type_db = result["txn_type"].iloc[0]
                logger.info(f"Fetching txn type from txn table: {txn_type_db}")
                tid_db = result['tid'].values[0]
                logger.info(f"Fetching tid from txn table: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.info(f"Fetching mid from txn table: {mid_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["state"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_status_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_txn_type_db}")
                brq_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching details for the txn : {brq_bank_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "bqr_txn_state": bqr_status_db,
                    "bank_name": bank_name_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_bank_code": brq_bank_code_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db
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
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn)
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"fetched date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"fetched status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"fetched username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal
                }

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
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username,
                                                                   "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_428():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_CheckStatus_YES_Same_Amount_Same_Order_ID
    Sub Feature Description: Perform BQRV4_BQR YES Successful Transactions Via CheckStatus Api with same amount and order ID.
    TC naming code description: 100: Payment Method, 102: BQR, 428: TC428
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES',
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
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                "status = 'ACTIVE' and bank_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        logger.debug(
            f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")
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

            amount = random.randint(226, 1000)
            logger.debug(f"Generating random amount : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the bqrGenerate : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)
            })
            APIProcessor.send_request(api_details)

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")
            rrn = response['rrNumber']
            logger.debug(f"Fetching rrn from the payment status api, rrn : {rrn}")
            auth_code = response['authCode']
            logger.debug(f"Fetching auth code from the payment status api, auth_code : {auth_code}")

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id)}' ORDER BY created_time DESC limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            bank_name = result['bank_name'].values[0]
            logger.debug(f"fetched bank name from txn table is : {bank_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org code from txn table is : {org_code_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth code from txn table is : {auth_code}")
            logger.info(f"Initiating transaction with same amount: {amount} and order id: {order_id} as previous "
                        f"transaction")
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details_2 = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response_2 = APIProcessor.send_request(api_details_2)
            logger.debug(f"response received for the bqrGenerate : {response_2}")
            success_2 = response_2['success']
            logger.debug(f"Fetching success value from the API_OUTPUT: {success_2}")
            error_message = response_2['errorMessage']
            logger.debug(f"Fetching message from the API_OUTPUT : {error_message}")
            error_code = response_2['errorCode']
            logger.debug(f"Fetching real code from the API_OUTPUT : {error_code}")
            # ----------------------------------------------------------------------------------------------------------
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
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": str(order_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info("Performing Login")
                login_page.perform_login(app_username, app_password)
                logger.info("Waiting for Home Page to load")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                order_id_app = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {order_id_app}")
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
                auth_code_app = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth code from txn history for the txn : {auth_code_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "auth_code": auth_code_app,
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": str(order_id),
                    "pmt_success_2": False,
                    "errorMessage": f"You have already made a similar payment for the same "
                                    f"Ref# {order_id} and amount {amount:.2f}. Please check"
                                    f" the status of the payment(s) made before you proceed.",
                    "errorCode": "EZETAP_0000033"
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = response["amount"]
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
                order_id_api = response["orderNumber"]

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
                    "order_id": str(order_id_api),
                    "pmt_success_2": success_2,
                    "errorMessage": error_message,
                    "errorCode": error_code
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
                    "bqr_txn_state": "SETTLED",
                    "bank_name": "Yes Bank",
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_code": "YES",
                    "pmt_gateway": "ATOS",
                    "rrn": rrn,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_bank_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id = '{str(txn_id)}';"
                logger.debug(f"Query to fetch txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                logger.info(f"Fetching status from txn table: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.info(f"Fetching amount from txn table: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.info(f"Fetching state from txn table: {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.info(f"Fetching bank code from txn table: {bank_code_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.info(f"Fetching bank name from txn table: {bank_name_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
                rrn_db = result["rr_number"].iloc[0]
                logger.info(f"Fetching rrn from txn table: {rrn_db}")
                txn_type_db = result["txn_type"].iloc[0]
                logger.info(f"Fetching txn type from txn table: {txn_type_db}")
                tid_db = result['tid'].values[0]
                logger.info(f"Fetching tid from txn table: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.info(f"Fetching mid from txn table: {mid_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["state"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_status_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_txn_type_db}")
                brq_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching details for the txn : {brq_bank_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "bqr_txn_state": bqr_status_db,
                    "bank_name": bank_name_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_bank_code": brq_bank_code_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db
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
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn)
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"fetched date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"fetched status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"fetched username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal
                }

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
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username,
                                                                   "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_429():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_CheckStatus_AXIS_ATOS_Same_Amount_Same_Order_ID
    Sub Feature Description:Perform BQRV4_BQR  AXIS_ATOS Successful Transactions Via CheckStatus Api with same amount and order ID.
    TC naming code description: 100: Payment Method, 102: BQR, 429: TC429
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS',
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
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                "status = 'ACTIVE' and bank_code='AXIS'"

        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        logger.debug(
            f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")
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

            amount = random.randint(226, 1000)
            logger.debug(f"Generating random amount : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the bqrGenerate : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)
            })
            APIProcessor.send_request(api_details)

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")
            rrn = response['rrNumber']
            logger.debug(f"Fetching rrn from the payment status api, rrn : {rrn}")
            auth_code = response['authCode']
            logger.debug(f"Fetching auth code from the payment status api, auth_code : {auth_code}")

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id)}' ORDER BY created_time DESC limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            bank_name = result['bank_name'].values[0]
            logger.debug(f"fetched bank name from txn table is : {bank_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org code from txn table is : {org_code_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth code from txn table is : {auth_code}")

            logger.info(f"Initiating transaction with same amount: {amount} and order id: {order_id} as previous "
                        f"transaction")
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details_2 = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response_2 = APIProcessor.send_request(api_details_2)
            logger.debug(f"response received for the bqrGenerate : {response_2}")
            success_2 = response_2['success']
            logger.debug(f"Fetching success value from the API_OUTPUT, txn_id : {success_2}")
            error_message = response_2['errorMessage']
            logger.debug(f"Fetching message from the API_OUTPUT, txn_id : {error_message}")
            error_code = response_2['errorCode']
            logger.debug(f"Fetching real code from the API_OUTPUT, txn_id : {error_code}")
            # ----------------------------------------------------------------------------------------------------------
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
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": str(order_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info("Performing Login")
                login_page.perform_login(app_username, app_password)
                logger.info("Waiting for Home Page to load")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                order_id_app = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {order_id_app}")
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
                auth_code_app = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth code from txn history for the txn : {auth_code_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "auth_code": auth_code_app,
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": str(order_id),
                    "pmt_success_2": False,
                    "errorMessage": f"You have already made a similar payment for the same "
                                    f"Ref# {order_id} and amount {amount:.2f}. Please check"
                                    f" the status of the payment(s) made before you proceed.",
                    "errorCode": "EZETAP_0000033"
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = response["amount"]
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
                order_id_api = response["orderNumber"]

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
                    "order_id": str(order_id_api),
                    "pmt_success_2": success_2,
                    "errorMessage": error_message,
                    "errorCode": error_code
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
                    "bqr_txn_state": "SETTLED",
                    "bank_name": "Axis Bank",
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "ATOS",
                    "rrn": rrn,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_bank_code": "AXIS",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id = '{str(txn_id)}';"
                logger.debug(f"Query to fetch txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                logger.info(f"Fetching status from txn table: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.info(f"Fetching amount from txn table: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.info(f"Fetching state from txn table: {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.info(f"Fetching bank code from txn table: {bank_code_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.info(f"Fetching bank name from txn table: {bank_name_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
                rrn_db = result["rr_number"].iloc[0]
                logger.info(f"Fetching rrn from txn table: {rrn_db}")
                txn_type_db = result["txn_type"].iloc[0]
                logger.info(f"Fetching txn type from txn table: {txn_type_db}")
                tid_db = result['tid'].values[0]
                logger.info(f"Fetching tid from txn table: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.info(f"Fetching mid from txn table: {mid_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["state"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_status_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_txn_type_db}")
                brq_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching details for the txn : {brq_bank_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "bqr_txn_state": bqr_status_db,
                    "bank_name": bank_name_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_bank_code": brq_bank_code_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db
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
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn)
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"fetched date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"fetched status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"fetched username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal
                }

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
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username,
                                                                   "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_430():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_CheckStatus_KOTAK_WL_Same_Amount_Same_Order_ID
    Sub Feature Description:Perform BQRV4_BQR KOTAK_WL Successful Transactions Via CheckStatus Api with same amount and order ID.
    TC naming code description: 100: Payment Method, 102: BQR, 430: TC430
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL',
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
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'KOTAK_WL'"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        logger.debug(
            f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")
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

            amount = random.randint(226, 1000)
            logger.debug(f"Generating random amount : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the bqrGenerate : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)
            })
            APIProcessor.send_request(api_details)

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")
            rrn = response['rrNumber']
            logger.debug(f"Fetching rrn from the payment status api, rrn : {rrn}")
            auth_code = response['authCode']
            logger.debug(f"Fetching auth code from the payment status api, auth_code : {auth_code}")

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id)}' ORDER BY created_time DESC limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            bank_name = result['bank_name'].values[0]
            logger.debug(f"fetched bank name from txn table is : {bank_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org code from txn table is : {org_code_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth code from txn table is : {auth_code}")

            logger.info(f"Initiating transaction with same amount: {amount} and order id: {order_id} as previous "
                        f"transaction")
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details_2 = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response_2 = APIProcessor.send_request(api_details_2)
            logger.debug(f"response received for the bqrGenerate : {response_2}")
            success_2 = response_2['success']
            logger.debug(f"Fetching success value from the API_OUTPUT : {success_2}")
            error_message = response_2['errorMessage']
            logger.debug(f"Fetching message from the API_OUTPUT : {error_message}")
            error_code = response_2['errorCode']
            logger.debug(f"Fetching real code from the API_OUTPUT : {error_code}")
            # ----------------------------------------------------------------------------------------------------------
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
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": str(order_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info("Performing Login")
                login_page.perform_login(app_username, app_password)
                logger.info("Waiting for Home Page to load")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                order_id_app = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {order_id_app}")
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
                auth_code_app = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth code from txn history for the txn : {auth_code_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "auth_code": auth_code_app,
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": str(order_id),
                    "pmt_success_2": False,
                    "errorMessage": f"You have already made a similar payment for the same "
                                    f"Ref# {order_id} and amount {amount:.2f}. Please check"
                                    f" the status of the payment(s) made before you proceed.",
                    "errorCode": "EZETAP_0000033"
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = response["amount"]
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
                order_id_api = response["orderNumber"]

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
                    "order_id": str(order_id_api),
                    "pmt_success_2": success_2,
                    "errorMessage": error_message,
                    "errorCode": error_code
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
                    "bqr_txn_state": "SETTLED",
                    "bank_name": "Kotak Mahindra",
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "rrn": rrn,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_bank_code": "KOTAK",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id = '{str(txn_id)}';"
                logger.debug(f"Query to fetch txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                logger.info(f"Fetching status from txn table: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.info(f"Fetching amount from txn table: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.info(f"Fetching state from txn table: {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.info(f"Fetching bank code from txn table: {bank_code_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.info(f"Fetching bank name from txn table: {bank_name_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
                rrn_db = result["rr_number"].iloc[0]
                logger.info(f"Fetching rrn from txn table: {rrn_db}")
                txn_type_db = result["txn_type"].iloc[0]
                logger.info(f"Fetching txn type from txn table: {txn_type_db}")
                tid_db = result['tid'].values[0]
                logger.info(f"Fetching tid from txn table: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.info(f"Fetching mid from txn table: {mid_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["state"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_status_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_txn_type_db}")
                brq_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching details for the txn : {brq_bank_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "bqr_txn_state": bqr_status_db,
                    "bank_name": bank_name_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_bank_code": brq_bank_code_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db
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
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn)
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"fetched date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"fetched status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"fetched username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal
                }

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
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username,
                                                                   "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_431():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_CheckStatus_FDC_ICICI_Same_Amount_Same_Order_ID
    Sub Feature Description: Perform BQRV4_BQR FDC_ICICI Successful Transactions Via CheckStatus Api with same amount and order ID.
    TC naming code description: 100: Payment Method, 102: BQR, 431: TC431
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='FDC_ICICI',
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
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' " \
                f"AND bank_code = 'FDC_ICICI'"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        logger.debug(
            f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"f"{mid}, {tid}, "
            f"{terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")
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

            amount = random.randint(226, 1000)
            logger.debug(f"Generating random amount : {amount}")
            order_id = "1234"
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the bqrGenerate : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)
            })
            APIProcessor.send_request(api_details)

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")
            rrn = response['rrNumber']
            logger.debug(f"Fetching rrn from the payment status api, rrn : {rrn}")
            auth_code = response['authCode']
            logger.debug(f"Fetching auth code from the payment status api, auth_code : {auth_code}")

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id)}' ORDER BY created_time DESC limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            bank_name = result['bank_name'].values[0]
            logger.debug(f"fetched bank name from txn table is : {bank_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org code from txn table is : {org_code_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth code from txn table is : {auth_code}")

            logger.info(f"Initiating transaction with same amount: {amount} and order id: {order_id} as previous "
                        f"transaction")
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details_2 = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response_2 = APIProcessor.send_request(api_details_2)
            logger.debug(f"response received for the bqrGenerate : {response_2}")
            success_2 = response_2['success']
            logger.debug(f"Fetching success value from the API_OUTPUT: {success_2}")
            error_message = response_2['errorMessage']
            logger.debug(f"Fetching message from the API_OUTPUT : {error_message}")
            error_code = response_2['errorCode']
            logger.debug(f"Fetching real code from the API_OUTPUT : {error_code}")
            # ----------------------------------------------------------------------------------------------------------
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
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": str(order_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info("Performing Login")
                login_page.perform_login(app_username, app_password)

                logger.info("Waiting for Home Page to load")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                order_id_app = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {order_id_app}")
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
                auth_code_app = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth code from txn history for the txn : {auth_code_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "auth_code": auth_code_app,
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": str(order_id),
                    "pmt_success_2": False,
                    "errorMessage": f"You have already made a similar payment for the same "
                                    f"Ref# {order_id} and amount {amount:.2f}. Please check"
                                    f" the status of the payment(s) made before you proceed.",
                    "errorCode": "EZETAP_0000033"
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = response["amount"]
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
                order_id_api = response["orderNumber"]

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
                    "order_id": str(order_id_api),
                    "pmt_success_2": success_2,
                    "errorMessage": error_message,
                    "errorCode": error_code
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
                    "bqr_txn_state": "SETTLED",
                    "bank_name": "ICICI Bank",
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "FDC",
                    "rrn": rrn,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_bank_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id = '{str(txn_id)}';"
                logger.debug(f"Query to fetch txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                logger.info(f"Fetching status from txn table: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.info(f"Fetching amount from txn table: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.info(f"Fetching state from txn table: {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.info(f"Fetching bank code from txn table: {bank_code_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.info(f"Fetching bank name from txn table: {bank_name_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
                rrn_db = result["rr_number"].iloc[0]
                logger.info(f"Fetching rrn from txn table: {rrn_db}")
                txn_type_db = result["txn_type"].iloc[0]
                logger.info(f"Fetching txn type from txn table: {txn_type_db}")
                tid_db = result['tid'].values[0]
                logger.info(f"Fetching tid from txn table: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.info(f"Fetching mid from txn table: {mid_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["state"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_status_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching details for the txn : {bqr_txn_type_db}")
                brq_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching details for the txn : {brq_bank_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "bqr_txn_state": bqr_status_db,
                    "bank_name": bank_name_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_bank_code": brq_bank_code_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db
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
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn)
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"fetched date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"fetched status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"fetched username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal
                }

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
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username,
                                                                   "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
