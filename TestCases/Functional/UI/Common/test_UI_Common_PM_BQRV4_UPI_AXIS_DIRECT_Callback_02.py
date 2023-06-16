import random
import sys
import time
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, receipt_validator, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_177():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_2_Success_Callback_After_QR_Expiry_AutoRefund_Disabled_AXIS_DIRECT
    Sub Feature Description: Performing a pure bqrv4 upi 2 success callback via AXIS_DIRECT after qr expiry when autorefund is disabled
    TC naming code description: 100: Payment Method, 102: BQR, 177: TC177
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
        logger.debug(f"RESULT of updating DB setting active: {result}")

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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
            logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            bqr_merchant_config_id = result['id'].values[0]
            logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {bqr_merchant_config_id}")
            bqr_merchant_pan = result['merchant_pan'].values[0]
            logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {bqr_merchant_pan}")

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

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
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

            rrn_3 = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn_3}")
            ref_id_3 = '211115084892E01' + str(rrn_3)
            logger.debug(f"generated random ref_id is : {ref_id_3}")

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn_2} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': rrn_3,
                                                                 'gatewayTransactionId': ref_id_3})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            # data_buffer = ast.literal_eval(data_buffer)
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_3 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_3 : {txn_id_3}")
            customer_name_3 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_3 : {customer_name_3}")
            payer_name_3 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_3 : {payer_name_3}")
            org_code_txn_3 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_3 : {org_code_txn_3}")
            txn_type_3 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_3 : {txn_type_3}")
            auth_code_3 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_3 : {auth_code_3}")
            txn_created_time_3 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : txn_created_time_3 : {txn_created_time_3}")

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
                date_and_time_3 = date_time_converter.to_app_format(txn_created_time_3)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount)+".00",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount)+".00",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    # "auth_code_2": authid_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "pmt_mode_3": "UPI",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": str(amount)+".00",
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_3,
                    "order_id_3": order_id,
                    "pmt_msg_3": "PAYMENT SUCCESSFUL",
                    "date_3": date_and_time_3,
                    # "auth_code_2": authid_2,
                    "rrn_3": str(rrn_3),
                    "customer_name_3": customer_name_3,
                    "payer_name_3": payer_name_3,
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
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
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

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_3)
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_3}, {payment_status_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_3}, {app_date_and_time_3}")
                # app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_3}, {app_auth_code_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_3}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_txn_id_3}")
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_3}, {app_amount_3}")
                app_customer_name_3 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_3}, {app_customer_name_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_3}, {app_settlement_status_3}")
                app_payer_name_3 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_3}, {app_payer_name_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_3}, {app_payment_msg_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_3}, {app_order_id_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_3}")

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
                    "date_2": app_date_and_time_3,
                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "txn_id_3": app_txn_id_3,
                    "rrn_3": str(app_rrn_3),
                    "customer_name_3": app_customer_name_3,
                    "settle_status_3": app_settlement_status_3,
                    "payer_name_3": app_payer_name_3,
                    "order_id_3": app_order_id_3,
                    "pmt_msg_3": app_payment_msg_3,
                    # "auth_code_3": app_auth_code_3,
                    "date_3": app_date_and_time_3
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
                date_3 = date_time_converter.db_datetime(txn_created_time_3)
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
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": float(amount), "pmt_mode_3": "UPI",
                    "pmt_state_3": "SETTLED", "rrn_3": str(rrn_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "AXIS",
                    "issuer_code_3": "AXIS",
                    "order_id_3": order_id,
                    "txn_type_3": "CHARGE", "mid_3": mid, "tid_3": tid,
                    "org_code_3": org_code,
                    # "auth_code_3": authid_3,
                    "date_3": date_3,
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

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_3][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

                status_api_3 = response["status"]
                amount_api_3 = float(response["amount"])
                payment_mode_api_3 = response["paymentMode"]
                state_api_3 = response["states"][0]
                rrn_api_3 = response["rrNumber"]
                settlement_status_api_3 = response["settlementStatus"]
                issuer_code_api_3 = response["issuerCode"]
                acquirer_code_api_3 = response["acquirerCode"]
                orgCode_api_3 = response["orgCode"]
                mid_api_3 = response["mid"]
                tid_api_3 = response["tid"]
                txn_type_api_3 = response["txnType"]
                # auth_code_api_3 = response["authCode"]
                date_api_3 = response["createdTime"]
                order_id_api_3 = response["orderNumber"]

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
                    "pmt_status_3": status_api_3,
                    "txn_amt_3": float(amount_api_3), "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_2, "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "issuer_code_3": issuer_code_api_3,
                    "order_id_3": order_id_api_3,
                    "txn_type_3": txn_type_api_3, "mid_3": mid_api_3, "tid_3": tid_api_3,
                    "org_code_3": orgCode_api_3,
                    # "auth_code_3": auth_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_3),
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
                    "payment_gateway_2": "AXIS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "upi_txn_status_2": "AUTHORIZED",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "pmt_status_3": "AUTHORIZED",
                    "pmt_state_3": "SETTLED",
                    "pmt_mode_3": "UPI",
                    "rr_number_3": str(rrn_3),
                    # "auth_code_3": authid_2,
                    "txn_amt_3": float(amount),
                    "settle_status_3": "SETTLED",
                    "order_id_3": order_id,
                    "acquirer_code_3": "AXIS",
                    "bank_code_3": "AXIS",
                    "payment_gateway_3": "AXIS",
                    "mid_3": mid,
                    "tid_3": tid,
                    "upi_txn_status_3": "AUTHORIZED",
                    "upi_txn_type_3": "PAY_BQR",
                    "upi_bank_code_3": "AXIS_DIRECT",
                    "upi_mc_id_3": upi_mc_id,
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

                query = "select * from txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_3 = result["status"].iloc[0]
                payment_mode_db_3 = result["payment_mode"].iloc[0]
                amount_db_3 = float(result["amount"].iloc[0])
                state_db_3 = result["state"].iloc[0]
                payment_gateway_db_3 = result["payment_gateway"].iloc[0]
                acquirer_code_db_3 = result["acquirer_code"].iloc[0]
                bank_code_db_3 = result["bank_code"].iloc[0]
                settlement_status_db_3 = result["settlement_status"].iloc[0]
                tid_db_3 = result['tid'].values[0]
                mid_db_3 = result['mid'].values[0]
                order_id_db_3 = result['external_ref'].values[0]
                rr_number_db_3 = result['rr_number'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_3 = result["status"].iloc[0]
                upi_txn_type_db_3 = result["txn_type"].iloc[0]
                upi_bank_code_db_3 = result["bank_code"].iloc[0]
                upi_mc_id_db_3 = result["upi_mc_id"].iloc[0]

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
                    "pmt_status_3": status_db_3,
                    "pmt_state_3": state_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "rr_number_3": str(rr_number_db_3),
                    # "auth_code_3": auth_code_3,
                    "txn_amt_3": float(amount_db_3),
                    "settle_status_3": settlement_status_db_3,
                    "order_id_3": order_id_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "bank_code_3": bank_code_db_3,
                    "payment_gateway_3": payment_gateway_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "upi_txn_status_3": upi_status_db_3,
                    "upi_txn_type_3": upi_txn_type_db_3,
                    "upi_bank_code_3": upi_bank_code_db_3,
                    "upi_mc_id_3": upi_mc_id_db_3,
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
                date_and_time_portal_3 = date_time_converter.to_portal_format(txn_created_time_3)
                date_and_time_portal_2 = date_time_converter.to_portal_format(txn_created_time_2)
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{amount}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rr_number_db is None else rr_number_db,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{amount}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "auth_code_2": "-" if auth_code_2 is None else auth_code_2,
                    "rrn_2": "-" if rrn_2 is None else rrn_2,
                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "AUTHORIZED",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": f"{amount}.00",
                    "username_3": app_username,
                    "txn_id_3": txn_id_3,
                    "auth_code_3": "-" if auth_code_3 is None else auth_code_3,
                    "rrn_3": "-" if rrn_3 is None else rrn_3
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_3 = transaction_details[0]['Date & Time']
                logger.info(f"fetched date_time_3 from portal {date_time_3}")
                transaction_id_3 = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id_3 from portal {transaction_id_3}")
                total_amount_3 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total_amount_3 from portal {total_amount_3}")
                transaction_type_3 = transaction_details[0]['Type']
                logger.info(f"fetched txn_type_3 from portal {transaction_type_3}")
                auth_code_portal_3 = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code_3 from portal {auth_code_portal_3}")
                status_3 = transaction_details[0]['Status']
                logger.info(f"fetched status_3 {status_3}")
                username_3 = transaction_details[0]['Username']
                logger.info(f"fetched username_3 from portal {username_3}")
                rr_number_3 = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number_3 from portal {rr_number_3}")

                date_time_2 = transaction_details[1]['Date & Time']
                logger.info(f"fetched date_time_2 from portal {date_time_2}")
                transaction_id_2 = transaction_details[1]['Transaction ID']
                logger.info(f"fetched txn_id_2 from portal {transaction_id_2}")
                total_amount_2 = transaction_details[1]['Total Amount'].split()
                logger.debug(f"fetched total_amount_2 from portal {total_amount_2}")
                auth_code_portal_2 = transaction_details[1]['Auth Code']
                logger.debug(f"fetched auth_code_2 from portal {auth_code_portal_2}")
                rr_number_2 = transaction_details[1]['RR Number']
                logger.debug(f"fetched rr_number_2 from portal {rr_number_2}")
                transaction_type_2 = transaction_details[1]['Type']
                logger.info(f"fetched txn_type_2 from portal {transaction_type_2}")
                status_2 = transaction_details[1]['Status']
                logger.info(f"fetched status_2 {status_2}")
                username_2 = transaction_details[1]['Username']
                logger.info(f"fetched username_2 from portal {username_2}")

                date_time = transaction_details[2]['Date & Time']
                logger.info(f"fetched date time from portal {date_time}")
                transaction_id = transaction_details[2]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id}")
                total_amount = transaction_details[2]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount}")
                auth_code_portal = transaction_details[2]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number = transaction_details[2]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number}")
                transaction_type = transaction_details[2]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type}")
                status = transaction_details[2]['Status']
                logger.info(f"fetched status {status}")
                username = transaction_details[2]['Username']
                logger.info(f"fetched username from portal {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": status,
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": int(rr_number_2),
                    "date_time_3": date_time_3,
                    "pmt_state_3": status_3,
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "auth_code_3": auth_code_portal_3,
                    "rrn_3": int(rr_number_3)
                }

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
                txn_date_3, txn_time_3 = date_time_converter.to_chargeslip_format(txn_created_time_3)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(txn_created_time_2)
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2,
                }
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_2, {
                    "username": app_username, "password": app_password}, expected_charge_slip_values_2)
                expected_chargeslip_values_3 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_3),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'time': txn_time_3, 'date': txn_date_3
                }
                chargeslip_val_result_3 = receipt_validator.perform_charge_slip_validations(txn_id_3, {
                    "username": app_username, "password": app_password}, expected_chargeslip_values_3)

                if chargeslip_val_result_2 and chargeslip_val_result_3:
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
def test_common_100_102_211():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_1_UPI_AXIS_DIRECT_And_1_BQR_HDFC_Success_Callback_After_QR_Expiry_AutoRefund_Disabled
    Sub Feature Description: Performing a pure bqrv4 1 upi success callback via AXIS_DIRECT and 1 bqr success callback via HDFC, after qr expiry when autorefund is disabled
    TC naming code description: 100: Payment Method, 102: BQR, 211: TC211
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
        logger.debug(f"RESULT of updating DB setting active: {result}")

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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = 49.65
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
            username = result['username'].values[0]
            logger.debug(f"fetched username_3 : {username}")
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

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            # data_buffer = ast.literal_eval(data_buffer)
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_2 : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_2 : {customer_name_2}")
            username_2 = result['username'].values[0]
            logger.debug(f"fetched username_3 : {username_2}")
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

            rrn_3 = "RE" + txn_id.split('E')[1]
            logger.debug(f"generated random rrn number is : {rrn_3}")
            auth_code_3 = "AE" + txn_id.split('E')[1]
            logger.debug(f"generated random auth_code is : {auth_code_3}")

            logger.debug(
                f"Fetching Txn_id,Auth code,RRN from data base : Txn_id : {txn_id},"
                f" Auth code : {auth_code_3}, RRN : {rrn_3}")
            api_details = DBProcessor.get_api_details('callbackHDFC', request_body={
                "PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                "TXN_ID": txn_id,
                "AUTH_CODE": auth_code_3, "RRN": rrn_3,
                "MERCHANT_PAN": bqr_merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_3 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_3 : {txn_id_3}")
            customer_name_3 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_3 : {customer_name_3}")
            username_3 = result['username'].values[0]
            logger.debug(f"fetched username_3 : {username_3}")
            payer_name_3 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_3 : {payer_name_3}")
            org_code_txn_3 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_3 : {org_code_txn_3}")
            txn_type_3 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_3 : {txn_type_3}")
            auth_code_3 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_3 : {auth_code_3}")
            txn_created_time_3 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : txn_created_time_3 : {txn_created_time_3}")

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
                date_and_time_3 = date_time_converter.to_app_format(txn_created_time_3)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    # "auth_code_2": authid_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "pmt_mode_3": "BHARAT QR",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": str(amount),
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_3,
                    "order_id_3": order_id,
                    "payment_msg_3": "PAYMENT SUCCESSFUL",
                    "date_3": date_and_time_3,
                    "auth_code_3": auth_code_3,
                    "rrn_3": str(rrn_3),
                    # "customer_name_3": customer_name_3,
                    # "payer_name_3": payer_name_3,
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
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
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

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_3)
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_3}, {payment_status_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_3}, {app_date_and_time_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_3}, {app_auth_code_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_3}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_txn_id_3}")
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_3}, {app_amount_3}")
                # app_customer_name_3 = txn_history_page.fetch_customer_name_text()
                # logger.info(
                #     f"Fetching txn customer name from txn history for the txn : {txn_id_3}, {app_customer_name_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_3}, {app_settlement_status_3}")
                # app_payer_name_3 = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_3}, {app_payer_name_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_3}, {app_payment_msg_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_3}, {app_order_id_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_3}")

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
                    "date_2": app_date_and_time_3,
                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "txn_id_3": app_txn_id_3,
                    "rrn_3": str(app_rrn_3),
                    # "customer_name_3": app_customer_name_3,
                    "settle_status_3": app_settlement_status_3,
                    # "payer_name_3": app_payer_name_3,
                    "order_id_3": app_order_id_3,
                    "payment_msg_3": app_payment_msg_3,
                    "auth_code_3": app_auth_code_3,
                    "date_3": app_date_and_time_3
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
                date_3 = date_time_converter.db_datetime(txn_created_time_3)
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
                    "issuer_code_2": "AXIS", "customer_name_2": customer_name_2,
                    "order_id_2": order_id, "payer_name_2": payer_name_2,
                    "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    # "auth_code": authid_2,
                    "date_2": date_2,
                    "orig_txn_id_2": txn_id,
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": float(amount), "pmt_mode_3": "BHARATQR",
                    "pmt_state_3": "SETTLED", "rrn_3": str(rrn_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "issuer_code_3": "HDFC",
                    "order_id_3": order_id,
                    "txn_type_3": "CHARGE", "mid_3": hdfc_mid, "tid_3": hdfc_tid,
                    "org_code_3": org_code,
                    "auth_code_3": auth_code_3,
                    "date_3": date_3,
                    "orig_txn_id_3": txn_id,
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
                customer_name_api_2 = response["customerName"]
                payer_name_api_2 = response["payerName"]
                date_api_2 = response["createdTime"]
                order_id_api_2 = response["orderNumber"]
                orig_txn_id_api_2 = response["origTxnId"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_3][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_3 = response["status"]
                amount_api_3 = float(response["amount"])
                payment_mode_api_3 = response["paymentMode"]
                state_api_3 = response["states"][0]
                rrn_api_3 = response["rrNumber"]
                settlement_status_api_3 = response["settlementStatus"]
                issuer_code_api_3 = response["issuerCode"]
                acquirer_code_api_3 = response["acquirerCode"]
                orgCode_api_3 = response["orgCode"]
                mid_api_3 = response["mid"]
                tid_api_3 = response["tid"]
                txn_type_api_3 = response["txnType"]
                auth_code_api_3 = response["authCode"]
                date_api_3 = response["createdTime"]
                order_id_api_3 = response["orderNumber"]
                orig_txn_id_api_3 = response["origTxnId"]

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
                    "issuer_code_2": issuer_code_api_2, "customer_name_2": customer_name_api_2,
                    "order_id_2": order_id_api_2, "payer_name_2": payer_name_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    # "auth_code_2": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "orig_txn_id_2": orig_txn_id_api_2,
                    "pmt_status_3": status_api_3,
                    "txn_amt_3": float(amount_api_3), "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_2, "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "issuer_code_3": issuer_code_api_3,
                    "order_id_3": order_id_api_3,
                    "txn_type_3": txn_type_api_3, "mid_3": mid_api_3, "tid_3": tid_api_3,
                    "org_code_3": orgCode_api_3,
                    "auth_code_3": auth_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_3),
                    "orig_txn_id_3": orig_txn_id_api_3,
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
                    "payment_gateway_2": "AXIS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "orig_txn_id_2": txn_id,
                    "upi_txn_status_2": "AUTHORIZED",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "pmt_status_3": "AUTHORIZED",
                    "pmt_state_3": "SETTLED",
                    "pmt_mode_3": "BHARATQR",
                    "rr_number_3": str(rrn_3),
                    "auth_code_3": auth_code_3,
                    "txn_amt_3": float(amount),
                    "settle_status_3": "SETTLED",
                    "order_id_3": order_id,
                    "acquirer_code_3": "HDFC",
                    "bank_code_3": "HDFC",
                    "payment_gateway_3": "HDFC",
                    "mid_3": hdfc_mid,
                    "tid_3": hdfc_tid,
                    "orig_txn_id_3": txn_id,
                    "bqr_pmt_state_3": "SETTLED",
                    "bqr_txn_amt_3": float(amount),
                    "bqr_txn_type_3": "DYNAMIC_QR", "bqr_terminal_info_id_3": terminal_info_id,
                    "bqr_bank_code_3": "HDFC",
                    "bqr_merchant_config_id_3": bqr_merchant_config_id, "bqr_txn_primary_id_3": txn_id_3,
                    "bqr_org_code_3": org_code,
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
                orig_txn_id_db_2 = result['orig_txn_id'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_3 = result["status"].iloc[0]
                payment_mode_db_3 = result["payment_mode"].iloc[0]
                amount_db_3 = float(result["amount"].iloc[0])
                state_db_3 = result["state"].iloc[0]
                payment_gateway_db_3 = result["payment_gateway"].iloc[0]
                acquirer_code_db_3 = result["acquirer_code"].iloc[0]
                bank_code_db_3 = result["bank_code"].iloc[0]
                settlement_status_db_3 = result["settlement_status"].iloc[0]
                tid_db_3 = result['tid'].values[0]
                mid_db_3 = result['mid'].values[0]
                order_id_db_3 = result['external_ref'].values[0]
                rr_number_db_3 = result['rr_number'].values[0]
                auth_code_db_3 = result['auth_code'].values[0]
                orig_txn_id_db_3 = result['orig_txn_id'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_3 = result["status_code"].iloc[0]
                bqr_state_db_3 = result["state"].iloc[0]
                bqr_amount_db_3 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_3 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_3 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_3 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_3 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_3 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_3 = result['org_code'].values[0]

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
                    "orig_txn_id_2": orig_txn_id_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "pmt_status_3": status_db_3,
                    "pmt_state_3": state_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "rr_number_3": str(rr_number_db_3),
                    "auth_code_3": auth_code_db_3,
                    "txn_amt_3": float(amount_db_3),
                    "settle_status_3": settlement_status_db_3,
                    "order_id_3": order_id_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "bank_code_3": bank_code_db_3,
                    "payment_gateway_3": payment_gateway_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "orig_txn_id_3": orig_txn_id_db_3,
                    "bqr_pmt_state_3": bqr_state_db_3,
                    "bqr_txn_amt_3": bqr_amount_db_3,
                    "bqr_txn_type_3": bqr_txn_type_db_3, "bqr_terminal_info_id_3": bqr_terminal_info_id_db_3,
                    "bqr_bank_code_3": bqr_bank_code_db_3,
                    "bqr_merchant_config_id_3": bqr_merchant_config_id_db_3,
                    "bqr_txn_primary_id_3": bqr_txn_primary_id_db_3,
                    "bqr_org_code_3": bqr_org_code_db_3,
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
                date_and_time_portal_3 = date_time_converter.to_portal_format(txn_created_time_3)
                date_and_time_portal_2 = date_time_converter.to_portal_format(txn_created_time_2)
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "AUTHORIZED",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": f"{str(amount)}",
                    "username_3": username_3,
                    "txn_id_3": txn_id_3,
                    "rrn": rrn_3,
                    # "auth_code": auth_code_3,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}",
                    "username_2": username_2,
                    "txn_id_2": txn_id_2,
                    "rrn": rrn_2,
                    "auth_code": auth_code_2,

                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}",
                    "username": username,
                    "txn_id": txn_id,
                    "auth_code": auth_code
                    # "rrn": rrn
                }
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_3 = transaction_details[1]['Date & Time']
                transaction_id_3 = transaction_details[1]['Transaction ID']
                total_amount_3 = transaction_details[1]['Total Amount'].split()
                transaction_type_3 = transaction_details[1]['Type']
                status_3 = transaction_details[1]['Status']
                username_3 = transaction_details[1]['Username']
                auth_code_portal_3 = transaction_details[1]['Auth Code']

                date_time_2 = transaction_details[2]['Date & Time']
                transaction_id_2 = transaction_details[2]['Transaction ID']
                total_amount_2 = transaction_details[2]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[2]['Auth Code']
                transaction_type_2 = transaction_details[2]['Type']
                status_2 = transaction_details[2]['Status']
                username_2 = transaction_details[2]['Username']

                date_time = transaction_details[3]['Date & Time']
                transaction_id = transaction_details[3]['Transaction ID']
                total_amount = transaction_details[3]['Total Amount'].split()
                auth_code_portal = transaction_details[3]['Auth Code']
                rr_number = transaction_details[3]['RR Number']
                transaction_type = transaction_details[3]['Type']
                status = transaction_details[3]['Status']
                username = transaction_details[3]['Username']

                actual_portal_values = {

                    "date_time_3": date_time_3,
                    "pmt_state_3": status_3,
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "rrn": rrn_3,
                    # "auth_code": auth_code_portal_3,

                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn": rrn_2,
                    "auth_code": auth_code_portal_2,

                    "date_time": date_time,
                    "pmt_state": status,
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal
                    # "rrn": rr_number
                }

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
                txn_date_3, txn_time_3 = date_time_converter.to_chargeslip_format(txn_created_time_3)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(txn_created_time_2)

                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount), 'date': txn_date_2,
                    'time': txn_time_2,
                }

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_2, {
                    "username": app_username, "password": app_password}, expected_charge_slip_values_2)

                expected_chargeslip_values_3 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_3),
                    'BASE AMOUNT:': "Rs." + str(amount), 'time': txn_time_3, 'date': txn_date_3,
                    'AUTH CODE': auth_code_3
                }

                chargeslip_val_result_3 = receipt_validator.perform_charge_slip_validations(txn_id_3, {
                    "username": app_username, "password": app_password}, expected_chargeslip_values_3)

                if chargeslip_val_result_2 and chargeslip_val_result_3:
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
def test_common_100_102_212():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_1_UPI_AXIS_DIRECT_And_1_BQR_HDFC_Success_Callback_After_QR_Expiry_AutoRefund_Enabled
    Sub Feature Description: Performing a pure bqrv4 1 upi success callback via AXIS_DIRECT and 1 bqr success callback via HDFC, after qr expiry when autorefund is enabled
    TC naming code description: 100: Payment Method, 102: BQR, 212: TC212
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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = 49.65
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
            time.sleep(62)

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
            username = result['username'].values[0]
            logger.debug(f"fetched username_1 : {username}")
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

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            # data_buffer = ast.literal_eval(data_buffer)
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_2 : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_2 : {customer_name_2}")
            username_2 = result['username'].values[0]
            logger.debug(f"fetched username_1 : {username_2}")
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

            rrn_3 = "RE" + txn_id.split('E')[1]
            logger.debug(f"generated random rrn number is : {rrn_3}")
            auth_code_3 = "AE" + txn_id.split('E')[1]
            logger.debug(f"generated random auth_code is : {auth_code_3}")

            logger.debug(
                f"Fetching Txn_id,Auth code,RRN from data base : Txn_id : {txn_id},"
                f" Auth code : {auth_code_3}, RRN : {rrn_3}")
            api_details = DBProcessor.get_api_details('callbackHDFC', request_body={
                "PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                "TXN_ID": txn_id,
                "AUTH_CODE": auth_code_3, "RRN": rrn_3,
                "MERCHANT_PAN": bqr_merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_3 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_3 : {txn_id_3}")
            customer_name_3 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_3 : {customer_name_3}")
            username_3 = result['username'].values[0]
            logger.debug(f"fetched username_1 : {username_3}")
            payer_name_3 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_3 : {payer_name_3}")
            org_code_txn_3 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_3 : {org_code_txn_3}")
            txn_type_3 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_3 : {txn_type_3}")
            auth_code_3 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_3 : {auth_code_3}")
            txn_created_time_3 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : txn_created_time_3 : {txn_created_time_3}")

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
                date_and_time_3 = date_time_converter.to_app_format(txn_created_time_3)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    # "auth_code_2": authid_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "pmt_mode_3": "BHARAT QR",
                    "pmt_status_3": "REFUND_PENDING",
                    "txn_amt_3": "{:.2f}".format(amount),
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_3,
                    "order_id_3": order_id,
                    "payment_msg_3": "PAYMENT SUCCESSFUL",
                    "date_3": date_and_time_3,
                    "auth_code_3": auth_code_3,
                    "rrn_3": str(rrn_3),
                    # "customer_name_3": customer_name_3,
                    # "payer_name_3": payer_name_3,
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
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
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

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_3)
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_3}, {payment_status_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_3}, {app_date_and_time_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_3}, {app_auth_code_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_3}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_txn_id_3}")
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_3}, {app_amount_3}")
                # app_customer_name_3 = txn_history_page.fetch_customer_name_text()
                # logger.info(
                #     f"Fetching txn customer name from txn history for the txn : {txn_id_3}, {app_customer_name_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_3}, {app_settlement_status_3}")
                # app_payer_name_3 = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_3}, {app_payer_name_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_3}, {app_payment_msg_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_3}, {app_order_id_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_3}")

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
                    "date_2": app_date_and_time_3,
                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "txn_id_3": app_txn_id_3,
                    "rrn_3": str(app_rrn_3),
                    # "customer_name_3": app_customer_name_3,
                    "settle_status_3": app_settlement_status_3,
                    # "payer_name_3": app_payer_name_3,
                    "order_id_3": app_order_id_3,
                    "payment_msg_3": app_payment_msg_3,
                    "auth_code_3": app_auth_code_3,
                    "date_3": app_date_and_time_3
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
                date_3 = date_time_converter.db_datetime(txn_created_time_3)
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
                    "issuer_code_2": "AXIS", "customer_name_2": customer_name_2,
                    "order_id_2": order_id, "payer_name_2": payer_name_2,
                    "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    # "auth_code": authid_2,
                    "date_2": date_2,
                    "orig_txn_id_2": txn_id,
                    "pmt_status_3": "REFUND_PENDING",
                    "txn_amt_3": float(amount), "pmt_mode_3": "BHARATQR",
                    "pmt_state_3": "REFUND_PENDING", "rrn_3": str(rrn_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "issuer_code_3": "HDFC",
                    "order_id_3": order_id,
                    "txn_type_3": "CHARGE", "mid_3": hdfc_mid, "tid_3": hdfc_tid,
                    "org_code_3": org_code,
                    "auth_code_3": auth_code_3,
                    "date_3": date_3,
                    "orig_txn_id_3": txn_id,
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
                customer_name_api_2 = response["customerName"]
                payer_name_api_2 = response["payerName"]
                date_api_2 = response["createdTime"]
                order_id_api_2 = response["orderNumber"]
                orig_txn_id_api_2 = response["origTxnId"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_3][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_3 = response["status"]
                amount_api_3 = float(response["amount"])
                payment_mode_api_3 = response["paymentMode"]
                state_api_3 = response["states"][0]
                rrn_api_3 = response["rrNumber"]
                settlement_status_api_3 = response["settlementStatus"]
                issuer_code_api_3 = response["issuerCode"]
                acquirer_code_api_3 = response["acquirerCode"]
                orgCode_api_3 = response["orgCode"]
                mid_api_3 = response["mid"]
                tid_api_3 = response["tid"]
                txn_type_api_3 = response["txnType"]
                auth_code_api_3 = response["authCode"]
                date_api_3 = response["createdTime"]
                order_id_api_3 = response["orderNumber"]
                orig_txn_id_api_3 = response["origTxnId"]

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
                    "issuer_code_2": issuer_code_api_2, "customer_name_2": customer_name_api_2,
                    "order_id_2": order_id_api_2, "payer_name_2": payer_name_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    # "auth_code_2": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "orig_txn_id_2": orig_txn_id_api_2,
                    "pmt_status_3": status_api_3,
                    "txn_amt_3": float(amount_api_3), "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_2, "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "issuer_code_3": issuer_code_api_3,
                    "order_id_3": order_id_api_3,
                    "txn_type_3": txn_type_api_3, "mid_3": mid_api_3, "tid_3": tid_api_3,
                    "org_code_3": orgCode_api_3,
                    "auth_code_3": auth_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_3),
                    "orig_txn_id_3": orig_txn_id_api_3,
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
                    "orig_txn_id_2": txn_id,
                    "upi_txn_status_2": "REFUND_PENDING",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "pmt_status_3": "REFUND_PENDING",
                    "pmt_state_3": "REFUND_PENDING",
                    "pmt_mode_3": "BHARATQR",
                    "rr_number_3": str(rrn_3),
                    "auth_code_3": auth_code_3,
                    "txn_amt_3": float(amount),
                    "settle_status_3": "SETTLED",
                    "order_id_3": order_id,
                    "acquirer_code_3": "HDFC",
                    "bank_code_3": "HDFC",
                    "payment_gateway_3": "HDFC",
                    "mid_3": hdfc_mid,
                    "tid_3": hdfc_tid,
                    "orig_txn_id_3": txn_id,
                    "bqr_pmt_state_3": "REFUND_PENDING",
                    "bqr_txn_amt_3": float(amount),
                    "bqr_txn_type_3": "DYNAMIC_QR", "bqr_terminal_info_id_3": terminal_info_id,
                    "bqr_bank_code_3": "HDFC",
                    "bqr_merchant_config_id_3": bqr_merchant_config_id, "bqr_txn_primary_id_3": txn_id_3,
                    "bqr_org_code_3": org_code,
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
                orig_txn_id_db_2 = result['orig_txn_id'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_3 = result["status"].iloc[0]
                payment_mode_db_3 = result["payment_mode"].iloc[0]
                amount_db_3 = float(result["amount"].iloc[0])
                state_db_3 = result["state"].iloc[0]
                payment_gateway_db_3 = result["payment_gateway"].iloc[0]
                acquirer_code_db_3 = result["acquirer_code"].iloc[0]
                bank_code_db_3 = result["bank_code"].iloc[0]
                settlement_status_db_3 = result["settlement_status"].iloc[0]
                tid_db_3 = result['tid'].values[0]
                mid_db_3 = result['mid'].values[0]
                order_id_db_3 = result['external_ref'].values[0]
                rr_number_db_3 = result['rr_number'].values[0]
                auth_code_db_3 = result['auth_code'].values[0]
                orig_txn_id_db_3 = result['orig_txn_id'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_3 = result["status_code"].iloc[0]
                bqr_state_db_3 = result["state"].iloc[0]
                bqr_amount_db_3 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_3 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_3 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_3 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_3 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_3 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_3 = result['org_code'].values[0]

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
                    "orig_txn_id_2": orig_txn_id_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "pmt_status_3": status_db_3,
                    "pmt_state_3": state_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "rr_number_3": str(rr_number_db_3),
                    "auth_code_3": auth_code_db_3,
                    "txn_amt_3": float(amount_db_3),
                    "settle_status_3": settlement_status_db_3,
                    "order_id_3": order_id_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "bank_code_3": bank_code_db_3,
                    "payment_gateway_3": payment_gateway_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "orig_txn_id_3": orig_txn_id_db_3,
                    "bqr_pmt_state_3": bqr_state_db_3,
                    "bqr_txn_amt_3": bqr_amount_db_3,
                    "bqr_txn_type_3": bqr_txn_type_db_3, "bqr_terminal_info_id_3": bqr_terminal_info_id_db_3,
                    "bqr_bank_code_3": bqr_bank_code_db_3,
                    "bqr_merchant_config_id_3": bqr_merchant_config_id_db_3,
                    "bqr_txn_primary_id_3": bqr_txn_primary_id_db_3,
                    "bqr_org_code_3": bqr_org_code_db_3,
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
                date_and_time_portal_3 = date_time_converter.to_portal_format(txn_created_time_3)
                date_and_time_portal_2 = date_time_converter.to_portal_format(txn_created_time_2)
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {

                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "REFUND_PENDING",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": f"{str(amount)}",
                    "username_3": username_3,
                    "txn_id_3": txn_id_3,
                    "rrn": rrn_3,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}",
                    "username_2": username_2,
                    "txn_id_2": txn_id_2,
                    "auth_code": auth_code_2,
                    "rrn": rrn_2,

                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}",
                    "username": username,
                    "txn_id": txn_id
                    # "auth_code": auth_code
                    # "rrn": rrn
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_3 = transaction_details[1]['Date & Time']
                transaction_id_3 = transaction_details[1]['Transaction ID']
                total_amount_3 = transaction_details[1]['Total Amount'].split()
                transaction_type_3 = transaction_details[1]['Type']
                status_3 = transaction_details[1]['Status']
                username_3 = transaction_details[1]['Username']
                rr_number_3 = transaction_details[3]['RR Number']
                auth_code_portal_3 = transaction_details[1]['Auth Code']

                date_time_2 = transaction_details[2]['Date & Time']
                transaction_id_2 = transaction_details[2]['Transaction ID']
                total_amount_2 = transaction_details[2]['Total Amount'].split()
                transaction_type_2 = transaction_details[2]['Type']
                status_2 = transaction_details[2]['Status']
                username_2 = transaction_details[2]['Username']

                date_time = transaction_details[3]['Date & Time']
                transaction_id = transaction_details[3]['Transaction ID']
                total_amount = transaction_details[3]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[3]['RR Number']
                transaction_type = transaction_details[3]['Type']
                status = transaction_details[3]['Status']
                username = transaction_details[3]['Username']

                actual_portal_values = {
                    "date_time_3": date_time_3,
                    "pmt_state_3": status_3,
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "rrn": rr_number_3,
                    # "auth_code": auth_code_portal_3

                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code": auth_code_2,
                    "rrn": rrn_2,

                    "date_time": date_time,
                    "pmt_state": status,
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id
                    # "auth_code": auth_code_portal
                    # "rrn": rrn
                }

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
def test_common_100_102_247():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_2_Failed_Callback_After_QR_Expiry_AutoRefund_Disabled_AXIS_DIRECT
    Sub Feature Description: Performing a bqrv4 upi 2 failed callback via AXIS_DIRECT after qr expiry when autorefund is disabled
    TC naming code description: 100: Payment Method, 102: BQR, 247: TC247
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
        logger.debug(f"RESULT of updating DB setting active: {result}")

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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
            time.sleep(65)

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
            username = result['username'].values[0]
            logger.info(f"fetched username {username}")
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

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            rrn_3 = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn_3}")
            ref_id_3 = '211115084892E01' + str(rrn_3)
            logger.debug(f"generated random ref_id is : {ref_id_3}")

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn_2} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_failed_curl',
                                                      curl_data={'merchantTransactionId': txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': rrn_3,
                                                                 'gatewayTransactionId': ref_id_3})
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

            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

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
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time,
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
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
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
                date = date_time_converter.db_datetime(created_time)
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
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": username,
                    "txn_id": txn_id,
                    "rrn": rr_number_db
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.info(f"fetched date time from portal {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type}")
                status = transaction_details[0]['Status']
                logger.info(f"fetched status {status}")
                username = transaction_details[0]['Username']
                logger.info(f"fetched username from portal {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": status,
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number
                }

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
def test_common_100_102_248():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_1_UPI_AXIS_DIRECT_and_1_BQR_HDFC_Success_Callback_Before_QR_Expiry_AutoRefund_Disabled
    Sub Feature Description: Performing a pure bqrv4 1 upi success callback via AXIS_DIRECT and 1 bqr success callback
    via HDFC, before qr expiry when autorefund is disabled
    TC naming code description: 100: Payment Method, 102: BQR, 248: TC248
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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(401, 1000)
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

            rrn_2 = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn_2}")
            ref_id_2 = '211115084892E01' + str(rrn_2)
            logger.debug(f"generated random ref_id is : {ref_id_2}")

            logger.debug(f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn_2} in the curl_data")
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

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_2 : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_2 : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_2 : {payer_name_2}")
            username_2 = result['username'].values[0]
            logger.info(f"fetched username_2 from db {username_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_2 : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_2 : {txn_type_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_2 : {auth_code_2}")
            txn_created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : txn_created_time_2 : {txn_created_time_2}")

            rrn_3 = "RE" + txn_id.split('E')[1]
            logger.debug(f"generated random rrn number is : {rrn_3}")
            auth_code_3 = "AE" + txn_id.split('E')[1]
            logger.debug(f"generated random auth_code is : {auth_code_3}")

            logger.debug(
                f"Fetching Txn_id,Auth code,RRN from data base : Txn_id : {txn_id},"
                f" Auth code : {auth_code_3}, RRN : {rrn_3}")
            api_details = DBProcessor.get_api_details('callbackHDFC', request_body={
                "PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                "TXN_ID": txn_id,
                "AUTH_CODE": auth_code_3, "RRN": rrn_3,
                "MERCHANT_PAN": bqr_merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_3 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_3 : {txn_id_3}")
            customer_name_3 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_3 : {customer_name_3}")
            payer_name_3 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_3 : {payer_name_3}")
            org_code_txn_3 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_3 : {org_code_txn_3}")
            txn_type_3 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_3 : {txn_type_3}")
            auth_code_3 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_3 : {auth_code_3}")
            txn_created_time_3 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : txn_created_time_3 : {txn_created_time_3}")

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
                date_and_time_2 = date_time_converter.to_app_format(txn_created_time_2)
                date_and_time_3 = date_time_converter.to_app_format(txn_created_time_3)
                expected_app_values = {
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    # "auth_code_2": authid_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "pmt_mode_3": "BHARAT QR",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": str(amount)+".00",
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_3,
                    "order_id_3": order_id,
                    "payment_msg_3": "PAYMENT SUCCESSFUL",
                    "date_3": date_and_time_3,
                    "auth_code_3": auth_code_3,
                    "rrn_3": str(rrn_3),
                    # "customer_name_3": customer_name_3,
                    # "payer_name_3": payer_name_3,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
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
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
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

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_3)
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_3}, {payment_status_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_3}, {app_date_and_time_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_3}, {app_auth_code_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_3}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_txn_id_3}")
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_3}, {app_amount_3}")
                # app_customer_name_3 = txn_history_page.fetch_customer_name_text()
                # logger.info(
                #     f"Fetching txn customer name from txn history for the txn : {txn_id_3}, {app_customer_name_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_3}, {app_settlement_status_3}")
                # app_payer_name_3 = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_3}, {app_payer_name_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_3}, {app_payment_msg_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_3}, {app_order_id_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_3}")

                actual_app_values = {
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
                    "date_2": app_date_and_time_3,
                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "txn_id_3": app_txn_id_3,
                    "rrn_3": str(app_rrn_3),
                    # "customer_name_3": app_customer_name_3,
                    "settle_status_3": app_settlement_status_3,
                    # "payer_name_3": app_payer_name_3,
                    "order_id_3": app_order_id_3,
                    "payment_msg_3": app_payment_msg_3,
                    "auth_code_3": app_auth_code_3,
                    "date_3": app_date_and_time_3
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
                date_2 = date_time_converter.db_datetime(txn_created_time_2)
                date_3 = date_time_converter.db_datetime(txn_created_time_3)
                expected_api_values = {
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "issuer_code_2": "AXIS", "customer_name_2": customer_name_2,
                    "order_id_2": order_id, "payer_name_2": payer_name_2,
                    "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    # "auth_code": authid_2,
                    "date_2": date_2,
                    # "orig_txn_id_2": txn_id,
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": float(amount), "pmt_mode_3": "BHARATQR",
                    "pmt_state_3": "SETTLED", "rrn_3": str(rrn_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "issuer_code_3": "HDFC",
                    "order_id_3": order_id,
                    "txn_type_3": "CHARGE", "mid_3": hdfc_mid, "tid_3": hdfc_tid,
                    "org_code_3": org_code,
                    "auth_code_3": auth_code_3,
                    "date_3": date_3,
                    "orig_txn_id_3": txn_id,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

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
                customer_name_api_2 = response["customerName"]
                payer_name_api_2 = response["payerName"]
                date_api_2 = response["createdTime"]
                order_id_api_2 = response["orderNumber"]
                # orig_txn_id_api_2 = response["origTxnId"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_3][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_3 = response["status"]
                amount_api_3 = float(response["amount"])
                payment_mode_api_3 = response["paymentMode"]
                state_api_3 = response["states"][0]
                rrn_api_3 = response["rrNumber"]
                settlement_status_api_3 = response["settlementStatus"]
                issuer_code_api_3 = response["issuerCode"]
                acquirer_code_api_3 = response["acquirerCode"]
                orgCode_api_3 = response["orgCode"]
                mid_api_3 = response["mid"]
                tid_api_3 = response["tid"]
                txn_type_api_3 = response["txnType"]
                auth_code_api_3 = response["authCode"]
                date_api_3 = response["createdTime"]
                order_id_api_3 = response["orderNumber"]
                orig_txn_id_api_3 = response["origTxnId"]

                actual_api_values = {
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": float(amount_api_2), "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2, "customer_name_2": customer_name_api_2,
                    "order_id_2": order_id_api_2, "payer_name_2": payer_name_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    # "auth_code_2": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    # "orig_txn_id_2": orig_txn_id_api_2,
                    "pmt_status_3": status_api_3,
                    "txn_amt_3": float(amount_api_3), "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_2, "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "issuer_code_3": issuer_code_api_3,
                    "order_id_3": order_id_api_3,
                    "txn_type_3": txn_type_api_3, "mid_3": mid_api_3, "tid_3": tid_api_3,
                    "org_code_3": orgCode_api_3,
                    "auth_code_3": auth_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_3),
                    "orig_txn_id_3": orig_txn_id_api_3,
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
                    "payment_gateway_2": "AXIS",
                    "mid_2": mid,
                    "tid_2": tid,
                    # "orig_txn_id_2": txn_id,
                    "upi_txn_status_2": "AUTHORIZED",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "pmt_status_3": "AUTHORIZED",
                    "pmt_state_3": "SETTLED",
                    "pmt_mode_3": "BHARATQR",
                    "rr_number_3": str(rrn_3),
                    "auth_code_3": auth_code_3,
                    "txn_amt_3": float(amount),
                    "settle_status_3": "SETTLED",
                    "order_id_3": order_id,
                    "acquirer_code_3": "HDFC",
                    "bank_code_3": "HDFC",
                    "payment_gateway_3": "HDFC",
                    "mid_3": hdfc_mid,
                    "tid_3": hdfc_tid,
                    "orig_txn_id_3": txn_id,
                    "bqr_pmt_state_3": "SETTLED",
                    "bqr_txn_amt_3": float(amount),
                    "bqr_txn_type_3": "DYNAMIC_QR", "bqr_terminal_info_id_3": terminal_info_id,
                    "bqr_bank_code_3": "HDFC",
                    "bqr_merchant_config_id_3": bqr_merchant_config_id, "bqr_txn_primary_id_3": txn_id_3,
                    "bqr_org_code_3": org_code,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

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
                orig_txn_id_db_2 = result['orig_txn_id'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_3 = result["status"].iloc[0]
                payment_mode_db_3 = result["payment_mode"].iloc[0]
                amount_db_3 = float(result["amount"].iloc[0])
                state_db_3 = result["state"].iloc[0]
                payment_gateway_db_3 = result["payment_gateway"].iloc[0]
                acquirer_code_db_3 = result["acquirer_code"].iloc[0]
                bank_code_db_3 = result["bank_code"].iloc[0]
                settlement_status_db_3 = result["settlement_status"].iloc[0]
                tid_db_3 = result['tid'].values[0]
                mid_db_3 = result['mid'].values[0]
                order_id_db_3 = result['external_ref'].values[0]
                rr_number_db_3 = result['rr_number'].values[0]
                auth_code_db_3 = result['auth_code'].values[0]
                orig_txn_id_db_3 = result['orig_txn_id'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_3 = result["status_code"].iloc[0]
                bqr_state_db_3 = result["state"].iloc[0]
                bqr_amount_db_3 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_3 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_3 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_3 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_3 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_3 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_3 = result['org_code'].values[0]

                actual_db_values = {
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
                    # "orig_txn_id_2": orig_txn_id_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "pmt_status_3": status_db_3,
                    "pmt_state_3": state_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "rr_number_3": str(rr_number_db_3),
                    "auth_code_3": auth_code_db_3,
                    "txn_amt_3": float(amount_db_3),
                    "settle_status_3": settlement_status_db_3,
                    "order_id_3": order_id_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "bank_code_3": bank_code_db_3,
                    "payment_gateway_3": payment_gateway_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "orig_txn_id_3": orig_txn_id_db_3,
                    "bqr_pmt_state_3": bqr_state_db_3,
                    "bqr_txn_amt_3": bqr_amount_db_3,
                    "bqr_txn_type_3": bqr_txn_type_db_3, "bqr_terminal_info_id_3": bqr_terminal_info_id_db_3,
                    "bqr_bank_code_3": bqr_bank_code_db_3,
                    "bqr_merchant_config_id_3": bqr_merchant_config_id_db_3,
                    "bqr_txn_primary_id_3": bqr_txn_primary_id_db_3,
                    "bqr_org_code_3": bqr_org_code_db_3,
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
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time_2)
                date_and_time_portal_2 = date_time_converter.to_portal_format(txn_created_time_3)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id_2,
                    "auth_code": "-" if auth_code_2 is None else auth_code_2,
                    "rrn": rrn_2,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_3,
                    "auth_code_2": "-" if auth_code_3 is None else auth_code_3,
                    "rrn_2": "-" if rrn_3 is None else rrn_3
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                logger.info(f"fetched date time from portal {date_time}")
                transaction_id = transaction_details[1]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id}")
                total_amount = transaction_details[1]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount}")
                auth_code_portal = transaction_details[1]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number = transaction_details[1]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number}")
                transaction_type = transaction_details[1]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type}")
                status = transaction_details[1]['Status']
                logger.info(f"fetched status {status}")
                username = transaction_details[1]['Username']
                logger.info(f"fetched username from portal {username}")

                date_time_2 = transaction_details[0]['Date & Time']
                logger.info(f"fetched date_time_2 from portal {date_time_2}")
                transaction_id_2 = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id_2 from portal {transaction_id_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total_amount_2 from portal {total_amount_2}")
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code_2 from portal {auth_code_portal_2}")
                rr_number_2 = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number_2 from portal {rr_number_2}")
                transaction_type_2 = transaction_details[0]['Type']
                logger.info(f"fetched txn_type_2 from portal {transaction_type_2}")
                status_2 = transaction_details[0]['Status']
                logger.info(f"fetched status_2 {status_2}")
                username_2 = transaction_details[0]['Username']
                logger.info(f"fetched username_2 from portal {username_2}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": status,
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": int(rr_number),
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
                }

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
                txn_date_3, txn_time_3 = date_time_converter.to_chargeslip_format(txn_created_time_3)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(txn_created_time_2)

                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2,
                }

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_2, {
                    "username": app_username, "password": app_password}, expected_charge_slip_values_2)

                expected_chargeslip_values_3 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_3),
                    'BASE AMOUNT:': "Rs." + str(amount)  + ".00", 'time': txn_time_3, 'date': txn_date_3,
                    'AUTH CODE': auth_code_3
                }

                chargeslip_val_result_3 = receipt_validator.perform_charge_slip_validations(txn_id_3, {
                    "username": app_username, "password": app_password}, expected_chargeslip_values_3)

                if chargeslip_val_result_2 and chargeslip_val_result_3:
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
def test_common_100_102_249():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_1_UPI_AXIS_DIRECT_And_1_BQR_HDFC_Success_Callback_Before_QR_Expiry_AutoRefund_Enabled
    Sub Feature Description: Performing a pure bqrv4 1 upi success callback via AXIS_DIRECT and 1 bqr success callback
    via HDFC, before qr expiry when autorefund is enabled
    TC naming code description: 100: Payment Method, 102: BQR, 249: TC249
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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(401, 1000)
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

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for confirm_axisdirect : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
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

            rrn_3 = "RE" + txn_id.split('E')[1]
            logger.debug(f"generated random rrn number is : {rrn_3}")
            auth_code_3 = "AE" + txn_id.split('E')[1]
            logger.debug(f"generated random auth_code is : {auth_code_3}")

            logger.debug(
                f"Fetching Txn_id,Auth code,RRN from data base : Txn_id : {txn_id},"
                f" Auth code : {auth_code_3}, RRN : {rrn_3}")
            api_details = DBProcessor.get_api_details('callbackHDFC', request_body={
                "PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                "TXN_ID": txn_id,
                "AUTH_CODE": auth_code_3, "RRN": rrn_3,
                "MERCHANT_PAN": bqr_merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and orig_txn_id='" + str(txn_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_3 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_3 : {txn_id_3}")
            customer_name_3 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_3 : {customer_name_3}")
            payer_name_3 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_3 : {payer_name_3}")
            org_code_txn_3 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_3 : {org_code_txn_3}")
            txn_type_3 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_3 : {txn_type_3}")
            auth_code_3 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_3 : {auth_code_3}")
            txn_created_time_3 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : txn_created_time_3 : {txn_created_time_3}")

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
                date_and_time_2 = date_time_converter.to_app_format(txn_created_time_2)
                date_and_time_3 = date_time_converter.to_app_format(txn_created_time_3)
                expected_app_values = {
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    # "auth_code_2": authid_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "pmt_mode_3": "BHARAT QR",
                    "pmt_status_3": "REFUND_PENDING",
                    "txn_amt_3": str(amount)+".00",
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_3,
                    "order_id_3": order_id,
                    "payment_msg_3": "PAYMENT SUCCESSFUL",
                    "date_3": date_and_time_3,
                    "auth_code_3": auth_code_3,
                    "rrn_3": str(rrn_3),
                    # "customer_name_3": customer_name_3,
                    # "payer_name_3": payer_name_3,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
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
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
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

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_3)
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_3}, {payment_status_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_3}, {app_date_and_time_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_3}, {app_auth_code_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_3}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_txn_id_3}")
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_3}, {app_amount_3}")
                # app_customer_name_3 = txn_history_page.fetch_customer_name_text()
                # logger.info(
                #     f"Fetching txn customer name from txn history for the txn : {txn_id_3}, {app_customer_name_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_3}, {app_settlement_status_3}")
                # app_payer_name_3 = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_3}, {app_payer_name_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_3}, {app_payment_msg_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_3}, {app_order_id_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_3}")

                actual_app_values = {
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
                    "date_2": app_date_and_time_3,
                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "txn_id_3": app_txn_id_3,
                    "rrn_3": str(app_rrn_3),
                    # "customer_name_3": app_customer_name_3,
                    "settle_status_3": app_settlement_status_3,
                    # "payer_name_3": app_payer_name_3,
                    "order_id_3": app_order_id_3,
                    "payment_msg_3": app_payment_msg_3,
                    "auth_code_3": app_auth_code_3,
                    "date_3": app_date_and_time_3
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
                date_2 = date_time_converter.db_datetime(txn_created_time_2)
                date_3 = date_time_converter.db_datetime(txn_created_time_3)
                expected_api_values = {
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "issuer_code_2": "AXIS", "customer_name_2": customer_name_2,
                    "order_id_2": order_id, "payer_name_2": payer_name_2,
                    "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    # "auth_code": authid_2,
                    "date_2": date_2,
                    # "orig_txn_id_2": txn_id,
                    "pmt_status_3": "REFUND_PENDING",
                    "txn_amt_3": float(amount), "pmt_mode_3": "BHARATQR",
                    "pmt_state_3": "SETTLED", "rrn_3": str(rrn_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "issuer_code_3": "HDFC",
                    "order_id_3": order_id,
                    "txn_type_3": "CHARGE", "mid_3": hdfc_mid, "tid_3": hdfc_tid,
                    "org_code_3": org_code,
                    "auth_code_3": auth_code_3,
                    "date_3": date_3,
                    "orig_txn_id_3": txn_id,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

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
                customer_name_api_2 = response["customerName"]
                payer_name_api_2 = response["payerName"]
                date_api_2 = response["createdTime"]
                order_id_api_2 = response["orderNumber"]
                # orig_txn_id_api_2 = response["origTxnId"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_3][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_3 = response["status"]
                amount_api_3 = float(response["amount"])
                payment_mode_api_3 = response["paymentMode"]
                state_api_3 = response["states"][0]
                rrn_api_3 = response["rrNumber"]
                settlement_status_api_3 = response["settlementStatus"]
                issuer_code_api_3 = response["issuerCode"]
                acquirer_code_api_3 = response["acquirerCode"]
                orgCode_api_3 = response["orgCode"]
                mid_api_3 = response["mid"]
                tid_api_3 = response["tid"]
                txn_type_api_3 = response["txnType"]
                auth_code_api_3 = response["authCode"]
                date_api_3 = response["createdTime"]
                order_id_api_3 = response["orderNumber"]
                orig_txn_id_api_3 = response["origTxnId"]

                actual_api_values = {
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": float(amount_api_2), "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2, "customer_name_2": customer_name_api_2,
                    "order_id_2": order_id_api_2, "payer_name_2": payer_name_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    # "auth_code_2": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    # "orig_txn_id_2": orig_txn_id_api_2,
                    "pmt_status_3": status_api_3,
                    "txn_amt_3": float(amount_api_3), "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_2, "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "issuer_code_3": issuer_code_api_3,
                    "order_id_3": order_id_api_3,
                    "txn_type_3": txn_type_api_3, "mid_3": mid_api_3, "tid_3": tid_api_3,
                    "org_code_3": orgCode_api_3,
                    "auth_code_3": auth_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_3),
                    "orig_txn_id_3": orig_txn_id_api_3,
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
                    "payment_gateway_2": "AXIS",
                    "mid_2": mid,
                    "tid_2": tid,
                    # "orig_txn_id_2": txn_id,
                    "upi_txn_status_2": "AUTHORIZED",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "pmt_status_3": "REFUND_PENDING",
                    "pmt_state_3": "REFUND_PENDING",
                    "pmt_mode_3": "BHARATQR",
                    "rr_number_3": str(rrn_3),
                    "auth_code_3": auth_code_3,
                    "txn_amt_3": float(amount),
                    "settle_status_3": "SETTLED",
                    "order_id_3": order_id,
                    "acquirer_code_3": "HDFC",
                    "bank_code_3": "HDFC",
                    "payment_gateway_3": "HDFC",
                    "mid_3": hdfc_mid,
                    "tid_3": hdfc_tid,
                    "orig_txn_id_3": txn_id,
                    "bqr_pmt_state_3": "REFUND_PENDING",
                    "bqr_txn_amt_3": float(amount),
                    "bqr_txn_type_3": "DYNAMIC_QR", "bqr_terminal_info_id_3": terminal_info_id,
                    "bqr_bank_code_3": "HDFC",
                    "bqr_merchant_config_id_3": bqr_merchant_config_id, "bqr_txn_primary_id_3": txn_id_3,
                    "bqr_org_code_3": org_code,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

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
                orig_txn_id_db_2 = result['orig_txn_id'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_3 = result["status"].iloc[0]
                payment_mode_db_3 = result["payment_mode"].iloc[0]
                amount_db_3 = float(result["amount"].iloc[0])
                state_db_3 = result["state"].iloc[0]
                payment_gateway_db_3 = result["payment_gateway"].iloc[0]
                acquirer_code_db_3 = result["acquirer_code"].iloc[0]
                bank_code_db_3 = result["bank_code"].iloc[0]
                settlement_status_db_3 = result["settlement_status"].iloc[0]
                tid_db_3 = result['tid'].values[0]
                mid_db_3 = result['mid'].values[0]
                order_id_db_3 = result['external_ref'].values[0]
                rr_number_db_3 = result['rr_number'].values[0]
                auth_code_db_3 = result['auth_code'].values[0]
                orig_txn_id_db_3 = result['orig_txn_id'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_3 = result["status_code"].iloc[0]
                bqr_state_db_3 = result["state"].iloc[0]
                bqr_amount_db_3 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_3 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_3 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_3 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_3 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_3 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_3 = result['org_code'].values[0]

                actual_db_values = {
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
                    # "orig_txn_id_2": orig_txn_id_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "pmt_status_3": status_db_3,
                    "pmt_state_3": state_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "rr_number_3": str(rr_number_db_3),
                    "auth_code_3": auth_code_db_3,
                    "txn_amt_3": float(amount_db_3),
                    "settle_status_3": settlement_status_db_3,
                    "order_id_3": order_id_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "bank_code_3": bank_code_db_3,
                    "payment_gateway_3": payment_gateway_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "orig_txn_id_3": orig_txn_id_db_3,
                    "bqr_pmt_state_3": bqr_state_db_3,
                    "bqr_txn_amt_3": bqr_amount_db_3,
                    "bqr_txn_type_3": bqr_txn_type_db_3, "bqr_terminal_info_id_3": bqr_terminal_info_id_db_3,
                    "bqr_bank_code_3": bqr_bank_code_db_3,
                    "bqr_merchant_config_id_3": bqr_merchant_config_id_db_3,
                    "bqr_txn_primary_id_3": bqr_txn_primary_id_db_3,
                    "bqr_org_code_3": bqr_org_code_db_3,
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
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time_2)
                date_and_time_portal_2 = date_time_converter.to_portal_format(txn_created_time_3)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id_2,
                    "auth_code": "-" if auth_code_2 is None else auth_code_2,
                    "rrn": rrn_2,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_3,
                    "auth_code_2": "-" if auth_code_3 is None else auth_code_3,
                    "rrn_2": "-" if rrn_3 is None else rrn_3
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                logger.info(f"fetched date time from portal {date_time}")
                transaction_id = transaction_details[1]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id}")
                total_amount = transaction_details[1]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount}")
                auth_code_portal = transaction_details[1]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number = transaction_details[1]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number}")
                transaction_type = transaction_details[1]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type}")
                status = transaction_details[1]['Status']
                logger.info(f"fetched status {status}")
                username = transaction_details[1]['Username']
                logger.info(f"fetched username from portal {username}")

                date_time_2 = transaction_details[0]['Date & Time']
                logger.info(f"fetched date_time_2 from portal {date_time_2}")
                transaction_id_2 = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id_2 from portal {transaction_id_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total_amount_2 from portal {total_amount_2}")
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code_2 from portal {auth_code_portal_2}")
                rr_number_2 = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number_2 from portal {rr_number_2}")
                transaction_type_2 = transaction_details[0]['Type']
                logger.info(f"fetched txn_type_2 from portal {transaction_type_2}")
                status_2 = transaction_details[0]['Status']
                logger.info(f"fetched status_2 {status_2}")
                username_2 = transaction_details[0]['Username']
                logger.info(f"fetched username_2 from portal {username_2}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": status,
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": int(rr_number),
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
                }

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
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(txn_created_time_2)

                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2,
                }

                receipt_validator.perform_charge_slip_validations(txn_id_2, {
                    "username": app_username, "password": app_password}, expected_charge_slip_values_2)
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
