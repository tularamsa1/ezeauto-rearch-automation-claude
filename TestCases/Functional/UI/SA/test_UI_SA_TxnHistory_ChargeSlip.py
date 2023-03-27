from datetime import datetime
import pytest

from DataProvider.config import TestData
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from DataProvider import GlobalVariables
from Utilities.ConfigReader import read_config
from Configuration import Configuration
from Utilities import Validator, ReportProcessor, ConfigReader

'''''''''
@pytest.mark.usefixtures("log_on_success")
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_SA_TxnHistory_ChargeSlip_01(method_setup, appium_driver,ui_driver):
    GlobalVariables.api_logs = True
    GlobalVariables.portal_logs = True
    GlobalVariables.cnpware_logs = False
    GlobalVariables.middleware_logs = False

    global success_Val_Execution
    success_Val_Execution = True

    # =============Execution Block=====================
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_dev11')
        password = read_config("credentials", 'password_dev11')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homepage_text = homePage.check_home_page_logo()
        assert homepage_text == TestData.HOMEPAGE_TEXT
        homePage.click_on_history()
        transactionsHistoryPage = TransHistoryPage(driver)
        transactionsHistoryPage.click_first_amount_field()
        text = transactionsHistoryPage.click_charge_slip()
        assert text == 'Receipt'
        receipt_view = ''

        Utilities.ReportProcessor.get_TC_Exe_Time()

    except Exception as e:
        print(e)
        Utilities.ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        pytest.fail()

    else:
        # ======================Validation Block==========================
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # ====================APP validation==========================
        try:
            try:
                print("Try block")
                transactionsHistoryPage.check_receipt_not_shown()
                receipt_view = "FAILURE"
            except:
                print("Except block")
                receipt_view = "SUCCESS"
            expectedAPPValues = "SUCCESS:"+receipt_view
        except Exception as e:
            print("Exception:", e)
            print("APP Validation did not complete due to exception")
            print("")
            expectedAPPValues = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False


  #  ==========================Portal validation===============================
        try:
            driver_ui = GlobalVariables.portalDriver
            loginPagePortal = PortalLoginPage(driver_ui)
            username_portal = read_config("credentials", 'username_portal')
            password_portal = read_config('credentials', 'password_portal')
            loginPagePortal.perform_login_to_portal(username_portal, password_portal)
            homePagePortal = PortalHomePage(driver_ui)
            homePagePortal.search_merchant_name(read_config("testdata","org_code"))
            homePagePortal.click_switch_button()
            homePagePortal.click_transaction_search_menu()
            text = homePagePortal.click_charge_slip_of_transaction()
            print("Receipt txt", text)
            expectedPortalValues = "SALE:"+text
            print("Expected portal values", expectedPortalValues)
        except:
            print("Portal Validation did not complete due to exception")
            print("")
            expectedPortalValues = "Failed"
            GlobalVariables.EXCEL_Portal_Val = "Fail"
            success_Val_Execution = False

        success = Utilities.Validator.validateValues("", "", expectedPortalValues, expectedAPPValues)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()
'''''

@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_SA_TxnHistory_ChargeSlip_01(): #Make sure to add the test case name as same as the sub feature code.
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
            #
            driver = GlobalVariables.appDriver
            loginPage = LoginPage(driver)
            username = read_config("credentials", 'username_dev11')
            password = read_config("credentials", 'password_dev11')
            loginPage.perform_login(username, password)
            homePage = HomePage(driver)
            homepage_text = homePage.check_home_page_logo()
            assert homepage_text == ConfigReader.read_config("testdata", 'homepage_text')
            homePage.enter_amount_and_order_number(TestData.AMOUNT, TestData.ORDER_NUMBER)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Cash()
            paymentPage.click_on_confirm()
            paymentPage.click_on_proceed_homepage()

            homePage.click_on_history()
            transactionsHistoryPage = TransHistoryPage(driver)
            transactionsHistoryPage.click_first_amount_field()
            text = transactionsHistoryPage.click_charge_slip()
            assert text == 'Receipt'
            receipt_view = ''
            #
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
                expectedAppValues = {"Receipt": "SUCCESS"}
                #
                try:
                    print("Try block")
                    transactionsHistoryPage.check_receipt_not_shown()
                    receipt_view = "FAILURE"
                except:
                    print("Except block")
                    receipt_view = "SUCCESS"
                #
                actualAppValues = {"Receipt": receipt_view}
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
                expectedAPIValues = {}
                #
                pass
                #
                actualAPIValues = {}
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
                expectedDBValues = {}
                #
                pass
                #
                actualDBValues = {}
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
                expectedPortalValues = {"Receipt": "SALE"}
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
                text = homePagePortal.click_charge_slip_of_transaction()
                print("Receipt txt", text)
                #
                actualPortalValues = {"Receipt": text}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of Portal Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)
        Configuration.executeFinallyBlock("test_UI_SA_TxnHistory_ChargeSlip_01")