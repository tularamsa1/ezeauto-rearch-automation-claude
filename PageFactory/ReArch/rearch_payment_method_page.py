from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
from PageFactory.ReArch.rearch_native_locators import PaymentMethodLocators
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class ReArchPaymentMethodPage(ReArchNativeBasePage):
    """Page object for the ReArch Payment Method Selection overlay (native context).

    This overlay appears after entering an amount, showing all available payment
    methods: UPI, Card, Cash, Payment Link, Pre Auth, Bharat QR, Cheque, Demand Draft.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_payment_methods(self, timeout: int = 30):
        """Wait until the payment method selection overlay is displayed."""
        self.wait_for_element(PaymentMethodLocators.lbl_payment_amount, timeout)
        logger.info("Payment method selection overlay is ready.")

    def is_payment_methods_displayed(self) -> bool:
        return self.is_element_visible(PaymentMethodLocators.lbl_payment_amount, time=5)

    # ── Payment method clicks ─────────────────────────────────────────────────

    def click_upi(self):
        self.perform_click(PaymentMethodLocators.btn_upi)
        logger.info("Selected UPI from payment methods.")

    def click_card(self):
        self.perform_click(PaymentMethodLocators.btn_card)
        logger.info("Selected Card from payment methods.")

    def click_cash(self):
        self.perform_click(PaymentMethodLocators.btn_cash)
        logger.info("Selected Cash from payment methods.")

    def click_payment_link(self):
        self.perform_click(PaymentMethodLocators.btn_payment_link)
        logger.info("Selected Payment Link from payment methods.")

    def click_pre_auth(self):
        self.perform_click(PaymentMethodLocators.btn_pre_auth)
        logger.info("Selected Pre Auth from payment methods.")

    def click_bharat_qr(self):
        self.scroll_to_text("Bharat QR")
        self.perform_click(PaymentMethodLocators.btn_bharat_qr)
        logger.info("Selected Bharat QR from payment methods.")

    def click_cheque(self):
        self.perform_click(PaymentMethodLocators.btn_cheque)
        logger.info("Selected Cheque from payment methods.")

    def click_demand_draft(self):
        self.perform_click(PaymentMethodLocators.btn_demand_draft)
        logger.info("Selected Demand Draft from payment methods.")

    def click_emi(self):
        self.scroll_to_text("EMI")
        self.perform_click(PaymentMethodLocators.btn_emi)
        logger.info("Selected EMI from payment methods.")

    def click_my_discount_emi(self):
        self.scroll_to_text("Demand Draft")
        self.perform_click(PaymentMethodLocators.btn_my_discount_emi)
        logger.info("Selected My Discount EMI from payment methods.")

    # ── Availability checks ───────────────────────────────────────────────────

    def is_cash_available(self) -> bool:
        return self.is_element_visible(PaymentMethodLocators.btn_cash, time=5)

    def is_upi_available(self) -> bool:
        return self.is_element_visible(PaymentMethodLocators.btn_upi, time=5)

    def is_card_available(self) -> bool:
        return self.is_element_visible(PaymentMethodLocators.btn_card, time=5)

    def is_payment_link_available(self) -> bool:
        return self.is_element_visible(PaymentMethodLocators.btn_payment_link, time=5)

    def is_cheque_available(self) -> bool:
        return self.is_element_visible(PaymentMethodLocators.btn_cheque, time=5)
