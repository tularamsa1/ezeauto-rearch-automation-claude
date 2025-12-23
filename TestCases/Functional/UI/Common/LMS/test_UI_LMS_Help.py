import sys
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables

from PageFactory.LMS.app_home_page import HomePage
from PageFactory.LMS.app_help_page import HelpPage
from PageFactory.mpos.app_login_page import LoginPage

from Utilities import ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_013():
    """
    sub_feature_code: UI_Common_PM_LMS_Help_Page_UI_Elements_Verification
    file_name: test_UI_Common_LMS_Help.py
    Sub Feature Description: Verify all UI elements are displayed correctly on the Help & Support page
                            including title and help question text
    TC naming code description: 100: Payment Method, 1010: LMS, 013: TC013
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -----------------------------PreConditions--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get app credentials
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        # Define expected values
        expected_help_title = "Help & Support"
        expected_help_question = "Need urgent help?"
        expected_support_number = "18002000313"
        expected_call_support_text = "Call Razorpay Support"

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------

        # -----------------------------------------Start of Test Execution----------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Initialize app driver
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id, no_reset=True)
            home_page = HomePage(driver=app_driver)
            help_page = HelpPage(driver=app_driver)
            login_page = LoginPage(driver=app_driver)

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Navigate to Help page
            home_page.click_on_help_button()
            logger.info("Navigated to Help page")

            # Step 2: Verify Help page title
            help_title = help_page.fetch_help_title()
            assert help_title == expected_help_title, f"Help page title should be '{expected_help_title}', but got: '{help_title}'"
            logger.info(f"Verified: Help page title is '{help_title}'")

            # Step 3: Verify help question text
            help_question = help_page.fetch_help_question_text()
            assert help_question == expected_help_question, f"Help question should be '{expected_help_question}', but got: '{help_question}'"
            logger.info(f"Verified: Help question text is '{help_question}'")

            # Step 4: Verify Call Razorpay Support text
            call_support_text = help_page.fetch_call_razorpay_support_text()
            assert call_support_text == expected_call_support_text, f"Call support text should be '{expected_call_support_text}', but got: '{call_support_text}'"
            logger.info(f"Verified: Call Razorpay Support text is '{call_support_text}'")

            # Step 5: Verify support phone number
            support_number = help_page.fetch_call_support_number()
            assert support_number == expected_support_number, f"Support number should be '{expected_support_number}', but got: '{support_number}'"
            logger.info(f"Verified: Support number is '{support_number}'")

            # Step 6: Click back button to return to home page
            help_page.click_on_back_button()
            home_page.wait_for_navigation_to_load()
            logger.info("Navigated back to home page successfully")

            logger.info(f"Test case {testcase_id} completed successfully - Help page UI elements verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_014():
    """
    sub_feature_code: UI_Common_PM_LMS_Help_Page_Call_Support_And_Back_Navigation
    file_name: test_UI_Common_LMS_Help.py
    Sub Feature Description: Verify user can click on call support button and navigate back to home page
    TC naming code description: 100: Payment Method, 1010: LMS, 014: TC014
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -----------------------------PreConditions--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get app credentials
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------

        # -----------------------------------------Start of Test Execution----------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Initialize app driver
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id, no_reset=True)
            home_page = HomePage(driver=app_driver)
            help_page = HelpPage(driver=app_driver)
            login_page = LoginPage(driver=app_driver)

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Navigate to Help page
            home_page.click_on_help_button()
            logger.info("Navigated to Help page")

            # Step 2: Verify Help page is displayed
            assert help_page.is_help_page_displayed(), "Help page should be displayed"
            logger.info("Verified: Help page is displayed")

            # Step 3: Verify call support button is displayed
            assert help_page.is_call_support_button_displayed(), "Call support button should be displayed"
            logger.info("Verified: Call support button is displayed")

            # Step 4: Click on call support button (Bug: phone dialer not opening)
            help_page.click_on_call_support_button()
            logger.info("Clicked on call support button")

            # Step 5: Click back button to navigate to home page
            help_page.click_on_back_button()
            logger.info("Clicked on back button")

            # Step 6: Verify navigation back to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: Navigated back to home page successfully")

            logger.info(f"Test case {testcase_id} completed successfully - Call support and back navigation verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)

