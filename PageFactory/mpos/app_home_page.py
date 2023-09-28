from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage


class HomePage(BasePage):
    lbl_home = (By.ID, 'com.ezetap.basicapp:id/navigation_bar_item_large_label_view')
    lbl_navigation = (By.ID, 'com.ezetap.basicapp:id/nav_account')
    mnu_account = (By.ID, 'com.ezetap.basicapp:id/nav_account')
    txt_enterAmountField = (By.ID, 'com.ezetap.basicapp:id/tvAmountCard')
    btn_pay = (By.ID, "com.ezetap.basicapp:id/btnPay")
    btn_goToHistory = (By.ID, "com.ezetap.basicapp:id/clGotoHistory")
    img_companyLogo = (By.XPATH,'//android.widget.ImageView[@content-desc="Company Logo"]')
    tab_history = (By.ID,"com.ezetap.basicapp:id/nav_txn_history")
    mnu_engSideMenu =(By.XPATH, '//android.widget.ImageButton[@content-desc="Open navigation drawer"]')
    mnu_hindiSideMenu = (By.XPATH, '//android.widget.ImageButton[@content-desc="नेविगेशन ड्रावर खोलें"]')
    mnu_merchantDetail = (By.ID, 'com.ezetap.basicapp:id/arrow')
    rdo_langSelection = (By.ID, 'com.ezetap.basicapp:id/clLanguage')
    btn_langProceed = (By.ID, 'com.ezetap.basicapp:id/btnProceed')
    txt_mobileField = (By.ID, 'com.ezetap.basicapp:id/editTextMobile')
    txt_emailField = (By.ID, 'com.ezetap.basicapp:id/editTextEmail')
    btn_paymentProceed = (By.ID, 'com.ezetap.basicapp:id/buttonProceed')
    txt_orderNo = (By.ID, "com.ezetap.basicapp:id/editTextOrderNo")
    txt_tip_amount = (By.ID, "com.ezetap.basicapp:id/editTextTipAmount")
    device_serialNo = (By.ID, 'com.ezetap.basicapp:id/editTextRef2')
    btn_checkStatus = (By.ID, "com.ezetap.service.demo:id/btn_check_status")
    mnu_navigationDrawer = (By.XPATH, '//android.widget.ImageButton[@content-desc="Open navigation drawer"]')
    mnu_transactionHistory = (By.XPATH, "//android.widget.CheckedTextView[@text='Transaction History']")
    btn_cashAtPos = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Cash @ POS")')
    txt_cashAtPosAmount = (By.ID, 'com.ezetap.basicapp:id/etCashAmount')
    btn_payNow = (By.ID, "com.ezetap.basicapp:id/btnPayNow")
    btn_cashAtPosWithSale = (By.ID, 'com.ezetap.basicapp:id/switchSale')
    txt_cashAtPosSaleAmount = (By.ID, 'com.ezetap.basicapp:id/etSaleAmount')
    btn_back = (By.ID, "com.ezetap.basicapp:id/imgBack")
    btn_skip = (By.ID, "com.ezetap.service.demo:id/btnSkip")
    lbl_p2p_notification = (By.ID, "com.ezetap.service.demo:id/title")
    btn_preauth = (By.XPATH, "//android.widget.TextView[@text='Pre-Auth']")
    txt_enter_pre_auth_amt = (By.ID, "com.ezetap.basicapp:id/textViewAmount")
    btn_cash_at_pos_back = (By.ID, 'com.ezetap.basicapp:id/imgToolbarBack')

    btn_Refund = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Refund")')
    btn_proceed = (AppiumBy.ID, 'com.ezetap.basicapp:id/btn_authenticate')
    txt_password = (AppiumBy.ID, 'com.ezetap.basicapp:id/txt_password')
    card_last_four_digit = (AppiumBy.ID, "com.ezetap.basicapp:id/txt_last_digits_card")
    txt_date_txn_history = (AppiumBy.ID, "com.ezetap.basicapp:id/txt_date_txn_history")
    button1 = (AppiumBy.ID, "android:id/button1")
    btn_authenticate = (AppiumBy.ID, "com.ezetap.basicapp:id/btn_authenticate")
    txnCard = (AppiumBy.ID, "com.ezetap.basicapp:id/txnCard")
    btn_refund = (AppiumBy.ID, "com.ezetap.basicapp:id/btn_refund")
    proceed_btn = (AppiumBy.ID, "com.ezetap.basicapp:id/proceed_btn")
    device_serial = (AppiumBy.ID, "com.ezetap.service.demo:id/et_DeviceSerialNo")
    btn_externalSerialProceed = (AppiumBy.ID, "com.ezetap.service.demo:id/btn_externalSerialProceed")

    def __init__(self, driver):
        super().__init__(driver)

    def check_home_page_logo(self):
        return self.fetch_text(self.lbl_home, 30)

    def check_home_page_for_invalid_Login(self):
        return self.fetch_text(self.lbl_home, 5)

    def enter_amount_and_order_number(self, amt, order_number):
        self.perform_click(self.txt_enterAmountField)
        list = self.type_amount(amt)
        for i in list:
            self.perform_click(i)
        self.perform_click(self.btn_pay)
        self.perform_click(self.txt_orderNo)
        self.perform_sendkeys(self.txt_orderNo, order_number)
        self.perform_click(self.btn_paymentProceed)

    def enter_amount_order_number_and_customer_details(self, amt, order_number, mobilenum, email):
        self.perform_click(self.txt_enterAmountField)
        list = self.type_amount(amt)
        for i in list:
            self.perform_click(i)
        self.perform_click(self.btn_pay)
        self.perform_click(self.txt_orderNo)
        self.perform_sendkeys(self.txt_orderNo, order_number)
        self.perform_sendkeys(self.txt_mobileField, str(mobilenum))
        self.perform_sendkeys(self.txt_emailField, str(email))
        self.driver.hide_keyboard()
        self.perform_click(self.btn_paymentProceed)

    def enter_amount_and_order_number_and_device_serial_for_card(self, amt: int, order_number: str, device_serial: str):
        """
       This method is used to enter amount, order number and device serial in the home page.
       :param amt int
       :param order_number str
       :param device_serial str
       """
        self.perform_click(self.txt_enterAmountField)
        list = self.type_amount(amt)
        for i in list:
            self.perform_click(i)
        self.perform_click(self.btn_pay)
        self.perform_click(self.txt_orderNo)
        self.perform_sendkeys(self.txt_orderNo, order_number)
        self.perform_click(self.device_serialNo)
        self.perform_sendkeys(self.device_serialNo, device_serial)
        self.perform_click(self.btn_paymentProceed)

    def enter_tip_and_amount_and_order_number_and_device_serial_for_card(self, amt: int, order_number: str,
                                                                     tip_amt: int, device_serial: str):
        """
          This method is used to enter amount, order number, tip amount and device serial in the home page.
          :param amt: int,
          :param order_number: str
          :param tip_amt: int
          :param device_serial: str
        """
        self.perform_click(self.txt_enterAmountField)
        list = self.type_amount(amt)
        for i in list:
            self.perform_click(i)
        self.perform_click(self.btn_pay)
        self.perform_click(self.txt_orderNo)
        self.perform_sendkeys(self.txt_orderNo, order_number)
        self.perform_click(self.txt_tip_amount)
        self.perform_sendkeys(self.txt_tip_amount, tip_amt)
        self.perform_click(self.device_serialNo)
        self.perform_sendkeys(self.device_serialNo, device_serial)
        self.perform_click(self.btn_paymentProceed)

    def enter_order_number_and_device_serial_for_card(self, order_number, device_serial):
        self.perform_click(self.txt_orderNo)
        self.perform_sendkeys(self.txt_orderNo, order_number)
        self.perform_click(self.device_serialNo)
        self.perform_sendkeys(self.device_serialNo, device_serial)
        self.perform_click(self.btn_paymentProceed)

    def enter_amt_order_no_and_device_serial_for_pre_auth(self, amt: str, order_number: str, device_serial: str):
        """
        This method is used to enter amount, order_id, device_serial for preauth payment mode and click on proceed button.
            :param amt: str
            :param order_number: str
            :param device_serial: str
        """
        self.perform_click(self.txt_enter_pre_auth_amt)
        list = self.type_amount(amt)
        for i in list:
            self.perform_click(i)
        self.perform_click(self.btn_pay)
        self.perform_click(self.txt_orderNo)
        self.perform_sendkeys(self.txt_orderNo, order_number)
        self.perform_click(self.device_serialNo)
        self.perform_sendkeys(self.device_serialNo, device_serial)
        self.perform_click(self.btn_paymentProceed)

    def type_amount(self, amt):
        li = []
        for i in str(amt):
            if i == '.':
                li.append((By.ID, "com.ezetap.basicapp:id/button_dot"))
            else:
                li.append((By.ID, "com.ezetap.basicapp:id/button_"+i+""))
        return li

    def perform_check_status(self):
        self.perform_click(self.btn_checkStatus)

    def click_on_skip_button(self):
        self.perform_click(self.btn_skip)

    def click_navigation_drawer(self):
        self.perform_click(self.mnu_navigationDrawer)

    def click_on_transaction_history(self):
        self.perform_click(self.mnu_transactionHistory)

    def click_cash_at_pos(self):
        """
            This method is used to click on cash@pos payment mode.
        """
        self.perform_click(self.btn_cashAtPos)

    def enter_cash_at_pos_amount(self, amount):
        """
          This method clicks on the cash@pos icon and then enters the cashback amount and close the onscreen keyboard
          :param amount: int
        """
        self.perform_click(self.txt_cashAtPosAmount)
        self.perform_sendkeys(self.txt_cashAtPosAmount, amount)
        self.driver.back()

    def enter_cash_at_pos_sale_amount(self, amount):
        """
        This method clicks on the cash@pos icon and then enters the cashback, sale amount and close the onscreen keyboard
        :param amount: int
        """
        self.perform_click(self.txt_cashAtPosSaleAmount)
        self.perform_sendkeys(self.txt_cashAtPosSaleAmount, amount)
        self.driver.back()

    def enter_order_number_and_device_serial(self, order_number: str, device_serial: str):
        """
            This method is used to enter the order number and device serial for cash@pos payment mode and click on proceed button.

            :param order_number: str
            :param device_serial: str
        """
        self.perform_click(self.txt_orderNo)
        self.perform_sendkeys(self.txt_orderNo, order_number)
        self.perform_click(self.device_serialNo)
        self.perform_sendkeys(self.device_serialNo, device_serial)
        self.perform_click(self.btn_paymentProceed)

    def click_on_pre_auth(self):
        """
        This method is used to click on pre-auth payment mode.
        """
        self.perform_click(self.btn_preauth)

    def click_pay_now_button(self):
        self.perform_click(self.btn_payNow)

    def click_cash_at_pos_with_sale_switch(self):
        self.perform_click(self.btn_cashAtPosWithSale)

    def click_account_menu(self):
        self.perform_click(self.mnu_account)

    def check_lang_selection_option(self):
        return self.wait_for_element(self.rdo_langSelection).is_displayed()

    def select_eng_language(self):
        self.perform_clickIndex(self.rdo_langSelection, 0)

    def select_hindi_language(self):
        self.perform_clickIndex(self.rdo_langSelection, 1)

    def click_on_lang_proceed(self):
        self.perform_click(self.btn_langProceed)

    def get_home_page_logo(self):
        return self.wait_for_element(self.img_companyLogo)

    def get_EnterAmt_text(self):
        return self.fetch_text(self.txt_enterAmountField)

    def click_on_history(self):
        self.perform_click(self.tab_history)

    def wait_for_home_page_load(self):
        self.wait_for_element(self.btn_goToHistory, 30)

    def click_side_menu_eng(self):
        self.perform_click(self.mnu_engSideMenu)

    def click_side_menu_hindi(self):
        self.perform_click(self.mnu_hindiSideMenu)

    def click_on_merchant_name(self):
        self.perform_click(self.mnu_merchantDetail)

    def check_mob_num_field(self):
        return self.wait_for_element(self.txt_mobileField).is_displayed()

    def check_email_field(self):
        return self.wait_for_element(self.txt_emailField).is_displayed()

    def click_on_back_btn_enter_amt_page(self):
        self.perform_click(self.btn_back)

    def wait_for_navigation_to_load(self):
        self.wait_for_element_to_be_clickable(self.lbl_navigation)

    def wait_for_navigationTo_load(self):
        self.wait_for_element(self.lbl_navigation)

    def check_p2p_notification(self):
        return self.fetch_text(self.lbl_p2p_notification, 30)

    def click_on_back_btn_cash_at_pos_page(self):
        """
        This method clicks on the back btn on the cash@pos enter amount page
       """
        self.perform_click(self.btn_cash_at_pos_back)

    def perform_online_refund(self, password: str, card_last_four_digit: str, device_serial: str):
        self.perform_click(self.btn_Refund)
        self.perform_sendkeys(self.txt_password, password)
        self.perform_click(self.btn_proceed)
        self.perform_sendkeys(self.card_last_four_digit, card_last_four_digit)
        self.perform_click(self.txt_date_txn_history)
        self.perform_click(self.button1)
        self.perform_click(self.btn_authenticate)
        self.visibility_of_elements(self.txnCard)
        txn_locator_list = self.driver.find_elements(By.ID, 'com.ezetap.basicapp:id/txnCard')
        txn_locator_list[0].click()
        self.perform_click(self.btn_refund)
        self.perform_click(self.proceed_btn)
        self.perform_sendkeys(self.device_serial, device_serial)
        # self.perform_click(self.btn_ok)
        self.perform_click(self.btn_externalSerialProceed)
