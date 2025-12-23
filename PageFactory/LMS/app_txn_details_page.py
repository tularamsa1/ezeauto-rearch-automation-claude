from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage
from Utilities.EzeAutoLogger import EzeAutoLogger

logger = EzeAutoLogger.get_logger()


class TxnDetailsPage(BasePage):
    """
    Page object for the Transaction Details page in LMS application.
    Contains locators and methods for transaction details view functionality.
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

        # ============== PAGE HEADER ==============
        self.lbl_txn_header = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvTxnHeader')

        # ============== ACTION BUTTONS ==============
        self.btn_dismiss = (AppiumBy.ID, 'com.ezetap.service.demo:id/btnDismiss')

    def is_txn_details_page_displayed(self):
        """
        Checks if Transaction Details page is displayed.
        :return: True if displayed, False otherwise
        """
        try:
            logger.info("Checking if Transaction Details page is displayed")
            element = self.wait_for_element(self.lbl_txn_header)
            is_displayed = element.is_displayed()
            logger.info(f"Transaction Details page displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Transaction Details page not displayed: {str(e)}")
            return False

    def fetch_txn_header(self):
        """
        Fetches the transaction details header text.
        :return: Header text (e.g., 'Transaction Details')
        """
        try:
            logger.info("Fetching transaction header")
            element = self.wait_for_element(self.lbl_txn_header)
            header = element.text
            logger.info(f"Transaction header: {header}")
            return header
        except Exception as e:
            logger.error(f"Failed to fetch transaction header: {str(e)}")
            return None

    def click_close_button(self):
        """
        Clicks on the Close/Dismiss button.
        """
        try:
            logger.info("Clicking on Close button")
            element = self.wait_for_element(self.btn_dismiss)
            element.click()
            logger.info("Clicked on Close button successfully")
        except Exception as e:
            logger.error(f"Failed to click on Close button: {str(e)}")
            raise

    def fetch_field_value(self, field_name: str):
        """
        Fetches the value for a specific field by finding the value element following the key.
        :param field_name: The text of the key field (e.g., 'Customer Name', 'Status')
        :return: Field value text
        """
        try:
            logger.info(f"Fetching value for field: {field_name}")
            # Use XPath to find the value element that follows the key element
            xpath = f'//android.widget.TextView[@resource-id="com.ezetap.service.demo:id/tvTxnItemKey" and @text="{field_name}"]/following-sibling::android.widget.TextView[@resource-id="com.ezetap.service.demo:id/tvTxnItemValue"]'
            value_element = self.wait_for_element((By.XPATH, xpath))
            value = value_element.text
            logger.info(f"Field '{field_name}' value: {value}")
            return value
        except Exception as e:
            logger.error(f"Failed to fetch value for field '{field_name}': {str(e)}")
            return None

    def fetch_customer_name_value(self):
        """
        Fetches the Customer Name value.
        :return: Customer name text
        """
        return self.fetch_field_value("Customer Name")

    def fetch_customer_mobile_value(self):
        """
        Fetches the Customer Mobile value.
        :return: Customer mobile text
        """
        return self.fetch_field_value("Customer Mobile")

    def fetch_date_value(self):
        """
        Fetches the Date value.
        :return: Date text
        """
        return self.fetch_field_value("Date")

    def fetch_transaction_id_value(self):
        """
        Fetches the Transaction Id value.
        :return: Transaction ID text
        """
        return self.fetch_field_value("Transaction Id")

    def fetch_status_value(self):
        """
        Fetches the Status value.
        :return: Status text
        """
        return self.fetch_field_value("Status")

    def fetch_card_value(self):
        """
        Fetches the Card value.
        :return: Card text
        """
        return self.fetch_field_value("Card")

    def fetch_auth_code_value(self):
        """
        Fetches the Auth Code value.
        :return: Auth Code text
        """
        return self.fetch_field_value("Auth Code")

    def fetch_tid_value(self):
        """
        Fetches the TID value.
        :return: TID text
        """
        return self.fetch_field_value("TID")

    def fetch_mid_value(self):
        """
        Fetches the MID value.
        :return: MID text
        """
        return self.fetch_field_value("MID")

    def fetch_rr_number_value(self):
        """
        Fetches the RR Number value.
        :return: RR Number text
        """
        return self.fetch_field_value("RR Number")

    def fetch_batch_no_value(self):
        """
        Fetches the Batch no. value.
        :return: Batch number text
        """
        return self.fetch_field_value("Batch no.")

