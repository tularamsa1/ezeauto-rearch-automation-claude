from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import (
    PaymentSuccessLocators,
    PaymentFailedLocators,
    TxnDetailLocators,
)
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchCompletePage(ReArchNativeBasePage):
    """Page object for the ReArch Payment Complete / Result screen (native context)."""

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_result_screen(self, timeout: int = 90):
        """Wait until the payment result screen appears (txn-page container)."""
        self.wait_for_element(PaymentSuccessLocators.lbl_txn_page, timeout)
        logger.info("ReArch payment result screen is ready.")

    def wait_for_success_screen(self, timeout: int = 90):
        """Wait specifically for a successful payment outcome."""
        self.wait_for_element(PaymentSuccessLocators.lbl_payment_successful, timeout)
        logger.info("Payment Successful screen confirmed.")

    def wait_for_failure_screen(self, timeout: int = 90):
        """Wait specifically for a failed payment outcome."""
        self.wait_for_element(PaymentFailedLocators.lbl_payment_failed, timeout)
        logger.info("Payment Failed screen confirmed.")

    # ── Status fetch ──────────────────────────────────────────────────────────

    def is_payment_successful(self) -> bool:
        return self.is_element_visible(PaymentSuccessLocators.lbl_payment_successful, time=5)

    def is_payment_failed(self) -> bool:
        return self.is_element_visible(PaymentFailedLocators.lbl_payment_failed, time=5)

    def fetch_result_heading(self) -> str:
        """Return the main heading text (e.g. 'Thank you!', 'Payment Failed')."""
        if self.is_element_visible(PaymentSuccessLocators.lbl_thank_you, time=3):
            return self.fetch_text(PaymentSuccessLocators.lbl_thank_you)
        return self.fetch_text(PaymentFailedLocators.lbl_payment_failed)

    def fetch_amount_label(self) -> str:
        return self.fetch_text(PaymentSuccessLocators.lbl_amount_received)

    def fetch_error_detail(self) -> str:
        return self.fetch_text(PaymentFailedLocators.lbl_error_detail, time=5)

    # ── View Details ──────────────────────────────────────────────────────────

    def open_view_details(self):
        self.perform_click(PaymentSuccessLocators.btn_view_details)
        logger.info("Opened View Details dialog.")

    def fetch_all_details(self) -> dict:
        """Open the details dialog and return a dict of all visible fields."""
        self.open_view_details()
        details = {}
        for field_name in ["Status", "Payment ID", "RRN", "Auth Code", "Date & Time"]:
            locator = TxnDetailLocators.field_value_after(field_name)
            if self.is_element_visible(locator, time=3):
                details[field_name.lower().replace(" & ", "_").replace(" ", "_")] = self.fetch_text(locator)
        logger.debug(f"Payment details fetched: {details}")
        return details

    # ── Action buttons ────────────────────────────────────────────────────────

    def click_proceed_to_home(self):
        """Click the primary done/proceed button (tries multiple label variants)."""
        for locator in [
            PaymentSuccessLocators.btn_accept_more_payments,
            PaymentFailedLocators.btn_back_to_home,
            PaymentFailedLocators.btn_go_back,
        ]:
            if self.is_element_visible(locator, time=3):
                self.perform_click(locator)
                logger.info("Clicked proceed-to-home button.")
                return
        logger.warning("No proceed-to-home button found.")

    def click_retry(self):
        self.perform_click(PaymentFailedLocators.btn_retry)
        logger.info("Clicked Retry button.")

    def click_print_receipt(self):
        self.perform_click(PaymentSuccessLocators.btn_print_receipt)
        logger.info("Clicked Print Receipt.")

    def click_send_e_receipt(self):
        self.perform_click(PaymentSuccessLocators.btn_send_ereceipt)
        logger.info("Clicked Send E-Receipt.")
