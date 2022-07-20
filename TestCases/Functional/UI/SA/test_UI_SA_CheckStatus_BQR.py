from datetime import datetime
import pytest

from Configuration import Configuration
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from DataProvider.config import TestData
from Utilities.ConfigReader import read_config
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, APIProcessor, DBProcessor



@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_SA_CheckStatus_BQR_01(): #Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        global bool_val_exe
        bool_val_exe = True
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            driver = GlobalVariables.appDriver
            loginPage = LoginPage(driver)
            username = read_config("credentials", 'username_dev11')
            password = read_config("credentials", 'password_dev11')
            loginPage.perform_login(username, password)
            homePage = HomePage(driver)
            homePage.check_home_page_logo()
            amount = TestData.AMOUNT
            order_num = TestData.ORDER_NUMBER
            homePage.enter_amount_and_order_number(amount, order_num)
            paymentPage = PaymentPage(driver)
            paymentPage.is_payment_page_displayed()
            paymentPage.click_on_Bqr_paymentMode()
            text = paymentPage.validate_upi_bqr_payment_screen()
            assert text == "Scan QR code using"
            driver.terminate_app("com.ezetap.basicapp")
            driver.activate_app("com.ezetap.basicapp")
            loginPage = LoginPage(driver)
            loginPage.perform_login(username, password)
            homePage = HomePage(driver)
            homePage.enter_amount_and_order_number(amount, order_num)
            homePage.perform_check_status()
            paymentPage = PaymentPage(driver)
            payment_status = paymentPage.fetch_payment_status()
            payment_mode = paymentPage.fetch_payment_mode()
            txn_id, status = paymentPage.get_transaction_details()
            paymentPage.click_on_proceed_homepage()

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
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
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "Payment Successful", "Payment mode": "Bharat QR"}



                actualAppValues = {"Payment Status": payment_status, "Payment mode": payment_mode}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Payment Status":"AUTHORIZED","Amount": amount, "Payment Mode": "BHARATQR"}
                response = APIProcessor.post(TestData.payload, TestData.API)
                print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api=''
                for li in list:
                    if li["txnId"] == txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": status, "Payment mode":"BHARATQR" , "Payment amount":amount}
                #
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": status}
                #
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = read_config("credentials", 'username_portal')
                password_portal = read_config('credentials', 'password_portal')
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name(read_config("testdata", "org_code"))
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                text = homePagePortal.fetch_status_from_transaction_id(txn_id)
                print("Status of txn:", text)
                #
                actualPortalValues = {"Payment Status": text}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of Portal Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        Configuration.executeFinallyBlock("test_UI_SA_CheckStatus_BQR_01")

