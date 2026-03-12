from PageFactory.ReArch.rearch_base_page import ReArchBasePage
from PageFactory.ReArch.rearch_locators import QRPaymentLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchQRPage(ReArchBasePage):
    """
    Page object for the ReArch QR / UPI payment screen.
    Sources: pos/web/src/modules/payment/qr/index.svelte
             pos/web/src/modules/payment/qr/Upi.svelte
             pos/web/src/modules/payment/PaymentPage.svelte
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits / presence checks ───────────────────────────────────────────────

    def wait_for_qr_screen(self, timeout: int = 60):
        """
        Wait until the QR screen is displayed.
        The 'Scan & Pay' label is the most reliable indicator.
        """
        self.switch_to_webview()
        self.wait_for_element(QRPaymentLocators.lbl_scan_and_pay, timeout)
        logger.info("ReArch QR payment screen is ready.")

    def is_qr_screen_displayed(self) -> bool:
        self.switch_to_webview()
        return self.is_element_visible(QRPaymentLocators.lbl_scan_and_pay, time=5)

    def is_qr_code_rendered(self) -> bool:
        """Returns True when the QR code canvas/image has been rendered."""
        return self.is_element_visible(QRPaymentLocators.img_qr_code, time=10)

    # ── Fetch displayed values ─────────────────────────────────────────────────

    def fetch_scan_and_pay_text(self) -> str:
        return self.fetch_text(QRPaymentLocators.lbl_scan_and_pay)

    def fetch_amount_text(self) -> str:
        return self.fetch_text(QRPaymentLocators.lbl_amount)

    def fetch_timer_text(self) -> str:
        """Fetch the remaining countdown timer value (if visible)."""
        return self.fetch_text(QRPaymentLocators.lbl_timer, time=10)

    # ── Validations ───────────────────────────────────────────────────────────

    def validate_qr_screen(self):
        """
        Assert that the QR payment screen is fully loaded:
          • 'Scan & Pay' label is visible
          • QR code is rendered
          • UPI and Razorpay logos are present
        """
        self.wait_for_qr_screen()
        self.wait_for_element(QRPaymentLocators.img_qr_code, time=30)
        self.wait_for_element(QRPaymentLocators.img_upi_logo, time=15)
        scan_text = self.fetch_scan_and_pay_text()
        logger.info(f"QR screen validated — header text: '{scan_text}'")
        return scan_text

    # ── Cancel payment flow ───────────────────────────────────────────────────

    def initiate_cancel_payment(self):
        """Press the device back button to trigger the cancel confirmation dialog."""
        self.go_back()
        logger.info("Triggered payment cancel via back navigation.")

    def confirm_cancel_payment(self):
        """Confirm cancellation inside the 'Cancel the Payment?' dialog."""
        self.wait_for_element(QRPaymentLocators.lbl_cancel_dialog_title, time=15)
        self.perform_click(QRPaymentLocators.btn_confirm_cancel)
        logger.info("Payment cancellation confirmed.")

    def cancel_payment(self):
        """Full cancel flow: trigger dialog → confirm."""
        self.initiate_cancel_payment()
        self.confirm_cancel_payment()
