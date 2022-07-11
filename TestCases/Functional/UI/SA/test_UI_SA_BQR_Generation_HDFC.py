import sys
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
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.ConfigReader import read_config
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.appVal
def test_sa_100_102_010():
    """
    :Description: Verification of a BQR QR Generation Success through SA via HDFC
    :Subfeature code: UI_SA_PM_BQR_HDFC_QR_Generation_Success_010
    :TC naming code description: 100->Payment Method
                                102->BQR
                                010-> TC10
    """

    try:
        testcase_id = sys._getframe().f_code.co_name

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True
        #---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)
        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        logger.info(f"Starting execution for the test case : {testcase_id}")

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
            logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
            username = app_cred['Username']
            password = app_cred['Password']
            portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
            logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
            portal_username = portal_cred['Username']
            portal_password = portal_cred['Password']

            query = "select org_code from org_employee where username='" + str(username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            app_driver = GlobalVariables.appDriver
            loginPage = LoginPage(app_driver)
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
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()
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
                ReportProcessor.capture_ss_when_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)
        logger.info(
            f"**********Test case Execution and Validation compeleted for testcase: {testcase_id}**************")
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------


# @pytest.mark.usefixtures("log_on_success", "method_setup")
# @pytest.mark.usefixtures("appium_driver")
# @pytest.mark.appVal
# def test_sa_100_102_011():
#     """
#     :Description: Verification of a BQR QR Generation Success through SA via HDFC
#     :Sub Feature code: UI_SA_PM_BQR_HDFC_QR_Generation_Failed_011
#     :TC naming code description: 100->Payment Method
#                                 102->BQR
#                                 011-> TC11
#     """
#
#     try:
#         testcase_id = sys._getframe().f_code.co_name
#         # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
#         # Write the setup code here
#
#         GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
#         # ---------------------------------------------------------------------------------------------------------
#         # Set the below variables depending on the log capturing need of the test case.
#         Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)
#
#         # Variable which tracks if the execution is going on through all the lines of code of test case.
#         # Set to failure where ever there are chances of failure.
#         msg = ""
#         logger.info(f"Starting execution for the test case : {testcase_id}")
#
#         # -----------------------------------------Start of Test Execution-------------------------------------
#         try:
#             # ------------------------------------------------------------------------------------------------
#             #
#             app_driver = GlobalVariables.appDriver
#             loginPage = LoginPage(app_driver)
#             username = read_config("credentials", 'username_HDFC')
#             password = read_config("credentials", 'password')
#             org_code = read_config("testdata", "org_code_hdfc")
#             logger.info(f"Logging in the MPOSX application using username : {username}")
#             loginPage.perform_login(username, password)
#             homePage = HomePage(app_driver)
#             homePage.check_home_page_logo()
#             logger.info(f"App homepage loaded successfully")
#             amount = random.randint(101, 200)
#             order_id = datetime.now().strftime('%m%d%H%M%S')
#             print("Order id", order_id)
#             homePage.enter_amount_and_order_number(amount, order_id)
#             logger.debug(f"Entered amount is : {amount}")
#             logger.debug(f"Entered order_id is : {order_id}")
#             paymentPage = PaymentPage(app_driver)
#             paymentPage.is_payment_page_displayed(amount, order_id)
#             paymentPage.click_on_Bqr_paymentMode()
#             #
#             # ------------------------------------------------------------------------------------------------
#             GlobalVariables.EXCEL_TC_Execution = "Pass"
#             ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
#         except Exception as e:
#             ReportProcessor.capture_ss_when_exe_failed()
#             GlobalVariables.EXCEL_TC_Execution = "Fail"
#             GlobalVariables.Incomplete_ExecutionCount += 1
#             ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
#             pytest.fail("Test case execution failed due to the exception -" + str(e))
#         # -----------------------------------------End of Test Execution--------------------------------------
#
#         # -----------------------------------------Start of Validation----------------------------------------
#         current = datetime.now()
#         GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
#
#         # -----------------------------------------Start of App Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "app_validation")) == "True":
#             try:
#                 # --------------------------------------------------------------------------------------------
#                 expectedAppValues = {"Payment Screen text": "Scan QR code using"}
#
#                 text = paymentPage.validate_upi_bqr_payment_screen()
#
#                 actualAppValues = {"Payment Screen text": text}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_exe_failed()
#                 print("App Validation failed due to exception - " + str(e))
#                 msg = msg + "App Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_app_val_result = "Fail"
#
#         # -----------------------------------------End of App Validation---------------------------------------
#
#
#     # -------------------------------------------End of Validation---------------------------------------------
#
#     finally:
#         Configuration.executeFinallyBlock(testcase_id)
#         logger.info(
#             f"**********Test case Execution and Validation compeleted for testcase: {testcase_id}**************")
#         if not GlobalVariables.setupCompletedSuccessfully:
#             print("Test case setup itself failed. So the test case was not executed.")
#             logger.error("Test case setup itself failed. So the test case was not executed.")
#         else:
#             ReportProcessor.updateTestCaseResult(msg)  # pass msg
#         # -------------------------------Revert Preconditions done(setup)--------------------------------------------
#
#         # Write the code here to revert the settings that were done as precondition
#
#         # ----------------------------------------------------------------------------------------------------------
#

