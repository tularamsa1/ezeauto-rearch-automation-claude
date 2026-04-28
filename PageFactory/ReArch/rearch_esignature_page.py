from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import ESignatureLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchESignaturePage(ReArchNativeBasePage):
    """Page object for the ReArch eSignature capture screen (native context).

    This screen appears after cash/non-card confirm payment when
    eSignatureForNonCardEnabled is true. The user draws a signature,
    agrees to save it, then proceeds.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_esignature_screen(self, timeout: int = 30):
        """Wait until the eSignature agree checkbox is visible."""
        self.wait_for_element(ESignatureLocators.chk_agree_signature, timeout)
        logger.info("eSignature screen is ready.")

    # ── Actions ───────────────────────────────────────────────────────────────

    def draw_signature(self, start_x: int = 271, start_y: int = 588,
                       end_x: int = 441, end_y: int = 555, duration_ms: int = 800):
        """Draw a signature by swiping between the given coordinates."""
        self.driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
        logger.info(f"Signature drawn from ({start_x},{start_y}) to ({end_x},{end_y})")

    def click_agree_signature(self):
        """Tap the 'I agree to securely save my signature' checkbox."""
        self.perform_click(ESignatureLocators.chk_agree_signature)
        logger.info("Clicked agree to save signature checkbox.")

    def click_proceed(self):
        """Tap the Proceed button on the eSignature screen."""
        self.perform_click(ESignatureLocators.btn_proceed)
        logger.info("Clicked Proceed on eSignature screen.")

    def click_confirm_payment(self):
        """Tap the Confirm Payment button after eSignature."""
        self.perform_click(ESignatureLocators.btn_confirm_payment)
        logger.info("Clicked Confirm Payment after eSignature.")
