import random
import time
from datetime import datetime
import pytest
from Configuration import Configuration
from DataProvider import GlobalVariables
from DataProvider.config import TestData
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor
from Utilities.execution_log_processor import EzeAutoLogger
import requests
import json
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Performing a successful upi txn via HDFC using SA check status
def test_sa_100_101_001():  # Make sure to add the test case name as same as the sub feature code.
    logger.info("Starting execution for the test case : test_sa_100_101_001")

    try:  # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        app_driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            username = '5784758454'
            password = 'A123456'
            logger.info(f"Logging in the MPOSX application using username : {username} and password : {password}")
            loginPage = LoginPage(app_driver)
            loginPage.perform_login(username, password)
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            homePage = HomePage(app_driver)
            # homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")

            paymentPage.click_back_btn_upi_bqr_payment_screen()
            paymentPage.click_cancel_btn_upi_bqr_payment_screen()

            Txn_id, status = paymentPage.get_transaction_details()
            logger.debug(
                f"Fetching Txn_id and status from the payment successful screen : Txn_id : {Txn_id}, status : {status}")
            logger.debug("Clicking on proceed to home page button on the Payment successful screen on the MPOS")
            paymentPage.click_on_proceed_homepage()

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            logger.error(f"Test case execution failed due to the exception : {e}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        logger.info("Execution is completed for the test case : test_sa_100_101_001")
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------

        logger.info("Starting validation for the test case : test_sa_100_101_001")

        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info("Started APP validation for the test case : test_sa_100_101_001")
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment mode": "UPI", "Status": "AUTHORIZED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(app_driver)
                txnHistoryPage.click_on_transaction_by_order_id(order_id)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {Txn_id}, {payment_status}")
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {Txn_id}, {payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {Txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {Txn_id}, {app_amount}")
                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
                logger.debug(f"actualAppValues: {actualAppValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

            logger.info("Completed APP validation for the test case : test_sa_100_101_001")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info("Started API validation for the test case : test_sa_100_101_001")
            try:
                expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "UPI"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                response = APIProcessor.send_request(api_details)
                # response = APIProcessor.post(payload, TestData.API)
                # print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for li in list:
                    if li["txnId"] == Txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'

            logger.info("Completed API validation for the test case : test_sa_100_101_001")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info("Started DB validation for the test case : test_sa_100_101_001")
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment State": "SETTLED", "Payment mode": "UPI",
                                    "Payment amount": amount,
                                    "UPI_Txn_Status": "AUTHORIZED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")
                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info("Completed DB validation for the test case : test_sa_100_101_001")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info("Started PORTAL validation for the test case : test_sa_100_101_001")
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Settled", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")
                #
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                logger.debug(
                    f"Logging in to the portal with the username : {username_portal} and password : {password_portal}")
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                logger.debug(f"searching for the org_code : UPIHDFCBANKHDFCPG")
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()

                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                logger.debug(f"actualPortalValues : {actualPortalValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

            logger.info("Completed PORTAL validation for the test case : test_sa_100_101_001")
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_sa_100_101_001")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Performing a failed UPI txn via HDFC using SA check status
def test_sa_100_101_002():  # Make sure to add the test case name as same as the sub feature code.
    logger.info("Starting execution for the test case : test_sa_100_101_002")
    try:  # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        app_driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(app_driver)
            username = '5784758454'
            password = 'A123456'
            logger.info(f"Logging in the MPOSX application using username : {username} and password : {password}")
            loginPage.perform_login(username, password)
            amount = random.randint(100, 200)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            homePage = HomePage(app_driver)
            homePage.wait_for_home_page_load()
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            # time.sleep(10)
            paymentPage.click_back_btn_upi_bqr_payment_screen()
            paymentPage.click_cancel_btn_upi_bqr_payment_screen()

            # query = "select * from upi_txn where org_code = 'UPIHDFCBANKHDFCPG' order by created_time desc limit 1;"
            query = "select * from txn where org_code = 'UPIHDFCBANKHDFCPG' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            logger.error(f"Test case execution failed due to the exception : {e}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        logger.info("Execution is completed for the test case : test_sa_100_101_002")
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------

        logger.info("Starting validation for the test case : test_sa_100_101_002")

        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info("Started APP validation for the test case : test_sa_100_101_002")
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment mode": "UPI", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                logger.info("reseting the com.ezetap.basicapp")
                app_driver.reset()
                loginPage.perform_login(username, password)
                homepage_text = homePage.wait_for_home_page_load()

                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(app_driver)
                txnHistoryPage.click_on_transaction_by_order_id(order_id)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {Txn_id}, {payment_status}")
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {Txn_id}, {payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {Txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {Txn_id}, {app_amount}")
                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
                logger.debug(f"actualAppValues: {actualAppValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

            logger.info("Completed APP validation for the test case : test_sa_100_101_002")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info("Started API validation for the test case : test_sa_100_101_002")
            try:
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "UPI"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                response = APIProcessor.send_request(api_details)
                # logger.debug(f"payload : {payload} to trigger the {TestData.API} api and the API_OUTPUT is : {response}")
                # print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for li in list:
                    if li["txnId"] == Txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'

            logger.info("Completed API validation for the test case : test_sa_100_101_002")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info("Started DB validation for the test case : test_sa_100_101_002")
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment State": "FAILED", "Payment mode": "UPI",
                                    "Payment amount": amount,
                                    "UPI_Txn_Status": "FAILED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info("Completed DB validation for the test case : test_sa_100_101_002")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info("Started PORTAL validation for the test case : test_sa_100_101_002")
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                logger.debug(
                    f"Logging in to the portal with the username : {username_portal} and password : {password_portal}")
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)

                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                logger.debug(f"searching for the org_code : UPIHDFCBANKHDFCPG")
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()

                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                logger.debug(f"actualPortalValues : {actualPortalValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

            logger.info("Completed PORTAL validation for the test case : test_sa_100_101_002")
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_sa_100_101_002")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Performing a upi txn after expiry for HDFC using SA check status
def test_sa_100_101_003():  # Make sure to add the test case name as same as the sub feature code.
    logger.info("Starting execution for the test case : test_sa_100_101_003")
    try:  # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        url = "https://dev11.ezetap.com//api/2.0/setting/update/ "

        payload = json.dumps({
            "username": "9660867345",
            "password": "A123456",
            "entityName": "org",
            "settings": {
                "upiQRExpiryTime": 1
            },
            "settingForOrgCode": "UPIHDFCBANKHDFCPG"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '5784758454'
            password = 'A123456'
            logger.info(f"Logging in the MPOSX application using username : {username} and password : {password}")
            loginPage.perform_login(username, password)
            amount = random.randint(51, 100)
            if amount == 55:
                amount = 56
            # order_number = random.randint(1, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage = HomePage(driver)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")

            logger.info("reseting the com.ezetap.basicapp")
            driver.reset()
            logger.info("waiting for the time till qr get expired")
            time.sleep(60)

            loginPage.perform_login(username, password)
            logger.info(
                f"After reseting the app logging in again in the MPOSX application using username : {username} and password : {password}")
            homePage.enter_amount_and_order_number(amount, order_id)
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()

            paymentPage.click_on_proceed_homepage()
            homePage.click_on_back_btn_enter_amt_page()

            query = "select * from txn where org_code = 'UPIHDFCBANKHDFCPG' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.bool_ss_app_val = 'Failed'
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            logger.error(f"Test case execution failed due to the exception : {e}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        logger.info("Execution is completed for the test case : test_sa_100_101_003")
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------

        logger.info("Starting validation for the test case : test_sa_100_101_003")

        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info("Started APP validation for the test case : test_sa_100_101_003")
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment mode": "UPI", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                # driver.reset()
                # loginPage.perform_login(username, password)
                # homepage_text = homePage.check_home_page_logo()
                # assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(driver)
                # txnHistoryPage.click_first_amount_field()
                txnHistoryPage.click_on_transaction_by_order_id(order_id)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {Txn_id}, {payment_status}")
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {Txn_id}, {payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {Txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {Txn_id}, {app_amount}")

                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
                logger.debug(f"actualAppValues: {actualAppValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

            logger.info("Completed APP validation for the test case : test_sa_100_101_003")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info("Started API validation for the test case : test_sa_100_101_003")
            try:
                expectedAPIValues = {"Payment Status": "EXPIRED", "Amount": amount, "Payment Mode": "UPI"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
                response = APIProcessor.send_request(api_details)
                # logger.debug(f"payload : {payload} to trigger the {TestData.API} api and the API_OUTPUT is : {response}")
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for li in list:
                    if li["txnId"] == Txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'

            logger.info("Completed API validation for the test case : test_sa_100_101_003")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info("Started DB validation for the test case : test_sa_100_101_003")
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "EXPIRED", "Payment State": "FAILED", "Payment mode": "UPI",
                                    "Payment amount": amount,
                                    "UPI_Txn_Status": "EXPIRED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info("Completed DB validation for the test case : test_sa_100_101_003")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info("Started PORTAL validation for the test case : test_sa_100_101_003")
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Expired", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                logger.debug(
                    f"Logging in to the portal with the username : {username_portal} and password : {password_portal}")
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                logger.debug(f"searching for the org_code : UPIHDFCBANKHDFCPG")
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()

                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                logger.debug(f"actualPortalValues : {actualPortalValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

            logger.info("Completed PORTAL validation for the test case : test_sa_100_101_003")
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_sa_100_101_003")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            url = "https://dev11.ezetap.com//api/2.0/setting/update/ "

            payload = json.dumps({
                "username": "9660867345",
                "password": "A123456",
                "entityName": "org",
                "settings": {
                    "upiQRExpiryTime": 6
                },
                "settingForOrgCode": "UPIHDFCBANKHDFCPG"
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)
