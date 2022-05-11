from datetime import datetime
import pytest

import Utilities.ReportProcessor
import Utilities.Validator
from DataProvider import GlobalVariables
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from DataProvider.config import TestData
from TestCases import setUp
from Utilities.ConfigReader import read_config


@pytest.mark.usefixtures("log_on_success")
@pytest.mark.appVal
def test_UI_SA_Promo_Displayed_01(method_setup, appium_driver):

    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True

    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_dev11')
        password = read_config("credentials", 'password_dev11')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homepage_text = homePage.check_home_page_logo()
        assert homepage_text == TestData.HOMEPAGE_TEXT
        homePage.enter_amount_and_order_number(TestData.AMOUNT, TestData.ORDER_NUMBER)

        Utilities.ReportProcessor.get_TC_Exe_Time()
    except:
        Utilities.ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        pytest.fail()
    else:
        #validation execution part
        paymentPage = PaymentPage(driver)
        promo_message = paymentPage.fetch_promo_offer()
        print(promo_message)
        #Validation Part
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        #"actual:expected,actual2:expected2,actual3:expected3"
        try:
            expectedAPPValues = promo_message+":"+read_config("testdata","promo_offer")
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
