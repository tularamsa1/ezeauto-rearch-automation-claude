from datetime import datetime
import pytest
import Utilities.ReportProcessor
import Utilities.Validator
from DataProvider.config import TestData
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
import cv2
from DataProvider import GlobalVariables
import allure
from allure_commons.types import AttachmentType
from Utilities.ConfigReader import read_config
from Configuration import Configuration
from Utilities import Validator, ReportProcessor, ConfigReader


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

        success = Utilities.Validator.validateValues("", "", "", expectedAPPValue)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()




@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.appVal
def test_GUI_APP_Branding_Ezetap_01(): #Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
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
                expectedAppValues = {"Result": "Success"}
                #
                difference = cv2.subtract(originalImg, ActualImg)
                # difference = abs(originalImg-ActualImg)
                b, g, r = cv2.split(difference)
                if originalImg.shape == ActualImg.shape:
                    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                        print("=======Image Comparison========")
                        actualAppValues = {"Result": "Success"}
                    else:
                        actualAppValues = {"Result": "Fail"}
                #

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_GUI_APP_Branding_Ezetap_01")



@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.appVal
def test_GUI_APP_Branding_Axis_02(): #Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
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
                expectedAppValues = {"Result": "Success"}
                #
                difference = cv2.subtract(originalImg, ActualImg)
                # difference = abs(originalImg-ActualImg)
                b, g, r = cv2.split(difference)
                if originalImg.shape == ActualImg.shape:
                    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                        print("=======Image Comparison========")
                        actualAppValues = {"Result": "Success"}
                    else:
                        actualAppValues = {"Result": "Fail"}
                #

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_GUI_APP_Branding_Axis_02")





@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.appVal
def test_GUI_APP_Branding_Hdfc_03(): #Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
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
            ActualImg = cv2.imread("/home/oem/PycharmProjects/EzeAuto/Images/HDFCComp.png")            #
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
                expectedAppValues = {"Result": "Success"}
                #
                difference = cv2.subtract(originalImg, ActualImg)
                # difference = abs(originalImg-ActualImg)
                b, g, r = cv2.split(difference)
                if originalImg.shape == ActualImg.shape:
                    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                        print("=======Image Comparison========")
                        actualAppValues = {"Result": "Success"}
                    else:
                        actualAppValues = {"Result": "Fail"}
                #

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_GUI_APP_Branding_Hdfc_03")