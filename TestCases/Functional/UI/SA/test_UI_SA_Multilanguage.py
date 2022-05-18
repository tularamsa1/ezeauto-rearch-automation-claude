import pytest
from DataProvider import GlobalVariables
from PageFactory.App_AccountPage import AccountPage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from datetime import datetime
from Utilities.APIPost import post
from Utilities.ConfigReader import read_config
from Configuration import Configuration
from Utilities import Validator, ReportProcessor, ConfigReader


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.apiVal
@pytest.mark.appVal
def test_UI_SA_Multilanguage_English_01(): #Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        global bool_val_exe
        bool_val_exe = True
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
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
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Amount Field": "Enter Amount", "Summary Field": "Summary", "Lang": 'English'}
                #
                actualAppValues = {"Amount Field": str(Hometext), "Summary Field": str(HistoryText), "Lang": str(LangText)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Lang": "English"}
                #
                login_payload = {'username': ConfigReader.read_config("credentials", "username_EngLang"),
                                 'password': ConfigReader.read_config("credentials", "password")}
                list = post(login_payload, ConfigReader.read_config("credentials", "loginurl"))
                result = list['setting']['userAppOptions']['preferences']['language']['value']
                #
                actualAPIValues = {"Lang": str(result)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of API Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_SA_Multilanguage_English_01")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.apiVal
@pytest.mark.appVal
def test_UI_SA_Multilanguage_Hindi_02(): #Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        global bool_val_exe
        bool_val_exe = True
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
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
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Amount Field": "राशि दर्ज करें", "Summary Field": "सारांश", "Lang": "हिंदी"}
                actualAppValues = {"Amount Field": str(Hometext), "Summary Field": str(HistoryText), "Lang": str(LangText)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Lang": "Hindi"}
                #
                login_payload = {'username': ConfigReader.read_config("credentials", "username_HindiLang"),
                                 'password': ConfigReader.read_config("credentials", "password")}
                list = post(login_payload, ConfigReader.read_config("credentials", "loginurl"))
                result = list['setting']['userAppOptions']['preferences']['language']['value']
                #
                actualAPIValues = {"Lang": str(result)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of API Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_SA_Multilanguage_Hindi_02")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.apiVal
@pytest.mark.appVal
def test_UI_SA_Multilanguage_English_to_Hindi_03(): #Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        global bool_val_exe
        bool_val_exe = True
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
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
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Lang": 'हिंदी'}

                actualAppValues = {"Lang": str(LangText)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Lang": "Hindi"}
                #
                login_payload = {'username': ConfigReader.read_config("credentials", "username_EngLang"),
                                 'password': ConfigReader.read_config("credentials", "password")}
                list = post(login_payload, ConfigReader.read_config("credentials", "loginurl"))
                result = list['setting']['userAppOptions']['preferences']['language']['value']
                #
                actualAPIValues = {"Lang": str(result)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of API Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_SA_Multilanguage_English_to_Hindi_03")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.apiVal
@pytest.mark.appVal
def test_UI_SA_Multilanguage_Hindi_to_English_04():  # Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        global bool_val_exe
        bool_val_exe = True
        msg = ""

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
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
            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Lang": "English"}

                actualAppValues = {"Lang": str(LangText)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Lang": "English"}
                #
                login_payload = {'username': ConfigReader.read_config("credentials", "username_EngLang"),
                                 'password': ConfigReader.read_config("credentials", "password")}
                list = post(login_payload, ConfigReader.read_config("credentials", "loginurl"))
                result = list['setting']['userAppOptions']['preferences']['language']['value']
                #
                actualAPIValues = {"Lang": str(result)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of API Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_SA_Multilanguage_English_to_Hindi_03")


#Below test case works for only new user
@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.apiVal
@pytest.mark.appVal
def test_UI_SA_Multilanguage_Lang_selection_05():  # Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        global bool_val_exe
        bool_val_exe = True
        msg = ""

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
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
            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Lang": "English"}

                actualAppValues = {"Lang": str(LangText)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Lang": "English"}
                #
                login_payload = {'username': ConfigReader.read_config("credentials", "username_EngLang"),
                                 'password': ConfigReader.read_config("credentials", "password")}
                list = post(login_payload, ConfigReader.read_config("credentials", "loginurl"))
                result = list['setting']['userAppOptions']['preferences']['language']['value']
                #
                actualAPIValues = {"Lang": str(result)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                bool_val_exe = False

        # -----------------------------------------End of API Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_SA_Multilanguage_Lang_selection_05")



