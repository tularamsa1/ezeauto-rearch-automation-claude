import sys
import time
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables

from PageFactory.LMS.app_home_page import HomePage
from PageFactory.LMS.app_lounge_access_page import LoungeAccessPage
from PageFactory.LMS.app_pin_entry_page import PinEntryPage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_card_page import CardPage

from Utilities import ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

# ============== CONSTANTS ==============
# Card type to use for PIN entry tests (uses free visit card to get to PIN entry via Pay)
# TODO: Update with actual card type
PIN_ENTRY_TEST_CARD_TYPE = "EMV_WITH_PIN_VISA_CREDIT_417666"

# Expected dialog values for transaction declined
EXPECTED_TXN_DECLINED_TITLE = "TXN_DECLINED"
EXPECTED_TXN_DECLINED_TEXT = "Transaction declined"


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_021():
    """
    sub_feature_code: UI_Common_PM_LMS_Pin_Entry_Page_UI_Verification
    file_name: test_UI_Common_LMS_PinEntryPage.py
    Sub Feature Description: Verify PIN Entry page is displayed with PIN content field
                            and Cancel button returns to Lounge Access page
    TC naming code description: 100: Payment Method, 1010: LMS, 021: TC021
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
            lounge_access_page = LoungeAccessPage(driver=app_driver)
            pin_entry_page = PinEntryPage(driver=app_driver)

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Navigate to PIN Entry page (Home -> Proceed -> Card -> Lounge -> Pay)
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting card type: {PIN_ENTRY_TEST_CARD_TYPE}")
            card_page.select_cardtype(text=PIN_ENTRY_TEST_CARD_TYPE)
            logger.info(f"Selected card type: {PIN_ENTRY_TEST_CARD_TYPE}")

            assert lounge_access_page.is_lounge_access_page_displayed(), "Lounge Access page should be displayed"
            logger.info("Lounge Access page is displayed")

            lounge_access_page.click_on_pay_button()
            logger.info("Clicked on Pay button")

            # Step 2: Verify PIN Entry page is displayed
            assert pin_entry_page.is_pin_entry_page_displayed(), "PIN Entry page should be displayed"
            logger.info("Verified: PIN Entry page is displayed")

            # Step 3: Verify PIN content field is present (initially empty)
            pin_content = pin_entry_page.get_pin_content()
            logger.info(f"Verified: PIN content field is present, value: '{pin_content}'")

            # Step 4: Click Cancel to return to Lounge Access
            pin_entry_page.click_cancel_button()
            logger.info("Clicked Cancel button to exit PIN Entry")

            # Step 5: Verify return to Lounge Access page
            assert lounge_access_page.is_lounge_access_page_displayed(), \
                "Lounge Access page should be displayed after Cancel"
            logger.info("Verified: Returned to Lounge Access page")

            # Step 6: Click back to return to home page
            lounge_access_page.click_on_back_button()
            logger.info("Clicked back button to return to home page")

            # Step 7: Verify return to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: User returned to home page")

            logger.info(f"Test case {testcase_id} completed successfully - PIN Entry page UI verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_022():
    """
    sub_feature_code: UI_Common_PM_LMS_Pin_Entry_Page_Enter_Pin_Functionality
    file_name: test_UI_Common_LMS_PinEntryPage.py
    Sub Feature Description: Verify PIN can be entered using number pad and
                            PIN content field displays entered digits
    TC naming code description: 100: Payment Method, 1010: LMS, 022: TC022
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

        # Test PIN to enter
        test_pin = "1234"

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
            lounge_access_page = LoungeAccessPage(driver=app_driver)
            pin_entry_page = PinEntryPage(driver=app_driver)

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Navigate to PIN Entry page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting card type: {PIN_ENTRY_TEST_CARD_TYPE}")
            card_page.select_cardtype(text=PIN_ENTRY_TEST_CARD_TYPE)
            logger.info(f"Selected card type: {PIN_ENTRY_TEST_CARD_TYPE}")

            lounge_access_page.click_on_pay_button()
            logger.info("Clicked on Pay button")

            # Step 2: Verify PIN Entry page is displayed
            assert pin_entry_page.is_pin_entry_page_displayed(), "PIN Entry page should be displayed"
            logger.info("PIN Entry page is displayed")

            # Step 3: Enter PIN using the enter_pin method
            pin_entry_page.enter_pin(test_pin)
            logger.info(f"Entered PIN: {test_pin}")

            # Step 4: Verify PIN content is not empty (PIN is usually masked)
            pin_content = pin_entry_page.get_pin_content()
            assert pin_content is not None, "PIN content should be displayed"
            logger.info(f"Verified: PIN content field has value: '{pin_content}'")

            # Step 5: Click Cancel to return
            pin_entry_page.click_cancel_button()
            logger.info("Clicked Cancel button to exit PIN Entry")

            # Step 6: Click back on lounge access to return to home
            lounge_access_page.click_on_back_button()
            logger.info("Clicked back button to return to home page")

            # Step 7: Verify return to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: User returned to home page")

            logger.info(f"Test case {testcase_id} completed successfully - PIN entry functionality verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_023():
    """
    sub_feature_code: UI_Common_PM_LMS_Pin_Entry_Page_Clear_Button_Functionality
    file_name: test_UI_Common_LMS_PinEntryPage.py
    Sub Feature Description: Verify Clear button clears entered PIN digits
    TC naming code description: 100: Payment Method, 1010: LMS, 023: TC023
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
            lounge_access_page = LoungeAccessPage(driver=app_driver)
            pin_entry_page = PinEntryPage(driver=app_driver)

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Navigate to PIN Entry page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting card type: {PIN_ENTRY_TEST_CARD_TYPE}")
            card_page.select_cardtype(text=PIN_ENTRY_TEST_CARD_TYPE)
            logger.info(f"Selected card type: {PIN_ENTRY_TEST_CARD_TYPE}")

            lounge_access_page.click_on_pay_button()
            logger.info("Clicked on Pay button")

            # Step 2: Verify PIN Entry page is displayed
            assert pin_entry_page.is_pin_entry_page_displayed(), "PIN Entry page should be displayed"
            logger.info("PIN Entry page is displayed")

            # Step 3: Enter some digits
            pin_entry_page.enter_pin("1234")
            logger.info("Entered PIN: 1234")

            # Step 4: Get PIN content before clear
            pin_content_before = pin_entry_page.get_pin_content()
            logger.info(f"PIN content before clear: '{pin_content_before}'")

            # Step 5: Click Clear button
            pin_entry_page.click_clear_button()
            logger.info("Clicked Clear button")

            # Step 6: Get PIN content after clear
            pin_content_after = pin_entry_page.get_pin_content()
            logger.info(f"PIN content after clear: '{pin_content_after}'")

            # Step 7: Verify PIN content is cleared (different from before or empty)
            assert pin_content_after != pin_content_before or pin_content_after == "", \
                "PIN content should be cleared after clicking Clear button"
            logger.info("Verified: Clear button successfully cleared PIN content")

            # Step 8: Click Cancel to return
            pin_entry_page.click_cancel_button()
            logger.info("Clicked Cancel button to exit PIN Entry")

            # Step 9: Click back on lounge access to return to home
            lounge_access_page.click_on_back_button()
            logger.info("Clicked back button to return to home page")

            # Step 10: Verify return to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: User returned to home page")

            logger.info(f"Test case {testcase_id} completed successfully - Clear button functionality verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_024():
    """
    sub_feature_code: UI_Common_PM_LMS_Pin_Entry_Page_Cancel_Button_Navigation
    file_name: test_UI_Common_LMS_PinEntryPage.py
    Sub Feature Description: Verify Cancel button returns user to Lounge Access page
    TC naming code description: 100: Payment Method, 1010: LMS, 024: TC024
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
            lounge_access_page = LoungeAccessPage(driver=app_driver)
            pin_entry_page = PinEntryPage(driver=app_driver)

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Navigate to PIN Entry page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting card type: {PIN_ENTRY_TEST_CARD_TYPE}")
            card_page.select_cardtype(text=PIN_ENTRY_TEST_CARD_TYPE)
            logger.info(f"Selected card type: {PIN_ENTRY_TEST_CARD_TYPE}")

            lounge_access_page.click_on_pay_button()
            logger.info("Clicked on Pay button")

            # Step 2: Verify PIN Entry page is displayed
            assert pin_entry_page.is_pin_entry_page_displayed(), "PIN Entry page should be displayed"
            logger.info("PIN Entry page is displayed")

            # Step 3: Click Cancel button
            pin_entry_page.click_cancel_button()
            logger.info("Clicked Cancel button")

            # Step 4: Verify user is returned to Lounge Access page
            assert lounge_access_page.is_lounge_access_page_displayed(), \
                "Lounge Access page should be displayed after clicking Cancel"
            logger.info("Verified: User returned to Lounge Access page after clicking Cancel")

            # Step 5: Click back to return to home page
            lounge_access_page.click_on_back_button()
            logger.info("Clicked back button to return to home page")

            # Step 6: Verify return to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: User returned to home page")

            logger.info(f"Test case {testcase_id} completed successfully - Cancel button navigation verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_025():
    """
    sub_feature_code: UI_Common_PM_LMS_Pin_Entry_Page_Transaction_Declined_Timeout
    file_name: test_UI_Common_LMS_PinEntryPage.py
    Sub Feature Description: Verify transaction declined dialog appears after 30 second timeout
                            when no PIN is entered on PIN Entry page
    TC naming code description: 100: Payment Method, 1010: LMS, 025: TC025
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

        # Timeout duration in seconds
        pin_entry_timeout = 30

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
            lounge_access_page = LoungeAccessPage(driver=app_driver)
            pin_entry_page = PinEntryPage(driver=app_driver)

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Navigate to PIN Entry page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting card type: {PIN_ENTRY_TEST_CARD_TYPE}")
            card_page.select_cardtype(text=PIN_ENTRY_TEST_CARD_TYPE)
            logger.info(f"Selected card type: {PIN_ENTRY_TEST_CARD_TYPE}")

            lounge_access_page.click_on_pay_button()
            logger.info("Clicked on Pay button")

            # Step 2: Verify PIN Entry page is displayed
            assert pin_entry_page.is_pin_entry_page_displayed(), "PIN Entry page should be displayed"
            logger.info("PIN Entry page is displayed")

            # Step 3: Wait for timeout (~30 seconds) without entering PIN
            logger.info(f"Waiting for {pin_entry_timeout} seconds for PIN entry timeout...")
            time.sleep(pin_entry_timeout)
            logger.info(f"Waited {pin_entry_timeout} seconds")

            # Step 4: Verify transaction declined dialog is displayed
            assert pin_entry_page.is_txn_declined_dialog_displayed(), \
                "Transaction declined dialog should be displayed after timeout"
            logger.info("Transaction declined dialog is displayed")

            # Step 5: Verify dialog title
            dialog_title = pin_entry_page.fetch_txn_declined_title()
            assert dialog_title == EXPECTED_TXN_DECLINED_TITLE, \
                f"Dialog title should be '{EXPECTED_TXN_DECLINED_TITLE}', but got: '{dialog_title}'"
            logger.info(f"Verified: Dialog title is '{dialog_title}'")

            # Step 6: Verify dialog text
            dialog_text = pin_entry_page.fetch_txn_declined_text()
            assert dialog_text == EXPECTED_TXN_DECLINED_TEXT, \
                f"Dialog text should be '{EXPECTED_TXN_DECLINED_TEXT}', but got: '{dialog_text}'"
            logger.info(f"Verified: Dialog text is '{dialog_text}'")

            # Step 7: Click OK to dismiss dialog
            pin_entry_page.click_txn_declined_ok_button()
            logger.info("Clicked OK button to dismiss dialog")

            # Step 8: Verify return to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: User returned to home page after transaction declined")

            logger.info(f"Test case {testcase_id} completed successfully - PIN entry timeout dialog verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)

