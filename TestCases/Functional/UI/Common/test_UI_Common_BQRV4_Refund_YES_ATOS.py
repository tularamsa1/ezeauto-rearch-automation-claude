import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


# @pytest.mark.usefixtures("log_on_success", "method_setup")
# @pytest.mark.apiVal
# @pytest.mark.dbVal
# @pytest.mark.portalVal
# @pytest.mark.appVal
# @pytest.mark.chargeSlipVal
# def test_common_100_102_062():
#     """
#     :Description: Verification of a BQRV4 Refund transaction via YES_ATOS
#     :Sub feature code: UI_Common_BQRV4_Refund_via_YES_ATOS_062
#     :TC naming code description:100->Payment Method, 102->BQR, 062-> TC062
#     """
#     try:
#         testcase_id = sys._getframe().f_code.co_name
#         GlobalVariables.time_calc.setup.resume()
#         print(
#             colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
#         # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
#         logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
#
#         app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
#         logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
#         username = app_cred['Username']
#         password = app_cred['Password']
#
#         portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
#         logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
#         portal_username = portal_cred['Username']
#         portal_password = portal_cred['Password']
#
#         query = "select org_code from org_employee where username='" + str(username) + "';"
#         logger.debug(f"Query to fetch org_code from the DB : {query}")
#         result = DBProcessor.getValueFromDB(query)
#         org_code = result['org_code'].values[0]
#         logger.debug(f"Query result, org_code : {org_code}")
#
#         testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')
#
#         api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
#                                                                                "password": portal_password,
#                                                                                "settingForOrgCode": org_code})
#         api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
#         logger.debug(f"API details  : {api_details} ")
#         response = APIProcessor.send_request(api_details)
#         logger.debug(f"Response received for setting preconditions is : {response}")
#
#         query = "select mid from terminal_info where org_code='" + org_code + "' and acquirer_code='YES'"
#         result = DBProcessor.getValueFromDB(query)
#         mid = result["mid"].iloc[0]
#         logger.debug(f"Fetching mid from database for current merchant:{mid}")
#
#         GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
#         logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
#         # ---------------------------------------------------------------------------------------------------------
#         # Set the below variables depending on the log capturing need of the test case.
#         Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)
#
#         # Variable which tracks if the execution is going on through all the lines of code of test case.
#         # Set to failure where ever there are chances of failure.
#         msg = ""
#         GlobalVariables.time_calc.setup.end()
#         print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
#
#         # -----------------------------------------Start of Test Execution-------------------------------------
#         try:
#             logger.info(f"Starting execution for the test case : {testcase_id}")
#             GlobalVariables.time_calc.execution.start()
#             print(
#                 colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
#                         'cyan'))
#
#             amount = random.randint(301, 400)
#             order_id = datetime.now().strftime('%m%d%H%M%S')
#             logger.debug("Generating QR using BQR QR generate APi")
#             api_details = DBProcessor.get_api_details('bqrGenerate',
#                                                       request_body={"username": username, "password": password,
#                                                                     "amount": str(amount),
#                                                                     "orderNumber": str(order_id)})
#             response = APIProcessor.send_request(api_details)
#             logger.debug(f"Resonse recived for QR genration api is : {response}")
#             query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
#             logger.debug(f"Query to fetch transaction id from database : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             txn_id = result["id"].iloc[0]
#             logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
#             api_details = DBProcessor.get_api_details('stopPayment',
#                                                       request_body={"username": username, "password": password,
#                                                                     "orgCode":org_code ,"txnId": txn_id})
#             response = APIProcessor.send_request(api_details)
#             print("Response received:", response)
#             logger.info("Opening Portal to perform refund of the transaction")
#             ui_driver = TestSuiteSetup.initialize_portal_driver()
#             loginPagePortal = PortalLoginPage(ui_driver)
#             logger.info(f"Logging in Portal using username : {portal_username}")
#             loginPagePortal.perform_login_to_portal(portal_username, portal_password)
#             homePagePortal = PortalHomePage(ui_driver)
#             homePagePortal.search_merchant_name(str(org_code))
#             logger.info(f"Switching to merchant : {org_code}")
#             homePagePortal.click_switch_button(str(org_code))
#             homePagePortal.click_transaction_search_menu()
#             logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
#             homePagePortal.click_on_transaction_details_based_on_transaction_id(txn_id)
#             logger.debug("Clicking on refund button")
#             homePagePortal.click_on_refund_button()
#             homePagePortal.perform_refund_of_txn(amount)
#             logger.info("Performing Page refresh after refund is performed")
#             query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
#             logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             txn_id_refunded = result["id"].iloc[0]
#             rrn = result['rr_number'].iloc[0]
#             logger.debug(f"Fetching Transaction id, rrn from db query, txn_id : {txn_id_refunded}, rrn : {rrn} ")
#             # ------------------------------------------------------------------------------------------------
#             GlobalVariables.EXCEL_TC_Execution = "Pass"
#             GlobalVariables.time_calc.execution.pause()
#             print(colored(
#                 "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
#                                                                                   "="), 'cyan'))
#             logger.info(f"Execution is completed for the test case : {testcase_id}")
#         except Exception as e:
#             if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
#                 GlobalVariables.time_calc.execution.pause()
#                 print(colored(
#                     "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
#                         shutil.get_terminal_size().columns, "="), 'cyan'))
#             GlobalVariables.time_calc.execution.resume()
#             print(colored("Execution Timer resumed in execpt block of testcase function".center(
#                 shutil.get_terminal_size().columns, "="), 'cyan'))
#
#             ReportProcessor.capture_ss_when_app_val_exe_failed()
#             ReportProcessor.capture_ss_when_portal_val_exe_failed()
#             GlobalVariables.EXCEL_TC_Execution = "Fail"
#             GlobalVariables.Incomplete_ExecutionCount += 1
#
#             GlobalVariables.time_calc.execution.pause()
#             print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
#                 shutil.get_terminal_size().columns, "="), 'cyan'))
#
#             logger.exception(f"Execution is completed for the test case : {testcase_id}")
#             pytest.fail("Test case execution failed due to the exception -" + str(e))
#         # -----------------------------------------End of Test Execution--------------------------------------
#         # -----------------------------------------Start of Validation----------------------------------------
#         logger.info(f"Starting Validation for the test case : {testcase_id}")
#         GlobalVariables.time_calc.validation.start()
#         print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
#                       'cyan'))
#
#         # -----------------------------------------Start of App Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "app_validation")) == "True":
#             logger.info(f"Started APP validation for the test case : {testcase_id}")
#             try:
#                 expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "UPI",
#                                      "Payment Txn ID": txn_id_refunded, "Payment Amt": str(amount),
#                                      "Payment Status Original": "STATUS:AUTHORIZED_REFUNDED",
#                                      "Payment mode Original": "UPI", "Payment Txn ID Original": txn_id,
#                                      "Payment Amt Original": str(amount), "rrn":str(rrn)}
#                 app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
#                 loginPage = LoginPage(app_driver)
#                 logger.info(f"Logging in the MPOSX application using username : {username}")
#                 loginPage.perform_login(username, password)
#                 homePage = HomePage(app_driver)
#                 homePage.wait_for_navigation_to_load()
#                 homePage.wait_for_home_page_load()
#                 homePage.check_home_page_logo()
#                 logger.info(f"App homepage loaded successfully")
#                 homePage.click_on_history()
#                 transactionsHistoryPage = TransHistoryPage(app_driver)
#                 transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
#                 app_rrn = transactionsHistoryPage.fetch_RRN_text()
#                 logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn}")
#                 app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
#                 logger.debug(
#                     f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
#                 app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
#                 logger.debug(
#                     f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
#                 app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
#                 logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
#                 app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
#                 logger.debug(
#                     f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
#                 transactionsHistoryPage.click_back_Btn_transaction_details()
#                 transactionsHistoryPage.click_on_second_transaction_by_order_id(order_id)
#                 app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
#                 logger.debug(
#                     f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
#                 app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
#                 logger.debug(
#                     f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
#                     f"Mode = {app_payment_mode_original}")
#                 app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
#                 logger.debug(
#                     f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
#                 app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
#                 logger.debug(
#                     f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
#
#                 actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode,
#                                    "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),
#                                    "Payment Status Original": app_payment_status_original,
#                                    "Payment mode Original": app_payment_mode_original,
#                                    "Payment Txn ID Original": txn_id,
#                                    "Payment Amt Original": str(app_payment_amt_original), "rrn":str(app_rrn)}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_app_val_exe_failed()
#                 print("App Validation failed due to exception - " + str(e))
#                 logger.exception(f"App Validation failed due to exception - {e}")
#                 msg = msg + "App Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_app_val_result = "Fail"
#             logger.info(f"Completed APP validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of App Validation---------------------------------------
#
#         # -----------------------------------------Start of API Validation------------------------------------
#         if (ConfigReader.read_config("Validations", "api_validation")) == "True":
#             logger.info(f"Started API validation for the test case : {testcase_id}")
#             try:
#                 expectedAPIValues = {"Payment Status": "REFUNDED", "Amount": amount, "Payment Mode": "UPI",
#                                      "Payment Status Original": "AUTHORIZED_REFUNDED", "Amount Original": amount,
#                                      "Payment Mode Original": "UPI", "rrn":str(rrn)}
#                 api_details = DBProcessor.get_api_details('txnDetails',
#                                                           request_body={"username": username, "password": password,
#                                                                         "txnId": txn_id})
#                 print("API DETAILS for original txn:", api_details)
#                 response = APIProcessor.send_request(api_details)
#                 logger.debug(f"Response received for transaction details api is : {response}")
#                 print(response)
#                 status_api_orginal = response["status"]
#                 amount_api_original = int(response["amount"])
#                 payment_mode_api_orginal = response["paymentMode"]
#
#                 api_details = DBProcessor.get_api_details('txnDetails',
#                                                           request_body={"username": username, "password": password,
#                                                                         "txnId": txn_id_refunded})
#                 print("API DETAILS for refunded txn:", api_details)
#                 response = APIProcessor.send_request(api_details)
#                 logger.debug(f"Response received for transaction details api is : {response}")
#                 print(response)
#                 status_api = response["status"]
#                 amount_api = int(response["amount"])
#                 payment_mode_api = response["paymentMode"]
#                 rrn_api = response["rrNumber"]
#
#                 logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
#                 logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
#                 logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
#                 logger.debug(
#                     f"Fetching Transaction status of original txn from transaction api : {status_api_orginal} ")
#                 logger.debug(
#                     f"Fetching Transaction amount of original txn from transaction api : {amount_api_original} ")
#                 logger.debug(
#                     f"Fetching Transaction payment of original txn mode from transaction api : {payment_mode_api_orginal} ")
#                 #
#                 actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,
#                                    "Payment Status Original": status_api_orginal,
#                                    "Amount Original": amount_api_original,
#                                    "Payment Mode Original": payment_mode_api_orginal, "rrn":str(rrn_api)}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
#             except Exception as e:
#                 print("API Validation failed due to exception - " + str(e))
#                 logger.exception(f"API Validation failed due to exception : {e} ")
#                 msg = msg + "API Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_api_val_result = "Fail"
#             logger.info(f"Completed API validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of API Validation---------------------------------------
#
#         # -----------------------------------------Start of DB Validation--------------------------------------
#         if (ConfigReader.read_config("Validations", "db_validation")) == "True":
#             logger.info(f"Started DB validation for the test case : {testcase_id}")
#             try:
#                 expectedDBValues = {"Payment Status": "REFUNDED", "Payment mode": "UPI", "Payment amount": amount,
#                                     "Payment Status Original": "AUTHORIZED_REFUNDED", "Amount Original": amount,
#                                     "Payment Mode Original": "UPI"}
#                 #
#                 query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_refunded + "'"
#                 logger.debug(f"DB query to fetch status, amount, payment mode and external reference from DB : {query}")
#                 print("Query:", query)
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Fetching Query result from DB : {result} ")
#                 print(result)
#                 status_db = result["status"].iloc[0]
#                 payment_mode_db = result["payment_mode"].iloc[0]
#                 amount_db = int(result["amount"].iloc[0])
#                 logger.debug(f"Fetching Transaction status from DB : {status_db} ")
#                 logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
#                 logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
#                 query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
#                 logger.debug(
#                     f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
#                 print("Query:", query)
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Fetching Query result from DB of original txn : {result} ")
#                 print(result)
#                 status_db_original = result["status"].iloc[0]
#                 payment_mode_db_original = result["payment_mode"].iloc[0]
#                 amount_db_original = int(result["amount"].iloc[0])
#                 logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
#                 logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
#                 logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
#                 # Write the test case DB validation code block here. Set this to pass if not required.
#                 #
#                 actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
#                                   "Payment amount": amount_db, "Payment Status Original": status_db_original,
#                                   "Amount Original": amount_db_original,
#                                   "Payment Mode Original": payment_mode_db_original}
#
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
#             except Exception as e:
#                 print("DB Validation failed due to exception - " + str(e))
#                 logger.exception(f"DB Validation failed due to exception :  {e}")
#                 msg = msg + "DB Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_db_val_result = 'Fail'
#             logger.info(f"Completed DB validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of DB Validation---------------------------------------
#
#         # -----------------------------------------Start of Portal Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
#             logger.info(f"Started Portal validation for the test case : {testcase_id}")
#             try:
#                 expectedPortalValues = {"Payment Status": "Refunded", "Payment mode": "UPI",
#                                         "Payment amount": str(amount), "Payment Status Original": "Authorized Refunded",
#                                         "Amount Original": str(amount), "Payment Mode Original": "UPI"}
#                 #
#                 ui_driver.refresh()
#                 portalTransHistoryPage = PortalTransHistoryPage(ui_driver)
#                 portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id_refunded)
#                 portal_txn_type = portalValuesDict['Type']
#                 portal_status = portalValuesDict['Status']
#                 portal_amt = portalValuesDict['Total Amount']
#                 portal_username = portalValuesDict['Username']
#
#                 logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
#                 logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
#                 logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
#                 logger.debug(f"Fetching Username from portal : {portal_username} ")
#
#                 portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id)
#                 portal_txn_type_original = portalValuesDict['Type']
#                 portal_status_original = portalValuesDict['Status']
#                 portal_amt_original = portalValuesDict['Total Amount']
#                 portal_username_original = portalValuesDict['Username']
#
#                 logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
#                 logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
#                 logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
#                 logger.debug(f"Fetching Username from portal : {portal_username_original} ")
#                 #
#                 actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
#                                       "Payment amount": str(portal_amt.split('.')[1]),
#                                       "Payment Status Original": portal_status_original,
#                                       "Amount Original": str(portal_amt_original.split('.')[1]),
#                                       "Payment Mode Original": portal_txn_type_original}
#
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_portal_val_exe_failed()
#                 print("Portal Validation failed due to exception - " + str(e))
#                 logger.exception(f"Portal Validation failed due to exception : {e}")
#                 msg = msg + "Portal Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_portal_val_result = 'Fail'
#             logger.info(f"Completed Portal validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of Portal Validation---------------------------------------
#
#         # -----------------------------------------Start of ChargeSlip Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
#             logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
#             try:
#                 date = datetime.today().strftime('%Y-%m-%d')
#                 expectedValues = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
#                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
#                 receipt_validator.perform_charge_slip_validations(txn_id_refunded, {"username": username, "password": password},
#                                                                   expectedValues)
#
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
#                 print("Charge Slip Validation failed due to exception - " + str(e))
#                 logger.exception(f"Charge Slip Validation failed due to exception : {e}")
#                 msg = msg + "Charge Slip Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_chargeslip_val_result = "Fail"
#             logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of ChargeSlip Validation---------------------------------------
#         GlobalVariables.time_calc.validation.end()
#         print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
#                       'cyan'))
#         logger.info(f"Completed Validation for the test case : {testcase_id}")
#
#     # -------------------------------------------End of Validation---------------------------------------------
#
#     finally:
#         Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_102_063():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Refund_via_YES_ATOS
    Sub Feature Description: Verification of a BQRV4 Refund transaction via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQR, 063: TC063
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select mid, tid, id from upi_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        upi_mc_id = result["id"].iloc[0]
        logger.debug(f"Fetching mid, tid from database for current merchant:{mid}, {tid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False, config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(301, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Amount and order id for this txn is: {amount}, {order_id}")
            logger.debug("Generating QR using BQR QR generate API")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for QR generation api is : {response}")
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            api_details = DBProcessor.get_api_details('stopPayment',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "orgCode":org_code ,"txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stop payment api is : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            rrn = result['rr_number'].iloc[0]
            posting_date = result['created_time'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching auth_code, rrn, posting_date, customer name and payer name from database for "
                         f"current merchant:{auth_code}, {rrn}, {posting_date}, {customer_name}, {payer_name}")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            auth_code_refunded = result['auth_code'].values[0]
            rrn_refunded = result['rr_number'].iloc[0]
            posting_date_refunded = result['created_time'].values[0]
            logger.debug(f"Fetching auth_code, rrn, txn_id, and posting date from database for "
                 f"current merchant:{auth_code_refunded}, {rrn_refunded}, {txn_id_refunded}, {posting_date_refunded}")

            # ------------------------------------------------------------------------------------------------
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
                date_and_time = date_time_converter.to_app_format(posting_date)
                refund_date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED REFUNDED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": txn_id_refunded,
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_amt_2": "{:.2f}".format(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "REFUND SUCCESSFUL",
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "rrn": str(rrn),
                    "rrn_2": str(rrn_refunded),
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "date_2": refund_date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)
                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
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
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_refunded}")
                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code_original}")
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
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

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
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "rrn_2": str(app_rrn_refunded),
                    "auth_code": app_auth_code_original,
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_refunded
                }

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)
                refund_date = date_time_converter.db_datetime(posting_date_refunded)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn),
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "acquirer_code_2": "YES",
                    "txn_type_2": "REFUND",
                    "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code": auth_code,"date": date, "date_2": refund_date
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                amount_api_original = float(response["amount"])
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
                date_api_original = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                rrn_api_refunded = response["rrNumber"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt": amount_api_original,
                    "txn_amt_2": amount_api_refunded,
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original, "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded, "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "auth_code": auth_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

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
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "YES",
                    "acquirer_code_2": "YES",
                    "bank_code": "YES",
                    "pmt_gateway": "ATOS",
                    "pmt_gateway_2": "ATOS",
                    "upi_txn_type": "PAY_BQR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "YES",
                    "upi_bank_code_2": "YES",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = float(result["amount"].iloc[0])
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
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

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = float(result["amount"].iloc[0])
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db_original,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db_original,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db_original,
                    "pmt_gateway": payment_gateway_db_original,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id": upi_mc_id_db_original,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid": mid_db_original,
                    "tid": tid_db_original,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(posting_date)
                date_and_time_portal_2 = date_time_converter.to_portal_format(posting_date_refunded)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "auth_code_2": "-" if auth_code_refunded is None else auth_code_refunded,
                    "rrn_2": "-" if rrn_refunded is None else rrn_refunded
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
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
                }
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_refunded)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_refunded),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",  'date': txn_date,'time': txn_time}
                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_values)
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
