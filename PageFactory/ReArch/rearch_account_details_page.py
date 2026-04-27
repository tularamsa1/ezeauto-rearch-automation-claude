from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import AccountDetailsLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchAccountDetailsPage(ReArchNativeBasePage):
    """Page object for the ReArch Account Details / Settings screen (native context).

    Covers: account info display (username, org_code), MID, TID,
    App Version, Web App Version, Devices.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_account_screen(self, timeout: int = 30):
        """Wait until the account details screen is displayed."""
        self.wait_for_element(AccountDetailsLocators.lbl_account, timeout)
        logger.info("Account details screen is ready.")

    # ── Navigation ────────────────────────────────────────────────────────────

    def click_org_code(self, org_code: str):
        """Tap the org_code button/text to open org details."""
        self.perform_click(AccountDetailsLocators.btn_text(org_code))
        logger.info(f"Clicked org_code: {org_code}")

    def click_relaunch_app(self):
        """Scroll down and tap the Relaunch App button."""
        self.scroll_to_text("Relaunch App")
        self.perform_click(AccountDetailsLocators.btn_relaunch_app)
        logger.info("Clicked Relaunch App.")

    def click_delete_cache_and_relaunch(self):
        """Scroll down and tap the Delete Cache & Relaunch App button."""
        self.scroll_to_text("Delete Cache")
        self.perform_click(AccountDetailsLocators.btn_delete_cache_relaunch)
        logger.info("Clicked Delete Cache & Relaunch App.")

    def click_confirm_delete_relaunch(self):
        """Tap 'Yes, Delete & Relaunch' on the confirmation dialog."""
        self.perform_click(AccountDetailsLocators.btn_yes_delete_relaunch)
        logger.info("Confirmed Delete & Relaunch.")

    # ── Verification ──────────────────────────────────────────────────────────

    def is_mid_displayed(self, timeout: int = 10) -> bool:
        """Check if the MID label is visible."""
        return self.is_element_visible(AccountDetailsLocators.lbl_mid, time=timeout)

    def is_tid_displayed(self, timeout: int = 10) -> bool:
        """Check if the TID label is visible."""
        return self.is_element_visible(AccountDetailsLocators.lbl_tid, time=timeout)

    def is_text_displayed(self, text: str, timeout: int = 10) -> bool:
        """Check if a specific text (e.g. username) is visible on screen."""
        return self.is_element_visible(AccountDetailsLocators.lbl_text(text), time=timeout)
