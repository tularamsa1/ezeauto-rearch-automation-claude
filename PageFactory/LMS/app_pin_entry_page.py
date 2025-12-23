from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.mpos.app_base_page import BasePage
from Utilities.EzeAutoLogger import EzeAutoLogger

logger = EzeAutoLogger.get_logger()


class PinEntryPage(BasePage):
    """
    Page object for the PIN Entry page (PAX daemon).
    Contains locators and methods for PIN input functionality.
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

        # ============== PIN ENTRY CONTAINER ==============
        self.lyt_pin_parent_panel = (AppiumBy.ID, 'com.pax.daemon:id/input_pin_parent_panel')
        self.txt_pin_content = (AppiumBy.ID, 'com.pax.daemon:id/input_pin_content')

        # ============== NUMBER PAD (0-9) ==============
        self.btn_zero = (AppiumBy.ID, 'com.pax.daemon:id/btn_zero')
        self.btn_one = (AppiumBy.ID, 'com.pax.daemon:id/btn_one')
        self.btn_two = (AppiumBy.ID, 'com.pax.daemon:id/btn_two')
        self.btn_three = (AppiumBy.ID, 'com.pax.daemon:id/btn_three')
        self.btn_four = (AppiumBy.ID, 'com.pax.daemon:id/btn_four')
        self.btn_five = (AppiumBy.ID, 'com.pax.daemon:id/btn_five')
        self.btn_six = (AppiumBy.ID, 'com.pax.daemon:id/btn_six')
        self.btn_seven = (AppiumBy.ID, 'com.pax.daemon:id/btn_seven')
        self.btn_eight = (AppiumBy.ID, 'com.pax.daemon:id/btn_eight')
        self.btn_nine = (AppiumBy.ID, 'com.pax.daemon:id/btn_nine')

        # ============== CONTROL BUTTONS ==============
        self.btn_cancel = (AppiumBy.ID, 'com.pax.daemon:id/btn_cancel')
        self.btn_clear = (AppiumBy.ID, 'com.pax.daemon:id/btn_clear')
        self.btn_sure = (AppiumBy.ID, 'com.pax.daemon:id/btn_sure')

        # ============== NON-INTERACTIVE ELEMENTS ==============
        self.btn_func = (AppiumBy.ID, 'com.pax.daemon:id/btn_func')
        self.btn_abc = (AppiumBy.ID, 'com.pax.daemon:id/btn_abc')

        # ============== TRANSACTION DECLINED DIALOG ==============
        self.lbl_txn_declined_title = (AppiumBy.ID, 'com.ezetap.service.demo:id/dialogTitle')
        self.lbl_txn_declined_text = (AppiumBy.ID, 'com.ezetap.service.demo:id/dialogText')
        self.btn_txn_declined_ok = (AppiumBy.ID, 'com.ezetap.service.demo:id/rightButton')

    def is_pin_entry_page_displayed(self):
        """
        Checks if PIN entry page is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if PIN entry page is displayed")
            element = self.wait_for_element(self.lyt_pin_parent_panel)
            is_displayed = element.is_displayed()
            logger.info(f"PIN entry page displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"PIN entry page not displayed: {str(e)}")
            return False

    def get_pin_content(self):
        """
        Gets the current PIN content displayed.
        :return: PIN content text
        """
        try:
            logger.info("Getting PIN content")
            element = self.wait_for_element(self.txt_pin_content)
            content = element.text
            logger.info(f"PIN content: {content}")
            return content
        except Exception as e:
            logger.error(f"Failed to get PIN content: {str(e)}")
            return None

    def click_number_button(self, number: int):
        """
        Clicks on a number button (0-9).
        :param number: Number to click (0-9)
        """
        try:
            logger.info(f"Clicking on number button: {number}")
            button_map = {
                0: self.btn_zero,
                1: self.btn_one,
                2: self.btn_two,
                3: self.btn_three,
                4: self.btn_four,
                5: self.btn_five,
                6: self.btn_six,
                7: self.btn_seven,
                8: self.btn_eight,
                9: self.btn_nine
            }
            if number not in button_map:
                raise ValueError(f"Invalid number: {number}. Must be 0-9.")
            element = self.wait_for_element(button_map[number])
            element.click()
            logger.info(f"Clicked on number button {number} successfully")
        except Exception as e:
            logger.error(f"Failed to click on number button {number}: {str(e)}")
            raise

    def enter_pin(self, pin: str):
        """
        Enters a PIN by clicking number buttons sequentially.
        :param pin: PIN to enter (string of digits)
        """
        try:
            logger.info(f"Entering PIN of length: {len(pin)}")
            for digit in pin:
                self.click_number_button(int(digit))
            logger.info("PIN entered successfully")
        except Exception as e:
            logger.error(f"Failed to enter PIN: {str(e)}")
            raise

    def click_cancel_button(self):
        """
        Clicks on the Cancel button.
        """
        try:
            logger.info("Clicking on Cancel button")
            element = self.wait_for_element(self.btn_cancel)
            element.click()
            logger.info("Clicked on Cancel button successfully")
        except Exception as e:
            logger.error(f"Failed to click on Cancel button: {str(e)}")
            raise

    def click_clear_button(self):
        """
        Clicks on the Clear button.
        """
        try:
            logger.info("Clicking on Clear button")
            element = self.wait_for_element(self.btn_clear)
            element.click()
            logger.info("Clicked on Clear button successfully")
        except Exception as e:
            logger.error(f"Failed to click on Clear button: {str(e)}")
            raise

    def click_sure_button(self):
        """
        Clicks on the Sure/Confirm button.
        """
        try:
            logger.info("Clicking on Sure button")
            element = self.wait_for_element(self.btn_sure)
            element.click()
            logger.info("Clicked on Sure button successfully")
        except Exception as e:
            logger.error(f"Failed to click on Sure button: {str(e)}")
            raise

    def is_txn_declined_dialog_displayed(self):
        """
        Checks if transaction declined dialog is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if transaction declined dialog is displayed")
            element = self.wait_for_element(self.lbl_txn_declined_title)
            is_displayed = element.is_displayed()
            logger.info(f"Transaction declined dialog displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Transaction declined dialog not displayed: {str(e)}")
            return False

    def fetch_txn_declined_title(self):
        """
        Fetches the transaction declined dialog title.
        :return: Title text (e.g., 'TXN_DECLINED')
        """
        try:
            logger.info("Fetching transaction declined title")
            element = self.wait_for_element(self.lbl_txn_declined_title)
            title = element.text
            logger.info(f"Transaction declined title: {title}")
            return title
        except Exception as e:
            logger.error(f"Failed to fetch transaction declined title: {str(e)}")
            return None

    def fetch_txn_declined_text(self):
        """
        Fetches the transaction declined dialog text.
        :return: Dialog text (e.g., 'Transaction declined')
        """
        try:
            logger.info("Fetching transaction declined text")
            element = self.wait_for_element(self.lbl_txn_declined_text)
            text = element.text
            logger.info(f"Transaction declined text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch transaction declined text: {str(e)}")
            return None

    def click_txn_declined_ok_button(self):
        """
        Clicks on the OK button in transaction declined dialog.
        """
        try:
            logger.info("Clicking on transaction declined OK button")
            element = self.wait_for_element(self.btn_txn_declined_ok)
            element.click()
            logger.info("Clicked on transaction declined OK button successfully")
        except Exception as e:
            logger.error(f"Failed to click on transaction declined OK button: {str(e)}")
            raise

