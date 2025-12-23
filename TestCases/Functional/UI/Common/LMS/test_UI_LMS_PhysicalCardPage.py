import sys
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables

from PageFactory.LMS.app_home_page import HomePage
from PageFactory.LMS.app_physical_card_page import PhysicalCardPage
from PageFactory.mpos.app_login_page import LoginPage

from Utilities import ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_011():
    """
    sub_feature_code: UI_Common_PM_LMS_Physical_Card_Page_UI_Elements_And_Exit_Dialog
    file_name: test_UI_Common_LMS_PhysicalCardPage.py
    Sub Feature Description: Verify physical card page UI elements and exit dialog functionality
                            with NO and YES buttons
    TC naming code description: 100: Payment Method, 1010: LMS, 011: TC011
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
        expected_order_value = "CARD"
        expected_status_details = "Swipe or Insert or Tap"
        expected_dialog_title = "Exit"
        expected_dialog_text = "Are you sure you want to abort?"
        expected_no_button = "NO"
        expected_yes_button = "YES"

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
            physical_card_page = PhysicalCardPage(driver=app_driver)
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

            # Step 1: Click on Proceed button
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            # Step 2: Verify physical card page logo is displayed
            assert physical_card_page.is_logo_displayed(), "Logo should be displayed on physical card page"
            logger.info("Verified: Logo is displayed on physical card page")

            # Step 3: Verify order ID value
            order_value = physical_card_page.fetch_order_id_value()
            assert order_value == expected_order_value, f"Order value should be '{expected_order_value}', but got: '{order_value}'"
            logger.info(f"Verified: Order value is '{order_value}'")

            # Step 4: Verify status details
            status_details = physical_card_page.fetch_status_details()
            assert status_details == expected_status_details, f"Status details should be '{expected_status_details}', but got: '{status_details}'"
            logger.info(f"Verified: Status details is '{status_details}'")

            # Step 5: Verify device icon is displayed
            assert physical_card_page.is_device_icon_displayed(), "Device icon should be displayed"
            logger.info("Verified: Device icon is displayed")

            # Step 6: Verify footer logo is displayed
            assert physical_card_page.is_footer_logo_displayed(), "Footer logo should be displayed"
            logger.info("Verified: Footer logo is displayed")

            # Step 7: Click on back button
            physical_card_page.click_back_button()
            logger.info("Clicked on back button")

            # Step 8: Verify exit dialog title
            dialog_title = physical_card_page.fetch_dialog_title()
            assert dialog_title == expected_dialog_title, f"Dialog title should be '{expected_dialog_title}', but got: '{dialog_title}'"
            logger.info(f"Verified: Dialog title is '{dialog_title}'")

            # Step 9: Verify exit dialog text
            dialog_text = physical_card_page.fetch_dialog_text()
            assert dialog_text == expected_dialog_text, f"Dialog text should be '{expected_dialog_text}', but got: '{dialog_text}'"
            logger.info(f"Verified: Dialog text is '{dialog_text}'")

            # Step 10: Verify NO button text
            no_button_text = physical_card_page.fetch_no_button_text()
            assert no_button_text == expected_no_button, f"NO button text should be '{expected_no_button}', but got: '{no_button_text}'"
            logger.info(f"Verified: NO button text is '{no_button_text}'")

            # Step 11: Verify YES button text
            yes_button_text = physical_card_page.fetch_yes_button_text()
            assert yes_button_text == expected_yes_button, f"YES button text should be '{expected_yes_button}', but got: '{yes_button_text}'"
            logger.info(f"Verified: YES button text is '{yes_button_text}'")

            # Step 12: Click NO to stay on physical card page
            physical_card_page.click_no_button()
            logger.info("Clicked on NO button - Stayed on physical card page")

            # Step 13: Click back button again
            physical_card_page.click_back_button()
            logger.info("Clicked on back button again")

            # Step 14: Click YES to exit and return to home page
            physical_card_page.click_yes_button()
            logger.info("Clicked on YES button")

            # Step 15: Verify navigation back to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: Navigated back to home page successfully")

            logger.info(f"Test case {testcase_id} completed successfully - Physical card page UI and exit dialog verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_012():
    """
    sub_feature_code: UI_Common_PM_LMS_Physical_Card_Page_Transaction_Idle_Timeout
    file_name: test_UI_Common_LMS_PhysicalCardPage.py
    Sub Feature Description: Verify transaction idle timer expires after ~2 minutes of inactivity
                            on physical card page and appropriate timeout dialog is displayed
    TC naming code description: 100: Payment Method, 1010: LMS, 012: TC012
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
        expected_dialog_title = "TXN_IDLE_TIMER_EXPIRED"
        expected_dialog_text = "Transaction Failed. Please try again."
        expected_ok_button = "OK"

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
            physical_card_page = PhysicalCardPage(driver=app_driver)
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

            # Step 1: Click on Proceed button
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button - Waiting for idle timeout (~2 minutes)")

            # Step 2: Wait for timeout dialog to appear (approximately 2 minutes)
            physical_card_page.wait_for_timeout_dialog(timeout=150)
            logger.info("Timeout dialog appeared after idle timer expired")

            # Step 3: Verify timeout dialog title
            dialog_title = physical_card_page.fetch_dialog_title()
            assert dialog_title == expected_dialog_title, f"Dialog title should be '{expected_dialog_title}', but got: '{dialog_title}'"
            logger.info(f"Verified: Dialog title is '{dialog_title}'")

            # Step 4: Verify timeout dialog text
            dialog_text = physical_card_page.fetch_dialog_text()
            assert dialog_text == expected_dialog_text, f"Dialog text should be '{expected_dialog_text}', but got: '{dialog_text}'"
            logger.info(f"Verified: Dialog text is '{dialog_text}'")

            # Step 5: Verify OK button text
            ok_button_text = physical_card_page.fetch_ok_button_text()
            assert ok_button_text == expected_ok_button, f"OK button text should be '{expected_ok_button}', but got: '{ok_button_text}'"
            logger.info(f"Verified: OK button text is '{ok_button_text}'")

            # Step 6: Click OK to dismiss dialog and return to home page
            physical_card_page.click_ok_button()
            logger.info("Clicked on OK button")

            # Step 7: Verify navigation back to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: Navigated back to home page successfully")

            logger.info(f"Test case {testcase_id} completed successfully - Transaction idle timeout verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)

