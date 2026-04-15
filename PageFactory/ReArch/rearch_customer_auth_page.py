from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import CustomerAuthLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchCustomerAuthPage(ReArchNativeBasePage):
    """Page object for the ReArch Customer Auth / PAN entry screen (native context).

    This screen appears when customerAuthDataCaptureEnabled is true and the
    transaction amount is below amountCutOffForCustomerAuth. It requires
    entering a PAN number before confirming payment.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_customer_auth_screen(self, timeout: int = 30):
        """Wait until the PAN entry screen is displayed."""
        self.wait_for_element(CustomerAuthLocators.txt_pan_number, timeout)
        logger.info("Customer Auth / PAN entry screen is ready.")

    # ── Actions ───────────────────────────────────────────────────────────────

    def enter_pan_number(self, pan: str):
        """Tap the PAN text field and enter the PAN number."""
        self.perform_sendkeys(CustomerAuthLocators.txt_pan_number, pan)
        logger.info(f"PAN number entered: {pan}")

    def click_confirm_payment(self):
        """Tap the Confirm Payment button on the PAN entry screen."""
        self.perform_click(CustomerAuthLocators.btn_confirm_payment)
        logger.info("Confirm Payment clicked on Customer Auth screen.")
