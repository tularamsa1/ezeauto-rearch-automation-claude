import sys
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

# ============== CARD TYPE CONSTANTS ==============
# Common expected values
EXPECTED_VISITS_LEFT_TEXT = "Visits Left"

# ------------------ FREE VISIT SCENARIO ------------------
# Card with free visits available (e.g., 1/2 Free visit left in this quarter)
# TODO: Update with actual card type that has free visits
FREE_VISIT_CARD_TYPE = "EMV_WITH_PIN_VISA_CREDIT_417666"
FREE_VISIT_EXPECTED_MESSAGE = "1/2 Free visit left in this quarter"
FREE_VISIT_EXPECTED_VISITS_NUMBER = "1"
FREE_VISIT_TO_PAY_AMOUNT = "₹2"

# ------------------ FREE VISITS EXHAUSTED SCENARIO ------------------
# Card with all free visits used up (0 remaining out of 2 total)
# TODO: Update with actual card type
FREE_VISITS_EXHAUSTED_CARD_TYPE = "FREE_VISITS_EXHAUSTED_CARD_HERE"
FREE_VISITS_EXHAUSTED_MESSAGE = "0/2 Free visit left in this quarter"
FREE_VISITS_EXHAUSTED_MESSAGE_TAG = "Paid lounge access available"  # Shows when visits exhausted
FREE_VISITS_EXHAUSTED_VISITS_NUMBER = "0"
FREE_VISITS_EXHAUSTED_TO_PAY_AMOUNT = "₹2,100"  # Paid access since free visits exhausted

# ------------------ PAID ACCESS SCENARIO ------------------
# Card with no free visits (paid access only, amount ₹2,100)
# TODO: Update with actual card type that has NO free visits
PAID_ACCESS_CARD_TYPE = "PAID_ACCESS_CARD_TYPE_HERE"
PAID_ACCESS_MESSAGE_TAG = "Paid lounge access available"
PAID_ACCESS_TO_PAY_AMOUNT = "₹2,100"


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_015():
    """
    sub_feature_code: UI_Common_PM_LMS_Lounge_Access_Page_Card_Details_Verification
    file_name: test_UI_Common_LMS_LoungeAccess.py
    Sub Feature Description: Verify card details section on Lounge Access page including
                            card holder name, card name, card brand logo and bank logo
    TC naming code description: 100: Payment Method, 1010: LMS, 015: TC015
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
        expected_title = "Lounge access"

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

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Click on Proceed button to navigate to card page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            # Step 2: Select card type on card page (using FREE_VISIT card for generic card details)
            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting card type: {FREE_VISIT_CARD_TYPE}")
            card_page.select_cardtype(text=FREE_VISIT_CARD_TYPE)
            logger.info(f"Selected card type: {FREE_VISIT_CARD_TYPE}")

            # Step 3: Verify Lounge Access page is displayed
            assert lounge_access_page.is_lounge_access_page_displayed(), "Lounge Access page should be displayed"
            logger.info("Lounge Access page is displayed")

            # Step 4: Verify page title
            title = lounge_access_page.fetch_lounge_access_title()
            assert title == expected_title, f"Title should be '{expected_title}', but got: '{title}'"
            logger.info(f"Verified: Page title is '{title}'")

            # Step 5: Verify card holder name is displayed
            card_holder_name = lounge_access_page.fetch_card_holder_name()
            assert card_holder_name is not None and card_holder_name != "", "Card holder name should be displayed"
            logger.info(f"Verified: Card holder name is '{card_holder_name}'")

            # Step 6: Verify card name is displayed
            card_name = lounge_access_page.fetch_card_name()
            assert card_name is not None and card_name != "", "Card name should be displayed"
            logger.info(f"Verified: Card name is '{card_name}'")

            # Step 7: Verify card brand logo is displayed
            assert lounge_access_page.is_card_brand_logo_displayed(), "Card brand logo should be displayed"
            logger.info("Verified: Card brand logo is displayed")

            # Step 8: Verify bank logo is displayed
            assert lounge_access_page.is_bank_logo_displayed(), "Bank logo should be displayed"
            logger.info("Verified: Bank logo is displayed")

            # Step 9: Click back to return to home page
            lounge_access_page.click_on_back_button()
            logger.info("Clicked on back button to return to home page")

            logger.info(f"Test case {testcase_id} completed successfully - Card details verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_016():
    """
    sub_feature_code: UI_Common_PM_LMS_Lounge_Access_Page_Visits_Section_Free_Visit_Card
    file_name: test_UI_Common_LMS_LoungeAccess.py
    Sub Feature Description: Verify visits section on Lounge Access page for FREE VISIT card
                            including visits left label, visits number, visits message
    TC naming code description: 100: Payment Method, 1010: LMS, 016: TC016
    Card Type: FREE_VISIT_CARD_TYPE (card with free visits available)
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

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Click on Proceed button to navigate to card page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            # Step 2: Select FREE VISIT card type
            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting FREE VISIT card type: {FREE_VISIT_CARD_TYPE}")
            card_page.select_cardtype(text=FREE_VISIT_CARD_TYPE)
            logger.info(f"Selected FREE VISIT card type: {FREE_VISIT_CARD_TYPE}")

            # Step 3: Verify Lounge Access page is displayed
            assert lounge_access_page.is_lounge_access_page_displayed(), "Lounge Access page should be displayed"
            logger.info("Lounge Access page is displayed")

            # Step 4: Verify "Visits Left" label
            visits_left_text = lounge_access_page.fetch_visits_left_text()
            assert visits_left_text == EXPECTED_VISITS_LEFT_TEXT, \
                f"Visits left text should be '{EXPECTED_VISITS_LEFT_TEXT}', but got: '{visits_left_text}'"
            logger.info(f"Verified: Visits left text is '{visits_left_text}'")

            # Step 5: Verify visits number matches expected for free visit card
            visits_number = lounge_access_page.fetch_visits_number()
            assert visits_number == FREE_VISIT_EXPECTED_VISITS_NUMBER, \
                f"Visits number should be '{FREE_VISIT_EXPECTED_VISITS_NUMBER}', but got: '{visits_number}'"
            logger.info(f"Verified: Visits number is '{visits_number}'")

            # Step 6: Verify visits message for free visit card
            visits_message = lounge_access_page.fetch_visits_message()
            assert visits_message == FREE_VISIT_EXPECTED_MESSAGE, \
                f"Visits message should be '{FREE_VISIT_EXPECTED_MESSAGE}', but got: '{visits_message}'"
            logger.info(f"Verified: Visits message is '{visits_message}'")

            # Step 7: Verify free guest text is displayed
            free_guest_text = lounge_access_page.fetch_free_guest_text()
            assert free_guest_text is not None and free_guest_text != "", "Free guest text should be displayed"
            logger.info(f"Verified: Free guest text is '{free_guest_text}'")

            # Step 8: Verify guests number is displayed
            guests_number = lounge_access_page.fetch_guests_number()
            assert guests_number is not None and guests_number != "", "Guests number should be displayed"
            logger.info(f"Verified: Guests number is '{guests_number}'")

            # Step 9: Click back to return to home page
            lounge_access_page.click_on_back_button()
            logger.info("Clicked on back button to return to home page")

            logger.info(f"Test case {testcase_id} completed successfully - Visits section verified for FREE VISIT card")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_017():
    """
    sub_feature_code: UI_Common_PM_LMS_Lounge_Access_Page_Visits_Section_Paid_Access_Card
    file_name: test_UI_Common_LMS_LoungeAccess.py
    Sub Feature Description: Verify visits section on Lounge Access page for PAID ACCESS card
                            including message tag and to pay amount
    TC naming code description: 100: Payment Method, 1010: LMS, 017: TC017
    Card Type: PAID_ACCESS_CARD_TYPE (card with NO free visits - paid access only)
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

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Click on Proceed button to navigate to card page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            # Step 2: Select PAID ACCESS card type (no free visits)
            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting PAID ACCESS card type: {PAID_ACCESS_CARD_TYPE}")
            card_page.select_cardtype(text=PAID_ACCESS_CARD_TYPE)
            logger.info(f"Selected PAID ACCESS card type: {PAID_ACCESS_CARD_TYPE}")

            # Step 3: Verify Lounge Access page is displayed
            assert lounge_access_page.is_lounge_access_page_displayed(), "Lounge Access page should be displayed"
            logger.info("Lounge Access page is displayed")

            # Step 4: Verify "Paid lounge access available" message tag
            message_tag = lounge_access_page.fetch_visits_message_tag()
            assert message_tag == PAID_ACCESS_MESSAGE_TAG, \
                f"Message tag should be '{PAID_ACCESS_MESSAGE_TAG}', but got: '{message_tag}'"
            logger.info(f"Verified: Message tag is '{message_tag}'")

            # Step 5: Verify paid access label
            paid_access_text = lounge_access_page.fetch_paid_access_text()
            assert paid_access_text is not None and paid_access_text != "", "Paid access label should be displayed"
            logger.info(f"Verified: Paid access text is '{paid_access_text}'")

            # Step 6: Verify paid access amount
            paid_access_amount = lounge_access_page.fetch_paid_access_amount()
            assert paid_access_amount is not None and paid_access_amount != "", "Paid access amount should be displayed"
            logger.info(f"Verified: Paid access amount is '{paid_access_amount}'")

            # Step 7: Verify to pay amount for paid access card
            to_pay_amount = lounge_access_page.fetch_to_pay_amount()
            assert to_pay_amount == PAID_ACCESS_TO_PAY_AMOUNT, \
                f"To pay amount should be '{PAID_ACCESS_TO_PAY_AMOUNT}', but got: '{to_pay_amount}'"
            logger.info(f"Verified: To pay amount is '{to_pay_amount}'")

            # Step 8: Click back to return to home page
            lounge_access_page.click_on_back_button()
            logger.info("Clicked on back button to return to home page")

            logger.info(f"Test case {testcase_id} completed successfully - Visits section verified for PAID ACCESS card")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_018():
    """
    sub_feature_code: UI_Common_PM_LMS_Lounge_Access_Page_Cancel_Button_Verification
    file_name: test_UI_Common_LMS_LoungeAccess.py
    Sub Feature Description: Verify Cancel button functionality on Lounge Access page
                            returns user to home page
    TC naming code description: 100: Payment Method, 1010: LMS, 018: TC018
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

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Click on Proceed button to navigate to card page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            # Step 2: Select card type on card page
            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting card type: {FREE_VISIT_CARD_TYPE}")
            card_page.select_cardtype(text=FREE_VISIT_CARD_TYPE)
            logger.info(f"Selected card type: {FREE_VISIT_CARD_TYPE}")

            # Step 3: Verify Lounge Access page is displayed
            assert lounge_access_page.is_lounge_access_page_displayed(), "Lounge Access page should be displayed"
            logger.info("Lounge Access page is displayed")

            # Step 4: Click on Cancel button
            lounge_access_page.click_on_cancel_button()
            logger.info("Clicked on Cancel button")

            # Step 5: Verify user is returned to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: User returned to home page after clicking Cancel")

            logger.info(f"Test case {testcase_id} completed successfully - Cancel button functionality verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_019():
    """
    sub_feature_code: UI_Common_PM_LMS_Lounge_Access_Page_Pay_Button_Navigation
    file_name: test_UI_Common_LMS_LoungeAccess.py
    Sub Feature Description: Verify Pay button on Lounge Access page navigates to PIN Entry page
    TC naming code description: 100: Payment Method, 1010: LMS, 019: TC019
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

            # Step 1: Click on Proceed button to navigate to card page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            # Step 2: Select card type on card page
            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting card type: {FREE_VISIT_CARD_TYPE}")
            card_page.select_cardtype(text=FREE_VISIT_CARD_TYPE)
            logger.info(f"Selected card type: {FREE_VISIT_CARD_TYPE}")

            # Step 3: Verify Lounge Access page is displayed
            assert lounge_access_page.is_lounge_access_page_displayed(), "Lounge Access page should be displayed"
            logger.info("Lounge Access page is displayed")

            # Step 4: Click on Pay button
            lounge_access_page.click_on_pay_button()
            logger.info("Clicked on Pay button")

            # Step 5: Verify PIN Entry page is displayed
            assert pin_entry_page.is_pin_entry_page_displayed(), "PIN Entry page should be displayed after clicking Pay"
            logger.info("Verified: PIN Entry page is displayed after clicking Pay button")

            # Step 6: Click cancel to return to lounge access page
            pin_entry_page.click_cancel_button()
            logger.info("Clicked cancel button on PIN Entry page")

            # Step 7: Click back on lounge access to return to home
            lounge_access_page.click_on_back_button()
            logger.info("Clicked back button to return to home page")

            # Step 8: Verify return to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: User returned to home page")

            logger.info(f"Test case {testcase_id} completed successfully - Pay button navigation verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_020():
    """
    sub_feature_code: UI_Common_PM_LMS_Lounge_Access_Page_Free_Visits_Exhausted_Scenario
    file_name: test_UI_Common_LMS_LoungeAccess.py
    Sub Feature Description: Verify lounge access page for card with free visits exhausted
                            (0/2 free visits remaining, shows "Paid lounge access available", amount ₹2,100)
    TC naming code description: 100: Payment Method, 1010: LMS, 020: TC020
    Card Type: FREE_VISITS_EXHAUSTED_CARD_TYPE
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

            # Check if already logged in, if not perform login
            try:
                home_page.wait_for_navigation_to_load()
                logger.info("Already logged in - Home page loaded directly")
            except Exception:
                logger.info(f"Not logged in - Performing login with username: {app_username}")
                login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
                home_page.wait_for_navigation_to_load()
                logger.info("App homepage loaded successfully after login")

            # Step 1: Click on Proceed button to navigate to card page
            home_page.click_on_proceed_button()
            logger.info("Clicked on Proceed button")

            # Step 2: Select card with free visits exhausted
            card_page = CardPage(driver=app_driver)
            logger.info(f"Selecting card type: {FREE_VISITS_EXHAUSTED_CARD_TYPE}")
            card_page.select_cardtype(text=FREE_VISITS_EXHAUSTED_CARD_TYPE)
            logger.info(f"Selected card type: {FREE_VISITS_EXHAUSTED_CARD_TYPE}")

            # Step 3: Verify Lounge Access page is displayed
            assert lounge_access_page.is_lounge_access_page_displayed(), "Lounge Access page should be displayed"
            logger.info("Lounge Access page is displayed")

            # Step 4: Verify visits number (should be 0 since all exhausted)
            visits_number = lounge_access_page.fetch_visits_number()
            assert visits_number == FREE_VISITS_EXHAUSTED_VISITS_NUMBER, \
                f"Visits number should be '{FREE_VISITS_EXHAUSTED_VISITS_NUMBER}', but got: '{visits_number}'"
            logger.info(f"Verified: Visits number is '{visits_number}'")

            # Step 5: Verify visits message (e.g., "0/2 Free visit left in this quarter")
            visits_message = lounge_access_page.fetch_visits_message()
            assert visits_message == FREE_VISITS_EXHAUSTED_MESSAGE, \
                f"Visits message should be '{FREE_VISITS_EXHAUSTED_MESSAGE}', but got: '{visits_message}'"
            logger.info(f"Verified: Visits message is '{visits_message}'")

            # Step 6: Verify "Paid lounge access available" message tag (shown when visits exhausted)
            message_tag = lounge_access_page.fetch_visits_message_tag()
            assert message_tag == FREE_VISITS_EXHAUSTED_MESSAGE_TAG, \
                f"Message tag should be '{FREE_VISITS_EXHAUSTED_MESSAGE_TAG}', but got: '{message_tag}'"
            logger.info(f"Verified: Message tag is '{message_tag}'")

            # Step 7: Verify to pay amount (should be paid access amount since free visits exhausted)
            to_pay_amount = lounge_access_page.fetch_to_pay_amount()
            assert to_pay_amount == FREE_VISITS_EXHAUSTED_TO_PAY_AMOUNT, \
                f"To pay amount should be '{FREE_VISITS_EXHAUSTED_TO_PAY_AMOUNT}', but got: '{to_pay_amount}'"
            logger.info(f"Verified: To pay amount is '{to_pay_amount}'")

            # Step 8: Click back to return to home page
            lounge_access_page.click_on_back_button()
            logger.info("Clicked on back button to return to home page")

            logger.info(f"Test case {testcase_id} completed successfully - Free visits exhausted scenario verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
