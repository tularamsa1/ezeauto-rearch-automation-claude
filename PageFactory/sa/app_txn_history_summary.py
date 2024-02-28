from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class TxnSummary(BasePage):
    btn_txn_summary = (By.ID, 'com.ezetap.service.demo:id/btnPrint')
    txt_pmt_mode = (AppiumBy.XPATH, '//*[@text="Payment -UPI"]')
    txt_pmt_mode_1 = (AppiumBy.XPATH, '//*[@text="Payment -BHARATQR"]')
    txt_pmt_mode_2 = (AppiumBy.XPATH, '//*[@text="Payment -CASH"]')
    txt_pmt_mode_3 = (AppiumBy.XPATH, '//*[@text="Payment -CHEQUE"]')
    txt_pmt_mode_4 = (AppiumBy.XPATH, '//*[@text="Payment -CNP"]')
    txt_pmt_mode_5 = (AppiumBy.XPATH, '//*[@text="Payment -CARD"]')
    txt_amt = (AppiumBy.XPATH, '//*[@text="Payment -UPI"]/..//*[@resource-id="com.ezetap.service.demo:id/tvTotalAmount"]')
    txn_amt_1 = (AppiumBy.XPATH, '//*[@text="Payment -BHARATQR"]/..//*[@resource-id="com.ezetap.service.demo:id/tvTotalAmount"]')
    txn_amt_2 = (AppiumBy.XPATH, '//*[@text="Payment -CASH"]/..//*[@resource-id="com.ezetap.service.demo:id/tvTotalAmount"]')
    txn_amt_3 = (AppiumBy.XPATH, '//*[@text="Payment -CHEQUE"]/..//*[@resource-id="com.ezetap.service.demo:id/tvTotalAmount"]')
    txn_amt_4 = (AppiumBy.XPATH, '//*[@text="Payment -CNP"]/..//*[@resource-id="com.ezetap.service.demo:id/tvTotalAmount"]')
    txn_amt_5 = (AppiumBy.XPATH, '//*[@text="Payment -CARD"]/..//*[@resource-id="com.ezetap.service.demo:id/tvTotalAmount"]')
    txt_sales_volume = (AppiumBy.XPATH, '//*[@resource-id="com.ezetap.service.demo:id/clFooterView"]/..//*[@resource-id="com.ezetap.service.demo:id/tvGrandTotalAmount"]')
    txt_total_sales_count = (AppiumBy.XPATH, '//*[@resource-id="com.ezetap.service.demo:id/clFooterView"]/..//*[@resource-id="com.ezetap.service.demo:id/tvGrandTotalCount"]')

    def __init__(self, driver):
        super().__init__(driver)

    def fetch_total_volume(self):
        """
        fetches the volume(total amount of txn) from the txn summary page
        return: str
        """
        self.scroll_to_text("Grand Total")
        grand_total = self.fetch_text(self.txt_sales_volume)
        grand_total = ''.join(filter(str.isdigit, grand_total.split('.')[0]))
        return grand_total

    def fetch_total_sales(self):
        """
        fetches the total count of sales done for today from txn summary
        return: str
        """
        self.scroll_to_text("Grand Total")
        return self.fetch_text(self.txt_total_sales_count)

    def fetch_first_highest_payment_mode_and_amount(self):
        """
        Fetches the transaction amount and payment mode for UPI transactions
        return: str
        """
        self.scroll_to_text("Payment -UPI")
        txn_amt = self.fetch_text(self.txt_amt)
        txn_amt = ''.join(filter(str.isdigit, txn_amt.split('.')[0]))
        pmt_mode = self.fetch_text(self.txt_pmt_mode)
        pmt_mode = pmt_mode[len("Payment -"):]
        return txn_amt, pmt_mode

    def fetch_second_highest_payment_mode_and_amount(self):
        """
         Fetches the transaction amount and payment mode for BHARATQR transactions
         return: str
         """
        txn_amt = self.fetch_text(self.txn_amt_1)
        txn_amt = ''.join(filter(str.isdigit, txn_amt.split('.')[0]))
        pmt_mode = self.fetch_text(self.txt_pmt_mode_1)
        pmt_mode = pmt_mode[len("Payment -"):]
        return txn_amt, pmt_mode

    def fetch_third_highest_payment_mode_and_amount(self):
        """
        Fetches the transaction amount and payment mode for CHEQUE transactions
        return: str
         """
        txn_amt = self.fetch_text(self.txn_amt_3)
        txn_amt = ''.join(filter(str.isdigit, txn_amt.split('.')[0]))
        pmt_mode = self.fetch_text(self.txt_pmt_mode_3)
        pmt_mode = pmt_mode[len("Payment -"):]
        return txn_amt, pmt_mode

    def fetch_fourth_highest_payment_mode_and_amount(self):
        """
         Fetches the transaction amount and payment mode for CASH transactions
         return: str
         """
        txn_amt = self.fetch_text(self.txn_amt_2)
        txn_amt = ''.join(filter(str.isdigit, txn_amt.split('.')[0]))
        pmt_mode = self.fetch_text(self.txt_pmt_mode_2)
        pmt_mode = pmt_mode[len("Payment -"):]
        return txn_amt, pmt_mode

    def fetch_cnp_payment_mode_and_amount(self):
        """
         Fetches the transaction amount and payment mode for CNP transactions
         return: str
         """
        self.scroll_to_text("Payment -CNP")
        txn_amt = self.fetch_text(self.txn_amt_4)
        txn_amt = ''.join(filter(str.isdigit, txn_amt.split('.')[0]))
        pmt_mode = self.fetch_text(self.txt_pmt_mode_4)
        pmt_mode = pmt_mode[len("Payment -"):]
        return txn_amt, pmt_mode

    def fetch_card_payment_mode_and_amount(self):
        """
         Fetches the transaction amount and payment mode for card transactions
         return: str
         """
        self.scroll_to_text("Payment -CARD")
        txn_amt = self.fetch_text(self.txn_amt_5)
        txn_amt = ''.join(filter(str.isdigit, txn_amt.split('.')[0]))
        pmt_mode = self.fetch_text(self.txt_pmt_mode_5)
        pmt_mode = pmt_mode[len("Payment -"):]
        return txn_amt, pmt_mode

    def click_on_txn_summary(self):
        """
        performs click on the txn summary button from the transaction page
        """
        self.perform_click(self.btn_txn_summary)

