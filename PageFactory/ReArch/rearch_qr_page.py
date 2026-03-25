from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import QRPaymentLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchQRPage(ReArchNativeBasePage):
    """Page object for the ReArch QR / UPI payment screen (native context)."""

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits / presence checks ───────────────────────────────────────────────

    def wait_for_qr_screen(self, timeout: int = 60):
        """Wait until the QR screen is displayed ('Scan & Pay' label visible)."""
        self.wait_for_element(QRPaymentLocators.lbl_scan_and_pay, timeout)
        logger.info("ReArch QR payment screen is ready.")

    def is_qr_screen_displayed(self) -> bool:
        return self.is_element_visible(QRPaymentLocators.lbl_scan_and_pay, time=5)

    # ── Fetch displayed values ─────────────────────────────────────────────────

    def fetch_scan_and_pay_text(self) -> str:
        return self.fetch_text(QRPaymentLocators.lbl_scan_and_pay)

    def fetch_amount_text(self) -> str:
        return self.fetch_text(QRPaymentLocators.lbl_amount_value)

    # ── Validations ───────────────────────────────────────────────────────────

    def validate_qr_screen(self):
        """Assert that the QR payment screen is fully loaded."""
        self.wait_for_qr_screen()
        scan_text = self.fetch_scan_and_pay_text()
        logger.info(f"QR screen validated -- header text: '{scan_text}'")
        return scan_text

    # ── Cancel payment flow ───────────────────────────────────────────────────

    def initiate_cancel_payment(self):
        """Press the device back button to trigger the cancel confirmation dialog."""
        self.perform_click(QRPaymentLocators.btn_back)
        logger.info("Triggered payment cancel via back navigation.")

    def confirm_cancel_payment(self):
        """Confirm cancellation inside the 'Cancel the Payment?' dialog."""
        self.wait_for_element(QRPaymentLocators.lbl_cancel_dialog_title, time=15)
        self.perform_click(QRPaymentLocators.btn_confirm_cancel)
        logger.info("Payment cancellation confirmed.")

    def cancel_payment(self):
        """Full cancel flow: trigger dialog -> confirm."""
        self.initiate_cancel_payment()
        self.confirm_cancel_payment()
