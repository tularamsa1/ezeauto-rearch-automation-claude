import sys
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables

from PageFactory.LMS.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage

from Utilities import ResourceAssigner, DBProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_004():
    """
    Sub Feature Code: UI_LMS_Home_Page_UI_Elements_Verification
    Sub Feature Description: Verify all UI elements are displayed correctly on the LMS home page
                            including merchant name, username, labels, images and buttons
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
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        # Get org_code from database
        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        # Fetch expected merchant name from terminal_details table using org_code
        expected_merchant_name = ResourceAssigner.getMerchantNameByOrgCode(org_code)
        logger.info(f"Expected merchant name from terminal_details: {expected_merchant_name}")

        # Define expected values
        expected_username_label = "User:"
        expected_additional_guest_text = "Add Guests To Check-in"

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

            # Step 1: Verify merchant name matches expected value from DB
            merchant_name = home_page.fetch_merchant_name()
            logger.info(f"Actual merchant name from app: '{merchant_name}'")
            assert merchant_name == expected_merchant_name, f"Merchant name should be '{expected_merchant_name}', but got: '{merchant_name}'"
            logger.info(f"Verified: Merchant name is '{merchant_name}'")

            # Step 2: Verify username label
            username_label = home_page.fetch_username_label()
            assert username_label == expected_username_label, f"Username label should be '{expected_username_label}', but got: '{username_label}'"
            logger.info(f"Verified: Username label is '{username_label}'")

            # Step 3: Verify username matches the logged in user
            displayed_username = home_page.fetch_username()
            logger.info(f"Actual username from app: '{displayed_username}'")
            assert displayed_username == app_username, f"Username should be '{app_username}', but got: '{displayed_username}'"
            logger.info(f"Verified: Username is '{displayed_username}'")

            # Step 4: Verify additional guest text
            additional_guest_text = home_page.fetch_additional_guest()
            assert additional_guest_text == expected_additional_guest_text, f"Additional guest text should be '{expected_additional_guest_text}', but got: '{additional_guest_text}'"
            logger.info(f"Verified: Additional guest text is '{additional_guest_text}'")

            # Step 5: Verify Razorpay Payments image is displayed
            is_razorpay_displayed = home_page.is_razorpay_image_displayed()
            logger.info(f"Razorpay image displayed: {is_razorpay_displayed}")
            assert is_razorpay_displayed, "Razorpay Payments image should be displayed on the home page"
            logger.info("Verified: Razorpay Payments image is displayed")

            # Step 6: Verify proceed button text
            proceed_button_text = home_page.fetch_proceed_button_text()
            logger.info(f"Proceed button text: '{proceed_button_text}'")
            assert proceed_button_text is not None and proceed_button_text != "", f"Proceed button text should not be empty, but got: '{proceed_button_text}'"
            logger.info(f"Verified: Proceed button text is '{proceed_button_text}'")

            logger.info(f"Test case {testcase_id} completed successfully - All UI elements verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_005():
    """
    Sub Feature Code: UI_LMS_Home_Page_Guest_Counter_Functionality
    Sub Feature Description: Verify the guest counter increment/decrement functionality and chair image count
                            on the LMS home page with boundary validations (min: 1, max: 10)
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
            login_page = LoginPage(driver=app_driver)

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username : {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Verify decrement button is NOT clickable initially
            is_decrement_clickable = home_page.is_guest_button_clickable('decrement')
            assert not is_decrement_clickable, "Decrement button should NOT be clickable when guest count is 1"
            logger.info("Verified: Decrement button is not clickable initially")

            # Step 2: Verify initial guest number is 1
            initial_guest_number = int(home_page.fetch_guest_number())
            assert initial_guest_number == 1, f"Initial guest number should be 1, but got {initial_guest_number}"
            logger.info(f"Verified: Initial guest number is {initial_guest_number}")

            # Step 3: Verify chair image count matches initial guest number
            initial_chair_count = home_page.get_chair_image_count()
            assert initial_chair_count == initial_guest_number, f"Chair image count should be {initial_guest_number}, but got {initial_chair_count}"
            logger.info(f"Verified: Chair image count is {initial_chair_count} (matches guest number)")

            # Step 4: Verify increment button is clickable initially
            is_increment_clickable = home_page.is_guest_button_clickable('increment')
            assert is_increment_clickable, "Increment button should be clickable initially"
            logger.info("Verified: Increment button is clickable initially")

            # Step 5: Click increment button 9 times (from 1 to 10) and verify each time
            for i in range(9):
                expected_guest_number = initial_guest_number + i + 1
                home_page.click_on_btnIncrement()
                current_guest_number = int(home_page.fetch_guest_number())
                assert current_guest_number == expected_guest_number, f"Guest number should be {expected_guest_number}, but got {current_guest_number}"

                chair_count = home_page.get_chair_image_count()
                assert chair_count == current_guest_number, f"Chair image count should be {current_guest_number}, but got {chair_count}"
                logger.info(f"Clicked increment {i + 1} time(s). Guest: {current_guest_number}, Chairs: {chair_count}")

            # Step 6: Verify guest number is now 10
            final_guest_number = int(home_page.fetch_guest_number())
            assert final_guest_number == 10, f"Final guest number should be 10, but got {final_guest_number}"
            logger.info(f"Verified: Guest number reached maximum value of {final_guest_number}")

            # Step 7: Verify increment button is NOT clickable after reaching 10
            is_increment_clickable_after_max = home_page.is_guest_button_clickable('increment')
            assert not is_increment_clickable_after_max, "Increment button should NOT be clickable after reaching 10"
            logger.info("Verified: Increment button is not clickable after reaching maximum guest count")

            # Step 8: Verify decrement button is now clickable
            is_decrement_clickable_at_max = home_page.is_guest_button_clickable('decrement')
            assert is_decrement_clickable_at_max, "Decrement button should be clickable when guest count is 10"
            logger.info("Verified: Decrement button is clickable at maximum guest count")

            # Step 9: Click decrement button 9 times (from 10 to 1) and verify each time
            for i in range(9):
                expected_guest_number = 10 - i - 1
                home_page.click_on_btnDecrement()
                current_guest_number = int(home_page.fetch_guest_number())
                assert current_guest_number == expected_guest_number, f"Guest number should be {expected_guest_number}, but got {current_guest_number}"

                chair_count = home_page.get_chair_image_count()
                assert chair_count == current_guest_number, f"Chair image count should be {current_guest_number}, but got {chair_count}"
                logger.info(f"Clicked decrement {i + 1} time(s). Guest: {current_guest_number}, Chairs: {chair_count}")

            # Step 10: Verify guest number is back to 1
            final_guest_number_after_decrement = int(home_page.fetch_guest_number())
            assert final_guest_number_after_decrement == 1, f"Guest number should be 1 after decrementing, but got {final_guest_number_after_decrement}"
            logger.info(f"Verified: Guest number is back to {final_guest_number_after_decrement}")

            # Step 11: Verify chair image count is back to 1
            final_chair_count = home_page.get_chair_image_count()
            assert final_chair_count == 1, f"Chair image count should be 1 after decrementing, but got {final_chair_count}"
            logger.info(f"Verified: Chair image count is back to {final_chair_count}")

            # Step 12: Verify decrement button is NOT clickable after reaching 1
            is_decrement_clickable_at_min = home_page.is_guest_button_clickable('decrement')
            assert not is_decrement_clickable_at_min, "Decrement button should NOT be clickable when guest count is 1"
            logger.info("Verified: Decrement button is not clickable at minimum guest count")

            logger.info(f"Test case {testcase_id} completed successfully - Guest counter functionality verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_006():
    """
    Sub Feature Code: UI_LMS_Home_Page_Help_Button_Verification
    Sub Feature Description: Verify the Help button is displayed and clickable on the LMS home page
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
            login_page = LoginPage(driver=app_driver)

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username : {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Click on Help button
            home_page.click_on_help_button()
            logger.info("Clicked on Help button successfully")

            logger.info(f"Test case {testcase_id} completed successfully - Help button verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
