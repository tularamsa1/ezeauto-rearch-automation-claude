import sys
import random
import time
import pytest
from datetime import datetime
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities.execution_log_processor import EzeAutoLogger
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, receipt_validator, date_time_converter

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_common_100_102_322():
    """
    Sub Feature Code: Tid Dep - UI_Common_BQRV4_QR_Generation_Success_YES_ATOS
    Sub Feature Description: Tid Dep -Verification of a success BQRV4 QR Generation via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 322: TC322
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

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

            amount = random.randint(401, 1000)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")
            status_api = response["status"]
            logger.debug(f"Value of status obtained from BQR generation response : {status_api}")
            amount_api = int(response["amount"])
            logger.debug(f"Value of amount obtained from BQR generation response : {amount_api}")
            payment_mode_api = response["paymentMode"]
            logger.debug(f"Value of paymentMode obtained from BQR generation response : {payment_mode_api}")
            state_api = response["states"][0]
            logger.debug(f"Value of states obtained from BQR generation response : {state_api}")
            settlement_status_api = response["settlementStatus"]
            logger.debug(f"Value of settlementStatus obtained from BQR generation response : {settlement_status_api}")
            issuer_code_api = response["issuerCode"]
            logger.debug(f"Value of issuerCode obtained from BQR generation response : {issuer_code_api}")
            acquirer_code_api = response["acquirerCode"]
            logger.debug(f"Value of acquirerCode obtained from BQR generation response : {acquirer_code_api}")
            org_code_api = response["orgCode"]
            logger.debug(f"Value of orgCode obtained from BQR generation response : {org_code_api}")
            mid_api = response["mid"]
            logger.debug(f"Value of mid obtained from BQR generation response : {mid_api}")
            tid_api = response["tid"]
            logger.debug(f"Value of tid obtained from BQR generation response : {tid_api}")
            txn_type_api = response["txnType"]
            logger.debug(f"Value of txnType obtained from BQR generation response : {txn_type_api}")
            date_api = response["createdTime"]
            logger.debug(f"Value of createdTime obtained from BQR generation response : {date_api}")
            device_serial_api = response["deviceSerial"]
            logger.debug(f"Value of deviceSerial obtained from BQR generation response : {device_serial_api}")
            order_id_api = response["orderNumber"]
            logger.debug(f"Value of orderNumber obtained from BQR generation response : {order_id_api}")
            qr_code_uri_api = response["qrCodeUri"]
            logger.debug(f"Value of qrCodeUri obtained from BQR generation response : {qr_code_uri_api}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_time}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Value of org_code obtained from txn table : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table : {txn_type}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")
            order_id_db = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table : {order_id_db}")

            query = "select * from bharatqr_txn where id='" + txn_id + "'"
            logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of bharatqr_txn table : {result}")
            qrcode_uri = result['qrcode_uri'].values[0]
            logger.debug(f"Value of qrcode_uri obtained from txn table : {qrcode_uri}")

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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "PENDING",
                    "txn_amt": amount,
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "PENDING",
                    "settle_status": "PENDING",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "qr_code_uri_api": str(qrcode_uri).__contains__(txn_id)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                if str(qr_code_uri_api).__contains__(txn_id):
                    qr_code_uri_msg = 'valid_qrCodeUri'
                else:
                    qr_code_uri_msg = 'invalid_qrCodeUri'

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
                    "device_serial": str(device_serial_api),
                    "qr_code_uri_api": str(qr_code_uri_api).__contains__(txn_id)
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": amount,
                    "settle_status": "PENDING",
                    "acquirer_code": "YES",
                    "bank_code": "YES",
                    "pmt_gateway": "ATOS",
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "bqr_pmt_state": "PENDING",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "YES"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table : {bqr_state_db}")
                bqr_txn_amt_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table : {bqr_txn_amt_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table : {bqr_org_code_db}")

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
                    "order_id": order_id_db,
                    "device_serial": str(device_serial_db),
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-----------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "PENDING",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else rrn,
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
def test_common_100_102_323():
    """
    Sub Feature Code: Tid Dep - UI_Common_BQRV4_QR_Generation_Failed_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a failed BQRV4 QR Generation via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 323: TC323
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select * from upi_merchant_config where bank_code = 'YES' AND status = 'ACTIVE' AND org_code = '" + str(org_code) + "'; "
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from the upi_merchant_config table : vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : upi_mc_id : {upi_mc_id}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

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

            amount = 111
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            message = response['message']
            logger.debug(f"Value of message obtained from BQR generation response : {message}")
            error_message = response['errorMessage']
            logger.debug(f"Value of errorMessage obtained from BQR generation response : {error_message}")
            real_code = response['realCode']
            logger.debug(f"Value of realCode obtained from BQR generation response : {real_code}")
            api_message = response['apiMessage']
            logger.debug(f"Value of apiMessage obtained from BQR generation response : {api_message}")

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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "message": "No transaction records found.",
                    "error_message": "No transaction records found.",
                    "real_code": "TXN_NO_RESULTS",
                    "api_message": "No transaction records found."
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "message": message,
                    "error_message": error_message,
                    "real_code": real_code,
                    "api_message": api_message
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)