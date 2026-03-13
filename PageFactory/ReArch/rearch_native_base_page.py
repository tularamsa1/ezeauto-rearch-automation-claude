import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PageFactory.ReArch.rearch_native_locators import REARCH_PACKAGE
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchNativeBasePage:
    """
    Base page for the ReArch application using NATIVE_APP context only.

    The ReArch app (com.razorpay.pos) is a hybrid WebView app, but all its UI
    elements are accessible as native Android widgets through uiautomator.
    This base page operates entirely in NATIVE_APP context, eliminating the
    need for WebView context switching and making tests faster and more stable.

    All locators should use AppiumBy (defined in rearch_native_locators.py).
    """

    def __init__(self, driver):
        self.driver = driver

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

    def perform_click_index(self, locator, index: int, time: int = 45):
        """Click the nth element matching the locator (0-based)."""
        elements = WebDriverWait(self.driver, time).until(
            EC.presence_of_all_elements_located(locator)
        )
        elements[index].click()

    # ── Scroll helpers (native only) ─────────────────────────────────────────

    def scroll_to_text(self, text: str):
        """Scroll using UiScrollable to bring a text element into view."""
        try:
            return self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                f'.scrollIntoView(new UiSelector().text("{text}").instance(0));',
            )
        except NoSuchElementException:
            logger.warning(f"scroll_to_text: '{text}' not found")
            return None

    def swipe_up(self, duration_ms: int = 800):
        """Swipe up on the screen (scroll content down)."""
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.7)
        end_y = int(size["height"] * 0.3)
        self.driver.swipe(start_x, start_y, start_x, end_y, duration_ms)

    def swipe_down(self, duration_ms: int = 800):
        """Swipe down on the screen (scroll content up)."""
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.3)
        end_y = int(size["height"] * 0.7)
        self.driver.swipe(start_x, start_y, start_x, end_y, duration_ms)

    def swipe_up_multiple(self, count: int = 3, duration_ms: int = 800):
        for _ in range(count):
            self.swipe_up(duration_ms)
            time.sleep(0.5)

    # ── Navigation ───────────────────────────────────────────────────────────

    def go_back(self):
        """Press the Android hardware back button."""
        self.driver.back()

    # ── App lifecycle helpers ────────────────────────────────────────────────

    def launch_app(self):
        """Launch or bring the ReArch app to the foreground."""
        self.driver.activate_app(REARCH_PACKAGE)
        logger.info(f"Launched {REARCH_PACKAGE}")

    def terminate_app(self):
        """Force-stop the ReArch app."""
        self.driver.terminate_app(REARCH_PACKAGE)
        logger.info(f"Terminated {REARCH_PACKAGE}")

    def is_app_running(self) -> bool:
        """Check if the ReArch app is in the foreground."""
        state = self.driver.query_app_state(REARCH_PACKAGE)
        return state == 4  # RUNNING_IN_FOREGROUND
