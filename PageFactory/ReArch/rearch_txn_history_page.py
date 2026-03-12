from PageFactory.ReArch.rearch_base_page import ReArchBasePage
from PageFactory.ReArch.rearch_locators import TxnHistoryLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchTxnHistoryPage(ReArchBasePage):
    """
    Page object for the ReArch Transaction History / List screen.
    Sources: pos/web/src/pages/txn/TransactionHistory.svelte
             pos/web/src/pages/txn/list.svelte
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_txn_list(self, timeout: int = 45):
        """Wait until at least one transaction list item is visible."""
        self.switch_to_webview()
        self.wait_for_all_elements(TxnHistoryLocators.lst_txn_items, timeout)
        logger.info("ReArch transaction history list is ready.")

    def wait_for_page_load(self, timeout: int = 45):
        """
        Wait for the history page to finish loading.
        Falls back to checking either list items or the empty-state block.
        """
        self.switch_to_webview()
        import time as _time
        deadline = _time.time() + timeout
        while _time.time() < deadline:
            if self.is_element_visible(TxnHistoryLocators.lst_txn_items, time=2):
                break
            if self.is_element_visible(TxnHistoryLocators.lbl_empty_state, time=2):
                break
            _time.sleep(1)
        logger.info("Transaction history page loaded.")

    # ── List access ───────────────────────────────────────────────────────────

    def get_all_txn_items(self):
        """Return a list of WebElement objects representing each txn row."""
        return self.fetch_elements(TxnHistoryLocators.lst_txn_items)

    def get_txn_count(self) -> int:
        try:
            return len(self.get_all_txn_items())
        except Exception:
            return 0

    # ── Click a specific transaction ──────────────────────────────────────────

    def click_txn_by_index(self, index: int = 0):
        """Click the nth transaction item (0-based)."""
        items = self.get_all_txn_items()
        if index >= len(items):
            raise IndexError(f"Transaction index {index} is out of range (total: {len(items)})")
        items[index].click()
        logger.info(f"Clicked transaction at index {index}.")

    def click_txn_by_amount(self, amount_str: str):
        """
        Click the first transaction whose amount text contains the given string.
        amount_str should match the displayed format, e.g. '₹100.00' or '100'.
        """
        items = self.get_all_txn_items()
        for item in items:
            try:
                amt_el = item.find_element(*TxnHistoryLocators.lbl_txn_amount)
                if amount_str in amt_el.text:
                    item.click()
                    logger.info(f"Clicked transaction with amount containing '{amount_str}'.")
                    return
            except Exception:
                continue
        raise LookupError(f"No transaction found with amount '{amount_str}'")

    def click_txn_by_method(self, method_name: str):
        """
        Click the first transaction whose payment method text matches.
        method_name: e.g. 'UPI', 'Card', 'Cash'.
        """
        items = self.get_all_txn_items()
        for item in items:
            try:
                method_el = item.find_element(*TxnHistoryLocators.lbl_txn_method)
                if method_name.lower() in method_el.text.lower():
                    item.click()
                    logger.info(f"Clicked transaction with method '{method_name}'.")
                    return
            except Exception:
                continue
        raise LookupError(f"No transaction found with method '{method_name}'")

    # ── Row field fetch ───────────────────────────────────────────────────────

    def fetch_txn_method_at_index(self, index: int = 0) -> str:
        items = self.get_all_txn_items()
        return items[index].find_element(*TxnHistoryLocators.lbl_txn_method).text

    def fetch_txn_amount_at_index(self, index: int = 0) -> str:
        items = self.get_all_txn_items()
        return items[index].find_element(*TxnHistoryLocators.lbl_txn_amount).text

    def fetch_txn_status_at_index(self, index: int = 0) -> str:
        items = self.get_all_txn_items()
        return items[index].find_element(*TxnHistoryLocators.lbl_txn_status).text

    def fetch_txn_time_at_index(self, index: int = 0) -> str:
        items = self.get_all_txn_items()
        return items[index].find_element(*TxnHistoryLocators.lbl_txn_time).text

    # ── Date headers ──────────────────────────────────────────────────────────

    def get_date_headers(self):
        return self.fetch_elements(TxnHistoryLocators.lbl_date_header)

    def fetch_date_header_texts(self) -> list:
        return [h.text for h in self.get_date_headers()]

    # ── Empty state ───────────────────────────────────────────────────────────

    def is_empty_state_displayed(self) -> bool:
        return self.is_element_visible(TxnHistoryLocators.lbl_empty_state, time=5)
