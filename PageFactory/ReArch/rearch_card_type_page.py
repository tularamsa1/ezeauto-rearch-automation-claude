from appium.webdriver.common.appiumby import AppiumBy

from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import CardTypeSelectionLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchCardTypePage(ReArchNativeBasePage):
    """Page object for the ReArch card type selection screen (DUMMY / test simulator).

    This screen appears after selecting Card as the payment method and proceeding
    through the Order Details overlay. It shows a scrollable list of test card
    types (Visa, Mastercard, RuPay) to simulate physical card insertion.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_card_type_screen(self, timeout: int = 30):
        """Wait until the card type selection screen is displayed."""
        self.wait_for_element(CardTypeSelectionLocators.lbl_select_test_card, timeout)
        logger.info("Card type selection screen is ready.")

    def is_card_type_screen_displayed(self) -> bool:
        return self.is_element_visible(CardTypeSelectionLocators.lbl_select_test_card, time=5)

    # ── Actions ───────────────────────────────────────────────────────────────

    def select_card_type(self, card_name: str):
        """Select a card type by its display name prefix (e.g. 'Visa Debit (EMV)').

        Scrolls to the card if it is not currently in view before clicking.
        """
        locator = CardTypeSelectionLocators.card_type_btn(card_name)
        if not self.is_element_visible(locator, time=2):
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                f'.scrollIntoView(new UiSelector().textStartsWith("{card_name}").instance(0));',
            )
        self.perform_click(locator)
        logger.info(f"Selected card type: {card_name}")

    def click_visa_debit_emv(self):
        """Select Visa Debit (EMV) from the card type list."""
        self.select_card_type("Visa Debit (EMV)")

    def click_visa_debit_with_pin_emv(self):
        """Select Visa Debit with PIN (EMV) from the card type list."""
        self.select_card_type("Visa Debit with PIN (EMV)")

    def click_visa_debit_with_pin_contactless(self):
        """Select Visa Debit with PIN (Contactless) from the card type list."""
        self.select_card_type("Visa Debit with PIN (Contactless)")

    def click_visa_debit_contactless(self):
        """Select Visa Debit (Contactless) from the card type list."""
        self.select_card_type("Visa Debit (Contactless)")

    def click_visa_credit_emv(self):
        """Select Visa Credit (EMV) from the card type list."""
        self.select_card_type("Visa Credit (EMV)")

    def click_mastercard_debit_emv(self):
        """Scroll to and select MasterCard Debit (EMV) from the card type list."""
        self.scroll_to_text("MasterCard Debit (EMV)")
        self.perform_click(CardTypeSelectionLocators.card_type_btn("MasterCard Debit (EMV)"))

    def click_mastercard_debit_contactless(self):
        """Select MasterCard Debit (Contactless) from the card type list."""
        self.select_card_type("MasterCard Debit (Contactless)")

    def click_rupay_debit_emv(self):
        """Select RuPay Debit (EMV) from the card type list."""
        self.select_card_type("RuPay Debit (EMV)")
