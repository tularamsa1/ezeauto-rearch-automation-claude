from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from PageFactory.mpos.app_base_page import BasePage
from PageFactory.mpos.app_home_page import HomePage


class RefundPage(BasePage):
    ref_amount_field = (By.ID, 'com.ezetap.basicapp:id/amountView')
    card_type_desc_field = (By.ID, 'com.ezetap.basicapp:id/cardChequeLabel')
    date_time_field = (By.ID, 'com.ezetap.basicapp:id/dateView')
    status_field = (By.ID, 'com.ezetap.basicapp:id/statusText')
    device_serial_field = (By.ID, 'com.ezetap.basicapp:id/externalRef2Value')
    ref3_field = (By.ID, 'com.ezetap.basicapp:id/externalRef3Value')
    customer_name_field = (By.ID, 'com.ezetap.basicapp:id/customerNameValue')
    auth_code_field = (By.ID, 'com.ezetap.basicapp:id/authCodeValue')
    mid_field = (By.ID, 'com.ezetap.basicapp:id/midValue')
    tid_field = (By.ID, 'com.ezetap.basicapp:id/tidValue')
    rrn_field = (By.ID, 'com.ezetap.basicapp:id/rrnValue')
    batch_number_field = (By.ID, 'com.ezetap.basicapp:id/batchNoValue')
    tip_amount_field = (By.ID, 'com.ezetap.basicapp:id/tipAmountValue')
    ref1_field = (By.ID, 'com.ezetap.basicapp:id/orderNoValue')

    btn_Refund = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Refund")')
    btn_proceed = (AppiumBy.ID, 'com.ezetap.basicapp:id/btn_authenticate')
    txt_password = (AppiumBy.ID, 'com.ezetap.basicapp:id/txt_password')
    txt_last_digits_card = (AppiumBy.ID, "com.ezetap.basicapp:id/txt_last_digits_card")
    txt_date_txn_history = (AppiumBy.ID, "com.ezetap.basicapp:id/txt_date_txn_history")
    button1 = (AppiumBy.ID, "android:id/button1")
    btn_authenticate = (AppiumBy.ID, "com.ezetap.basicapp:id/btn_authenticate")
    txnCard = (AppiumBy.ID, "com.ezetap.basicapp:id/txnCard")
    btn_refund = (AppiumBy.ID, "com.ezetap.basicapp:id/btn_refund")
    proceed_btn = (AppiumBy.ID, "com.ezetap.basicapp:id/proceed_btn")
    device_serial = (AppiumBy.ID, "com.ezetap.service.demo:id/et_deviceSerial")
    btn_ok = (AppiumBy.ID, "android:id/button1")

    def __init__(self, driver):
        super().__init__(driver)

    def fetch_amount_text(self) -> str:
        """
        This method is used to fetch amount on refund page
        return: amount: str
        """
        return self.fetch_text(locator=self.ref_amount_field)

    def fetch_card_type_desc_text(self) -> str:
        """
        This method is used to fetch card type desc on refund page
        return: card_type_desc: str
        """
        return self.fetch_text(locator=self.card_type_desc_field)

    def fetch_date_time_text(self) -> str:
        """
        This method is used to fetch date and time on refund page
        return: date_time: str
        """
        return self.fetch_text(locator=self.date_time_field)

    def fetch_status_text(self) -> str:
        """
        This method is used to fetch status on refund page
        return: status: str
        """
        return self.fetch_text(locator=self.status_field)

    def fetch_device_serial_text(self) -> str:
        """
        his method is used to fetch device serial on refund page
        return: device_serial: str
        """
        return self.fetch_text(locator=self.device_serial_field)

    def fetch_ref3_text(self) -> str:
        """
        This method is used to fetch ref3 on refund page
        return: ref3: str
        """
        return self.fetch_text(locator=self.ref3_field)

    def fetch_customer_name_text(self) -> str:
        """
        This method is used to fetch customer name on refund page
        return: customer_name: str
        """
        return self.fetch_text(locator=self.customer_name_field)

    def fetch_auth_code_text(self) -> str:
        """
        This method is used to fetch auth code on refund page
        return: auth_code: str
        """
        return self.fetch_text(locator=self.auth_code_field)

    def fetch_mid_text(self) -> str:
        """
        This method is used to fetch mid on refund page
        return: mid: str
        """
        return self.fetch_text(locator=self.mid_field)

    def fetch_tid_text(self) -> str:
        """
        This method is used to fetch tid on refund page
        return: tid: str
        """
        return self.fetch_text(locator=self.tid_field)

    def fetch_rrn_text(self) -> str:
        """
        This method is used to fetch rrn on refund page
        return: rrn: str
        """
        return self.fetch_text(locator=self.rrn_field)

    def fetch_batch_number_text(self) -> str:
        """
        This method is used to fetch batch number on refund page
        return: batch_number: str
        """
        return self.fetch_text(locator=self.batch_number_field)

    def fetch_tip_amount_text(self) -> str:
        """
        This method is used to fetch tip amount on refund page
        return: tip_amount: str
        """
        return self.fetch_text(locator=self.tip_amount_field)

    def fetch_ref1_text(self) -> str:
        """
        This method is used to fetch ref1 on refund page
        return: ref1: str
        """
        return self.fetch_text(locator=self.ref1_field)

    def capture_online_refund_txn_data(self, password: str, card_last_four_digit: str, customer_name: str, txn_type: str) -> dict:
        """
        This method is used to capture online refund txn data
        param: password str
        param: card_last_four_digit str
        param: customer_name str
        param: txn_type str
        or: online_refund
        return: online_refund_txn_data: dict
        """
        self.wait_for_visibility_of_elements(self.status_field)
        self.driver.back()
        self.wait_for_visibility_of_elements(self.btn_Refund)
        self.perform_click(self.btn_Refund)
        self.perform_sendkeys(self.txt_password, password)
        self.perform_click(self.btn_proceed)
        self.perform_sendkeys(self.txt_last_digits_card, card_last_four_digit)
        self.perform_click(self.txt_date_txn_history)
        self.perform_click(self.button1)
        self.perform_click(self.btn_authenticate)
        self.wait_for_visibility_of_elements(self.txnCard)
        txn_locator_list = self.driver.find_elements(By.ID, 'com.ezetap.basicapp:id/txnCard')

        txn_locator_list[0].click()
        online_refund_txn_data = {
            "or_device_serial_2": self.fetch_device_serial_text(),
            "or_amount_2": self.fetch_amount_text(),
            "or_card_type_desc_2": self.fetch_card_type_desc_text(),
            "or_date_time_2": self.fetch_date_time_text(),
            "or_status_2": self.fetch_status_text(), "or_ref3_2": self.fetch_ref3_text(),
            "or_auth_code_name_2": self.fetch_auth_code_text(), "or_mid_2": self.fetch_mid_text(),
            "or_tid_2": self.fetch_tid_text(), "or_rrn_2": self.fetch_rrn_text(),
            "or_batch_number_2": self.fetch_batch_number_text(), "or_ref1_2": self.fetch_ref1_text()}
        if customer_name is not None:
            online_refund_txn_data["or_customer_name_2"] = self.fetch_customer_name_text()

        self.driver.back()
        txn_locator_list[1].click()
        online_refund_txn_data["or_device_serial"] = self.fetch_device_serial_text()
        online_refund_txn_data["or_amount"] = self.fetch_amount_text()
        online_refund_txn_data["or_card_type_desc"] = self.fetch_card_type_desc_text()
        online_refund_txn_data["or_date_time"] = self.fetch_date_time_text()
        online_refund_txn_data["or_status"] = self.fetch_status_text()
        online_refund_txn_data["or_auth_code_name"] = self.fetch_auth_code_text()
        online_refund_txn_data["or_mid"] = self.fetch_mid_text()
        online_refund_txn_data["or_tid"] = self.fetch_tid_text()
        online_refund_txn_data["or_rrn"] = self.fetch_rrn_text()
        online_refund_txn_data["or_batch_number"] = self.fetch_batch_number_text()
        online_refund_txn_data["or_ref1"] = self.fetch_ref1_text()
        if customer_name is not None:
            online_refund_txn_data["or_customer_name"] = self.fetch_customer_name_text()
        if txn_type == "sale_tip":
            online_refund_txn_data["or_tip_amt"] = self.fetch_tip_amount_text()

        if txn_type == "preauth":
            self.driver.back()
            txn_locator_list[2].click()
            online_refund_txn_data["or_device_serial_3"] = self.fetch_device_serial_text()
            online_refund_txn_data["or_amount_3"] = self.fetch_amount_text()
            online_refund_txn_data["or_card_type_desc_3"] = self.fetch_card_type_desc_text()
            online_refund_txn_data["or_date_time_3"] = self.fetch_date_time_text()
            online_refund_txn_data["or_status_3"] = self.fetch_status_text()
            online_refund_txn_data["or_auth_code_name_3"] = self.fetch_auth_code_text()
            online_refund_txn_data["or_mid_3"] = self.fetch_mid_text()
            online_refund_txn_data["or_tid_3"] = self.fetch_tid_text()
            online_refund_txn_data["or_rrn_3"] = self.fetch_rrn_text()
            online_refund_txn_data["or_batch_number_3"] = self.fetch_batch_number_text()
            online_refund_txn_data["or_ref1_3"] = self.fetch_ref1_text()
            if customer_name is not None:
                online_refund_txn_data["or_customer_name_3"] = self.fetch_customer_name_text()

        self.driver.back()
        self.wait_for_visibility_of_elements(self.txnCard)
        self.driver.back()
        self.wait_for_visibility_of_elements(self.txt_last_digits_card)
        self.driver.back()
        self.wait_for_visibility_of_elements(self.txt_password)
        self.driver.back()
        home_page = HomePage(driver=self.driver)
        home_page.wait_for_home_page_load()

        return online_refund_txn_data
