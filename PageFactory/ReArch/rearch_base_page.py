from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PageFactory.ReArch.rearch_locators import NativeLocators, REARCH_PACKAGE
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

_WEBVIEW_PREFIX = "WEBVIEW"
_NATIVE_CONTEXT = "NATIVE_APP"


class ReArchBasePage:
    """
    Base page for the ReArch application (com.razorpay.pos).

    The ReArch app is a hybrid WebView application: the Android shell wraps a
    Svelte/TypeScript web frontend served inside a WebView.  Appium must switch
    between two contexts:
      • NATIVE_APP  — for system dialogs, permission prompts, and identifying
                      the WebView container itself.
      • WEBVIEW_*   — for all in-app UI interaction (login, amount, payment,
                      transaction history, etc.) via HTML CSS / XPath selectors.

    All subclasses should call self.switch_to_webview() before interacting with
    page elements, and self.switch_to_native() when handling system-level
    dialogs.
    """

    def __init__(self, driver):
        self.driver = driver

    # ── Context management ────────────────────────────────────────────────────

    def switch_to_webview(self, timeout: int = 30) -> bool:
        """
        Switch Appium driver to the ReArch WebView context.
        Returns True on success, False if no WebView context is available.
        """
        end_time = __import__("time").time() + timeout
        while __import__("time").time() < end_time:
            contexts = self.driver.contexts
            webview_ctx = next(
                (c for c in contexts if _WEBVIEW_PREFIX in c and REARCH_PACKAGE in c),
                None,
            )
            if webview_ctx:
                self.driver.switch_to.context(webview_ctx)
                logger.debug(f"Switched to WebView context: {webview_ctx}")
                return True
            __import__("time").sleep(1)
        logger.warning("No WebView context found after waiting; staying in current context.")
        return False

    def switch_to_native(self):
        """Switch Appium driver back to the native Android context."""
        self.driver.switch_to.context(_NATIVE_CONTEXT)
        logger.debug("Switched to NATIVE_APP context.")

    def current_context(self) -> str:
        return self.driver.current_context

    # ── Core wait / interaction helpers ──────────────────────────────────────

    def wait_for_element(self, locator, time: int = 45):
        return WebDriverWait(self.driver, time).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_element_to_be_clickable(self, locator, time: int = 45):
        return WebDriverWait(self.driver, time).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_all_elements(self, locator, time: int = 45):
        return WebDriverWait(self.driver, time).until(
            EC.presence_of_all_elements_located(locator)
        )

    def wait_for_invisibility(self, locator, time: int = 30) -> bool:
        return WebDriverWait(self.driver, time).until(
            EC.invisibility_of_element_located(locator)
        )

    def perform_click(self, locator, time: int = 45):
        WebDriverWait(self.driver, time).until(
            EC.element_to_be_clickable(locator)
        ).click()

    def perform_sendkeys(self, locator, value: str, time: int = 45):
        element = WebDriverWait(self.driver, time).until(
            EC.visibility_of_element_located(locator)
        )
        element.clear()
        element.send_keys(value)

    def fetch_text(self, locator, time: int = 45) -> str:
        return WebDriverWait(self.driver, time).until(
            EC.presence_of_element_located(locator)
        ).text

    def is_element_present(self, locator, time: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, time).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def is_element_visible(self, locator, time: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, time).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def fetch_elements(self, locator, time: int = 45):
        return WebDriverWait(self.driver, time).until(
            EC.presence_of_all_elements_located(locator)
        )

    # ── Scroll helpers ────────────────────────────────────────────────────────

    def scroll_to_text_native(self, text: str):
        """
        Scroll (UiScrollable) in NATIVE_APP context to bring a text element
        into view.  Must be in NATIVE_APP context before calling.
        """
        try:
            return self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                f'.scrollIntoView(new UiSelector().text("{text}").instance(0));',
            )
        except NoSuchElementException:
            logger.warning(f"scroll_to_text_native: '{text}' not found")
            return None

    def scroll_to_element_webview(self, locator, time: int = 45):
        """
        Scroll a WebView element into view using JavaScript.
        Must be in WEBVIEW context before calling.
        """
        element = self.wait_for_element(locator, time)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        return element

    # ── Navigation ───────────────────────────────────────────────────────────

    def go_back(self):
        """Press the Android hardware back button."""
        self.driver.back()
