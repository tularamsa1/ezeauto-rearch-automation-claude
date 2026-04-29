import re

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

    def get_relative_coordinate_for_signature(self):
        """Get relative coordinates for signature placement from 'Please sign here' bounds."""
        bounds_str = self.wait_for_element(ESignatureLocators.lbl_please_sign_here).get_attribute("bounds")
        matches = re.findall(r'\d+', bounds_str)
        if len(matches) >= 2:
            x = int(matches[0]) * 5
            y = round(int(matches[1]) * 1.25)
            return x, y
        else:
            logger.info("Not enough numeric values found in bounds string")

    def add_signature(self, x: int, y: int):
        """Add a signature by performing a swipe gesture from (x, y) to (x+60, y)."""
        from appium.webdriver.common.touch_action import TouchAction
        x2 = x + 60
        TouchAction(self.driver).press(x=x, y=y).move_to(x=x2, y=y).release().perform()
        logger.info(f"Signature drawn at ({x},{y}) to ({x2},{y})")

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
