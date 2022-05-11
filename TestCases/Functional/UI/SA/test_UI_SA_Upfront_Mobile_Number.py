import allure
import pytest

import Utilities.ReportProcessor
import Utilities.Validator
from DataProvider import GlobalVariables
from PageFactory.App_AccountPage import AccountPage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.App_PaymentPage import PaymentPage
from TestCases import setUp
from allure_commons.types import AttachmentType
from datetime import datetime
from DataProvider.config import TestData
from Utilities import ConfigReader
from Utilities.APIPost import post
from Utilities.ConfigReader import read_config


@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.usefixtures("log_on_success")
def test_UI_SA_Upfront_Mobile_Number_01(method_setup,appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_EZETAP')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homePage.wait_for_home_page_load()
        homePage.enter_amount_order_number_and_customer_details(TestData.AMOUNT, TestData.ORDER_NUMBER,read_config("credentials","Mobile_Number"),read_config("credentials","Email"))
        Utilities.ReportProcessor.get_TC_Exe_Time()

    except:
        allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                      attachment_type=AttachmentType.PNG)
        Utilities.ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

        # ======================APP Validation=======================
    else:
        print("===============Inside validation==================")
        global expectedAPPValue
        global Email,MobNum
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            print("===========Inside Try============")
            # validation
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Cash()
            paymentPage.click_on_view_btn()
            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                          attachment_type=AttachmentType.PNG)
            paymentPage.click_on_dismiss()
            paymentPage.click_on_confirm()
            paymentPage.click_on_proceed_homepage()
            expectedAPPValue = "Success:Success"
        except Exception as e:
            print(e,"Exception")
            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                          attachment_type=AttachmentType.PNG)
            print("App Validation did not complete")
            print("")
            GlobalVariables.app_ValidationFailureCount += 1
            expectedAPPValue = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False

        success = Utilities.Validator.validateValues("", "", "", expectedAPPValue)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()