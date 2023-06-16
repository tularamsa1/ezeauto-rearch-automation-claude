import random
import sys
import time
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter, receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_101_102():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_Success_Callback_After_QR_Expiry_AutoRefund_Enabled_HDFC
    Sub Feature Description: Tid Dep - Performing a pure upi success callback via HDFC Tid Dep after qr expiry when autorefund is enabled.
    TC naming code description: 100: Payment Method, 101: UPI, 102: TC102
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
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='UPI' and payment_gateway='HDFC';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")
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
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            tid = result['tid'].values[0]
            mid = result['mid'].values[0]
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
            logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            device_serial = result['device_serial'].values[0]
            logger.info(f"fetched device_serial is : {device_serial}")
            amount = random.randint(51, 100)
            if amount == 55:
                amount = 56
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepUpiQRGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            original_txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {original_txn_id}")

            logger.info("waiting for the time till qr get expired...")
            time.sleep(63)

            query = "select * from txn where id = '" + str(original_txn_id) + "'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_rrn = result['rr_number'].values[0]
            original_txn_id = original_txn_id
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {original_txn_id} and {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            original_payer_name = result['payer_name'].values[0]
            original_org_code_txn = result['org_code'].values[0]
            original_txn_type = result['txn_type'].values[0]
            original_posting_date = result['posting_date'].values[0]

            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': ref_id, 'Txn_id': original_txn_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            new_customer_name = result['customer_name'].values[0]
            new_payer_name = result['payer_name'].values[0]
            new_org_code_txn = result['org_code'].values[0]
            new_txn_type = result['txn_type'].values[0]
            new_auth_code = result['auth_code'].values[0]
            new_modified_date = result['modified_time'].values[0]

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
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                new_date_and_time = date_time_converter.to_app_format(new_modified_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    "rrn": str(original_rrn),
                    "customer_name": original_customer_name,
                    "payer_name": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    # "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id,
                    "rrn_2": str(rrn),
                    "customer_name_2": new_customer_name,
                    "payer_name_2": new_payer_name,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": new_auth_code,
                    "date_2": new_date_and_time
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
                txn_history_page.click_on_transaction_by_txn_id(original_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                # app_auth_code = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {original_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id)
                new_app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {new_txn_id}, {new_app_payment_status}")
                new_app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id}, {new_app_date_and_time}")
                new_app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {new_txn_id}, {new_app_auth_code}")
                new_app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {new_txn_id}, {new_app_payment_mode}")
                new_app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_txn_id}")
                new_app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id}, {new_app_amount}")
                new_app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {new_txn_id}, {new_app_customer_name}")
                new_app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id}, {new_app_settlement_status}")
                new_app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {new_txn_id}, {new_app_payer_name}")
                new_app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {new_txn_id}, {new_app_payment_msg}")
                new_app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {new_txn_id}, {new_app_order_id}")
                new_app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_rrn}")

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
                    "date": app_date_and_time,
                    "pmt_mode_2": new_app_payment_mode,
                    "pmt_status_2": new_app_payment_status.split(':')[1],
                    "txn_amt_2": str(new_app_amount).split(' ')[1],
                    "settle_status_2": new_app_settlement_status,
                    "txn_id_2": new_app_txn_id,
                    "rrn_2": str(new_app_rrn),
                    "customer_name_2": new_app_customer_name,
                    "payer_name_2": new_app_payer_name,
                    "order_id_2": new_app_order_id,
                    "pmt_msg_2": new_app_payment_msg,
                    "auth_code_2": new_app_auth_code,
                    "date_2": new_app_date_and_time
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
                date = date_time_converter.db_datetime(original_posting_date)
                new_txn_date = date_time_converter.db_datetime(new_modified_date)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "EXPIRED", "rrn": str(original_rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": original_txn_type, "mid": mid, "tid": tid,
                    "org_code": original_org_code_txn,
                    # "auth_code": auth_code,
                    "date": date,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": amount, "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUND_PENDING", "rrn_2": str(rrn),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": new_txn_type, "mid_2": mid, "tid_2": tid,
                    "org_code_2": new_org_code_txn,
                    "auth_code_2": new_auth_code,
                    "date_2": new_txn_date,
                    "order_id_2": order_id,
                    "device_serial_2": str(device_serial)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for original_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == original_txn_id:
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
                        # auth_code_api = response["authCode"]
                        date_api = elements["createdTime"]
                        device_serial_api = elements["deviceSerial"]
                        order_id_api = elements["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for new_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == new_txn_id:
                        new_txn_status_api = elements["status"]
                        new_txn_amount_api = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        new_txn_payment_mode_api = elements["paymentMode"]
                        new_txn_state_api = elements["states"][0]
                        new_txn_rrn_api = elements["rrNumber"]
                        new_txn_settlement_status_api = elements["settlementStatus"]
                        new_txn_issuer_code_api = elements["issuerCode"]
                        new_txn_acquirer_code_api = elements["acquirerCode"]
                        new_txn_orgCode_api = elements["orgCode"]
                        new_txn_mid_api = elements["mid"]
                        new_txn_tid_api = elements["tid"]
                        new_txn_type_api = elements["txnType"]
                        new_txn_auth_code_api = elements["authCode"]
                        new_txn_date_api = elements["createdTime"]
                        new_txn_device_serial_api = elements["deviceSerial"]
                        new_txn_order_id_api = elements["orderNumber"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "order_id": order_id_api,
                    # "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "device_serial": str(device_serial_api),
                    "pmt_status_2": new_txn_status_api,
                    "txn_amt_2": new_txn_amount_api, "pmt_mode_2": new_txn_payment_mode_api,
                    "pmt_state_2": new_txn_state_api, "rrn_2": str(new_txn_rrn_api),
                    "settle_status_2": new_txn_settlement_status_api,
                    "acquirer_code_2": new_txn_acquirer_code_api,
                    "issuer_code_2": new_txn_issuer_code_api,
                    "txn_type_2": new_txn_type_api, "mid_2": new_txn_mid_api, "tid_2": new_txn_tid_api,
                    "org_code_2": new_txn_orgCode_api,
                    "auth_code_2": new_txn_auth_code_api,
                    "order_id_2": new_txn_order_id_api,
                    "date_2": date_time_converter.from_api_to_datetime_format(new_txn_date_api),
                    "device_serial_2": str(new_txn_device_serial_api)
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
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "REFUND_PENDING",
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "REFUND_PENDING",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "bank_code_2": "HDFC",
                    "pmt_gateway_2": "HDFC",
                    "upi_txn_type_2": "PAY_QR",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "order_id_2": order_id,
                    "device_serial_2": str(device_serial)
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
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                device_serial_db = result['device_serial'].values[0]
                order_id_db = result['external_ref'].values[0]

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
                new_txn_amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db = result["state"].iloc[0]
                new_txn_payment_gateway_db = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db = result["bank_code"].iloc[0]
                new_txn_settlement_status_db = result["settlement_status"].iloc[0]
                new_txn_tid_db = result['tid'].values[0]
                new_txn_mid_db = result['mid'].values[0]
                new_txn_device_serial_db = result['device_serial'].values[0]
                new_txn_order_id_db = result['external_ref'].values[0]

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
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "order_id": order_id_db,
                    "device_serial": str(device_serial_db),
                    "pmt_status_2": new_txn_status_db,
                    "pmt_state_2": new_txn_state_db,
                    "pmt_mode_2": new_txn_payment_mode_db,
                    "txn_amt_2": new_txn_amount_db,
                    "upi_txn_status_2": new_txn_upi_status_db,
                    "settle_status_2": new_txn_settlement_status_db,
                    "acquirer_code_2": new_txn_acquirer_code_db,
                    "bank_code_2": new_txn_bank_code_db,
                    "pmt_gateway_2": new_txn_payment_gateway_db,
                    "upi_txn_type_2": new_txn_upi_txn_type_db,
                    "upi_bank_code_2": new_txn_upi_bank_code_db,
                    "upi_mc_id_2": new_txn_upi_mc_id_db,
                    "mid_2": new_txn_mid_db,
                    "tid_2": new_txn_tid_db,
                    "order_id_2": new_txn_order_id_db,
                    "device_serial_2": str(new_txn_device_serial_db)
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
                date_and_time_portal = date_time_converter.to_portal_format(original_posting_date)
                date_and_time_portal_2 = date_time_converter.to_portal_format(new_modified_date)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "rrn": str(original_rrn),
                    "txn_id": original_txn_id,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "rrn_2": str(rrn),
                    "txn_id_2": new_txn_id
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                refunded_date_time = transaction_details[0]['Date & Time']
                refunded_transaction_id = transaction_details[0]['Transaction ID']
                refunded_total_amount = transaction_details[0]['Total Amount'].split()
                refunded_transaction_type = transaction_details[0]['Type']
                refunded_status = transaction_details[0]['Status']
                refunded_username = transaction_details[0]['Username']
                refunded_rrn = transaction_details[0]['RR Number']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                rrn = transaction_details[1]['RR Number']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "rrn": rrn,
                    "txn_id": transaction_id,
                    "date_time_2": refunded_date_time,
                    "pmt_state_2": str(refunded_status),
                    "pmt_type_2": refunded_transaction_type,
                    "txn_amt_2": refunded_total_amount[1],
                    "username_2": str(refunded_username),
                    "rrn_2": refunded_rrn,
                    "txn_id_2": refunded_transaction_id
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

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
def test_common_100_101_104():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_2_Success_Callback_After_QR_Expiry_HDFC_AutoRefund_Disabled
    Sub Feature Description: Tid Dep - Performing two pure upi success callback via HDFC after expiry the qr when autorefund is disabled
    TC naming code description: 100: Payment Method, 101: UPI, 104: TC104
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
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='UPI' and payment_gateway='HDFC';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            tid = result['tid'].values[0]
            mid = result['mid'].values[0]
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")


            query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
            logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            device_serial = result['device_serial'].values[0]
            logger.info(f"fetched device_serial is : {device_serial}")
            amount = random.randint(51, 100)
            if amount == 55:
                amount = 56
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepUpiQRGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            original_txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {original_txn_id}")

            logger.info("waiting for the time till qr get expired...")
            time.sleep(63)

            query = "select * from txn where id = '" + str(original_txn_id) + "'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn_expired : {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            original_payer_name = result['payer_name'].values[0]
            original_org_code_txn = result['org_code'].values[0]
            original_txn_type = result['txn_type'].values[0]
            original_posting_date = result['posting_date'].values[0]

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id is : {callback_1_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_1_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': callback_1_ref_id, 'Txn_id': original_txn_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_1_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_1 = result['id'].values[0]
            new_txn_customer_name_1 = result['customer_name'].values[0]
            new_txn_payer_name_1 = result['payer_name'].values[0]
            new_org_code_txn_1 = result['org_code'].values[0]
            new_txn_type_1 = result['txn_type'].values[0]
            new_txn_auth_code_1 = result['auth_code'].values[0]
            new_modified_date_1 = result['modified_time'].values[0]
            new_txn_posting_date_1 = result['modified_time'].values[0]

            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_2_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': callback_2_ref_id, 'Txn_id': original_txn_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_2_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_2 = result['id'].values[0]
            new_txn_customer_name_2 = result['customer_name'].values[0]
            new_txn_payer_name_2 = result['payer_name'].values[0]
            new_org_code_txn_2 = result['org_code'].values[0]
            new_txn_type_2 = result['txn_type'].values[0]
            new_txn_auth_code_2 = result['auth_code'].values[0]
            new_modified_date_2 = result['modified_time'].values[0]
            new_txn_posting_date_2 = result['modified_time'].values[0]

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
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                new_txn_date_and_time_1 = date_time_converter.to_app_format(new_txn_posting_date_1)
                new_txn_date_and_time_2 = date_time_converter.to_app_format(new_txn_posting_date_2)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "rrn": str(original_rrn),
                    "payer_name": original_payer_name,
                    "customer_name": original_customer_name,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id_1,
                    "customer_name_2": new_txn_customer_name_1,
                    "payer_name_2": new_txn_payer_name_1,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "rrn_2": str(callback_1_rrn),
                    "auth_code_2": str(new_txn_auth_code_1),
                    "pmt_mode_3": "UPI",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": "{:.2f}".format(amount),
                    "settle_status_3": "SETTLED",
                    "txn_id_3": new_txn_id_2,
                    "customer_name_3": new_txn_customer_name_2,
                    "payer_name_3": new_txn_payer_name_2,
                    "order_id_3": order_id,
                    "pmt_msg_3": "PAYMENT SUCCESSFUL",
                    "rrn_3": str(callback_2_rrn),
                    "auth_code_3": str(new_txn_auth_code_2),
                    "date": date_and_time,
                    "date_2": new_txn_date_and_time_1,
                    "date_3": new_txn_date_and_time_2
                }

                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_original_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the original txn : {original_txn_id}, {app_original_rrn}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the original txn : {original_txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time from txn history for the original txn : {original_txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the original txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the original txn : {original_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the original txn : {original_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement_status from txn history for the original txn : {original_txn_id}, {app_settlement_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the original txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the original txn : {original_txn_id}, {app_payment_msg}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id_1)
                new_app_payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {new_txn_id_1}, {new_app_payment_status_1}")
                new_app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id_1}, {new_app_date_and_time_1}")
                new_app_payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id_1}, {new_app_payment_mode_1}")
                new_app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_1}, {new_app_txn_id_1}")
                new_app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id_1}, {new_app_amount_1}")
                new_app_rrn_1 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_1}, {new_app_rrn_1}")
                new_app_customer_name_1 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id_1}, {new_app_customer_name_1}")
                new_app_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id_1}, {new_app_settlement_status_1}")
                new_app_payer_name_1 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id_1}, {new_app_payer_name_1}")
                new_app_payment_status_1 = new_app_payment_status_1.split(':')[1]
                new_app_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {new_txn_id_1}, {new_app_order_id_1}")
                new_app_payment_msg_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id_1}, {new_app_payment_msg_1}")
                new_txn_app_auth_code_1 = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching txn auth code from txn history for the txn : {new_txn_id_1}, {new_txn_app_auth_code_1}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id_2)
                new_app_payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {new_txn_id_2}, {new_app_payment_status_2}")
                new_app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id_2}, {new_app_date_and_time_2}")
                new_app_payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id_2}, {new_app_payment_mode_2}")
                new_app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_2}, {new_app_txn_id_2}")
                new_app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id_2}, {new_app_amount_2}")
                new_app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_2}, {new_app_rrn_2}")
                new_app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id_2}, {new_app_customer_name_2}")
                new_app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id_2}, {new_app_settlement_status_2}")
                new_app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id_2}, {new_app_payer_name_2}")
                new_app_payment_status_2 = new_app_payment_status_2.split(':')[1]
                new_app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {new_txn_id_2}, {new_app_order_id_2}")
                new_app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id_2}, {new_app_payment_msg_2}")
                new_txn_app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching txn auth code from txn history for the txn : {new_txn_id_2}, {new_txn_app_auth_code_2}")

                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "rrn": str(app_original_rrn),
                    "payer_name": app_payer_name,
                    "customer_name": app_customer_name,
                    "pmt_mode_2": new_app_payment_mode_1,
                    "pmt_status_2": new_app_payment_status_1,
                    "txn_amt_2": str(new_app_amount_1).split(' ')[1],
                    "settle_status_2": new_app_settlement_status_1,
                    "txn_id_2": new_app_txn_id_1,
                    "auth_code_2": str(new_txn_app_auth_code_1),
                    "customer_name_2": new_app_customer_name_1,
                    "payer_name_2": new_app_payer_name_1,
                    "order_id_2": new_app_order_id_1,
                    "pmt_msg_2": new_app_payment_msg_1,
                    "rrn_2": str(new_app_rrn_1),
                    "pmt_mode_3": new_app_payment_mode_2,
                    "pmt_status_3": new_app_payment_status_2,
                    "txn_amt_3": str(new_app_amount_2).split(' ')[1],
                    "settle_status_3": new_app_settlement_status_2,
                    "txn_id_3": new_app_txn_id_2,
                    "customer_name_3": new_app_customer_name_2,
                    "payer_name_3": new_app_payer_name_2,
                    "order_id_3": new_app_order_id_2,
                    "pmt_msg_3": new_app_payment_msg_2,
                    "rrn_3": str(new_app_rrn_2),
                    "auth_code_3": str(new_txn_app_auth_code_2),
                    "date": app_date_and_time,
                    "date_2": new_app_date_and_time_1,
                    "date_3": new_app_date_and_time_2
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
                # time.sleep(5)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(original_posting_date)
                new_txn_date_1 = date_time_converter.db_datetime(new_txn_posting_date_1)
                new_txn_date_2 = date_time_converter.db_datetime(new_txn_posting_date_2)
                expected_api_values = {"pmt_status": "EXPIRED",
                                       "txn_amt": amount, "pmt_mode": "UPI",
                                       "pmt_state": "EXPIRED",
                                       "settle_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "order_id": order_id,
                                       "issuer_code": "HDFC", "rrn": str(original_rrn),
                                       "txn_type": original_txn_type, "mid": mid, "tid": tid, "org_code": org_code,
                                       "payer_name": original_payer_name,
                                       "customer_name": original_customer_name,
                                       "device_serial": str(device_serial),
                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": amount, "pmt_mode_2": "UPI",
                                       "pmt_state_2": "SETTLED",
                                       "rrn_2": str(callback_1_rrn),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "HDFC",
                                       "customer_name_2": new_txn_customer_name_1,
                                       "payer_name_2": new_txn_payer_name_1,
                                       "order_id_2": order_id,
                                       "issuer_code_2": "HDFC",
                                       "txn_type_2": new_txn_type_1, "mid_2": mid,
                                       "tid_2": tid, "org_code_2": org_code,
                                       "device_serial_2": str(device_serial),
                                       "auth_code_2": str(new_txn_auth_code_1),
                                       "pmt_status_3": "AUTHORIZED",
                                       "txn_amt_3": amount, "pmt_mode_3": "UPI",
                                       "pmt_state_3": "SETTLED",
                                       "rrn_3": str(callback_2_rrn),
                                       "settle_status_3": "SETTLED",
                                       "acquirer_code_3": "HDFC",
                                       "customer_name_3": new_txn_customer_name_2,
                                       "payer_name_3": new_txn_payer_name_2,
                                       "order_id_3": order_id,
                                       "issuer_code_3": "HDFC",
                                       "txn_type_3": new_txn_type_2, "mid_3": mid,
                                       "tid_3": tid, "org_code_3": org_code,
                                       "auth_code_3": str(new_txn_auth_code_2),
                                       "date": date,
                                       "date_2": new_txn_date_1,
                                       "date_3": new_txn_date_2,
                                       "device_serial_3": str(device_serial)
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,})
                logger.debug(f"API DETAILS for original_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == original_txn_id:
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
                        date_api = elements["postingDate"]
                        rrn_api = elements["rrNumber"]
                        order_id_api = elements["orderNumber"]
                        device_serial_api = elements["deviceSerial"]
                        payer_name_api = elements["payerName"]
                        customer_name_api = elements["customerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for new_txn_id_1 : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == new_txn_id_1:
                        new_txn_status_api_1 = elements["status"]
                        new_txn_amount_api_1 = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        new_payment_mode_api_1 = elements["paymentMode"]
                        new_txn_state_api_1 = elements["states"][0]
                        new_txn_rrn_api_1 = elements["rrNumber"]
                        new_txn_settlement_status_api_1 = elements["settlementStatus"]
                        new_txn_issuer_code_api_1 = elements["issuerCode"]
                        new_txn_acquirer_code_api_1 = elements["acquirerCode"]
                        new_txn_orgCode_api_1 = elements["orgCode"]
                        new_txn_mid_api_1 = elements["mid"]
                        new_txn_tid_api_1 = elements["tid"]
                        new_txn_txn_type_api_1 = elements["txnType"]
                        new_txn_date_api_1 = elements["createdTime"]
                        new_txn_order_id_api_1 = elements["orderNumber"]
                        new_txn_device_serial_api_1 = elements["deviceSerial"]
                        new_txn_payer_name_api_1 = elements["payerName"]
                        new_txn_customer_name_api_1 = elements["customerName"]
                        new_txn_auth_code_api_1 = elements["authCode"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for new_txn_id_1 : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == new_txn_id_2:
                        new_txn_status_api_2 = elements["status"]
                        new_txn_amount_api_2 = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        new_payment_mode_api_2 = elements["paymentMode"]
                        new_txn_state_api_2 = elements["states"][0]
                        new_txn_rrn_api_2 = elements["rrNumber"]
                        new_txn_settlement_status_api_2 = elements["settlementStatus"]
                        new_txn_issuer_code_api_2 = elements["issuerCode"]
                        new_txn_acquirer_code_api_2 = elements["acquirerCode"]
                        new_txn_orgCode_api_2 = elements["orgCode"]
                        new_txn_mid_api_2 = elements["mid"]
                        new_txn_tid_api_2 = elements["tid"]
                        new_txn_type_api_2 = elements["txnType"]
                        new_txn_date_api_2 = elements["createdTime"]
                        new_txn_order_id_api_2 = elements["orderNumber"]
                        new_txn_device_serial_api_2 = elements["deviceSerial"]
                        new_txn_payer_name_api_2 = elements["payerName"]
                        new_txn_customer_name_api_2 = elements["customerName"]
                        new_txn_auth_code_api_2 = elements["authCode"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "order_id": order_id_api,
                                     "issuer_code": issuer_code_api, "rrn": str(rrn_api),
                                     "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api, "org_code": orgCode_api,
                                     "device_serial": str(device_serial_api),
                                     "payer_name": payer_name_api,
                                     "customer_name": customer_name_api,
                                     "pmt_status_2": new_txn_status_api_1,
                                     "txn_amt_2": new_txn_amount_api_1, "pmt_mode_2": new_payment_mode_api_1,
                                     "pmt_state_2": new_txn_state_api_1,
                                     "rrn_2": str(new_txn_rrn_api_1),
                                     "settle_status_2": new_txn_settlement_status_api_1,
                                     "acquirer_code_2": new_txn_acquirer_code_api_1,
                                     "customer_name_2": new_txn_customer_name_api_1,
                                     "payer_name_2": new_txn_payer_name_api_1,
                                     "issuer_code_2": new_txn_issuer_code_api_1,
                                     "order_id_2": new_txn_order_id_api_1,
                                     "txn_type_2": new_txn_txn_type_api_1, "mid_2": new_txn_mid_api_1,
                                     "tid_2": new_txn_tid_api_1, "org_code_2": new_txn_orgCode_api_1,
                                     "device_serial_2": str(new_txn_device_serial_api_1),
                                     "auth_code_2": str(new_txn_auth_code_api_1),
                                     "pmt_status_3": new_txn_status_api_2,
                                     "txn_amt_3": new_txn_amount_api_2, "pmt_mode_3": new_payment_mode_api_2,
                                     "pmt_state_3": new_txn_state_api_2,
                                     "rrn_3": str(new_txn_rrn_api_2),
                                     "settle_status_3": new_txn_settlement_status_api_2,
                                     "acquirer_code_3": new_txn_acquirer_code_api_2,
                                     "issuer_code_3": new_txn_issuer_code_api_2,
                                     "customer_name_3": new_txn_customer_name_api_2,
                                     "payer_name_3": new_txn_payer_name_api_2,
                                     "order_id_3": new_txn_order_id_api_2,
                                     "txn_type_3": new_txn_type_api_2, "mid_3": new_txn_mid_api_2,
                                     "tid_3": new_txn_tid_api_2, "org_code_3": new_txn_orgCode_api_2,
                                     "auth_code_3": str(new_txn_auth_code_api_2),
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "date_2": date_time_converter.from_api_to_datetime_format(new_txn_date_api_1),
                                     "date_3": date_time_converter.from_api_to_datetime_format(new_txn_date_api_2),
                                     "device_serial_3": str(new_txn_device_serial_api_2)
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
                expected_db_values = {
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    # "payer_name": orig_txn_payer_name,
                    "rrn": str(original_rrn),
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "bank_code_2": "HDFC",
                    "pmt_gateway_2": "HDFC",
                    "payer_name_2": new_txn_payer_name_1,
                    "rrn_2": str(callback_1_rrn),
                    "upi_txn_type_2": "PAY_QR",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id_2": upi_mc_id,
                    "order_id_2": order_id,
                    "device_serial_2": str(device_serial),
                    "pmt_status_3": "AUTHORIZED",
                    "pmt_state_3": "SETTLED",
                    "pmt_mode_3": "UPI",
                    "txn_amt_3": amount,
                    "upi_txn_status_3": "AUTHORIZED",
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "bank_code_3": "HDFC",
                    "pmt_gateway_3": "HDFC",
                    "upi_txn_type_3": "PAY_QR",
                    "upi_bank_code_3": "HDFC",
                    "upi_mc_id_3": upi_mc_id,
                    "order_id_3": order_id,
                    "device_serial_3": str(device_serial),
                    "payer_name_3": new_txn_payer_name_2,
                    "rrn_3": str(callback_2_rrn),
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "mid_3": mid,
                    "tid_3": tid
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
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                # orig_txn_payer_name_db = result['payerName'].values[0]
                original_rrn_db = result['rr_number'].values[0]
                order_id_db = result['external_ref'].values[0]
                device_serial_db = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + new_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_1 = result["status"].iloc[0]
                new_txn_payment_mode_db_1 = result["payment_mode"].iloc[0]
                new_txn_amount_db_1 = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db_1 = result["state"].iloc[0]
                new_txn_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_1 = result["settlement_status"].iloc[0]
                new_txn_tid_db_1 = result['tid'].values[0]
                new_txn_mid_db_1 = result['mid'].values[0]
                new_txn_payer_name_1_db = result['payer_name'].values[0]
                callback_1_rrn_db = result['rr_number'].values[0]
                new_txn_order_id_db_1 = result['external_ref'].values[0]
                new_txn_device_serial_db_1 = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_1 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + new_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_2 = result["status"].iloc[0]
                new_txn_payment_mode_db_2 = result["payment_mode"].iloc[0]
                new_txn_amount_db_2 = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db_2 = result["state"].iloc[0]
                new_txn_payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_2 = result["settlement_status"].iloc[0]
                new_txn_tid_db_2 = result['tid'].values[0]
                new_txn_mid_db_2 = result['mid'].values[0]
                new_txn_payer_name_2_db = result['payer_name'].values[0]
                callback_2_rrn_db = result['rr_number'].values[0]
                new_txn_order_id_db_2 = result['external_ref'].values[0]
                new_txn_device_serial_db_2 = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_2 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_2 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

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
                    # "payer_name": orig_txn_payer_name_db,
                    "rrn": str(original_rrn_db),
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "order_id": order_id_db,
                    "device_serial": str(device_serial_db),
                    "pmt_status_2": new_txn_status_db_1,
                    "pmt_state_2": new_txn_state_db_1,
                    "pmt_mode_2": new_txn_payment_mode_db_1,
                    "txn_amt_2": new_txn_amount_db_1,
                    "upi_txn_status_2": new_txn_upi_status_db_1,
                    "settle_status_2": new_txn_settlement_status_db_1,
                    "acquirer_code_2": new_txn_acquirer_code_db_1,
                    "bank_code_2": new_txn_bank_code_db_1,
                    "pmt_gateway_2": new_txn_payment_gateway_db_1,
                    "payer_name_2": new_txn_payer_name_1_db,
                    "rrn_2": str(callback_1_rrn_db),
                    "upi_txn_type_2": new_txn_upi_txn_type_db_1,
                    "upi_bank_code_2": new_txn_upi_bank_code_db_1,
                    "upi_mc_id_2": new_txn_upi_mc_id_db_1,
                    "order_id_2": new_txn_order_id_db_1,
                    "device_serial_2": str(new_txn_device_serial_db_1),
                    "pmt_status_3": new_txn_status_db_2,
                    "pmt_state_3": new_txn_state_db_2,
                    "pmt_mode_3": new_txn_payment_mode_db_2,
                    "txn_amt_3": new_txn_amount_db_2,
                    "upi_txn_status_3": new_txn_upi_status_db_2,
                    "settle_status_3": new_txn_settlement_status_db_2,
                    "acquirer_code_3": new_txn_acquirer_code_db_2,
                    "bank_code_3": new_txn_bank_code_db_2,
                    "pmt_gateway_3": new_txn_payment_gateway_db_2,
                    "upi_txn_type_3": new_txn_upi_txn_type_db_2,
                    "upi_bank_code_3": new_txn_upi_bank_code_db_2,
                    "upi_mc_id_3": new_txn_upi_mc_id_db_2,
                    "payer_name_3": new_txn_payer_name_2_db,
                    "order_id_3": new_txn_order_id_db_2,
                    "device_serial_3": str(new_txn_device_serial_db_2),
                    "rrn_3": str(callback_2_rrn_db),
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": new_txn_mid_db_1,
                    "tid_2": new_txn_tid_db_1,
                    "mid_3": new_txn_mid_db_2,
                    "tid_3": new_txn_tid_db_2
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
                date_and_time_portal = date_time_converter.to_portal_format(original_posting_date)
                date_and_time_portal_2 = date_time_converter.to_portal_format(new_txn_posting_date_1)
                date_and_time_portal_3 = date_time_converter.to_portal_format(new_txn_posting_date_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": original_txn_id,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "rrn_2": str(callback_1_rrn),
                    "txn_id_2": new_txn_id_1,

                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "AUTHORIZED",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": f"{str(amount)}.00",
                    "username_3": app_username,
                    "rrn_3": str(callback_2_rrn),
                    "txn_id_3": new_txn_id_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                refunded_date_time = transaction_details[0]['Date & Time']
                refunded_transaction_id = transaction_details[0]['Transaction ID']
                refunded_total_amount = transaction_details[0]['Total Amount'].split()
                refunded_transaction_type = transaction_details[0]['Type']
                refunded_status = transaction_details[0]['Status']
                refunded_username = transaction_details[0]['Username']
                refunded_rrn = transaction_details[0]['RR Number']

                date_time_1 = transaction_details[1]['Date & Time']
                transaction_id_1 = transaction_details[1]['Transaction ID']
                total_amount_1 = transaction_details[1]['Total Amount'].split()
                transaction_type_1 = transaction_details[1]['Type']
                status_1 = transaction_details[1]['Status']
                username_1 = transaction_details[1]['Username']
                rrn_1 = transaction_details[1]['RR Number']

                date_time = transaction_details[2]['Date & Time']
                transaction_id = transaction_details[2]['Transaction ID']
                total_amount = transaction_details[2]['Total Amount'].split()
                transaction_type = transaction_details[2]['Type']
                status = transaction_details[2]['Status']
                username = transaction_details[2]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,

                    "date_time_2": date_time_1,
                    "pmt_state_2": str(status_1),
                    "pmt_type_2": transaction_type_1,
                    "txn_amt_2": total_amount_1[1],
                    "username_2": username_1,
                    "rrn_2": rrn_1,
                    "txn_id_2": transaction_id_1,

                    "date_time_3": refunded_date_time,
                    "pmt_state_3": str(refunded_status),
                    "pmt_type_3": refunded_transaction_type,
                    "txn_amt_3": refunded_total_amount[1],
                    "username_3": str(refunded_username),
                    "rrn_3": refunded_rrn,
                    "txn_id_3": refunded_transaction_id
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

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
                new_txn_date_1, new_txn_time_1 = date_time_converter.to_chargeslip_format(new_txn_posting_date_1)
                new_txn_date_2, new_txn_time_2 = date_time_converter.to_chargeslip_format(new_txn_posting_date_2)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(callback_1_rrn), 'date': new_txn_date_1, 'time': new_txn_time_1,
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    "AUTH CODE": str(new_txn_auth_code_1),
                }
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(callback_2_rrn), 'date': new_txn_date_2, 'time': new_txn_time_2,
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    "AUTH CODE": str(new_txn_auth_code_2),
                }
                charge_slip_val_result_1 = receipt_validator.perform_charge_slip_validations(
                    new_txn_id_1, {"username": app_username, "password": app_password}, expected_charge_slip_values_1)
                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(
                    new_txn_id_2, {"username": app_username, "password": app_password}, expected_charge_slip_values_2)

                if charge_slip_val_result_1 and charge_slip_val_result_2:
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_101_105():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_2_Success_Callback_After_QR_Expiry_HDFC_AutoRefund_Enabled
    Sub Feature Description: Tid Dep - Performing two  upi success callback via HDFC after expiry the qr when autorefund is enabled
    TC naming code description: 100: Payment Method, 101: UPI, 105: TC105
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
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='UPI' and payment_gateway='HDFC';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")
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
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            tid = result['tid'].values[0]
            mid = result['mid'].values[0]
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
            logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            device_serial = result['device_serial'].values[0]
            logger.info(f"fetched device_serial is : {device_serial}")
            amount = random.randint(51, 100)
            if amount == 55:
                amount = 56
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepUpiQRGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            original_txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {original_txn_id}")

            logger.info("waiting for the time till qr get expired...")
            time.sleep(63)

            query = "select * from txn where id = '" + str(original_txn_id) + "'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn_expired : {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            original_payer_name = result['payer_name'].values[0]
            original_org_code_txn = result['org_code'].values[0]
            original_txn_type = result['txn_type'].values[0]
            original_posting_date = result['posting_date'].values[0]

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id is : {callback_1_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_1_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': callback_1_ref_id, 'Txn_id': original_txn_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_1_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_1 = result['id'].values[0]
            new_txn_customer_name_1 = result['customer_name'].values[0]
            new_txn_payer_name_1 = result['payer_name'].values[0]
            new_org_code_txn_1 = result['org_code'].values[0]
            new_txn_type_1 = result['txn_type'].values[0]
            new_txn_auth_code_1 = result['auth_code'].values[0]
            new_modified_date_1 = result['modified_time'].values[0]
            new_txn_posting_date_1 = result['modified_time'].values[0]

            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_2_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': callback_2_ref_id, 'Txn_id': original_txn_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_2_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_2 = result['id'].values[0]
            new_txn_customer_name_2 = result['customer_name'].values[0]
            new_txn_payer_name_2 = result['payer_name'].values[0]
            new_org_code_txn_2 = result['org_code'].values[0]
            new_txn_type_2 = result['txn_type'].values[0]
            new_txn_auth_code_2 = result['auth_code'].values[0]
            new_modified_date_2 = result['modified_time'].values[0]
            new_txn_posting_date_2 = result['modified_time'].values[0]

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
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                new_txn_date_and_time_1 = date_time_converter.to_app_format(new_txn_posting_date_1)
                new_txn_date_and_time_2 = date_time_converter.to_app_format(new_txn_posting_date_2)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount)+".00",
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "rrn": str(original_rrn),
                    "payer_name": original_payer_name,
                    "customer_name": original_customer_name,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": str(amount)+".00",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id_1,
                    "customer_name_2": new_txn_customer_name_1,
                    "payer_name_2": new_txn_payer_name_1,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "rrn_2": str(callback_1_rrn),
                    "auth_code_2": str(new_txn_auth_code_1),
                    "pmt_mode_3": "UPI",
                    "pmt_status_3": "REFUND_PENDING",
                    "txn_amt_3": str(amount)+".00",
                    "settle_status_3": "SETTLED",
                    "txn_id_3": new_txn_id_2,
                    "customer_name_3": new_txn_customer_name_2,
                    "payer_name_3": new_txn_payer_name_2,
                    "order_id_3": order_id,
                    "pmt_msg_3": "PAYMENT SUCCESSFUL",
                    "rrn_3": str(callback_2_rrn),
                    "auth_code_3": str(new_txn_auth_code_2),
                    "date": date_and_time,
                    "date_2": new_txn_date_and_time_1,
                    "date_3": new_txn_date_and_time_2
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_original_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the original txn : {original_txn_id}, {app_original_rrn}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the original txn : {original_txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time from txn history for the original txn : {original_txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the original txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the original txn : {original_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the original txn : {original_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement_status from txn history for the original txn : {original_txn_id}, {app_settlement_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the original txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the original txn : {original_txn_id}, {app_payment_msg}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id_1)
                new_app_payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {new_txn_id_1}, {new_app_payment_status_1}")
                new_app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id_1}, {new_app_date_and_time_1}")
                new_app_payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id_1}, {new_app_payment_mode_1}")
                new_app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_1}, {new_app_txn_id_1}")
                new_app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id_1}, {new_app_amount_1}")
                new_app_rrn_1 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_1}, {new_app_rrn_1}")
                new_app_customer_name_1 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id_1}, {new_app_customer_name_1}")
                new_app_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id_1}, {new_app_settlement_status_1}")
                new_app_payer_name_1 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id_1}, {new_app_payer_name_1}")
                new_app_payment_status_1 = new_app_payment_status_1.split(':')[1]
                new_app_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {new_txn_id_1}, {new_app_order_id_1}")
                new_app_payment_msg_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id_1}, {new_app_payment_msg_1}")
                new_txn_app_auth_code_1 = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching txn auth code from txn history for the txn : {new_txn_id_1}, {new_txn_app_auth_code_1}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id_2)
                new_app_payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {new_txn_id_2}, {new_app_payment_status_2}")
                new_app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id_2}, {new_app_date_and_time_2}")
                new_app_payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id_2}, {new_app_payment_mode_2}")
                new_app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_2}, {new_app_txn_id_2}")
                new_app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id_2}, {new_app_amount_2}")
                new_app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_2}, {new_app_rrn_2}")
                new_app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id_2}, {new_app_customer_name_2}")
                new_app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id_2}, {new_app_settlement_status_2}")
                new_app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id_2}, {new_app_payer_name_2}")
                new_app_payment_status_2 = new_app_payment_status_2.split(':')[1]
                new_app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {new_txn_id_2}, {new_app_order_id_2}")
                new_app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id_2}, {new_app_payment_msg_2}")
                new_txn_app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching txn auth code from txn history for the txn : {new_txn_id_2}, {new_txn_app_auth_code_2}")

                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "rrn": str(app_original_rrn),
                    "payer_name": app_payer_name,
                    "customer_name": app_customer_name,
                    "pmt_mode_2": new_app_payment_mode_1,
                    "pmt_status_2": new_app_payment_status_1,
                    "txn_amt_2": str(new_app_amount_1).split(' ')[1],
                    "settle_status_2": new_app_settlement_status_1,
                    "txn_id_2": new_app_txn_id_1,
                    "auth_code_2": str(new_txn_app_auth_code_1),
                    "customer_name_2": new_app_customer_name_1,
                    "payer_name_2": new_app_payer_name_1,
                    "order_id_2": new_app_order_id_1,
                    "pmt_msg_2": new_app_payment_msg_1,
                    "rrn_2": str(new_app_rrn_1),
                    "pmt_mode_3": new_app_payment_mode_2,
                    "pmt_status_3": new_app_payment_status_2,
                    "txn_amt_3": str(new_app_amount_2).split(' ')[1],
                    "settle_status_3": new_app_settlement_status_2,
                    "txn_id_3": new_app_txn_id_2,
                    "customer_name_3": new_app_customer_name_2,
                    "payer_name_3": new_app_payer_name_2,
                    "order_id_3": new_app_order_id_2,
                    "pmt_msg_3": new_app_payment_msg_2,
                    "rrn_3": str(new_app_rrn_2),
                    "auth_code_3": str(new_txn_app_auth_code_2),
                    "date": app_date_and_time,
                    "date_2": new_app_date_and_time_1,
                    "date_3": new_app_date_and_time_2
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
                # time.sleep(5)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(original_posting_date)
                new_txn_date_1 = date_time_converter.db_datetime(new_txn_posting_date_1)
                new_txn_date_2 = date_time_converter.db_datetime(new_txn_posting_date_2)
                expected_api_values = {"pmt_status": "EXPIRED",
                                       "txn_amt": amount, "pmt_mode": "UPI",
                                       "pmt_state": "EXPIRED",
                                       "settle_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "order_id": order_id,
                                       "issuer_code": "HDFC", "rrn": str(original_rrn),
                                       "txn_type": original_txn_type, "mid": mid, "tid": tid, "org_code": org_code,
                                       "payer_name": original_payer_name,
                                       "customer_name": original_customer_name,
                                       "device_serial": str(device_serial),
                                       "pmt_status_2": "REFUND_PENDING",
                                       "txn_amt_2": amount, "pmt_mode_2": "UPI",
                                       "pmt_state_2": "REFUND_PENDING",
                                       "rrn_2": str(callback_1_rrn),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "HDFC",
                                       "customer_name_2": new_txn_customer_name_1,
                                       "payer_name_2": new_txn_payer_name_1,
                                       "order_id_2": order_id,
                                       "issuer_code_2": "HDFC",
                                       "txn_type_2": new_txn_type_1, "mid_2": mid,
                                       "tid_2": tid, "org_code_2": org_code,
                                       "device_serial_2": str(device_serial),
                                       "auth_code_2": str(new_txn_auth_code_1),
                                       "pmt_status_3": "REFUND_PENDING",
                                       "txn_amt_3": amount, "pmt_mode_3": "UPI",
                                       "pmt_state_3": "REFUND_PENDING",
                                       "rrn_3": str(callback_2_rrn),
                                       "settle_status_3": "SETTLED",
                                       "acquirer_code_3": "HDFC",
                                       "customer_name_3": new_txn_customer_name_2,
                                       "payer_name_3": new_txn_payer_name_2,
                                       "order_id_3": order_id,
                                       "issuer_code_3": "HDFC",
                                       "txn_type_3": new_txn_type_2, "mid_3": mid,
                                       "tid_3": tid, "org_code_3": org_code,
                                       "auth_code_3": str(new_txn_auth_code_2),
                                       "date": date,
                                       "date_2": new_txn_date_1,
                                       "date_3": new_txn_date_2,
                                       "device_serial_3": str(device_serial)
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,})
                logger.debug(f"API DETAILS for original_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == original_txn_id:
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
                        date_api = elements["postingDate"]
                        rrn_api = elements["rrNumber"]
                        order_id_api = elements["orderNumber"]
                        device_serial_api = elements["deviceSerial"]
                        payer_name_api = elements["payerName"]
                        customer_name_api = elements["customerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for new_txn_id_1 : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == new_txn_id_1:
                        new_txn_status_api_1 = elements["status"]
                        new_txn_amount_api_1 = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        new_payment_mode_api_1 = elements["paymentMode"]
                        new_txn_state_api_1 = elements["states"][0]
                        new_txn_rrn_api_1 = elements["rrNumber"]
                        new_txn_settlement_status_api_1 = elements["settlementStatus"]
                        new_txn_issuer_code_api_1 = elements["issuerCode"]
                        new_txn_acquirer_code_api_1 = elements["acquirerCode"]
                        new_txn_orgCode_api_1 = elements["orgCode"]
                        new_txn_mid_api_1 = elements["mid"]
                        new_txn_tid_api_1 = elements["tid"]
                        new_txn_txn_type_api_1 = elements["txnType"]
                        new_txn_date_api_1 = elements["createdTime"]
                        new_txn_order_id_api_1 = elements["orderNumber"]
                        new_txn_device_serial_api_1 = elements["deviceSerial"]
                        new_txn_payer_name_api_1 = elements["payerName"]
                        new_txn_customer_name_api_1 = elements["customerName"]
                        new_txn_auth_code_api_1 = elements["authCode"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for new_txn_id_1 : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == new_txn_id_2:
                        new_txn_status_api_2 = elements["status"]
                        new_txn_amount_api_2 = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        new_payment_mode_api_2 = elements["paymentMode"]
                        new_txn_state_api_2 = elements["states"][0]
                        new_txn_rrn_api_2 = elements["rrNumber"]
                        new_txn_settlement_status_api_2 = elements["settlementStatus"]
                        new_txn_issuer_code_api_2 = elements["issuerCode"]
                        new_txn_acquirer_code_api_2 = elements["acquirerCode"]
                        new_txn_orgCode_api_2 = elements["orgCode"]
                        new_txn_mid_api_2 = elements["mid"]
                        new_txn_tid_api_2 = elements["tid"]
                        new_txn_type_api_2 = elements["txnType"]
                        new_txn_date_api_2 = elements["createdTime"]
                        new_txn_order_id_api_2 = elements["orderNumber"]
                        new_txn_device_serial_api_2 = elements["deviceSerial"]
                        new_txn_payer_name_api_2 = elements["payerName"]
                        new_txn_customer_name_api_2 = elements["customerName"]
                        new_txn_auth_code_api_2 = elements["authCode"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "order_id": order_id_api,
                                     "issuer_code": issuer_code_api, "rrn": str(rrn_api),
                                     "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api, "org_code": orgCode_api,
                                     "device_serial": str(device_serial_api),
                                     "payer_name": payer_name_api,
                                     "customer_name": customer_name_api,
                                     "pmt_status_2": new_txn_status_api_1,
                                     "txn_amt_2": new_txn_amount_api_1, "pmt_mode_2": new_payment_mode_api_1,
                                     "pmt_state_2": new_txn_state_api_1,
                                     "rrn_2": str(new_txn_rrn_api_1),
                                     "settle_status_2": new_txn_settlement_status_api_1,
                                     "acquirer_code_2": new_txn_acquirer_code_api_1,
                                     "customer_name_2": new_txn_customer_name_api_1,
                                     "payer_name_2": new_txn_payer_name_api_1,
                                     "issuer_code_2": new_txn_issuer_code_api_1,
                                     "order_id_2": new_txn_order_id_api_1,
                                     "txn_type_2": new_txn_txn_type_api_1, "mid_2": new_txn_mid_api_1,
                                     "tid_2": new_txn_tid_api_1, "org_code_2": new_txn_orgCode_api_1,
                                     "device_serial_2": str(new_txn_device_serial_api_1),
                                     "auth_code_2": str(new_txn_auth_code_api_1),
                                     "pmt_status_3": new_txn_status_api_2,
                                     "txn_amt_3": new_txn_amount_api_2, "pmt_mode_3": new_payment_mode_api_2,
                                     "pmt_state_3": new_txn_state_api_2,
                                     "rrn_3": str(new_txn_rrn_api_2),
                                     "settle_status_3": new_txn_settlement_status_api_2,
                                     "acquirer_code_3": new_txn_acquirer_code_api_2,
                                     "issuer_code_3": new_txn_issuer_code_api_2,
                                     "customer_name_3": new_txn_customer_name_api_2,
                                     "payer_name_3": new_txn_payer_name_api_2,
                                     "order_id_3": new_txn_order_id_api_2,
                                     "txn_type_3": new_txn_type_api_2, "mid_3": new_txn_mid_api_2,
                                     "tid_3": new_txn_tid_api_2, "org_code_3": new_txn_orgCode_api_2,
                                     "auth_code_3": str(new_txn_auth_code_api_2),
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "date_2": date_time_converter.from_api_to_datetime_format(new_txn_date_api_1),
                                     "date_3": date_time_converter.from_api_to_datetime_format(new_txn_date_api_2),
                                     "device_serial_3": str(new_txn_device_serial_api_2)
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
                expected_db_values = {
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    # "payer_name": orig_txn_payer_name,
                    "rrn": str(original_rrn),
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "REFUND_PENDING",
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "REFUND_PENDING",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "bank_code_2": "HDFC",
                    "pmt_gateway_2": "HDFC",
                    "payer_name_2": new_txn_payer_name_1,
                    "rrn_2": str(callback_1_rrn),
                    "upi_txn_type_2": "PAY_QR",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id_2": upi_mc_id,
                    "order_id_2": order_id,
                    "device_serial_2": str(device_serial),
                    "pmt_status_3": "REFUND_PENDING",
                    "pmt_state_3": "REFUND_PENDING",
                    "pmt_mode_3": "UPI",
                    "txn_amt_3": amount,
                    "upi_txn_status_3": "REFUND_PENDING",
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "bank_code_3": "HDFC",
                    "pmt_gateway_3": "HDFC",
                    "upi_txn_type_3": "PAY_QR",
                    "upi_bank_code_3": "HDFC",
                    "upi_mc_id_3": upi_mc_id,
                    "order_id_3": order_id,
                    "device_serial_3": str(device_serial),
                    "payer_name_3": new_txn_payer_name_2,
                    "rrn_3": str(callback_2_rrn),
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "mid_3": mid,
                    "tid_3": tid
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
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                # orig_txn_payer_name_db = result['payerName'].values[0]
                original_rrn_db = result['rr_number'].values[0]
                order_id_db = result['external_ref'].values[0]
                device_serial_db = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + new_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_1 = result["status"].iloc[0]
                new_txn_payment_mode_db_1 = result["payment_mode"].iloc[0]
                new_txn_amount_db_1 = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db_1 = result["state"].iloc[0]
                new_txn_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_1 = result["settlement_status"].iloc[0]
                new_txn_tid_db_1 = result['tid'].values[0]
                new_txn_mid_db_1 = result['mid'].values[0]
                new_txn_payer_name_1_db = result['payer_name'].values[0]
                callback_1_rrn_db = result['rr_number'].values[0]
                new_txn_order_id_db_1 = result['external_ref'].values[0]
                new_txn_device_serial_db_1 = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_1 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + new_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_2 = result["status"].iloc[0]
                new_txn_payment_mode_db_2 = result["payment_mode"].iloc[0]
                new_txn_amount_db_2 = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db_2 = result["state"].iloc[0]
                new_txn_payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_2 = result["settlement_status"].iloc[0]
                new_txn_tid_db_2 = result['tid'].values[0]
                new_txn_mid_db_2 = result['mid'].values[0]
                new_txn_payer_name_2_db = result['payer_name'].values[0]
                callback_2_rrn_db = result['rr_number'].values[0]
                new_txn_order_id_db_2 = result['external_ref'].values[0]
                new_txn_device_serial_db_2 = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_2 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_2 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

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
                    # "payer_name": orig_txn_payer_name_db,
                    "rrn": str(original_rrn_db),
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "order_id": order_id_db,
                    "device_serial": str(device_serial_db),
                    "pmt_status_2": new_txn_status_db_1,
                    "pmt_state_2": new_txn_state_db_1,
                    "pmt_mode_2": new_txn_payment_mode_db_1,
                    "txn_amt_2": new_txn_amount_db_1,
                    "upi_txn_status_2": new_txn_upi_status_db_1,
                    "settle_status_2": new_txn_settlement_status_db_1,
                    "acquirer_code_2": new_txn_acquirer_code_db_1,
                    "bank_code_2": new_txn_bank_code_db_1,
                    "pmt_gateway_2": new_txn_payment_gateway_db_1,
                    "payer_name_2": new_txn_payer_name_1_db,
                    "rrn_2": str(callback_1_rrn_db),
                    "upi_txn_type_2": new_txn_upi_txn_type_db_1,
                    "upi_bank_code_2": new_txn_upi_bank_code_db_1,
                    "upi_mc_id_2": new_txn_upi_mc_id_db_1,
                    "order_id_2": new_txn_order_id_db_1,
                    "device_serial_2": str(new_txn_device_serial_db_1),
                    "pmt_status_3": new_txn_status_db_2,
                    "pmt_state_3": new_txn_state_db_2,
                    "pmt_mode_3": new_txn_payment_mode_db_2,
                    "txn_amt_3": new_txn_amount_db_2,
                    "upi_txn_status_3": new_txn_upi_status_db_2,
                    "settle_status_3": new_txn_settlement_status_db_2,
                    "acquirer_code_3": new_txn_acquirer_code_db_2,
                    "bank_code_3": new_txn_bank_code_db_2,
                    "pmt_gateway_3": new_txn_payment_gateway_db_2,
                    "upi_txn_type_3": new_txn_upi_txn_type_db_2,
                    "upi_bank_code_3": new_txn_upi_bank_code_db_2,
                    "upi_mc_id_3": new_txn_upi_mc_id_db_2,
                    "payer_name_3": new_txn_payer_name_2_db,
                    "order_id_3": new_txn_order_id_db_2,
                    "device_serial_3": str(new_txn_device_serial_db_2),
                    "rrn_3": str(callback_2_rrn_db),
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": new_txn_mid_db_1,
                    "tid_2": new_txn_tid_db_1,
                    "mid_3": new_txn_mid_db_2,
                    "tid_3": new_txn_tid_db_2
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
                date_and_time_portal = date_time_converter.to_portal_format(original_posting_date)
                date_and_time_portal_2 = date_time_converter.to_portal_format(new_txn_posting_date_1)
                date_and_time_portal_3 = date_time_converter.to_portal_format(new_txn_posting_date_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": original_txn_id,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "rrn_2": str(callback_1_rrn),
                    "txn_id_2": new_txn_id_1,

                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "REFUND_PENDING",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": f"{str(amount)}.00",
                    "username_3": app_username,
                    "rrn_3": str(callback_2_rrn),
                    "txn_id_3": new_txn_id_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                refunded_date_time = transaction_details[0]['Date & Time']
                refunded_transaction_id = transaction_details[0]['Transaction ID']
                refunded_total_amount = transaction_details[0]['Total Amount'].split()
                refunded_transaction_type = transaction_details[0]['Type']
                refunded_status = transaction_details[0]['Status']
                refunded_username = transaction_details[0]['Username']
                refunded_rrn = transaction_details[0]['RR Number']

                date_time_1 = transaction_details[1]['Date & Time']
                transaction_id_1 = transaction_details[1]['Transaction ID']
                total_amount_1 = transaction_details[1]['Total Amount'].split()
                transaction_type_1 = transaction_details[1]['Type']
                status_1 = transaction_details[1]['Status']
                username_1 = transaction_details[1]['Username']
                rrn_1 = transaction_details[1]['RR Number']

                date_time = transaction_details[2]['Date & Time']
                transaction_id = transaction_details[2]['Transaction ID']
                total_amount = transaction_details[2]['Total Amount'].split()
                transaction_type = transaction_details[2]['Type']
                status = transaction_details[2]['Status']
                username = transaction_details[2]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,

                    "date_time_2": date_time_1,
                    "pmt_state_2": str(status_1),
                    "pmt_type_2": transaction_type_1,
                    "txn_amt_2": total_amount_1[1],
                    "username_2": username_1,
                    "rrn_2": rrn_1,
                    "txn_id_2": transaction_id_1,

                    "date_time_3": refunded_date_time,
                    "pmt_state_3": str(refunded_status),
                    "pmt_type_3": refunded_transaction_type,
                    "txn_amt_3": refunded_total_amount[1],
                    "username_3": str(refunded_username),
                    "rrn_3": refunded_rrn,
                    "txn_id_3": refunded_transaction_id
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_101_106():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_failed_callback_after_qr_expiry_TID_Dep_HDFC_AutoRefund_Disabled
    Sub Feature Description: Tid Dep - Performing two pure upi failed callback via HDFC after expiry the qr when autorefund is disabled
    TC naming code description: 100: Payment Method, 101: UPI, 106: TC106
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
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='UPI' and payment_gateway='HDFC';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            tid = result['tid'].values[0]
            mid = result['mid'].values[0]
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
            logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            device_serial = result['device_serial'].values[0]
            logger.info(f"fetched device_serial is : {device_serial}")
            amount = random.randint(51, 100)
            if amount == 55:
                amount = 56
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepUpiQRGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            original_txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {original_txn_id}")

            logger.info("waiting for the time till qr get expired...")
            time.sleep(63)

            query = "select * from txn where id = '" + str(original_txn_id) + "'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn_expired : {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            original_payer_name = result['payer_name'].values[0]
            original_org_code_txn = result['org_code'].values[0]
            original_txn_type = result['txn_type'].values[0]
            original_posting_date = result['posting_date'].values[0]

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id is : {callback_1_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_1_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': callback_1_ref_id, 'Txn_id': original_txn_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_1_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")

            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_2_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': callback_2_ref_id, 'Txn_id': original_txn_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_2_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")

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
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "rrn": str(original_rrn),
                    "payer_name": original_payer_name,
                    "customer_name": original_customer_name,
                    "date": date_and_time,
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_original_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the original txn : {original_txn_id}, {app_original_rrn}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the original txn : {original_txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time from txn history for the original txn : {original_txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the original txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the original txn : {original_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the original txn : {original_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement_status from txn history for the original txn : {original_txn_id}, {app_settlement_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the original txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the original txn : {original_txn_id}, {app_payment_msg}")

                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "rrn": str(app_original_rrn),
                    "payer_name": app_payer_name,
                    "customer_name": app_customer_name,
                    "date": app_date_and_time,
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
                date = date_time_converter.db_datetime(original_posting_date)
                expected_api_values = {"pmt_status": "EXPIRED",
                                       "txn_amt": amount, "pmt_mode": "UPI",
                                       "pmt_state": "EXPIRED",
                                       "settle_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "order_id": order_id,
                                       "issuer_code": "HDFC", "rrn": str(original_rrn),
                                       "txn_type": original_txn_type, "mid": mid, "tid": tid, "org_code": org_code,
                                       "payer_name": original_payer_name,
                                       "customer_name": original_customer_name,
                                       "device_serial": str(device_serial),
                                       "date": date,
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,})
                logger.debug(f"API DETAILS for original_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == original_txn_id:
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
                        date_api = elements["postingDate"]
                        rrn_api = elements["rrNumber"]
                        order_id_api = elements["orderNumber"]
                        device_serial_api = elements["deviceSerial"]
                        payer_name_api = elements["payerName"]
                        customer_name_api = elements["customerName"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "order_id": order_id_api,
                                     "issuer_code": issuer_code_api, "rrn": str(rrn_api),
                                     "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api, "org_code": orgCode_api,
                                     "device_serial": str(device_serial_api),
                                     "payer_name": payer_name_api,
                                     "customer_name": customer_name_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
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
                expected_db_values = {
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    # "payer_name": orig_txn_payer_name,
                    "rrn": str(original_rrn),
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "mid": mid,
                    "tid": tid,
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
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                # orig_txn_payer_name_db = result['payerName'].values[0]
                original_rrn_db = result['rr_number'].values[0]
                order_id_db = result['external_ref'].values[0]
                device_serial_db = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

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
                    # "payer_name": orig_txn_payer_name_db,
                    "rrn": str(original_rrn_db),
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "order_id": order_id_db,
                    "device_serial": str(device_serial_db),
                    "mid": mid_db,
                    "tid": tid_db,
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
                date_and_time_portal = date_time_converter.to_portal_format(original_posting_date)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_101_107():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_2_Failed_Callback_After_QR_Expiry_HDFC_AutoRefund_Enabled
    Sub Feature Description: Tid Dep - Performing two upi failed callback via HDFC after expiry the qr when autorefund is enabled
    TC naming code description: 100: Payment Method, 101: UPI, 107: TC107
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
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='UPI' and payment_gateway='HDFC';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")
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
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            tid = result['tid'].values[0]
            mid = result['mid'].values[0]
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
            logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            device_serial = result['device_serial'].values[0]
            logger.info(f"fetched device_serial is : {device_serial}")
            amount = random.randint(51, 100)
            if amount == 55:
                amount = 56
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepUpiQRGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            original_txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {original_txn_id}")

            logger.info("waiting for the time till qr get expired...")
            time.sleep(63)

            query = "select * from txn where id = '" + str(original_txn_id) + "'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn_expired : {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            original_payer_name = result['payer_name'].values[0]
            original_org_code_txn = result['org_code'].values[0]
            original_txn_type = result['txn_type'].values[0]
            original_posting_date = result['posting_date'].values[0]

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id is : {callback_1_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_1_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': callback_1_ref_id, 'Txn_id': original_txn_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_1_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")

            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_2_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': callback_2_ref_id, 'Txn_id': original_txn_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_2_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")

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
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "rrn": str(original_rrn),
                    "payer_name": original_payer_name,
                    "customer_name": original_customer_name,
                    "date": date_and_time,
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_original_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the original txn : {original_txn_id}, {app_original_rrn}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the original txn : {original_txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time from txn history for the original txn : {original_txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the original txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the original txn : {original_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the original txn : {original_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement_status from txn history for the original txn : {original_txn_id}, {app_settlement_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the original txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the original txn : {original_txn_id}, {app_payment_msg}")

                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "rrn": str(app_original_rrn),
                    "payer_name": app_payer_name,
                    "customer_name": app_customer_name,
                    "date": app_date_and_time,
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
                date = date_time_converter.db_datetime(original_posting_date)
                expected_api_values = {"pmt_status": "EXPIRED",
                                       "txn_amt": amount, "pmt_mode": "UPI",
                                       "pmt_state": "EXPIRED",
                                       "settle_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "order_id": order_id,
                                       "issuer_code": "HDFC", "rrn": str(original_rrn),
                                       "txn_type": original_txn_type, "mid": mid, "tid": tid, "org_code": org_code,
                                       "payer_name": original_payer_name,
                                       "customer_name": original_customer_name,
                                       "device_serial": str(device_serial),
                                       "date": date,
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,})
                logger.debug(f"API DETAILS for original_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == original_txn_id:
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
                        date_api = elements["postingDate"]
                        rrn_api = elements["rrNumber"]
                        order_id_api = elements["orderNumber"]
                        device_serial_api = elements["deviceSerial"]
                        payer_name_api = elements["payerName"]
                        customer_name_api = elements["customerName"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "order_id": order_id_api,
                                     "issuer_code": issuer_code_api, "rrn": str(rrn_api),
                                     "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api, "org_code": orgCode_api,
                                     "device_serial": str(device_serial_api),
                                     "payer_name": payer_name_api,
                                     "customer_name": customer_name_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
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
                expected_db_values = {
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    # "payer_name": orig_txn_payer_name,
                    "rrn": str(original_rrn),
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "order_id": order_id,
                    "device_serial": str(device_serial),
                    "mid": mid,
                    "tid": tid,
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
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                # orig_txn_payer_name_db = result['payerName'].values[0]
                original_rrn_db = result['rr_number'].values[0]
                order_id_db = result['external_ref'].values[0]
                device_serial_db = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

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
                    # "payer_name": orig_txn_payer_name_db,
                    "rrn": str(original_rrn_db),
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "order_id": order_id_db,
                    "device_serial": str(device_serial_db),
                    "mid": mid_db,
                    "tid": tid_db,
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
                date_and_time_portal = date_time_converter.to_portal_format(original_posting_date)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
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
