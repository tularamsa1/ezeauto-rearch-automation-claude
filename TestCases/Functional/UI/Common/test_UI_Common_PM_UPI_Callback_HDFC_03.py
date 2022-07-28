import random
import shutil
import sys
import time
from datetime import datetime

import pytest
from termcolor import colored

from Configuration import TestSuiteSetup, Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_101_029():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_failed_callback_after_qr_expiry_HDFC_AutoRefund_Enabled
    Sub Feature Description: Performing two pure upi failed callback via HDFC after expiry the qr when autorefund is enabled
    100: Payment Method
    101: UPI
    029: TC029
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

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
            amount = random.randint(51, 100)
            if amount == 55:
                amount = 56
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

            payment_page.click_on_Upi_paymentMode()
            logger.info("selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            logger.info("resetting the com.ezetap.basicapp")
            app_driver.reset()
            logger.info("waiting for the time till qr get expired...")
            time.sleep(63)

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random callback_1_rrn number is : {callback_1_rrn}")
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
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id_1 from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_1 = result['id'].values[0]
            logger.debug(f"Query result new_txn_id_1 : {new_txn_id_1}")

            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random callback_2_rrn number is : {callback_2_rrn}")
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
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id_2 from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_2 = result['id'].values[0]
            logger.debug(f"Query result new_txn_id_2 : {new_txn_id_2}")

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
            logger.error(f"Test case execution failed due to the exception : {e}")
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
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
                expected_app_values = {"Payment mode": "UPI", "Payment Txn ID": original_txn_id,
                                       "Payment Amt": str(amount),
                                       "Payment Status": "EXPIRED", "rrn original": str(original_rrn)}
                logger.debug(f"expected_app_values : {expected_app_values}")

                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_order_id(order_id)

                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {original_txn_id}, {app_rrn_original}")

                actual_app_values = {"Payment Status": app_payment_status_original.split(':')[1],
                                     "Payment mode": app_payment_mode_original,
                                     "Payment Txn ID": app_txn_id_original,
                                     "Payment Amt": str(app_payment_amt_original),
                                     "rrn original": str(app_rrn_original)}

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
                expected_api_values = {"Payment Status": "EXPIRED",
                                       "Amount": amount,
                                       "Payment State": "EXPIRED",
                                       "Payment Mode": "UPI",
                                       "rrn": str(original_rrn)}

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                logger.debug(f"API DETAILS for original_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")

                status_api = response["status"]
                amount_api = int(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]

                actual_api_values = {"Payment Status": status_api,
                                     "Amount": amount_api,
                                     "Payment State": state_api,
                                     "Payment Mode": payment_mode_api,
                                     "rrn": str(rrn_api)}

                logger.debug(f"actual_api_values: {actual_api_values}")
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
                expected_db_values = {"Payment Status": "EXPIRED",
                                      "Payment State": "EXPIRED",
                                      "UPI_Txn_Status": "EXPIRED",
                                      "Payment mode": "UPI",
                                      "Payment amount": amount}
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]

                actual_db_values = {"Payment Status": status_db,
                                    "Payment State": state_db,
                                    "Payment mode": payment_mode_db,
                                    "Payment amount": amount_db,
                                    "UPI_Txn_Status": upi_status_db}

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
                expected_portal_values = {"Payment Type": "UPI",
                                          "Payment State": "Expired",
                                          "Amount": "Rs." + str(amount) + ".00",
                                          "Username": app_username, }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)

                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.search_merchant_name(org_code)
                logger.debug(f"searching for the org_code : {org_code}")

                home_page_portal.click_switch_button(org_code)
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()
                portal_trans_history_page = PortalTransHistoryPage(portal_driver)

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(original_txn_id)
                portal_txn_type = portal_values_dict['Type']
                portal_state = portal_values_dict['Status']
                portal_amt = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction state from portal : {portal_state} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                actual_portal_values = {"Payment Type": portal_txn_type,
                                        "Payment State": portal_state,
                                        "Amount": portal_amt,
                                        "Username": portal_username, }

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
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)------------------------------------------
            logger.info(f"Reverting all the settings that were done as preconditions for test case : {testcase_id}")
            api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions is : {response}")

            api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                                  "password": portal_password,
                                                                                  "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

            logger.info("Reverted back all the settings that were done as preconditions")
            GlobalVariables.time_calc.execution.end()
            print(colored(
                "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_030():
    """
    Sub Feature Code: UI_Common_PM_UPI_success_callback_before_qr_expiry_AutoRefund_Enabled_HDFC
    Sub Feature Description: Performing a pure upi success callback via HDFC before qr expiry when autorefund is enabled
    100: Payment Method
    101: UPI
    030: TC030
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
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
        logger.info("Finished performing preconditions before starting test case execution")

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
            amount = random.randint(301, 399)
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

            payment_page.click_on_Upi_paymentMode()
            logger.info("selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch original_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

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
            logger.debug(f"response : {response}")

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
                expected_app_values = {"Payment Status": "AUTHORIZED", "Payment mode": "UPI",
                                       "Payment Txn ID": original_txn_id, "Payment Amt": str(amount),
                                       "rrn": str(rrn)
                                       }
                logger.debug(f"expected_app_values : {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_order_id(order_id)
                app_rrn = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")

                actual_app_values = {"Payment Status": app_payment_status.split(':')[1],
                                     "Payment mode": app_payment_mode,
                                     "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),
                                     "rrn": str(app_rrn)
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
                expected_api_values = {"Payment Status": "AUTHORIZED",
                                       "Payment Settlement Status": "SETTLED",
                                       "Payment mode": "UPI",
                                       "Payment State": "SETTLED",
                                       "Payment Amt": str(amount),
                                       "rrn": str(rrn)
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)

                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                state_api_original = response["states"][0]
                rrn_api_original = response["rrNumber"]
                settlement_status_api_original = response["settlementStatus"]

                actual_api_values = {"Payment Status": status_api_original,
                                     "Payment Settlement Status": settlement_status_api_original,
                                     "Payment mode": payment_mode_api_original,
                                     "Payment State": state_api_original,
                                     "Payment Amt": str(amount_api_original),
                                     "rrn": str(rrn_api_original),
                                     }

                logger.debug(f"actual_api_values: {actual_api_values}")
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
                expected_db_values = {"Payment Status": "AUTHORIZED",
                                      "Payment mode": "UPI",
                                      "Payment State": "SETTLED",
                                      "Payment Amt": "{:.2f}".format(amount),
                                      "rrn": str(rrn),
                                      "UPI_Txn_Status": "AUTHORIZED",
                                      "UPI_Txn resp_code": "SUCCESS",
                                      "UPI_Txn txn_type": "PAY_QR",
                                      "UPI_Txn bank_code": "HDFC",
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select state,status,amount,payment_mode,external_ref,rr_number from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = "{:.2f}".format(result["amount"].iloc[0])
                state_db_original = result["state"].iloc[0]
                rr_number_original = result['rr_number'].values[0]

                query = "select status,resp_code,bank_code,txn_type from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_resp_code_db_original = result["resp_code"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]

                actual_db_values = {"Payment Status": status_db_original,
                                    "Payment mode": payment_mode_db_original,
                                    "Payment State": state_db_original,
                                    "Payment Amt": str(amount_db_original),
                                    "rrn": str(rr_number_original),
                                    "UPI_Txn_Status": upi_status_db_original,
                                    "UPI_Txn resp_code": upi_resp_code_db_original,
                                    "UPI_Txn txn_type": upi_txn_type_db_original,
                                    "UPI_Txn bank_code": upi_bank_code_db_original,
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
                expected_portal_values = {}

                actual_portal_values = {}

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                logger.debug(f"expected_values: {expected_values}")
                receipt_validator.perform_charge_slip_validations(original_txn_id,
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

        # -----------------------------------------End of ChargeSlip Validation----------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
            # -------------------------------Revert Preconditions done(setup)------------------------------------------
            logger.info(f"Reverting all the settings that were done as preconditions for test case : {testcase_id}")

            api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                                  "password": portal_password,
                                                                                  "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
            logger.info("Reverted back all the settings that were done as preconditions")
            GlobalVariables.time_calc.execution.end()
            print(colored(
                "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_031():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_success_callback_before_qr_expiry_HDFC_AutoRefund_Disabled
    Sub Feature Description: Performing two pure upi success callback via HDFC beofre expiry the qr when autorefund is disabled
    100: Payment Method
    101: UPI
    031: TC031
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
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
            amount = random.randint(301, 399)
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
            payment_page.click_on_Upi_paymentMode()
            logger.info("selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            logger.info("starting first callback")
            logger.info(
                "fetching pg merchant id and vps from the upi_merchant_config table to perform the 1st upi callback")
            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            logger.info(
                "fetching txn_id from the txn table to perform the 1st upi callback")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 1st upi callback is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id to perform the 1st upi callback is : {callback_1_ref_id}")

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

            logger.debug("executing the curl_data on the server to encrypt the data")
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes, "
                f"payload is the combination of the pg_merchant_id and the encrypted data")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request is : {response}")
            logger.info("completed first callback")

            logger.info("starting second callback")
            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 2nd upi callback is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id to perform the 2nd upi callback is : {callback_2_ref_id}")

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
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            logger.info("completed second callback")
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
            logger.error(f"Test case execution failed due to the exception : {e}")
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
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
                expected_app_values = {"Payment Status Original": "AUTHORIZED",
                                       "Payment Status new": "AUTHORIZED",
                                       "Payment Settlement Status": "SETTLED",
                                       "Payment Settlement Status new": "SETTLED",
                                       "Payment mode Original": "UPI",
                                       "Payment mode new": "UPI",
                                       "Payment Txn ID Original": original_txn_id,
                                       "Payment Txn ID new": new_txn_id,
                                       "Payment Amt Original": str(amount),
                                       "Payment Amt new": str(amount),
                                       "rrn original": str(callback_1_rrn),
                                       "rrn new": str(callback_2_rrn),
                                       }
                logger.debug(f"expected_app_values: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)

                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id)
                app_rrn_new = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {new_txn_id}, {app_rrn_new}")
                app_settlement_status_new = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status from txn history for the txn : {new_txn_id}, {app_settlement_status_new}")
                app_payment_status_new = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_new}")
                app_payment_mode_new = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_new}")
                app_txn_id_new = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_new}")
                app_payment_amt_new = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_new}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status from txn history for the txn : {new_txn_id}, {app_settlement_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {original_txn_id}, {app_rrn_original}")

                actual_app_values = {"Payment Status Original": app_payment_status_original.split(':')[1],
                                     "Payment Status new": app_payment_status_new.split(':')[1],
                                     "Payment Settlement Status": "SETTLED",
                                     "Payment Settlement Status new": "SETTLED",
                                     "Payment mode Original": app_payment_mode_original,
                                     "Payment mode new": app_payment_mode_new,
                                     "Payment Txn ID Original": app_txn_id_original,
                                     "Payment Txn ID new": app_txn_id_new,
                                     "Payment Amt Original": str(app_payment_amt_original),
                                     "Payment Amt new": str(app_payment_amt_new),
                                     "rrn original": str(app_rrn_original),
                                     "rrn new": str(app_rrn_new)
                                     }

                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info("App Validation Completed successfully for test case")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {"Payment Status Original": "AUTHORIZED",
                                       "Payment Status new": "AUTHORIZED",
                                       "Payment Settlement Status Original": "SETTLED",
                                       "Payment Settlement Status new": "SETTLED",
                                       "Payment mode Original": "UPI",
                                       "Payment mode new": "UPI",
                                       "Payment State Original": "SETTLED",
                                       "Payment State new": "SETTLED",
                                       "Payment Amt Original": str(amount),
                                       "Payment Amt new": str(amount),
                                       "rrn original": str(callback_1_rrn),
                                       "rrn new": str(callback_2_rrn),
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": new_txn_id})
                print("API DETAILS for new_txn_id_1 after callback:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)

                status_api_new = response["status"]
                amount_api_new = int(response["amount"])
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)

                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                state_api_original = response["states"][0]
                rrn_api_original = response["rrNumber"]
                settlement_status_api_original = response["settlementStatus"]

                actual_api_values = {"Payment Status Original": status_api_original,
                                     "Payment Status new": status_api_new,
                                     "Payment Settlement Status Original": settlement_status_api_original,
                                     "Payment Settlement Status new": settlement_status_api_new,
                                     "Payment mode Original": payment_mode_api_original,
                                     "Payment mode new": payment_mode_api_new,
                                     "Payment State Original": state_api_original,
                                     "Payment State new": state_api_new,
                                     "Payment Amt Original": str(amount_api_original),
                                     "Payment Amt new": str(amount_api_new),
                                     "rrn original": str(rrn_api_original),
                                     "rrn new": str(rrn_api_new),
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
                expected_db_values = {"Payment Status Original": "AUTHORIZED",
                                      "Payment Status new": "AUTHORIZED",
                                      "Payment mode Original": "UPI",
                                      "Payment mode new": "UPI",
                                      "Payment State Original": "SETTLED",
                                      "Payment State new": "SETTLED",
                                      "Payment Amt Original": "{:.2f}".format(amount),
                                      "Payment Amt new": "{:.2f}".format(amount),
                                      "rrn original": str(callback_1_rrn),
                                      "rrn new": str(callback_2_rrn),
                                      "UPI_Txn_Status Original": "AUTHORIZED",
                                      "UPI_Txn_Status new": "AUTHORIZED",
                                      "UPI_Txn resp_code Original": "SUCCESS",
                                      "UPI_Txn resp_code new": "SUCCESS",
                                      "UPI_Txn txn_type Original": "PAY_QR",
                                      "UPI_Txn txn_type new": "PAY_QR",
                                      "UPI_Txn bank_code Original": "HDFC",
                                      "UPI_Txn bank_code new": "HDFC",
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select state,status,amount,payment_mode,external_ref,rr_number from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = "{:.2f}".format(result["amount"].iloc[0])
                state_db_original = result["state"].iloc[0]
                rr_number_original = result['rr_number'].values[0]

                query = "select status,resp_code,bank_code,txn_type from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_resp_code_db_original = result["resp_code"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref,rr_number from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].iloc[0]
                payment_mode_db_new = result["payment_mode"].iloc[0]
                amount_db_new = "{:.2f}".format(result["amount"].iloc[0])
                state_db_new = result["state"].iloc[0]
                rr_number_new = result['rr_number'].values[0]

                query = "select status,resp_code,bank_code,txn_type from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_resp_code_db_new = result["resp_code"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]

                actual_db_values = {"Payment Status Original": status_db_original,
                                    "Payment Status new": status_db_new,
                                    "Payment mode Original": payment_mode_db_original,
                                    "Payment mode new": payment_mode_db_new,
                                    "Payment State Original": state_db_original,
                                    "Payment State new": state_db_new,
                                    "Payment Amt Original": str(amount_db_original),
                                    "Payment Amt new": str(amount_db_new),
                                    "rrn original": str(rr_number_original),
                                    "rrn new": str(rr_number_new),
                                    "UPI_Txn_Status Original": upi_status_db_original,
                                    "UPI_Txn_Status new": upi_status_db_new,
                                    "UPI_Txn resp_code Original": upi_resp_code_db_original,
                                    "UPI_Txn resp_code new": upi_resp_code_db_new,
                                    "UPI_Txn txn_type Original": upi_txn_type_db_original,
                                    "UPI_Txn txn_type new": upi_txn_type_db_new,
                                    "UPI_Txn bank_code Original": upi_bank_code_db_original,
                                    "UPI_Txn bank_code new": upi_bank_code_db_new,
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
                expected_portal_values = {}

                actual_portal_values = {}

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(callback_1_rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                logger.debug(f"expected_values 1 : {expected_values}")
                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(original_txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_values)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(callback_2_rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                logger.debug(f"expected_values 2 : {expected_values}")
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(new_txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_values)
                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'
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
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)------------------------------------------
            logger.info(f"Reverting all the settings that were done as preconditions for test case : {testcase_id}")
            api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions is : {response}")
            logger.info("Reverted back all the settings that were done as preconditions")
            GlobalVariables.time_calc.execution.end()
            print(colored(
                "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_032():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_success_callback_before_qr_expiry_HDFC_AutoRefund_Enabled
    Sub Feature Description: Performing two pure upi success callback via HDFC before expiry the qr when autorefund is enabled
    100: Payment Method
    101: UPI
    032: TC032
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
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
            amount = random.randint(301, 399)
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
            payment_page.click_on_Upi_paymentMode()
            logger.info("selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            logger.info("starting first callback")
            logger.info(
                "fetching pg merchant id and vps from the upi_merchant_config table to perform the 1st upi callback")
            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            logger.info(
                "fetching txn_id from the txn table to perform the 1st upi callback")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 1st upi callback is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id to perform the 1st upi callback is : {callback_1_ref_id}")

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

            logger.debug("executing the curl_data on the server to encrypt the data")
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes, "
                f"payload is the combination of the pg_merchant_id and the encrypted data")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request is : {response}")
            logger.info("completed first callback")

            logger.info("starting second callback")
            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 2nd upi callback is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id to perform the 2nd upi callback is : {callback_2_ref_id}")

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
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            logger.info("completed second callback")
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
            logger.error(f"Test case execution failed due to the exception : {e}")
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
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
                expected_app_values = {"Payment Status Original": "AUTHORIZED",
                                       "Payment Status new": "REFUND_PENDING",
                                       "Payment Settlement Status Original": "SETTLED",
                                       "Payment Settlement Status new": "SETTLED",
                                       "Payment mode Original": "UPI",
                                       "Payment mode new": "UPI",
                                       "Payment Txn ID Original": original_txn_id,
                                       "Payment Txn ID new": new_txn_id,
                                       "Payment Amt Original": str(amount),
                                       "Payment Amt new": str(amount),
                                       "rrn original": str(callback_1_rrn),
                                       "rrn new": str(callback_2_rrn),
                                       }
                logger.debug(f"expected_app_values: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)

                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id)
                app_rrn_new = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {new_txn_id}, {app_rrn_new}")
                app_settlement_status_new = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status from txn history for the txn : {new_txn_id}, {app_settlement_status_new}")
                app_payment_status_new = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_new}")
                app_payment_mode_new = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_new}")
                app_txn_id_new = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_new}")
                app_payment_amt_new = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_new}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status from txn history for the txn : {new_txn_id}, {app_settlement_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {original_txn_id}, {app_rrn_original}")

                actual_app_values = {"Payment Status Original": app_payment_status_original.split(':')[1],
                                     "Payment Status new": app_payment_status_new.split(':')[1],
                                     "Payment Settlement Status Original": app_settlement_status_original,
                                     "Payment Settlement Status new": app_settlement_status_new,
                                     "Payment mode Original": app_payment_mode_original,
                                     "Payment mode new": app_payment_mode_new,
                                     "Payment Txn ID Original": app_txn_id_original,
                                     "Payment Txn ID new": app_txn_id_new,
                                     "Payment Amt Original": str(app_payment_amt_original),
                                     "Payment Amt new": str(app_payment_amt_new),
                                     "rrn original": str(app_rrn_original),
                                     "rrn new": str(app_rrn_new)
                                     }

                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info("App Validation Completed successfully for test case")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {"Payment Status Original": "AUTHORIZED",
                                       "Payment Status new": "REFUND_PENDING",
                                       "Payment Settlement Status Original": "SETTLED",
                                       "Payment Settlement Status new": "SETTLED",
                                       "Payment mode Original": "UPI",
                                       "Payment mode new": "UPI",
                                       "Payment State Original": "SETTLED",
                                       "Payment State new": "REFUND_PENDING",
                                       "Payment Amt Original": str(amount),
                                       "Payment Amt new": str(amount),
                                       "rrn original": str(callback_1_rrn),
                                       "rrn new": str(callback_2_rrn),
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                # api_details = DBProcessor.get_api_details('txnDetails',
                #                                           request_body={"username": app_username,
                #                                                         "password": app_password,
                #                                                         "txnId": new_txn_id})
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                print("API DETAILS for new_txn_id after callback:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_new = amount_api_new = payment_mode_api_new = state_api_new = rrn_api_new = settlement_status_api_new = ''
                list_txns = response['txns']
                for txn in list_txns:
                    if txn['txnId'] == new_txn_id:
                        status_api_new = txn["status"]
                        amount_api_new = int(txn["amount"])
                        payment_mode_api_new = txn["paymentMode"]
                        state_api_new = txn["states"][0]
                        rrn_api_new = txn["rrNumber"]
                        settlement_status_api_new = txn["settlementStatus"]

                # api_details = DBProcessor.get_api_details('txnDetails',
                #                                           request_body={"username": app_username,
                #                                                         "password": app_password,
                #                                                         "txnId": original_txn_id})
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_original = amount_api_original = payment_mode_api_original = state_api_original = rrn_api_original = settlement_status_api_original = ''
                list_txns = response['txns']
                for txn in list_txns:
                    if txn['txnId'] == original_txn_id:
                        status_api_original = txn["status"]
                        amount_api_original = int(txn["amount"])
                        payment_mode_api_original = txn["paymentMode"]
                        state_api_original = txn["states"][0]
                        rrn_api_original = txn["rrNumber"]
                        settlement_status_api_original = txn["settlementStatus"]

                actual_api_values = {"Payment Status Original": status_api_original,
                                     "Payment Status new": status_api_new,
                                     "Payment Settlement Status Original": settlement_status_api_original,
                                     "Payment Settlement Status new": settlement_status_api_new,
                                     "Payment mode Original": payment_mode_api_original,
                                     "Payment mode new": payment_mode_api_new,
                                     "Payment State Original": state_api_original,
                                     "Payment State new": state_api_new,
                                     "Payment Amt Original": str(amount_api_original),
                                     "Payment Amt new": str(amount_api_new),
                                     "rrn original": str(rrn_api_original),
                                     "rrn new": str(rrn_api_new),
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
                expected_db_values = {"Payment Status Original": "AUTHORIZED",
                                      "Payment Status new": "REFUND_PENDING",
                                      "Payment mode Original": "UPI",
                                      "Payment mode new": "UPI",
                                      "Payment State Original": "SETTLED",
                                      "Payment State new": "REFUND_PENDING",
                                      "Payment Amt Original": "{:.2f}".format(amount),
                                      "Payment Amt new": "{:.2f}".format(amount),
                                      "rrn original": str(callback_1_rrn),
                                      "rrn new": str(callback_2_rrn),
                                      "UPI_Txn_Status Original": "AUTHORIZED",
                                      "UPI_Txn_Status new": "REFUND_PENDING",
                                      "UPI_Txn resp_code Original": "SUCCESS",
                                      "UPI_Txn resp_code new": "SUCCESS",
                                      "UPI_Txn txn_type Original": "PAY_QR",
                                      "UPI_Txn txn_type new": "PAY_QR",
                                      "UPI_Txn bank_code Original": "HDFC",
                                      "UPI_Txn bank_code new": "HDFC",
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select state,status,amount,payment_mode,external_ref,rr_number from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = "{:.2f}".format(result["amount"].iloc[0])
                state_db_original = result["state"].iloc[0]
                rr_number_original= result['rr_number'].values[0]

                query = "select status,resp_code,bank_code,txn_type from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_resp_code_db_original = result["resp_code"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref,rr_number from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].iloc[0]
                payment_mode_db_new = result["payment_mode"].iloc[0]
                amount_db_new = "{:.2f}".format(result["amount"].iloc[0])
                state_db_new = result["state"].iloc[0]
                rr_number_new = result['rr_number'].values[0]

                query = "select status,resp_code,bank_code,txn_type from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_resp_code_db_new = result["resp_code"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]

                actual_db_values = {"Payment Status Original": status_db_original,
                                    "Payment Status new": status_db_new,
                                    "Payment mode Original": payment_mode_db_original,
                                    "Payment mode new": payment_mode_db_new,
                                    "Payment State Original": state_db_original,
                                    "Payment State new": state_db_new,
                                    "Payment Amt Original": str(amount_db_original),
                                    "Payment Amt new": str(amount_db_new),
                                    "rrn original": str(rr_number_original),
                                    "rrn new": str(rr_number_new),
                                    "UPI_Txn_Status Original": upi_status_db_original,
                                    "UPI_Txn_Status new": upi_status_db_new,
                                    "UPI_Txn resp_code Original": upi_resp_code_db_original,
                                    "UPI_Txn resp_code new": upi_resp_code_db_new,
                                    "UPI_Txn txn_type Original": upi_txn_type_db_original,
                                    "UPI_Txn txn_type new": upi_txn_type_db_new,
                                    "UPI_Txn bank_code Original": upi_bank_code_db_original,
                                    "UPI_Txn bank_code new": upi_bank_code_db_new,
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
                expected_portal_values = {}

                actual_portal_values = {}

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(callback_1_rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                logger.debug(f"expected_values : {expected_values}")
                receipt_validator.perform_charge_slip_validations(original_txn_id,
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
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)------------------------------------------
            logger.info(f"Reverting all the settings that were done as preconditions for test case : {testcase_id}")
            api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions is : {response}")

            api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                                  "password": portal_password,
                                                                                  "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
            logger.debug(f"API details  : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

            logger.info("Reverted back all the settings that were done as preconditions")
            GlobalVariables.time_calc.execution.end()
            print(colored(
                "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_033():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_failed_callback_before_qr_expiry_HDFC_AutoRefund_Disabled
    Sub Feature Description: Performing two pure upi failed callback via HDFC before expiry the qr when autorefund is disabled
    100: Payment Method
    101: UPI
    033: TC033
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
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
            amount = random.randint(301, 399)
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
            payment_page.click_on_Upi_paymentMode()
            logger.info("selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            logger.info("starting first callback")
            logger.info(
                "fetching pg merchant id and vps from the upi_merchant_config table to perform the 1st upi callback")
            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            logger.info(
                "fetching txn_id from the txn table to perform the 1st upi callback")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 1st upi callback is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id to perform the 1st upi callback is : {callback_1_ref_id}")

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

            logger.debug("executing the curl_data on the server to encrypt the data")
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes, "
                f"payload is the combination of the pg_merchant_id and the encrypted data")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request is : {response}")
            logger.info("completed first callback")

            logger.info("starting second callback")
            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 2nd upi callback is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id to perform the 2nd upi callback is : {callback_2_ref_id}")

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
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            logger.info("completed second callback")
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
            logger.error(f"Test case execution failed due to the exception : {e}")
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
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
                expected_app_values = {"Payment Status Original": "FAILED",
                                       "Payment Settlement Status Original": "FAILED",
                                       "Payment mode Original": "UPI",
                                       "Payment Txn ID Original": original_txn_id,
                                       "Payment Txn ID": original_txn_id,
                                       "Payment Amt Original": str(amount),
                                       "rrn original": str(callback_1_rrn),
                                       }
                logger.debug(f"expected_app_values: {expected_app_values}")

                logger.info("resetting the the")
                app_driver.reset()
                login_page = LoginPage(app_driver)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)

                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id)
                app_rrn_new = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {new_txn_id}, {app_rrn_new}")
                app_settlement_status_new = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status from txn history for the txn : {new_txn_id}, {app_settlement_status_new}")
                app_payment_status_new = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_new}")
                app_payment_mode_new = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_new}")
                app_txn_id_new = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_new}")
                app_payment_amt_new = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_new}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status from txn history for the txn : {new_txn_id}, {app_settlement_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {original_txn_id}, {app_rrn_original}")

                actual_app_values = {"Payment Status Original": app_payment_status_original.split(':')[1],
                                     "Payment Settlement Status Original": app_settlement_status_original,
                                     "Payment mode Original": app_payment_mode_original,
                                     "Payment Txn ID Original": app_txn_id_original,
                                     "Payment Txn ID": app_txn_id_new,
                                     "Payment Amt Original": str(app_payment_amt_original),
                                     "rrn original": str(app_rrn_original),
                                     }

                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info("App Validation Completed successfully for test case")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {"Payment Status Original": "FAILED",
                                       "Payment Status new": "FAILED",
                                       "Payment Settlement Status Original": "FAILED",
                                       "Payment Settlement Status new": "FAILED",
                                       "Payment mode Original": "UPI",
                                       "Payment mode new": "UPI",
                                       "Payment State Original": "FAILED",
                                       "Payment State new": "FAILED",
                                       "Payment Amt Original": str(amount),
                                       "Payment Amt new": str(amount),
                                       "rrn original": str(callback_1_rrn),
                                       "rrn new": str(callback_1_rrn),
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                # api_details = DBProcessor.get_api_details('txnDetails',
                #                                           request_body={"username": app_username,
                #                                                         "password": app_password,
                #                                                         "txnId": new_txn_id})
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                print("API DETAILS for new_txn_id after callback:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_new = amount_api_new = payment_mode_api_new = state_api_new = rrn_api_new = settlement_status_api_new = ''
                list_txns = response['txns']
                for txn in list_txns:
                    if txn['txnId'] == new_txn_id:
                        status_api_new = txn["status"]
                        amount_api_new = int(txn["amount"])
                        payment_mode_api_new = txn["paymentMode"]
                        state_api_new = txn["states"][0]
                        rrn_api_new = txn["rrNumber"]
                        settlement_status_api_new = txn["settlementStatus"]

                # api_details = DBProcessor.get_api_details('txnDetails',
                #                                           request_body={"username": app_username,
                #                                                         "password": app_password,
                #                                                         "txnId": original_txn_id})
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_original = amount_api_original = payment_mode_api_original = state_api_original = rrn_api_original = settlement_status_api_original = ''
                list_txns = response['txns']
                for txn in list_txns:
                    if txn['txnId'] == original_txn_id:
                        status_api_original = txn["status"]
                        amount_api_original = int(txn["amount"])
                        payment_mode_api_original = txn["paymentMode"]
                        state_api_original = txn["states"][0]
                        rrn_api_original = txn["rrNumber"]
                        settlement_status_api_original = txn["settlementStatus"]

                actual_api_values = {"Payment Status Original": status_api_original,
                                     "Payment Status new": status_api_new,
                                     "Payment Settlement Status Original": settlement_status_api_original,
                                     "Payment Settlement Status new": settlement_status_api_new,
                                     "Payment mode Original": payment_mode_api_original,
                                     "Payment mode new": payment_mode_api_new,
                                     "Payment State Original": state_api_original,
                                     "Payment State new": state_api_new,
                                     "Payment Amt Original": str(amount_api_original),
                                     "Payment Amt new": str(amount_api_new),
                                     "rrn original": str(rrn_api_original),
                                     "rrn new": str(rrn_api_new),
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
                expected_db_values = {"Payment Status Original": "FAILED",
                                      "Payment Status new": "FAILED",
                                      "Payment mode Original": "UPI",
                                      "Payment mode new": "UPI",
                                      "Payment State Original": "FAILED",
                                      "Payment State new": "FAILED",
                                      "Payment Amt Original": "{:.2f}".format(amount),
                                      "Payment Amt new": "{:.2f}".format(amount),
                                      "rrn original": str(callback_1_rrn),
                                      "rrn new": str(callback_1_rrn),
                                      "UPI_Txn_Status Original": "FAILED",
                                      "UPI_Txn_Status new": "FAILED",
                                      "UPI_Txn resp_code Original": "FAILED",
                                      "UPI_Txn resp_code new": "FAILED",
                                      "UPI_Txn txn_type Original": "PAY_QR",
                                      "UPI_Txn txn_type new": "PAY_QR",
                                      "UPI_Txn bank_code Original": "HDFC",
                                      "UPI_Txn bank_code new": "HDFC",
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select state,status,amount,payment_mode,external_ref,rr_number from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = "{:.2f}".format(result["amount"].iloc[0])
                state_db_original = result["state"].iloc[0]
                rr_number_original= result['rr_number'].values[0]

                query = "select status,resp_code,bank_code,txn_type from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_resp_code_db_original = result["resp_code"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref,rr_number from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].iloc[0]
                payment_mode_db_new = result["payment_mode"].iloc[0]
                amount_db_new = "{:.2f}".format(result["amount"].iloc[0])
                state_db_new = result["state"].iloc[0]
                rr_number_new = result['rr_number'].values[0]

                query = "select status,resp_code,bank_code,txn_type from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_resp_code_db_new = result["resp_code"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]

                actual_db_values = {"Payment Status Original": status_db_original,
                                    "Payment Status new": status_db_new,
                                    "Payment mode Original": payment_mode_db_original,
                                    "Payment mode new": payment_mode_db_new,
                                    "Payment State Original": state_db_original,
                                    "Payment State new": state_db_new,
                                    "Payment Amt Original": str(amount_db_original),
                                    "Payment Amt new": str(amount_db_new),
                                    "rrn original": str(rr_number_original),
                                    "rrn new": str(rr_number_new),
                                    "UPI_Txn_Status Original": upi_status_db_original,
                                    "UPI_Txn_Status new": upi_status_db_new,
                                    "UPI_Txn resp_code Original": upi_resp_code_db_original,
                                    "UPI_Txn resp_code new": upi_resp_code_db_new,
                                    "UPI_Txn txn_type Original": upi_txn_type_db_original,
                                    "UPI_Txn txn_type new": upi_txn_type_db_new,
                                    "UPI_Txn bank_code Original": upi_bank_code_db_original,
                                    "UPI_Txn bank_code new": upi_bank_code_db_new,
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
                expected_portal_values = {}

                actual_portal_values = {}

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)------------------------------------------
            logger.info(f"Reverting all the settings that were done as preconditions for test case : {testcase_id}")
            api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions is : {response}")

            api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                                  "password": portal_password,
                                                                                  "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
            logger.debug(f"API details  : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

            logger.info("Reverted back all the settings that were done as preconditions")
            GlobalVariables.time_calc.execution.end()
            print(colored(
                "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_034():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_failed_callback_before_qr_expiry_HDFC_AutoRefund_Enabled
    Sub Feature Description: Performing two pure upi failed callback via HDFC before expiry the qr when autorefund is enabled
    100: Payment Method
    101: UPI
    034: TC034
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
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
            amount = random.randint(301, 399)
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
            payment_page.click_on_Upi_paymentMode()
            logger.info("selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            logger.info("starting first callback")
            logger.info(
                "fetching pg merchant id and vps from the upi_merchant_config table to perform the 1st upi callback")
            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            logger.info(
                "fetching txn_id from the txn table to perform the 1st upi callback")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 1st upi callback is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id to perform the 1st upi callback is : {callback_1_ref_id}")

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

            logger.debug("executing the curl_data on the server to encrypt the data")
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes, "
                f"payload is the combination of the pg_merchant_id and the encrypted data")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request is : {response}")
            logger.info("completed first callback")

            logger.info("starting second callback")
            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 2nd upi callback is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id to perform the 2nd upi callback is : {callback_2_ref_id}")

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
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            logger.info("completed second callback")
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
            logger.error(f"Test case execution failed due to the exception : {e}")
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
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
                expected_app_values = {"Payment Status Original": "FAILED",
                                       "Payment Status new": "FAILED",
                                       "Payment Settlement Status Original": "FAILED",
                                       "Payment Settlement Status new": "FAILED",
                                       "Payment mode Original": "UPI",
                                       "Payment mode new": "UPI",
                                       "Payment Txn ID Original": original_txn_id,
                                       "Payment Txn ID new": original_txn_id,
                                       "Payment Amt Original": str(amount),
                                       "Payment Amt new": str(amount),
                                       "rrn original": str(callback_1_rrn),
                                       "rrn new": str(callback_1_rrn),
                                       }
                logger.debug(f"expected_app_values: {expected_app_values}")

                logger.info("resetting the the")
                app_driver.reset()
                login_page = LoginPage(app_driver)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)

                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id)
                app_rrn_new = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {new_txn_id}, {app_rrn_new}")
                app_settlement_status_new = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status from txn history for the txn : {new_txn_id}, {app_settlement_status_new}")
                app_payment_status_new = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_new}")
                app_payment_mode_new = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_new}")
                app_txn_id_new = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_new}")
                app_payment_amt_new = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_new}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status from txn history for the txn : {new_txn_id}, {app_settlement_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {original_txn_id}, {app_rrn_original}")

                actual_app_values = {"Payment Status Original": app_payment_status_original.split(':')[1],
                                     "Payment Status new": app_payment_status_new.split(':')[1],
                                     "Payment Settlement Status Original": app_settlement_status_original,
                                     "Payment Settlement Status new": app_settlement_status_new,
                                     "Payment mode Original": app_payment_mode_original,
                                     "Payment mode new": app_payment_mode_new,
                                     "Payment Txn ID Original": app_txn_id_original,
                                     "Payment Txn ID new": app_txn_id_new,
                                     "Payment Amt Original": str(app_payment_amt_original),
                                     "Payment Amt new": str(app_payment_amt_new),
                                     "rrn original": str(app_rrn_original),
                                     "rrn new": str(app_rrn_new)
                                     }

                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info("App Validation Completed successfully for test case")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {"Payment Status Original": "FAILED",
                                       "Payment Status new": "FAILED",
                                       "Payment Settlement Status Original": "FAILED",
                                       "Payment Settlement Status new": "FAILED",
                                       "Payment mode Original": "UPI",
                                       "Payment mode new": "UPI",
                                       "Payment State Original": "FAILED",
                                       "Payment State new": "FAILED",
                                       "Payment Amt Original": str(amount),
                                       "Payment Amt new": str(amount),
                                       "rrn original": str(callback_1_rrn),
                                       "rrn new": str(callback_1_rrn),
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                # api_details = DBProcessor.get_api_details('txnDetails',
                #                                           request_body={"username": app_username,
                #                                                         "password": app_password,
                #                                                         "txnId": new_txn_id})
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                print("API DETAILS for new_txn_id after callback:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_new = amount_api_new = payment_mode_api_new = state_api_new = rrn_api_new = settlement_status_api_new = ''
                list_txns = response['txns']
                for txn in list_txns:
                    if txn['txnId'] == new_txn_id:
                        status_api_new = txn["status"]
                        amount_api_new = int(txn["amount"])
                        payment_mode_api_new = txn["paymentMode"]
                        state_api_new = txn["states"][0]
                        rrn_api_new = txn["rrNumber"]
                        settlement_status_api_new = txn["settlementStatus"]

                # api_details = DBProcessor.get_api_details('txnDetails',
                #                                           request_body={"username": app_username,
                #                                                         "password": app_password,
                #                                                         "txnId": original_txn_id})
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_original = amount_api_original = payment_mode_api_original = state_api_original = rrn_api_original = settlement_status_api_original = ''
                list_txns = response['txns']
                for txn in list_txns:
                    if txn['txnId'] == original_txn_id:
                        status_api_original = txn["status"]
                        amount_api_original = int(txn["amount"])
                        payment_mode_api_original = txn["paymentMode"]
                        state_api_original = txn["states"][0]
                        rrn_api_original = txn["rrNumber"]
                        settlement_status_api_original = txn["settlementStatus"]

                actual_api_values = {"Payment Status Original": status_api_original,
                                     "Payment Status new": status_api_new,
                                     "Payment Settlement Status Original": settlement_status_api_original,
                                     "Payment Settlement Status new": settlement_status_api_new,
                                     "Payment mode Original": payment_mode_api_original,
                                     "Payment mode new": payment_mode_api_new,
                                     "Payment State Original": state_api_original,
                                     "Payment State new": state_api_new,
                                     "Payment Amt Original": str(amount_api_original),
                                     "Payment Amt new": str(amount_api_new),
                                     "rrn original": str(rrn_api_original),
                                     "rrn new": str(rrn_api_new),
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
                expected_db_values = {"Payment Status Original": "FAILED",
                                      "Payment Status new": "FAILED",
                                      "Payment mode Original": "UPI",
                                      "Payment mode new": "UPI",
                                      "Payment State Original": "FAILED",
                                      "Payment State new": "FAILED",
                                      "Payment Amt Original": "{:.2f}".format(amount),
                                      "Payment Amt new": "{:.2f}".format(amount),
                                      "rrn original": str(callback_1_rrn),
                                      "rrn new": str(callback_1_rrn),
                                      "UPI_Txn_Status Original": "FAILED",
                                      "UPI_Txn_Status new": "FAILED",
                                      "UPI_Txn resp_code Original": "FAILED",
                                      "UPI_Txn resp_code new": "FAILED",
                                      "UPI_Txn txn_type Original": "PAY_QR",
                                      "UPI_Txn txn_type new": "PAY_QR",
                                      "UPI_Txn bank_code Original": "HDFC",
                                      "UPI_Txn bank_code new": "HDFC",
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select state,status,amount,payment_mode,external_ref,rr_number from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = "{:.2f}".format(result["amount"].iloc[0])
                state_db_original = result["state"].iloc[0]
                rr_number_original= result['rr_number'].values[0]

                query = "select status,resp_code,bank_code,txn_type from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_resp_code_db_original = result["resp_code"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref,rr_number from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].iloc[0]
                payment_mode_db_new = result["payment_mode"].iloc[0]
                amount_db_new = "{:.2f}".format(result["amount"].iloc[0])
                state_db_new = result["state"].iloc[0]
                rr_number_new = result['rr_number'].values[0]

                query = "select status,resp_code,bank_code,txn_type from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_resp_code_db_new = result["resp_code"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]

                actual_db_values = {"Payment Status Original": status_db_original,
                                    "Payment Status new": status_db_new,
                                    "Payment mode Original": payment_mode_db_original,
                                    "Payment mode new": payment_mode_db_new,
                                    "Payment State Original": state_db_original,
                                    "Payment State new": state_db_new,
                                    "Payment Amt Original": str(amount_db_original),
                                    "Payment Amt new": str(amount_db_new),
                                    "rrn original": str(rr_number_original),
                                    "rrn new": str(rr_number_new),
                                    "UPI_Txn_Status Original": upi_status_db_original,
                                    "UPI_Txn_Status new": upi_status_db_new,
                                    "UPI_Txn resp_code Original": upi_resp_code_db_original,
                                    "UPI_Txn resp_code new": upi_resp_code_db_new,
                                    "UPI_Txn txn_type Original": upi_txn_type_db_original,
                                    "UPI_Txn txn_type new": upi_txn_type_db_new,
                                    "UPI_Txn bank_code Original": upi_bank_code_db_original,
                                    "UPI_Txn bank_code new": upi_bank_code_db_new,
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
                expected_portal_values = {}

                actual_portal_values = {}

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)------------------------------------------
            logger.info(f"Reverting all the settings that were done as preconditions for test case : {testcase_id}")
            api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions is : {response}")

            api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                                  "password": portal_password,
                                                                                  "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
            logger.debug(f"API details  : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

            logger.info("Reverted back all the settings that were done as preconditions")
            GlobalVariables.time_calc.execution.end()
            print(colored(
                "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")
