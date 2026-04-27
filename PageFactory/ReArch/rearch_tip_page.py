from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import TipDetailsLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchTipPage(ReArchNativeBasePage):
    """Page object for the ReArch Tip Details screen (native context).

    Covers: tip percentage buttons, custom amount entry, payment details,
    and Done button.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_tip_screen(self, timeout: int = 30):
        """Wait until the tip details screen is displayed."""
        self.wait_for_element(TipDetailsLocators.lbl_want_to_leave_a_tip, timeout)
        logger.info("Tip details screen is ready.")

    # ── Tip percentage verification (amount=515, multiTipPercentage="6, 11, 16") ──

    def is_6_percent_displayed(self, timeout: int = 10) -> bool:
        """Check if the 6% tip button (₹31 6%) is visible."""
        return self.is_element_visible(TipDetailsLocators.btn_31_6, time=timeout)

    def is_11_percent_displayed(self, timeout: int = 10) -> bool:
        """Check if the 11% tip button (₹57 11%) is visible."""
        return self.is_element_visible(TipDetailsLocators.btn_57_11, time=timeout)

    # ── Actions ───────────────────────────────────────────────────────────────

    def click_6_percent(self):
        """Select the 6% tip button."""
        self.perform_click(TipDetailsLocators.btn_31_6)
        logger.info("Clicked 6% tip (₹31).")

    def click_11_percent(self):
        """Select the 11% tip button."""
        self.perform_click(TipDetailsLocators.btn_57_11)
        logger.info("Clicked 11% tip (₹57).")

    def click_done(self):
        """Tap the Done button."""
        self.perform_click(TipDetailsLocators.btn_done)
        logger.info("Clicked Done on tip screen.")
