import time as _time

from appium.webdriver.common.appiumby import AppiumBy

from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import TxnHistoryLocators, TxnSearchLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchTxnHistoryPage(ReArchNativeBasePage):
    """Page object for the ReArch Transaction History / List screen (native context)."""

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_txn_list(self, timeout: int = 45):
        """Wait until the Payments header is visible."""
        self.wait_for_element(TxnHistoryLocators.lbl_payments, timeout)
        logger.info("ReArch transaction history list is ready.")

    def wait_for_page_load(self, timeout: int = 45):
        """Wait for the history page to finish loading."""
        deadline = _time.time() + timeout
        while _time.time() < deadline:
            if self.is_element_visible(TxnHistoryLocators.lbl_payments, time=2):
                break
            _time.sleep(1)
        logger.info("Transaction history page loaded.")

    # ── Transaction row access ────────────────────────────────────────────────

    def click_txn_by_method_and_amount(self, method: str, amount: str):
        """Click a transaction row matching both method and amount text."""
        locator = TxnHistoryLocators.txn_row_by_method_and_amount(method, amount)
        self.perform_click(locator)
        logger.info(f"Clicked transaction: method={method}, amount={amount}")

    def click_txn_by_status(self, status: str):
        """Click the first transaction row matching the given status."""
        locator = TxnHistoryLocators.txn_row_by_status(status)
        self.perform_click(locator)
        logger.info(f"Clicked transaction with status: {status}")

    # def click_first_transaction(self):
    #     """Click the first transaction row visible on the page."""
    #     locator = TxnHistoryLocators.txn_row_by_status("")
    #     self.perform_click(locator)
    #     logger.info("Clicked first transaction row.")

    def click_on_transaction_by_txn_id(self, txn_id: str):
        """Search by Payment ID and open the matching transaction.

        Flow: Search button → Payment ID filter → type txn_id → tap result row.
        """
        self.perform_click(TxnHistoryLocators.btn_search)
        # self.wait_for_element(TxnSearchLocators.lbl_search)
        self.perform_click(TxnSearchLocators.txt_search_input)
        self.perform_sendkeys(TxnSearchLocators.txt_search_input, txn_id)
        self.driver.press_keycode(66)   # Android Enter/Search key


        self.wait_for_element(TxnSearchLocators.txn_row)
        self.perform_click(TxnSearchLocators.txn_row)
        logger.info(f"Opened transaction with txn_id: {txn_id}")

    def click_on_transaction_by_amount(self, amount: str):
        """Search by Amount and open the matching transaction.

        Flow: Search button → Amount tab → type amount → tap result row.
        """
        self.perform_click(TxnHistoryLocators.btn_search)
        self.perform_click(TxnSearchLocators.btn_amount)
        self.perform_click(TxnSearchLocators.txt_search_input)
        self.perform_sendkeys(TxnSearchLocators.txt_search_input, amount)
        self.driver.press_keycode(66)   # Android Enter/Search key

        self.wait_for_element(TxnSearchLocators.txn_row)
        self.perform_click(TxnSearchLocators.txn_row)
        logger.info(f"Opened transaction with amount: {amount}")

    def click_on_transaction_by_rrn(self, rrn: str):
        """Search by RRN Number and open the matching transaction.

        Flow: Search button → RRN Number tab → type rrn → tap result row.
        """
        self.perform_click(TxnHistoryLocators.btn_search)
        self.perform_click(TxnSearchLocators.btn_rrn_number)
        self.perform_click(TxnSearchLocators.txt_search_input)
        self.perform_sendkeys(TxnSearchLocators.txt_search_input, rrn)
        self.driver.press_keycode(66)   # Android Enter/Search key

        self.wait_for_element(TxnSearchLocators.txn_row)
        self.perform_click(TxnSearchLocators.txn_row)
        logger.info(f"Opened transaction with rrn: {rrn}")

    def click_on_transaction_by_auth_code(self, auth_code: str):
        """Search by Auth Code and open the matching transaction.

        Flow: Search button → scroll to Auth Code tab → type auth_code → tap result row.
        Auth Code tab is off-screen to the right, so a horizontal scroll is needed.
        """
        self.perform_click(TxnHistoryLocators.btn_search)
        self.scroll_to_text("Auth Code")
        self.perform_click(TxnSearchLocators.btn_auth_code)
        self.perform_click(TxnSearchLocators.txt_search_input)
        self.perform_sendkeys(TxnSearchLocators.txt_search_input, auth_code)
        self.driver.press_keycode(66)   # Android Enter/Search key

        self.wait_for_element(TxnSearchLocators.txn_row)
        self.perform_click(TxnSearchLocators.txn_row)
        logger.info(f"Opened transaction with auth_code: {auth_code}")

    # ── Navigation ────────────────────────────────────────────────────────────

    def click_search(self):
        self.perform_click(TxnHistoryLocators.btn_search)
        logger.info("Clicked Search button.")

    def click_my_dashboard(self):
        self.perform_click(TxnHistoryLocators.btn_my_dashboard)
        logger.info("Clicked My Dashboard button.")

    def click_back(self):
        self.perform_click(TxnHistoryLocators.btn_back)
        logger.info("Clicked Back button from transaction history.")

    # ── Filters ───────────────────────────────────────────────────────────────

    def click_filter_date(self):
        self.perform_click(TxnHistoryLocators.btn_filter_date)
        logger.info("Clicked Date filter.")

    def click_filter_method(self):
        self.perform_click(TxnHistoryLocators.btn_filter_method)
        logger.info("Clicked Method filter.")

    def click_filter_status(self):
        self.perform_click(TxnHistoryLocators.btn_filter_status)
        logger.info("Clicked Status filter.")

    # ── Filter actions ───────────────────────────────────────────────────────

    def select_filter_option(self, option_text: str):
        """Select a filter option from the filter dropdown (e.g., 'Cash', 'Settled')."""
        self.perform_click(TxnHistoryLocators.filter_option_btn(option_text))
        logger.info(f"Selected filter option: {option_text}")

    def click_apply_filter(self):
        """Click the Apply button in the filter dropdown."""
        self.perform_click(TxnHistoryLocators.btn_apply_filter)
        logger.info("Clicked Apply filter button.")

    def is_filter_text_displayed(self, text: str, timeout: int = 10) -> bool:
        """Check if a specific text is visible on the current page (e.g., active filter chip)."""
        return self.is_element_visible(TxnHistoryLocators.filter_chip_text(text), time=timeout)

    # ── Presence checks ───────────────────────────────────────────────────────

    def is_payments_header_visible(self) -> bool:
        return self.is_element_visible(TxnHistoryLocators.lbl_payments, time=5)
