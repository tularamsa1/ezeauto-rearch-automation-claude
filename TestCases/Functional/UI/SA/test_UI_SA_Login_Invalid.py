from datetime import datetime

import pytest

import Utilities.ReportProcessor
import Utilities.Validator
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from DataProvider.config import TestData
from TestCases import setUp
from DataProvider import GlobalVariables
from Utilities.ConfigReader import read_config


@pytest.mark.usefixtures("log_on_success")
@pytest.mark.appVal
def test_UI_SA_Login_Invalid_01(method_setup,appium_driver):

    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    # ----------------Execution Block--------------------------
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_dev11')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)

        Utilities.ReportProcessor.get_TC_Exe_Time()
    except:
        Utilities.ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        pytest.fail()

    else:
        # --------------Validation Block-----------------------------
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        # --------------APP validation-----------------------
        try:
            login = ''
            try:
                homePage.check_home_page_for_invalid_Login()
                login = 'Success'
            except:
                login = 'Failure'

            expectedAPPValues = "Failure:" + login
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
