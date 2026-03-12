from PageFactory.ReArch.rearch_base_page import ReArchBasePage
from PageFactory.ReArch.rearch_locators import TxnDetailLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchTxnDetailPage(ReArchBasePage):
    """
    Page object for the ReArch Transaction Detail screen.
    Source: pos/web/src/pages/txn/detail.svelte
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_detail_page(self, timeout: int = 45):
        """Wait until the detail page status field is visible."""
        self.switch_to_webview()
        self.wait_for_element(TxnDetailLocators.lbl_status_value, timeout)
        logger.info("ReArch transaction detail page is ready.")

    # ── Field fetchers ────────────────────────────────────────────────────────

    def fetch_status(self) -> str:
        return self.fetch_text(TxnDetailLocators.lbl_status_value)

    def fetch_payment_id(self) -> str:
        return self.fetch_text(TxnDetailLocators.lbl_payment_id_value)

    def fetch_rrn(self) -> str:
        return self.fetch_text(TxnDetailLocators.lbl_rrn_value)

    def fetch_auth_code(self) -> str:
        return self.fetch_text(TxnDetailLocators.lbl_auth_code_value)

    def fetch_date_time(self) -> str:
        return self.fetch_text(TxnDetailLocators.lbl_date_time_value)

    def fetch_payment_mode(self) -> str:
        return self.fetch_text(TxnDetailLocators.lbl_payment_mode_value)

    def fetch_customer_name(self) -> str:
        if self.is_element_visible(TxnDetailLocators.lbl_customer_name, time=3):
            return self.fetch_text(TxnDetailLocators.lbl_customer_name)
        return ""

    def fetch_page_title(self) -> str:
        return self.fetch_text(TxnDetailLocators.lbl_page_title)

    def fetch_all_detail_fields(self) -> dict:
        """Return a dict with all visible detail page fields."""
        fields = {}
        field_map = {
            "status":       TxnDetailLocators.lbl_status_value,
            "payment_id":   TxnDetailLocators.lbl_payment_id_value,
            "rrn":          TxnDetailLocators.lbl_rrn_value,
            "auth_code":    TxnDetailLocators.lbl_auth_code_value,
            "date_time":    TxnDetailLocators.lbl_date_time_value,
            "payment_mode": TxnDetailLocators.lbl_payment_mode_value,
            "customer_name":TxnDetailLocators.lbl_customer_name,
        }
        for field_name, locator in field_map.items():
            if self.is_element_visible(locator, time=3):
                fields[field_name] = self.fetch_text(locator)
        logger.debug(f"Transaction detail fields: {fields}")
        return fields

    # ── Action buttons ────────────────────────────────────────────────────────

    def click_refund(self):
        self.wait_for_element(TxnDetailLocators.btn_refund)
        self.perform_click(TxnDetailLocators.btn_refund)
        logger.info("Clicked Refund button.")

    def click_print_chargeslip(self):
        self.perform_click(TxnDetailLocators.btn_print_chargeslip)
        logger.info("Clicked Print Chargeslip button.")

    def click_send_receipt(self):
        self.perform_click(TxnDetailLocators.btn_send_receipt)
        logger.info("Clicked Send E-Receipt button.")

    def is_refund_available(self) -> bool:
        return self.is_element_visible(TxnDetailLocators.btn_refund, time=5)
