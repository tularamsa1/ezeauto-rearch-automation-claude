from datetime import datetime

import pytest

import Utilities.ReportProcessor
import Utilities.Validator
from PageFactory.App_AccountPage import AccountPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from DataProvider.config import TestData
from TestCases import setUp
from DataProvider import GlobalVariables
from Utilities.ConfigReader import read_config


@pytest.mark.usefixtures("log_on_success")
@pytest.mark.appVal
def test_UI_SA_Logout_Success_01(method_setup,appium_driver):

    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = True
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
#----------------Execution Block--------------------------
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_dev11')
        password = read_config("credentials", 'password_dev11')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homepage_text = homePage.check_home_page_logo()
        assert homepage_text == TestData.HOMEPAGE_TEXT
        homePage.click_account_menu()
        accountPage = AccountPage(driver)
        accountPage.click_on_logout()
        element=loginPage.validate_login_page()
        logout=''
        if element:
            logout="Success"
        else:
            logout="Failure"

        Utilities.ReportProcessor.get_TC_Exe_Time()
    except:
        Utilities.ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

    else:
         # --------------Validation Block-----------------------------
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        # --------------APP validation-----------------------
        try:

            expectedAPPValues = "Success:"+logout
        except:
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
