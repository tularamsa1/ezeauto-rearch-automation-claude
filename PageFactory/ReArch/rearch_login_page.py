from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import LoginLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchLoginPage(ReArchNativeBasePage):
    """Page object for the ReArch Login screen (native context)."""

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits / presence checks ───────────────────────────────────────────────

    def wait_for_login_page(self, timeout: int = 45):
        """Wait until the login page is fully rendered (username field visible)."""
        self.wait_for_element(LoginLocators.txt_username, timeout)
        logger.info("ReArch login page is ready.")

    def is_login_page_displayed(self) -> bool:
        return self.is_element_visible(LoginLocators.txt_username)

    def is_retry_page_displayed(self) -> bool:
        """Returns True when the network-error / retry state is shown."""
        return self.is_element_visible(LoginLocators.btn_retry, time=5)

    # ── Login actions ─────────────────────────────────────────────────────────

    def enter_username(self, username: str):
        self.perform_sendkeys(LoginLocators.txt_username, username)
        logger.debug(f"Entered username: {username}")

    def enter_password(self, password: str):
        self.perform_sendkeys(LoginLocators.txt_password, password)
        logger.debug("Entered password.")

    def click_login(self):
        self.perform_click(LoginLocators.btn_login)
        logger.info("Clicked Login button.")

    def perform_login(self, username: str, password: str):
        """Full login flow: wait for form -> enter credentials -> submit."""
        logger.info(f"Performing login for user: {username}")
        self.wait_for_element(LoginLocators.txt_username)
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        logger.info("Login submitted.")

    def toggle_password_visibility(self):
        self.perform_click(LoginLocators.btn_toggle_password)
        logger.debug("Toggled password visibility.")

    # ── Settings navigation ───────────────────────────────────────────────────

    def click_settings(self):
        self.perform_click(LoginLocators.btn_settings)
        logger.info("Clicked Settings from login screen.")

    # ── Network-error retry ───────────────────────────────────────────────────

    def click_retry(self):
        self.perform_click(LoginLocators.btn_retry)
        logger.info("Clicked Try Again (network retry).")

    # ── Validations ───────────────────────────────────────────────────────────

    def validate_login_page(self):
        """Assert that the Razorpay logo and username field are visible."""
        self.wait_for_element(LoginLocators.img_razorpay_logo)
        self.wait_for_element(LoginLocators.txt_username)
        logger.info("Login page validated successfully.")

    def fetch_snackbar_error(self) -> str:
        return self.fetch_text(LoginLocators.lbl_snackbar_error, time=10)

    def fetch_support_number(self) -> str:
        return self.fetch_text(LoginLocators.lbl_support_number)
