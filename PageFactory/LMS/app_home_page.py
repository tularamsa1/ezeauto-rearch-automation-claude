from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class HomePage(BasePage):

    btn_proceed = (By.ID, "com.ezetap.basicapp:id/btnProceedLMS")
    lbl_navigation = (By.ID, 'com.ezetap.basicapp:id/logoToolbar')
    btn_increment = (By.ID, "com.ezetap.basicapp:id/btnIncrement")
    btn_decrement = (By.ID, "com.ezetap.basicapp:id/btnDecrement")
    lbl_merchant_name = (By.ID, "com.ezetap.basicapp:id/tvMerchantName")
    lbl_username_label = (By.ID, "com.ezetap.basicapp:id/tvUsernameLabel")
    lbl_username = (By.ID, "com.ezetap.basicapp:id/tvUsername")
    lbl_additional_guest = (By.ID, "com.ezetap.basicapp:id/tvAdditionalGuest")
    lbl_guest_number = (By.ID, "com.ezetap.basicapp:id/tvGuestNumber")
    img_razorpay = (By.XPATH, '//android.widget.ImageView[@content-desc="Razorpay Payments"]')
    img_chair_list = (By.XPATH, '//android.widget.LinearLayout[@resource-id="com.ezetap.basicapp:id/chairList"]/android.widget.ImageView')
    btn_help = (By.ID, "com.ezetap.basicapp:id/rlHelp")


    def __init__(self, driver):
        """
        Initializes the HomePage with the given driver.
        :param driver: Appium WebDriver instance
        """
        super().__init__(driver)

    def click_on_proceed_button(self):
        """
        Waits for the proceed button to be visible and clicks on it.
        """
        try:
            logger.info("Clicking on proceed button")
            self.wait_for_element(self.btn_proceed)
            self.perform_click(self.btn_proceed)
            logger.info("Clicked on proceed button successfully")
        except Exception as e:
            logger.error(f"Failed to click on proceed button: {str(e)}")
            raise

    def fetch_proceed_button_text(self):
        """
        Fetches the text displayed on the proceed button.
        :return: Proceed button text as a string
        """
        try:
            logger.info("Fetching proceed button text")
            text = str(self.fetch_text(self.btn_proceed))
            logger.info(f"Proceed button text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch proceed button text: {str(e)}")
            raise

    def wait_for_navigation_to_load(self):
        """
        Waits for the navigation toolbar to be clickable, indicating the page has loaded.
        """
        try:
            logger.info("Waiting for home page navigation to load")
            self.wait_for_element_to_be_clickable(self.lbl_navigation)
            logger.info("Home page navigation loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load home page navigation: {str(e)}")
            raise

    def click_on_btnDecrement(self):
        """
        Waits for the decrement button to be visible and clicks on it.
        """
        try:
            logger.info("Clicking on decrement button")
            self.wait_for_element(self.btn_decrement)
            self.perform_click(self.btn_decrement)
            logger.info("Clicked on decrement button successfully")
        except Exception as e:
            logger.error(f"Failed to click on decrement button: {str(e)}")
            raise

    def click_on_btnIncrement(self):
        """
        Waits for the increment button to be visible and clicks on it.
        """
        try:
            logger.info("Clicking on increment button")
            self.wait_for_element(self.btn_increment)
            self.perform_click(self.btn_increment)
            logger.info("Clicked on increment button successfully")
        except Exception as e:
            logger.error(f"Failed to click on increment button: {str(e)}")
            raise

    def fetch_merchant_name(self):
        """
        Fetches the merchant name displayed on the home page.
        :return: Merchant name as a string
        """
        try:
            logger.info("Fetching merchant name")
            merchant_name = str(self.fetch_text(self.lbl_merchant_name))
            logger.info(f"Merchant name: {merchant_name}")
            return merchant_name
        except Exception as e:
            logger.error(f"Failed to fetch merchant name: {str(e)}")
            raise

    def fetch_username_label(self):
        """
        Fetches the username label displayed on the home page.
        :return: Username label as a string
        """
        try:
            logger.info("Fetching username label")
            username_label = str(self.fetch_text(self.lbl_username_label))
            logger.info(f"Username label: {username_label}")
            return username_label
        except Exception as e:
            logger.error(f"Failed to fetch username label: {str(e)}")
            raise

    def fetch_username(self):
        """
        Fetches the username displayed on the home page.
        :return: Username as a string
        """
        try:
            logger.info("Fetching username")
            username = str(self.fetch_text(self.lbl_username))
            logger.info(f"Username: {username}")
            return username
        except Exception as e:
            logger.error(f"Failed to fetch username: {str(e)}")
            raise

    def fetch_additional_guest(self):
        """
        Fetches the additional guest text displayed on the home page.
        :return: Additional guest text as a string
        """
        try:
            logger.info("Fetching additional guest text")
            additional_guest = str(self.fetch_text(self.lbl_additional_guest))
            logger.info(f"Additional guest text: {additional_guest}")
            return additional_guest
        except Exception as e:
            logger.error(f"Failed to fetch additional guest text: {str(e)}")
            raise

    def fetch_guest_number(self):
        """
        Fetches the guest number displayed on the home page.
        :return: Guest number as a string
        """
        try:
            logger.info("Fetching guest number")
            guest_number = str(self.fetch_text(self.lbl_guest_number))
            logger.info(f"Guest number: {guest_number}")
            return guest_number
        except Exception as e:
            logger.error(f"Failed to fetch guest number: {str(e)}")
            raise

    def is_guest_button_clickable(self, button_type: str):
        """
        Checks if the increment or decrement button is enabled/clickable.
        :param button_type: 'increment' or 'decrement'
        :return: True if button is clickable, False if disabled
        """
        try:
            logger.info(f"Checking if {button_type} button is clickable")
            button_locators = {
                'increment': self.btn_increment,
                'decrement': self.btn_decrement
            }
            locator = button_locators.get(button_type.lower())
            if locator is None:
                raise ValueError(f"Invalid button_type: {button_type}. Use 'increment' or 'decrement'.")
            button = self.wait_for_element(locator)
            is_enabled = button.is_enabled()
            logger.info(f"{button_type} button clickable: {is_enabled}")
            return is_enabled
        except ValueError as ve:
            logger.error(f"Invalid button type: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Failed to check if {button_type} button is clickable: {str(e)}")
            raise

    def is_razorpay_image_displayed(self):
        """
        Checks if the Razorpay Payments image is displayed on the home page.
        :return: True if image is displayed, False otherwise
        """
        try:
            logger.info("Checking if Razorpay image is displayed")
            element = self.wait_for_element(self.img_razorpay)
            is_displayed = element.is_displayed()
            logger.info(f"Razorpay image displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Razorpay image not found or not displayed: {str(e)}")
            return False

    def get_chair_image_count(self):
        """
        Counts the number of chair images displayed in the chairList.
        :return: Number of chair images as an integer
        """
        try:
            logger.info("Getting chair image count")
            elements = self.driver.find_elements(*self.img_chair_list)
            count = len(elements)
            logger.info(f"Chair image count: {count}")
            return count
        except Exception as e:
            logger.warning(f"Failed to get chair image count: {str(e)}")
            return 0

    def click_on_help_button(self):
        """
        Waits for the help button to be visible and clicks on it.
        """
        try:
            logger.info("Clicking on help button")
            self.wait_for_element(self.btn_help)
            self.perform_click(self.btn_help)
            logger.info("Clicked on help button successfully")
        except Exception as e:
            logger.error(f"Failed to click on help button: {str(e)}")
            raise
