from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import DemandDraftLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchDemandDraftPage(ReArchNativeBasePage):
    """Page object for the ReArch Demand Draft payment form (native context).

    Covers: DD number entry, bank selection (dropdown), branch name entry,
    DD date picker, and Confirm Payment submission.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_dd_form(self, timeout: int = 30):
        """Wait until the demand draft payment form is displayed."""
        self.wait_for_element(DemandDraftLocators.txt_enter_dd_number, timeout)
        logger.info("Demand Draft payment form is ready.")

    # ── DD Number ─────────────────────────────────────────────────────────────

    def enter_dd_number(self, dd_number: str):
        """Click the DD number field and type the number."""
        self.perform_click(DemandDraftLocators.txt_enter_dd_number)
        self.perform_sendkeys(DemandDraftLocators.txt_enter_dd_number, dd_number)
        logger.info(f"DD number entered: {dd_number}")

    # ── Bank Selection ────────────────────────────────────────────────────────

    def click_select_bank(self):
        """Tap the Select Bank dropdown button."""
        self.perform_click(DemandDraftLocators.btn_select_bank)
        logger.info("Clicked Select Bank.")

    def select_bank(self, bank_name: str):
        """Select a bank from the dropdown by name."""
        # self.scroll_to_text(bank_name)
        self.perform_click(DemandDraftLocators.bank_btn(bank_name))
        logger.info(f"Selected bank: {bank_name}")

    def click_apply(self):
        """Tap the Apply button (used by both bank dropdown and date picker)."""
        self.perform_click(DemandDraftLocators.btn_apply)
        logger.info("Clicked Apply.")

    # ── Branch Name ───────────────────────────────────────────────────────────

    def enter_branch_name(self, branch_name: str):
        """Click the Branch Name field and type the name."""
        self.perform_click(DemandDraftLocators.txt_enter_branch_name)
        self.perform_sendkeys(DemandDraftLocators.txt_enter_branch_name, branch_name)
        logger.info(f"Branch name entered: {branch_name}")

    # ── DD Date ───────────────────────────────────────────────────────────────

    def click_date_picker(self):
        """Tap the dd/mm/yyyy date button to open the date picker."""
        self.perform_click(DemandDraftLocators.btn_ddmmyyyy)
        logger.info("Clicked date picker (dd/mm/yyyy).")

    # ── Confirm ───────────────────────────────────────────────────────────────

    def click_confirm_payment(self):
        """Tap the Confirm Payment button to submit the DD form."""
        self.perform_click(DemandDraftLocators.btn_confirm_payment)
        logger.info("Clicked Confirm Payment on DD form.")

    # ── Error message verification ───────────────────────────────────────────

    def is_error_dd_number_displayed(self, timeout: int = 10) -> bool:
        """Check if 'DD number should be 6 digits' error is visible."""
        return self.is_element_visible(DemandDraftLocators.lbl_error_dd_number, time=timeout)

    def is_error_select_bank_displayed(self, timeout: int = 10) -> bool:
        """Check if 'Please select a bank' error is visible."""
        return self.is_element_visible(DemandDraftLocators.lbl_error_select_bank, time=timeout)

    def is_error_branch_name_displayed(self, timeout: int = 10) -> bool:
        """Check if 'Please provide Branch Name' error is visible."""
        return self.is_element_visible(DemandDraftLocators.lbl_error_branch_name, time=timeout)

    def is_error_dd_date_displayed(self, timeout: int = 10) -> bool:
        """Check if 'Please enter DD Date' error is visible."""
        return self.is_element_visible(DemandDraftLocators.lbl_error_dd_date, time=timeout)
