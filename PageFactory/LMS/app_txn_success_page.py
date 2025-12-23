from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage
from Utilities.EzeAutoLogger import EzeAutoLogger

logger = EzeAutoLogger.get_logger()


class TxnSuccessPage(BasePage):
    """
    Page object for the Transaction Success page in LMS application.
    Contains locators and methods for transaction success screen functionality.
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

        # ============== TRANSACTION STATUS SECTION ==============
        self.img_payment_type = (AppiumBy.ID, 'com.ezetap.service.demo:id/imgPaymentType')
        self.lbl_txn_amount = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvTxnAmount')
        self.btn_view_details = (AppiumBy.ID, 'com.ezetap.service.demo:id/btnViewDetails')

        # ============== ACTION BUTTONS ==============
        self.btn_scan_boarding_pass = (AppiumBy.ID, 'com.ezetap.service.demo:id/btnScanBoardingPass')

        # ============== PRINT RECEIPT OPTIONS ==============
        self.btn_print_customer_receipt = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvPrintCustomerReceiptNew')
        self.btn_print_merchant_receipt = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvPrintMerchantReceiptNew')

        # ============== E-RECEIPT SECTION ==============
        self.lbl_e_receipt_text = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvEReceiptText')
        self.lbl_e_receipt_caption = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvEReceiptCaption1')
        self.img_e_receipt_icon = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivEReceiptIcon')
        self.img_e_receipt_icon2 = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivEReceiptIcon2')

        # ============== GO GREEN MESSAGE ==============
        self.lbl_go_green_text = (By.XPATH, '//android.widget.TextView[@text="Go green, save paper & nature"]')

        # ============== PAGE FOOTER ==============
        self.img_footer_rzp_logo = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivFooterRzpLogoDefault')

    def is_txn_success_page_displayed(self):
        """
        Checks if Transaction Success page is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if Transaction Success page is displayed")
            element = self.wait_for_element(self.img_payment_type)
            is_displayed = element.is_displayed()
            logger.info(f"Transaction Success page displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Transaction Success page not displayed: {str(e)}")
            return False

    def is_payment_type_image_displayed(self):
        """
        Checks if payment type image is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if payment type image is displayed")
            element = self.wait_for_element(self.img_payment_type)
            is_displayed = element.is_displayed()
            logger.info(f"Payment type image displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Payment type image not found: {str(e)}")
            return False

    def fetch_txn_amount(self):
        """
        Fetches the transaction amount.
        :return: Transaction amount text
        """
        try:
            logger.info("Fetching transaction amount")
            element = self.wait_for_element(self.lbl_txn_amount)
            amount = element.text
            logger.info(f"Transaction amount: {amount}")
            return amount
        except Exception as e:
            logger.error(f"Failed to fetch transaction amount: {str(e)}")
            return None

    def click_view_details_button(self):
        """
        Clicks on the View Details button.
        """
        try:
            logger.info("Clicking on View Details button")
            element = self.wait_for_element(self.btn_view_details)
            element.click()
            logger.info("Clicked on View Details button successfully")
        except Exception as e:
            logger.error(f"Failed to click on View Details button: {str(e)}")
            raise

    def click_scan_boarding_pass_button(self):
        """
        Clicks on the Scan Boarding Pass button.
        """
        try:
            logger.info("Clicking on Scan Boarding Pass button")
            element = self.wait_for_element(self.btn_scan_boarding_pass)
            element.click()
            logger.info("Clicked on Scan Boarding Pass button successfully")
        except Exception as e:
            logger.error(f"Failed to click on Scan Boarding Pass button: {str(e)}")
            raise

    def fetch_scan_boarding_pass_button_text(self):
        """
        Fetches the Scan Boarding Pass button text.
        :return: Button text
        """
        try:
            logger.info("Fetching Scan Boarding Pass button text")
            element = self.wait_for_element(self.btn_scan_boarding_pass)
            text = element.text
            logger.info(f"Scan Boarding Pass button text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch Scan Boarding Pass button text: {str(e)}")
            raise

    def click_print_customer_receipt(self):
        """
        Clicks on Print Customer Receipt button.
        """
        try:
            logger.info("Clicking on Print Customer Receipt button")
            element = self.wait_for_element(self.btn_print_customer_receipt)
            element.click()
            logger.info("Clicked on Print Customer Receipt button successfully")
        except Exception as e:
            logger.error(f"Failed to click on Print Customer Receipt button: {str(e)}")
            raise

    def click_print_merchant_receipt(self):
        """
        Clicks on Print Merchant Receipt button.
        """
        try:
            logger.info("Clicking on Print Merchant Receipt button")
            element = self.wait_for_element(self.btn_print_merchant_receipt)
            element.click()
            logger.info("Clicked on Print Merchant Receipt button successfully")
        except Exception as e:
            logger.error(f"Failed to click on Print Merchant Receipt button: {str(e)}")
            raise

    def fetch_e_receipt_text(self):
        """
        Fetches the e-receipt text.
        :return: E-receipt text
        """
        try:
            logger.info("Fetching e-receipt text")
            element = self.wait_for_element(self.lbl_e_receipt_text)
            text = element.text
            logger.info(f"E-receipt text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch e-receipt text: {str(e)}")
            return None

    def fetch_e_receipt_caption(self):
        """
        Fetches the e-receipt caption.
        :return: E-receipt caption text (e.g., 'Get digital receipt on phone no.')
        """
        try:
            logger.info("Fetching e-receipt caption")
            element = self.wait_for_element(self.lbl_e_receipt_caption)
            caption = element.text
            logger.info(f"E-receipt caption: {caption}")
            return caption
        except Exception as e:
            logger.error(f"Failed to fetch e-receipt caption: {str(e)}")
            return None

    def is_e_receipt_icon_displayed(self):
        """
        Checks if e-receipt icon is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if e-receipt icon is displayed")
            element = self.wait_for_element(self.img_e_receipt_icon)
            is_displayed = element.is_displayed()
            logger.info(f"E-receipt icon displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"E-receipt icon not found: {str(e)}")
            return False

    def fetch_go_green_text(self):
        """
        Fetches the go green text.
        :return: Go green text (e.g., 'Go green, save paper & nature')
        """
        try:
            logger.info("Fetching go green text")
            element = self.wait_for_element(self.lbl_go_green_text)
            text = element.text
            logger.info(f"Go green text: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to fetch go green text: {str(e)}")
            return None

    def is_footer_rzp_logo_displayed(self):
        """
        Checks if footer Razorpay logo is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if footer Razorpay logo is displayed")
            element = self.wait_for_element(self.img_footer_rzp_logo)
            is_displayed = element.is_displayed()
            logger.info(f"Footer Razorpay logo displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Footer Razorpay logo not found: {str(e)}")
            return False

