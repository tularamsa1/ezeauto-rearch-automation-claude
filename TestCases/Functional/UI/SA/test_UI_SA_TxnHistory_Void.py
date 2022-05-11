from datetime import datetime
import pytest

import Utilities.APIProcessor
import Utilities.DBProcessor
import Utilities.ReportProcessor
import Utilities.Validator
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.App_FiltersPage import FiltersPage
from DataProvider.config import TestData
from DataProvider import GlobalVariables
from TestCases import setUp
from Utilities.ConfigReader import read_config


@pytest.mark.usefixtures("log_on_success")
#@pytest.mark.portalVal
#@pytest.mark.appVal
def test_UI_SA_TxnHistory_Void_01(method_setup,appium_driver, ui_driver):

    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = True
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    global auth_code

   # 'select * from txn where auth_code = "D56598" and org_code = "VINEET_191036200"'

#-----------------Execution Block----------------------------
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
        filtersPage = FiltersPage(driver)
        filtersPage.apply_filter_card_and_success()
        transactionsHistoryPage.click_first_amount_field()
        text = transactionsHistoryPage.click_void_tarnsaction() # STATUS:VOIDED
        text = text.split(":")[1]
        auth_code = transactionsHistoryPage.fetch_auth_code_text()

        Utilities.ReportProcessor.get_TC_Exe_Time()
    except:
        Utilities.ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

    else:
        # -------------Validation Blcok-------------------------
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")



        # --------------APP validation-----------------------
        try:

            expectedAPPValues = "VOIDED:"+text
        except:
            print("APP Validation did not complete due to exception")
            print("")
            expectedAPPValues = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False


        # ----------------Portal validation-----------------------------------
        try:
            driver_ui = GlobalVariables.portalDriver
            loginPagePortal = PortalLoginPage(driver_ui)
            username_portal = read_config("credentials", 'username_portal')
            password_portal = read_config('credentials', 'password_portal')
            loginPagePortal.perform_login_to_portal(username_portal, password_portal)
            homePagePortal = PortalHomePage(driver_ui)
            homePagePortal.search_merchant_name(read_config("org_code","org_code"))
            homePagePortal.click_switch_button()
            homePagePortal.click_transaction_search_menu()
            homePagePortal.search_by_auth_code(auth_code)
            text = homePagePortal.fetch_status_of_transaction().upper()
            print("STatus of txn:", text)
            expectedPortalValues = "VOIDED:"+text
        except:
            print("Portal Validation did not complete due to exception")
            print("")
            expectedPortalValues = "Failed"
            GlobalVariables.EXCEL_Portal_Val = "Fail"
            success_Val_Execution = False


        # ---------------------DB validation-------------------------------

        try:

            query = "select status from txn where auth_code = '" +auth_code+"' and org_code = '"+read_config("testdata","org_code") +"'"
           # query = "select status from txn where rr_number='" +rr_num+ "'"
            print("Query:", query)
            result = Utilities.DBProcessor.getValueFromDB(query)
            result = result["status"].iloc[0]
            print("Result DB:", result)
            expectedDBValues = result + ":VOIDED"
        except:
            print("DB Validation did not complete due to exception")
            print("")
            expectedDBValues = "Failed"
            GlobalVariables.EXCEL_DB_Val = "Fail"
            success_Val_Execution = False

        # -------------------API validation---------------------------------
        try:
            response = Utilities.APIProcessor.post(TestData.payload, TestData.API)
            print(response)
            list = response["txns"]
            print("Response list: ", list)
            status = ''
            for li in list:
                if li["authCode"] == auth_code:
                    status = li["status"]
            expectedAPIValues ="VOIDED:"+ status
            print(expectedAPIValues)
        except:
            print("API Validation did not complete due to exception")
            print("")
            expectedAPIValues = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        success = Utilities.Validator.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, expectedAPPValues)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()