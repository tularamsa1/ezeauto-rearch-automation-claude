from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import HomeAmountLocators, HomeScreen
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

_NUMPAD_LOCATORS = {
    "0": HomeAmountLocators.btn_numpad_0,
    "1": HomeAmountLocators.btn_numpad_1,
    "2": HomeAmountLocators.btn_numpad_2,
    "3": HomeAmountLocators.btn_numpad_3,
    "4": HomeAmountLocators.btn_numpad_4,
    "5": HomeAmountLocators.btn_numpad_5,
    "6": HomeAmountLocators.btn_numpad_6,
    "7": HomeAmountLocators.btn_numpad_7,
    "8": HomeAmountLocators.btn_numpad_8,
    "9": HomeAmountLocators.btn_numpad_9,
}


class ReArchHomePage(ReArchNativeBasePage):
    """Page object for the ReArch Amount / Home screen (native context)."""

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_home_page_load(self, timeout: int = 45):
        """Wait until the amount page numpad is visible."""
        self.wait_for_element(HomeAmountLocators.btn_numpad_1, timeout)
        logger.info("ReArch home/amount page is ready.")

    def is_home_page_displayed(self) -> bool:
        return self.is_element_visible(HomeAmountLocators.btn_numpad_1, time=5)

    # ── Amount entry ──────────────────────────────────────────────────────────

    def enter_amount(self, amount):
        """
        Type an amount using the on-screen numpad.
        Accepts int or str; handles digits only (no dot in native numpad).
        """
        amount_str = str(amount)
        logger.debug(f"Entering amount via numpad: {amount_str}")
        for char in amount_str:
            locator = _NUMPAD_LOCATORS.get(char)
            if locator:
                self.perform_click(locator)
            else:
                logger.warning(f"No numpad locator for character '{char}' -- skipping.")
        logger.info(f"Amount entered: {amount_str}")

    def clear_amount(self):
        """Clear the amount display by pressing numpad back repeatedly."""
        for _ in range(10):
            if not self.is_element_visible(HomeAmountLocators.btn_numpad_back, time=1):
                break
            self.perform_click(HomeAmountLocators.btn_numpad_back)

    # ── Payment method selection ───────────────────────────────────────────────

    def click_pay_by_card(self):
        self.perform_click(HomeAmountLocators.btn_card)
        logger.info("Clicked Card payment button.")

    def click_pay_by_upi(self):
        self.perform_click(HomeAmountLocators.btn_upi)
        logger.info("Clicked UPI payment button.")

    def click_more_payment_options(self):
        """Tap the ⋯ button beside UPI to open the full payment method overlay."""
        self.perform_click(HomeAmountLocators.btn_more_payment_options)
        logger.info("Clicked More Payment Options (⋯) button.")

    def click_pay_by_cash(self):
        """Click Cash on the home screen (triggers payment method overlay if not directly visible)."""
        from PageFactory.ReArch.rearch_native_locators import PaymentMethodLocators
        if self.is_element_visible(PaymentMethodLocators.btn_cash, time=3):
            self.perform_click(PaymentMethodLocators.btn_cash)


    # ── Navigation helpers ────────────────────────────────────────────────────

    def click_menu(self):
        """Open the side/bottom menu."""
        self.perform_click(HomeAmountLocators.btn_menu)
        logger.info("Clicked Menu (hamburger) button.")

    def click_txn_history(self):
        """Navigate to Transaction History from the amount screen header."""
        self.perform_click(HomeAmountLocators.btn_txn_history)
        logger.info("Clicked Transaction History button.")

    # ── Tip ───────────────────────────────────────────────────────────────────

    def click_add_tip(self):
        self.perform_click(HomeAmountLocators.btn_add_tip)
        logger.info("Clicked Add Tip button.")

    def is_add_tip_visible(self) -> bool:
        return self.is_element_visible(HomeAmountLocators.btn_add_tip, time=5)

    # ── Initial home screen (post-login dashboard) ────────────────────────────

    def wait_for_initial_home_screen(self, timeout: int = 45):
        """Wait until the post-login home screen (Collect Payment button) is visible."""
        self.wait_for_element(HomeScreen.btn_collect_payment, timeout)
        logger.info("ReArch initial home screen is ready.")

    def click_collect_payment(self):
        """Tap the Collect Payment button on the initial home screen."""
        self.perform_click(HomeScreen.btn_collect_payment)
        logger.info("Clicked Collect Payment button.")

    def click_transactions(self):
        """Tap the Transactions button on the initial home screen to navigate to Payment History."""
        self.perform_click(HomeScreen.btn_transactions)
        logger.info("Clicked Transactions button.")

    def click_help(self):
        """Tap the Help button on the initial home screen to navigate to Help Center."""
        self.perform_click(HomeScreen.btn_help)
        logger.info("Clicked Help button.")

    def click_other_apps(self):
        """Tap the Other Apps button on the initial home screen."""
        self.perform_click(HomeScreen.btn_other_apps)
        logger.info("Clicked Other Apps button.")

    # ── Compound flows ────────────────────────────────────────────────────────

    def enter_amount_and_proceed_upi(self, amount):
        """Enter the given amount and initiate a UPI payment."""
        self.wait_for_home_page_load()
        self.enter_amount(amount)
        self.click_pay_by_upi()
        logger.info(f"Initiated UPI payment for amount: {amount}")

    def enter_amount_and_proceed_card(self, amount):
        """Enter the given amount and initiate a Card payment."""
        self.wait_for_home_page_load()
        self.enter_amount(amount)
        self.click_pay_by_card()
        logger.info(f"Initiated Card payment for amount: {amount}")

    def enter_amount_and_proceed_cash(self, amount):
        """Enter the given amount and initiate a Cash payment."""
        self.wait_for_home_page_load()
        self.enter_amount(amount)
        self.click_pay_by_cash()
        logger.info(f"Initiated Cash payment for amount: {amount}")
