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


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Performing a successful upi txn via HDFC using SA check status
def test_sa_100_101_001():
    # Make sure to add the test case name as same as the sub feature code.
    try:# -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True   # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '5784758454'
            password = 'A123456'
            loginPage.perform_login(username, password)
            amount = random.randint(300, 399)
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            time.sleep(2)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Upi_paymentMode()
            time.sleep(10)
            paymentPage.click_back_btn_upi_bqr_payment_screen()
            paymentPage.click_cancel_btn_upi_bqr_payment_screen()

            Txn_id, status = paymentPage.get_transaction_details()
            paymentPage.click_on_proceed_homepage()

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
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
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment mode": "UPI","Status": "AUTHORIZED", "Amount": str(amount),
                                     "Txn_id": Txn_id}

                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(driver)
                txnHistoryPage.click_first_amount_field()
                payment_status = txnHistoryPage.fetch_txn_status_text()
                print("Fetching status from txn history page", payment_status)
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                print("Fetching payment mode from txn history page",payment_mode)
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                print("Fetching txn_id from txn history page", app_txn_id)
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                print("Fetching txn amount from txn history page", app_amount)
                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": username, "password": password}
                response = APIProcessor.post(payload, TestData.API)
                print(response)
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
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment State": "AUTHORIZED", "Payment mode": "UPI", "Payment amount": amount,
                                    "UPI_Txn_Status":"AUTHORIZED"}
                query = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query to fetch data from txn table:", query)
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                print("Query to fetch data from upi_txn table:", query)
                result = DBProcessor.getValueFromDB(query)
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status":upi_status_db}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Authorized", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                #
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()

                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                print("Status of txn:", portalStatus)
                # if portalStatus == 'Settled':
                #     portalStatus = 'AUTHORIZED'
                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)
                #
                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                        "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_sa_100_101_001")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Performing a failed UPI txn via HDFC using SA check status
def test_sa_100_101_002():
    # Make sure to add the test case name as same as the sub feature code.
    try:# -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True   # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '5784758454'
            password = 'A123456'
            loginPage.perform_login(username, password)
            amount = random.randint(101, 200)
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Upi_paymentMode()
            time.sleep(10)
            paymentPage.click_back_btn_upi_bqr_payment_screen()
            paymentPage.click_cancel_btn_upi_bqr_payment_screen()

            query = "select * from upi_txn where org_code = 'UPIHDFCBANKHDFCPG' order by created_time desc limit 1;"
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['txn_id'].values[0]

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
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
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment mode": "UPI","Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                driver.reset()
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(driver)
                txnHistoryPage.click_first_amount_field()
                payment_status = txnHistoryPage.fetch_txn_status_text()
                print("Fetching status from txn history page", payment_status)
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                print("Fetching payment mode from txn history page",payment_mode)
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                print("Fetching txn_id from txn history page", app_txn_id)
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                print("Fetching txn amount from txn history page", app_amount)
                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": username, "password": password}
                response = APIProcessor.post(payload, TestData.API)
                print(response)
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
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment State": "FAILED", "Payment mode": "UPI", "Payment amount": amount,
                                    "UPI_Txn_Status":"FAILED"}
                query = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query to fetch data from txn table:", query)
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = int(result["state"].iloc[0])

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                print("Query to fetch data from upi_txn table:", query)
                result = DBProcessor.getValueFromDB(query)
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status":upi_status_db}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                #
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()

                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                print("Status of txn:", portalStatus)
                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)
                #
                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                        "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_sa_100_101_002")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)

