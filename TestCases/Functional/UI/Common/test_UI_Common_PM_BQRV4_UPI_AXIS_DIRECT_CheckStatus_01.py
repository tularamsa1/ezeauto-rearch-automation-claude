import random
import shutil
import sys
import time
from datetime import datetime

import pytest
from termcolor import colored

from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_165():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Success_Via_CheckStatus_API_AXISDIRECT
    Sub Feature Description: Initiate qr by api and perform checkStatus by api for success using magic number for AXIS_DIRECT
    TC naming code description:
    100: Payment Method
    102: BQRV4
    165: TC165
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating bharatqr_merchant_config table inactive: {result}")
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(201, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for bqrGenerate api is : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)
            })
            APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stopPayment api is : {response}")

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stopPayment api is : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table : rrn : {rrn}")
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

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Fetching id from the upi_merchant_config table : id : {upi_mc_id}")
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the upi_merchant_config table : mid : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the upi_merchant_config table : tid : {tid}")

            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
            merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

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
                    "txn_amt": str(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    # "auth_code": auth_code,
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                logger.debug("Homepage of MPOSX app loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                # app_auth_code = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
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
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

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
                    # "auth_code": app_auth_code,
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
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    # "auth_code": auth_code,
                    "date": date,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        # auth_code_api = elements["authCode"]
                        date_api = elements["createdTime"]
                        customer_name_api = elements["customerName"]
                        payer_name_api = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    # "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
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
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "AXIS",
                    "upi_txn_type": "PAY_BQR",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    # "bqr_pmt_status_code": "SUCCESS",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    # "bqr_merchant_pan": merchant_pan,
                    # "bqr_rrn": rrn,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "HDFC",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
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

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
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

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    # "bqr_pmt_status_code": bqr_status_code_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    # "bqr_merchant_pan": bqr_merchant_pan_db,
                    # "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
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
                expected_portal_values = {}

                actual_portal_values = {}

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
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'time': txn_time,
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
def test_common_100_102_218():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Failed_Via_CheckStatus_API_AXISDIRECT
    Sub Feature Description: Initiate bqrv4 upi qr by api and perform checkStatus by api for failed using magic number for AXIS_DIRECT
    TC naming code description:
    100: Payment Method
    102: BQRV4
    218: TC218
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating bharatqr_merchant_config table inactive: {result}")
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC'"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active : {result}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 49.70
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for bqrGenerate api is : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)
            })
            APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stopPayment api is : {response}")

            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username, "password": app_password, "txnId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stopPayment api is : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table : rrn : {rrn}")
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

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Fetching id from the upi_merchant_config table : id : {upi_mc_id}")
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the upi_merchant_config table : mid : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the upi_merchant_config table : tid : {tid}")

            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
            merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

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
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    # "auth_code": auth_code,
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                logger.debug("Homepage of MPOSX app loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                # app_auth_code = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
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
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

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
                    # "auth_code": app_auth_code,
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
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "FAILED", "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    # "auth_code": auth_code,
                    "date": date,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = (elements["amount"])  # actual=345.00, expected should be in the same format
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        # auth_code_api = elements["authCode"]
                        date_api = elements["createdTime"]
                        customer_name_api = elements["customerName"]
                        payer_name_api = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    # "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
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
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "AXIS",
                    "upi_txn_type": "PAY_BQR",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    # "bqr_pmt_status_code": "SUCCESS",
                    "bqr_pmt_state": "FAILED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    # "bqr_merchant_pan": merchant_pan,
                    # "bqr_rrn": rrn,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "HDFC",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = (result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
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

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    # "bqr_pmt_status_code": bqr_status_code_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    # "bqr_merchant_pan": bqr_merchant_pan_db,
                    # "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
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
                expected_portal_values = {}

                actual_portal_values = {}

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
def test_common_100_102_220():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Check_Status_via_API_After_Expiry_AXIS_DIRECT
    Sub Feature Description: Verification of a bqrv4 upi txn after expiry for AXIS_DIRECT using check status api
    TC naming code description:
    100: Payment Method
    101: UPI
    220: TC220
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating bharatqr_merchant_config table inactive: {result}")
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC'"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active : {result}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

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
            amount = random.choice([i for i in range(1, 100) if i not in [45, 46]])
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
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            app_driver.reset()
            logger.info("waiting for the time till qr get expired...")
            time.sleep(60)

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            api_details = DBProcessor.get_api_details('stopPayment',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "orgCode": org_code, "txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stopPayment api of transaction is : {response}")
            api_details = DBProcessor.get_api_details('paymentStatus',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for checkstatus of transaction is : {response}")
            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table : rrn : {rrn}")
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

            query = "select id from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Fetching id from the upi_merchant_config table : id : {upi_mc_id}")

            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
            merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

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
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                logger.info("Restarting MPOS-X app to perform validation of the transaction")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                logger.debug("Homepage of MPOSX app loaded successfully")
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

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
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
                    "pmt_status": "EXPIRED",
                    "txn_amt": amount, "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        date_api = elements["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": amount,
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_merchant_pan": merchant_pan,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "HDFC",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
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

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db = result["state"].iloc[0]
                bqr_txn_amt_db = result["txn_amount"].iloc[0]
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result["org_code"].iloc[0]

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
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
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
                expected_portal_values = {}

                actual_portal_values = {}

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
def test_common_100_102_222():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_AXIS_DIRECT_Amount_Mismatch_Upon_Check_Status
    Sub Feature Description: Verification of  check status for amount mismatch via Axis acq and Axis PG where bqrv4 upi config is Axis_Direct
    100: Payment Method
    102: BQRV4
    222: TC222
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating bharatqr_merchant_config table inactive: {result}")
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC'"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active : {result}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = 260
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            logger.info("waiting for the time till QR gets expired")
            time.sleep(65)

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching Txn_id from data base : Txn_id : {txn_id}")
            org_code_txn = result['org_code'].values[0]
            txn_type = result['txn_type'].values[0]
            created_time = result['created_time'].values[0]

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            tid = result['tid'].values[0]
            mid = result['mid'].values[0]

            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
            merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

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
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                logger.info(f"App homepage loaded successfully")
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

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
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
                    "txn_amt": amount, "pmt_mode": "BHARATQR",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        created_time_api = elements["createdTime"]
                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(created_time_api)
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": amount,
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_state": "FAILED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_merchant_pan": merchant_pan,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "HDFC",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
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

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db = result["state"].iloc[0]
                bqr_txn_amt_db = result["txn_amount"].iloc[0]
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result["org_code"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
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
