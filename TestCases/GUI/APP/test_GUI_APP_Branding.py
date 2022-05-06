from datetime import datetime

import pytest

from DataProvider.config import TestData
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
import cv2

from TestCases import setUp
from DataProvider import GlobalVariables
import allure
from allure_commons.types import AttachmentType

from Utilities.configReader import read_config


@pytest.mark.appVal
@pytest.mark.usefixtures("log_on_success")
def test_GUI_APP_Branding_Ezetap_01(method_setup,appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    try:
        global originalImg
        global ActualImg
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_EZETAP')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        Home = HomePage(driver)
        Home.wait_for_home_page_load()
        ele = Home.get_home_page_logo()
        ele.screenshot("/home/oem/PycharmProjects/EzeAuto/Images/EZETAPComp.png")
        originalImg = cv2.imread("/home/oem/PycharmProjects/EzeAuto/Images/EZETAP.png")
        ActualImg = cv2.imread("/home/oem/PycharmProjects/EzeAuto/Images/EZETAPComp.png")
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

    else:
        print("===============Inside validation==================")
        global expectedAPPValue
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            print("===========Inside Try============")
            #validation
            difference = cv2.subtract(originalImg, ActualImg)
            #difference = abs(originalImg-ActualImg)
            b, g, r = cv2.split(difference)
            if originalImg.shape == ActualImg.shape:
                if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                    print("=======Image Comparison========")
                    expectedAPPValue = "Success:Success"
                else:
                    expectedAPPValue = "Success:Fail"
        except Exception as e:
            print("Inside Except condition")
            print(e)

            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                          attachment_type=AttachmentType.PNG)
            print("App Validation did not complete")
            print("")
            GlobalVariables.app_ValidationFailureCount +=1
            expectedAPPValue = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False
            print(expectedAPPValue)

        success = setUp.validateValues("", "", "", expectedAPPValue)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()


@pytest.mark.appVal
@pytest.mark.usefixtures("log_on_success")
def test_GUI_APP_Branding_Axis_02(method_setup,appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_AXIS')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homePage.wait_for_home_page_load()
        ele = homePage.get_home_page_logo()
        ele.screenshot("/home/oem/PycharmProjects/EzeAuto/Images/AXISComp.png")
        originalImg = cv2.imread("/home/oem/PycharmProjects/EzeAuto/Images/AXIS.png")
        ActualImg = cv2.imread("/home/oem/PycharmProjects/EzeAuto/Images/AXISComp.png")
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

    else:
        print("===============Inside validation==================")
        global expectedAPPValue
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            #print("===========Inside Try============")
            #validation
            difference = cv2.subtract(originalImg, ActualImg)
            b, g, r = cv2.split(difference)
            if originalImg.shape == ActualImg.shape:
                if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                    print("=======Image Comparison========")
                    expectedAPPValue = "Success:Success"
                else:
                    expectedAPPValue = "Success:Fail"
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

        success = setUp.validateValues("", "", "", expectedAPPValue)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()



@pytest.mark.appVal
@pytest.mark.usefixtures("log_on_success")
def test_GUI_APP_Branding_Hdfc_03(method_setup,appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_HDFC')
        password = read_config("credentials", 'password')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homePage.wait_for_home_page_load()
        ele = homePage.get_home_page_logo()
        ele.screenshot("/home/oem/PycharmProjects/EzeAuto/Images/HDFCComp.png")
        originalImg = cv2.imread("/home/oem/PycharmProjects/EzeAuto/Images/HDFC.png")
        ActualImg = cv2.imread("/home/oem/PycharmProjects/EzeAuto/Images/HDFCComp.png")
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

    else:
        print("===============Inside validation==================")
        global expectedAPPValue
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            #print("===========Inside Try============")
            #validation
            difference = cv2.subtract(originalImg, ActualImg)
            b, g, r = cv2.split(difference)
            if originalImg.shape == ActualImg.shape:
                if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                    print("=======Image Comparison========")
                    expectedAPPValue = "Success:Success"
                else:
                    expectedAPPValue = "Success:Fail"
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

        success = setUp.validateValues("", "", "", expectedAPPValue)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()
