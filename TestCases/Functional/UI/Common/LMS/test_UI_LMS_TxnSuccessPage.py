import sys
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables

from PageFactory.LMS.app_home_page import HomePage
from PageFactory.LMS.app_lounge_access_page import LoungeAccessPage
from PageFactory.LMS.app_pin_entry_page import PinEntryPage
from PageFactory.LMS.app_txn_success_page import TxnSuccessPage
from PageFactory.LMS.app_txn_details_page import TxnDetailsPage
from PageFactory.LMS.app_scan_boarding_pass_page import ScanBoardingPassPage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_card_page import CardPage

from Utilities import ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

# ============== CONSTANTS ==============
# Card type to use for successful transaction (must be a valid test card with correct PIN)
# TODO: Update with actual card type and PIN for successful transaction
TXN_SUCCESS_TEST_CARD_TYPE = "EMV_WITH_PIN_VISA_CREDIT_417666"
TXN_SUCCESS_TEST_PIN = "1234"  # TODO: Update with correct PIN for the test card

# Expected values
EXPECTED_TXN_DETAILS_HEADER = "Transaction Details"
EXPECTED_E_RECEIPT_CAPTION = "Get digital receipt on phone no."
EXPECTED_GO_GREEN_TEXT = "Go green, save paper & nature"
EXPECTED_SCAN_BOARDING_PASS_TEXT = "Scan Boarding Pass"


def navigate_to_txn_success_page(home_page, login_page, card_page, lounge_access_page, 
                                  pin_entry_page, app_username, app_password):
    """
    Helper function to navigate from home to transaction success page.
    Performs: Login -> Proceed -> Card Selection -> Pay -> PIN Entry -> Success
    """
    # Check if already logged in, if not perform login
    try:
        home_page.wait_for_navigation_to_load()
        logger.info("Already logged in - Home page loaded directly")
    except Exception:
        logger.info(f"Not logged in - Performing login with username: {app_username}")
        login_page.perform_login_for_auto_login_functionality(app_username, app_password, Pax_Device=True)
        home_page.wait_for_navigation_to_load()
        logger.info("App homepage loaded successfully after login")

    # Navigate: Home -> Proceed -> Card -> Lounge -> Pay -> PIN -> Success
    home_page.click_on_proceed_button()
    logger.info("Clicked on Proceed button")

    logger.info(f"Selecting card type: {TXN_SUCCESS_TEST_CARD_TYPE}")
    card_page.select_cardtype(text=TXN_SUCCESS_TEST_CARD_TYPE)
    logger.info(f"Selected card type: {TXN_SUCCESS_TEST_CARD_TYPE}")

    lounge_access_page.click_on_pay_button()
    logger.info("Clicked on Pay button")

    # assert pin_entry_page.is_pin_entry_page_displayed(), "PIN Entry page should be displayed"
    # logger.info("PIN Entry page is displayed")

    # # Enter PIN and confirm
    # pin_entry_page.enter_pin(TXN_SUCCESS_TEST_PIN)
    # logger.info(f"Entered PIN")

    # pin_entry_page.click_sure_button()
    # logger.info("Clicked Sure button to confirm PIN")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_026():
    """
    sub_feature_code: UI_Common_PM_LMS_Txn_Success_Page_UI_Elements_Verification
    file_name: test_UI_Common_LMS_TxnSuccessPage.py
    Sub Feature Description: Verify all UI elements on Transaction Success page including
                            payment type image, amount, buttons, and footer
    TC naming code description: 100: Payment Method, 1010: LMS, 026: TC026
    Prerequisite: Successful transaction (valid card with correct PIN)
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
            card_page = CardPage(driver=app_driver)
            lounge_access_page = LoungeAccessPage(driver=app_driver)
            pin_entry_page = PinEntryPage(driver=app_driver)
            txn_success_page = TxnSuccessPage(driver=app_driver)

            # Navigate to Transaction Success page
            navigate_to_txn_success_page(home_page, login_page, card_page, lounge_access_page,
                                         pin_entry_page, app_username, app_password)

            # Step 1: Verify Transaction Success page is displayed
            assert txn_success_page.is_txn_success_page_displayed(), \
                "Transaction Success page should be displayed"
            logger.info("Verified: Transaction Success page is displayed")

            # Step 2: Verify payment type image is displayed
            assert txn_success_page.is_payment_type_image_displayed(), \
                "Payment type image should be displayed"
            logger.info("Verified: Payment type image is displayed")

            # Step 3: Verify transaction amount is displayed
            txn_amount = txn_success_page.fetch_txn_amount()
            assert txn_amount is not None and txn_amount != "", \
                "Transaction amount should be displayed"
            logger.info(f"Verified: Transaction amount is '{txn_amount}'")

            # Step 4: Verify e-receipt caption
            e_receipt_caption = txn_success_page.fetch_e_receipt_caption()
            assert e_receipt_caption == EXPECTED_E_RECEIPT_CAPTION, \
                f"E-receipt caption should be '{EXPECTED_E_RECEIPT_CAPTION}', but got: '{e_receipt_caption}'"
            logger.info(f"Verified: E-receipt caption is '{e_receipt_caption}'")

            # Step 5: Verify Go Green text
            go_green_text = txn_success_page.fetch_go_green_text()
            assert go_green_text == EXPECTED_GO_GREEN_TEXT, \
                f"Go green text should be '{EXPECTED_GO_GREEN_TEXT}', but got: '{go_green_text}'"
            logger.info(f"Verified: Go green text is '{go_green_text}'")

            # Step 6: Verify footer Razorpay logo is displayed
            assert txn_success_page.is_footer_rzp_logo_displayed(), \
                "Footer Razorpay logo should be displayed"
            logger.info("Verified: Footer Razorpay logo is displayed")

            # Step 7: Verify Scan Boarding Pass button text
            scan_btn_text = txn_success_page.fetch_scan_boarding_pass_button_text()
            assert scan_btn_text == EXPECTED_SCAN_BOARDING_PASS_TEXT, \
                f"Scan Boarding Pass button text should be '{EXPECTED_SCAN_BOARDING_PASS_TEXT}', but got: '{scan_btn_text}'"
            logger.info(f"Verified: Scan Boarding Pass button text is '{scan_btn_text}'")

            logger.info(f"Test case {testcase_id} completed successfully - Transaction Success UI verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_027():
    """
    sub_feature_code: UI_Common_PM_LMS_Txn_Success_Page_View_Details_Navigation
    file_name: test_UI_Common_LMS_TxnSuccessPage.py
    Sub Feature Description: Verify View Details button opens Transaction Details dialog
                            with correct header
    TC naming code description: 100: Payment Method, 1010: LMS, 027: TC027
    Prerequisite: Successful transaction (valid card with correct PIN)
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
            card_page = CardPage(driver=app_driver)
            lounge_access_page = LoungeAccessPage(driver=app_driver)
            pin_entry_page = PinEntryPage(driver=app_driver)
            txn_success_page = TxnSuccessPage(driver=app_driver)
            txn_details_page = TxnDetailsPage(driver=app_driver)

            # Navigate to Transaction Success page
            navigate_to_txn_success_page(home_page, login_page, card_page, lounge_access_page,
                                         pin_entry_page, app_username, app_password)

            # Step 1: Verify Transaction Success page is displayed
            assert txn_success_page.is_txn_success_page_displayed(), \
                "Transaction Success page should be displayed"
            logger.info("Verified: Transaction Success page is displayed")

            # Step 2: Click View Details button
            txn_success_page.click_view_details_button()
            logger.info("Clicked View Details button")

            # Step 3: Verify Transaction Details dialog is displayed
            assert txn_details_page.is_txn_details_page_displayed(), \
                "Transaction Details dialog should be displayed"
            logger.info("Verified: Transaction Details dialog is displayed")

            # Step 4: Verify Transaction Details header
            header = txn_details_page.fetch_txn_header()
            assert header == EXPECTED_TXN_DETAILS_HEADER, \
                f"Header should be '{EXPECTED_TXN_DETAILS_HEADER}', but got: '{header}'"
            logger.info(f"Verified: Transaction Details header is '{header}'")

            # Step 5: Click Close to dismiss the dialog
            txn_details_page.click_close_button()
            logger.info("Clicked Close button to dismiss Transaction Details")

            # Step 6: Verify return to Transaction Success page
            assert txn_success_page.is_txn_success_page_displayed(), \
                "Should return to Transaction Success page after closing details"
            logger.info("Verified: Returned to Transaction Success page")

            # Step 7: Click Scan Boarding Pass to continue
            txn_success_page.click_scan_boarding_pass_button()
            logger.info("Clicked Scan Boarding Pass button to continue")

            logger.info(f"Test case {testcase_id} completed successfully - View Details navigation verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_028():
    """
    sub_feature_code: UI_Common_PM_LMS_Txn_Details_Fields_Verification
    file_name: test_UI_Common_LMS_TxnSuccessPage.py
    Sub Feature Description: Verify all transaction detail fields are displayed with values
                            (Customer Name, Date, Transaction Id, Status, Card, etc.)
    TC naming code description: 100: Payment Method, 1010: LMS, 028: TC028
    Prerequisite: Successful transaction (valid card with correct PIN)
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
            card_page = CardPage(driver=app_driver)
            lounge_access_page = LoungeAccessPage(driver=app_driver)
            pin_entry_page = PinEntryPage(driver=app_driver)
            txn_success_page = TxnSuccessPage(driver=app_driver)
            txn_details_page = TxnDetailsPage(driver=app_driver)

            # Navigate to Transaction Success page
            navigate_to_txn_success_page(home_page, login_page, card_page, lounge_access_page,
                                         pin_entry_page, app_username, app_password)

            # Step 1: Verify Transaction Success page is displayed
            assert txn_success_page.is_txn_success_page_displayed(), \
                "Transaction Success page should be displayed"
            logger.info("Verified: Transaction Success page is displayed")

            # Step 2: Click View Details button
            txn_success_page.click_view_details_button()
            logger.info("Clicked View Details button")

            # Step 3: Verify Transaction Details dialog is displayed
            assert txn_details_page.is_txn_details_page_displayed(), \
                "Transaction Details dialog should be displayed"
            logger.info("Verified: Transaction Details dialog is displayed")

            # Step 4: Verify Customer Name field has value
            customer_name = txn_details_page.fetch_customer_name_value()
            assert customer_name is not None and customer_name != "", \
                "Customer Name should have a value"
            logger.info(f"Verified: Customer Name is '{customer_name}'")

            # Step 5: Verify Date field has value
            date_value = txn_details_page.fetch_date_value()
            assert date_value is not None and date_value != "", \
                "Date should have a value"
            logger.info(f"Verified: Date is '{date_value}'")

            # Step 6: Verify Transaction Id field has value
            txn_id = txn_details_page.fetch_transaction_id_value()
            assert txn_id is not None and txn_id != "", \
                "Transaction Id should have a value"
            logger.info(f"Verified: Transaction Id is '{txn_id}'")

            # Step 7: Verify Status field has value
            status = txn_details_page.fetch_status_value()
            assert status is not None and status != "", \
                "Status should have a value"
            logger.info(f"Verified: Status is '{status}'")

            # Step 8: Verify Card field has value
            card = txn_details_page.fetch_card_value()
            assert card is not None and card != "", \
                "Card should have a value"
            logger.info(f"Verified: Card is '{card}'")

            # Step 9: Verify TID field has value
            tid = txn_details_page.fetch_tid_value()
            assert tid is not None and tid != "", \
                "TID should have a value"
            logger.info(f"Verified: TID is '{tid}'")

            # Step 10: Verify MID field has value
            mid = txn_details_page.fetch_mid_value()
            assert mid is not None and mid != "", \
                "MID should have a value"
            logger.info(f"Verified: MID is '{mid}'")

            # Step 11: Click Close to dismiss the dialog
            txn_details_page.click_close_button()
            logger.info("Clicked Close button to dismiss Transaction Details")

            # Step 12: Click Scan Boarding Pass to continue
            txn_success_page.click_scan_boarding_pass_button()
            logger.info("Clicked Scan Boarding Pass button to continue")

            logger.info(f"Test case {testcase_id} completed successfully - Transaction details fields verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_1010_029():
    """
    sub_feature_code: UI_Common_PM_LMS_Txn_Success_Page_Scan_Boarding_Pass_Navigation
    file_name: test_UI_Common_LMS_TxnSuccessPage.py
    Sub Feature Description: Verify Scan Boarding Pass button navigates to Scan Boarding Pass page
    TC naming code description: 100: Payment Method, 1010: LMS, 029: TC029
    Prerequisite: Successful transaction (valid card with correct PIN)
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
            card_page = CardPage(driver=app_driver)
            lounge_access_page = LoungeAccessPage(driver=app_driver)
            pin_entry_page = PinEntryPage(driver=app_driver)
            txn_success_page = TxnSuccessPage(driver=app_driver)
            scan_boarding_pass_page = ScanBoardingPassPage(driver=app_driver)

            # Navigate to Transaction Success page
            navigate_to_txn_success_page(home_page, login_page, card_page, lounge_access_page,
                                         pin_entry_page, app_username, app_password)

            # Step 1: Verify Transaction Success page is displayed
            assert txn_success_page.is_txn_success_page_displayed(), \
                "Transaction Success page should be displayed"
            logger.info("Verified: Transaction Success page is displayed")

            # Step 2: Click Scan Boarding Pass button
            txn_success_page.click_scan_boarding_pass_button()
            logger.info("Clicked Scan Boarding Pass button")

            # Step 3: Verify Scan Boarding Pass page is displayed
            assert scan_boarding_pass_page.is_scan_boarding_pass_page_displayed(), \
                "Scan Boarding Pass page should be displayed"
            logger.info("Verified: Scan Boarding Pass page is displayed")

            # Step 4: Verify page title
            title = scan_boarding_pass_page.fetch_title()
            assert title == "Scan Boarding Pass", \
                f"Title should be 'Scan Boarding Pass', but got: '{title}'"
            logger.info(f"Verified: Page title is '{title}'")

            # Step 5: Click Go Home to return to home page
            scan_boarding_pass_page.click_go_home_button()
            logger.info("Clicked Go Home button")

            # Step 6: Click Home on confirmation dialog
            scan_boarding_pass_page.click_go_home_skip_button()
            logger.info("Clicked Home button on confirmation dialog")

            # Step 7: Verify return to home page
            home_page.wait_for_navigation_to_load()
            logger.info("Verified: Returned to home page")

            logger.info(f"Test case {testcase_id} completed successfully - Scan Boarding Pass navigation verified")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution----------
    finally:
        Configuration.executeFinallyBlock(testcase_id)

