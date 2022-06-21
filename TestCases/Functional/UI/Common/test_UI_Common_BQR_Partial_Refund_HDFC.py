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
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor
from Utilities.ConfigReader import read_config
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)





@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver",
                         "ui_driver")  # This is an optional line. Keep only whichever app_driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_sa_100_102_021():  # Make sure to add the test case name as same as the sub feature code.
    """
    :Description: Verification of a BQR Partial Refund transaction through API via HDFC
    :Sub Feature code: UI_Common_PM_BQR_Partial_Refund_API_HDFC _021
    :TC naming code description: 100->Payment Method
                                102->BQR
                                021-> TC21
    """

    try:
        logger.info("Starting execution for the test case : test_common_100_102_021")
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
            username = read_config("credentials", 'username_HDFC')
            password = read_config("credentials", 'password')
            org_code = read_config("testdata", "org_code_hdfc")
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(401, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount, order_id)
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
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")
            refund_amount = amount - 100
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": username, "amount": refund_amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for refund api is : {response}")
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            logger.info("Execution is completed for the test case : test_sa_100_102_021")
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
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
                expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "BHARAT QR",
                                     "Payment Txn ID": txn_id_refunded, "Payment Amt": str(refund_amount),
                                     "Payment Status Original": "STATUS:AUTHORIZED",
                                     "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id,
                                     "Payment Amt Original": str(amount)}

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
                                   "Payment Amt Original": str(app_payment_amt_original)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
            except Exception as e:
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

                expectedAPIValues = {"Payment Status": "REFUNDED", "Amount": refund_amount, "Payment Mode": "BHARATQR",
                                     "Payment Status Original": "AUTHORIZED", "Amount Original": amount,
                                     "Payment Mode Original": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                list = response["txns"]
                status_api = amount_api = payment_mode_api = ''
                status_api_orginal = amount_api_original = payment_mode_api_orginal = ''
                for li in list:
                    if li["txnId"] == txn_id_refunded:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
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
                                   "Payment Mode Original": payment_mode_api_orginal}
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
                expectedDBValues = {"Payment Status": "REFUNDED", "Payment mode": "BHARATQR", "Payment amount": refund_amount,
                                    "Payment Status Original": "AUTHORIZED", "Amount Original": amount,
                                    "Payment Mode Original": "BHARATQR"}
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
                expectedPortalValues = {"Payment Status": "Refunded", "Payment mode": "BHARATQR",
                                        "Payment amount": str(refund_amount), "Payment Status Original": "Settled",
                                        "Amount Original": str(amount), "Payment Mode Original": "BHARATQR"}
                #
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = read_config("credentials", 'username_portal')
                password_portal = read_config('credentials', 'password_portal')
                logger.info(f"Logging in Portal using username : {username_portal}")
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name(read_config("testdata", "org_code_hdfc"))
                logger.info(f"Switching to merchant : {read_config('testdata', 'org_code_hdfc')}")
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id_refunded)
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id_refunded)
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id_refunded)
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                portal_status_original = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portal_txn_type_original = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)
                portal_amt_original = homePagePortal.fetch_amount_from_transaction_id(txn_id)
                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
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
                logger.error(f"Test case Portal validation failed due to the exception : {e}")
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_sa_100_102_021")
        logger.info(
            "**********Test case Execution and Validation completed for test case : test_common_100_102_021**************")



@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver",
                         "ui_driver")  # This is an optional line. Keep only whichever app_driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_sa_100_102_022():  # Make sure to add the test case name as same as the sub feature code.
    """
    :Description: Verification of a BQR Partial Refund transaction via HDFC
    :Sub Feature code: UI_Common_PM_BQR_Partial_Refund_HDFC _022
    :TC naming code description: 100->Payment Method
                                102->BQR
                                022-> TC22
    """

    try:
        logger.info("Starting execution for the test case : test_common_100_102_022")
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
            username = read_config("credentials", 'username_HDFC')
            password = read_config("credentials", 'password')
            org_code = read_config("testdata", "org_code_hdfc")
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(401, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount, order_id)
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
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.info("Opening Portal to perform refund of the transaction")
            refund_amount = amount - 100
            ui_driver = GlobalVariables.portalDriver
            loginPagePortal = PortalLoginPage(ui_driver)
            username_portal = read_config("credentials", 'username_portal')
            password_portal = read_config('credentials', 'password_portal')
            logger.info(f"Logging in Portal using username : {username_portal}")
            loginPagePortal.perform_login_to_portal(username_portal, password_portal)
            homePagePortal = PortalHomePage(ui_driver)
            homePagePortal.search_merchant_name(read_config("testdata", "org_code_hdfc"))
            logger.info(f"Switching to merchant : {read_config('testdata', 'org_code_hdfc')}")
            homePagePortal.click_switch_button()
            homePagePortal.click_transaction_search_menu()
            logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
            homePagePortal.click_on_transaction_details_based_on_transaction_id(txn_id)
            logger.debug("Clicking on refund button")
            homePagePortal.click_on_refund_button()
            homePagePortal.perform_refund_of_txn(refund_amount)
            logger.info("Performing Page refresh after refund is performed")
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")



            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            logger.info("Execution is completed for the test case : test_sa_100_102_021")
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
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
                expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "BHARAT QR",
                                     "Payment Txn ID": txn_id_refunded, "Payment Amt": str(refund_amount),
                                     "Payment Status Original": "STATUS:AUTHORIZED",
                                     "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id,
                                     "Payment Amt Original": str(amount)}

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
                                   "Payment Amt Original": str(app_payment_amt_original)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
            except Exception as e:
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

                expectedAPIValues = {"Payment Status": "REFUNDED", "Amount": refund_amount, "Payment Mode": "BHARATQR",
                                     "Payment Status Original": "AUTHORIZED", "Amount Original": amount,
                                     "Payment Mode Original": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                list = response["txns"]
                status_api = amount_api = payment_mode_api = ''
                status_api_orginal = amount_api_original = payment_mode_api_orginal = ''
                for li in list:
                    if li["txnId"] == txn_id_refunded:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
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
                                   "Payment Mode Original": payment_mode_api_orginal}
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
                expectedDBValues = {"Payment Status": "REFUNDED", "Payment mode": "BHARATQR", "Payment amount": refund_amount,
                                    "Payment Status Original": "AUTHORIZED", "Amount Original": amount,
                                    "Payment Mode Original": "BHARATQR"}
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
                expectedPortalValues = {"Payment Status": "Refunded", "Payment mode": "BHARATQR",
                                        "Payment amount": str(refund_amount), "Payment Status Original": "Settled",
                                        "Amount Original": str(amount), "Payment Mode Original": "BHARATQR"}
                #
                ui_driver.refresh()
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id_refunded)
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id_refunded)
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id_refunded)
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                portal_status_original = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portal_txn_type_original = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)
                portal_amt_original = homePagePortal.fetch_amount_from_transaction_id(txn_id)
                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
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
                logger.error(f"Test case Portal validation failed due to the exception : {e}")
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_sa_100_102_022")
        logger.info(
            "**********Test case Execution and Validation completed for test case : test_common_100_102_022**************")

