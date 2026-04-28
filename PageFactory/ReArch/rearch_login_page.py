from appium.webdriver.common.appiumby import AppiumBy

from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import LoginLocators, OnboardingLocators
from Utilities import ConfigReader
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

    # ── Conditional login (handles auto-login vs manual login) ───────────────

    def is_select_environment_displayed(self, timeout: int = 10) -> bool:
        """Check if the Select Environment screen appears (manual login flow)."""
        return self.is_element_visible(OnboardingLocators.lbl_select_environment, time=timeout)



    def perform_login_if_required(self, username: str, password: str):
        """Handle login only if the Select Environment screen appears.

        Auto-login flow: app lands directly on the home screen — nothing to do.
        Manual login flow: [Select Environment →] Login → Don't show again → Next → Next → Start.
        The Select Environment screen may or may not appear.
        """
        if not self.is_select_environment_displayed():
            logger.info("Select Environment not displayed — auto-login flow, skipping login")
            return

        logger.info("Select Environment screen detected — performing manual login flow")

        # Step 1: Scroll to environment and tap
        env_name = ConfigReader.read_config("environment", "str_exe_env")
        logger.debug(f"Environment from config: {env_name}")
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
            f'.scrollIntoView(new UiSelector().textContains("{env_name}").instance(0));',
        ).click()
        logger.debug(f"Environment '{env_name}' selected")

        # Step 2: Enter credentials and tap Login (always required after env selection or directly)
        self.wait_for_element(LoginLocators.txt_username)
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

        # Step 3: Check "Don't show me again" checkbox
        self.perform_click(OnboardingLocators.chk_dont_show_again)
        logger.debug("Checked 'Don't show me again'")

        # Step 4: Tap Next twice
        self.perform_click(OnboardingLocators.btn_next)
        logger.debug("Clicked Next (1/2)")
        self.perform_click(OnboardingLocators.btn_next)
        logger.debug("Clicked Next (2/2)")

        # Step 5: Tap Start
        self.perform_click(OnboardingLocators.btn_start)
        logger.info("Clicked Start — manual login flow completed")

