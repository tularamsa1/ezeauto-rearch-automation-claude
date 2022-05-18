from datetime import datetime
import pytest
from PageFactory.App_FiltersPage import FiltersPage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities.ConfigReader import read_config
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader

'''''''''
@pytest.mark.usefixtures("log_on_success")
@pytest.mark.appVal
def test_UI_SA_TxnHistory_Filters_01(method_setup,appium_driver):

    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True

    #  =============Execution Block=====================

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
        transactionsHistoryPage.click_filter()
        filterPage = FiltersPage(driver)
        filterPage.click_on_select_date()
        filterPage.select_particular_date(read_config("testdata","transactions_by_date"))
        filterPage.click_ok_button()
        filterPage.click_on_apply_filter()

        Utilities.ReportProcessor.get_TC_Exe_Time()
    except Exception as e:
        print(e)
        Utilities.ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        #GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

    else:
        # ======================Validation Block==========================
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # ====================APP validation==========================
        try:
            element=transactionsHistoryPage.check_for_elements_in_txn_history()
            if element:
                result = "SUCCESS"
            else:
                result = "FAILURE"

            expectedAPPValues = "SUCCESS:"+result
        except Exception as e:
            print("Exception:", e)
            print("APP Validation did not complete due to exception")
            print("")
            expectedAPPValues = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False

        success = Utilities.Validator.validateValues("", "", "", expectedAPPValues)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()
'''''




@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.appVal
def test_UI_SA_TxnHistory_Filters_01():
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
            homepage_text = homePage.check_home_page_logo()
            assert homepage_text == ConfigReader.read_config("testdata", 'homepage_text')
            homePage.click_on_history()
            transactionsHistoryPage = TransHistoryPage(driver)
            transactionsHistoryPage.click_filter()
            filterPage = FiltersPage(driver)
            filterPage.click_on_select_date()
            filterPage.select_particular_date(read_config("testdata", "transactions_by_date"))
            filterPage.click_ok_button()
            filterPage.click_on_apply_filter()
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
                element = transactionsHistoryPage.check_for_elements_in_txn_history()
                if element:
                    result = "SUCCESS"
                else:
                    result = "FAILURE"
                #
                actualAppValues = {"Result": result}
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
                expectedPortalValues = {}
                #
                pass
                #
                actualPortalValues = {}
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
        Configuration.executeFinallyBlock("test_UI_SA_TxnHistory_Filters_01")