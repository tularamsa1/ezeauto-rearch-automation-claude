from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class FiltersPage(BasePage):
    rdo_card = (By.XPATH, "//android.widget.TextView[@text=\"Card\"]")
    rdo_success = (By.XPATH, "//android.widget.TextView[@text=\"Success\"]")
    btn_apply = (By.ID, "com.ezetap.service.demo:id/btnApply")
    btn_selectDate = (By.ID, "com.ezetap.service.demo:id/tvDR_CustomRange")
    btn_selectDateOk = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("OK")')
    btn_today = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvDR_Today')
    btn_this_week = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvDR_ThisWeek')
    btn_select_date_range = (AppiumBy.ID, 'com.ezetap.service.demo:id/tv_select_date_range')
    btn_payment_method_all = (AppiumBy.XPATH, '//*[@text="All"]')
    btn_payment_method_cash = (AppiumBy.XPATH, '//*[@text="Cash"]')
    btn_payment_method_card = (AppiumBy.XPATH, '//*[@text="Card"]')
    btn_payment_method_cheque = (AppiumBy.XPATH, '//*[@text="Cheque"]')
    btn_payment_method_bharat_qr = (AppiumBy.XPATH, '//*[@text="Bharat QR"]')
    btn_payment_method_upi = (AppiumBy.XPATH, '//*[@text="UPI"]')
    btn_payment_method_pay_link = (AppiumBy.XPATH, '//*[@text="Pay Link"]')
    btn_txn_status_all = (AppiumBy.XPATH, '//*[@text="All"]')
    btn_txn_status_success = (AppiumBy.XPATH, '//*[@text="Success"]')
    btn_txn_status_pending = (AppiumBy.XPATH, '//*[@text="Pending"]')
    btn_txn_status_failed = (AppiumBy.XPATH, '//*[@text="Failed"]')
    btn_txn_status_void_or_refund = (AppiumBy.XPATH, '//*[@text="Void/Refund"]')
    btn_txn_status_is_settled = (AppiumBy.XPATH, '//*[@text="Is Settled"]')
    btn_sort_by_date_descending = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivDateUp')
    btn_sort_by_date_ascending = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivDateDown')
    btn_sort_by_amount_descending = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivAmtUp')
    btn_sort_by_amount_ascending = (AppiumBy.ID, 'com.ezetap.service.demo:id/ivAmtDown')
    btn_from_date = (AppiumBy.ID, 'com.ezetap.service.demo:id/tv_start_date')
    btn_to_date = (AppiumBy.ID, 'com.ezetap.service.demo:id/tv_end_date')
    txt_tnx_history = (AppiumBy.XPATH, '(//*[@resource-id="com.ezetap.service.demo:id/clTxnView"])[1]')

    def __init__(self, driver):
        super().__init__(driver)

    def apply_filter_card_and_success(self):
        """
        performs click on the card in the txn type and success in the txn status
        """
        self.perform_click(self.rdo_card)
        TouchAction(self.driver).press(x=317, y=980).move_to(x=315, y=148).release().perform()
        self.perform_click(self.rdo_success)
        self.perform_click(self.btn_apply)

    def click_on_apply_filter(self):
        """
        performs click on the apply button
        """
        self.perform_click(self.btn_apply)

    def click_on_select_date(self):
        """
        performs click on the select date button
        """
        self.perform_click(self.btn_selectDate)

    def select_particular_date(self, date: str):
        """
        performs click on the particular date
        param: date: str
        """
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + date + ''))

    def click_ok_button(self):
        """
        performs click in the ok button
        """
        self.perform_click(self.btn_selectDateOk)

    def click_on_today(self):
        """
        performs click on today button on the txn filter page
        """
        self.perform_click(self.btn_today)

    def click_on_this_week(self):
        """
        performs click on this week on the txn filter page
        """
        self.perform_click(self.btn_this_week)

    def click_on_select_date_range(self, from_date: str, to_date: str):
        """
        performs selection of date range on the txn filter page to get the txn details in that date range
        param: from_date
        param: to_date
        """
        self.perform_click(self.btn_select_date_range)
        self.perform_click(self.btn_from_date)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + from_date + ''))
        self.perform_click(self.btn_selectDateOk)
        self.perform_click(self.btn_to_date)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + to_date + ''))
        self.perform_click(self.btn_selectDateOk)

    def click_on_payment_method_all(self):
        """
        performs click on payment mode all in the filter page
        """
        self.wait_for_element(self.btn_payment_method_all)
        self.perform_click(self.btn_payment_method_all)

    def click_on_payment_method_cash(self):
        """
        performs click on the cash txn
        """
        self.wait_for_element(self.btn_payment_method_cash)
        self.perform_click(self.btn_payment_method_cash)

    def click_on_payment_method_card(self):
        """
        performs click on the card txn
        """
        self.wait_for_element(self.btn_payment_method_card)
        self.perform_click(self.btn_payment_method_card)

    def click_on_payment_method_cheque(self):
        """
        performs click on the cheque txn
        """
        self.wait_for_element(self.btn_payment_method_cheque)
        self.perform_click(self.btn_payment_method_cheque)

    def click_on_payment_method_bharat_qr(self):
        """
        performs click on the bharat Qr txn
        """
        self.wait_for_element(self.btn_payment_method_bharat_qr)
        self.perform_click(self.btn_payment_method_bharat_qr)

    def click_on_payment_method_upi(self):
        """
        performs click on the upi txn
        """
        self.wait_for_element(self.btn_payment_method_upi)
        self.perform_click(self.btn_payment_method_upi)

    def click_on_payment_method_pay_link(self):
        """
        performs click on the pay link(cnp) txn
        """
        self.wait_for_element(self.btn_payment_method_pay_link)
        self.perform_click(self.btn_payment_method_pay_link)

    def click_on_txn_status_all(self):
        """
        performs click on the status all
        """
        self.wait_for_element(self.btn_txn_status_all)
        self.perform_click(self.btn_txn_status_all)

    def click_on_txn_status_success(self):
        """
        performs click on the status success
        """
        self.wait_for_element(self.btn_txn_status_success)
        self.perform_click(self.btn_txn_status_success)

    def click_on_txn_status_failed(self):
        """
        performs click on the status fail
        """
        self.wait_for_element(self.btn_txn_status_failed)
        self.perform_click(self.btn_txn_status_failed)

    def click_on_txn_status_pending(self):
        """
        performs click on the status pending
        """
        self.wait_for_element(self.btn_txn_status_pending)
        self.perform_click(self.btn_txn_status_pending)

    def click_on_txn_status_void_or_refund(self):
        """
        performs click on the status void or refund
        """
        self.wait_for_element(self.btn_txn_status_void_or_refund)
        self.perform_click(self.btn_txn_status_void_or_refund)

    def click_on_txn_status_is_settled(self):
        """
        performs click on the status is_settled
        """
        self.wait_for_element(self.btn_txn_status_is_settled)
        self.perform_click(self.btn_txn_status_is_settled)

    def click_on_sort_by_date_descending(self):
        """
        Perform click on the date descending to sort the transactions in descending order based on the date."
        """
        self.scroll_to_text('Sort By')
        self.wait_for_element(self.btn_sort_by_date_descending)
        self.perform_click(self.btn_sort_by_date_descending)

    def click_on_sort_by_date_ascending(self):
        """
        Perform click on the date ascending to sort the transactions in ascending order based on the date."
        """
        self.scroll_to_text('Sort By')
        self.wait_for_element(self.btn_sort_by_date_ascending)
        self.perform_click(self.btn_sort_by_date_ascending)

    def click_on_sort_by_amount_descending(self):
        """
        Perform click on the amount descending to sort the transactions in descending order based on the amount."
        """
        self.scroll_to_text('Sort By')
        self.wait_for_element(self.btn_sort_by_amount_descending)
        self.perform_click(self.btn_sort_by_amount_descending)

    def click_on_sort_by_amount_ascending(self):
        """
        Perform click on the amount ascending to sort the transactions in ascending order based on the amount."
        """
        self.scroll_to_text('Sort By')
        self.wait_for_element(self.btn_sort_by_date_ascending)
        self.perform_click(self.btn_sort_by_date_ascending)

    def click_on_first_txn_after_filtration(self):
        """
        performs click on the first txn after applying all the required filter
        """
        self.wait_for_element(self.txt_tnx_history)
        self.perform_click(self.txt_tnx_history)
