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
    btn_payment_method_all = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[1]')
    btn_payment_method_cash = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[2]')
    btn_payment_method_card = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[3]')
    btn_payment_method_cheque = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[4]')
    btn_payment_method_bharat_qr = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[5]')
    btn_payment_method_upi = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[6]')
    btn_payment_method_pay_link = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[7]')
    btn_payment_method_emi = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[8]')
    btn_txn_status_all = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[9]')
    btn_txn_status_success = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[10]')
    btn_txn_status_pending = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[11')
    btn_txn_status_failed = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[12]')
    btn_txn_status_void_or_refund = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[13]')
    btn_txn_status_is_settle = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvFilter"])[14]')
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
        self.perform_click(self.rdo_card)
        TouchAction(self.driver).press(x=317, y=980).move_to(x=315, y=148).release().perform()
        self.perform_click(self.rdo_success)
        self.perform_click(self.btn_apply)

    def click_on_apply_filter(self):
        self.perform_click(self.btn_apply)

    def click_on_select_date(self):
        self.perform_click(self.btn_selectDate)

    def select_particular_date(self, date):
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + date + ''))

    def click_ok_button(self):
        self.perform_click(self.btn_selectDateOk)

    def click_on_today(self):
        self.perform_click(self.btn_today)

    def click_on_this_week(self):
        self.perform_click(self.btn_this_week)

    def click_on_select_date_range(self,from_date,to_date):
        self.perform_click(self.btn_select_date_range)
        self.perform_click(self.btn_from_date)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID,''+ from_date +''))
        self.perform_click(self.btn_selectDateOk)
        self.perform_click(self.btn_to_date)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID,'' + to_date + ''))
        self.perform_click(self.btn_selectDateOk)

    def click_on_payment_method_all(self):
        self.wait_for_element(self.btn_payment_method_all)
        self.perform_click(self.btn_payment_method_all)

    def click_on_payment_method_cash(self):
        self.wait_for_element(self.btn_payment_method_cash)
        self.perform_click(self.btn_payment_method_cash)

    def click_on_payment_method_card(self):
        self.wait_for_element(self.btn_payment_method_card)
        self.perform_click(self.btn_payment_method_card)

    def click_on_payment_method_cheque(self):
        self.wait_for_element(self.btn_payment_method_cheque)
        self.perform_click(self.btn_payment_method_cheque)

    def click_on_payment_method_bharat_qr(self):
        self.wait_for_element(self.btn_payment_method_bharat_qr)
        self.perform_click(self.btn_payment_method_bharat_qr)

    def click_on_payment_method_upi(self):
        self.wait_for_element(self.btn_payment_method_upi)
        self.perform_click(self.btn_payment_method_upi)

    def click_on_payment_method_pay_link(self):
        self.wait_for_element(self.btn_payment_method_pay_link)
        self.perform_click(self.btn_payment_method_pay_link)

    def click_on_payment_method_emi(self):
        self.wait_for_element(self.btn_payment_method_emi)
        self.perform_click(self.btn_payment_method_emi)

    def click_on_txn_status_all(self):
        self.wait_for_element(self.btn_txn_status_all)
        self.perform_click(self.btn_txn_status_all)

    def click_on_txn_status_success(self):
        self.wait_for_element(self.btn_txn_status_success)
        self.perform_click(self.btn_txn_status_success)

    def click_on_txn_status_failed(self):
        self.wait_for_element(self.btn_txn_status_failed)
        self.perform_click(self.btn_txn_status_failed)

    def click_on_txn_status_pending(self):
        self.wait_for_element(self.btn_txn_status_pending)
        self.perform_click(self.btn_txn_status_pending)

    def click_on_txn_status_void_or_refund(self):
        self.wait_for_element(self.btn_txn_status_void_or_refund)
        self.perform_click(self.btn_txn_status_void_or_refund)

    def click_on_txn_status_is_settle(self):
        self.wait_for_element(self.btn_txn_status_is_settle)
        self.perform_click(self.btn_txn_status_is_settle)

    def click_on_sort_by_date_descending(self):
        self.wait_for_element(self.btn_sort_by_date_descending)
        self.perform_click(self.btn_sort_by_date_descending)

    def click_on_sort_by_date_ascending(self):
        self.wait_for_element(self.btn_sort_by_date_ascending)
        self.perform_click(self.btn_sort_by_date_ascending)

    def click_on_sort_by_amount_descending(self):
        self.wait_for_element(self.btn_sort_by_amount_descending)
        self.perform_click(self.btn_sort_by_amount_descending)

    def click_on_sort_by_amount_ascending(self):
        self.wait_for_element(self.btn_sort_by_date_ascending)
        self.perform_click(self.btn_sort_by_date_ascending)

    def click_on_tnx_after_first_tnx_after_filtration(self):
        self.wait_for_element(self.txt_tnx_history)
        self.perform_click(self.txt_tnx_history)
