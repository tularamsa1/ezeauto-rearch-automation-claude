from datetime import datetime
from time import sleep

import pytest
import random
from Configuration import Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor
from Utilities.ConfigReader import read_config
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver") #This is an optional line. Keep only whichever app_driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.appVal
def test_sa_100_102_010(): #Make sure to add the test case name as same as the sub feature code.
    """
    :Description: Verification of a BQR QR Generation Success through SA via HDFC
    :Subfeature code: UI_SA_PM_BQR_HDFC_QR_Generation_010
    :TC naming code description: 100->Payment Method
                                102->BQR
                                010-> TC10
    """

    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        logger.info("Starting execution for the test case : test_common_100_102_010")

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            app_driver = GlobalVariables.appDriver
            loginPage = LoginPage(app_driver)
            username = read_config("credentials", 'username_HDFC')
            password = read_config("credentials", 'password')
            org_code = read_config("testdata", "org_code_hdfc")
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(301, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            homePage.enter_amount_and_order_number(amount, order_id)
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()

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
                expectedAppValues = {"Payment Screen text": "Scan QR code using"}

                text = paymentPage.validate_upi_bqr_payment_screen()

                actualAppValues = {"Payment Screen text": text}
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
        logger.info("Completed execution and validation for the test case : test_common_100_102_010")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_sa_100_102_010")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver")  # This is an optional line. Keep only whichever app_driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.appVal
def test_sa_100_102_011():  # Make sure to add the test case name as same as the sub feature code.
    """
    :Description: Verification of a BQR QR Generation Success through SA via HDFC
    :Sub Feature code: UI_SA_PM_BQR_HDFC_QR_Generation_Failed_011
    :TC naming code description: 100->Payment Method
                                102->BQR
                                011-> TC11
    """

    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        logger.info("Starting execution for the test case : test_common_100_102_011")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            app_driver = GlobalVariables.appDriver
            loginPage = LoginPage(app_driver)
            username = read_config("credentials", 'username_HDFC')
            password = read_config("credentials", 'password')
            org_code = read_config("testdata", "org_code_hdfc")
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(101, 200)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.check_payment_page(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
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
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Screen text": "Scan QR code using"}

                text = paymentPage.validate_upi_bqr_payment_screen()

                actualAppValues = {"Payment Screen text": text}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        logger.info("Compelted execution and validation for the test case : test_common_100_102_011")
        Configuration.executeFinallyBlock("test_sa_100_102_011")

