from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import OrderDetailsLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchOrderDetailsPage(ReArchNativeBasePage):
    """Page object for the ReArch Order Details overlay (native context).

    This overlay appears after selecting a payment method (e.g. UPI) and
    contains an optional Order ID field, a Device Serial field, and Proceed/Cancel buttons.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_order_details_screen(self, timeout: int = 30):
        """Wait until the Order Details overlay is visible."""
        self.wait_for_element(OrderDetailsLocators.lbl_order_details, timeout)
        logger.info("Order Details screen is ready.")

    def is_order_details_displayed(self) -> bool:
        return self.is_element_visible(OrderDetailsLocators.lbl_order_details, time=5)

    # ── Input ─────────────────────────────────────────────────────────────────

    def enter_order_id(self, order_id: str):
        """Type an order ID into the Order ID input field."""
        self.perform_sendkeys(OrderDetailsLocators.txt_order_number, order_id)
        logger.info(f"Order ID entered: {order_id}")

    def enter_device_serial(self, serial: str):
        """Type a device serial / IMEI into the additional field input."""
        self.perform_sendkeys(OrderDetailsLocators.txt_additional_field, serial)
        logger.info(f"Device serial entered: {serial}")

    # ── Actions ───────────────────────────────────────────────────────────────

    def click_proceed(self):
        """Tap the Proceed button to advance past the Order Details overlay."""
        self.perform_click(OrderDetailsLocators.btn_proceed)
        logger.info("Clicked Proceed on Order Details screen.")

    def click_cancel(self):
        """Tap Cancel to dismiss the Order Details overlay."""
        self.perform_click(OrderDetailsLocators.btn_cancel)
        logger.info("Clicked Cancel on Order Details screen.")
