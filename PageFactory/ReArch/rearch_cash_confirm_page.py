from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import CashConfirmLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchCashConfirmPage(ReArchNativeBasePage):
    """Page object for the ReArch Cash Payment Confirmation screen (native context).

    This screen appears after selecting Cash as the payment method. It shows the
    payment amount and a 'Confirm Payment' button to record the cash transaction.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_cash_confirm_screen(self, timeout: int = 30):
        """Wait until the cash confirmation screen is displayed."""
        self.wait_for_element(CashConfirmLocators.btn_confirm_payment, timeout)
        logger.info("Cash confirmation screen is ready.")

    def is_cash_confirm_displayed(self) -> bool:
        return self.is_element_visible(CashConfirmLocators.btn_confirm_payment, time=5)

    # ── Fetch ─────────────────────────────────────────────────────────────────

    def fetch_tap_confirm_text(self) -> str:
        return self.fetch_text(CashConfirmLocators.lbl_tap_confirm)

    def is_payment_amount_displayed(self) -> bool:
        return self.is_element_visible(CashConfirmLocators.lbl_payment_amount, time=5)

    # ── Actions ───────────────────────────────────────────────────────────────

    def click_confirm_payment(self):
        """Tap the Confirm Payment button to record the cash transaction."""
        self.perform_click(CashConfirmLocators.btn_confirm_payment)
        logger.info("Cash payment confirmed.")

    # ── Compound flow ─────────────────────────────────────────────────────────

    def wait_and_confirm_cash_payment(self, timeout: int = 30):
        """Wait for the cash confirm screen and confirm the payment."""
        self.wait_for_cash_confirm_screen(timeout)
        self.click_confirm_payment()
        logger.info("Cash payment confirmed via compound flow.")
