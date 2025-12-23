from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage
from Utilities.EzeAutoLogger import EzeAutoLogger

logger = EzeAutoLogger.get_logger()


class LoungeAccessPage(BasePage):
    """
    Page object for the Lounge Access page in LMS application.
    Contains locators and methods for lounge access related functionality.
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

        # ============== PAGE HEADER ==============
        self.lbl_lounge_access_title = (By.XPATH, '//android.widget.TextView[@text="Lounge access"]')

        # ============== CARD DETAILS SECTION ==============
        self.lbl_card_holder_name = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvCardHolderName')
        self.lbl_card_name = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvCardName')
        self.img_card_brand_logo = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivCardBrandLogo')
        self.img_bank_logo = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivBankLogo')

        # ============== VISITS & GUESTS SECTION ==============
        self.lbl_visits_left = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvVisitsLeftr')
        self.lbl_visits_number = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvVisitsNumber')
        self.lbl_visits_message = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvVisitsMessage')
        self.lbl_visits_message_tag = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvVisitsMessageTag')
        self.img_visits_info = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivVisitsInfo')
        self.lbl_free_guest = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvFreeGuest')
        self.lbl_guests_number = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvGuestsNumber')
        self.img_guest_logo = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivGuestLogo')
        self.img_chair_logo = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivChairLogo')

        # ============== PAYMENT DETAILS SECTION ==============
        self.lbl_payment_details = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvPaymentDetails')

        # Free Access
        self.lbl_free_access = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvLabelFreeAccess')
        self.lbl_free_access_amount = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvFreeAccessAmount')

        # Paid Access
        self.lbl_paid_access = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvLabelPaidAccess')
        self.lbl_paid_access_amount = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvPaidAccessAmount')
        self.lbl_paid_access_tag = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvLabelPaidAccessTag')

        # To Pay
        self.lbl_to_pay = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvLabelToPay')
        self.lbl_to_pay_amount = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvToPayAmount')

        # ============== ACTION BUTTONS ==============
        self.btn_lms_back = (AppiumBy.ID, 'com.ezetap.service.demo:id/btnLmsBack')
        self.btn_pay = (AppiumBy.ID, 'com.ezetap.service.demo:id/btnPay')
        self.btn_cancel = (AppiumBy.ID, 'com.ezetap.service.demo:id/btnCancel')

    def is_lounge_access_page_displayed(self):
        """
        Checks if Lounge Access page is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if Lounge Access page is displayed")
            element = self.wait_for_element(self.lbl_lounge_access_title)
            is_displayed = element.is_displayed()
            logger.info(f"Lounge Access page displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Lounge Access page not displayed: {str(e)}")
            return False

    def fetch_lounge_access_title(self):
        """
        Fetches the Lounge Access title text.
        :return: Title text
        """
        try:
            logger.info("Fetching Lounge Access title")
            element = self.wait_for_element(self.lbl_lounge_access_title)
            title = element.text
            logger.info(f"Lounge Access title: {title}")
            return title
        except Exception as e:
            logger.error(f"Failed to fetch Lounge Access title: {str(e)}")
            return None

    def fetch_card_holder_name(self):
        """
        Fetches the card holder name.
        :return: Card holder name text
        """
        try:
            logger.info("Fetching card holder name")
            element = self.wait_for_element(self.lbl_card_holder_name)
            name = element.text
            logger.info(f"Card holder name: {name}")
            return name
        except Exception as e:
            logger.error(f"Failed to fetch card holder name: {str(e)}")
            return None

    def fetch_card_name(self):
        """
        Fetches the card name.
        :return: Card name text
        """
        try:
            logger.info("Fetching card name")
            element = self.wait_for_element(self.lbl_card_name)
            name = element.text
            logger.info(f"Card name: {name}")
            return name
        except Exception as e:
            logger.error(f"Failed to fetch card name: {str(e)}")
            return None

    def is_card_brand_logo_displayed(self):
        """
        Checks if the card brand logo is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if card brand logo is displayed")
            element = self.wait_for_element(self.img_card_brand_logo)
            is_displayed = element.is_displayed()
            logger.info(f"Card brand logo displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Card brand logo not found: {str(e)}")
            return False

    def is_bank_logo_displayed(self):
        """
        Checks if the bank logo is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if bank logo is displayed")
            element = self.wait_for_element(self.img_bank_logo)
            is_displayed = element.is_displayed()
            logger.info(f"Bank logo displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Bank logo not found: {str(e)}")
            return False

    def fetch_visits_message(self):
        """
        Fetches the visits message text.
        :return: Visits message text (e.g., "1/2 Free visit left in this quarter")
        """
        try:
            logger.info("Fetching visits message")
            element = self.wait_for_element(self.lbl_visits_message)
            message = element.text
            logger.info(f"Visits message: {message}")
            return message
        except Exception as e:
            logger.error(f"Failed to fetch visits message: {str(e)}")
            return None

    def fetch_visits_message_tag(self):
        """
        Fetches the visits message tag text.
        :return: Visits message tag text (e.g., "Paid lounge access available" for cards with no free visits)
        """
        try:
            logger.info("Fetching visits message tag")
            element = self.wait_for_element(self.lbl_visits_message_tag)
            message_tag = element.text
            logger.info(f"Visits message tag: {message_tag}")
            return message_tag
        except Exception as e:
            logger.error(f"Failed to fetch visits message tag: {str(e)}")
            return None

    def click_on_back_button(self):
        """
        Clicks on the LMS back button.
        """
        try:
            logger.info("Clicking on LMS back button")
            element = self.wait_for_element(self.btn_lms_back)
            element.click()
            logger.info("Clicked on LMS back button successfully")
        except Exception as e:
            logger.error(f"Failed to click on LMS back button: {str(e)}")
            raise

    def click_on_pay_button(self):
        """
        Clicks on the Pay button.
        """
        try:
            logger.info("Clicking on Pay button")
            element = self.wait_for_element(self.btn_pay)
            element.click()
            logger.info("Clicked on Pay button successfully")
        except Exception as e:
            logger.error(f"Failed to click on Pay button: {str(e)}")
            raise

    def click_on_cancel_button(self):
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

    # Visits and Guests Section Methods
    def fetch_visits_left_text(self):
        """
        Fetches the Visits Left label text.
        :return: Visits Left text
        """
        try:
            logger.info("Fetching visits left text")
            element = self.wait_for_element(self.lbl_visits_left)
            text = element.text
            logger.info(f"Visits left text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch visits left text: {str(e)}")
            return None

    def fetch_visits_number(self):
        """
        Fetches the visits number.
        :return: Visits number text
        """
        try:
            logger.info("Fetching visits number")
            element = self.wait_for_element(self.lbl_visits_number)
            number = element.text
            logger.info(f"Visits number: {number}")
            return number
        except Exception as e:
            logger.error(f"Failed to fetch visits number: {str(e)}")
            return None

    def fetch_free_guest_text(self):
        """
        Fetches the free guest text.
        :return: Free guest text
        """
        try:
            logger.info("Fetching free guest text")
            element = self.wait_for_element(self.lbl_free_guest)
            text = element.text
            logger.info(f"Free guest text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch free guest text: {str(e)}")
            return None

    def fetch_guests_number(self):
        """
        Fetches the guests number.
        :return: Guests number text
        """
        try:
            logger.info("Fetching guests number")
            element = self.wait_for_element(self.lbl_guests_number)
            number = element.text
            logger.info(f"Guests number: {number}")
            return number
        except Exception as e:
            logger.error(f"Failed to fetch guests number: {str(e)}")
            return None

    # Free Access Section Methods
    def fetch_free_access_text(self):
        """
        Fetches the free access label text.
        :return: Free access text
        """
        try:
            logger.info("Fetching free access text")
            element = self.wait_for_element(self.lbl_free_access)
            text = element.text
            logger.info(f"Free access text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch free access text: {str(e)}")
            return None

    def fetch_free_access_amount(self):
        """
        Fetches the free access amount.
        :return: Free access amount text
        """
        try:
            logger.info("Fetching free access amount")
            element = self.wait_for_element(self.lbl_free_access_amount)
            amount = element.text
            logger.info(f"Free access amount: {amount}")
            return amount
        except Exception as e:
            logger.error(f"Failed to fetch free access amount: {str(e)}")
            return None

    def fetch_paid_access_text(self):
        """
        Fetches the paid access label text.
        :return: Paid access text
        """
        try:
            logger.info("Fetching paid access text")
            element = self.wait_for_element(self.lbl_paid_access)
            text = element.text
            logger.info(f"Paid access text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch paid access text: {str(e)}")
            return None

    def fetch_paid_access_amount(self):
        """
        Fetches the paid access amount.
        :return: Paid access amount text
        """
        try:
            logger.info("Fetching paid access amount")
            element = self.wait_for_element(self.lbl_paid_access_amount)
            amount = element.text
            logger.info(f"Paid access amount: {amount}")
            return amount
        except Exception as e:
            logger.error(f"Failed to fetch paid access amount: {str(e)}")
            return None

    def fetch_to_pay_text(self):
        """
        Fetches the to pay label text.
        :return: To pay text
        """
        try:
            logger.info("Fetching to pay text")
            element = self.wait_for_element(self.lbl_to_pay)
            text = element.text
            logger.info(f"To pay text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch to pay text: {str(e)}")
            return None

    def fetch_to_pay_amount(self):
        """
        Fetches the to pay amount.
        :return: To pay amount text
        """
        try:
            logger.info("Fetching to pay amount")
            element = self.wait_for_element(self.lbl_to_pay_amount)
            amount = element.text
            logger.info(f"To pay amount: {amount}")
            return amount
        except Exception as e:
            logger.error(f"Failed to fetch to pay amount: {str(e)}")
            return None

