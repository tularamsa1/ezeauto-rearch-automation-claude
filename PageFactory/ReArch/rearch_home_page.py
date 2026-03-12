from PageFactory.ReArch.rearch_base_page import ReArchBasePage
from PageFactory.ReArch.rearch_locators import AmountLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

# Digit-to-locator map for numpad entry
_NUMPAD_LOCATORS = {
    "0": AmountLocators.btn_numpad_0,
    "1": AmountLocators.btn_numpad_1,
    "2": AmountLocators.btn_numpad_2,
    "3": AmountLocators.btn_numpad_3,
    "4": AmountLocators.btn_numpad_4,
    "5": AmountLocators.btn_numpad_5,
    "6": AmountLocators.btn_numpad_6,
    "7": AmountLocators.btn_numpad_7,
    "8": AmountLocators.btn_numpad_8,
    "9": AmountLocators.btn_numpad_9,
    ".": AmountLocators.btn_numpad_dot,
}


class ReArchHomePage(ReArchBasePage):
    """
    Page object for the ReArch Amount / Home screen.
    Source: pos/web/src/pages/pay/amount.svelte
            pos/web/src/base/rzp/numpad.svelte
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_home_page_load(self, timeout: int = 45):
        """Wait until the amount page numpad is visible."""
        self.switch_to_webview()
        self.wait_for_element(AmountLocators.btn_numpad_1, timeout)
        logger.info("ReArch home/amount page is ready.")

    def is_home_page_displayed(self) -> bool:
        self.switch_to_webview()
        return self.is_element_visible(AmountLocators.btn_numpad_1, time=5)

    # ── Amount entry ──────────────────────────────────────────────────────────

    def enter_amount(self, amount):
        """
        Type an amount using the on-screen numpad.
        Accepts int or str; handles digits and '.' separator.
        """
        amount_str = str(amount)
        logger.debug(f"Entering amount via numpad: {amount_str}")
        for char in amount_str:
            locator = _NUMPAD_LOCATORS.get(char)
            if locator:
                self.perform_click(locator)
            else:
                logger.warning(f"No numpad locator for character '{char}' — skipping.")
        logger.info(f"Amount entered: {amount_str}")

    def fetch_displayed_amount(self) -> str:
        return self.fetch_text(AmountLocators.lbl_amount_display)

    # ── Payment method selection ───────────────────────────────────────────────

    def click_collect_payment(self):
        """Tap 'Collect Payment' (shown when no specific method is pre-configured)."""
        self.perform_click(AmountLocators.btn_collect_payment)
        logger.info("Clicked Collect Payment.")

    def click_pay_by_card(self):
        self.perform_click(AmountLocators.btn_pay_by_card)
        logger.info("Clicked Card payment button.")

    def click_pay_by_upi(self):
        self.perform_click(AmountLocators.btn_pay_by_upi)
        logger.info("Clicked UPI payment button.")

    def click_pay_by_bqr(self):
        self.perform_click(AmountLocators.btn_pay_by_bqr)
        logger.info("Clicked Bharat QR payment button.")

    def click_other_methods(self):
        """Tap the 'Others' union button to see all payment methods."""
        self.perform_click(AmountLocators.btn_other_methods)
        logger.info("Clicked Other payment methods.")

    # ── Navigation helpers ────────────────────────────────────────────────────

    def click_menu(self):
        """Open the side/bottom menu."""
        self.perform_click(AmountLocators.btn_menu)
        logger.info("Clicked Menu (hamburger) button.")

    def click_txn_history(self):
        """Navigate to Transaction History from the amount screen header."""
        self.perform_click(AmountLocators.btn_txn_history)
        logger.info("Clicked Transaction History button.")

    # ── Tip ───────────────────────────────────────────────────────────────────

    def click_add_tip(self):
        self.perform_click(AmountLocators.btn_add_tip)
        logger.info("Clicked Add Tip button.")

    def is_add_tip_visible(self) -> bool:
        return self.is_element_visible(AmountLocators.btn_add_tip, time=5)

    # ── Compound flow ─────────────────────────────────────────────────────────

    def enter_amount_and_proceed_upi(self, amount):
        """
        Enter the given amount and initiate a UPI payment.
        Falls back to 'Collect Payment' if the UPI button is not shown.
        """
        self.wait_for_home_page_load()
        self.enter_amount(amount)

        if self.is_element_visible(AmountLocators.btn_pay_by_upi, time=3):
            self.click_pay_by_upi()
        else:
            self.click_collect_payment()
        logger.info(f"Initiated UPI payment for amount: {amount}")

    def enter_amount_and_proceed_card(self, amount):
        """Enter the given amount and initiate a Card payment."""
        self.wait_for_home_page_load()
        self.enter_amount(amount)

        if self.is_element_visible(AmountLocators.btn_pay_by_card, time=3):
            self.click_pay_by_card()
        else:
            self.click_collect_payment()
        logger.info(f"Initiated Card payment for amount: {amount}")
