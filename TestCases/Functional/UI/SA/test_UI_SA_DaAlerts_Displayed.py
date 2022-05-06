from datetime import datetime
import pytest

from DataProvider import GlobalVariables
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from DataProvider.config import TestData
from TestCases import setUp
from Utilities.configReader import read_config


@pytest.mark.usefixtures("log_on_success")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.uiVal
@pytest.mark.appVal
def test_UI_SA_DaAlerts_Displayed_01(method_setup, appium_driver):

    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = True
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False
    print("Inside test case 1 ")
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

        setUp.get_TC_Exe_Time()
    except:
        setUp.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        pytest.fail()
    else:
        #validation execution part
        paymentPage = PaymentPage(driver)
        da_message = paymentPage.fetch_da_alert_message()
        print(da_message)
        #Validation Part
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        #"actual:expected,actual2:expected2,actual3:expected3"
        try:
            expectedAPPValues = da_message+":"+ TestData.DA_ALERT_MESSAGE
            #expectedAPPval = {"message":TestData.DA_ALERT_MESSAGE}
            #actualAPPval = {"message":da_message}
        except:
            print("APP Validation did not complete due to exception")
            print("")
            expectedAPPValues = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False

        success = setUp.validateValues("", "", "", expectedAPPValues)
        #success = setUp.validateValues("","","","","","",expectedAPPval,actualAPPval)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()
