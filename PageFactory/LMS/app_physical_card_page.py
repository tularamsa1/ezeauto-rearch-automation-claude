from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class PhysicalCardPage(BasePage):

    # ============== PAGE HEADER ==============
    img_logo = (By.ID, "com.ezetap.service.demo:id/imgLogo")
    btn_back = (By.ID, "com.ezetap.service.demo:id/ibtnBack")

    # ============== PAYMENT STATUS SECTION ==============
    lbl_order_id_value = (By.ID, "com.ezetap.service.demo:id/tvOrderIdValue")
    lbl_status_details = (By.ID, "com.ezetap.service.demo:id/statusDetails")
    img_device_icon = (By.ID, "com.ezetap.service.demo:id/ivDeviceIcon")

    # ============== PAGE FOOTER ==============
    img_footer_logo = (By.ID, "com.ezetap.service.demo:id/ivFooterRzpLogoDefault")

    # ============== EXIT / TIMEOUT DIALOG ==============
    lbl_dialog_title = (By.ID, "com.ezetap.service.demo:id/dialogTitle")
    lbl_dialog_text = (By.ID, "com.ezetap.service.demo:id/dialogText")
    btn_no = (By.ID, "com.ezetap.service.demo:id/leftButton")
    btn_yes = (By.ID, "com.ezetap.service.demo:id/rightButton")
    btn_ok = (By.ID, "com.ezetap.service.demo:id/rightButton")

    def __init__(self, driver):
        """
        Initializes the PaymentPage with the given driver.
        :param driver: Appium WebDriver instance
        """
        super().__init__(driver)

    def is_logo_displayed(self):
        """
        Checks if the logo is displayed on payment page.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if logo is displayed on payment page")
            element = self.wait_for_element(self.img_logo)
            is_displayed = element.is_displayed()
            logger.info(f"Logo displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Logo not found: {str(e)}")
            return False

    def fetch_order_id_value(self):
        """
        Fetches the order ID value text.
        :return: Order ID value as a string
        """
        try:
            logger.info("Fetching order ID value")
            self.wait_for_element(self.lbl_order_id_value)
            text = str(self.fetch_text(self.lbl_order_id_value))
            logger.info(f"Order ID value: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch order ID value: {str(e)}")
            raise

    def fetch_status_details(self):
        """
        Fetches the status details text.
        :return: Status details as a string
        """
        try:
            logger.info("Fetching status details")
            self.wait_for_element(self.lbl_status_details)
            text = str(self.fetch_text(self.lbl_status_details))
            logger.info(f"Status details: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch status details: {str(e)}")
            raise

    def is_device_icon_displayed(self):
        """
        Checks if the device icon is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if device icon is displayed")
            element = self.wait_for_element(self.img_device_icon)
            is_displayed = element.is_displayed()
            logger.info(f"Device icon displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Device icon not found: {str(e)}")
            return False

    def is_footer_logo_displayed(self):
        """
        Checks if the footer Razorpay logo is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if footer logo is displayed")
            element = self.wait_for_element(self.img_footer_logo)
            is_displayed = element.is_displayed()
            logger.info(f"Footer logo displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Footer logo not found: {str(e)}")
            return False

    def click_back_button(self):
        """
        Clicks on the back button.
        """
        try:
            logger.info("Clicking on back button")
            self.wait_for_element(self.btn_back)
            self.perform_click(self.btn_back)
            logger.info("Clicked on back button successfully")
        except Exception as e:
            logger.error(f"Failed to click back button: {str(e)}")
            raise

    def fetch_dialog_title(self):
        """
        Fetches the exit dialog title.
        :return: Dialog title as a string
        """
        try:
            logger.info("Fetching dialog title")
            self.wait_for_element(self.lbl_dialog_title)
            text = str(self.fetch_text(self.lbl_dialog_title))
            logger.info(f"Dialog title: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch dialog title: {str(e)}")
            raise

    def fetch_dialog_text(self):
        """
        Fetches the exit dialog text.
        :return: Dialog text as a string
        """
        try:
            logger.info("Fetching dialog text")
            self.wait_for_element(self.lbl_dialog_text)
            text = str(self.fetch_text(self.lbl_dialog_text))
            logger.info(f"Dialog text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch dialog text: {str(e)}")
            raise

    def click_no_button(self):
        """
        Clicks on the NO button in exit dialog.
        """
        try:
            logger.info("Clicking on NO button")
            self.wait_for_element(self.btn_no)
            self.perform_click(self.btn_no)
            logger.info("Clicked on NO button successfully")
        except Exception as e:
            logger.error(f"Failed to click NO button: {str(e)}")
            raise

    def click_yes_button(self):
        """
        Clicks on the YES button in exit dialog.
        """
        try:
            logger.info("Clicking on YES button")
            self.wait_for_element(self.btn_yes)
            self.perform_click(self.btn_yes)
            logger.info("Clicked on YES button successfully")
        except Exception as e:
            logger.error(f"Failed to click YES button: {str(e)}")
            raise

    def fetch_no_button_text(self):
        """
        Fetches the NO button text.
        :return: NO button text as a string
        """
        try:
            logger.info("Fetching NO button text")
            self.wait_for_element(self.btn_no)
            text = str(self.fetch_text(self.btn_no))
            logger.info(f"NO button text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch NO button text: {str(e)}")
            raise

    def fetch_yes_button_text(self):
        """
        Fetches the YES button text.
        :return: YES button text as a string
        """
        try:
            logger.info("Fetching YES button text")
            self.wait_for_element(self.btn_yes)
            text = str(self.fetch_text(self.btn_yes))
            logger.info(f"YES button text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch YES button text: {str(e)}")
            raise

    def wait_for_timeout_dialog(self, timeout=150):
        """
        Waits for the timeout dialog to appear after idle timer expires.
        :param timeout: Maximum wait time in seconds (default 150 = 2.5 min)
        :return: True if dialog appears, raises exception otherwise
        """
        try:
            logger.info(f"Waiting for timeout dialog (max {timeout} seconds)")
            self.wait_for_element(self.lbl_dialog_title, time=timeout)
            logger.info("Timeout dialog appeared")
            return True
        except Exception as e:
            logger.error(f"Timeout dialog did not appear: {str(e)}")
            raise

    def fetch_ok_button_text(self):
        """
        Fetches the OK button text.
        :return: OK button text as a string
        """
        try:
            logger.info("Fetching OK button text")
            self.wait_for_element(self.btn_ok)
            text = str(self.fetch_text(self.btn_ok))
            logger.info(f"OK button text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch OK button text: {str(e)}")
            raise

    def click_ok_button(self):
        """
        Clicks on the OK button in timeout dialog.
        """
        try:
            logger.info("Clicking on OK button")
            self.wait_for_element(self.btn_ok)
            self.perform_click(self.btn_ok)
            logger.info("Clicked on OK button successfully")
        except Exception as e:
            logger.error(f"Failed to click OK button: {str(e)}")
            raise

