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
    sub_feature_code: UI_Common_PM_LMS_Login_Incorrect_Username_Validation
    file_name: test_UI_Common_LMS_Login.py
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
    sub_feature_code: UI_Common_PM_LMS_Login_Incorrect_Password_Validation
    file_name: test_UI_Common_LMS_Login.py
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
    sub_feature_code: UI_Common_PM_LMS_Login_Successful_Login_With_Valid_Credentials
    file_name: test_UI_Common_LMS_Login.py
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_004():
    """
    sub_feature_code: UI_Common_PM_LMS_Login_Button_Disabled_Until_Credentials_Filled
    file_name: test_UI_Common_LMS_Login.py
    Sub Feature Description: Verify that login button is disabled until both username
                            and password fields are filled
    TC naming code description: 100: Payment Method, 1010: LMS, 004: TC004
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
        test_username = app_cred['Username']
        test_password = app_cred['Password']

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

            # Select environment first
            login_page.select_environment()
            logger.info("Environment selected")

            # Step 1: Verify login button is disabled when both fields are empty
            is_enabled_empty = login_page.is_login_button_enabled()
            assert not is_enabled_empty, "Login button should be disabled when both username and password are empty"
            logger.info("Verified: Login button is disabled when both fields are empty")

            # Step 2: Enter only username and verify login button is still disabled
            login_page.wait_for_element(login_page.txt_username).clear()
            login_page.perform_sendkeys(login_page.txt_username, test_username)
            is_enabled_username_only = login_page.is_login_button_enabled()
            assert not is_enabled_username_only, "Login button should be disabled when only username is filled"
            logger.info("Verified: Login button is disabled when only username is filled")

            # Step 3: Clear username, enter only password and verify login button is still disabled
            login_page.wait_for_element(login_page.txt_username).clear()
            login_page.wait_for_element(login_page.txt_password).clear()
            login_page.perform_sendkeys(login_page.txt_password, test_password)
            is_enabled_password_only = login_page.is_login_button_enabled()
            assert not is_enabled_password_only, "Login button should be disabled when only password is filled"
            logger.info("Verified: Login button is disabled when only password is filled")

            # Step 4: Enter both username and password and verify login button is enabled
            login_page.perform_sendkeys(login_page.txt_username, test_username)
            is_enabled_both = login_page.is_login_button_enabled()
            assert is_enabled_both, "Login button should be enabled when both username and password are filled"
            logger.info("Verified: Login button is enabled when both username and password are filled")

            logger.info(f"Test case {testcase_id} completed successfully - Login button state validation passed")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_005():
    """
    sub_feature_code: UI_Common_PM_LMS_Login_Show_Password_Button_Validation
    file_name: test_UI_Common_LMS_Login.py
    Sub Feature Description: Verify that show password button is displayed and functional
                            to toggle password visibility
    TC naming code description: 100: Payment Method, 1010: LMS, 005: TC005
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
        test_password = app_cred['Password']

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

            # Select environment first
            login_page.select_environment()
            logger.info("Environment selected")

            # Step 1: Enter password in the password field
            login_page.wait_for_element(login_page.txt_password).clear()
            login_page.perform_sendkeys(login_page.txt_password, test_password)
            logger.info("Password entered in the password field")

            # Step 2: Click on show password button to show password
            login_page.click_show_password_button()
            logger.info("Clicked on show password button")

            # Step 3: Verify password is visible (text should match entered password)
            visible_password = login_page.get_password_field_text()
            assert visible_password == test_password, f"Password should be visible as '{test_password}', but got: '{visible_password}'"
            logger.info("Verified: Password is now visible")

            # Step 4: Click on show password button again to hide password
            login_page.click_show_password_button()
            logger.info("Clicked on show password button again to hide password")

            logger.info(f"Test case {testcase_id} completed successfully - Show password button validation passed")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_006():
    """
    sub_feature_code: UI_Common_PM_LMS_Login_Page_UI_Elements_Verification
    file_name: test_UI_Common_LMS_Login.py
    Sub Feature Description: Verify all UI elements are displayed correctly on the login page
                            including logo, labels, support info and WhatsApp icon
    TC naming code description: 100: Payment Method, 1010: LMS, 006: TC006
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

        # Define expected values
        expected_login_hint = "Log in"
        expected_login_issue = "Having issue with login?"
        expected_missed_call = "Give missed call on this number"
        expected_support_number = "+91 806 177 0858"

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

            # Select environment first
            login_page.select_environment()
            logger.info("Environment selected")

            # Step 1: Verify logo is displayed
            assert login_page.is_logo_displayed(), "Logo should be displayed on login page"
            logger.info("Verified: Logo is displayed")

            # Step 2: Verify login hint text
            login_hint = login_page.fetch_login_hint_text()
            assert login_hint == expected_login_hint, f"Login hint should be '{expected_login_hint}', but got: '{login_hint}'"
            logger.info(f"Verified: Login hint text is '{login_hint}'")

            # Step 3: Verify login issue text
            login_issue = login_page.fetch_login_issue_text()
            assert login_issue == expected_login_issue, f"Login issue text should be '{expected_login_issue}', but got: '{login_issue}'"
            logger.info(f"Verified: Login issue text is '{login_issue}'")

            # Step 4: Verify missed call text
            missed_call = login_page.fetch_missed_call_text()
            assert missed_call == expected_missed_call, f"Missed call text should be '{expected_missed_call}', but got: '{missed_call}'"
            logger.info(f"Verified: Missed call text is '{missed_call}'")

            # Step 5: Verify support contact number
            support_number = login_page.fetch_support_contact_number()
            assert support_number == expected_support_number, f"Support number should be '{expected_support_number}', but got: '{support_number}'"
            logger.info(f"Verified: Support contact number is '{support_number}'")

            # Step 6: Verify WhatsApp icon is displayed
            assert login_page.is_whatsapp_icon_displayed(), "WhatsApp icon should be displayed on login page"
            logger.info("Verified: WhatsApp icon is displayed")

            logger.info(f"Test case {testcase_id} completed successfully - Login page UI elements verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
