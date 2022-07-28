import random
import shutil
import sys
from datetime import datetime
import pytest
from termcolor import colored
from Configuration import TestSuiteSetup, Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor, receipt_validator, \
    ResourceAssigner, date_time_val
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_050():
    """
    Sub Feature Code: UI_Common_PM_Initiate_BQRV4_qr_via_api_Success_Via_CheckStatus_API_HDFC
    Sub Feature Description: Initiate qr by api and perform checkStatus by api for success using magic number
    100: Payment Method
    101: UPI
    005: TC005
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

        query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                "'" + str(org_code) + "'; "
        logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]
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

            amount = random.randint(201, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)

            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "txnId": str(txn_id)})
            APIProcessor.send_request(api_details)

            api_details = DBProcessor.get_api_details('paymentStatus',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "txnId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            print(response)

            query = "select auth_code,posting_date from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            posting_date = result['posting_date'].values[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

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
                date_and_time = date_time_val.date_and_time_val_against_app(posting_date)
                expected_app_values = {"Payment mode": "UPI", "Status": "AUTHORIZED","Amount": str(amount),
                                       "settlement_status": "SETTLED","txn_id": txn_id, "rrn": str(rrn),
                                       "customer_name": "Test Payer","payer_name": "Test Payer",
                                       "order_id": order_id,"payment_msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code, "date": date_and_time
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
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                     "Amount": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     "customer_name": app_customer_name,"settlement_status": app_settlement_status,
                                     "payer_name": app_payer_name,"order_id": app_order_id,"date": app_date_and_time,
                                     "payment_msg": app_payment_msg, "auth_code": app_auth_code}
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
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_val.db_datetime(posting_date)
                expected_api_values = {"Payment Status": "AUTHORIZED",
                                       "Amount": amount, "Payment Mode": "UPI",
                                       "Payment State": "SETTLED", "rrn": str(rrn),
                                       "settlement_status": "SETTLED",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "CHARGE", "mid": mid, "tid": tid, "org_code": org_code,
                                       "auth_code": auth_code, "date": date
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_api = response["postingDate"]

                actual_api_values = {"Payment Status": status_api, "Amount": amount_api,
                                     "Payment Mode": payment_mode_api,
                                     "Payment State": state_api, "rrn": str(rrn_api),
                                     "settlement_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api, "org_code": orgCode_api,
                                     "auth_code": auth_code_api,
                                     "date": date_time_val.date_and_time_val_against_api(date_api)
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
                expected_db_values = {"Payment amount": amount,"Payment mode": "UPI","Payment Status": "AUTHORIZED",
                                      "Payment State": "SETTLED","Accquirer Code" : "HDFC", "Bank Name" : "HDFC Bank",
                                      "Payer Name": "Test Payer", "MID" :mid, "TID" : tid, "Payment Gateway": "HDFC",
                                      "RR NUMBER" : str(rrn), "Settlement Status": "SETTLED","UPI_Txn_Status": "AUTHORIZED",
                                      "UPI Txn Type": "PAY_BQR", "UPI MC ID": upi_mc_id, "UPI Bank code": "HDFC"}
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = int(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                payer_name_db = result["payer_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                actual_db_values = {"Payment amount": amount_db,"Payment mode": payment_mode_db,
                                    "Payment Status": payment_status_db, "Payment State": payment_state_db,
                                    "Accquirer Code" : acquirer_code_db, "Bank Name" : bank_name_db,
                                    "Payer Name": payer_name_db, "MID" :mid_db, "TID" : tid_db,
                                    "Payment Gateway": payment_gateway_db, "RR NUMBER" : rr_number_db,
                                    "Settlement Status": settlement_status_db,"UPI_Txn_Status": upi_status_db,
                                    "UPI Txn Type": upi_txn_type_db, "UPI MC ID": upi_mc_id_db, "UPI Bank code": upi_bank_code_db}
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
                    f"Logging in to the portal with the app_username : {portal_username} and app_password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.search_merchant_name(str(org_code))
                home_page_portal.wait_for_home_page_load()

                logger.debug(f"searching for the org_code : {str(org_code)}")
                home_page_portal.click_switch_button(str(org_code))
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
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
                txn_date, txn_time = date_time_val.date_and_time_val_against_charge_slip(posting_date)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,'time': txn_time,
                                   'AUTH CODE': auth_code}
                receipt_validator.perform_charge_slip_validations(txn_id,
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