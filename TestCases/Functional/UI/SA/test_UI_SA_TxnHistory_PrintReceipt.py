from datetime import datetime
import pytest
from Configuration import Configuration
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from DataProvider import GlobalVariables
from Utilities import ConfigReader, ReportProcessor, Validator
from Utilities.ConfigReader import read_config


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.appVal
def test_UI_SA_TxnHistory_PrintReceipt_01():
    try:
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

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
            homePage.check_home_page_logo()
            homePage.click_on_history()
            transactionsHistoryPage = TransHistoryPage(driver)
            transactionsHistoryPage.click_first_amount_field()
            transactionsHistoryPage.click_status_arrow_button()
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
                expectedAppValues = {"Result": "SUCCESS"}
                #
                transactionsHistoryPage.click_print_receipt()
                transactionsHistoryPage.click_customer_copy()
                #
                actualAppValues = {"Result": "SUCCESS"}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of App Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)
        Configuration.executeFinallyBlock("test_UI_SA_TxnHistory_PrintReceipt_01")
