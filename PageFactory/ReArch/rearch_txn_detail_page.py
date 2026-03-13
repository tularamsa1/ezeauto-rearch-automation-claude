from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import TxnDetailLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchTxnDetailPage(ReArchNativeBasePage):
    """Page object for the ReArch Transaction Detail screen (native context)."""

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_detail_page(self, timeout: int = 45):
        """Wait until the detail page status field is visible."""
        self.wait_for_element(TxnDetailLocators.lbl_status_label, timeout)
        logger.info("ReArch transaction detail page is ready.")

    # ── Field fetchers (using the dynamic following-sibling locator) ──────────

    def fetch_status(self) -> str:
        return self.fetch_text(TxnDetailLocators.field_value_after("Status"))

    def fetch_payment_id(self) -> str:
        return self.fetch_text(TxnDetailLocators.field_value_after("Payment ID"))

    def fetch_rrn(self) -> str:
        return self.fetch_text(TxnDetailLocators.field_value_after("RRN"))

    def fetch_auth_code(self) -> str:
        return self.fetch_text(TxnDetailLocators.field_value_after("Auth Code"))

    def fetch_date_time(self) -> str:
        return self.fetch_text(TxnDetailLocators.field_value_after("Date & Time"))

    def fetch_payment_mode(self) -> str:
        return self.fetch_text(TxnDetailLocators.field_value_after("Payment Mode"))

    def fetch_customer_name(self) -> str:
        locator = TxnDetailLocators.field_value_after("Customer Name")
        if self.is_element_visible(locator, time=3):
            return self.fetch_text(locator)
        return ""

    def fetch_all_detail_fields(self) -> dict:
        """Return a dict with all visible detail page fields."""
        fields = {}
        field_names = ["Status", "Payment ID", "RRN", "Auth Code", "Date & Time", "Payment Mode", "Customer Name"]
        for label in field_names:
            locator = TxnDetailLocators.field_value_after(label)
            if self.is_element_visible(locator, time=3):
                key = label.lower().replace(" & ", "_").replace(" ", "_")
                fields[key] = self.fetch_text(locator)
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

    def click_back(self):
        self.perform_click(TxnDetailLocators.btn_back)
        logger.info("Clicked Back button from transaction detail.")
