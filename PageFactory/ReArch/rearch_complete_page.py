from PageFactory.ReArch.rearch_base_page import ReArchBasePage
from PageFactory.ReArch.rearch_locators import PaymentCompleteLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchCompletePage(ReArchBasePage):
    """
    Page object for the ReArch Payment Complete / Result screen.
    Source: pos/web/src/pages/pay/complete.svelte
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_result_screen(self, timeout: int = 90):
        """
        Wait until the payment result screen appears.
        The #txn-page container is always present on this screen.
        """
        self.switch_to_webview()
        self.wait_for_element(PaymentCompleteLocators.page_txn, timeout)
        logger.info("ReArch payment result screen is ready.")

    def wait_for_success_screen(self, timeout: int = 90):
        """Wait specifically for a successful payment outcome."""
        self.wait_for_result_screen(timeout)
        self.wait_for_element(PaymentCompleteLocators.lbl_payment_successful, timeout)
        logger.info("Payment Successful screen confirmed.")

    def wait_for_failure_screen(self, timeout: int = 90):
        """Wait specifically for a failed payment outcome."""
        self.wait_for_result_screen(timeout)
        self.wait_for_element(PaymentCompleteLocators.lbl_payment_failed, timeout)
        logger.info("Payment Failed screen confirmed.")

    # ── Status fetch ──────────────────────────────────────────────────────────

    def is_payment_successful(self) -> bool:
        return self.is_element_visible(PaymentCompleteLocators.lbl_payment_successful, time=5)

    def is_payment_failed(self) -> bool:
        return self.is_element_visible(PaymentCompleteLocators.lbl_payment_failed, time=5)

    def fetch_result_heading(self) -> str:
        """Return the main heading text (e.g. 'Thank you!', 'Payment Failed')."""
        if self.is_element_visible(PaymentCompleteLocators.lbl_thank_you, time=3):
            return self.fetch_text(PaymentCompleteLocators.lbl_thank_you)
        if self.is_element_visible(PaymentCompleteLocators.lbl_payment_settled, time=3):
            return self.fetch_text(PaymentCompleteLocators.lbl_payment_settled)
        return self.fetch_text(PaymentCompleteLocators.lbl_payment_failed)

    def fetch_payment_status_text(self) -> str:
        """Return the sub-status label ('Payment Successful' / 'Payment Failed')."""
        if self.is_payment_successful():
            return self.fetch_text(PaymentCompleteLocators.lbl_payment_successful)
        return self.fetch_text(PaymentCompleteLocators.lbl_payment_failed)

    def fetch_amount_label(self) -> str:
        return self.fetch_text(PaymentCompleteLocators.lbl_amount_label)

    def fetch_error_detail(self) -> str:
        return self.fetch_text(PaymentCompleteLocators.lbl_error_detail, time=5)

    # ── View Details dialog ───────────────────────────────────────────────────

    def open_view_details(self):
        self.perform_click(PaymentCompleteLocators.btn_view_details)
        logger.info("Opened View Details dialog.")

    def fetch_detail_payment_id(self) -> str:
        return self.fetch_text(PaymentCompleteLocators.lbl_detail_payment_id)

    def fetch_detail_rrn(self) -> str:
        return self.fetch_text(PaymentCompleteLocators.lbl_detail_rrn)

    def fetch_detail_auth_code(self) -> str:
        return self.fetch_text(PaymentCompleteLocators.lbl_detail_auth_code)

    def fetch_detail_status(self) -> str:
        return self.fetch_text(PaymentCompleteLocators.lbl_detail_status)

    def fetch_detail_date_time(self) -> str:
        return self.fetch_text(PaymentCompleteLocators.lbl_detail_date_time)

    def fetch_all_details(self) -> dict:
        """Open the details dialog and return a dict of all visible fields."""
        self.open_view_details()
        details = {}
        for field, locator in [
            ("payment_id",  PaymentCompleteLocators.lbl_detail_payment_id),
            ("rrn",         PaymentCompleteLocators.lbl_detail_rrn),
            ("auth_code",   PaymentCompleteLocators.lbl_detail_auth_code),
            ("status",      PaymentCompleteLocators.lbl_detail_status),
            ("date_time",   PaymentCompleteLocators.lbl_detail_date_time),
        ]:
            if self.is_element_visible(locator, time=3):
                details[field] = self.fetch_text(locator)
        logger.debug(f"Payment details fetched: {details}")
        return details

    # ── Action buttons ────────────────────────────────────────────────────────

    def click_proceed_to_home(self):
        """
        Click the primary done/proceed button.
        Tries all three label variants in order.
        """
        for locator in [
            PaymentCompleteLocators.btn_accept_more_payments,
            PaymentCompleteLocators.btn_back_to_home,
            PaymentCompleteLocators.btn_go_back,
        ]:
            if self.is_element_visible(locator, time=3):
                self.perform_click(locator)
                logger.info("Clicked proceed-to-home button.")
                return
        logger.warning("No proceed-to-home button found.")

    def click_retry(self):
        self.perform_click(PaymentCompleteLocators.btn_retry)
        logger.info("Clicked Retry button.")

    def click_print_receipt(self):
        self.perform_click(PaymentCompleteLocators.btn_print_receipt)
        logger.info("Clicked Print Receipt.")

    def click_print_merchant_copy(self):
        """Select Merchant Copy inside the print options sheet."""
        self.wait_for_element(PaymentCompleteLocators.btn_print_merchant_copy)
        self.perform_click(PaymentCompleteLocators.btn_print_merchant_copy)
        logger.info("Clicked Print Merchant Copy.")

    def click_print_customer_copy(self):
        """Select Customer Copy inside the print options sheet."""
        self.wait_for_element(PaymentCompleteLocators.btn_print_customer_copy)
        self.perform_click(PaymentCompleteLocators.btn_print_customer_copy)
        logger.info("Clicked Print Customer Copy.")

    def click_send_e_receipt(self):
        self.perform_click(PaymentCompleteLocators.btn_send_e_receipt)
        logger.info("Clicked Send E-Receipt.")
