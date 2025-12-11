import sys
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.LMS.app_home_page import HomePage
from Utilities import ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_001():
    """
    Sub Feature Code: UI_LMS_Login_Incorrect_Username_Validation
    Sub Feature Description: Verify that login fails when incorrect username is provided
                            and appropriate error message is displayed to the user
    TC naming code description: 100: Payment Method, 1010: LMS, 001: TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -----------------------------PreConditions--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get app credentials (valid ones for reference)
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        valid_password = app_cred['Password']

        # Define incorrect username and expected values
        incorrect_username = "invalid_user_12345"
        expected_error_title = "Incorrect Username or Password"
        expected_error_message = "Please enter the correct \nUsername & password"

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------

        # -----------------------------------------Start of Test Execution----------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Initialize app driver with reset to ensure we start from login page
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id, no_reset=False)
            login_page = LoginPage(driver=app_driver)
            logger.info("Login page initialized")

            # Step 1: Enter incorrect username with valid password
            logger.info(f"Attempting login with incorrect username: {incorrect_username}")
            login_page.perform_login_for_auto_login_functionality(incorrect_username, valid_password, Pax_Device=True)
            logger.info("Clicked login button with incorrect username")

            # Step 2: Verify error popup is displayed
            assert login_page.is_error_layout_displayed(), "Error layout should be displayed for incorrect username"
            logger.info("Verified: Error layout is displayed")

            # Step 3: Fetch and verify error title and message
            error_title = login_page.fetch_error_title()
            error_message = login_page.fetch_error_message()
            logger.info(f"Error title: '{error_title}'")
            logger.info(f"Error message: '{error_message}'")

            assert error_title == expected_error_title, f"Error title should be '{expected_error_title}', but got: '{error_title}'"
            logger.info(f"Verified: Error title is '{error_title}'")

            assert error_message == expected_error_message, f"Error message should be '{expected_error_message}', but got: '{error_message}'"
            logger.info(f"Verified: Error message is '{error_message}'")

            # Step 4: Close the error popup
            login_page.close_error_popup()
            logger.info("Closed error popup")

            # Step 5: Verify user remains on login page
            login_page.validate_login_page()
            logger.info("Verified: User remains on login page after incorrect username")

            logger.info(f"Test case {testcase_id} completed successfully - Incorrect username login test passed")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_002():
    """
    Sub Feature Code: UI_LMS_Login_Incorrect_Password_Validation
    Sub Feature Description: Verify that login fails when incorrect password is provided
                            and appropriate error message is displayed to the user
    TC naming code description: 100: Payment Method, 1010: LMS, 002: TC002
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -----------------------------PreConditions--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get app credentials (valid ones for reference)
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        valid_username = app_cred['Username']

        # Define incorrect password and expected values
        incorrect_password = "WrongPassword123!"
        expected_error_title = "Incorrect Username or Password"
        expected_error_message = "Please enter the correct \nUsername & password"

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------

        # -----------------------------------------Start of Test Execution----------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Initialize app driver with reset to ensure we start from login page
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id, no_reset=False)
            login_page = LoginPage(driver=app_driver)
            logger.info("Login page initialized")

            # Step 1: Enter valid username with incorrect password
            logger.info(f"Attempting login with valid username: {valid_username} and incorrect password")
            login_page.perform_login_for_auto_login_functionality(valid_username, incorrect_password, Pax_Device=True)
            logger.info("Clicked login button with incorrect password")

            # Step 2: Verify error popup is displayed
            assert login_page.is_error_layout_displayed(), "Error layout should be displayed for incorrect password"
            logger.info("Verified: Error layout is displayed")

            # Step 3: Fetch and verify error title and message
            error_title = login_page.fetch_error_title()
            error_message = login_page.fetch_error_message()
            logger.info(f"Error title: '{error_title}'")
            logger.info(f"Error message: '{error_message}'")

            assert error_title == expected_error_title, f"Error title should be '{expected_error_title}', but got: '{error_title}'"
            logger.info(f"Verified: Error title is '{error_title}'")

            assert error_message == expected_error_message, f"Error message should be '{expected_error_message}', but got: '{error_message}'"
            logger.info(f"Verified: Error message is '{error_message}'")

            # Step 4: Close the error popup
            login_page.close_error_popup()
            logger.info("Closed error popup")

            # Step 5: Verify user remains on login page
            login_page.validate_login_page()
            logger.info("Verified: User remains on login page after incorrect password")

            logger.info(f"Test case {testcase_id} completed successfully - Incorrect password login test passed")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_003():
    """
    Sub Feature Code: UI_LMS_Login_Successful_Login_With_Valid_Credentials
    Sub Feature Description: Verify that login succeeds when correct username and password
                            are provided and user is redirected to home page
    TC naming code description: 100: Payment Method, 1010: LMS, 003: TC003
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
        valid_username = app_cred['Username']
        valid_password = app_cred['Password']

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------

        # -----------------------------------------Start of Test Execution----------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Initialize app driver with reset to ensure we start from login page
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id, no_reset=False)
            login_page = LoginPage(driver=app_driver)
            home_page = HomePage(driver=app_driver)
            logger.info("Login page initialized")

            # Step 1: Enter valid username with valid password
            logger.info(f"Attempting login with valid username: {valid_username} and valid password")
            login_page.perform_login_for_auto_login_functionality(valid_username, valid_password, Pax_Device=True)
            logger.info("Clicked login button with valid credentials")

            # Step 2: Verify user is redirected to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: User is redirected to home page after successful login")

            # Additional validation - verify username on home page
            displayed_username = home_page.fetch_username()
            assert displayed_username == valid_username, f"Username should be '{valid_username}', but got: '{displayed_username}'"
            logger.info(f"Verified: Username on home page is '{displayed_username}'")

            logger.info(f"Test case {testcase_id} completed successfully - Correct credentials login test passed")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
