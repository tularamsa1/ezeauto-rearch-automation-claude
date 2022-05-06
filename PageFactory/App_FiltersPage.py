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
