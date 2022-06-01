from datetime import datetime
import pytest
from DataProvider.config import TestData
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
import cv2
from DataProvider import GlobalVariables
import allure
from allure_commons.types import AttachmentType
from Utilities.ConfigReader import read_config
from Configuration import Configuration
from Utilities import Validator, ReportProcessor, ConfigReader, APIProcessor


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

        #---------------------------Pre requisite----------------------------------------------
        payload = {
        "username":"9731545096",
        "password":"A123456",
        "entityName":"org",
        "settings":{
            "brandingInfo":"{ }"},
        "settingForOrgCode":"MANASAAUTOMATION"
        }
        response = APIProcessor.post(payload, "orgupdate")
        if response["success"]==True:
            pass
        else:
            msg = "Pre requisite setting failure"
            pytest.fail(msg)
        #----------------------End of Pre requisite--------------------------------------------

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
        try:
            payload = {
                "username": "9731545096",
                "password": "A123456",
                "entityName": "org",
                "settings": {
                    "brandingInfo": "{}"
                },
                "settingForOrgCode": "MANASAAUTOMATION"
            }
            response = APIProcessor.post(payload, "orgupdate")
            if response["success"] == True:
                pass

            else:
                msg = "Pre requisite reset failure"
                pytest.fail(msg)
        except:
            pass

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

        #---------------------------Pre requisite----------------------------------------------
        payload = {
        "username":"9731545096",
        "password":"A123456",
        "entityName":"org",
        "settings":{
            "brandingInfo":"{\"options\": [{\"field\": \"themeName\",\"value\": \"AXIS\"},{\"field\": \"primaryColor\",\"value\": \"#98144D\"},{\"field\": \"secondaryColor\",\"value\": \"#CD1C60\"},{\"field\": \"titlebarColor\",\"value\": \"#98144D\"},{\"field\": \"homeTitlebarColor\",\"value\": \"#98144D\"},{\"field\": \"customBrandColor\",\"value\": \"#98144D\"},{\"field\": \"customStatusBarColor\",\"value\": \"#98144D\"},{\"field\": \"customBrandTextColor\",\"value\": \"#FFFFFF\"},{\"field\": \"primary\",\"value\": \"#98144D\"},{\"field\": \"secondary\",\"value\": \"#CD1C60\"},{\"field\": \"titlebarTheme\",\"value\": \"dark\"},{\"field\": \"titlebarButtonColor\",\"value\": \"#CD1C60\"},{\"field\": \"titlebarButtonTextColor\",\"value\": \"light\"},{\"field\": \"bankIcon\",\"value\": \"axis\"},{\"field\": \"customBrandColor\",\"value\": \"#98144D\"},{\"field\": \"customTextColor\",\"value\": \"light\"},{\"field\": \"detailsButtonColor\",\"value\": \"#CD1C60\"},{\"field\": \"detailsButtonTextColor\",\"value\": \"light\"},{\"field\": \"merchantLogo\",\"value\": \"axis\"},{\"field\": \"customLogo\",\"value\": \"light\"}]}"
        },
        "settingForOrgCode":"AUTOAXIS_905968"
        }
        response = APIProcessor.post(payload, "orgupdate")
        if response["success"]==True:
            pass
        else:
            msg = "Pre requisite setting failure"
            pytest.fail(msg)
        #----------------------End of Pre requisite--------------------------------------------


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
        try:
            payload = {
                "username": "9731545096",
                "password": "A123456",
                "entityName": "org",
                "settings": {
                    "brandingInfo": "{}"
                },
                "settingForOrgCode": "AUTOAXIS_905968"
            }
            response = APIProcessor.post(payload, "orgupdate")
            if response["success"] == True:
                pass

            else:
                msg = "Pre requisite reset failure"
                pytest.fail(msg)
        except:
            pass

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

        #---------------------------Pre requisite----------------------------------------------
        payload = {
        "username":"9731545096",
        "password":"A123456",
        "entityName":"org",
        "settings":{
            "brandingInfo":"{\"options\":[   {\"field\": \"themeName\",\"value\": \"HDFC\"},   {\"field\": \"primaryColor\",\"value\": \"#0D4C8F\"},   {\"field\": \"secondaryColor\",\"value\": \"#ED232A\"},   {\"field\": \"titlebarColor\",\"value\": \"#0D4C8F\"},   {\"field\": \"homeTitlebarColor\",\"value\": \"#0D4C8F\"},   {\"field\": \"customBrandColor\",\"value\": \"#0D4C8F\"},   {\"field\": \"customStatusBarColor\",\"value\": \"#0D4C8F\"},   {\"field\": \"customBrandTextColor\",\"value\": \"#FFFFFF\"},   {\"field\": \"primary\",\"value\": \"#0D4C8F\"},   {\"field\": \"secondary\",\"value\": \"#ED232A\"},   {\"field\": \"titlebarTheme\",\"value\": \"dark\"},   {\"field\": \"titlebarButtonColor\",\"value\":\"#ED232A\"},   {\"field\": \"titlebarButtonTextColor\",\"value\": \"light\"},   {\"field\": \"bankIcon\",\"value\": \"hdfc\"},   {\"field\": \"customBrandColor\",\"value\": \"#0D4C8F\"},   {\"field\": \"customTextColor\",\"value\":\"light\"},   {\"field\": \"detailsButtonColor\",\"value\": \"#ED232A\"},   {\"field\": \"detailsButtonTextColor\",\"value\": \"light\"},   {\"field\": \"merchantLogo\",\"value\": \"hdfc\"},   {\"field\": \"customLogo\",\"value\": \"light\"} ]}"},
        "settingForOrgCode":"AUTOHDFC_9225028"
        }
        response = APIProcessor.post(payload, "orgupdate")
        if response["success"]==True:
            pass
        else:
            msg = "Pre requisite setting failure"
            pytest.fail(msg)
        #----------------------End of Pre requisite--------------------------------------------


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
        try:
            payload = {
                "username": "9731545096",
                "password": "A123456",
                "entityName": "org",
                "settings": {
                    "brandingInfo": "{}"
                },
                "settingForOrgCode": "AUTOHDFC_9225028"
            }
            response = APIProcessor.post(payload, "orgupdate")
            if response["success"] == True:
                pass

            else:
                msg = "Pre requisite reset failure"
                pytest.fail(msg)
        except:
            pass

        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_GUI_APP_Branding_Hdfc_03")