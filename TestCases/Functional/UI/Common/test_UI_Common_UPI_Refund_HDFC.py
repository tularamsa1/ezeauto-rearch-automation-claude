import random
from datetime import datetime
import pytest
from Configuration import Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
# Performing a upi txn and full refund via portal
def test_com_100_101_010():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code:
    Sub Feature Description:
    """

    try:
        logger.info("Starting execution for the test case : test_com_100_101_010")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------

            # Write the test case execution code block here
            app_driver = GlobalVariables.appDriver
            loginPage = LoginPage(app_driver)
            username = '5784758454'
            password = 'A123456'
            org_code = "UPIHDFCBANKHDFCPG"
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount, order_id)
            paymentPage.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            paymentPage.click_on_back_btn()
            paymentPage.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            paymentPage.click_on_proceed_homepage()
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")
            ui_driver = GlobalVariables.portalDriver
            loginPagePortal = PortalLoginPage(ui_driver)
            username_portal = '9660867344'
            password_portal = 'A123456'
            logger.info(f"Logging in Portal using username : {username_portal}")
            loginPagePortal.perform_login_to_portal(username_portal, password_portal)
            homePagePortal = PortalHomePage(ui_driver)
            homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
            logger.info(f"Switching to merchant : UPIHDFCBANKHDFCPG")
            homePagePortal.click_switch_button()
            homePagePortal.click_transaction_search_menu()
            logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
            homePagePortal.click_on_transaction_details_based_on_transaction_id(txn_id)
            logger.debug("Clicking on refund button")
            homePagePortal.click_on_refund_button()
            homePagePortal.perform_refund_of_txn(amount)
            logger.info("Performing Page refresh after refund is performed")
            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_id : {txn_id_refunded}, rrn : {rrn} ")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            logger.info("Execution is completed for the test case : test_com_100_101_010")
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            logger.error("Testcase execution failed due to exception: str(")
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info("Starting App Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "UPI",
                                     "Payment Txn ID": txn_id_refunded, "Payment Amt": str(amount),
                                     "Payment Status Original": "STATUS:AUTHORIZED_REFUNDED",
                                     "Payment mode Original": "UPI", "Payment Txn ID Original": txn_id,
                                     "Payment Amt Original": str(amount), "rrn":str(rrn)}

                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_rrn = transactionsHistoryPage.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn}")
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
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode,
                                   "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),
                                   "Payment Status Original": app_payment_status_original,
                                   "Payment mode Original": app_payment_mode_original,
                                   "Payment Txn ID Original": txn_id,
                                   "Payment Amt Original": str(app_payment_amt_original), "rrn":str(app_rrn)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"App Validation failed due to exception : {e}")
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info("Starting API Validation for the test case")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status": "REFUNDED", "Amount": amount, "Payment Mode": "UPI",
                                     "Payment Status Original": "AUTHORIZED_REFUNDED", "Amount Original": amount,
                                     "Payment Mode Original": "UPI", "rrn":str(rrn)}
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                list = response["txns"]
                status_api = amount_api = payment_mode_api = rrn_api = ''
                status_api_orginal = amount_api_original = payment_mode_api_orginal = ''
                for li in list:
                    if li["txnId"] == txn_id_refunded:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                        rrn_api = li["rrNumber"]
                    elif li["txnId"] == txn_id:
                        status_api_orginal = li["status"]
                        amount_api_original = int(li["amount"])
                        payment_mode_api_orginal = li["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction api : {status_api_orginal} ")
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction api : {amount_api_original} ")
                logger.debug(
                    f"Fetching Transaction payment of original txn mode from transaction api : {payment_mode_api_orginal} ")
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,
                                   "Payment Status Original": status_api_orginal,
                                   "Amount Original": amount_api_original,
                                   "Payment Mode Original": payment_mode_api_orginal, "rrn":str(rrn_api)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case API validation failed due to the exception : {e}")
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Starting DB Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "REFUNDED", "Payment mode": "UPI", "Payment amount": amount,
                                    "Payment Status Original": "AUTHORIZED_REFUNDED", "Amount Original": amount,
                                    "Payment Mode Original": "UPI"}
                #
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
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "Payment Status Original": status_db_original,
                                  "Amount Original": amount_db_original,
                                  "Payment Mode Original": payment_mode_db_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case DB validation failed due to the exception : {e}")
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Refunded", "Payment mode": "UPI",
                                        "Payment amount": str(amount), "Payment Status Original": "Authorized Refunded",
                                        "Amount Original": str(amount), "Payment Mode Original": "UPI"}
                #
                ui_driver.refresh()
                portalTransHistoryPage = PortalTransHistoryPage(ui_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id_refunded)
                portal_txn_type = portalValuesDict['Type']
                portal_status = portalValuesDict['Status']
                portal_amt = portalValuesDict['Total Amount']
                portal_username = portalValuesDict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id)
                portal_txn_type_original = portalValuesDict['Type']
                portal_status_original = portalValuesDict['Status']
                portal_amt_original = portalValuesDict['Total Amount']
                portal_username_original = portalValuesDict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                      "Payment amount": str(portal_amt.split('.')[1]),
                                      "Payment Status Original": portal_status_original,
                                      "Amount Original": str(portal_amt_original.split('.')[1]),
                                      "Payment Mode Original": portal_txn_type_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"Test case Portal validation failed due to the exception : {e}")
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info("Started ChargeSlip validation for the test case : test_com_100_101_010")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expectedValues = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                  'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                receipt_validator.perform_charge_slip_validations(txn_id_refunded, {"username": username, "password": password},
                                                                  expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.bool_chargeslip_val_result = False

            logger.info("Completed ChargeSlip validation for the test case : test_com_100_101_010")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_010")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        logger.info(
            "**********Test case Execution and Validation completed for test case : test_com_100_101_010**************")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
# Performing a upi txn and full refund via api
def test_com_100_101_011():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code:
    Sub Feature Description:
    """

    try:
        logger.info("Starting execution for the test case : test_com_100_101_011")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        app_driver = GlobalVariables.appDriver

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------

            # Write the test case execution code block here

            loginPage = LoginPage(app_driver)
            username = '5784758454'
            password = 'A123456'
            org_code = "UPIHDFCBANKHDFCPG"
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount, order_id)
            paymentPage.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            paymentPage.click_on_back_btn()
            paymentPage.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            paymentPage.click_on_proceed_homepage()
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")
            api_details = DBProcessor.get_api_details('payment_unified_refund',
                                                      request_body={"username": username, "amount": amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            print(response)
            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_id : {txn_id_refunded}, rrn : {rrn} ")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            logger.info("Execution is completed for the test case : test_sa_100_102_019")
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            logger.error("Testcase execution failed due to exception: str(")
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info("Starting App Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "UPI",
                                     "Payment Txn ID": txn_id_refunded, "Payment Amt": str(amount),
                                     "Payment Status Original": "STATUS:AUTHORIZED_REFUNDED",
                                     "Payment mode Original": "UPI", "Payment Txn ID Original": txn_id,
                                     "Payment Amt Original": str(amount), "rrn":str(rrn)}

                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_rrn = transactionsHistoryPage.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn}")
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
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode,
                                   "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),
                                   "Payment Status Original": app_payment_status_original,
                                   "Payment mode Original": app_payment_mode_original,
                                   "Payment Txn ID Original": txn_id,
                                   "Payment Amt Original": str(app_payment_amt_original), "rrn":str(app_rrn)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"App Validation failed due to exception : {e}")
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info("Starting API Validation for the test case")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status": "REFUNDED", "Amount": amount, "Payment Mode": "UPI",
                                     "Payment Status Original": "AUTHORIZED_REFUNDED", "Amount Original": amount,
                                     "Payment Mode Original": "UPI", "rrn":str(rrn)}
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                list = response["txns"]
                status_api = amount_api = payment_mode_api = rrn_api = ''
                status_api_orginal = amount_api_original = payment_mode_api_orginal = ''
                for li in list:
                    if li["txnId"] == txn_id_refunded:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                        rrn_api = li["rrNumber"]
                    elif li["txnId"] == txn_id:
                        status_api_orginal = li["status"]
                        amount_api_original = int(li["amount"])
                        payment_mode_api_orginal = li["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction api : {status_api_orginal} ")
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction api : {amount_api_original} ")
                logger.debug(
                    f"Fetching Transaction payment of original txn mode from transaction api : {payment_mode_api_orginal} ")
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,
                                   "Payment Status Original": status_api_orginal,
                                   "Amount Original": amount_api_original,
                                   "Payment Mode Original": payment_mode_api_orginal, "rrn":str(rrn_api)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case API validation failed due to the exception : {e}")
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Starting DB Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "REFUNDED", "Payment mode": "UPI", "Payment amount": amount,
                                    "Payment Status Original": "AUTHORIZED_REFUNDED", "Amount Original": amount,
                                    "Payment Mode Original": "UPI"}
                #
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
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "Payment Status Original": status_db_original,
                                  "Amount Original": amount_db_original,
                                  "Payment Mode Original": payment_mode_db_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case DB validation failed due to the exception : {e}")
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Refunded", "Payment mode": "UPI",
                                        "Payment amount": str(amount), "Payment Status Original": "Authorized Refunded",
                                        "Amount Original": str(amount), "Payment Mode Original": "UPI"}
                #
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = '9660867344'
                password_portal = 'A123456'
                logger.info(f"Logging in Portal using username : {username_portal}")
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                logger.info(f"Switching to merchant : UPIHDFCBANKHDFCPG")
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()

                portalTransHistoryPage = PortalTransHistoryPage(driver_ui)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id_refunded)
                portal_txn_type = portalValuesDict['Type']
                portal_status = portalValuesDict['Status']
                portal_amt = portalValuesDict['Total Amount']
                portal_username = portalValuesDict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id)
                portal_txn_type_original = portalValuesDict['Type']
                portal_status_original = portalValuesDict['Status']
                portal_amt_original = portalValuesDict['Total Amount']
                portal_username_original = portalValuesDict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                      "Payment amount": str(portal_amt.split('.')[1]),
                                      "Payment Status Original": portal_status_original,
                                      "Amount Original": str(portal_amt_original.split('.')[1]),
                                      "Payment Mode Original": portal_txn_type_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"Test case Portal validation failed due to the exception : {e}")
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info("Started ChargeSlip validation for the test case : test_com_100_101_011")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expectedValues = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                  'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                receipt_validator.perform_charge_slip_validations(txn_id_refunded, {"username": username, "password": password},
                                                                  expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.bool_chargeslip_val_result = False

            logger.info("Completed ChargeSlip validation for the test case : test_com_100_101_011")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_011")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        logger.info(
            "**********Test case Execution and Validation completed for test case : test_com_100_101_011**************")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
# Performing a upi txn and partial refund via api
def test_com_100_101_012():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code:
    Sub Feature Description:
    """

    try:
        logger.info("Starting execution for the test case : test_com_100_101_012")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        app_driver = GlobalVariables.appDriver

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------

            # Write the test case execution code block here

            loginPage = LoginPage(app_driver)
            username = '5784758454'
            password = 'A123456'
            org_code = "UPIHDFCBANKHDFCPG"
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount, order_id)
            paymentPage.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            paymentPage.click_on_back_btn()
            paymentPage.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            paymentPage.click_on_proceed_homepage()
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")
            refund_amount = amount - 100
            api_details = DBProcessor.get_api_details('payment_unified_refund',
                                                      request_body={"username": username, "amount": refund_amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for refund api is : {response}")
            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_id : {txn_id_refunded}, rrn : {rrn} ")


            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            logger.info("Execution is completed for the test case : test_sa_100_102_021")
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            logger.error("Testcase execution failed due to exception: str(")
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info("Starting App Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "UPI",
                                     "Payment Txn ID": txn_id_refunded, "Payment Amt": str(refund_amount),
                                     "Payment Status Original": "STATUS:AUTHORIZED",
                                     "Payment mode Original": "UPI", "Payment Txn ID Original": txn_id,
                                     "Payment Amt Original": str(amount), "rrn":str(rrn)}

                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_rrn = transactionsHistoryPage.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn}")
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
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode,
                                   "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),
                                   "Payment Status Original": app_payment_status_original,
                                   "Payment mode Original": app_payment_mode_original,
                                   "Payment Txn ID Original": txn_id,
                                   "Payment Amt Original": str(app_payment_amt_original), "rrn":str(app_rrn)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"App Validation failed due to exception : {e}")
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info("Starting API Validation for the test case")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status": "REFUNDED", "Amount": refund_amount, "Payment Mode": "UPI",
                                     "Payment Status Original": "AUTHORIZED", "Amount Original": amount,
                                     "Payment Mode Original": "UPI", "rrn":str(rrn)}
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                list = response["txns"]
                status_api = amount_api = payment_mode_api = ''
                status_api_orginal = amount_api_original = payment_mode_api_orginal, rrn_api = ''
                for li in list:
                    if li["txnId"] == txn_id_refunded:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                        rrn_api = li["rrNumber"]
                    elif li["txnId"] == txn_id:
                        status_api_orginal = li["status"]
                        amount_api_original = int(li["amount"])
                        payment_mode_api_orginal = li["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction api : {status_api_orginal} ")
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction api : {amount_api_original} ")
                logger.debug(
                    f"Fetching Transaction payment of original txn mode from transaction api : {payment_mode_api_orginal} ")
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,
                                   "Payment Status Original": status_api_orginal,
                                   "Amount Original": amount_api_original,
                                   "Payment Mode Original": payment_mode_api_orginal, "rrn":str(rrn_api)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case API validation failed due to the exception : {e}")
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Starting DB Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "REFUNDED", "Payment mode": "UPI",
                                    "Payment amount": refund_amount,
                                    "Payment Status Original": "AUTHORIZED", "Amount Original": amount,
                                    "Payment Mode Original": "UPI"}
                #
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
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "Payment Status Original": status_db_original,
                                  "Amount Original": amount_db_original,
                                  "Payment Mode Original": payment_mode_db_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case DB validation failed due to the exception : {e}")
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Refunded", "Payment mode": "UPI",
                                        "Payment amount": str(refund_amount), "Payment Status Original": "Settled",
                                        "Amount Original": str(amount), "Payment Mode Original": "UPI"}
                #
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = '9660867344'
                password_portal = 'A123456'
                logger.info(f"Logging in Portal using username : {username_portal}")
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                logger.info(f"Switching to merchant : UPIHDFCBANKHDFCPG")
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()

                portalTransHistoryPage = PortalTransHistoryPage(driver_ui)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id_refunded)
                portal_txn_type = portalValuesDict['Type']
                portal_status = portalValuesDict['Status']
                portal_amt = portalValuesDict['Total Amount']
                portal_username = portalValuesDict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id)
                portal_txn_type_original = portalValuesDict['Type']
                portal_status_original = portalValuesDict['Status']
                portal_amt_original = portalValuesDict['Total Amount']
                portal_username_original = portalValuesDict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                      "Payment amount": str(portal_amt.split('.')[1]),
                                      "Payment Status Original": portal_status_original,
                                      "Amount Original": str(portal_amt_original.split('.')[1]),
                                      "Payment Mode Original": portal_txn_type_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"Test case Portal validation failed due to the exception : {e}")
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------

        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info("Started ChargeSlip validation for the test case : test_com_100_101_012")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expectedValues = {'PAID BY:':'UPI', 'merchant_ref_no': 'Ref # '+str(order_id), 'RRN':str(rrn), 'BASE AMOUNT:':"Rs." + str(refund_amount) + ".00",
                                  'date':date}
                receipt_validator.perform_charge_slip_validations(txn_id_refunded, {"username":username,"password":password}, expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.bool_chargeslip_val_result = False

            logger.info("Completed ChargeSlip validation for the test case : test_com_100_101_012")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_012")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        logger.info(
            "**********Test case Execution and Validation completed for test case : test_com_100_101_012**************")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
# Performing a upi txn and partial refund via portal
def test_com_100_101_013():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code:
    Sub Feature Description:
    """

    try:
        logger.info("Starting execution for the test case : test_com_100_101_013")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        app_driver = GlobalVariables.appDriver

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------

            # Write the test case execution code block here

            loginPage = LoginPage(app_driver)
            username = '5784758454'
            password = 'A123456'
            org_code = "UPIHDFCBANKHDFCPG"
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount, order_id)
            paymentPage.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            paymentPage.click_on_back_btn()
            paymentPage.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status}")
            paymentPage.click_on_proceed_homepage()
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")
            refund_amount = amount - 100
            ui_driver = GlobalVariables.portalDriver
            loginPagePortal = PortalLoginPage(ui_driver)
            username_portal = '9660867344'
            password_portal = 'A123456'
            logger.info(f"Logging in Portal using username : {username_portal}")
            loginPagePortal.perform_login_to_portal(username_portal, password_portal)
            homePagePortal = PortalHomePage(ui_driver)
            homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
            logger.info(f"Switching to merchant : UPIHDFCBANKHDFCPG")
            homePagePortal.click_switch_button()
            homePagePortal.click_transaction_search_menu()
            logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
            homePagePortal.click_on_transaction_details_based_on_transaction_id(txn_id)
            logger.debug("Clicking on refund button")
            homePagePortal.click_on_refund_button()
            homePagePortal.perform_refund_of_txn(refund_amount)
            logger.info("Performing Page refresh after refund is performed")
            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            rrn = result['rr_number'].iloc[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_id : {txn_id_refunded}, rrn : {rrn} ")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            logger.info("Execution is completed for the test case : test_sa_100_102_021")
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            logger.error("Testcase execution failed due to exception: str(")
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info("Starting App Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "UPI",
                                     "Payment Txn ID": txn_id_refunded, "Payment Amt": str(refund_amount),
                                     "Payment Status Original": "STATUS:AUTHORIZED",
                                     "Payment mode Original": "UPI", "Payment Txn ID Original": txn_id,
                                     "Payment Amt Original": str(amount), "rrn":str(rrn)}

                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_rrn = transactionsHistoryPage.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn}")
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
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode,
                                   "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),
                                   "Payment Status Original": app_payment_status_original,
                                   "Payment mode Original": app_payment_mode_original,
                                   "Payment Txn ID Original": txn_id,
                                   "Payment Amt Original": str(app_payment_amt_original), "rrn":str(app_rrn)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"App Validation failed due to exception : {e}")
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info("Starting API Validation for the test case")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status": "REFUNDED", "Amount": refund_amount, "Payment Mode": "UPI",
                                     "Payment Status Original": "AUTHORIZED", "Amount Original": amount,
                                     "Payment Mode Original": "UPI", "rrn":str(rrn)}
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                list = response["txns"]
                status_api = amount_api = payment_mode_api = ''
                status_api_orginal = amount_api_original = payment_mode_api_orginal, rrn_api = ''
                for li in list:
                    if li["txnId"] == txn_id_refunded:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                        rrn_api = li["rrNumber"]
                    elif li["txnId"] == txn_id:
                        status_api_orginal = li["status"]
                        amount_api_original = int(li["amount"])
                        payment_mode_api_orginal = li["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction api : {status_api_orginal} ")
                logger.debug(
                    f"Fetching Transaction amount of original txn from transaction api : {amount_api_original} ")
                logger.debug(
                    f"Fetching Transaction payment of original txn mode from transaction api : {payment_mode_api_orginal} ")
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,
                                   "Payment Status Original": status_api_orginal,
                                   "Amount Original": amount_api_original,
                                   "Payment Mode Original": payment_mode_api_orginal, "rrn":str(rrn_api)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case API validation failed due to the exception : {e}")
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Starting DB Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "REFUNDED", "Payment mode": "UPI",
                                    "Payment amount": refund_amount,
                                    "Payment Status Original": "AUTHORIZED", "Amount Original": amount,
                                    "Payment Mode Original": "UPI"}
                #
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
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "Payment Status Original": status_db_original,
                                  "Amount Original": amount_db_original,
                                  "Payment Mode Original": payment_mode_db_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case DB validation failed due to the exception : {e}")
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Refunded", "Payment mode": "UPI",
                                        "Payment amount": str(refund_amount), "Payment Status Original": "Settled",
                                        "Amount Original": str(amount), "Payment Mode Original": "UPI"}
                #
                ui_driver.refresh()
                portalTransHistoryPage = PortalTransHistoryPage(ui_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id_refunded)
                portal_txn_type = portalValuesDict['Type']
                portal_status = portalValuesDict['Status']
                portal_amt = portalValuesDict['Total Amount']
                portal_username = portalValuesDict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id)
                portal_txn_type_original = portalValuesDict['Type']
                portal_status_original = portalValuesDict['Status']
                portal_amt_original = portalValuesDict['Total Amount']
                portal_username_original = portalValuesDict['Username']

                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                      "Payment amount": str(portal_amt.split('.')[1]),
                                      "Payment Status Original": portal_status_original,
                                      "Amount Original": str(portal_amt_original.split('.')[1]),
                                      "Payment Mode Original": portal_txn_type_original}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"Test case Portal validation failed due to the exception : {e}")
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------

        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info("Started ChargeSlip validation for the test case : test_com_100_101_013")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expectedValues = {'PAID BY:':'UPI', 'merchant_ref_no': 'Ref # '+str(order_id), 'RRN':str(rrn), 'BASE AMOUNT:':"Rs." + str(refund_amount) + ".00",
                                  'date':date}
                receipt_validator.perform_charge_slip_validations(txn_id_refunded, {"username":username,"password":password}, expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.bool_chargeslip_val_result = False

            logger.info("Completed ChargeSlip validation for the test case : test_com_100_101_013")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_013")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        logger.info(
            "**********Test case Execution and Validation completed for test case : test_com_100_101_013**************")
