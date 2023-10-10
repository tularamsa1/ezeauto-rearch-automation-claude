from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage


class Upfront(BasePage):
    txt_order_number = (AppiumBy.ID, 'com.ezetap.basicapp:id/editTextOrderNo')
    txt_ph_number = (AppiumBy.ID, 'com.ezetap.basicapp:id/editTextMobile')
    txt_email = (AppiumBy.ID, 'com.ezetap.basicapp:id/editTextEmail')
    txt_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvAmountCard')
    btn_pay = (AppiumBy.ID, "com.ezetap.basicapp:id/btnPay")
    txt_enterAmountField = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvAmountCard')
    txt_orderNo = (AppiumBy.ID, "com.ezetap.basicapp:id/editTextOrderNo")
    txt_mobileField = (AppiumBy.ID, 'com.ezetap.basicapp:id/editTextMobile')
    txt_emailField = (AppiumBy.ID, 'com.ezetap.basicapp:id/editTextEmail')
    btn_paymentProceed = (AppiumBy.ID, 'com.ezetap.basicapp:id/buttonProceed')

    def __init__(self, driver):
        super().__init__(driver)

    def type_amount(self, amt):
        li = []
        for i in str(amt):
            if i == '.':
                li.append((AppiumBy.ID, "com.ezetap.basicapp:id/button_dot"))
            else:
                li.append((AppiumBy.ID, "com.ezetap.basicapp:id/button_" + i + ""))
        return li

    def enter_amount_order_number_and_customer_details(self, amt, order_number, mobile_num, email):
        self.perform_click(self.txt_enterAmountField)
        list = self.type_amount(amt)
        for i in list:
            self.perform_click(i)
        self.perform_click(self.btn_pay)
        self.perform_click(self.txt_orderNo)
        self.perform_sendkeys(self.txt_orderNo, order_number)
        self.perform_sendkeys(self.txt_mobileField, str(mobile_num))
        self.perform_sendkeys(self.txt_emailField, str(email))
        self.perform_click(self.btn_paymentProceed)

    def fetch_txt_order_number(self):
        self.wait_for_element(self.txt_order_number)
        return self.fetch_text(self.txt_order_number)

    def fetch_txt_phone_number(self):
        self.wait_for_element(self.txt_ph_number)
        return self.fetch_text(self.txt_ph_number)

    def fetch_txt_email(self):
        self.wait_for_element(self.txt_email)
        return self.fetch_text(self.txt_email)
