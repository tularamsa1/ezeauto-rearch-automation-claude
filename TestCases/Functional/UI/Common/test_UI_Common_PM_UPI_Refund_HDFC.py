import random
import shutil
import sys
from datetime import datetime
import pytest
from termcolor import colored

from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_010():
    """
    Sub Feature Code: UI_Common_PM_UPI_full_Refund_via-Portal_HDFC
    Sub Feature Description: Performing a upi txn and full refund via portal
    100: Payment Method
    101: UPI
    010: TC010
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
        username = app_cred['Username']
        password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
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

            logger.info(f"Logging in the MPOSX application using username : {username}")
            login_page.perform_login(username, password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Order id : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")

            app_payment_status = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            payment_page.click_on_proceed_homepage()

            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")

            portal_driver = TestSuiteSetup.initialize_portal_driver()

            login_page_portal = PortalLoginPage(portal_driver)

            logger.info(f"Logging in Portal using username : {portal_username}")
            login_page_portal.perform_login_to_portal(portal_username, portal_password)
            home_page_portal = PortalHomePage(portal_driver)
            home_page_portal.search_merchant_name(str(org_code))
            logger.info(f"Switching to merchant : {org_code}")
            home_page_portal.click_switch_button(str(org_code))
            home_page_portal.click_transaction_search_menu()
            logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
            home_page_portal.click_on_transaction_details_based_on_transaction_id(txn_id)
            logger.debug("Clicking on refund button")
            home_page_portal.click_on_refund_button()
            home_page_portal.perform_refund_of_txn(amount)

            logger.info("Performing Page refresh after refund is performed")
            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_id : {txn_id_refunded}, rrn : {rrn} ")

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
            ReportProcessor.capture_ss_when_portal_val_exe_failed()
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
                expected_app_values = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "UPI",
                                       "Payment Txn ID": txn_id_refunded, "Payment Amt": str(amount),
                                       "Payment Status Original": "STATUS:AUTHORIZED_REFUNDED",
                                       "Payment mode Original": "UPI", "Payment Txn ID Original": txn_id,
                                       "Payment Amt Original": str(amount), "rrn": str(rrn)}

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id : {testcase_id}")

                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_order_id(order_id)
                app_rrn = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn}")
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
                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_second_transaction_by_order_id(order_id)
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

                actual_app_values = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode,
                                     "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),
                                     "Payment Status Original": app_payment_status_original,
                                     "Payment mode Original": app_payment_mode_original,
                                     "Payment Txn ID Original": txn_id,
                                     "Payment Amt Original": str(app_payment_amt_original), "rrn": str(app_rrn)}

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id : {testcase_id}")

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
                expected_api_values = {"Payment Status": "REFUNDED", "Amount": amount, "Payment Mode": "UPI",
                                       "Payment Status Original": "AUTHORIZED_REFUNDED", "Amount Original": amount,
                                       "Payment Mode Original": "UPI", "rrn": str(rrn)}

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id : {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS for original txn:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api_orginal = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_orginal = response["paymentMode"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_refunded})
                print("API DETAILS for refunded txn:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = int(response["amount"])
                payment_mode_api = response["paymentMode"]
                rrn_api = response["rrNumber"]

                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction api : {status_api_orginal} ")
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction api : {amount_api_original} ")
                logger.debug(
                    f"Fetching Transaction payment of original txn mode from transaction api : {payment_mode_api_orginal} ")

                actual_api_values = {"Payment Status": status_api, "Amount": amount_api,
                                     "Payment Mode": payment_mode_api,
                                     "Payment Status Original": status_api_orginal,
                                     "Amount Original": amount_api_original,
                                     "Payment Mode Original": payment_mode_api_orginal, "rrn": str(rrn_api)}

                logger.debug(f"actual_api_values : {actual_api_values} for the testcase_id : {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {"Payment Status": "REFUNDED", "Payment mode": "UPI", "Payment amount": amount,
                                      "Payment Status Original": "AUTHORIZED_REFUNDED", "Amount Original": amount,
                                      "Payment Mode Original": "UPI"}

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id : {testcase_id}")

                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                logger.debug(
                    f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB of original txn : {result} ")
                print(result)
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")

                actual_db_values = {"Payment Status": status_db, "Payment mode": payment_mode_db,
                                    "Payment amount": amount_db, "Payment Status Original": status_db_original,
                                    "Amount Original": amount_db_original,
                                    "Payment Mode Original": payment_mode_db_original}

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id : {testcase_id}")

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
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {"Payment Status": "Refunded", "Payment mode": "UPI",
                                          "Payment amount": str(amount),
                                          "Payment Status Original": "Authorized Refunded",
                                          "Amount Original": str(amount), "Payment Mode Original": "UPI"}

                logger.debug(f"expected_portal_values : {expected_portal_values} for the testcase_id : {testcase_id}")

                portal_driver.refresh()
                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id_refunded)
                portal_txn_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amt = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
                portal_txn_type_original = portal_values_dict['Type']
                portal_status_original = portal_values_dict['Status']
                portal_amt_original = portal_values_dict['Total Amount']
                portal_username_original = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")

                actual_portal_values = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                        "Payment amount": str(portal_amt.split('.')[1]),
                                        "Payment Status Original": portal_status_original,
                                        "Amount Original": str(portal_amt_original.split('.')[1]),
                                        "Payment Mode Original": portal_txn_type_original}

                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

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
                expected_chargeslip_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(rrn),
                                              'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}

                logger.debug(
                    f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id : {testcase_id}")

                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": username, "password": password},
                                                                  expected_chargeslip_values)

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
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")
        # Write the code here to revert the settings that were done as precondition
        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_011():
    """
    Sub Feature Code: UI_Common_PM_Pure_UPI_full_Refund_via_API_HDFC
    Sub Feature Description: Verification of a full refund using api for HDFC
    100: Payment Method
    101: UPI
    011: TC011
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
        username = app_cred['Username']
        password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
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

            logger.info(f"Logging in the MPOSX application using username : {username}")
            login_page.perform_login(username, password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Order id : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")

            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status_refunded = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status_refunded}")
            payment_page.click_on_proceed_homepage()

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "'"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_original = result["id"].iloc[0]
            status = result['status'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            settlement_status = result['settlement_status'].values[0]
            auth_code = result['auth_code'].values[0]
            acquirer_code = result['acquirer_code'].values[0]
            issuer_code = result['issuer_code'].values[0]
            org_code_txn = result['org_code'].values[0]
            rrn_original = result['rr_number'].iloc[0]
            txn_type_original = result['txn_type'].values[0]

            logger.debug(f"Fetching Transaction id from db query : {txn_id_original} ")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": username, "password": password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id_original)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            logger.debug(f"response : response")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(txn_id_original) +"'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            refund_auth_code = result['auth_code'].values[0]
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            rrn_refunded = result['rr_number'].iloc[0]
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_id : {txn_id_refunded}, rrn : {rrn_refunded} ")

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED_REFUNDED",
                    "refund_pmt_status": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "refund_pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "refund_settle_status": "SETTLED",
                    "txn_id": txn_id_original,
                    "refund_txn_id": txn_id_refunded,
                    "txn_amt": str(amount),
                    "refund_txn_amt": str(amount),
                    "customer_name": customer_name,
                    "refund_customer_name": customer_name,
                    "payer_name": payer_name,
                    "refund_payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "refund_pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(rrn_original),
                    "refund_rrn": str(rrn_refunded),
                    "auth_code": auth_code,
                    "refund_auth_code": refund_auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                logger.info("resetting the app after sending the request for refund")
                app_driver.reset()

                logger.info(f"Logging in the MPOSX application using username : {username}")
                login_page.perform_login(username, password)
                home_page = HomePage(app_driver)

                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_auth_code_refunded = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_refunded}, {app_auth_code_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_original}, {app_auth_code_original}")
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
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "refund_pmt_status": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "refund_pmt_mode": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "refund_settle_status": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "refund_txn_id": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "refund_txn_amt": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "refund_customer_name": customer_name,
                    "payer_name": payer_name,
                    "refund_payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "refund_pmt_msg": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "refund_rrn": str(app_rrn_refunded),
                    "auth_code": app_auth_code_original,
                    "refund_auth_code": app_auth_code_refunded,
                    "date": app_date_and_time
                }

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id {testcase_id}")

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
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "refunded_pmt_status": "REFUNDED",
                    "original_pmt_state": "REFUNDED",
                    "refunded_pmt_state": "REFUNDED",
                    "original_pmt_mode": "UPI",
                    "refunded_pmt_mode": "UPI",
                    "original_settle_status": "SETTLED",
                    "refunded_settle_status": "SETTLED",
                    "original_amt": str(amount),
                    "refunded_amt": str(amount),
                    "original_customer_name": customer_name,
                    "refunded_customer_name": customer_name,
                    "original_payer_name": payer_name,
                    "refunded_payer_name": payer_name,
                    "original_order_id": order_id,
                    "original_rrn": str(rrn_original),
                    "refunded_rrn": str(rrn_refunded),
                    "original_acquirer_code": "HDFC",
                    "original_issuer_code": "HDFC",
                    "original_txn_type": txn_type_original,
                    "original_mid": mid, "original_tid": tid,
                    "original_org_code": org_code_txn,
                    "refunded_acquirer_code": "HDFC",
                    # "issuer_code_refunded": "HDFC",
                    "refunded_txn_type": txn_type_refunded,
                    "refunded_mid": mid, "refunded_tid": tid,
                    "refunded_org_code": org_code_txn,
                    "refund_auth_code": refund_auth_code,
                    "original_auth_code": auth_code,
                    "date": date
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_original})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]
                state_api_original = response["states"][0]
                settlement_status_api_original = response["settlementStatus"]
                issuer_code_api_original = response["issuerCode"]
                acquirer_code_api_original = response["acquirerCode"]
                org_code_api_original = response["orgCode"]
                mid_api_original = response["mid"]
                tid_api_original = response["tid"]
                txn_type_api_original = response["txnType"]
                auth_code_api_original = response["authCode"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_refunded})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                rrn_api_refunded = response["rrNumber"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                # issuer_code_api_refunded = response["issuerCode"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                auth_code_api_refunded = response["authCode"]
                date_api_refunded = response["postingDate"]

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "refunded_pmt_status": status_api_refunded,
                    "original_pmt_state": state_api_original,
                    "refunded_pmt_state": state_api_refunded,
                    "original_pmt_mode": payment_mode_api_original,
                    "refunded_pmt_mode": payment_mode_api_refunded,
                    "original_settle_status": settlement_status_api_original,
                    "refunded_settle_status": settlement_status_api_refunded,
                    "original_amt": str(amount_api_original),
                    "refunded_amt": str(amount_api_refunded),
                    "original_customer_name": customer_name,
                    "refunded_customer_name": customer_name,
                    "original_payer_name": payer_name,
                    "refunded_payer_name": payer_name,
                    "original_order_id": order_id,
                    "original_rrn": str(rrn_api_original),
                    "refunded_rrn": str(rrn_api_refunded),
                    "original_acquirer_code": acquirer_code_api_original,
                    "original_issuer_code": issuer_code_api_original,
                    "original_txn_type": txn_type_api_original,
                    "original_mid": mid_api_original, "original_tid": tid_api_original,
                    "original_org_code": org_code_api_original,
                    "refunded_acquirer_code": acquirer_code_api_refunded,
                    # "issuer_code_refunded": issuer_code_api_refunded,
                    "refunded_txn_type": txn_type_api_refunded,
                    "refunded_mid": mid_api_refunded, "refunded_tid": tid_api_refunded,
                    "refunded_org_code": org_code_api_refunded,
                    "refund_auth_code": auth_code_api_refunded,
                    "original_auth_code": auth_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_refunded)
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "refunded_pmt_status": "REFUNDED",
                    "refunded_pmt_state": "REFUNDED",
                    "original_pmt_state": "REFUNDED",
                    "original_pmt_mode": "UPI",
                    "refunded_pmt_mode": "UPI",
                    "original_amt": amount,
                    "refunded_amt": amount,
                    "original_upi_txn_status": "AUTHORIZED_REFUNDED",
                    "refunded_upi_txn_status": "REFUNDED",
                    "original_settle_status": "SETTLED",
                    "refunded_settle_status": "SETTLED",
                    "original_acquirer_code": "HDFC",
                    "refunded_acquirer_code": "HDFC",
                    "original_bank_code": "HDFC",
                    "bank_code_refunded": "HDFC",
                    "original_pmt_gateway": "HDFC",
                    "refunded_pmt_gateway": "HDFC",
                    "original_upi_txn_type": "PAY_QR",
                    "refunded_upi_txn_type": "REFUND",
                    "original_upi_bank_code": "HDFC",
                    "refunded_upi_bank_code": "HDFC",
                    "original_upi_mc_id": upi_mc_id,
                    "refunded_upi_mc_id": upi_mc_id,
                    "original_mid": mid,
                    "original_tid": tid,
                    "refund_mid": mid,
                    "refund_tid": tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                bank_code_db_refunded = result["bank_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "refunded_pmt_status": status_db_refunded,
                    "original_pmt_state": state_db_original,
                    "refunded_pmt_state": state_db_refunded,
                    "original_pmt_mode": payment_mode_db_original,
                    "refunded_pmt_mode": payment_mode_db_refunded,
                    "original_amt": amount_db_original,
                    "refunded_amt": amount_db_refunded,
                    "original_upi_txn_status": upi_status_db_original,
                    "refunded_upi_txn_status": upi_status_db_refunded,
                    "original_settle_status": settlement_status_db_original,
                    "refunded_settle_status": settlement_status_db_refunded,
                    "original_acquirer_code": acquirer_code_db_original,
                    "refunded_acquirer_code": acquirer_code_db_refunded,
                    "original_bank_code": bank_code_db_original,
                    "bank_code_refunded": bank_code_db_refunded,
                    "original_pmt_gateway": payment_gateway_db_original,
                    "refunded_pmt_gateway": payment_gateway_db_refunded,
                    "original_upi_txn_type": upi_txn_type_db_original,
                    "refunded_upi_txn_type": upi_txn_type_db_refunded,
                    "original_upi_bank_code": upi_bank_code_db_original,
                    "refunded_upi_bank_code": upi_bank_code_db_refunded,
                    "original_upi_mc_id": upi_mc_id_db_original,
                    "refunded_upi_mc_id": upi_mc_id_db_refunded,
                    "original_mid": mid_db_original,
                    "original_tid": tid_db_original,
                    "refund_mid": mid_db_refunded,
                    "refund_tid": tid_db_refunded,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

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
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {"refunded_pmt_state": "Refunded", "original_pmt_mode": "UPI",
                                          "original_pmt_amt": str(amount),
                                          "original_pmt_state": "Authorized Refunded",
                                          "Amount Original": str(amount), "refunded_pmt_mode": "UPI"}

                logger.debug(f"expected_portal_values : {expected_portal_values} for the testcase_id {testcase_id}")

                driver_ui = TestSuiteSetup.initialize_portal_driver()

                login_page_portal = PortalLoginPage(driver_ui)

                logger.info(f"Logging in Portal using username : {portal_username}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(driver_ui)
                home_page_portal.search_merchant_name(str(org_code))
                logger.info(f"Switching to merchant : {org_code}")
                home_page_portal.click_switch_button(org_code)
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(driver_ui)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id_refunded)
                portal_txn_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amt = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id_original)
                portal_txn_type_original = portal_values_dict['Type']
                portal_status_original = portal_values_dict['Status']
                portal_amt_original = portal_values_dict['Total Amount']
                portal_username_original = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")

                actual_portal_values = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                        "Payment amount": str(portal_amt.split('.')[1]),
                                        "Payment Status Original": portal_status_original,
                                        "Amount Original": str(portal_amt_original.split('.')[1]),
                                        "Payment Mode Original": portal_txn_type_original}

                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id {testcase_id}")

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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_chargeslip_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(rrn_refunded),
                                              'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                              'date': txn_date, 'time': txn_time,
                                              'AUTH CODE': refund_auth_code}

                logger.debug(
                    f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": username, "password": password},
                                                                  expected_chargeslip_values)

            except Exception as e:
                ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_chargeslip_val_result = False
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
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")
        # Write the code here to revert the settings that were done as precondition
        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_046():
    """
    Sub Feature Code: UI_Common_PM_Pure_UPI_Refund_Failed_via_API_AXIS_DIRECT
    Sub Feature Description: Verification of a refund failed using api for AXIS_DIRECT
    100: Payment Method
    101: UPI
    042: TC042
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
        username = app_cred['Username']
        password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
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
            logger.info(f"Logging in the MPOSX application using username : {username}")
            login_page.perform_login(username, password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")

            amount = 333
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Order id : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")

            payment_page = PaymentPage(app_driver)

            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status_refunded = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status_refunded}")
            payment_page.click_on_proceed_homepage()

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_original = result["id"].iloc[0]
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"Fetched original transaction id : {txn_id_original}, original rrn : {rrn_original} ")
            logger.info("sending request to perform refund of the transaction using api")

            api_details = DBProcessor.get_api_details(
                'paymentRefund', request_body={"username": username, "password": password, "amount": amount,
                                               "originalTransactionId": str(txn_id_original)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            logger.debug(f"response : response")
            logger.debug(f"apiMessage : {response['apiMessage']}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id='" + txn_id_original + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetched Refunded transaction id from txn table is : {txn_id_refunded}")

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
                expected_app_values = {"refunded_txn_status": "STATUS:FAILED",
                                       "refunded_txn_mode": "UPI",
                                       "refunded_txn_id": txn_id_refunded,
                                       "refunded_txn_amt": str(amount),
                                       "original_txn_status": "STATUS:AUTHORIZED",
                                       "original_txn_mode": "UPI",
                                       "original_txn_id": txn_id_original,
                                       "original_txn_amt": str(amount),
                                       "original_txn_rrn": str(rrn_original)
                                       }
                logger.debug(f"expected_app_values : {expected_app_values} for the test case {testcase_id}")

                logger.info("resetting the app after sending the request for refund")
                app_driver.reset()

                logger.info(f"Logging in the MPOSX application using username : {username}")
                login_page.perform_login(username, password)
                home_page = HomePage(app_driver)

                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_original)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_original}")
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

                actual_app_values = {"refunded_txn_status": app_payment_status_refunded,
                                     "refunded_txn_mode": app_payment_mode_refunded,
                                     "refunded_txn_id": app_txn_id_refunded,
                                     "refunded_txn_amt": str(app_payment_amt_refunded),
                                     "original_txn_status": app_payment_status_original,
                                     "original_txn_mode": app_payment_mode_original,
                                     "original_txn_id": txn_id_original,
                                     "original_txn_amt": str(app_payment_amt_original),
                                     "original_txn_rrn": str(app_rrn_original)
                                     }
                logger.debug(f"actual_app_values : {actual_app_values} for the test case {testcase_id}")
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
                expected_api_values = {"refunded_txn_status": "FAILED",
                                       "refunded_txn_amt": amount,
                                       "refunded_txn_mode": "UPI",
                                       "original_txn_status": "AUTHORIZED",
                                       "original_txn_amt": amount,
                                       "original_txn_mode": "UPI",
                                       "original_txn_rrn": str(rrn_original)
                                       }
                logger.debug(f"expected_api_values : {expected_api_values} for the test case {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_original})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_refunded})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]

                logger.debug(
                    f"Fetching Transaction status of refunded txn from transaction api : {status_api_refunded}")
                logger.debug(
                    f"Fetching Transaction amount of refunded txn from transaction api : {amount_api_refunded}")
                logger.debug(
                    f"Fetching Transaction payment of refunded txn mode from transaction api : {payment_mode_api_refunded}")
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction api : {status_api_original}")
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction api : {amount_api_original}")
                logger.debug(
                    f"Fetching Transaction payment of original txn mode from transaction api : {payment_mode_api_original}")

                actual_api_values = {"refunded_txn_status": status_api_refunded,
                                     "refunded_txn_amt": amount_api_refunded,
                                     "refunded_txn_mode": payment_mode_api_refunded,
                                     "original_txn_status": status_api_original,
                                     "original_txn_amt": amount_api_original,
                                     "original_txn_mode": payment_mode_api_original,
                                     "original_txn_rrn": str(rrn_api_original)
                                     }
                logger.debug(f"actual_api_values : {actual_api_values} for the test case {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {"refunded_txn_status": "FAILED",
                                      "refunded_txn_mode": "UPI",
                                      "refunded_txn_amt": amount,
                                      "original_txn_status": "AUTHORIZED",
                                      "original_txn_amt": amount,
                                      "original_txn_mode": "UPI",
                                      "refunded_upi_txn_status": "FAILED",
                                      "refunded_upi_txn_bank_code": "HDFC",
                                      "refunded_upi_txn_type": "REFUND",
                                      "original_upi_txn_status": "AUTHORIZED",
                                      "original_upi_txn_bank_code": "HDFC",
                                      "original_upi_txn_type": "PAY_QR",
                                      }

                logger.debug(f"expected_db_values : {expected_db_values} for the test case {testcase_id}")

                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference from DB : {query}")
                logger.debug(f"Query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db_refunded} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_refunded} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_refunded} ")

                query = "select status,bank_code,txn_type from upi_txn where txn_id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]

                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_original + "'"
                logger.debug(
                    f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
                logger.debug(f"Query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB of original txn : {result} ")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")

                query = "select status,bank_code,txn_type from upi_txn where txn_id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]

                actual_db_values = {"refunded_txn_status": status_db_refunded,
                                    "refunded_txn_mode": payment_mode_db_refunded,
                                    "refunded_txn_amt": amount_db_refunded,
                                    "original_txn_status": status_db_original,
                                    "original_txn_amt": amount_db_original,
                                    "original_txn_mode": payment_mode_db_original,
                                    "refunded_upi_txn_status": upi_status_db_refunded,
                                    "refunded_upi_txn_bank_code": upi_bank_code_db_refunded,
                                    "refunded_upi_txn_type": upi_txn_type_db_refunded,
                                    "original_upi_txn_status": upi_status_db_original,
                                    "original_upi_txn_bank_code": upi_bank_code_db_original,
                                    "original_upi_txn_type": upi_txn_type_db_original,
                                    }
                logger.debug(f"actual_db_values : {actual_db_values} for the test case {testcase_id}")

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
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {}

                actual_portal_values = {}

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
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn_original),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                receipt_validator.perform_charge_slip_validations(txn_id_original,
                                                                  {"username": username, "password": password},
                                                                  expected_values)

            except Exception as e:
                ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_chargeslip_val_result = False
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
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")
        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "' and bank_code='AXIS_DIRECT'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_047():
    """
    Sub Feature Code: UI_Common_PM_Pure_UPI_Refund_Failed_via_API_AXIS_DIRECT
    Sub Feature Description: Verification of a refund failed using api for AXIS_DIRECT
    100: Payment Method
    101: UPI
    042: TC042
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
        username = app_cred['Username']
        password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
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
            logger.info(f"Logging in the MPOSX application using username : {username}")
            login_page.perform_login(username, password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")

            amount = 555
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Order id : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")

            payment_page = PaymentPage(app_driver)

            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status_refunded = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status_refunded}")
            payment_page.click_on_proceed_homepage()

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_original = result["id"].iloc[0]
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"Fetched original transaction id : {txn_id_original}, original rrn : {rrn_original} ")
            logger.info("sending request to perform refund of the transaction using api")

            api_details = DBProcessor.get_api_details(
                'paymentRefund', request_body={"username": username, "password": password, "amount": amount,
                                               "originalTransactionId": str(txn_id_original)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            logger.debug(f"response : response")
            logger.debug(f"apiMessage : {response['apiMessage']}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id='" + txn_id_original + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetched Refunded transaction id from txn table is : {txn_id_refunded}")

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
                expected_app_values = {"refunded_txn_status": "STATUS:REFUND_POSTED",
                                       "refunded_txn_mode": "UPI",
                                       "refunded_txn_id": txn_id_refunded,
                                       "refunded_txn_amt": str(amount),
                                       "original_txn_status": "STATUS:AUTHORIZED",
                                       "original_txn_mode": "UPI",
                                       "original_txn_id": txn_id_original,
                                       "original_txn_amt": str(amount),
                                       "original_txn_rrn": str(rrn_original)
                                       }
                logger.debug(f"expected_app_values : {expected_app_values} for the test case {testcase_id}")

                logger.info("resetting the app after sending the request for refund")
                app_driver.reset()

                logger.info(f"Logging in the MPOSX application using username : {username}")
                login_page.perform_login(username, password)
                home_page = HomePage(app_driver)

                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_original)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_original}")
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

                actual_app_values = {"refunded_txn_status": app_payment_status_refunded,
                                     "refunded_txn_mode": app_payment_mode_refunded,
                                     "refunded_txn_id": app_txn_id_refunded,
                                     "refunded_txn_amt": str(app_payment_amt_refunded),
                                     "original_txn_status": app_payment_status_original,
                                     "original_txn_mode": app_payment_mode_original,
                                     "original_txn_id": txn_id_original,
                                     "original_txn_amt": str(app_payment_amt_original),
                                     "original_txn_rrn": str(app_rrn_original)
                                     }
                logger.debug(f"actual_app_values : {actual_app_values} for the test case {testcase_id}")
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
                expected_api_values = {"refunded_txn_status": "REFUND_POSTED",
                                       "refunded_txn_amt": amount,
                                       "refunded_txn_mode": "UPI",
                                       "original_txn_status": "AUTHORIZED",
                                       "original_txn_amt": amount,
                                       "original_txn_mode": "UPI",
                                       "original_txn_rrn": str(rrn_original)
                                       }
                logger.debug(f"expected_api_values : {expected_api_values} for the test case {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_original})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_refunded})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]

                logger.debug(
                    f"Fetching Transaction status of refunded txn from transaction api : {status_api_refunded}")
                logger.debug(
                    f"Fetching Transaction amount of refunded txn from transaction api : {amount_api_refunded}")
                logger.debug(
                    f"Fetching Transaction payment of refunded txn mode from transaction api : {payment_mode_api_refunded}")
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction api : {status_api_original}")
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction api : {amount_api_original}")
                logger.debug(
                    f"Fetching Transaction payment of original txn mode from transaction api : {payment_mode_api_original}")

                actual_api_values = {"refunded_txn_status": status_api_refunded,
                                     "refunded_txn_amt": amount_api_refunded,
                                     "refunded_txn_mode": payment_mode_api_refunded,
                                     "original_txn_status": status_api_original,
                                     "original_txn_amt": amount_api_original,
                                     "original_txn_mode": payment_mode_api_original,
                                     "original_txn_rrn": str(rrn_api_original)
                                     }
                logger.debug(f"actual_api_values : {actual_api_values} for the test case {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {"refunded_txn_status": "REFUND_POSTED",
                                      "refunded_txn_mode": "UPI",
                                      "refunded_txn_amt": amount,
                                      "original_txn_status": "AUTHORIZED",
                                      "original_txn_amt": amount,
                                      "original_txn_mode": "UPI",
                                      "refunded_upi_txn_status": "REFUND_POSTED",
                                      "refunded_upi_txn_bank_code": "HDFC",
                                      "refunded_upi_txn_type": "REFUND",
                                      "original_upi_txn_status": "AUTHORIZED",
                                      "original_upi_txn_bank_code": "HDFC",
                                      "original_upi_txn_type": "PAY_QR",
                                      }

                logger.debug(f"expected_db_values : {expected_db_values} for the test case {testcase_id}")

                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference from DB : {query}")
                logger.debug(f"Query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db_refunded} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_refunded} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_refunded} ")

                query = "select status,bank_code,txn_type from upi_txn where txn_id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]

                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_original + "'"
                logger.debug(
                    f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
                logger.debug(f"Query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB of original txn : {result} ")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")

                query = "select status,bank_code,txn_type from upi_txn where txn_id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]

                actual_db_values = {"refunded_txn_status": status_db_refunded,
                                    "refunded_txn_mode": payment_mode_db_refunded,
                                    "refunded_txn_amt": amount_db_refunded,
                                    "original_txn_status": status_db_original,
                                    "original_txn_amt": amount_db_original,
                                    "original_txn_mode": payment_mode_db_original,
                                    "refunded_upi_txn_status": upi_status_db_refunded,
                                    "refunded_upi_txn_bank_code": upi_bank_code_db_refunded,
                                    "refunded_upi_txn_type": upi_txn_type_db_refunded,
                                    "original_upi_txn_status": upi_status_db_original,
                                    "original_upi_txn_bank_code": upi_bank_code_db_original,
                                    "original_upi_txn_type": upi_txn_type_db_original,
                                    }
                logger.debug(f"actual_db_values : {actual_db_values} for the test case {testcase_id}")

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
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {}

                actual_portal_values = {}

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
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn_original),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                receipt_validator.perform_charge_slip_validations(txn_id_original,
                                                                  {"username": username, "password": password},
                                                                  expected_values)

            except Exception as e:
                ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_chargeslip_val_result = False
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
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")
        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "' and bank_code='AXIS_DIRECT'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")
