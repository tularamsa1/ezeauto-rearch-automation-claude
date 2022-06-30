from time import sleep

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from PageFactory.App_BasePage import BasePage



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
    # NUMBER_PRESS_1 = (By.ID,"com.ezetap.basicapp:id/button_1")
    # NUMBER_PRESS_2 = (By.ID, "com.ezetap.basicapp:id/button_2")
    # NUMBER_PRESS_3 = (By.ID, "com.ezetap.basicapp:id/button_3")
    # NUMBER_PRESS_4 = (By.ID,"com.ezetap.basicapp:id/button_4")
    # NUMBER_PRESS_5 = (By.ID, "com.ezetap.basicapp:id/button_5")
    # NUMBER_PRESS_6 = (By.ID, "com.ezetap.basicapp:id/button_6")
    # NUMBER_PRESS_7 = (By.ID, "com.ezetap.basicapp:id/button_7")
    # NUMBER_PRESS_8 = (By.ID, "com.ezetap.basicapp:id/button_8")
    # NUMBER_PRESS_9 = (By.ID, "com.ezetap.basicapp:id/button_9")
    # NUMBER_PRESS_0 = (By.ID, "com.ezetap.basicapp:id/button_0")
    txt_orderNo = (By.ID, "com.ezetap.basicapp:id/editTextOrderNo")
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


    def __init__(self, driver):
        super().__init__(driver)

    def check_home_page_logo(self):
        return self.fetch_text(self.lbl_home, 30)

    def check_home_page_for_invalid_Login(self):
        return self.fetch_text(self.lbl_home, 5)

    # def click_enter_amount_field(self):
    #     self.perform_click(self.txt_enterAmountField)

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

    def type_amount(self, amt):
        li = []
        for i in str(amt):
            li.append((By.ID, "com.ezetap.basicapp:id/button_"+i+""))
        return li

    # def enter_order_number(self, order_number):
    #     self.perform_click(self.txt_orderNo)
    #     self.perform_sendkeys(self.txt_orderNo, order_number)
    #     self.perform_click(self.btn_paymentProceed)

    def perform_check_status(self):
        self.perform_click(self.btn_checkStatus)

    def click_on_skip_button(self):
        self.perform_click(self.btn_skip)

    def click_navigation_drawer(self):
        self.perform_click(self.mnu_navigationDrawer)

    def click_on_transaction_history(self):
        self.perform_click(self.mnu_transactionHistory)

    def click_cash_at_pos(self):
        self.perform_click(self.btn_cashAtPos)

    def enter_cash_at_pos_amount(self, amount):
        self.perform_click(self.txt_cashAtPosAmount)
        self.perform_sendkeys(self.txt_cashAtPosAmount, amount)
        self.perform_touch_action_using_cordinates(648,1119, 648,1117)

    def enter_cash_at_pos_sale_amount(self, amount):
        self.perform_click(self.txt_cashAtPosSaleAmount)
        self.perform_sendkeys(self.txt_cashAtPosSaleAmount, amount)
        self.perform_touch_action_using_cordinates(648,1119, 648,1117)

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
        self.wait_for_element_to_be_clickable(self.btn_goToHistory, 30)

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


