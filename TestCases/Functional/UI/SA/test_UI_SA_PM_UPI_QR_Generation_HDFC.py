import random
import sys
from datetime import datetime

import pytest

from Configuration import Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver")
@pytest.mark.appVal
def test_sa_100_101_024():
    """
    Description: Verification of a UPI QR Generation Success through SA via HDFC
    Subfeature code: UI_SA_PM_UPI_HDFC_QR_Generation_Success
    TC naming code description:
    100->Payment Method
    101->UPI
    024->TC24
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        logger.info("Performing preconditions before starting test case execution")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        logger.info("Finished performing preconditions before starting test case execution")

        GlobalVariables.setupCompletedSuccessfully = True
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)
        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            query = "select org_code from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            app_driver = GlobalVariables.appDriver
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(301, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expected_app_values = {"Payment Screen text": "Scan QR code using"}

                text = payment_page.validate_upi_bqr_payment_screen()

                actual_app_values = {"Payment Screen text": text}
                app_driver.reset()
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

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
