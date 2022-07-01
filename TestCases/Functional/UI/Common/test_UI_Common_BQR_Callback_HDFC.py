import sys
from time import sleep
import pytest
import random
from datetime import datetime
from Configuration import Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner
from Utilities.ConfigReader import read_config
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_001():
    """
    :Description: Verification of a BQR Callback Success transaction via HDFC
    :Sub Feature code: UI_Common_PM_BQR_Callback_Success_HDFC _01
    :TC naming code description: 100->Payment Method
                                102->BQR
                                001-> TC01
    """
    testcase_id = sys._getframe().f_code.co_name
    logger.info(f"Starting execution for the test case : {testcase_id}")

    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------


        GlobalVariables.setupCompletedSuccessfully = True
        #---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)
        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            app_cred = ResourceAssigner.getAppUserCredentials('test_common_100_102_001')
            logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
            username = app_cred['Username']
            password = app_cred['Password']
            portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_102_001')
            logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
            portal_username = portal_cred['Username']
            portal_password = portal_cred['Password']

            query = "select org_code from org_employee where username='" + str(username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            app_driver = GlobalVariables.appDriver
            loginPage = LoginPage(app_driver)
            # username = read_config("credentials", 'username_HDFC')
            # password = read_config("credentials", 'password')
            # org_code = read_config("testdata", "org_code_hdfc")
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.wait_for_navigationTo_load()
            homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(401, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code and RRN from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount), "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            print("Response received:", response)
            logger.debug(f"Fetching API Response for call back : {response}")
            app_payment_status = paymentPage.fetch_payment_status()
            logger.info(f"Fetching status of payment from payment screen: {app_payment_status} ")
            paymentPage.click_on_proceed_homepage()
            logger.info(f"Execution is completed for the test case : {testcase_id}")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
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
                expectedAppValues = {"Payment Status": "STATUS:AUTHORIZED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}
                homePage.check_home_page_logo()
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
                ReportProcessor.capture_ss_when_exe_failed()
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
                expectedAPIValues = {"Payment Status":"AUTHORIZED","Amount": amount, "Payment Mode": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password, "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api=response["paymentMode"]
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
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount), "State":"SETTLED", "State Bharatqr": "SETTLED", "Amount Bharatqr": amount, "Status Bharatqr": "Transaction Success"}
                #
                query = "select status,amount,payment_mode,state from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
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
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"BHARATQR" , "Payment amount":str(amount)}
                #
                ui_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(ui_driver)
                # portal_username = read_config("credentials", 'username_portal')
                # portal_password = read_config('credentials', 'password_portal')
                logger.info(f"Logging in Portal using username : {portal_username}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(ui_driver)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(str(org_code))
                logger.info(f"Switching to merchant : {str(org_code)}")
                homePagePortal.click_switch_button(str(org_code))
                homePagePortal.perform_merchant_switched_verfication()
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
                logger.info(f"Portal Validation Completed successfully for test case : {testcase_id}")
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
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                expectedValues = {'PAID BY:':'BHARATQR', 'merchant_ref_no': 'Ref # '+str(order_id), 'RRN': rrn, 'BASE AMOUNT:': 'Rs.'+str(amount)+'.00'}
                receipt_validator.perform_charge_slip_validations(txn_id, {"username":username,"password":password}, expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_chargeslip_val_result = "Fail"

            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
        logger.info(
            f"**********Test case Execution and Validation compeleted for testcase: {testcase_id}**************")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.




@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_002():
    """
    :Description: Verification of a BQR Callback Failed transaction via HDFC
    :Sub Feature code: UI_Common_PM_BQR_Callback_Failed_HDFC _02
    :TC naming code description: 100->Payment Method
                                102->BQR
                                002-> TC02
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True
        #---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)
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
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(101, 200)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            query = "select * from bharatqr_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code and RRN from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback of transaction is : {response}")
            print("API Res:", response)
            app_payment_status = paymentPage.fetch_payment_status()
            logger.info(f"Fetching status of payment from payment screen: {app_payment_status} ")
            paymentPage.click_on_proceed_homepage()
            paymentPage.click_on_back_btn()
            #
            logger.info(f"Execution is completed for the test case : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            logger.error(f"Test case execution failed due to the exception : {e}")
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info(f"Starting APP Validation for the test case: {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:FAILED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}
                homePage.click_on_back_btn_enter_amt_page()
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
                logger.info(f"App Validation Completed successfully for test case : {testcase_id}")
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error("App Validation failed due to exception - " + str(e))
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info(f"Starting API Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"FAILED","Amount": amount, "Payment Mode": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
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
                logger.info(f"Starting DB Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment mode": "BHARATQR",
                                    "Payment amount": "{:.2f}".format(amount), "State": "FAILED", "State Bharatqr": "FAILED",
                                    "Amount Bharatqr": amount, "Status Bharatqr": "Transaction failed"}
                #
                query = "select status,amount,payment_mode,state from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
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
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
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
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id) # use get_transaction_details_for_portal istead of this
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)# use get_transaction_details_for_portal istead of this
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id)# use get_transaction_details_for_portal istead of this
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
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

    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
        logger.info(
            f"**********Test case Execution and Validation compeleted for testcase: {testcase_id}**************")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_003():
    """
    :Description: Verification of a BQR Callback After QR Expiry transaction via HDFC
    :Sub Feature code: UI_Common_PM_BQR_Callback_AfterExpiry_HDFC _03
    :TC naming code description: 100->Payment Method
                                102->BQR
                                003-> TC03
    """


    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
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
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)
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
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.choice([i for i in range(51, 100) if i != 55])
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
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
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            logger.info(f"Execution is completed for the test case : {testcase_id}")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()
            logger.error(f"Test case execution failed due to the exception : {e}")
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Starting App Validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:EXPIRED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}
                #
                logger.info(f"Logining in to app again with username : {username}")
                loginPage.perform_login(username, password)
                homePage = HomePage(app_driver)
                homePage.check_home_page_logo()
                logger.info(f"App homepage loaded successfully")
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
                ReportProcessor.capture_ss_when_exe_failed()
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

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
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
                                    "Payment amount": "{:.2f}".format(amount), "State": "EXPIRED", "State Bharatqr": "EXPIRED",
                                    "Amount Bharatqr": amount, "Status Bharatqr": "Transaction Pending"}
                #
                query = "select status,amount,payment_mode,state from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
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
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id) #change this method
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

    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
        logger.info(
            f"**********Test case Execution and Validation completed for testcase: {testcase_id}**************")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info(f"Reverting all the settings that were done as preconditions for test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 6
        logger.debug(f"API details  : {api_details} ")
        print("***********API DETAILS **********:", api_details)
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_011():
    """
    :Description: Verification of a BQR Success transaction with two Callback via HDFC
    :Sub Feature code: UI_Common_PM_BQR_two_Callback_Success_HDFC_11
    :TC naming code description: 100->Payment Method
                                102->BQR
                                011-> TC11
    """


    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------


        GlobalVariables.setupCompletedSuccessfully = True
        #---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)
        msg = ""
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            app_driver = GlobalVariables.appDriver
            username = read_config("credentials", 'username_HDFC')
            password = read_config("credentials", 'password')
            org_code = read_config("testdata", "org_code_hdfc")
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage = LoginPage(app_driver)
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(401, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code and RRN from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for 1st call back : {response}")

            app_payment_status = paymentPage.fetch_payment_status()
            logger.info(f"Fetching status of payment from payment screen: {app_payment_status} ")
            paymentPage.click_on_proceed_homepage()
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for 2nd call back : {response}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()
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
                expectedAppValues = {"Payment Status": "STATUS:AUTHORIZED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}
                homePage.check_home_page_logo()
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
                ReportProcessor.capture_ss_when_exe_failed()
                logger.error(f"Test case App validation failed due to the exception : {e}")
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info(f"Starting API Validation for the test case :{testcase_id}")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"AUTHORIZED","Amount": amount, "Payment Mode": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
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
                logger.info(f"Starting DB Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount), "State":"SETTLED", "State Bharatqr": "SETTLED", "Amount Bharatqr": amount, "Status Bharatqr": "Transaction Success"}
                #
                query = "select status,amount,payment_mode,state from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
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
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
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
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
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
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                expectedValues = {'PAID BY:':'BHARATQR', 'merchant_ref_no': 'Ref # '+str(order_id), 'RRN': rrn, 'BASE AMOUNT:': 'Rs.'+str(amount)+'.00'}
                receipt_validator.perform_charge_slip_validations(txn_id, {"username":username,"password":password}, expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_chargeslip_val_result = False

            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
        logger.info(
            f"**********Test case Execution and Validation compeleted for testcase: {testcase_id}**************")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        # Write the code here to revert the settings that were done as precondition
        # ----------------------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_012():
    """
    :Description: Verification of  a BQR expired Callback when auto refund disabled viaHDFC
    :Sub Feature code: UI_Common_PM_BQR_Expired_Callback_AutoRefund_disabled_HDFC_12
    :TC naming code description: 100->Payment Method
                                102->BQR
                                012-> TC12
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")
        portal_username = read_config("credentials", "username_portal")
        portal_password = read_config("credentials", "password_portal")
        org_code = read_config("testdata", "org_code_hdfc")
        api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        query = "update bharatqr_provider_config set auto_check_status_enabled = 0 where id = '2'"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result of updating autocheck status in db is : {result}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        logger.info("Finished performing preconditions before starting test case execution")

        GlobalVariables.setupCompletedSuccessfully = True

        #---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)
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
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(401, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch expired transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_expired = result["id"].iloc[0]
            auth_code = "AE" + txn_id_expired.split('E')[1]
            rrn = "RE" + txn_id_expired.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code and RRN from data base : Txn_id expired : {txn_id_expired}, Auth code : {auth_code}, RRN : {rrn}")
            logger.info(f"Waiting for QR code to get Expired.. Please wait")
            sleep(61)
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id_expired, "TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            logger.info(f"Logining in to app again with username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]

            logger.info(f"Execution is completed for the test case : {testcase_id}")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()
            logger.error(f"Test case execution failed due to the exception : {e}")
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info(f"Starting App Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:AUTHORIZED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount), "Payment Status Original": "STATUS:EXPIRED", "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id_expired, "Payment Amt Original": str(amount)}

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

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt), "Payment Status Original": app_payment_status_original, "Payment mode Original": app_payment_mode_original, "Payment Txn ID Original": app_txn_id_original, "Payment Amt Original": str(app_payment_amt_original)}
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
                logger.info(f"Starting API Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"AUTHORIZED","Amount": amount, "Payment Mode": "BHARATQR", "Payment Status Original":"EXPIRED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_expired})
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
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api, "Payment Status Original":status_api_orginal,"Amount Original": amount_api_original, "Payment Mode Original": payment_mode_api_orginal}
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
                logger.info(f"Starting DB Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount), "Payment Status Original":"EXPIRED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                #
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_expired + "'"
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
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db, "Payment Status Original":status_db_original,"Amount Original": amount_db_original, "Payment Mode Original": payment_mode_db_original}

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
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"BHARATQR" , "Payment amount":str(amount), "Payment Status Original":"Expired","Amount Original": str(amount), "Payment Mode Original": "BHARATQR"}
                #
                ui_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(ui_driver)
                username_portal = read_config("credentials", 'username_portal')
                password_portal = read_config('credentials', 'password_portal')
                logger.info(f"Logging in Portal using username : {username_portal}")
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(ui_driver)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id)
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                portal_status_original = homePagePortal.fetch_status_from_transaction_id(txn_id_expired)
                portal_txn_type_original = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id_expired)
                portal_amt_original = homePagePortal.fetch_amount_from_transaction_id(txn_id_expired)
                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")       #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Payment Status Original":portal_status_original,"Amount Original": str(portal_amt_original.split('.')[1]), "Payment Mode Original": portal_txn_type_original}

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

    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
        logger.info(
            f"**********Test case Execution and Validation completed for testcase: {testcase_id}**************")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting all the settings that were done as preconditions")
        api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 6
        logger.debug(f"API details  : {api_details} ")
        print("***********API DETAILS **********:", api_details)
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        query = "update bharatqr_provider_config set auto_check_status_enabled = 1 where id = '2'"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result of updating autocheck status in db is : {result}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        logger.info("Reverted back all the settings that were done as preconditions")

        # ----------------------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_013():
    """
    :Description: Verification of  a BQR expired Callback when auto refund enabled via HDFC
    :Sub Feature code: UI_Common_PM_BQR_Expired_Callback_AutoRefund_enabled_HDFC_13
    :TC naming code description: 100->Payment Method
                                102->BQR
                                013-> TC13
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")
        portal_username = read_config("credentials", "username_portal")
        portal_password = read_config("credentials", "password_portal")
        org_code = read_config("testdata", "org_code_hdfc")
        api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        api_details = DBProcessor.get_api_details('AutoRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        query = "update bharatqr_provider_config set auto_check_status_enabled=0 where id='2'"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result from updating autocheck status is : {result}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        logger.info("Finished performing preconditions before starting test case execution")

        GlobalVariables.setupCompletedSuccessfully = True
        #---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)
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
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(401, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch expired transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_expired = result["id"].iloc[0]
            auth_code = "AE" + txn_id_expired.split('E')[1]
            rrn = "RE" + txn_id_expired.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code and RRN from data base : Txn_id expired : {txn_id_expired}, Auth code : {auth_code}, RRN : {rrn}")
            logger.info(f"Waiting for QR code to get Expired.. Please wait")
            sleep(61)
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id_expired, "TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            logger.info(f"Logining in to app again with username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]

            logger.info(f"Execution is completed for the test case : {testcase_id}")
            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()
            logger.error(f"Test case execution failed due to the exception : {e}")
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info(f"Starting App Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:REFUND_PENDING", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount), "Payment Status Original": "STATUS:EXPIRED", "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id_expired, "Payment Amt Original": str(amount)}

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

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt), "Payment Status Original": app_payment_status_original, "Payment mode Original": app_payment_mode_original, "Payment Txn ID Original": app_txn_id_original, "Payment Amt Original": str(app_payment_amt_original)}
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
                logger.info(f"Starting API Validation for the test case : {testcase_id}")

                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"REFUND_PENDING","Amount": amount, "Payment Mode": "BHARATQR", "Payment Status Original":"EXPIRED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id_expired})
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
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api, "Payment Status Original":status_api_orginal,"Amount Original": amount_api_original, "Payment Mode Original": payment_mode_api_orginal}
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
                logger.info(f"Starting DB Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "REFUND_PENDING", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount), "Payment Status Original":"EXPIRED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                #
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_expired + "'"
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
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db, "Payment Status Original":status_db_original,"Amount Original": amount_db_original, "Payment Mode Original": payment_mode_db_original}

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
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Refund Pending", "Payment mode":"BHARATQR" , "Payment amount":str(amount), "Payment Status Original":"Expired","Amount Original": str(amount), "Payment Mode Original": "BHARATQR"}
                #
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = read_config("credentials", 'username_portal')
                password_portal = read_config('credentials', 'password_portal')
                logger.info(f"Logging in Portal using username : {username_portal}")
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id)
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                portal_status_original = homePagePortal.fetch_status_from_transaction_id(txn_id_expired)
                portal_txn_type_original = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id_expired)
                portal_amt_original = homePagePortal.fetch_amount_from_transaction_id(txn_id_expired)
                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Payment Status Original":portal_status_original,"Amount Original": str(portal_amt_original.split('.')[1]), "Payment Mode Original": portal_txn_type_original}

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

    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
        logger.info(
            f"**********Test case Execution and Validation completed for testcase: {testcase_id}**************")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        logger.info("Reverting all the settings that were done as preconditions")
        api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 6
        logger.debug(f"API details  : {api_details} ")
        print("***********API DETAILS **********:", api_details)
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        query = "update bharatqr_provider_config set auto_check_status_enabled=1 where id='2'"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result from updating autocheck status is : {result}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        api_details = DBProcessor.get_api_details('AutoRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        logger.info("Reverted back all the settings that were done as preconditions")

        # ----------------------------------------------------------------------------------------------------------
