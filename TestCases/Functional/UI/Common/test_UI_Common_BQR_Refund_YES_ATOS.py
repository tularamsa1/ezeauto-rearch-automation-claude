import random
import shutil
import sys
from datetime import datetime
import pytest
from termcolor import colored

from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_035():
    """
    :Description: Verification of a BQR Refund transaction via YES ATOS
    :Sub Feature code: UI_Common_PM_BQR_Refund_YES_ATOS_035
    :TC naming code description: 100->Payment Method
                                102->BQR
                                035-> TC35
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')
        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
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
            loginPage = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(401, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            paymentPage.click_on_back_btn()
            paymentPage.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            paymentPage.click_on_proceed_homepage()
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            loginPagePortal = PortalLoginPage(ui_driver)
            logger.info(f"Logging in Portal using username : {portal_username}")
            loginPagePortal.perform_login_to_portal(portal_username, portal_password)
            homePagePortal = PortalHomePage(ui_driver)
            homePagePortal.search_merchant_name(org_code)
            logger.info(f"Switching to merchant : {org_code}")
            homePagePortal.click_switch_button(org_code)
            homePagePortal.click_transaction_search_menu()
            logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
            homePagePortal.click_on_transaction_details_based_on_transaction_id(txn_id)
            logger.debug("Clicking on refund button")
            homePagePortal.click_on_refund_button()
            homePagePortal.perform_refund_of_txn(amount)
            logger.info("Performing Page refresh after refund is performed")
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            #
            # ------------------------------------------------------------------------------------------------
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
            try:
                logger.info(f"Starting App Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id_refunded, "Payment Amt": str(amount), "Payment Status Original": "STATUS:AUTHORIZED_REFUNDED", "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id, "Payment Amt Original": str(amount)}

                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
                transactionsHistoryPage.click_back_Btn_transaction_details()
                transactionsHistoryPage.click_on_second_transaction_by_order_id(order_id)
                app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn Mode = {app_payment_mode_original}")
                app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt), "Payment Status Original": app_payment_status_original, "Payment mode Original": app_payment_mode_original, "Payment Txn ID Original": txn_id, "Payment Amt Original": str(app_payment_amt_original)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting API Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Payment Status":"REFUNDED","Amount": amount, "Payment Mode": "BHARATQR", "Txn Type":"REFUND", "Acquirer Code":"YES","Payment Status Original":"AUTHORIZED_REFUNDED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_refunded})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                txn_type_api = response["txnType"]
                accuirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api_orginal = response["status"]
                amount_api_original = response["amount"]
                payment_mode_api_orginal = response["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api_orginal} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api_original} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api_orginal} ")
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Txn Type":txn_type_api, "Acquirer Code":accuirer_code_api, "Payment Status Original":status_api_orginal,"Amount Original": amount_api_original, "Payment Mode Original": payment_mode_api_orginal}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting DB Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "REFUNDED", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount),"Txn Type":"REFUND","Acquirer Code":"YES", "Payment Status Original":"AUTHORIZED_REFUNDED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                #
                query = "select status,amount,payment_mode,txn_type,acquirer_code,external_ref from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode,txn_type,acquirer_codeand external reference from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                txn_type_db = result["txn_type"].iloc[0]
                accuirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
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
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db,"Txn Type":txn_type_db, "Acquirer Code":accuirer_code_db, "Payment Status Original":status_db_original,"Amount Original": amount_db_original, "Payment Mode Original": payment_mode_db_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Refunded", "Payment mode":"BHARATQR" , "Payment amount":str(amount), "Payment Status Original":"Authorized Refunded","Amount Original": str(amount), "Payment Mode Original": "BHARATQR"}
                #
                ui_driver.refresh()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id_refunded)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status_original = portalValuesDict['Status']
                portal_txn_type_original = portalValuesDict['Type']
                portal_amt_original = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Payment Status Original":portal_status_original,"Amount Original": str(portal_amt_original.split('.')[1]), "Payment Mode Original": portal_txn_type_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
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
                expectedValues = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                  'RRN': rrn,
                                  'BASE AMOUNT:': 'Rs.' + str(amount) + '.00'}
                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": username, "password": password},
                                                                  expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
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
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_036():
    """
    :Description: Verification of a BQR Refund transaction through API via YES_ATOS
    :Sub Feature code: UI_Common_PM_BQR_Refund_API_YES_ATOS_036
    :TC naming code description: 100->Payment Method
                                102->BQR
                                036-> TC36
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')
        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
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
            loginPage = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(401, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            paymentPage.click_on_back_btn()
            paymentPage.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            paymentPage.click_on_proceed_homepage()
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": username, "password": password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            refund_auth_code = result['auth_code'].values[0]
            rrn_refunded = result['rr_number'].iloc[0]
            posting_date_refunded = result['posting_date'].values[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_id : {txn_id_refunded}")
            #
            # ------------------------------------------------------------------------------------------------
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
            try:
                logger.info("Starting App Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id_refunded, "Payment Amt": str(amount), "Payment Status Original": "STATUS:AUTHORIZED_REFUNDED", "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id, "Payment Amt Original": str(amount)}
                app_driver.reset()
                logger.info(f"Logging in the MPOSX application using username : {username}")
                loginPage.perform_login(username, password)
                homePage = HomePage(app_driver)
                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
                transactionsHistoryPage.click_back_Btn_transaction_details()
                transactionsHistoryPage.click_on_second_transaction_by_order_id(order_id)
                app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn Mode = {app_payment_mode_original}")
                app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt), "Payment Status Original": app_payment_status_original, "Payment mode Original": app_payment_mode_original, "Payment Txn ID Original": txn_id, "Payment Amt Original": str(app_payment_amt_original)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting API Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"REFUNDED","Amount": amount, "Payment Mode": "BHARATQR","Txn Type":"REFUND", "Acquirer Code":"YES", "Payment Status Original":"AUTHORIZED_REFUNDED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_refunded})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                txn_type_api = response["txnType"]
                accuirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api_orginal = response["status"]
                amount_api_original = response["amount"]
                payment_mode_api_orginal = response["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api_orginal} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api_original} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api_orginal} ")
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Txn Type":txn_type_api, "Acquirer Code":accuirer_code_api, "Payment Status Original":status_api_orginal,"Amount Original": amount_api_original, "Payment Mode Original": payment_mode_api_orginal}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting DB Validation for the test case: {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "REFUNDED", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount),"Txn Type":"REFUND","Acquirer Code":"YES", "Payment Status Original":"AUTHORIZED_REFUNDED","Amount Original": "{:.2f}".format(amount), "Payment Mode Original": "BHARATQR"}
                #
                query = "select status,amount,payment_mode,external_ref,txn_type,acquirer_code from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode,txn_type,acquirer_code and external reference from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                txn_type_db = result["txn_type"].iloc[0]
                accuirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB of original txn : {result} ")
                print(result)
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = "{:.2f}".format(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db,"Txn Type":txn_type_db, "Acquirer Code":accuirer_code_db, "Payment Status Original":status_db_original,"Amount Original": amount_db_original, "Payment Mode Original": payment_mode_db_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Refunded", "Payment mode":"BHARATQR" , "Payment amount":str(amount), "Payment Status Original":"Authorized Refunded","Amount Original": str(amount), "Payment Mode Original": "BHARATQR"}
                #
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                loginPagePortal = PortalLoginPage(ui_driver)
                logger.info(f"Logging in Portal using username : {portal_username}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(ui_driver)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id_refunded)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status_original = portalValuesDict['Status']
                portal_txn_type_original = portalValuesDict['Type']
                portal_amt_original = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Payment Status Original":portal_status_original,"Amount Original": str(portal_amt_original.split('.')[1]), "Payment Mode Original": portal_txn_type_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
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
                expectedValues = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                  'RRN': rrn,
                                  'BASE AMOUNT:': 'Rs.' + str(amount) + '.00'}
                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": username, "password": password},
                                                                  expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
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
        Configuration.executeFinallyBlock(testcase_id)
        # ----------------------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_045():
    """
        :Description: Verification of a BQR Refund Failed transaction via YES_ATOS
        :Sub Feature code: UI_Common_PM_BQR_Refund_Failed_YES_ATOS_045
        :TC naming code description: 100->Payment Method,102->BQR,045->TC45
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')
        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
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
            loginPage = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            homePage.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            amount = 444
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            paymentPage.click_on_back_btn()
            paymentPage.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            paymentPage.click_on_proceed_homepage()
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            loginPagePortal = PortalLoginPage(ui_driver)
            logger.info(f"Logging in Portal using username : {portal_username}")
            loginPagePortal.perform_login_to_portal(portal_username, portal_password)
            homePagePortal = PortalHomePage(ui_driver)
            homePagePortal.search_merchant_name(org_code)
            logger.info(f"Switching to merchant : {org_code}")
            homePagePortal.click_switch_button(org_code)
            homePagePortal.click_transaction_search_menu()
            logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
            homePagePortal.click_on_transaction_details_based_on_transaction_id(txn_id)
            logger.debug("Clicking on refund button")
            homePagePortal.click_on_refund_button()
            refund_message=homePagePortal.perform_refund_of_txn_and_fetch_alert_msg(amount)
            logger.debug(f"Message for performing Refund of txn is : {refund_message}")
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            #
            # ------------------------------------------------------------------------------------------------
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
            try:
                logger.info(f"Starting App Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:FAILED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id_refunded, "Payment Amt": str(amount), "Payment Status Original": "STATUS:AUTHORIZED", "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id, "Payment Amt Original": str(amount)}

                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
                transactionsHistoryPage.click_back_Btn_transaction_details()
                transactionsHistoryPage.click_on_second_transaction_by_order_id(order_id)
                app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn Mode = {app_payment_mode_original}")
                app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt), "Payment Status Original": app_payment_status_original, "Payment mode Original": app_payment_mode_original, "Payment Txn ID Original": txn_id, "Payment Amt Original": str(app_payment_amt_original)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting API Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Payment Status":"FAILED","Amount": amount, "Payment Mode": "BHARATQR","Txn Type":"REFUND", "Acquirer Code":"YES","Error Msg":"Bharat QR Refund Failed: ", "Payment Status Original":"AUTHORIZED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_refunded})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                txn_type_api = response["txnType"]
                error_msg_api = response["errorMessage"]
                accuirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(f"Fetching Transaction type from transaction api : {txn_type_api} ")
                logger.debug(f"Fetching Transaction error msg mode from transaction api : {error_msg_api} ")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api_orginal = response["status"]
                amount_api_original = response["amount"]
                payment_mode_api_orginal = response["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api_orginal} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api_original} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api_orginal} ")
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Txn Type":txn_type_api, "Acquirer Code":accuirer_code_api,"Error Msg":error_msg_api,"Payment Status Original":status_api_orginal,"Amount Original": amount_api_original, "Payment Mode Original": payment_mode_api_orginal}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting DB Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment mode":"BHARATQR" ,"Txn Type":"REFUND","Error Message": "Bharat QR Refund Failed: ","Acquirer Code":"YES", "Payment amount":"{:.2f}".format(amount), "Payment Status Original":"AUTHORIZED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                #
                query = "select status,amount,payment_mode,external_ref,txn_type,error_message,acquirer_code from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode,txn_type,error_message,acquirer_code and external reference from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                txn_type_db = result["txn_type"].iloc[0]
                error_msg_db = result["error_message"].iloc[0]
                accuirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                logger.debug(f"Fetching Transaction type from DB : {txn_type_db} ")
                logger.debug(f"Fetching Transaction error msg from DB : {error_msg_db} ")
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
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
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db,"Txn Type":txn_type_db,"Error Message": error_msg_db,"Acquirer Code":accuirer_code_db, "Payment Status Original":status_db_original,"Amount Original": amount_db_original, "Payment Mode Original": payment_mode_db_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Failed", "Payment mode":"BHARATQR" , "Payment amount":str(amount), "Payment Status Original":"Settled","Amount Original": str(amount), "Payment Mode Original": "BHARATQR","Refund message": "ERROR: Bharat QR Refund Failed: "}
                #
                ui_driver.refresh()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id_refunded)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status_original = portalValuesDict['Status']
                portal_txn_type_original = portalValuesDict['Type']
                portal_amt_original = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Payment Status Original":portal_status_original,"Amount Original": str(portal_amt_original.split('.')[1]), "Payment Mode Original": portal_txn_type_original,"Refund message":refund_message}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
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
                expectedValues = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                  'RRN': rrn,
                                  'BASE AMOUNT:': 'Rs.' + str(amount) + '.00'}
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": username, "password": password},
                                                                  expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
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
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_044():
    """
        :Description: Verification of a BQR Refund Posted transaction via YES_ATOS
        :Sub Feature code: UI_Common_PM_BQR_Refund_Posted_YES_ATOS_044
        :TC naming code description: 100->Payment Method,102->BQR,044->TC44
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')
        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
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
            loginPage = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = 555
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            paymentPage.click_on_back_btn()
            paymentPage.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            paymentPage.click_on_proceed_homepage()
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            loginPagePortal = PortalLoginPage(ui_driver)
            logger.info(f"Logging in Portal using username : {portal_username}")
            loginPagePortal.perform_login_to_portal(portal_username, portal_password)
            homePagePortal = PortalHomePage(ui_driver)
            homePagePortal.search_merchant_name(org_code)
            logger.info(f"Switching to merchant : {org_code}")
            homePagePortal.click_switch_button(org_code)
            homePagePortal.click_transaction_search_menu()
            logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
            homePagePortal.click_on_transaction_details_based_on_transaction_id(txn_id)
            logger.debug("Clicking on refund button")
            homePagePortal.click_on_refund_button()
            refund_message=homePagePortal.perform_refund_of_txn_and_fetch_alert_msg(amount)
            logger.debug(f"Message for performing Refund of txn is : {refund_message}")
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            #
            # ------------------------------------------------------------------------------------------------
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
            try:
                logger.info(f"Starting App Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:REFUND_POSTED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id_refunded, "Payment Amt": str(amount), "Payment Status Original": "STATUS:AUTHORIZED", "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id, "Payment Amt Original": str(amount)}

                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
                transactionsHistoryPage.click_back_Btn_transaction_details()
                transactionsHistoryPage.click_on_second_transaction_by_order_id(order_id)
                app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn Mode = {app_payment_mode_original}")
                app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt), "Payment Status Original": app_payment_status_original, "Payment mode Original": app_payment_mode_original, "Payment Txn ID Original": txn_id, "Payment Amt Original": str(app_payment_amt_original)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting API Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Payment Status":"REFUND_POSTED","Amount": amount, "Payment Mode": "BHARATQR","Txn Type":"REFUND", "Acquirer Code":"YES", "Payment Status Original":"AUTHORIZED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_refunded})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                txn_type_api = response["txnType"]
                accuirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(f"Fetching Transaction type from transaction api : {txn_type_api} ")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api_orginal = response["status"]
                amount_api_original = response["amount"]
                payment_mode_api_orginal = response["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api_orginal} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api_original} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api_orginal} ")
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Txn Type":txn_type_api, "Acquirer Code":accuirer_code_api,"Payment Status Original":status_api_orginal,"Amount Original": amount_api_original, "Payment Mode Original": payment_mode_api_orginal}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting DB Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "REFUND_POSTED", "Payment mode":"BHARATQR" ,"Txn Type":"REFUND","Acquirer Code":"YES", "Payment amount":"{:.2f}".format(amount), "Payment Status Original":"AUTHORIZED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                #
                query = "select status,amount,payment_mode,external_ref,txn_type,acquirer_code from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode,txn_type,acquirer_code and external reference from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                txn_type_db = result["txn_type"].iloc[0]
                accuirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                logger.debug(f"Fetching Transaction type from DB : {txn_type_db} ")
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
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
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db,"Txn Type":txn_type_db,"Acquirer Code":accuirer_code_db, "Payment Status Original":status_db_original,"Amount Original": amount_db_original, "Payment Mode Original": payment_mode_db_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
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
            try:
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Refund Posted", "Payment mode":"BHARATQR" , "Payment amount":str(amount), "Payment Status Original":"Settled","Amount Original": str(amount), "Payment Mode Original": "BHARATQR","Refund message": "Transaction refund is pending"}
                #
                ui_driver.refresh()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id_refunded)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status_original = portalValuesDict['Status']
                portal_txn_type_original = portalValuesDict['Type']
                portal_amt_original = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Payment Status Original":portal_status_original,"Amount Original": str(portal_amt_original.split('.')[1]), "Payment Mode Original": portal_txn_type_original,"Refund message":refund_message}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
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
                expectedValues = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                  'RRN': rrn,
                                  'BASE AMOUNT:': 'Rs.' + str(amount) + '.00'}
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": username, "password": password},
                                                                  expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
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
        Configuration.executeFinallyBlock(testcase_id)
        # ----------------------------------------------------------------------------------------------------------