import random
import sys
import time
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
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
def test_common_100_101_301():
    """
    Sub Feature Code: UI_Common_PM_UPI_ICICI_Direct_CheckStatus_Success_Txn
    Sub Feature Description: Generate QR and perform checkstatus through api for UPI success txn of ICICI_Direct pg
    TC naming code description: 100: Payment Method, 101: UPI, 301: TC301
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from org_employee table: {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'ICICI_DIRECT';"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Value of pg_merchant_id from upi_merchant_config table: {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Value of vpa from upi_merchant_config table: {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table: {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(501, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from upi qr generation api : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the upi qr generation api: {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from stop payment api : {response}")

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")
            rrn = response['rrNumber']
            logger.debug(f"Fetching rrn from the payment status api, rrn : {rrn}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table is : {payer_name}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table is : {auth_code}")
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
            payer_name_db = result["payer_name"].iloc[0]
            logger.info(f"Fetching payer name from txn table: {payer_name_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            rrn_db = result["rr_number"].iloc[0]
            logger.info(f"Fetching rrn from txn table: {rrn_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].iloc[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].iloc[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_msg_db = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
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
                logger.info("clicking on history")
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("selecting txn by txn id")
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

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "date": date_and_time_app
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation-----------------------------------------

        # -----------------------------------------Start of API Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": order_id,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api response")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response")

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
                    "order_id": order_id_api,
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "payer_name": payer_name,
                    "bank_name": "ICICI Bank",
                    "error_msg": "None",
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "rrn": rrn,
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status from the upi_txn table: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type from the upi_txn table: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code from the upi_txn table: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from the upi_txn table: {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "payer_name": payer_name_db,
                    "bank_name": bank_name_db,
                    "error_msg": error_msg_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
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
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn)
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetching auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"fetching username from portal {username_portal}")

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

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
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
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id, {"username": app_username,
                                                                "password": app_password}, expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_common_100_101_302():
    """
    Sub Feature Code: UI_Common_PM_UPI_ICICI_Direct_Checkstatus_Failed_Txn
    Sub Feature Description: Generate QR and perform checkstatus through api for failed UPI txn of ICICI_Direct pg
    TC naming code description: 100: Payment Method, 101: UPI, 302: TC302
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'ICICI_DIRECT';"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Value of pg_merchant_id from upi_merchant_config table: {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Value of vpa from upi_merchant_config table: {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table: {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)--------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(101, 200)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upi qr generation api : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the upi qr generate api, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from stop payment api: {response}")

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")
            rrn = response['rrNumber']
            logger.debug(f"Fetching rrn from the payment status, rrn : {rrn}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer name from txn table is : {payer_name}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table is : {auth_code}")
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
            bank_name_db = result["bank_name"].iloc[0]
            logger.info(f"Fetching bank name from txn table: {bank_name_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.info(f"Fetching bank code from txn table: {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            rrn_db = result["rr_number"].iloc[0]
            logger.info(f"Fetching rrn from txn table: {rrn_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].iloc[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].iloc[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_msg_db = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "settle_status": "FAILED",
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
                logger.info("clicking on history")
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("selecting txn by txn id")
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

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
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
                date_and_time_api = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "rrn": rrn,
                    "settle_status": "FAILED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": order_id,
                    "date": date_and_time_api
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api response")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response")

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
                    "order_id": order_id_api,
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
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "FAILED",
                    "error_msg": "None",
                    "bank_name": "ICICI Bank",
                    "settle_status": "FAILED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "rrn": rrn,
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status from the upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type from the upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code from the upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from the upi_txn table : {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "error_msg": error_msg_db,
                    "bank_name": bank_name_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
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
                    "pmt_state": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn)
                }

                logger.debug(f"expected portal values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"Fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal {username_portal}")

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

                logger.debug(f"actual portal values: {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
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
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_101_303():
    """
    Sub Feature Code: UI_Common_PM_UPI_CheckStatus_API_ICICI_DIRECT_Cancel_Txn
    Sub Feature Description: Generate QR and performing cancel transaction through checkstatus api for ICICI Direct pg.
    TC naming code description: 100: Payment Method, 101: UPI, 303: TC303
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'ICICI_DIRECT';"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Value of pg_merchant_id from upi_merchant_config table: {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Value of vpa from upi_merchant_config table: {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table: {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upi qr generate api: {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the upi qr generation api, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for stop payment api is : {response}")

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table is : {payer_name}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table is : {auth_code}")
            created_by = result['created_by'].values[0]
            logger.debug(f"Fetching name from txn table is : {created_by}")
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
            payer_name_db = result["payer_name"].iloc[0]
            logger.info(f"Fetching payer name from txn table: {payer_name_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].iloc[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].iloc[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_code_db = result['error_code'].iloc[0]
            logger.info(f"Fetching error code from txn table: {error_code_db}")
            error_message_db = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_message_db}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "settle_status": "FAILED",
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
                logger.info("clicking on history")
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("selecting txn by txn id")
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
                date_and_time_app = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {date_and_time_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "date": date_and_time_app
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": order_id,
                    "date": date_and_time
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response")

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
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "error_code": "EZETAP_0000702",
                    "error_message": f"Transaction cancelled by : {created_by}",
                    "upi_txn_status": "EXPIRED",
                    "bank_name": "ICICI Bank",
                    "settle_status": "FAILED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status from the upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type from the upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code from the upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from the upi_txn table : {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "error_code": error_code_db,
                    "error_message": error_message_db,
                    "upi_txn_status": upi_status_db,
                    "bank_name": bank_name_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
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
                    "pmt_state": "EXPIRED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"Fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
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
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_common_100_101_304():
    """
    Sub Feature Code: UI_Common_PM_UPI_ICICI_DIRECT_CheckStatus_Pending_Txn
    Sub Feature Description: Generate QR and perform checkstatus through api for UPI Pending Txn of ICICI Direct pg
    TC naming code description: 100: Payment Method, 101: UPI, 304: TC304
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'ICICI_DIRECT';"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Value of pg_merchant_id from upi_merchant_config table: {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Value of vpa from upi_merchant_config table: {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table: {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------------Start of Test Execution----------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upi qr generate api: {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the upi qr generate api, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for payment status api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table is : {payer_name}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table is : {auth_code}")
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
            payer_name_db = result["payer_name"].iloc[0]
            logger.info(f"Fetching payer name from txn table: {payer_name_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].iloc[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].iloc[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_msg_db = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "PENDING",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT PENDING",
                    "settle_status": "PENDING",
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
                logger.info("clicking on history")
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("selecting txn by txn id")
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
                date_and_time_app = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {date_and_time_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "date": date_and_time_app
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation-------------------------------------------

        # -----------------------------------------Start of API Validation-----------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "PENDING",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "PENDING",
                    "settle_status": "PENDING",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": order_id,
                    "date": date_and_time
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response")

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
                    "pmt_status": "PENDING",
                    "pmt_state": "PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "PENDING",
                    "error_msg": "None",
                    "settle_status": "PENDING",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status from the upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type from the upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code from the upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from the upi_txn table : {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "error_msg": error_msg_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
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
                    "pmt_state": "PENDING",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"Fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal
                }

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
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
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_common_100_101_307():
    """
    Sub Feature Code: UI_Common_PM_UPI_ICICI_DIRECT_QR_Expiry_Through_App
    Sub Feature Description: Generate QR through app and perform UPI txn via checkstatus after qr expiry ICICI_Direct pg
    TC naming code description: 100: Payment Method, 101: UPI, 307: TC307
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'ICICI_DIRECT';"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Value of pg_merchant_id from upi_merchant_config table: {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Value of vpa from upi_merchant_config table: {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table: {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received from preconditions for UPI QR Expiry : {response}")

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)----------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info("Performing Login")
            login_page.perform_login(app_username, app_password)
            logger.info("Waiting for Home Page to load")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.check_home_page_logo()
            home_page.wait_for_home_page_load()
            logger.info(f"Entering amount and proceeding with order id")
            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            logger.info(f"Checking the amount and order id displayed is same as entered")
            payment_page.is_payment_page_displayed(amount, order_id)
            logger.info("Selecting payment mode as UPI")
            payment_page.click_on_Upi_paymentMode()
            logger.info("Generating Payment QR and validating it")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info(f"Waiting for qr to get expired")
            time.sleep(60)
            logger.info("Terminating the com.ezetap.basicapp and activating again the com.ezetap.basicapp")
            app_driver.reset()
            login_page.perform_login(app_username, app_password)
            logger.info("Waiting for Home Page to load")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.check_home_page_logo()
            home_page.wait_for_home_page_load()

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch data from the txn table: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table is : {payer_name}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table is : {auth_code}")
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
            payer_name_db = result["payer_name"].iloc[0]
            logger.info(f"Fetching payer name from txn table: {payer_name_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].iloc[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].iloc[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_msg_db = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "settle_status": "FAILED",
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                logger.info("Clicking on history")
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("Selecting txn by txn id")
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
                date_and_time_app = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {date_and_time_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "date": date_and_time_app
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": order_id,
                    "date": date_and_time
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response")

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
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "EXPIRED",
                    "bank_name": "ICICI Bank",
                    "error_msg": "None",
                    "settle_status": "FAILED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status from the upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type from the upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code from the upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from the upi_txn table : {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "bank_name": bank_name_db,
                    "error_msg": error_msg_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db,
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation--------------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal {auth_code_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"Fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal
                }

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
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