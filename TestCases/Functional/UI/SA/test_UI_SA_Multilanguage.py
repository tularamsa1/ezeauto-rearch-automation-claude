import allure
import pytest

from DataProvider import GlobalVariables
from PageFactory.App_AccountPage import AccountPage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from TestCases import setUp
from allure_commons.types import AttachmentType
from datetime import datetime
from Utilities import configReader
from Utilities.APIPost import post
from Utilities.configReader import read_config


@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.usefixtures("log_on_success")
def test_UI_SA_Multilanguage_English_01(method_setup,appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    global Hometext, HistoryText, LangText
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_EngLang')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homePage.wait_for_home_page_load()
        Hometext = homePage.get_EnterAmt_text()
        homePage.click_on_history()
        transactionHistoryPage = TransHistoryPage(driver)
        HistoryText = transactionHistoryPage.get_summary_text()
        transactionHistoryPage.click_back_Btn()
        homePage.wait_for_home_page_load()
        homePage.click_side_menu_eng()
        homePage.click_on_merchant_name()
        accountPage = AccountPage(driver)
        accountPage.click_on_setting()
        LangText = accountPage.get_Lang_text()
        setUp.get_TC_Exe_Time()

    except:
        allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                      attachment_type=AttachmentType.PNG)
        setUp.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()
    #======================APP Validation=======================
    else:
        print("===============Inside validation==================")
        global expectedAPPValue
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            print("===========Inside Try============")
            #validation
            expectedAPPValue = "Enter Amount:" + str(Hometext) +",Summary:" + str(HistoryText) + ",English:" + str(LangText)
            print(expectedAPPValue)
        except:

            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                              attachment_type=AttachmentType.PNG)
            print("App Validation did not complete")
            print("")
            GlobalVariables.app_ValidationFailureCount +=1
            expectedAPPValue = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False
            print(expectedAPPValue)

        #========================API Validation==================================

        try:
            global expectedAPIValue
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            current = datetime.now()
            #GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
            login_payload = {'username' : configReader.read_config("credentials", "username_EngLang"), 'password' : configReader.read_config("credentials", "password")}
            list = post(login_payload,configReader.read_config("credentials", "loginurl"))
            result = list['setting']['userAppOptions']['preferences']['language']['value']
            expectedAPIValue = "English:" + str(result)
        except:

            print("Inside except block")
            print("API Validation did not complete")
            print("")
            GlobalVariables.api_ValidationFailureCount += 1
            expectedAPIValue = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        success = setUp.validateValues(expectedAPIValue, "", "", expectedAPPValue)

        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()




@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.usefixtures("log_on_success")
def test_UI_SA_Multilanguage_Hindi_02(method_setup,appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    global Hometext, HistoryText, LangText
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_HindiLang')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homePage.wait_for_home_page_load()
        Hometext = homePage.get_EnterAmt_text()
        homePage.click_on_history()
        transactionHistoryPage = TransHistoryPage(driver)
        HistoryText = transactionHistoryPage.get_summary_text()
        transactionHistoryPage.click_back_Btn()
        homePage.wait_for_home_page_load()
        homePage.click_side_menu_hindi()
        homePage.click_on_merchant_name()
        accountPage = AccountPage(driver)
        accountPage.click_on_setting()
        LangText = accountPage.get_Lang_text()
        setUp.get_TC_Exe_Time()

    except:
        allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                      attachment_type=AttachmentType.PNG)
        setUp.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()
    #======================APP Validation=======================
    else:
        print("===============Inside validation==================")
        global expectedAPPValue
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            print("===========Inside Try============")
            #validation
            expectedAPPValue = "राशि दर्ज करें:" + str(Hometext) +",सारांश:" + str(HistoryText) + ",हिंदी:" + str(LangText)
            print(expectedAPPValue)
        except:

            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                              attachment_type=AttachmentType.PNG)
            print("App Validation did not complete")
            print("")
            GlobalVariables.app_ValidationFailureCount +=1
            expectedAPPValue = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False
            print(expectedAPPValue)


        #========================API Validation==================================

        try:
            global expectedAPIValue
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            current = datetime.now()
            #GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
            login_payload = {'username' : configReader.read_config("credentials", "username_HindiLang"), 'password' : configReader.read_config("credentials", "password")}
            list = post(login_payload,configReader.read_config("credentials", "loginurl"))
            result = list['setting']['userAppOptions']['preferences']['language']['value']
            expectedAPIValue = "Hindi:" + str(result)
        except:

            print("Inside except block")
            print("API Validation did not complete")
            print("")
            GlobalVariables.api_ValidationFailureCount += 1
            expectedAPIValue = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        success = setUp.validateValues(expectedAPIValue, "", "", expectedAPPValue)

        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()




@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.usefixtures("log_on_success")
def test_UI_SA_Multilanguage_English_to_Hindi_03(method_setup,appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    global Hometext, HistoryText, LangText
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_EZETAP')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homePage.wait_for_home_page_load()
        Hometext = homePage.get_EnterAmt_text()
        homePage.click_on_history()
        transactionHistoryPage = TransHistoryPage(driver)
        HistoryText = transactionHistoryPage.get_summary_text()
        transactionHistoryPage.click_back_Btn()
        homePage.wait_for_home_page_load()
        homePage.click_side_menu_eng()
        homePage.click_on_merchant_name()
        accountPage = AccountPage(driver)
        accountPage.click_on_setting()
        accountPage.click_on_Language()
        accountPage.click_on_hindi_Lang()
        accountPage.click_on_proceed_btn()
        homePage.wait_for_home_page_load()
        homePage.click_side_menu_hindi()
        homePage.click_on_merchant_name()
        accountPage.click_on_setting()
        LangText = accountPage.get_Lang_text()
        setUp.get_TC_Exe_Time()

    except:
        allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                  attachment_type=AttachmentType.PNG)
        setUp.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

# ======================APP Validation=======================
    else:
        print("===============Inside validation==================")
        global expectedAPPValue
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            print("===========Inside Try============")
            # validation
            expectedAPPValue = "हिंदी:" + str(LangText)
            print(expectedAPPValue)
        except:

            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                  attachment_type=AttachmentType.PNG)
            print("App Validation did not complete")
            print("")
            GlobalVariables.app_ValidationFailureCount += 1
            expectedAPPValue = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False
            print(expectedAPPValue)

# ========================API Validation==================================

        try:
            global expectedAPIValue
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            current = datetime.now()
            # GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
            login_payload = {'username': configReader.read_config("credentials", "username_EngLang"),
                     'password': configReader.read_config("credentials", "password")}
            list = post(login_payload, configReader.read_config("credentials", "loginurl"))
            result = list['setting']['userAppOptions']['preferences']['language']['value']
            expectedAPIValue = "Hindi:" + str(result)
        except:

            print("Inside except block")
            print("API Validation did not complete")
            print("")
            GlobalVariables.api_ValidationFailureCount += 1
            expectedAPIValue = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        success = setUp.validateValues(expectedAPIValue, "", "", expectedAPPValue)

        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()



@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.usefixtures("log_on_success")
def test_UI_SA_Multilanguage_Hindi_to_English_04(method_setup,appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    global Hometext, HistoryText, LangText
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_EZETAP')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homePage.wait_for_home_page_load()
        Hometext = homePage.get_EnterAmt_text()
        homePage.click_on_history()
        transactionHistoryPage = TransHistoryPage(driver)
        HistoryText = transactionHistoryPage.get_summary_text()
        transactionHistoryPage.click_back_Btn()
        homePage.wait_for_home_page_load()
        homePage.click_side_menu_hindi()
        homePage.click_on_merchant_name()
        accountPage = AccountPage(driver)
        accountPage.click_on_setting()
        accountPage.click_on_Language()
        accountPage.click_on_eng_Lang()
        accountPage.click_on_proceed_btn()
        homePage.wait_for_home_page_load()
        homePage.click_side_menu_eng()
        homePage.click_on_merchant_name()
        accountPage.click_on_setting()
        LangText = accountPage.get_Lang_text()
        setUp.get_TC_Exe_Time()
    except:
        allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                  attachment_type=AttachmentType.PNG)
        setUp.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

# ======================APP Validation=======================
    else:
        print("===============Inside validation==================")
        global expectedAPPValue
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            print("===========Inside Try============")
            # validation
            expectedAPPValue = "English:" + str(LangText)
            print(expectedAPPValue)
        except:

            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                  attachment_type=AttachmentType.PNG)
            print("App Validation did not complete")
            print("")
            GlobalVariables.app_ValidationFailureCount += 1
            expectedAPPValue = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False
            print(expectedAPPValue)


# ========================API Validation==================================

        try:
            global expectedAPIValue
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            current = datetime.now()
            # GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
            login_payload = {'username': configReader.read_config("credentials", "username_EngLang"),
                     'password': configReader.read_config("credentials", "password")}
            list = post(login_payload, configReader.read_config("credentials", "loginurl"))
            result = list['setting']['userAppOptions']['preferences']['language']['value']
            expectedAPIValue = "English:" + str(result)
        except:

            print("Inside except block")
            print("API Validation did not complete")
            print("")
            GlobalVariables.api_ValidationFailureCount += 1
            expectedAPIValue = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        success = setUp.validateValues(expectedAPIValue, "", "", expectedAPPValue)

        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()



#Below test case works for only new user
@pytest.mark.appVal
@pytest.mark.usefixtures("log_on_success")
def test_UI_SA_Multilanguage_Lang_selection_05(method_setup,appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    global Hometext, HistoryText, LangText
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_EZETAP')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homePage.check_lang_selection_option()
        homePage.select_eng_language()
        homePage.click_on_lang_proceed()
        homePage.wait_for_home_page_load()
        homePage.wait_for_home_page_load()
        Hometext = homePage.get_EnterAmt_text()
        homePage.click_on_history()
        transactionHistoryPage = TransHistoryPage(driver)
        HistoryText = transactionHistoryPage.get_summary_text()
        transactionHistoryPage.click_back_Btn()
        homePage.wait_for_home_page_load()
        homePage.click_side_menu_hindi()
        homePage.click_on_merchant_name()
        accountHomePage = AccountPage(driver)
        accountHomePage.click_on_setting()
        accountHomePage.click_on_Language()
        accountHomePage.click_on_eng_Lang()
        accountHomePage.click_on_proceed_btn()
        homePage.wait_for_home_page_load()
        homePage.click_side_menu_eng()
        homePage.click_on_merchant_name()
        accountHomePage.click_on_setting()
        LangText = accountHomePage.get_Lang_text()
        setUp.get_TC_Exe_Time()

    except:
        allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                  attachment_type=AttachmentType.PNG)
        setUp.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution: Language selection is not enabled")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

# ======================APP Validation=======================
    else:
        print("===============Inside validation==================")
        global expectedAPPValue
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            print("===========Inside Try============")
            # validation
            expectedAPPValue = "English:" + str(LangText)
            print(expectedAPPValue)
        except:

            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                  attachment_type=AttachmentType.PNG)
            print("App Validation did not complete")
            print("")
            GlobalVariables.app_ValidationFailureCount += 1
            expectedAPPValue = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False
            print(expectedAPPValue)


# ========================API Validation==================================

        try:
            global expectedAPIValue
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            current = datetime.now()
            # GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
            login_payload = {'username': configReader.read_config("credentials", "username_EngLang"),
                     'password': configReader.read_config("credentials", "password")}
            list = post(login_payload, configReader.read_config("credentials", "loginurl"))
            result = list['setting']['userAppOptions']['preferences']['language']['value']
            expectedAPIValue = "English:" + str(result)
        except:

            print("Inside except block")
            print("API Validation did not complete")
            print("")
            GlobalVariables.api_ValidationFailureCount += 1
            expectedAPIValue = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        success = setUp.validateValues(expectedAPIValue, "", "", expectedAPPValue)

        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()

