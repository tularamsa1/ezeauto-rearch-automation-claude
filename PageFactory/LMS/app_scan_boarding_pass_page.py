"""
Page Object for Scan Boarding Pass Page
Contains locators and methods for the scan boarding pass screen elements
"""
from selenium.webdriver.common.by import By
from Utilities.EzeAutoLogger import EzeAutoLogger
from PageFactory.common_page_factory import CommonPageFactory


logger = EzeAutoLogger.set_logger(__name__)


class ScanBoardingPassPage(CommonPageFactory):
    """Page object class for the Scan Boarding Pass screen"""

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

        # ==================== Header Section ====================
        self.lbl_title = (By.ID, "com.ezetap.service.demo:id/tvTitle")
        self.btn_toolbar_back = (By.ID, "com.ezetap.service.demo:id/imgToolbarBack")

        # ==================== Scanner Section ====================
        self.view_scanner = (By.ID, "com.ezetap.service.demo:id/zxing_viewfinder_view")
        self.lbl_scan_count = (By.ID, "com.ezetap.service.demo:id/tvScanCount")
        self.lbl_scan_failed = (By.ID, "com.ezetap.service.demo:id/tvScanFailed")
        self.lbl_scanner_problem = (By.ID, "com.ezetap.service.demo:id/tvScannerProblem")
        self.btn_enter_pnr = (By.ID, "com.ezetap.service.demo:id/btnEnterPNR")

        # ==================== Action Buttons ====================
        self.btn_go_home = (By.ID, "com.ezetap.service.demo:id/btnGoHome")
        self.btn_view_details = (By.ID, "com.ezetap.service.demo:id/btnViewDetails")
        self.btn_done = (By.ID, "com.ezetap.service.demo:id/btnDone")

        # ==================== Footer Section ====================
        self.lbl_powered_by = (By.XPATH, "//android.widget.TextView[@text='Powered by']")
        self.img_powered_by_logo = (
            By.XPATH,
            "//android.widget.LinearLayout[@resource-id='com.ezetap.service.demo:id/imgPoweredByEzetap']"
            "/android.widget.ImageView"
        )

        # ==================== Enter PNR Dialog Section ====================
        self.img_enter_pnr = (By.ID, "com.ezetap.service.demo:id/ivEnterPNR")
        self.btn_scan_again = (By.ID, "com.ezetap.service.demo:id/btnScanAgain")
        self.lbl_pnr_instruction = (By.ID, "com.ezetap.service.demo:id/tvScannerProblem")
        self.txt_pnr_input = (By.ID, "com.ezetap.service.demo:id/etPnr")
        self.btn_done_pnr = (By.ID, "com.ezetap.service.demo:id/btnDonePnr")
        self.btn_close_pnr = (By.ID, "com.ezetap.service.demo:id/btnClosePNR")

        # ==================== Go Home Confirmation Dialog ====================
        self.img_flight_skip = (By.ID, "com.ezetap.service.demo:id/ivFlight")
        self.lbl_skip_title = (By.ID, "com.ezetap.service.demo:id/tvSkipTitle")
        self.lbl_skip_message = (By.ID, "com.ezetap.service.demo:id/tvSkipMessage")
        self.btn_go_home_skip = (By.ID, "com.ezetap.service.demo:id/btnGoHomeSkip")
        self.btn_continue_scanning = (By.ID, "com.ezetap.service.demo:id/btnCloseSkip")

    # ==================== Page Verification Methods ====================
    def is_scan_boarding_pass_page_displayed(self):
        """Check if scan boarding pass page is displayed"""
        try:
            self.wait_for_element_to_be_displayed(self.lbl_title)
            return True
        except Exception:
            logger.error("Scan Boarding Pass page is not displayed")
            return False

    # ==================== Header Methods ====================
    def fetch_title(self):
        """Fetch the page title text"""
        try:
            title = self.wait_for_element_to_be_displayed(self.lbl_title).text
            logger.info(f"Page title: {title}")
            return title
        except Exception:
            logger.error("Unable to fetch page title")
            return None

    def click_toolbar_back_button(self):
        """Click on the toolbar back button"""
        try:
            self.wait_for_element_and_click(self.btn_toolbar_back)
            logger.info("Clicked on toolbar back button")
        except Exception:
            logger.error("Unable to click on toolbar back button")
            raise

    # ==================== Scanner Methods ====================
    def is_scanner_viewfinder_displayed(self):
        """Check if scanner viewfinder is displayed"""
        try:
            self.wait_for_element_to_be_displayed(self.view_scanner)
            logger.info("Scanner viewfinder is displayed")
            return True
        except Exception:
            logger.error("Scanner viewfinder is not displayed")
            return False

    def fetch_scan_count(self):
        """Fetch the scan count text"""
        try:
            scan_count = self.wait_for_element_to_be_displayed(self.lbl_scan_count).text
            logger.info(f"Scan count: {scan_count}")
            return scan_count
        except Exception:
            logger.error("Unable to fetch scan count")
            return None

    def fetch_scan_failed_text(self):
        """Fetch the scan failed message text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.lbl_scan_failed).text
            logger.info(f"Scan failed text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch scan failed text")
            return None

    def fetch_scanner_problem_text(self):
        """Fetch the scanner problem message text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.lbl_scanner_problem).text
            logger.info(f"Scanner problem text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch scanner problem text")
            return None

    def click_enter_pnr_button(self):
        """Click on the Enter PNR button"""
        try:
            self.wait_for_element_and_click(self.btn_enter_pnr)
            logger.info("Clicked on Enter PNR button")
        except Exception:
            logger.error("Unable to click on Enter PNR button")
            raise

    def fetch_enter_pnr_button_text(self):
        """Fetch the Enter PNR button text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.btn_enter_pnr).text
            logger.info(f"Enter PNR button text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch Enter PNR button text")
            return None

    def is_enter_pnr_button_displayed(self, timeout=3):
        """Check if Enter PNR button is displayed (with short timeout for negative check)"""
        try:
            self.wait_for_element_to_be_displayed(self.btn_enter_pnr, timeout=timeout)
            logger.info("Enter PNR button is displayed")
            return True
        except Exception:
            logger.info("Enter PNR button is not displayed")
            return False

    # ==================== Action Button Methods ====================
    def click_go_home_button(self):
        """Click on the Go Home button"""
        try:
            self.wait_for_element_and_click(self.btn_go_home)
            logger.info("Clicked on Go Home button")
        except Exception:
            logger.error("Unable to click on Go Home button")
            raise

    def fetch_go_home_button_text(self):
        """Fetch the Go Home button text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.btn_go_home).text
            logger.info(f"Go Home button text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch Go Home button text")
            return None

    def click_view_details_button(self):
        """Click on the View Details button"""
        try:
            self.wait_for_element_and_click(self.btn_view_details)
            logger.info("Clicked on View Details button")
        except Exception:
            logger.error("Unable to click on View Details button")
            raise

    def click_done_button(self):
        """Click on the Done button"""
        try:
            self.wait_for_element_and_click(self.btn_done)
            logger.info("Clicked on Done button")
        except Exception:
            logger.error("Unable to click on Done button")
            raise

    def fetch_done_button_text(self):
        """Fetch the Done button text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.btn_done).text
            logger.info(f"Done button text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch Done button text")
            return None

    # ==================== Footer Methods ====================
    def fetch_powered_by_text(self):
        """Fetch the 'Powered by' text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.lbl_powered_by).text
            logger.info(f"Powered by text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch Powered by text")
            return None

    def is_powered_by_logo_displayed(self):
        """Check if the Powered by Ezetap logo is displayed"""
        try:
            self.wait_for_element_to_be_displayed(self.img_powered_by_logo)
            logger.info("Powered by Ezetap logo is displayed")
            return True
        except Exception:
            logger.error("Powered by Ezetap logo is not displayed")
            return False

    # ==================== Enter PNR Dialog Methods ====================
    def is_enter_pnr_dialog_displayed(self):
        """Check if Enter PNR dialog is displayed"""
        try:
            self.wait_for_element_to_be_displayed(self.img_enter_pnr)
            return True
        except Exception:
            logger.error("Enter PNR dialog is not displayed")
            return False

    def is_enter_pnr_image_displayed(self):
        """Check if Enter PNR image/icon is displayed"""
        try:
            self.wait_for_element_to_be_displayed(self.img_enter_pnr)
            logger.info("Enter PNR image is displayed")
            return True
        except Exception:
            logger.error("Enter PNR image is not displayed")
            return False

    def click_scan_again_button(self):
        """Click on the Scan Again button"""
        try:
            self.wait_for_element_and_click(self.btn_scan_again)
            logger.info("Clicked on Scan Again button")
        except Exception:
            logger.error("Unable to click on Scan Again button")
            raise

    def fetch_scan_again_button_text(self):
        """Fetch the Scan Again button text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.btn_scan_again).text
            logger.info(f"Scan Again button text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch Scan Again button text")
            return None

    def fetch_pnr_instruction_text(self):
        """Fetch the PNR instruction text (Enter 6 digit PNR number)"""
        try:
            text = self.wait_for_element_to_be_displayed(self.lbl_pnr_instruction).text
            logger.info(f"PNR instruction text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch PNR instruction text")
            return None

    def enter_pnr_number(self, pnr):
        """Enter PNR number in the input field"""
        try:
            pnr_field = self.wait_for_element_to_be_displayed(self.txt_pnr_input)
            pnr_field.clear()
            pnr_field.send_keys(pnr)
            logger.info(f"Entered PNR number: {pnr}")
        except Exception:
            logger.error(f"Unable to enter PNR number: {pnr}")
            raise

    def get_pnr_input_value(self):
        """Get the current value in PNR input field"""
        try:
            value = self.wait_for_element_to_be_displayed(self.txt_pnr_input).text
            logger.info(f"PNR input value: {value}")
            return value
        except Exception:
            logger.error("Unable to get PNR input value")
            return None

    def click_done_pnr_button(self):
        """Click on the Done button in PNR dialog"""
        try:
            self.wait_for_element_and_click(self.btn_done_pnr)
            logger.info("Clicked on Done PNR button")
        except Exception:
            logger.error("Unable to click on Done PNR button")
            raise

    def fetch_done_pnr_button_text(self):
        """Fetch the Done PNR button text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.btn_done_pnr).text
            logger.info(f"Done PNR button text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch Done PNR button text")
            return None

    def click_close_pnr_button(self):
        """Click on the Close button to dismiss PNR dialog"""
        try:
            self.wait_for_element_and_click(self.btn_close_pnr)
            logger.info("Clicked on Close PNR button")
        except Exception:
            logger.error("Unable to click on Close PNR button")
            raise

    # ==================== Go Home Confirmation Dialog Methods ====================
    def is_go_home_confirmation_displayed(self):
        """Check if Go Home confirmation dialog is displayed"""
        try:
            self.wait_for_element_to_be_displayed(self.lbl_skip_title)
            return True
        except Exception:
            logger.error("Go Home confirmation dialog is not displayed")
            return False

    def is_flight_icon_displayed(self):
        """Check if flight icon is displayed in confirmation dialog"""
        try:
            self.wait_for_element_to_be_displayed(self.img_flight_skip)
            logger.info("Flight icon is displayed")
            return True
        except Exception:
            logger.error("Flight icon is not displayed")
            return False

    def fetch_skip_title(self):
        """Fetch the skip/confirmation dialog title text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.lbl_skip_title).text
            logger.info(f"Skip dialog title: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch skip dialog title")
            return None

    def fetch_skip_message(self):
        """Fetch the skip/confirmation dialog message text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.lbl_skip_message).text
            logger.info(f"Skip dialog message: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch skip dialog message")
            return None

    def click_go_home_skip_button(self):
        """Click on Home button in confirmation dialog to go home"""
        try:
            self.wait_for_element_and_click(self.btn_go_home_skip)
            logger.info("Clicked on Home button in skip dialog")
        except Exception:
            logger.error("Unable to click on Home button in skip dialog")
            raise

    def fetch_go_home_skip_button_text(self):
        """Fetch the Home button text in confirmation dialog"""
        try:
            text = self.wait_for_element_to_be_displayed(self.btn_go_home_skip).text
            logger.info(f"Home skip button text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch Home skip button text")
            return None

    def click_continue_scanning_button(self):
        """Click on Continue scanning button to dismiss dialog"""
        try:
            self.wait_for_element_and_click(self.btn_continue_scanning)
            logger.info("Clicked on Continue scanning button")
        except Exception:
            logger.error("Unable to click on Continue scanning button")
            raise

    def fetch_continue_scanning_button_text(self):
        """Fetch the Continue scanning button text"""
        try:
            text = self.wait_for_element_to_be_displayed(self.btn_continue_scanning).text
            logger.info(f"Continue scanning button text: {text}")
            return text
        except Exception:
            logger.error("Unable to fetch Continue scanning button text")
            return None

