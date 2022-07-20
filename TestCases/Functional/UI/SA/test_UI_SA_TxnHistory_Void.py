from datetime import datetime
import pytest
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.App_FiltersPage import FiltersPage
from DataProvider.config import TestData
from Utilities.ConfigReader import read_config
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, APIProcessor, DBProcessor


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_SA_TxnHistory_Void_01(): #Make sure to add the test case name as same as the sub feature code.
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
            homePage.click_on_history()
            transactionsHistoryPage = TransHistoryPage(driver)
            transactionsHistoryPage.click_filter()
            filtersPage = FiltersPage(driver)
            filtersPage.apply_filter_card_and_success()
            transactionsHistoryPage.click_first_amount_field()
            text = transactionsHistoryPage.click_void_tarnsaction()  # STATUS:VOIDED
            text = text.split(":")[1]
            auth_code = transactionsHistoryPage.fetch_auth_code_text()
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
                expectedAppValues = {"Status": "VOIDED"}
                #

                #
                actualAppValues = {"Status": text}
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
                expectedAPIValues = {"Status": "VOIDED"}
                #
                response = APIProcessor.post(TestData.payload, TestData.API)
                list = response["txns"]
                status = ''
                for li in list:
                    if li["authCode"] == auth_code:
                        status = li["status"]
                        break
                #
                actualAPIValues = {"Status": status}
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
                expectedDBValues = {"Status": "VOIDED"}
                #
                query = "select status from txn where auth_code = '" + auth_code + "' and org_code = '" + read_config(
                    "testdata", "org_code") + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                result = result["status"].iloc[0]
                print("Result DB:", result)
                #
                actualDBValues = {"Status": result}
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
                expectedPortalValues = {"Status": "VOIDED"}
                #
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = read_config("credentials", 'username_portal')
                password_portal = read_config('credentials', 'password_portal')
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name(read_config("org_code", "org_code"))
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                homePagePortal.search_by_auth_code(auth_code)
                text = homePagePortal.fetch_status_of_transaction().upper()
                #
                actualPortalValues = {"Status": text}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_SA_TxnHistory_Void_01")