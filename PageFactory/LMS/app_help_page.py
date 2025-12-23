from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class HelpPage(BasePage):

    # ============== PAGE HEADER ==============
    lbl_help_title = (By.ID, "com.ezetap.basicapp:id/tvTitle")
    btn_back = (By.ID, "com.ezetap.basicapp:id/imgToolbarBack")

    # ============== HELP CONTENT ==============
    lbl_help_question = (By.ID, "com.ezetap.basicapp:id/tvHelpTextQuestion")

    # ============== SUPPORT SECTION ==============
    lbl_call_razorpay_support = (By.XPATH, '//android.widget.TextView[@text="Call Razorpay Support"]')
    btn_call_support = (By.ID, "com.ezetap.basicapp:id/btnCallSupport")

    def __init__(self, driver):
        """
        Initializes the HelpPage with the given driver.
        :param driver: Appium WebDriver instance
        """
        super().__init__(driver)

    def fetch_help_title(self):
        """
        Fetches the title displayed on the Help & Support page.
        :return: Help page title as a string
        """
        try:
            logger.info("Fetching help page title")
            self.wait_for_element(self.lbl_help_title)
            title = str(self.fetch_text(self.lbl_help_title))
            logger.info(f"Help page title: {title}")
            return title
        except Exception as e:
            logger.error(f"Failed to fetch help page title: {str(e)}")
            raise

    def fetch_help_question_text(self):
        """
        Fetches the help question text displayed on the Help & Support page.
        :return: Help question text as a string
        """
        try:
            logger.info("Fetching help question text")
            self.wait_for_element(self.lbl_help_question)
            question_text = str(self.fetch_text(self.lbl_help_question))
            logger.info(f"Help question text: {question_text}")
            return question_text
        except Exception as e:
            logger.error(f"Failed to fetch help question text: {str(e)}")
            raise

    def click_on_back_button(self):
        """
        Waits for the back button to be visible and clicks on it to navigate back.
        """
        try:
            logger.info("Clicking on back button")
            self.wait_for_element(self.btn_back)
            self.perform_click(self.btn_back)
            logger.info("Clicked on back button successfully")
        except Exception as e:
            logger.error(f"Failed to click on back button: {str(e)}")
            raise

    def is_help_page_displayed(self):
        """
        Checks if the Help & Support page is displayed by verifying the title.
        :return: True if help page is displayed, False otherwise
        """
        try:
            logger.info("Checking if Help page is displayed")
            self.wait_for_element(self.lbl_help_title)
            title = str(self.fetch_text(self.lbl_help_title))
            is_displayed = title == "Help & Support"
            logger.info(f"Help page displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Help page not displayed: {str(e)}")
            return False

    def fetch_call_support_number(self):
        """
        Fetches the support phone number displayed on the Call Support button.
        :return: Support phone number as a string
        """
        try:
            logger.info("Fetching call support number")
            self.wait_for_element(self.btn_call_support)
            number = str(self.fetch_text(self.btn_call_support))
            logger.info(f"Call support number: {number}")
            return number
        except Exception as e:
            logger.error(f"Failed to fetch call support number: {str(e)}")
            raise

    def fetch_call_razorpay_support_text(self):
        """
        Fetches the 'Call Razorpay Support' label text.
        :return: Label text as a string
        """
        try:
            logger.info("Fetching call razorpay support text")
            self.wait_for_element(self.lbl_call_razorpay_support)
            text = str(self.fetch_text(self.lbl_call_razorpay_support))
            logger.info(f"Call Razorpay Support text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch call razorpay support text: {str(e)}")
            raise

    def click_on_call_support_button(self):
        """
        Waits for the call support button to be visible and clicks on it.
        """
        try:
            logger.info("Clicking on call support button")
            self.wait_for_element(self.btn_call_support)
            self.perform_click(self.btn_call_support)
            logger.info("Clicked on call support button successfully")
        except Exception as e:
            logger.error(f"Failed to click on call support button: {str(e)}")
            raise

    def is_call_support_button_displayed(self):
        """
        Checks if the call support button is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if call support button is displayed")
            element = self.wait_for_element(self.btn_call_support)
            is_displayed = element.is_displayed()
            logger.info(f"Call support button displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Call support button not found: {str(e)}")
            return False

