from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import EMILocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchEMIPage(ReArchNativeBasePage):
    """Page object for the ReArch EMI Plan Selection and Breakup screens (native context).

    Covers: EMI plan selection (bank/credit/debit tabs), bank selection,
    EMI plan radio buttons, view breakup, and amount verification.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_emi_screen(self, timeout: int = 30):
        """Wait until the Choose EMI Plans screen is displayed."""
        self.wait_for_element(EMILocators.lbl_choose_emi_plans, timeout)
        logger.info("EMI plan selection screen is ready.")

    def wait_for_bank_button(self, timeout: int = 30):
        """Wait until the Bank tab button is visible."""
        self.wait_for_element(EMILocators.btn_bank, timeout)
        logger.info("Bank button is visible on EMI screen.")

    def wait_for_breakup_sheet(self, timeout: int = 30):
        """Wait until the EMI breakup bottomsheet is displayed."""
        self.wait_for_element(EMILocators.lbl_emi_breakup_sheet, timeout)
        logger.info("EMI breakup bottomsheet is ready.")

    # ── Tab / Bank selection ──────────────────────────────────────────────────

    def click_bank_tab(self):
        """Tap the Bank tab."""
        self.perform_click(EMILocators.btn_bank)
        logger.info("Clicked Bank tab.")

    def click_credit_card_tab(self):
        """Tap the Credit Card tab."""
        self.perform_click(EMILocators.btn_credit_card)
        logger.info("Clicked Credit Card tab.")

    def click_hdfc_bank_credit_card(self):
        """Select HDFC Bank Credit Card."""
        self.perform_click(EMILocators.btn_hdfc_bank_credit)
        logger.info("Clicked HDFC Bank Credit Card.")

    def click_debit_card_tab(self):
        """Tap the Debit Card tab."""
        self.perform_click(EMILocators.btn_debit_card)
        logger.info("Clicked Debit Card tab.")

    def click_hdfc_bank_debit_card(self):
        """Select HDFC Bank Debit Card."""
        self.perform_click(EMILocators.btn_hdfc_bank_debit)
        logger.info("Clicked HDFC Bank Debit Card.")

    def click_sbi_bank_credit_card(self):
        """Select SBI Bank Credit Card."""
        self.perform_click(EMILocators.btn_sbi_bank_credit)
        logger.info("Clicked SBI Bank Credit Card.")

    # ── EMI Plan selection ────────────────────────────────────────────────────

    def click_3m_plan(self):
        """Select the 3-month EMI plan radio button."""
        self.perform_click(EMILocators.rdb_3m_plan)
        logger.info("Selected 3-month EMI plan.")

    def click_3m_no_cost_plan(self):
        """Select the 3-month No Cost EMI plan radio button."""
        self.perform_click(EMILocators.rdb_3m_no_cost_plan)
        logger.info("Selected 3-month No Cost EMI plan.")

    # ── View Breakup ──────────────────────────────────────────────────────────

    def click_view_breakup(self):
        """Tap the View Breakup button."""
        self.perform_click(EMILocators.btn_view_breakup)
        logger.info("Clicked View Breakup.")

    def fetch_order_total(self) -> str:
        """Fetch the Order Total value from the breakup sheet (Credit Card EMI)."""
        return self.fetch_text(EMILocators.val_order_total)

    def fetch_item_price(self) -> str:
        """Fetch the Item Price value from the breakup sheet."""
        return self.fetch_text(EMILocators.val_item_price)

    def fetch_mydiscount(self) -> str:
        """Fetch the MyDiscount value from the breakup sheet (No Cost EMI)."""
        return self.fetch_text(EMILocators.val_mydiscount)

    def fetch_interest_charged(self) -> str:
        """Fetch the Interest charged by Bank value from the breakup sheet."""
        return self.fetch_text(EMILocators.val_interest_charged)

    def fetch_total_amount(self) -> str:
        """Fetch the Total Amount value from the breakup sheet."""
        return self.fetch_text(EMILocators.val_total_amount)

    # ── Navigation ────────────────────────────────────────────────────────────

    def click_proceed(self):
        """Tap the Proceed button on the EMI screen."""
        self.perform_click(EMILocators.btn_proceed)
        logger.info("Clicked Proceed on EMI screen.")
