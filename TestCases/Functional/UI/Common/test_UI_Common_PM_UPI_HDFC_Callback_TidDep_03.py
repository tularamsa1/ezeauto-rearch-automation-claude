import random
import sys
from datetime import datetime

import pytest

from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter, receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_109():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_success_callback_before_qr_expiry_TID_Dep_HDFC_AutoRefund_Disabled
    Sub Feature Description: Performing two pure upi success callback via TID Dep HDFC before expiry the qr when autorefund is disabled
    TC naming code description:
    100: Payment Method
    101: UPI
    109: TC109
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

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            tid = result['tid'].values[0]
            mid = result['mid'].values[0]
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

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

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
            new_txn_posting_date_1 = result['created_time'].values[0]

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
                new_txn_date_and_time_1 = date_time_converter.to_app_format(new_txn_posting_date_1)
                new_txn_date_and_time_2 = date_time_converter.to_app_format(new_txn_posting_date_2)
                expected_app_values = {
                    "new_txn_payment_mode_1": "UPI",
                    "new_txn_payment_status_1": "AUTHORIZED",
                    "new_txn_amount_1": str(amount),
                    "new_txn_settlement_status_1": "SETTLED",
                    "new_txn_id_1": new_txn_id_1,
                    "new_txn_customer_name_1": new_txn_customer_name_1,
                    "new_txn_payer_name_1": new_txn_payer_name_1,
                    "new_txn_order_id_1": order_id,
                    "new_txn_payment_msg_1": "PAYMENT SUCCESSFUL",
                    "new_txn_rrn_1": str(callback_1_rrn),
                    "new_txn_auth_code_1": str(new_txn_auth_code_1),
                    "new_txn_payment_mode_2": "UPI",
                    "new_txn_payment_status_2": "AUTHORIZED",
                    "new_txn_amount_2": str(amount),
                    "new_txn_settlement_status_2": "SETTLED",
                    "new_txn_id_2": new_txn_id_2,
                    "new_txn_customer_name_2": new_txn_customer_name_2,
                    "new_txn_payer_name_2": new_txn_payer_name_2,
                    "new_txn_order_id_2": order_id,
                    "new_txn_payment_msg_2": "PAYMENT SUCCESSFUL",
                    "new_txn_rrn_2": str(callback_2_rrn),
                    "new_txn_auth_code_2": str(new_txn_auth_code_2),
                    "new_txn_date_1": new_txn_date_and_time_1,
                    "new_txn_date_2": new_txn_date_and_time_2
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
                    "new_txn_payment_mode_1": new_app_payment_mode_1,
                    "new_txn_payment_status_1": new_app_payment_status_1,
                    "new_txn_amount_1": str(new_app_amount_1).split(' ')[1],
                    "new_txn_settlement_status_1": new_app_settlement_status_1,
                    "new_txn_id_1": new_app_txn_id_1,
                    "new_txn_auth_code_1": str(new_txn_app_auth_code_1),
                    "new_txn_customer_name_1": new_app_customer_name_1,
                    "new_txn_payer_name_1": new_app_payer_name_1,
                    "new_txn_order_id_1": new_app_order_id_1,
                    "new_txn_payment_msg_1": new_app_payment_msg_1,
                    "new_txn_rrn_1": str(new_app_rrn_1),
                    "new_txn_payment_mode_2": new_app_payment_mode_2,
                    "new_txn_payment_status_2": new_app_payment_status_2,
                    "new_txn_amount_2": str(new_app_amount_2).split(' ')[1],
                    "new_txn_settlement_status_2": new_app_settlement_status_2,
                    "new_txn_id_2": new_app_txn_id_2,
                    "new_txn_customer_name_2": new_app_customer_name_2,
                    "new_txn_payer_name_2": new_app_payer_name_2,
                    "new_txn_order_id_2": new_app_order_id_2,
                    "new_txn_payment_msg_2": new_app_payment_msg_2,
                    "new_txn_rrn_2": str(new_app_rrn_2),
                    "new_txn_auth_code_2": str(new_txn_app_auth_code_2),
                    "new_txn_date_1": new_app_date_and_time_1,
                    "new_txn_date_2": new_app_date_and_time_2
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
                new_txn_date_1 = date_time_converter.db_datetime(new_txn_posting_date_1)
                new_txn_date_2 = date_time_converter.db_datetime(new_txn_posting_date_2)
                expected_api_values = {"new_pmt_status_1": "AUTHORIZED",
                                       "new_txn_amt_1": amount, "new_pmt_mode_1": "UPI",
                                       "new_pmt_state_1": "SETTLED",
                                       "new_rrn_1": str(callback_1_rrn),
                                       "new_settlement_status_1": "SETTLED",
                                       "new_acquirer_code_1": "HDFC",
                                       "new_txn_customer_name_1": new_txn_customer_name_1,
                                       "new_txn_payer_name_1": new_txn_payer_name_1,
                                       "new_order_id_1": order_id,
                                       "new_issuer_code_1": "HDFC",
                                       "new_txn_type_1": new_txn_type_1, "new_mid_1": mid,
                                       "new_tid_1": tid, "new_org_code_1": org_code,
                                       "new_device_serial_1": str(device_serial),
                                       "new_txn_auth_code_1": str(new_txn_auth_code_1),
                                       "new_pmt_status_2": "AUTHORIZED",
                                       "new_txn_amt_2": amount, "new_pmt_mode_2": "UPI",
                                       "new_pmt_state_2": "SETTLED",
                                       "new_rrn_2": str(callback_2_rrn),
                                       "new_settlement_status_2": "SETTLED",
                                       "new_acquirer_code_2": "HDFC",
                                       "new_txn_customer_name_2": new_txn_customer_name_2,
                                       "new_txn_payer_name_2": new_txn_payer_name_2,
                                       "new_order_id_2": order_id,
                                       "new_issuer_code_2": "HDFC",
                                       "new_txn_type_2": new_txn_type_2, "new_mid_2": mid,
                                       "new_tid_2": tid, "new_org_code_2": org_code,
                                       "new_txn_auth_code_2": str(new_txn_auth_code_2),
                                       "new_txn_date_1": new_txn_date_1,
                                       "new_txn_date_2": new_txn_date_2,
                                       "new_device_serial_2": str(device_serial)
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

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

                actual_api_values = {"new_pmt_status_1": new_txn_status_api_1,
                                     "new_txn_amt_1": new_txn_amount_api_1, "new_pmt_mode_1": new_payment_mode_api_1,
                                     "new_pmt_state_1": new_txn_state_api_1,
                                     "new_rrn_1": str(new_txn_rrn_api_1),
                                     "new_settlement_status_1": new_txn_settlement_status_api_1,
                                     "new_acquirer_code_1": new_txn_acquirer_code_api_1,
                                     "new_txn_customer_name_1": new_txn_customer_name_api_1,
                                     "new_txn_payer_name_1": new_txn_payer_name_api_1,
                                     "new_issuer_code_1": new_txn_issuer_code_api_1,
                                     "new_order_id_1": new_txn_order_id_api_1,
                                     "new_txn_type_1": new_txn_txn_type_api_1, "new_mid_1": new_txn_mid_api_1,
                                     "new_tid_1": new_txn_tid_api_1, "new_org_code_1": new_txn_orgCode_api_1,
                                     "new_device_serial_1": str(new_txn_device_serial_api_1),
                                     "new_txn_auth_code_1": str(new_txn_auth_code_api_1),
                                     "new_pmt_status_2": new_txn_status_api_2,
                                     "new_txn_amt_2": new_txn_amount_api_2, "new_pmt_mode_2": new_payment_mode_api_2,
                                     "new_pmt_state_2": new_txn_state_api_2,
                                     "new_rrn_2": str(new_txn_rrn_api_2),
                                     "new_settlement_status_2": new_txn_settlement_status_api_2,
                                     "new_acquirer_code_2": new_txn_acquirer_code_api_2,
                                     "new_issuer_code_2": new_txn_issuer_code_api_2,
                                     "new_txn_customer_name_2": new_txn_customer_name_api_2,
                                     "new_txn_payer_name_2": new_txn_payer_name_api_2,
                                     "new_order_id_2": new_txn_order_id_api_2,
                                     "new_txn_type_2": new_txn_type_api_2, "new_mid_2": new_txn_mid_api_2,
                                     "new_tid_2": new_txn_tid_api_2, "new_org_code_2": new_txn_orgCode_api_2,
                                     "new_txn_auth_code_2": str(new_txn_auth_code_api_2),
                                     "new_txn_date_1": date_time_converter.from_api_to_datetime_format(new_txn_date_api_1),
                                     "new_txn_date_2": date_time_converter.from_api_to_datetime_format(new_txn_date_api_2),
                                     "new_device_serial_2": str(new_txn_device_serial_api_2)
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
                    "new_pmt_status_1": "AUTHORIZED",
                    "new_pmt_state_1": "SETTLED",
                    "new_pmt_mode_1": "UPI",
                    "new_txn_amt_1": amount,
                    "new_upi_txn_status_1": "AUTHORIZED",
                    "new_settlement_status_1": "SETTLED",
                    "new_acquirer_code_1": "HDFC",
                    "new_bank_code_1": "HDFC",
                    "new_payment_gateway_1": "HDFC",
                    "new_txn_payer_name_1": new_txn_payer_name_1,
                    "new_txn_rrn_1": str(callback_1_rrn),
                    "new_upi_txn_type_db_1": "PAY_QR",
                    "new_upi_bank_code_db_1": "HDFC",
                    "new_upi_mc_id_db_1": upi_mc_id,
                    "new_txn_order_id_1": order_id,
                    "new_txn_device_serial_1": str(device_serial),
                    "new_pmt_status_2": "AUTHORIZED",
                    "new_pmt_state_2": "SETTLED",
                    "new_pmt_mode_2": "UPI",
                    "new_txn_amt_2": amount,
                    "new_upi_txn_status_2": "AUTHORIZED",
                    "new_settlement_status_2": "SETTLED",
                    "new_acquirer_code_2": "HDFC",
                    "new_bank_code_2": "HDFC",
                    "new_payment_gateway_2": "HDFC",
                    "new_upi_txn_type_db_2": "PAY_QR",
                    "new_upi_bank_code_db_2": "HDFC",
                    "new_upi_mc_id_db_2": upi_mc_id,
                    "new_txn_order_id_2": order_id,
                    "new_txn_device_serial_2": str(device_serial),
                    "new_txn_payer_name_2": new_txn_payer_name_2,
                    "new_txn_rrn_2": str(callback_2_rrn),
                    "new_txn_mid_1": mid,
                    "new_txn_tid_1": tid,
                    "new_txn_mid_2": mid,
                    "new_txn_tid_2": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

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
                    "new_pmt_status_1": new_txn_status_db_1,
                    "new_pmt_state_1": new_txn_state_db_1,
                    "new_pmt_mode_1": new_txn_payment_mode_db_1,
                    "new_txn_amt_1": new_txn_amount_db_1,
                    "new_upi_txn_status_1": new_txn_upi_status_db_1,
                    "new_settlement_status_1": new_txn_settlement_status_db_1,
                    "new_acquirer_code_1": new_txn_acquirer_code_db_1,
                    "new_bank_code_1": new_txn_bank_code_db_1,
                    "new_payment_gateway_1": new_txn_payment_gateway_db_1,
                    "new_txn_payer_name_1": new_txn_payer_name_1_db,
                    "new_txn_rrn_1": str(callback_1_rrn_db),
                    "new_upi_txn_type_db_1": new_txn_upi_txn_type_db_1,
                    "new_upi_bank_code_db_1": new_txn_upi_bank_code_db_1,
                    "new_upi_mc_id_db_1": new_txn_upi_mc_id_db_1,
                    "new_txn_order_id_1": new_txn_order_id_db_1,
                    "new_txn_device_serial_1": str(new_txn_device_serial_db_1),
                    "new_pmt_status_2": new_txn_status_db_2,
                    "new_pmt_state_2": new_txn_state_db_2,
                    "new_pmt_mode_2": new_txn_payment_mode_db_2,
                    "new_txn_amt_2": new_txn_amount_db_2,
                    "new_upi_txn_status_2": new_txn_upi_status_db_2,
                    "new_settlement_status_2": new_txn_settlement_status_db_2,
                    "new_acquirer_code_2": new_txn_acquirer_code_db_2,
                    "new_bank_code_2": new_txn_bank_code_db_2,
                    "new_payment_gateway_2": new_txn_payment_gateway_db_2,
                    "new_upi_txn_type_db_2": new_txn_upi_txn_type_db_2,
                    "new_upi_bank_code_db_2": new_txn_upi_bank_code_db_2,
                    "new_upi_mc_id_db_2": new_txn_upi_mc_id_db_2,
                    "new_txn_payer_name_2": new_txn_payer_name_2_db,
                    "new_txn_order_id_2": new_txn_order_id_db_2,
                    "new_txn_device_serial_2": str(new_txn_device_serial_db_2),
                    "new_txn_rrn_2": str(callback_2_rrn_db),
                    "new_txn_mid_1": new_txn_mid_db_1,
                    "new_txn_tid_1": new_txn_tid_db_1,
                    "new_txn_mid_2": new_txn_mid_db_2,
                    "new_txn_tid_2": new_txn_tid_db_2
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
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                actual_portal_values = {}
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
@pytest.mark.chargeSlipVal
def test_common_100_101_110():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_success_callback_before_qr_expiry_TID_Dep_HDFC_AutoRefund_Enabled
    Sub Feature Description: Performing two pure upi success callback via TID Dep HDFC before expiry the qr when autorefund is enabled
    TC naming code description:
    100: Payment Method
    101: UPI
    110: TC110
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

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            tid = result['tid'].values[0]
            mid = result['mid'].values[0]
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

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

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
            new_txn_type_1 = result['txn_type'].values[0]
            new_txn_auth_code_1 = result['auth_code'].values[0]
            new_txn_created_time_1 = result['created_time'].values[0]

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
            new_txn_type_2 = result['txn_type'].values[0]
            new_txn_auth_code_2 = result['auth_code'].values[0]
            new_txn_created_time_2 = result['created_time'].values[0]

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
                new_txn_date_and_time_1 = date_time_converter.to_app_format(new_txn_created_time_1)
                new_txn_date_and_time_2 = date_time_converter.to_app_format(new_txn_created_time_2)
                expected_app_values = {
                    "new_txn_payment_mode_1": "UPI",
                    "new_txn_payment_status_1": "AUTHORIZED",
                    "new_txn_amount_1": str(amount),
                    "new_txn_settlement_status_1": "SETTLED",
                    "new_txn_id_1": new_txn_id_1,
                    "new_txn_customer_name_1": new_txn_customer_name_1,
                    "new_txn_payer_name_1": new_txn_payer_name_1,
                    "new_txn_order_id_1": order_id,
                    "new_txn_payment_msg_1": "PAYMENT SUCCESSFUL",
                    "new_txn_rrn_1": str(callback_1_rrn),
                    "new_txn_auth_code_1": str(new_txn_auth_code_1),
                    "new_txn_payment_mode_2": "UPI",
                    "new_txn_payment_status_2": "REFUND_PENDING",
                    "new_txn_amount_2": str(amount),
                    "new_txn_settlement_status_2": "SETTLED",
                    "new_txn_id_2": new_txn_id_2,
                    "new_txn_customer_name_2": new_txn_customer_name_2,
                    "new_txn_payer_name_2": new_txn_payer_name_2,
                    "new_txn_order_id_2": order_id,
                    "new_txn_payment_msg_2": "PAYMENT SUCCESSFUL",
                    "new_txn_rrn_2": str(callback_2_rrn),
                    "new_txn_auth_code_2": str(new_txn_auth_code_2),
                    "new_txn_date_1": new_txn_date_and_time_1,
                    "new_txn_date_2": new_txn_date_and_time_2
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
                    "new_txn_payment_mode_1": new_app_payment_mode_1,
                    "new_txn_payment_status_1": new_app_payment_status_1,
                    "new_txn_amount_1": str(new_app_amount_1).split(' ')[1],
                    "new_txn_settlement_status_1": new_app_settlement_status_1,
                    "new_txn_id_1": new_app_txn_id_1,
                    "new_txn_auth_code_1": str(new_txn_app_auth_code_1),
                    "new_txn_customer_name_1": new_app_customer_name_1,
                    "new_txn_payer_name_1": new_app_payer_name_1,
                    "new_txn_order_id_1": new_app_order_id_1,
                    "new_txn_payment_msg_1": new_app_payment_msg_1,
                    "new_txn_rrn_1": str(new_app_rrn_1),
                    "new_txn_payment_mode_2": new_app_payment_mode_2,
                    "new_txn_payment_status_2": new_app_payment_status_2,
                    "new_txn_amount_2": str(new_app_amount_2).split(' ')[1],
                    "new_txn_settlement_status_2": new_app_settlement_status_2,
                    "new_txn_id_2": new_app_txn_id_2,
                    "new_txn_customer_name_2": new_app_customer_name_2,
                    "new_txn_payer_name_2": new_app_payer_name_2,
                    "new_txn_order_id_2": new_app_order_id_2,
                    "new_txn_payment_msg_2": new_app_payment_msg_2,
                    "new_txn_rrn_2": str(new_app_rrn_2),
                    "new_txn_auth_code_2": str(new_txn_app_auth_code_2),
                    "new_txn_date_1": new_app_date_and_time_1,
                    "new_txn_date_2": new_app_date_and_time_2
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
                new_txn_date_1 = date_time_converter.db_datetime(new_txn_created_time_1)
                new_txn_date_2 = date_time_converter.db_datetime(new_txn_created_time_2)
                expected_api_values = {"new_pmt_status_1": "AUTHORIZED",
                                       "new_txn_amt_1": amount, "new_pmt_mode_1": "UPI",
                                       "new_pmt_state_1": "SETTLED",
                                       "new_rrn_1": str(callback_1_rrn),
                                       "new_settlement_status_1": "SETTLED",
                                       "new_acquirer_code_1": "HDFC",
                                       "new_txn_customer_name_1": new_txn_customer_name_1,
                                       "new_txn_payer_name_1": new_txn_payer_name_1,
                                       "new_order_id_1": order_id,
                                       "new_issuer_code_1": "HDFC",
                                       "new_txn_type_1": new_txn_type_1, "new_mid_1": mid,
                                       "new_tid_1": tid, "new_org_code_1": org_code,
                                       "new_device_serial_1": str(device_serial),
                                       "new_txn_auth_code_1": str(new_txn_auth_code_1),
                                       "new_pmt_status_2": "REFUND_PENDING",
                                       "new_txn_amt_2": amount, "new_pmt_mode_2": "UPI",
                                       "new_pmt_state_2": "REFUND_PENDING",
                                       "new_rrn_2": str(callback_2_rrn),
                                       "new_settlement_status_2": "SETTLED",
                                       "new_acquirer_code_2": "HDFC",
                                       "new_txn_customer_name_2": new_txn_customer_name_2,
                                       "new_txn_payer_name_2": new_txn_payer_name_2,
                                       "new_order_id_2": order_id,
                                       "new_issuer_code_2": "HDFC",
                                       "new_txn_type_2": new_txn_type_2, "new_mid_2": mid,
                                       "new_tid_2": tid, "new_org_code_2": org_code,
                                       "new_txn_auth_code_2": str(new_txn_auth_code_2),
                                       "new_txn_date_1": new_txn_date_1,
                                       "new_txn_date_2": new_txn_date_2,
                                       "new_device_serial_2": str(device_serial)
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

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

                actual_api_values = {"new_pmt_status_1": new_txn_status_api_1,
                                     "new_txn_amt_1": new_txn_amount_api_1, "new_pmt_mode_1": new_payment_mode_api_1,
                                     "new_pmt_state_1": new_txn_state_api_1,
                                     "new_rrn_1": str(new_txn_rrn_api_1),
                                     "new_settlement_status_1": new_txn_settlement_status_api_1,
                                     "new_acquirer_code_1": new_txn_acquirer_code_api_1,
                                     "new_txn_customer_name_1": new_txn_customer_name_api_1,
                                     "new_txn_payer_name_1": new_txn_payer_name_api_1,
                                     "new_issuer_code_1": new_txn_issuer_code_api_1,
                                     "new_order_id_1": new_txn_order_id_api_1,
                                     "new_txn_type_1": new_txn_txn_type_api_1, "new_mid_1": new_txn_mid_api_1,
                                     "new_tid_1": new_txn_tid_api_1, "new_org_code_1": new_txn_orgCode_api_1,
                                     "new_device_serial_1": str(new_txn_device_serial_api_1),
                                     "new_txn_auth_code_1": str(new_txn_auth_code_api_1),
                                     "new_pmt_status_2": new_txn_status_api_2,
                                     "new_txn_amt_2": new_txn_amount_api_2, "new_pmt_mode_2": new_payment_mode_api_2,
                                     "new_pmt_state_2": new_txn_state_api_2,
                                     "new_rrn_2": str(new_txn_rrn_api_2),
                                     "new_settlement_status_2": new_txn_settlement_status_api_2,
                                     "new_acquirer_code_2": new_txn_acquirer_code_api_2,
                                     "new_issuer_code_2": new_txn_issuer_code_api_2,
                                     "new_txn_customer_name_2": new_txn_customer_name_api_2,
                                     "new_txn_payer_name_2": new_txn_payer_name_api_2,
                                     "new_order_id_2": new_txn_order_id_api_2,
                                     "new_txn_type_2": new_txn_type_api_2, "new_mid_2": new_txn_mid_api_2,
                                     "new_tid_2": new_txn_tid_api_2, "new_org_code_2": new_txn_orgCode_api_2,
                                     "new_txn_auth_code_2": str(new_txn_auth_code_api_2),
                                     "new_txn_date_1": date_time_converter.from_api_to_datetime_format(new_txn_date_api_1),
                                     "new_txn_date_2": date_time_converter.from_api_to_datetime_format(new_txn_date_api_2),
                                     "new_device_serial_2": str(new_txn_device_serial_api_2)
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
                    "new_pmt_status_1": "AUTHORIZED",
                    "new_pmt_state_1": "SETTLED",
                    "new_pmt_mode_1": "UPI",
                    "new_txn_amt_1": amount,
                    "new_upi_txn_status_1": "AUTHORIZED",
                    "new_settlement_status_1": "SETTLED",
                    "new_acquirer_code_1": "HDFC",
                    "new_bank_code_1": "HDFC",
                    "new_payment_gateway_1": "HDFC",
                    "new_txn_payer_name_1": new_txn_payer_name_1,
                    "new_txn_rrn_1": str(callback_1_rrn),
                    "new_upi_txn_type_db_1": "PAY_QR",
                    "new_upi_bank_code_db_1": "HDFC",
                    "new_upi_mc_id_db_1": upi_mc_id,
                    "new_txn_order_id_1": order_id,
                    "new_txn_device_serial_1": str(device_serial),
                    "new_pmt_status_2": "REFUND_PENDING",
                    "new_pmt_state_2": "REFUND_PENDING",
                    "new_pmt_mode_2": "UPI",
                    "new_txn_amt_2": amount,
                    "new_upi_txn_status_2": "REFUND_PENDING",
                    "new_settlement_status_2": "SETTLED",
                    "new_acquirer_code_2": "HDFC",
                    "new_bank_code_2": "HDFC",
                    "new_payment_gateway_2": "HDFC",
                    "new_upi_txn_type_db_2": "PAY_QR",
                    "new_upi_bank_code_db_2": "HDFC",
                    "new_upi_mc_id_db_2": upi_mc_id,
                    "new_txn_order_id_2": order_id,
                    "new_txn_device_serial_2": str(device_serial),
                    "new_txn_payer_name_2": new_txn_payer_name_2,
                    "new_txn_rrn_2": str(callback_2_rrn),
                    "new_txn_mid_1": mid,
                    "new_txn_tid_1": tid,
                    "new_txn_mid_2": mid,
                    "new_txn_tid_2": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

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
                    "new_pmt_status_1": new_txn_status_db_1,
                    "new_pmt_state_1": new_txn_state_db_1,
                    "new_pmt_mode_1": new_txn_payment_mode_db_1,
                    "new_txn_amt_1": new_txn_amount_db_1,
                    "new_upi_txn_status_1": new_txn_upi_status_db_1,
                    "new_settlement_status_1": new_txn_settlement_status_db_1,
                    "new_acquirer_code_1": new_txn_acquirer_code_db_1,
                    "new_bank_code_1": new_txn_bank_code_db_1,
                    "new_payment_gateway_1": new_txn_payment_gateway_db_1,
                    "new_txn_payer_name_1": new_txn_payer_name_1_db,
                    "new_txn_rrn_1": str(callback_1_rrn_db),
                    "new_upi_txn_type_db_1": new_txn_upi_txn_type_db_1,
                    "new_upi_bank_code_db_1": new_txn_upi_bank_code_db_1,
                    "new_upi_mc_id_db_1": new_txn_upi_mc_id_db_1,
                    "new_txn_order_id_1": new_txn_order_id_db_1,
                    "new_txn_device_serial_1": str(new_txn_device_serial_db_1),
                    "new_pmt_status_2": new_txn_status_db_2,
                    "new_pmt_state_2": new_txn_state_db_2,
                    "new_pmt_mode_2": new_txn_payment_mode_db_2,
                    "new_txn_amt_2": new_txn_amount_db_2,
                    "new_upi_txn_status_2": new_txn_upi_status_db_2,
                    "new_settlement_status_2": new_txn_settlement_status_db_2,
                    "new_acquirer_code_2": new_txn_acquirer_code_db_2,
                    "new_bank_code_2": new_txn_bank_code_db_2,
                    "new_payment_gateway_2": new_txn_payment_gateway_db_2,
                    "new_upi_txn_type_db_2": new_txn_upi_txn_type_db_2,
                    "new_upi_bank_code_db_2": new_txn_upi_bank_code_db_2,
                    "new_upi_mc_id_db_2": new_txn_upi_mc_id_db_2,
                    "new_txn_payer_name_2": new_txn_payer_name_2_db,
                    "new_txn_order_id_2": new_txn_order_id_db_2,
                    "new_txn_device_serial_2": str(new_txn_device_serial_db_2),
                    "new_txn_rrn_2": str(callback_2_rrn_db),
                    "new_txn_mid_1": new_txn_mid_db_1,
                    "new_txn_tid_1": new_txn_tid_db_1,
                    "new_txn_mid_2": new_txn_mid_db_2,
                    "new_txn_tid_2": new_txn_tid_db_2
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
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                actual_portal_values = {}
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
                new_txn_date_1, new_txn_time_1 = date_time_converter.to_chargeslip_format(new_txn_created_time_1)
                new_txn_date_2, new_txn_time_2 = date_time_converter.to_chargeslip_format(new_txn_created_time_2)
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
