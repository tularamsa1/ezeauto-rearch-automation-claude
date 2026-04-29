from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import ChequePaymentLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchChequePage(ReArchNativeBasePage):
    """Page object for the ReArch Cheque Payment form (native context).

    Covers: cheque number entry, bank selection (dropdown), cheque date picker,
    IFSC code entry, and Confirm Payment submission.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_cheque_form(self, timeout: int = 30):
        """Wait until the cheque payment form is displayed."""
        self.wait_for_element(ChequePaymentLocators.txt_enter_cheque_number, timeout)
        logger.info("Cheque payment form is ready.")

    # ── Cheque Number ─────────────────────────────────────────────────────────

    def enter_cheque_number(self, cheque_number: str):
        """Click the cheque number field and type the number via Android system keyboard keycodes."""
        _DIGIT_KEYCODES = {
            "0": 7, "1": 8, "2": 9, "3": 10, "4": 11,
            "5": 12, "6": 13, "7": 14, "8": 15, "9": 16,
        }
        self.perform_click(ChequePaymentLocators.txt_enter_cheque_number)
        for char in str(cheque_number):
            keycode = _DIGIT_KEYCODES.get(char)
            if keycode:
                self.driver.press_keycode(keycode)
            else:
                logger.warning(f"No keycode for character '{char}' -- skipping.")
        logger.info(f"Cheque number entered: {cheque_number}")

    def perform_click_enter_cheque_number(self):
        """Click the cheque number field."""
        self.perform_click(ChequePaymentLocators.txt_enter_cheque_number)
        logger.info("Clicked on cheque number field.")

    def perform_click_on_confirm_payment(self):
        """Click the Confirm Payment button."""
        self.perform_click(ChequePaymentLocators.btn_confirm_payment)
        logger.info("Clicked on Confirm Payment button.")

    # ── Bank Selection ────────────────────────────────────────────────────────

    def click_select_bank(self):
        """Tap the Select Bank dropdown button."""
        self.perform_click(ChequePaymentLocators.btn_select_bank)
        logger.info("Clicked Select Bank.")

    def select_bank(self, bank_name: str):
        """Select a bank from the dropdown by name, then tap Apply."""
        self.scroll_to_text(bank_name)
        self.perform_click(ChequePaymentLocators.bank_btn(bank_name))
        logger.info(f"Selected bank: {bank_name}")

    def click_apply(self):
        """Tap the Apply button (used by both bank dropdown and date picker)."""
        self.perform_click(ChequePaymentLocators.btn_apply)
        logger.info("Clicked Apply.")

    # ── Cheque Date ───────────────────────────────────────────────────────────

    def click_date_picker(self):
        """Tap the dd/mm/yyyy date button to open the date picker."""
        self.perform_click(ChequePaymentLocators.btn_ddmmyyyy)
        logger.info("Clicked date picker (dd/mm/yyyy).")

    # ── IFSC Code ─────────────────────────────────────────────────────────────

    def enter_ifsc_code(self, ifsc_code: str):
        """Click the IFSC code field and type the code."""
        self.perform_click(ChequePaymentLocators.txt_enter_ifsc_code)
        self.perform_sendkeys(ChequePaymentLocators.txt_enter_ifsc_code, ifsc_code)
        logger.info(f"IFSC code entered: {ifsc_code}")

    # ── Confirm ───────────────────────────────────────────────────────────────

    def click_confirm_payment(self):
        """Tap the Confirm Payment button to submit the cheque form."""
        self.perform_click(ChequePaymentLocators.btn_confirm_payment)
        logger.info("Clicked Confirm Payment on cheque form.")

    # ── Error message verification ───────────────────────────────────────────

    def is_error_cheque_number_displayed(self, timeout: int = 10) -> bool:
        """Check if 'Cheque number should be 6 digits' error is visible."""
        return self.is_element_visible(ChequePaymentLocators.lbl_error_cheque_number, time=timeout)

    def is_error_select_bank_displayed(self, timeout: int = 10) -> bool:
        """Check if 'Please select a bank' error is visible."""
        return self.is_element_visible(ChequePaymentLocators.lbl_error_select_bank, time=timeout)

    def is_error_cheque_date_displayed(self, timeout: int = 10) -> bool:
        """Check if 'Please select Cheque Date' error is visible."""
        return self.is_element_visible(ChequePaymentLocators.lbl_error_cheque_date, time=timeout)

    def is_error_invalid_ifsc_displayed(self, timeout: int = 10) -> bool:
        """Check if 'Invalid Bank IFSC Code' error is visible."""
        return self.is_element_visible(ChequePaymentLocators.lbl_error_invalid_ifsc, time=timeout)
