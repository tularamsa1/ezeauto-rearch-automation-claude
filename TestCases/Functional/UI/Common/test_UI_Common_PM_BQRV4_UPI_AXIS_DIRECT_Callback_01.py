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
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    receipt_validator, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_168():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Success_using_UPI_Success_Callback_Via_AXISDIRECT
    Sub Feature Description: Performing a bqrv4 upi success callback via AXIS_DIRECT
    TC naming code description:
    100: Payment Method
    102: BQRV4
    168: TC168
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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)

            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(1, 49)
            order_id = datetime.now().strftime('%m%d%H%M%S')  # generate order id based on the current system time
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")

            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

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
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': rrn,
                                                                 'gatewayTransactionId': ref_id})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            print(type(data_buffer))
            # data_buffer = ast.literal_eval(data_buffer)
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id : {txn_id}")
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
                logger.debug(f"expected_app_values: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
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
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
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
                                                                  {"username": app_username,
                                                                   "password": app_password},
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
def test_common_100_102_169():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Failed_using_UPI_Failed_Callback_Via_AXISDIRECT
    Sub Feature Description: Performing a bqrv4 upi failed callback via AXIS_DIRECT
    TC naming code description:
    100: Payment Method
    102: BQRV4
    168: TC168
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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)

            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(1, 49)
            order_id = datetime.now().strftime('%m%d%H%M%S')  # generate order id based on the current system time
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")

            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

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
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_failed_curl',
                                                      curl_data={'merchantTransactionId': txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': rrn,
                                                                 'gatewayTransactionId': ref_id})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            print(type(data_buffer))
            # data_buffer = ast.literal_eval(data_buffer)
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id : {txn_id}")
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
                logger.debug(f"expected_app_values: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                payment_page.click_on_back_btn()
                home_page.click_on_back_btn_enter_amt_page()
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
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
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
def test_common_100_102_170():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_success_callback_after_qr_expiry_AutoRefund_Disabled_AXIS_DIRECT
    Sub Feature Description: Performing a pure bqrv4 upi success callback via AXIS_DIRECT after qr expiry when autorefund is disabled
    TC naming code description:
    100: Payment Method
    102: BQRV4
    170: TC170
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
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
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

            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(1, 49)
            order_id = datetime.now().strftime('%m%d%H%M%S')  # generate order id based on the current system time
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")

            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            logger.debug("waiting for the time till qr get expired...")
            time.sleep(60)

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
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            hdfc_mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {hdfc_mid}")
            hdfc_tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {hdfc_tid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            bqr_merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {bqr_merchant_config_id}")
            bqr_merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {bqr_merchant_pan}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
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

            rrn_2 = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn_2}")
            ref_id_2 = '211115084892E01' + str(rrn_2)
            logger.debug(f"generated random ref_id is : {ref_id_2}")

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn_2} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': rrn_2,
                                                                 'gatewayTransactionId': ref_id_2})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            print(type(data_buffer))
            # data_buffer = ast.literal_eval(data_buffer)
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_2 : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_2 : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_2 : {payer_name_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_2 : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_2 : {txn_type_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_2 : {auth_code_2}")
            txn_created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : txn_created_time_2 : {txn_created_time_2}")

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
                date_and_time_2 = date_time_converter.to_app_format(txn_created_time_2)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    # "auth_code_2": authid_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

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
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_2}, {payment_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_2}, {app_date_and_time_2}")
                # app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_2}, {app_auth_code_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_2}, {app_amount_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_2}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_2}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "customer_name_2": app_customer_name_2,
                    "settle_status_2": app_settlement_status_2,
                    "payer_name_2": app_payer_name_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    # "auth_code_2": app_auth_code_2,
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
                date = date_time_converter.db_datetime(created_time)
                date_2 = date_time_converter.db_datetime(txn_created_time_2)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "order_id": order_id,
                    "txn_type": "CHARGE", "mid": hdfc_mid, "tid": hdfc_tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "issuer_code_2": "AXIS",
                    "order_id_2": order_id,
                    "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    # "auth_code": authid_2,
                    "date_2": date_2,
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
                # rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                # auth_code_api = response["authCode"]
                date_api = response["createdTime"]
                order_id_api = response["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

                status_api_2 = response["status"]
                amount_api_2 = float(response["amount"])
                payment_mode_api_2 = response["paymentMode"]
                state_api_2 = response["states"][0]
                rrn_api_2 = response["rrNumber"]
                settlement_status_api_2 = response["settlementStatus"]
                issuer_code_api_2 = response["issuerCode"]
                acquirer_code_api_2 = response["acquirerCode"]
                orgCode_api_2 = response["orgCode"]
                mid_api_2 = response["mid"]
                tid_api_2 = response["tid"]
                txn_type_api_2 = response["txnType"]
                # auth_code_api_2 = response["authCode"]
                date_api_2 = response["createdTime"]
                order_id_api_2 = response["orderNumber"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "order_id": order_id_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": float(amount_api_2), "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "order_id_2": order_id_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    # "auth_code": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
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
                    "txn_amt": float(amount),
                    "settle_status": "FAILED",
                    "order_id": order_id,
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "mid": hdfc_mid,
                    "tid": hdfc_tid,
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "bqr_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_merchant_config_id, "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "rr_number_2": str(rrn_2),
                    # "auth_code_2": authid_2,
                    "txn_amt_2": float(amount),
                    "settle_status_2": "SETTLED",
                    "order_id_2": order_id,
                    "acquirer_code_2": "AXIS",
                    "bank_code_2": "AXIS",
                    "pmt_gateway_2": "AXIS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "upi_txn_status_2": "AUTHORIZED",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
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
                rr_number_db = result['rr_number'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result["status"].iloc[0]
                payment_mode_db_2 = result["payment_mode"].iloc[0]
                amount_db_2 = float(result["amount"].iloc[0])
                state_db_2 = result["state"].iloc[0]
                payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                bank_code_db_2 = result["bank_code"].iloc[0]
                settlement_status_db_2 = result["settlement_status"].iloc[0]
                tid_db_2 = result['tid'].values[0]
                mid_db_2 = result['mid'].values[0]
                order_id_db_2 = result['external_ref'].values[0]
                rr_number_db_2 = result['rr_number'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "order_id": order_id_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "rr_number_2": str(rr_number_db_2),
                    # "auth_code_2": auth_code_2,
                    "txn_amt_2": float(amount_db_2),
                    "settle_status_2": settlement_status_db_2,
                    "order_id_2": order_id_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time_2)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'time': txn_time,
                }
                receipt_validator.perform_charge_slip_validations(txn_id_2,
                                                                  {"username": app_username,
                                                                   "password": app_password},
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
def test_common_100_102_171():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_failed_callback_after_qr_expiry_AutoRefund_Disabled_AXIS_DIRECT
    Sub Feature Description: Performing a pure bqrv4 upi failed callback via AXIS_DIRECT after qr expiry when autorefund is disabled
    TC naming code description:
    100: Payment Method
    102: BQRV4
    171: TC171
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
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
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

            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(1, 49)
            order_id = datetime.now().strftime('%m%d%H%M%S')  # generate order id based on the current system time
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")

            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            logger.debug("waiting for the time till qr get expired...")
            time.sleep(60)

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
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            hdfc_mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {hdfc_mid}")
            hdfc_tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {hdfc_tid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            bqr_merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {bqr_merchant_config_id}")
            bqr_merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {bqr_merchant_pan}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
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

            rrn_2 = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn_2}")
            ref_id_2 = '211115084892E01' + str(rrn_2)
            logger.debug(f"generated random ref_id is : {ref_id_2}")

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn_2} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_failed_curl',
                                                      curl_data={'merchantTransactionId': txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': rrn_2,
                                                                 'gatewayTransactionId': ref_id_2})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            print(type(data_buffer))
            # data_buffer = ast.literal_eval(data_buffer)
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            # txn_id_2 = result['id'].values[0]
            # logger.debug(f"Fetching txn_id from the txn table : txn_id_2 : {txn_id_2}")
            # customer_name_2 = result['customer_name'].values[0]
            # logger.debug(f"Fetching customer_name from the txn table : customer_name_2 : {customer_name_2}")
            # payer_name_2 = result['payer_name'].values[0]
            # logger.debug(f"Fetching payer_name from the txn table : payer_name_2 : {payer_name_2}")
            # org_code_txn_2 = result['org_code'].values[0]
            # logger.debug(f"Fetching org_code from the txn table : org_code_2 : {org_code_txn_2}")
            # txn_type_2 = result['txn_type'].values[0]
            # logger.debug(f"Fetching txn_type from the txn table : txn_type_2 : {txn_type_2}")
            # auth_code_2 = result['auth_code'].values[0]
            # logger.debug(f"Fetching auth_code from the txn table : auth_code_2 : {auth_code_2}")
            # txn_created_time_2 = result['created_time'].values[0]
            # logger.debug(f"Fetching created_time from the txn table : txn_created_time_2 : {txn_created_time_2}")

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
                # date_and_time_2 = date_time_converter.to_app_format(txn_created_time_2)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    # "pmt_mode_2": "UPI",
                    # "pmt_status_2": "AUTHORIZED",
                    # "txn_amt_2": str(amount),
                    # "settle_status_2": "SETTLED",
                    # "txn_id_2": txn_id_2,
                    # "order_id_2": order_id,
                    # "payment_msg_2": "PAYMENT SUCCESSFUL",
                    # "date_2": date_and_time_2,
                    # # "auth_code_2": authid_2,
                    # "rrn_2": str(rrn_2),
                    # "customer_name_2": customer_name_2,
                    # "payer_name_2": payer_name_2,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

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
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                # txn_history_page.click_back_Btn_transaction_details()
                # txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                # payment_status_2 = txn_history_page.fetch_txn_status_text()
                # logger.info(f"Fetching status from txn history for the txn : {txn_id_2}, {payment_status_2}")
                # app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                # logger.info(f"Fetching date from txn history for the txn : {txn_id_2}, {app_date_and_time_2}")
                # # app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                # # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_2}, {app_auth_code_2}")
                # payment_mode_2 = txn_history_page.fetch_txn_type_text()
                # logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_2}, {payment_mode_2}")
                # app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                # logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_txn_id_2}")
                # app_amount_2 = txn_history_page.fetch_txn_amount_text()
                # logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_2}, {app_amount_2}")
                # app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
                # app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                # logger.info(
                #     f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                # app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                # app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                # logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
                # app_order_id_2 = txn_history_page.fetch_order_id_text()
                # logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_2}, {app_order_id_2}")
                # app_rrn_2 = txn_history_page.fetch_RRN_text()
                # logger.info(
                #     f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_2}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    # "pmt_mode_2": payment_mode_2,
                    # "pmt_status_2": payment_status_2.split(':')[1],
                    # "txn_amt_2": app_amount_2.split(' ')[1],
                    # "txn_id_2": app_txn_id_2,
                    # "rrn_2": str(app_rrn_2),
                    # "customer_name_2": app_customer_name_2,
                    # "settle_status_2": app_settlement_status_2,
                    # "payer_name_2": app_payer_name_2,
                    # "order_id_2": app_order_id_2,
                    # "payment_msg_2": app_payment_msg_2,
                    # # "auth_code_2": app_auth_code_2,
                    # "date_2": app_date_and_time_2
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
                # date_2 = date_time_converter.db_datetime(txn_created_time_2)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "order_id": order_id,
                    "txn_type": "CHARGE", "mid": hdfc_mid, "tid": hdfc_tid,
                    "org_code": org_code,
                    "date": date,
                    # "pmt_status_2": "AUTHORIZED",
                    # "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                    # "pmt_state_2": "SETTLED", "rrn_2": str(rrn_2),
                    # "settle_status_2": "SETTLED",
                    # "acquirer_code_2": "AXIS",
                    # "issuer_code_2": "AXIS",
                    # "order_id_2": order_id,
                    # "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                    # "org_code_2": org_code,
                    # # "auth_code": authid_2,
                    # "date_2": date_2,
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
                # rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                # auth_code_api = response["authCode"]
                date_api = response["createdTime"]
                order_id_api = response["orderNumber"]

                # api_details = DBProcessor.get_api_details('txnlist',
                #                                           request_body={"username": app_username,
                #                                                         "password": app_password})
                # logger.debug(f"API DETAILS for original txn : {api_details}")
                # response = APIProcessor.send_request(api_details)
                # logger.debug(f"Response received for transaction list api is : {response}")
                # response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                # logger.debug(f"Response after filtering data of current txn is : {response}")
                #
                # status_api_2 = response["status"]
                # amount_api_2 = float(response["amount"])
                # payment_mode_api_2 = response["paymentMode"]
                # state_api_2 = response["states"][0]
                # rrn_api_2 = response["rrNumber"]
                # settlement_status_api_2 = response["settlementStatus"]
                # issuer_code_api_2 = response["issuerCode"]
                # acquirer_code_api_2 = response["acquirerCode"]
                # orgCode_api_2 = response["orgCode"]
                # mid_api_2 = response["mid"]
                # tid_api_2 = response["tid"]
                # txn_type_api_2 = response["txnType"]
                # # auth_code_api_2 = response["authCode"]
                # date_api_2 = response["createdTime"]
                # order_id_api_2 = response["orderNumber"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "order_id": order_id_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    # "pmt_status_2": status_api_2,
                    # "txn_amt_2": float(amount_api_2), "pmt_mode_2": payment_mode_api_2,
                    # "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    # "settle_status_2": settlement_status_api_2,
                    # "acquirer_code_2": acquirer_code_api_2,
                    # "issuer_code_2": issuer_code_api_2,
                    # "order_id_2": order_id_api_2,
                    # "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    # "org_code_2": orgCode_api_2,
                    # # "auth_code": auth_code_api_2,
                    # "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
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
                    "txn_amt": float(amount),
                    "settle_status": "FAILED",
                    "order_id": order_id,
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "mid": hdfc_mid,
                    "tid": hdfc_tid,
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "bqr_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_merchant_config_id, "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    # "pmt_status_2": "AUTHORIZED",
                    # "pmt_state_2": "SETTLED",
                    # "pmt_mode_2": "UPI",
                    # "rr_number_2": str(rrn_2),
                    # # "auth_code_2": authid_2,
                    # "txn_amt_2": float(amount),
                    # "settle_status_2": "SETTLED",
                    # "order_id_2": order_id,
                    # "acquirer_code_2": "AXIS",
                    # "bank_code_2": "AXIS",
                    # "payment_gateway_2": "AXIS",
                    # "mid_2": mid,
                    # "tid_2": tid,
                    # "upi_txn_status_2": "AUTHORIZED",
                    # "upi_txn_type_2": "PAY_BQR",
                    # "upi_bank_code_2": "AXIS_DIRECT",
                    # "upi_mc_id_2": upi_mc_id,
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
                rr_number_db = result['rr_number'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                # query = "select * from txn where id='" + txn_id_2 + "'"
                # logger.debug(f"Query to fetch data from txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # status_db_2 = result["status"].iloc[0]
                # payment_mode_db_2 = result["payment_mode"].iloc[0]
                # amount_db_2 = float(result["amount"].iloc[0])
                # state_db_2 = result["state"].iloc[0]
                # payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                # acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                # bank_code_db_2 = result["bank_code"].iloc[0]
                # settlement_status_db_2 = result["settlement_status"].iloc[0]
                # tid_db_2 = result['tid'].values[0]
                # mid_db_2 = result['mid'].values[0]
                # order_id_db_2 = result['external_ref'].values[0]
                # rr_number_db_2 = result['rr_number'].values[0]

                # query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                # logger.debug(f"Query to fetch data from upi_txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # upi_status_db_2 = result["status"].iloc[0]
                # upi_txn_type_db_2 = result["txn_type"].iloc[0]
                # upi_bank_code_db_2 = result["bank_code"].iloc[0]
                # upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "order_id": order_id_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    # "pmt_status_2": status_db_2,
                    # "pmt_state_2": state_db_2,
                    # "pmt_mode_2": payment_mode_db_2,
                    # "rr_number_2": str(rr_number_db_2),
                    # # "auth_code_2": auth_code_2,
                    # "txn_amt_2": float(amount_db_2),
                    # "settle_status_2": settlement_status_db_2,
                    # "order_id_2": order_id_db_2,
                    # "acquirer_code_2": acquirer_code_db_2,
                    # "bank_code_2": bank_code_db_2,
                    # "payment_gateway_2": payment_gateway_db_2,
                    # "mid_2": mid_db_2,
                    # "tid_2": tid_db_2,
                    # "upi_txn_status_2": upi_status_db_2,
                    # "upi_txn_type_2": upi_txn_type_db_2,
                    # "upi_bank_code_2": upi_bank_code_db_2,
                    # "upi_mc_id_2": upi_mc_id_db_2,
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
@pytest.mark.chargeSlipVal
def test_common_100_102_172():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_success_callback_after_qr_expiry_AutoRefund_Enabled_AXIS_DIRECT
    Sub Feature Description: Performing a pure bqrv4 upi success callback via AXIS_DIRECT after qr expiry when autorefund is enabled
    TC naming code description:
    100: Payment Method
    102: BQRV4
    172: TC172
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
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
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

            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(1, 49)
            order_id = datetime.now().strftime('%m%d%H%M%S')  # generate order id based on the current system time
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")

            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            logger.debug("waiting for the time till qr get expired...")
            time.sleep(60)

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
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            hdfc_mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {hdfc_mid}")
            hdfc_tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {hdfc_tid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            bqr_merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {bqr_merchant_config_id}")
            bqr_merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {bqr_merchant_pan}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
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

            rrn_2 = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn_2}")
            ref_id_2 = '211115084892E01' + str(rrn_2)
            logger.debug(f"generated random ref_id is : {ref_id_2}")

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn_2} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': rrn_2,
                                                                 'gatewayTransactionId': ref_id_2})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            print(type(data_buffer))
            # data_buffer = ast.literal_eval(data_buffer)
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_2 : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_2 : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_2 : {payer_name_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_2 : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_2 : {txn_type_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_2 : {auth_code_2}")
            txn_created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : txn_created_time_2 : {txn_created_time_2}")

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
                date_and_time_2 = date_time_converter.to_app_format(txn_created_time_2)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    # "auth_code_2": authid_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

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
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_2}, {payment_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_2}, {app_date_and_time_2}")
                # app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_2}, {app_auth_code_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_2}, {app_amount_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_2}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_2}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "customer_name_2": app_customer_name_2,
                    "settle_status_2": app_settlement_status_2,
                    "payer_name_2": app_payer_name_2,
                    "order_id_2": app_order_id_2,
                    "payment_msg_2": app_payment_msg_2,
                    # "auth_code_2": app_auth_code_2,
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
                date = date_time_converter.db_datetime(created_time)
                date_2 = date_time_converter.db_datetime(txn_created_time_2)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "order_id": order_id,
                    "txn_type": "CHARGE", "mid": hdfc_mid, "tid": hdfc_tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUND_PENDING", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "issuer_code_2": "AXIS",
                    "order_id_2": order_id,
                    "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    # "auth_code": authid_2,
                    "date_2": date_2,
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
                # rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                # auth_code_api = response["authCode"]
                date_api = response["createdTime"]
                order_id_api = response["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

                status_api_2 = response["status"]
                amount_api_2 = float(response["amount"])
                payment_mode_api_2 = response["paymentMode"]
                state_api_2 = response["states"][0]
                rrn_api_2 = response["rrNumber"]
                settlement_status_api_2 = response["settlementStatus"]
                issuer_code_api_2 = response["issuerCode"]
                acquirer_code_api_2 = response["acquirerCode"]
                orgCode_api_2 = response["orgCode"]
                mid_api_2 = response["mid"]
                tid_api_2 = response["tid"]
                txn_type_api_2 = response["txnType"]
                # auth_code_api_2 = response["authCode"]
                date_api_2 = response["createdTime"]
                order_id_api_2 = response["orderNumber"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "order_id": order_id_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": float(amount_api_2), "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "order_id_2": order_id_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    # "auth_code": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
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
                    "txn_amt": float(amount),
                    "settle_status": "FAILED",
                    "order_id": order_id,
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "mid": hdfc_mid,
                    "tid": hdfc_tid,
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "bqr_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_merchant_config_id, "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "REFUND_PENDING",
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_mode_2": "UPI",
                    "rr_number_2": str(rrn_2),
                    # "auth_code_2": authid_2,
                    "txn_amt_2": float(amount),
                    "settle_status_2": "SETTLED",
                    "order_id_2": order_id,
                    "acquirer_code_2": "AXIS",
                    "bank_code_2": "AXIS",
                    "payment_gateway_2": "AXIS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "upi_txn_status_2": "REFUND_PENDING",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
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
                rr_number_db = result['rr_number'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result["status"].iloc[0]
                payment_mode_db_2 = result["payment_mode"].iloc[0]
                amount_db_2 = float(result["amount"].iloc[0])
                state_db_2 = result["state"].iloc[0]
                payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                bank_code_db_2 = result["bank_code"].iloc[0]
                settlement_status_db_2 = result["settlement_status"].iloc[0]
                tid_db_2 = result['tid'].values[0]
                mid_db_2 = result['mid'].values[0]
                order_id_db_2 = result['external_ref'].values[0]
                rr_number_db_2 = result['rr_number'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "order_id": order_id_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "rr_number_2": str(rr_number_db_2),
                    # "auth_code_2": auth_code_2,
                    "txn_amt_2": float(amount_db_2),
                    "settle_status_2": settlement_status_db_2,
                    "order_id_2": order_id_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "payment_gateway_2": payment_gateway_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
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
@pytest.mark.chargeSlipVal
def test_common_100_101_056():
    """
    Sub Feature Code: UI_Common_PM_UPI_failed_callback_after_qr_expiry_AutoRefund_Enabled_AXIS_DIRECT
    Sub Feature Description: Performing a pure upi failed callback via AXIS_DIRECT after qr expiry when autorefund is enabled.
    TC naming code description:
    100: Payment Method
    101: UPI
    056: TC056
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
        org_code = result['org_ChargeSlipcode'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)

            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(1, 49)
            order_id = datetime.now().strftime('%m%d%H%M%S')  # generate order id based on the current system time
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")

            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            logger.info("resetting the com.ezetap.basicapp")
            app_driver.reset()
            logger.info("waiting for the time till qr get expired...")
            time.sleep(62)

            query = "select * from upi_merchant_config where bank_code = 'AXIS_DIRECT' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, txn_id : {original_txn_id}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': original_txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': rrn,
                                                                 'gatewayTransactionId': ref_id})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            print(type(data_buffer))
            # data_buffer = ast.literal_eval(data_buffer)
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            status = result['status'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            settlement_status = result['settlement_status'].values[0]
            acquirer_code = result['acquirer_code'].values[0]
            issuer_code = result['issuer_code'].values[0]
            org_code_txn = result['org_code'].values[0]
            txn_type = result['txn_type'].values[0]

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(original_txn_id) + "';"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            new_txn_customer_name = result['customer_name'].values[0]
            new_txn_payer_name = result['payer_name'].values[0]
            new_txn_org_code = result['org_code'].values[0]
            new_txn_type = result['txn_type'].values[0]
            new_external_ref = result['external_ref'].values[0]

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                expected_app_values = {
                    "payment_mode": "UPI",
                    "payment_status": "EXPIRED",
                    "txn_amount": str(amount),
                    "settlement_status": "FAILED",
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "new_txn_payment_mode": "UPI",
                    "new_txn_payment_status": "REFUND_PENDING",
                    "new_txn_amount": str(amount),
                    "new_txn_settlement_status": "SETTLED",
                    "new_txn_id": new_txn_id,
                    "new_txn_customer_name": new_txn_customer_name,
                    "new_txn_payer_name": new_txn_payer_name,
                    "new_txn_order_id": new_external_ref,
                    "new_txn_payment_msg": "PAYMENT SUCCESSFUL",
                    "new_txn_rrn": str(rrn)
                }

                logger.debug(f"expected_app_values: {expected_app_values}")
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(original_txn_id)

                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id)

                new_app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {new_txn_id}, {new_app_payment_status}")
                new_app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id}, {new_app_payment_mode}")
                new_app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_txn_id}")
                new_app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id}, {new_app_amount}")
                new_app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_rrn}")
                new_app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id}, {new_app_customer_name}")
                new_app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id}, {new_app_settlement_status}")
                new_app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id}, {new_app_payer_name}")
                new_app_payment_status = new_app_payment_status.split(':')[1]
                new_app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {new_txn_id}, {new_app_order_id}")
                new_app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id}, {new_app_payment_msg}")

                actual_app_values = {
                    "payment_mode": "UPI",
                    "payment_status": app_payment_status,
                    "txn_amount": app_amount.split(' ')[1],
                    "settlement_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "new_txn_payment_mode": new_app_payment_mode,
                    "new_txn_payment_status": new_app_payment_status,
                    "new_txn_amount": str(new_app_amount).split(' ')[1],
                    "new_txn_settlement_status": new_app_settlement_status,
                    "new_txn_id": new_app_txn_id,
                    "new_txn_customer_name": new_app_customer_name,
                    "new_txn_payer_name": new_app_payer_name,
                    "new_txn_order_id": new_app_order_id,
                    "new_txn_payment_msg": new_app_payment_msg,
                    "new_txn_rrn": str(new_app_rrn)
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {"pmt_status": "EXPIRED",
                                       "txn_amt": amount, "pmt_mode": "UPI",
                                       "pmt_state": "EXPIRED",
                                       "settlement_status": "FAILED",
                                       "acquirer_code": "AXIS",
                                       "issuer_code": "AXIS",
                                       "txn_type": txn_type, "mid": mid, "tid": tid, "org_code": org_code_txn,
                                       "new_pmt_status": "REFUND_PENDING",
                                       "new_txn_amt": amount, "new_pmt_mode": "UPI",
                                       "new_pmt_state": "REFUND_PENDING",
                                       # "new_rrn": str(rrn),
                                       "new_settlement_status": "SETTLED",
                                       "new_acquirer_code": "AXIS",
                                       "new_issuer_code": "AXIS",
                                       "new_txn_type": new_txn_type, "new_mid": mid,
                                       "new_tid": tid, "new_org_code": org_code_txn
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": new_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                new_txn_status_api = response["status"]
                new_txn_amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                new_payment_mode_api = response["paymentMode"]
                new_txn_state_api = response["states"][0]
                # new_txn_rrn_api = response["rrNumber"]
                new_txn_settlement_status_api = response["settlementStatus"]
                new_txn_issuer_code_api = response["issuerCode"]
                new_txn_acquirer_code_api = response["acquirerCode"]
                new_txn_orgCode_api = response["orgCode"]
                new_txn_mid_api = response["mid"]
                new_txn_tid_api = response["tid"]
                new_txn_txn_type_api = response["txnType"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settlement_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api, "org_code": orgCode_api,
                                     "new_pmt_status": new_txn_status_api,
                                     "new_txn_amt": new_txn_amount_api, "new_pmt_mode": new_payment_mode_api,
                                     "new_pmt_state": new_txn_state_api,
                                     # "new_rrn": str(new_txn_rrn_api),
                                     "new_settlement_status": new_txn_settlement_status_api,
                                     "new_acquirer_code": new_txn_acquirer_code_api,
                                     "new_issuer_code": new_txn_issuer_code_api,
                                     "new_txn_type": new_txn_txn_type_api, "new_mid": new_txn_mid_api,
                                     "new_tid": new_txn_tid_api, "new_org_code": new_txn_orgCode_api
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
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
                    "settlement_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "payment_gateway": "AXIS",
                    "upi_txn_type_db": "PAY_QR",
                    "upi_bank_code_db": "AXIS_DIRECT",
                    "upi_mc_id_db": upi_mc_id,
                    "new_pmt_status": "REFUND_PENDING",
                    "new_pmt_state": "REFUND_PENDING",
                    "new_pmt_mode": "UPI",
                    "new_txn_amt": amount,
                    "new_upi_txn_status": "REFUND_PENDING",
                    "new_settlement_status": "SETTLED",
                    "new_acquirer_code": "AXIS",
                    "new_bank_code": "AXIS",
                    "new_payment_gateway": "AXIS",
                    "new_upi_txn_type_db": "PAY_QR",
                    "new_upi_bank_code_db": "AXIS_DIRECT",
                    "new_upi_mc_id_db": upi_mc_id,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + original_txn_id + "'"
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

                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db = result["status"].iloc[0]
                new_txn_payment_mode_db = result["payment_mode"].iloc[0]
                new_txn_amount_db = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db = result["state"].iloc[0]
                new_txn_payment_gateway_db = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db = result["bank_code"].iloc[0]
                new_txn_settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db = result["status"].iloc[0]
                new_txn_upi_txn_type_db = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settlement_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type_db": upi_txn_type_db,
                    "upi_bank_code_db": upi_bank_code_db,
                    "upi_mc_id_db": upi_mc_id_db,
                    "new_pmt_status": new_txn_upi_status_db,
                    "new_pmt_state": new_txn_state_db,
                    "new_pmt_mode": new_txn_payment_mode_db,
                    "new_txn_amt": new_txn_amount_db,
                    "new_upi_txn_status": new_txn_upi_status_db,
                    "new_settlement_status": new_txn_settlement_status_db,
                    "new_acquirer_code": new_txn_acquirer_code_db,
                    "new_bank_code": new_txn_bank_code_db,
                    "new_payment_gateway": new_txn_payment_gateway_db,
                    "new_upi_txn_type_db": new_txn_upi_txn_type_db,
                    "new_upi_bank_code_db": new_txn_upi_bank_code_db,
                    "new_upi_mc_id_db": new_txn_upi_mc_id_db,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {"Payment State": "Settled", "Payment Type": "UPI",
                                          "Amount": "Rs." + str(amount) + ".00", "Username": app_username}
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.search_merchant_name(str(org_code))
                home_page_portal.wait_for_home_page_load()

                logger.debug(f"searching for the org_code : {str(org_code)}")
                home_page_portal.click_switch_button(str(org_code))
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(original_txn_id)
                portal_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amount = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                actual_portal_values = {"Payment State": str(portal_status), "Payment Type": portal_type,
                                        "Amount": portal_amount, "Username": portal_username}
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")

        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': date}
                logger.debug(f"expected_values : {expected_values}")
                receipt_validator.perform_charge_slip_validations(new_txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_values)

            except Exception as e:
                ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_chargeslip_val_result = "Fail"
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)
