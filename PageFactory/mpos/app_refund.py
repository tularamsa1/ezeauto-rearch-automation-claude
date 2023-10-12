from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage


class Refund(BasePage):
    btn_refund = (AppiumBy.ID,'com.ezetap.basicapp:id/nav_online_refund')
    txt_refund_enter_password = (AppiumBy.ID,'com.ezetap.basicapp:id/txt_label')
    txt_password = (AppiumBy.ID,'com.ezetap.basicapp:id/txt_password')
    btn_proceed =(AppiumBy.ID,'com.ezetap.basicapp:id/btn_authenticate')
    txt_card_last_four_digits =(AppiumBy.ID,'com.ezetap.basicapp:id/txt_last_digits_card')
    txt_date_for_past_txn = (AppiumBy.ID, 'com.ezetap.basicapp:id/txt_date_txn_history')
    btn_search = (AppiumBy.ID,'com.ezetap.basicapp:id/btn_authenticate')
    btn_ok = (AppiumBy.ID, 'android:id/button1')
    dashboard_rewards_dtn = (AppiumBy.ID,'com.ezetap.basicapp:id/clGotoRewards')

    def __init__(self, driver):
        super().__init__(driver)

    def validate_refund_option_from_side_mnu(self):
        """
        verifies the availability of a refund option
        return: btn_refund: str
        """
        self.wait_for_element(self.btn_refund)
        return self.fetch_text(self.btn_refund)

    def click_on_refund(self):
        """
        performs click on refund option
        """
        self.wait_for_element(self.btn_refund)
        self.perform_click(self.btn_refund)

    def fetch_txt_from_refund_page(self):
        """
        Retrieves the title text of the refund login page.
        return: password:str
        """
        self.wait_for_element(self.txt_refund_enter_password)
        return self.fetch_text(self.txt_refund_enter_password)

    def enter_password(self,app_password):
        """
        performs entering the password in the refund login page
        """
        self.wait_for_element(self.txt_password)
        self.perform_sendkeys(self.txt_password,app_password)

    def click_on_proceed(self):
        """
        performs click on proceed button
        """
        self.wait_for_element(self.btn_proceed)
        self.perform_click(self.btn_proceed)

    def enter_last_four_card_number(self, card_number:str):
        """
        performs entering the last 4 digits of number number in the refund page
        param: card_number :str
        """
        self.wait_for_element(self.txt_card_last_four_digits)
        self.perform_sendkeys(self.txt_card_last_four_digits,card_number)

    def enter_the_date(self,date):
        """
         performs entering the date
         param: date
        """
        self.perform_click(self.txt_date_for_past_txn)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + date + ''))
        self.perform_click(self.btn_ok)

    def search_button_is_enabled(self):
        """
        verifies search bottom element is enabled or disabled
        return: bool value
        """
        button = self.wait_for_element(self.btn_search)
        return button.is_enabled()
