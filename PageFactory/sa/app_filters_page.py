from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.by import By
from PageFactory.App_BasePage import BasePage


class FiltersPage(BasePage):

    rdo_card = (By.XPATH, "//android.widget.TextView[@text=\"Card\"]")
    rdo_success = (By.XPATH, "//android.widget.TextView[@text=\"Success\"]")
    btn_apply = (By.ID, "com.ezetap.service.demo:id/btnApply")
    btn_selectDate = (By.ID, "com.ezetap.service.demo:id/tvDR_CustomRange")
    btn_selectDateOk = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("OK")')
    btn_today = (AppiumBy.ID,'com.ezetap.service.demo:id/tvDR_Today')
    btn_this_week = (AppiumBy.ID,'com.ezetap.service.demo:id/tvDR_ThisWeek')
    btn_select_date_range = (AppiumBy.ID,'com.ezetap.service.demo:id/tv_select_date_range')
    btn_payment_method_all = (AppiumBy.XPATH, '//*[@text="All"]')
    btn_payment_method_cash = (AppiumBy.XPATH, '//*[@text="Cash"]')
    btn_payment_method_card = (AppiumBy.XPATH,'//*[@text="Card"]')
    btn_payment_method_cheque = (AppiumBy.XPATH,'//*[@text="Cheque"]')
    btn_payment_method_bharat_qr = (AppiumBy.XPATH,'//*[@text="Bharat QR"]')
    btn_payment_method_upi = (AppiumBy.XPATH,'//*[@text="UPI"]')
    btn_payment_method_pay_link = (AppiumBy.XPATH,'//*[@text="Pay Link"]')
    btn_txn_status_all = (AppiumBy.XPATH,'//*[@text="All"]')
    btn_txn_status_success = (AppiumBy.XPATH,'//*[@text="Success"]')
    btn_txn_status_pending = (AppiumBy.XPATH,'//*[@text="Pending"]')
    btn_txn_status_failed = (AppiumBy.XPATH,'//*[@text="Failed"]')
    btn_txn_status_void_or_refund = (AppiumBy.XPATH,'//*[@text="Void/Refund"]')
    btn_txn_status_is_settle = (AppiumBy.XPATH,'//*[@text="Is Settled"]')
    btn_sort_by_date_descending = (AppiumBy.ID,'com.ezetap.service.demo:id/ivDateUp')
    btn_sort_by_date_ascending = (AppiumBy.ID,'com.ezetap.service.demo:id/ivDateDown')
    btn_sort_by_amount_descending = (AppiumBy.ID,'com.ezetap.service.demo:id/ivAmtUp')
    btn_sort_by_amount_ascending = (AppiumBy.ID,'com.ezetap.service.demo:id/ivAmtDown')
    btn_from_date = (AppiumBy.ID,'com.ezetap.service.demo:id/tv_start_date')
    btn_to_date = (AppiumBy.ID,'com.ezetap.service.demo:id/tv_end_date')
    txt_tnx_history = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/clTxnView"])[1]')

    def __init__(self, driver):
        super().__init__(driver)

    def apply_filter_card_and_success(self):
        """
        performs clicking on the card in the txn type and success in the txn status
        """
        self.perform_click(self.rdo_card)
        TouchAction(self.driver).press(x=317, y=980).move_to(x=315, y=148).release().perform()
        self.perform_click(self.rdo_success)
        self.perform_click(self.btn_apply)

    def click_on_apply_filter(self):
        """
        performs clicking on the apply button
        """
        self.perform_click(self.btn_apply)

    def click_on_select_date(self):
        """
        performs clicking on the select date button
        """
        self.perform_click(self.btn_selectDate)

    def select_particular_date(self, date: str):
        """
        performs clicking on the particular date
        param: date: str
        """
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + date + ''))

    def click_ok_button(self):
        """
        performs clinking in the ok button
        """
        self.perform_click(self.btn_selectDateOk)

    def click_on_today(self):
        """
        performs click on today button in the txn filter page
        """
        self.perform_click(self.btn_today)

    def click_on_this_week(self):
        """
        performs click on this week in the txn filter page
        """
        self.perform_click(self.btn_this_week)

    def click_on_select_date_range(self,from_date: str, to_date: str):
        """
        performs selection of date range in the txn filter page to get the txn details in that date range
        param: from_date
        param: to_date
        """
        self.perform_click(self.btn_select_date_range)
        self.perform_click(self.btn_from_date)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID,''+ from_date +''))
        self.perform_click(self.btn_selectDateOk)
        self.perform_click(self.btn_to_date)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID,'' + to_date + ''))
        self.perform_click(self.btn_selectDateOk)

    def click_on_payment_method_all(self):
        """
        performs clicking on payment mode all in the filter page
        """
        self.wait_for_element(self.btn_payment_method_all)
        self.perform_click(self.btn_payment_method_all)

    def click_on_payment_method_cash(self):
        """
        performs clicking on the cash txn
        """
        self.wait_for_element(self.btn_payment_method_cash)
        self.perform_click(self.btn_payment_method_cash)

    def click_on_payment_method_card(self):
        """
        performs clicking on the card txn
        """
        self.wait_for_element(self.btn_payment_method_card)
        self.perform_click(self.btn_payment_method_card)

    def click_on_payment_method_cheque(self):
        """
        performs clicking on the cheque txn
        """
        self.wait_for_element(self.btn_payment_method_cheque)
        self.perform_click(self.btn_payment_method_cheque)

    def click_on_payment_method_bharat_qr(self):
        """
        performs clicking on the bharat Qr txn
        """
        self.wait_for_element(self.btn_payment_method_bharat_qr)
        self.perform_click(self.btn_payment_method_bharat_qr)

    def click_on_payment_method_upi(self):
        """
        performs clicking on the upi txn
        """
        self.wait_for_element(self.btn_payment_method_upi)
        self.perform_click(self.btn_payment_method_upi)

    def click_on_payment_method_pay_link(self):
        """
        performs clicking on the pay link(cnp) txn
        """
        self.wait_for_element(self.btn_payment_method_pay_link)
        self.perform_click(self.btn_payment_method_pay_link)

    def click_on_txn_status_all(self):
        """
        performs clicking on the status all
        """
        self.wait_for_element(self.btn_txn_status_all)
        self.perform_click(self.btn_txn_status_all)

    def click_on_txn_status_success(self):
        """
        performs clicking on the status success
        """
        self.wait_for_element(self.btn_txn_status_success)
        self.perform_click(self.btn_txn_status_success)

    def click_on_txn_status_failed(self):
        """
        performs clicking on the status fail
        """
        self.wait_for_element(self.btn_txn_status_failed)
        self.perform_click(self.btn_txn_status_failed)

    def click_on_txn_status_pending(self):
        """
        performs clicking on the status pending
        """
        self.wait_for_element(self.btn_txn_status_pending)
        self.perform_click(self.btn_txn_status_pending)

    def click_on_txn_status_void_or_refund(self):
        """
        performs clicking on the status void or refund
        """
        self.wait_for_element(self.btn_txn_status_void_or_refund)
        self.perform_click(self.btn_txn_status_void_or_refund)

    def click_on_txn_status_is_settle(self):
        """
        performs clicking on the status settle
        """
        self.wait_for_element(self.btn_txn_status_is_settle)
        self.perform_click(self.btn_txn_status_is_settle)

    def click_on_sort_by_date_descending(self):
        """
        performs clicking on date descending to sort the txn in the descending based on the date
        """
        self.scroll_to_text('Date')
        self.wait_for_element(self.btn_sort_by_date_descending)
        self.perform_click(self.btn_sort_by_date_descending)

    def click_on_sort_by_date_ascending(self):
        """
        performs clicking on date ascending to sort the txn in the ascending based on the date
        """
        self.scroll_to_text('Sort By')
        self.wait_for_element(self.btn_sort_by_date_ascending)
        self.perform_click(self.btn_sort_by_date_ascending)

    def click_on_sort_by_amount_descending(self):
        """
        performs clicking on the descending to sort the txn in the descending based on the amount
        """
        self.scroll_to_text('Sort By')
        self.wait_for_element(self.btn_sort_by_amount_descending)
        self.perform_click(self.btn_sort_by_amount_descending)

    def click_on_sort_by_amount_ascending(self):
        """
        performs clicking on the ascending to sort the txn in the ascending based on the amount
        """
        self.scroll_to_text('Sort By')
        self.wait_for_element(self.btn_sort_by_date_ascending)
        self.perform_click(self.btn_sort_by_date_ascending)

    def click_on_tnx_after_first_tnx_after_filtration(self):
        """
        performs clicking on the first txn when applying all the required filter
        """
        self.wait_for_element(self.txt_tnx_history)
        self.perform_click(self.txt_tnx_history)
