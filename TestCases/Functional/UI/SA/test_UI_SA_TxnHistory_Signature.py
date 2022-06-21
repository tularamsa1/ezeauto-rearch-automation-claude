from datetime import datetime
import pytest
from PageFactory.App_FiltersPage import FiltersPage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from DataProvider.config import TestData
from Utilities.ConfigReader import read_config
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, APIProcessor


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.appVal
def test_UI_SA_TxnHistory_Signature_01(): #Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        global bool_val_exe
        bool_val_exe = True
        msg = ""

        #---------------------------Pre requisite----------------------------------------------
        payload = {
        "username":"9731545096",
        "password":"A123456",
        "entityName":"org",
        "settings":{
            "eSignatureForNonCardEnabled": "true",
            "signatureForCard": "ALWAYS"
        },
        "settingForOrgCode":"VINEET_191036200"
        }
        response = APIProcessor.post(payload, "orgupdate")
        if response["success"]==True:
            pass
        else:
            msg = "Pre requisite setting failure"
            pytest.fail(msg)
        #--------------------End of Pre requisite-----------------------------------


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
            homePage.enter_amount_and_order_number(TestData.AMOUNT, TestData.ORDER_NUMBER)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Cash()
            paymentPage.click_on_confirm()
            paymentPage.click_on_proceed_homepage()
            homePage.click_on_history()
            transactionsHistoryPage = TransHistoryPage(driver)
            transactionsHistoryPage.click_filter()
            filtersPage = FiltersPage(driver)
            filtersPage.apply_filter_card_and_success()
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
                transactionsHistoryPage.add_signature()
                #
                actualAppValues = {"Result": "SUCCESS"}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of App Validation---------------------------------------
#--------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)
        Configuration.executeFinallyBlock("test_UI_SA_TxnHistory_Signature_01")