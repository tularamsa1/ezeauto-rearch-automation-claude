import sys
import time
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables

from PageFactory.LMS.app_home_page import HomePage
from PageFactory.LMS.app_lounge_access_page import LoungeAccessPage
from PageFactory.LMS.app_pin_entry_page import PinEntryPage
from PageFactory.LMS.app_txn_success_page import TxnSuccessPage
from PageFactory.LMS.app_scan_boarding_pass_page import ScanBoardingPassPage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_card_page import CardPage

from Utilities import ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

# ============== CONSTANTS ==============
# Card type to use for successful transaction (must be a valid test card with correct PIN)
# TODO: Update with actual card type and PIN for successful transaction
SCAN_BP_TEST_CARD_TYPE = "EMV_WITH_PIN_VISA_CREDIT_417666"
SCAN_BP_TEST_PIN = "1234"  # TODO: Update with correct PIN for the test card

# Expected values
EXPECTED_PAGE_TITLE = "Scan Boarding Pass"
EXPECTED_GO_HOME_BUTTON_TEXT = "Home"
EXPECTED_SCANNER_PROBLEM_TEXT = "Facing problem with scanner?"
EXPECTED_ENTER_PNR_BUTTON_TEXT = "Enter PNR"
EXPECTED_PNR_INSTRUCTION_TEXT = "Enter 6 digit PNR number"
EXPECTED_SCAN_AGAIN_BUTTON_TEXT = "Scan again"
EXPECTED_DONE_PNR_BUTTON_TEXT = "Done"
EXPECTED_SKIP_TITLE = "Are you sure you want to go home?"
EXPECTED_SKIP_MESSAGE = "You will not be able to scan boarding pass for these travellers."
EXPECTED_CONTINUE_SCANNING_TEXT = "Continue scanning"

# Scanner timeout (in seconds)
SCANNER_TIMEOUT = 30


def navigate_to_scan_boarding_pass_page(home_page, login_page, card_page, lounge_access_page,
                                         pin_entry_page, txn_success_page, app_username, app_password):
    """
    Helper function to navigate from home to scan boarding pass page.
    Flow: Login -> Home -> Proceed -> Card Selection -> Pay -> PIN Entry -> Txn Success -> Scan Boarding Pass
    """
    # Login if needed
    if login_page.is_login_page_displayed():
        login_page.perform_login_for_auto_login_functionality(app_username, app_password)
        logger.info("Logged in successfully")

    # Wait for home page
    home_page.wait_for_navigation_to_load()
    logger.info("Home page displayed")

    # Click Proceed
    home_page.click_on_proceed_button()
    logger.info("Clicked Proceed button")

    # Select card type
    card_page.select_cardtype(text=SCAN_BP_TEST_CARD_TYPE)
    logger.info(f"Selected card type: {SCAN_BP_TEST_CARD_TYPE}")

    # Click Pay on Lounge Access page
    lounge_access_page.click_on_pay_button()
    logger.info("Clicked Pay button on Lounge Access page")

    # # Enter PIN
    # pin_entry_page.enter_pin(SCAN_BP_TEST_PIN)
    # pin_entry_page.click_sure_button()
    # logger.info("Entered PIN and clicked Sure")

    # Click Scan Boarding Pass on Transaction Success page
    txn_success_page.click_scan_boarding_pass_button()
    logger.info("Clicked Scan Boarding Pass button")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_030():
    """
    sub_feature_code: UI_Common_PM_LMS_Scan_Boarding_Pass_UI_Elements_Verification
    file_name: test_UI_Common_LMS_ScanBoardingPassPage.py
    Sub Feature Description: Verify Scan Boarding Pass page UI elements
    TC naming code description: 100: Payment Method, 1010: LMS, 030: TC030
    """
    testcase_id = "test_common_100_1010_030"
    # -----------------------------Preconditions (Start)---------------------
    try:
        Configuration.executePrerequisites(testcase_id)
    except Exception:
        Configuration.perform_exception(testcase_id)
        pytest.skip("Pre-requisites failed")

    app_username, app_password = ResourceAssigner.get_credentials(testcase_id)
    if app_username is None or app_password is None:
        GlobalVariables.EXCEL_TC_Execution = "Skip"
        pytest.skip("Unable to fetch credentials")
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
        card_page = CardPage(driver=app_driver)
        lounge_access_page = LoungeAccessPage(driver=app_driver)
        pin_entry_page = PinEntryPage(driver=app_driver)
        txn_success_page = TxnSuccessPage(driver=app_driver)
        scan_bp_page = ScanBoardingPassPage(driver=app_driver)

        # Navigate to Scan Boarding Pass page
        navigate_to_scan_boarding_pass_page(home_page, login_page, card_page, lounge_access_page,
                                            pin_entry_page, txn_success_page, app_username, app_password)

        # Step 1: Verify Scan Boarding Pass page is displayed
        assert scan_bp_page.is_scan_boarding_pass_page_displayed(), \
            "Scan Boarding Pass page should be displayed"
        logger.info("Verified: Scan Boarding Pass page is displayed")

        # Step 2: Verify page title
        title = scan_bp_page.fetch_title()
        assert title == EXPECTED_PAGE_TITLE, \
            f"Page title should be '{EXPECTED_PAGE_TITLE}', but got: '{title}'"
        logger.info(f"Verified: Page title is '{title}'")

        # Step 3: Verify scanner viewfinder is displayed
        assert scan_bp_page.is_scanner_viewfinder_displayed(), \
            "Scanner viewfinder should be displayed"
        logger.info("Verified: Scanner viewfinder is displayed")

        # Step 4: Verify Go Home button text
        go_home_text = scan_bp_page.fetch_go_home_button_text()
        assert go_home_text == EXPECTED_GO_HOME_BUTTON_TEXT, \
            f"Go Home button text should be '{EXPECTED_GO_HOME_BUTTON_TEXT}', but got: '{go_home_text}'"
        logger.info(f"Verified: Go Home button text is '{go_home_text}'")

        # Step 5: Verify Powered by logo is displayed
        assert scan_bp_page.is_powered_by_logo_displayed(), \
            "Powered by logo should be displayed"
        logger.info("Verified: Powered by logo is displayed")

        # Step 6: Verify Enter PNR button is NOT displayed (appears only after 30 sec timeout)
        assert not scan_bp_page.is_enter_pnr_button_displayed(), \
            "Enter PNR button should NOT be displayed initially (before timeout)"
        logger.info("Verified: Enter PNR button is NOT displayed initially")

        # Return to home
        scan_bp_page.click_go_home_button()
        scan_bp_page.click_go_home_skip_button()
        logger.info("Returned to home page")

        logger.info(f"Test case {testcase_id} completed successfully - Scan Boarding Pass UI verified")
        GlobalVariables.EXCEL_TC_Execution = "Pass"
    except Exception as e:
        Configuration.perform_exe_exception(testcase_id)
        pytest.fail("Test case execution failed due to the exception -" + str(e))
    # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_031():
    """
    sub_feature_code: UI_Common_PM_LMS_Scan_Boarding_Pass_Scanner_Timeout_And_Enter_PNR
    file_name: test_UI_Common_LMS_ScanBoardingPassPage.py
    Sub Feature Description: Verify scanner timeout elements and Enter PNR dialog functionality
    TC naming code description: 100: Payment Method, 1010: LMS, 031: TC031
    """
    testcase_id = "test_common_100_1010_031"
    # -----------------------------Preconditions (Start)---------------------
    try:
        Configuration.executePrerequisites(testcase_id)
    except Exception:
        Configuration.perform_exception(testcase_id)
        pytest.skip("Pre-requisites failed")

    app_username, app_password = ResourceAssigner.get_credentials(testcase_id)
    if app_username is None or app_password is None:
        GlobalVariables.EXCEL_TC_Execution = "Skip"
        pytest.skip("Unable to fetch credentials")
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
        card_page = CardPage(driver=app_driver)
        lounge_access_page = LoungeAccessPage(driver=app_driver)
        pin_entry_page = PinEntryPage(driver=app_driver)
        txn_success_page = TxnSuccessPage(driver=app_driver)
        scan_bp_page = ScanBoardingPassPage(driver=app_driver)

        # Navigate to Scan Boarding Pass page
        navigate_to_scan_boarding_pass_page(home_page, login_page, card_page, lounge_access_page,
                                            pin_entry_page, txn_success_page, app_username, app_password)

        # Step 1: Verify Scan Boarding Pass page is displayed
        assert scan_bp_page.is_scan_boarding_pass_page_displayed(), \
            "Scan Boarding Pass page should be displayed"
        logger.info("Verified: Scan Boarding Pass page is displayed")

        # Step 2: Wait for scanner timeout (30 seconds)
        logger.info(f"Waiting {SCANNER_TIMEOUT} seconds for scanner timeout...")
        time.sleep(SCANNER_TIMEOUT)
        logger.info("Scanner timeout period completed")

        # Step 3: Verify Scanner Problem text is displayed
        scanner_problem_text = scan_bp_page.fetch_scanner_problem_text()
        assert scanner_problem_text == EXPECTED_SCANNER_PROBLEM_TEXT, \
            f"Scanner problem text should be '{EXPECTED_SCANNER_PROBLEM_TEXT}', but got: '{scanner_problem_text}'"
        logger.info(f"Verified: Scanner problem text is '{scanner_problem_text}'")

        # Step 4: Verify Enter PNR button is displayed with correct text
        enter_pnr_text = scan_bp_page.fetch_enter_pnr_button_text()
        assert enter_pnr_text == EXPECTED_ENTER_PNR_BUTTON_TEXT, \
            f"Enter PNR button text should be '{EXPECTED_ENTER_PNR_BUTTON_TEXT}', but got: '{enter_pnr_text}'"
        logger.info(f"Verified: Enter PNR button text is '{enter_pnr_text}'")

        # Step 5: Click Enter PNR button
        scan_bp_page.click_enter_pnr_button()
        logger.info("Clicked Enter PNR button")

        # Step 6: Verify Enter PNR dialog is displayed
        assert scan_bp_page.is_enter_pnr_dialog_displayed(), \
            "Enter PNR dialog should be displayed"
        logger.info("Verified: Enter PNR dialog is displayed")

        # Step 7: Verify Scan Again button text
        scan_again_text = scan_bp_page.fetch_scan_again_button_text()
        assert scan_again_text == EXPECTED_SCAN_AGAIN_BUTTON_TEXT, \
            f"Scan Again button text should be '{EXPECTED_SCAN_AGAIN_BUTTON_TEXT}', but got: '{scan_again_text}'"
        logger.info(f"Verified: Scan Again button text is '{scan_again_text}'")

        # Step 8: Verify PNR instruction text
        pnr_instruction = scan_bp_page.fetch_pnr_instruction_text()
        assert pnr_instruction == EXPECTED_PNR_INSTRUCTION_TEXT, \
            f"PNR instruction text should be '{EXPECTED_PNR_INSTRUCTION_TEXT}', but got: '{pnr_instruction}'"
        logger.info(f"Verified: PNR instruction text is '{pnr_instruction}'")

        # Step 9: Enter a test PNR number
        test_pnr = "ABC123"
        scan_bp_page.enter_pnr_number(test_pnr)
        logger.info(f"Entered PNR number: {test_pnr}")

        # Step 10: Verify PNR input has the entered value
        pnr_value = scan_bp_page.get_pnr_input_value()
        assert pnr_value == test_pnr, \
            f"PNR input should contain '{test_pnr}', but got: '{pnr_value}'"
        logger.info(f"Verified: PNR input contains '{pnr_value}'")

        # Step 11: Click Done to submit PNR
        scan_bp_page.click_done_pnr_button()
        logger.info("Clicked Done to submit PNR")

        # Return to home
        scan_bp_page.click_go_home_button()
        scan_bp_page.click_go_home_skip_button()
        logger.info("Returned to home page")

        logger.info(f"Test case {testcase_id} completed successfully - Scanner timeout and Enter PNR verified")
        GlobalVariables.EXCEL_TC_Execution = "Pass"
    except Exception as e:
        Configuration.perform_exe_exception(testcase_id)
        pytest.fail("Test case execution failed due to the exception -" + str(e))
    # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_032():
    """
    sub_feature_code: UI_Common_PM_LMS_Scan_Boarding_Pass_Go_Home_Confirmation_Dialog
    file_name: test_UI_Common_LMS_ScanBoardingPassPage.py
    Sub Feature Description: Verify Go Home confirmation dialog elements and both button actions
    TC naming code description: 100: Payment Method, 1010: LMS, 032: TC032
    """
    testcase_id = "test_common_100_1010_032"
    # -----------------------------Preconditions (Start)---------------------
    try:
        Configuration.executePrerequisites(testcase_id)
    except Exception:
        Configuration.perform_exception(testcase_id)
        pytest.skip("Pre-requisites failed")

    app_username, app_password = ResourceAssigner.get_credentials(testcase_id)
    if app_username is None or app_password is None:
        GlobalVariables.EXCEL_TC_Execution = "Skip"
        pytest.skip("Unable to fetch credentials")
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
        card_page = CardPage(driver=app_driver)
        lounge_access_page = LoungeAccessPage(driver=app_driver)
        pin_entry_page = PinEntryPage(driver=app_driver)
        txn_success_page = TxnSuccessPage(driver=app_driver)
        scan_bp_page = ScanBoardingPassPage(driver=app_driver)

        # Navigate to Scan Boarding Pass page
        navigate_to_scan_boarding_pass_page(home_page, login_page, card_page, lounge_access_page,
                                            pin_entry_page, txn_success_page, app_username, app_password)

        # Step 1: Verify Scan Boarding Pass page is displayed
        assert scan_bp_page.is_scan_boarding_pass_page_displayed(), \
            "Scan Boarding Pass page should be displayed"
        logger.info("Verified: Scan Boarding Pass page is displayed")

        # Step 2: Click Go Home button
        scan_bp_page.click_go_home_button()
        logger.info("Clicked Go Home button")

        # Step 3: Verify confirmation dialog title
        skip_title = scan_bp_page.fetch_skip_title()
        assert skip_title == EXPECTED_SKIP_TITLE, \
            f"Skip dialog title should be '{EXPECTED_SKIP_TITLE}', but got: '{skip_title}'"
        logger.info(f"Verified: Skip dialog title is '{skip_title}'")

        # Step 4: Verify confirmation dialog message
        skip_message = scan_bp_page.fetch_skip_message()
        assert skip_message == EXPECTED_SKIP_MESSAGE, \
            f"Skip dialog message should be '{EXPECTED_SKIP_MESSAGE}', but got: '{skip_message}'"
        logger.info(f"Verified: Skip dialog message is '{skip_message}'")

        # Step 5: Verify Continue scanning button text
        continue_text = scan_bp_page.fetch_continue_scanning_button_text()
        assert continue_text == EXPECTED_CONTINUE_SCANNING_TEXT, \
            f"Continue scanning text should be '{EXPECTED_CONTINUE_SCANNING_TEXT}', but got: '{continue_text}'"
        logger.info(f"Verified: Continue scanning button text is '{continue_text}'")

        # Step 6: Click Continue scanning to dismiss dialog
        scan_bp_page.click_continue_scanning_button()
        logger.info("Clicked Continue scanning button")

        # Step 7: Verify still on Scan Boarding Pass page
        assert scan_bp_page.is_scan_boarding_pass_page_displayed(), \
            "Should still be on Scan Boarding Pass page after clicking Continue scanning"
        logger.info("Verified: Still on Scan Boarding Pass page")

        # Step 8: Click Go Home again
        scan_bp_page.click_go_home_button()
        logger.info("Clicked Go Home button again")

        # Step 9: Click Home to go to home page
        scan_bp_page.click_go_home_skip_button()
        logger.info("Clicked Home button on confirmation dialog")

        # Step 10: Verify returned to home page
        home_page.wait_for_navigation_to_load()
        logger.info("Verified: Returned to home page")

        logger.info(f"Test case {testcase_id} completed successfully - Go Home confirmation dialog verified")
        GlobalVariables.EXCEL_TC_Execution = "Pass"
    except Exception as e:
        Configuration.perform_exe_exception(testcase_id)
        pytest.fail("Test case execution failed due to the exception -" + str(e))
    # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)

