import random
from datetime import datetime
from time import sleep

import pytest

from Configuration import Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator
from Utilities.ConfigReader import read_config
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_004():
    """
    :Description: Verification of a BQR Check Status Success transaction via HDFC
    :Subfeature code: UI_Common_PM_BQR_Checkstatus_Success_HDFC _01
    :TC naming code description: 100->Payment Method
                                102->BQR
                                004-> TC04
    """

    try:
        logger.info("Starting execution for the test case : test_common_100_102_004")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""


        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            # Write the test case execution code block here
            app_driver = GlobalVariables.appDriver
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
            paymentPage.check_payment_page(amount,order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            query = "select * from bharatqr_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            api_details = DBProcessor.get_api_details('paymentStatus',
                                                      request_body={"username": username, "password": password,
                                                                    "txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            print("Response received:", response)
            logger.debug(f"Response received for checkstatus of transaction is : {response}")
            app_driver.reset()
            logger.info("Restarting MPOSX app to perfrom checkstatus of the transaction")
            loginPage = LoginPage(app_driver)
            logger.debug(f"Loging in again with user name : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.debug("Homepage of MPOSX app loaded successfully")
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            homePage.perform_check_status()
            logger.debug("Performing checkstatus of the previous transaction")
            paymentPage = PaymentPage(app_driver)
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of previous transaction : {app_payment_status}")
            paymentPage.click_on_proceed_homepage()
            paymentPage.click_on_back_btn()
            homePage.click_on_back_btn_enter_amt_page()
            logger.info("Execution is completed for the test case : test_sa_100_102_004")
            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            logger.error(f"Test case execution failed due to the exception : {e}")
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info("Starting App Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:AUTHORIZED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}

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

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"App Validation failed due to exception : {e}")
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info("Starting API Validation for the test case")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"AUTHORIZED","Amount": amount, "Payment Mode": "BHARATQR"}
                # payload = {"username": username, "password": password}
                # logger.debug(f"Paylaod for checking transaction details using api : {payload}")
                # response = APIProcessor.post(payload, 'txnList')

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                list = response["txns"]
                status_api = amount_api = payment_mode_api=''
                for li in list:
                    if li["txnId"] == txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case API validation failed due to the exception : {e}")
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Starting DB Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode":"BHARATQR" , "Payment amount":amount, "State":"SETTLED", "State Bharatqr": "SETTLED", "Amount Bharatqr": amount, "Status Bharatqr": "Transaction Success"}
                #
                query = "select status,amount,payment_mode,state from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                logger.debug(f"Fetching Transaction state from DB : {state_db} ")

                query = "select state,txn_amount,status_desc from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch state, txn amount and status_desc from bahratqr_txn DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from bharatqr txn table of DB : {result} ")
                state_bharatqr_db = result["state"].iloc[0]
                amount_bharatqr_db = result["txn_amount"].iloc[0]
                status_bharatqr_db = result["status_desc"].iloc[0]
                logger.debug(f"Fetching Transaction state from bharatqr txn table of DB : {state_bharatqr_db} ")
                logger.debug(f"Fetching Transaction amount from bharatqr txn table of DB : {amount_bharatqr_db} ")
                logger.debug(f"Fetching Transaction status description from bharatqr txn table of DB : {status_bharatqr_db} ")
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db, "State":state_db, "State Bharatqr": state_bharatqr_db, "Amount Bharatqr": amount_bharatqr_db, "Status Bharatqr": status_bharatqr_db}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case DB validation failed due to the exception : {e}")
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"BHARATQR" , "Payment amount":str(amount)}
                #
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
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id)
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"Test case Portal validation failed due to the exception : {e}")
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info("Started ChargeSlip validation for the test case : test_com_100_102_004")
            try:
                expectedValues = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': rrn,
                                  'BASE AMOUNT:': 'Rs.' + str(amount) + '.00'}
                receipt_validator.perform_charge_slip_validations(txn_id, {"username": username, "password": password},
                                                                  expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.bool_chargeslip_val_result = False

            logger.info("Completed ChargeSlip validation for the test case : test_com_100_102_004")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_common_100_102_004")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        logger.info("**********Test case Execution and Validation completed for testcase: test_common_100_102_004**************")




@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver") #This is an optional line. Keep only whichever app_driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_005(): #Make sure to add the test case name as same as the sub feature code.

    """
    :Description: Verification of a BQR Checkstatus Failed transaction via HDFC
    :Subfeature code: UI_Common_PM_BQR_Checkstatus_Failed_HDFC _05
    :TC naming code description: 100->Payment Method
                                102->BQR
                                005-> TC05
    """


    try:
        logger.info("Starting execution for the test case : test_common_100_102_005")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""


        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            # Write the test case execution code block here
            app_driver = GlobalVariables.appDriver
            loginPage = LoginPage(app_driver)
            username = read_config("credentials", 'username_HDFC')
            password = read_config("credentials", 'password')
            org_code = read_config("testdata", "org_code_hdfc")
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(101, 200)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount,order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            text = paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            query = "select * from bharatqr_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            api_details = DBProcessor.get_api_details('paymentStatus',
                                                      request_body={"username": username, "password": password,
                                                                    "txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for checkstatus of transaction is : {response}")
            print("API RESP settlementStatus", response["settlementStatus"])
            app_driver.reset()
            #app_driver.terminate_app("com.ezetap.basicapp")
            #app_driver.activate_app("com.ezetap.basicapp")
            logger.info("Restarting MPOSX app to perfrom checkstatus of the transaction")
            loginPage = LoginPage(app_driver)
            logger.debug(f"Loging in again with user name : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            homePage.perform_check_status()
            logger.debug("Performing checkstatus of the previous transaction")
            paymentPage = PaymentPage(app_driver)
            app_payment_status = paymentPage.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of previous transaction : {app_payment_status}")
            assert app_payment_status == "Payment Failed"
            paymentPage.click_on_proceed_homepage()
            homePage.click_on_back_btn_enter_amt_page()
            #
            # ------------------------------------------------------------------------------------------------
            logger.info("Execution is completed for the test case : test_sa_100_101_005")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            logger.error(f"Test case execution failed due to the exception : {e}")
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info("Starting App Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "FAILED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}

                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text().split(":")[1]
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

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info("App Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"App Validation failed due to exception : {e}")
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info("Starting API Validation for the test case")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"FAILED","Amount": amount, "Payment Mode": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                list = response["txns"]
                status_api = amount_api = payment_mode_api=''
                for li in list:
                    if li["txnId"] == txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case API validation failed due to the exception : {e}")
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Starting DB Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment mode": "BHARATQR",
                                    "Payment amount": amount, "State": "FAILED", "State Bharatqr": "FAILED",
                                    "Amount Bharatqr": amount, "Status Bharatqr": "Transaction failed"}
                #
                query = "select status,amount,payment_mode,state from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                logger.debug(f"Fetching Transaction state from DB : {state_db} ")

                query = "select state,txn_amount,status_desc from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch state, txn amount and status_desc from bahratqr_txn DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from bharatqr txn table of DB : {result} ")
                state_bharatqr_db = result["state"].iloc[0]
                amount_bharatqr_db = result["txn_amount"].iloc[0]
                status_bharatqr_db = result["status_desc"].iloc[0]
                logger.debug(f"Fetching Transaction state from bharatqr txn table of DB : {state_bharatqr_db} ")
                logger.debug(f"Fetching Transaction amount from bharatqr txn table of DB : {amount_bharatqr_db} ")
                logger.debug(
                    f"Fetching Transaction status description from bharatqr txn table of DB : {status_bharatqr_db} ")
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "State": state_db, "State Bharatqr": state_bharatqr_db,
                                  "Amount Bharatqr": amount_bharatqr_db, "Status Bharatqr": status_bharatqr_db}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case DB validation failed due to the exception : {e}")
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Failed", "Payment mode":"BHARATQR" , "Payment amount":str(amount)}
                #
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
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id)
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case Portal validation failed due to the exception : {e}")
                print("Portal Validation failed due to exception - "+str(e))
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
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_common_100_102_005")
        logger.info("**********Test case Execution and Validation completed for testcase: test_common_100_102_005**************")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_006(): #Make sure to add the test case name as same as the sub feature code.
    """
    :Description: Verification of a BQR Check Status After QR Expiry transaction via HDFC
    :Subfeature code: UI_Common_PM_BQR_Checkstatus_AfterExpiry_HDFC _06
    :TC naming code description: 100->Payment Method
                                102->BQR
                                006-> TC06
    """
    logger.info("Starting execution for the test case : test_common_100_102_006")

    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")
        portal_username = read_config("credentials", "username_portal")
        portal_password = read_config("credentials", "password_portal")
        org_code = read_config("testdata", "org_code_hdfc")
        api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        print("***********API DETAILS **********:", api_details)
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        logger.info("Finished performing preconditions before starting test case execution")



        GlobalVariables.setupCompletedSuccessfully = True

        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""


        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            app_driver = GlobalVariables.appDriver
            loginPage = LoginPage(app_driver)
            username = read_config("credentials", 'username_HDFC')
            password = read_config("credentials", 'password')
            org_code = read_config("testdata", "org_code_hdfc")
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.choice([i for i in range(51, 100) if i != 55])
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code and RRN from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}")
            logger.info(f"Waiting for QR code to get Expired.. Please wait")
            sleep(60)
            api_details = DBProcessor.get_api_details('paymentStatus',
                                                      request_body={"username": username, "password": password,
                                                                    "txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            logger.info(f"Logining in to app again with username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            homePage.enter_amount_and_order_number(amount, order_id)
            homePage.perform_check_status()
            app_payment_status = paymentPage.fetch_payment_status()
            logger.info(f"Fetching status of payment from payment screen: {app_payment_status} ")
            paymentPage.click_on_proceed_homepage()
            homePage.click_on_back_btn_enter_amt_page()

            logger.info("Execution is completed for the test case : test_sa_100_101_006")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            logger.error(f"Test case execution failed due to the exception : {e}")
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info("Starting App Validation for the test case")
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:EXPIRED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}

                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt)}
                logger.info("App Validation Completed successfully for test case")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                logger.error(f"Test case App validation failed due to the exception : {e}")
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info("Starting API Validation for the test case")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"EXPIRED","Amount": amount, "Payment Mode": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                list = response["txns"]
                status_api = amount_api = payment_mode_api = ''
                for li in list:
                    if li["txnId"] == txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api}

                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case API validation failed due to the exception : {e}")
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Starting DB Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "EXPIRED", "Payment mode": "BHARATQR",
                                    "Payment amount": amount, "State": "EXPIRED", "State Bharatqr": "EXPIRED",
                                    "Amount Bharatqr": amount, "Status Bharatqr": "Transaction Pending"}
                #
                query = "select status,amount,payment_mode,state from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                logger.debug(f"Fetching Transaction state from DB : {state_db} ")

                query = "select state,txn_amount,status_desc from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch state, txn amount and status_desc from bahratqr_txn DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from bharatqr txn table of DB : {result} ")
                state_bharatqr_db = result["state"].iloc[0]
                amount_bharatqr_db = result["txn_amount"].iloc[0]
                status_bharatqr_db = result["status_desc"].iloc[0]
                logger.debug(f"Fetching Transaction state from bharatqr txn table of DB : {state_bharatqr_db} ")
                logger.debug(f"Fetching Transaction amount from bharatqr txn table of DB : {amount_bharatqr_db} ")
                logger.debug(
                    f"Fetching Transaction status description from bharatqr txn table of DB : {status_bharatqr_db} ")
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "State": state_db, "State Bharatqr": state_bharatqr_db,
                                  "Amount Bharatqr": amount_bharatqr_db, "Status Bharatqr": status_bharatqr_db}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")

            except Exception as e:
                logger.error(f"Test case DB validation failed due to the exception : {e}")
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Expired", "Payment mode":"BHARATQR" , "Payment amount":str(amount)}
                #
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
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id)
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                logger.error(f"Test case Portal validation failed due to the exception : {e}")
                print("Portal Validation failed due to exception - "+str(e))
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
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition
        logger.info("Reverting all the settings that were done as preconditions")
        api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 6
        logger.debug(f"API details  : {api_details} ")
        print("***********API DETAILS **********:", api_details)
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        logger.info("Reverted back all the settings that were done as preconditions")

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_common_100_102_006")
        logger.info("**********Test case Execution and Validation compeleted for test case : test_common_100_102_006***********")
