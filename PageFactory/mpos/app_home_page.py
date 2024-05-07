import re
import time

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class HomePage(BasePage):
    lbl_home = (By.ID, 'com.ezetap.basicapp:id/navigation_bar_item_large_label_view')
    lbl_navigation = (By.ID, 'com.ezetap.basicapp:id/nav_account')
    mnu_account = (By.ID, 'com.ezetap.basicapp:id/nav_account')
    txt_enterAmountField = (By.ID, 'com.ezetap.basicapp:id/tvAmountCard')
    btn_pay = (By.ID, "com.ezetap.basicapp:id/btnPay")
    btn_goToHistory = (By.ID, "com.ezetap.basicapp:id/clGotoHistory")
    img_companyLogo = (By.XPATH, '//android.widget.ImageView[@content-desc="Company Logo"]')
    tab_history = (By.ID, "com.ezetap.basicapp:id/nav_txn_history")
    mnu_engSideMenu = (By.XPATH, '//android.widget.ImageButton[@content-desc="Open navigation drawer"]')
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

    txt_my_reports = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvReportsTitle')
    scrollable_it = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_goToHistory2')
    txt_todays_sales = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTodaySale')
    mnu_account_hindi = (AppiumBy.XPATH, '//android.widget.FrameLayout[@content-desc="अकाउंट"]')
    txt_yesterday_sales = (AppiumBy.XPATH, '//*[@text="Yesterday"]')
    btn_start_btn = (AppiumBy.ID, "com.ezetap.basicapp:id/btnStartConfig")

    lbl_fixed_line_LOB = (By.XPATH, "//android.widget.Button[@text='Fixed line']")
    lbl_fixed_line_bill_collection_active = (By.XPATH, "//*[@text='Bill Collection-Active']")
    txt_bill_collection_active_fixed_line_no = (By.XPATH, "//*[@text='Fixed Line No.']")
    txt_fixed_line_no_title = (By.XPATH, "//*[@text='Fixed Line No']")
    btn_fetch_details = (By.XPATH, "//*[@text='Fetch Details']")
    btn_check_out = (By.XPATH, "//*[@text='Checkout']")
    lbl_dth_LOB = (By.XPATH, "//android.widget.Button[@text='dth']")
    lbl_search_by_dth_id = (By.XPATH, "//*[@text='Search By DTH ID']")
    txt_dth_id = (By.XPATH, "//*[@text='Enter DTH ID']")
    btn_search_details = (By.XPATH, "//*[@text='Search Details']")
    txt_customer_mobile_no = (By.XPATH, "//*[@text='CustomerMobile No']")
    txt_alternative_mobile_no = (By.XPATH, "(//*[@class='android.widget.EditText'])[3]")
    txt_email_id = (By.XPATH, "//android.widget.EditText[@text='Email']")
    lbl_pos_sale_LOB = (By.XPATH, "//android.widget.Button[@text='Pos Sales']")
    txt_pos_sale_performa_no = (By.XPATH, "//*[@text='Enter Performa No.']")
    lbl_postpaid_mobile_LOB = (By.XPATH, "//android.widget.Button[@text='Postpaid-Mobile']")
    lbl_postpaid_bill_collection_active = (By.XPATH, "//androidx.recyclerview.widget.RecyclerView/android.view.ViewGroup[1]")
    txt_enter_no_field = (By.XPATH, "//android.widget.EditText")
    txt_customer_details = (AppiumBy.XPATH, '//*[@text="Customer Details"]')
    lbl_prepaid_mobile_LOB = (By.XPATH, "//android.widget.Button[@text='Pre Paid-Mobile']")
    lbl_prepaid_recharge = (By.XPATH, '//*[@text="Prepaid Recharge"]')
    txt_mobile_no = (By.XPATH, '//*[@text="Mobile No."]')
    txt_re_enter_mobile_no = (By.XPATH, '//*[@text="Re-enter Mobile No."]')
    txt_amt = (By.XPATH, '//android.widget.EditText[@text="Amount[INR]"]')
    lbl_new_activation_LOB = (By.XPATH, "//android.widget.Button[@text='New Activation']")
    lbl_new_act_butterfly = (By.XPATH, "//androidx.recyclerview.widget.RecyclerView/android.view.ViewGroup[1]")
    txt_caf_no = (By.XPATH, '//*[@text="CAF no."]')
    txt_order_no = (By.XPATH, '//*[@text="Order no."]')

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
                li.append((By.ID, "com.ezetap.basicapp:id/button_" + i + ""))
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
        """
        This method is used to perform online refund
        param: password str
        param: card_last_four_digit str
        param: device_serial str
        """
        self.perform_click(self.btn_Refund)
        self.perform_sendkeys(self.txt_password, password)
        self.perform_click(self.btn_proceed)
        self.perform_sendkeys(self.card_last_four_digit, card_last_four_digit)
        self.perform_click(self.txt_date_txn_history)
        self.perform_click(self.button1)
        self.perform_click(self.btn_authenticate)
        self.wait_for_visibility_of_elements(self.txnCard)
        txn_locator_list = self.driver.find_elements(By.ID, 'com.ezetap.basicapp:id/txnCard')
        txn_locator_list[0].click()
        self.perform_click(self.btn_refund)
        self.perform_click(self.proceed_btn)
        self.perform_sendkeys(self.device_serial, device_serial)
        self.perform_click(self.btn_externalSerialProceed)

    def fetch_text_from_my_reports_tab(self):
        return self.fetch_text(self.txt_my_reports)

    def click_on_go_to_history(self):
        self.wait_for_element(self.btn_goToHistory)
        self.perform_click(self.btn_goToHistory)

    def fetch_todays_sales_text(self):
        return self.fetch_text(self.txt_todays_sales)

    def todays_sales_go_to_history(self):
        self.perform_click(self.scrollable_it)

    def get_coordinates(self):
        """
        gives the relative co_ordinates of an element based on bounds attribute
        """
        bounds_str = self.wait_for_element(self.txt_yesterday_sales).get_attribute("bounds")
        print(bounds_str)
        matches = re.findall(r'\d+', bounds_str)
        if len(matches) >= 2:
            b = int(matches[0])
            b1 = round(int(matches[0]) * 0.16)
            c1 = round(int(matches[1]))
            return b, b1, c1
        else:
            logger.info("Not enough numeric values found in the string")

    def scroll_to_element_horizontally(self, swipe_count, b, b1, c1):
        """
        This function is used to scroll horizontally using relative co-ordinates
        """
        for i in range(1, swipe_count + 1):
            action = TouchAction(self.driver)
            action.press(x=b, y=c1).move_to(x=b1, y=c1).release().perform()

    def click_on_account_mnu_hindi(self):
        """
        performs clicking on hindi language
        """
        self.perform_click(self.mnu_account_hindi)

    def wait_to_load_today_sales(self):
        """
        This function is used to wait until today sales element is visible
        """
        self.wait_for_element(self.txt_todays_sales)

    def enter_amount_without_order_number(self, amt: int):
        """
        Enters amount without order ID and clicks on proceed button
        """
        self.perform_click(self.txt_enterAmountField)
        list = self.type_amount(amt)
        for i in list:
            self.perform_click(i)
        self.perform_click(self.btn_pay)
        self.perform_click(self.btn_paymentProceed)

    def click_on_start_btn(self):
        self.perform_click(self.btn_start_btn)

    def fetch_all_lobs(self):
        """
            This method is used to fetch all the lobs text and storing it in list
            return : list
        """
        list_of_lobs = []
        for i in range(1, 7):
            all_lobs = (By.XPATH, f"(//*[@resource-id='com.ezetap.basicapp:id/btnCustom'])[{i}]")
            self.wait_for_element(all_lobs)
            lobs = self.fetch_text(all_lobs)
            list_of_lobs.append(lobs)
        return list_of_lobs

    def click_on_fixed_line_LOB(self):
        """
            This method is used to click on fixed_line lob
        """
        self.perform_click(self.lbl_fixed_line_LOB)

    def click_on_fixed_line_bill_collection_active(self):
        """
           This method is used to click on fixed_line_bill_collection_active sub lob
        """
        self.wait_for_element(self.lbl_fixed_line_bill_collection_active)
        self.perform_click(self.lbl_fixed_line_bill_collection_active)

    def enter_bill_collection_active_details(self, fixed_line_no: str):
        """
            This method is used to send fixed line no for bill_collection_active sub lob and click on fetch details btn
            :param fixed_line_no: str
        """
        self.perform_click(self.txt_bill_collection_active_fixed_line_no)
        self.perform_sendkeys(self.txt_bill_collection_active_fixed_line_no, fixed_line_no)
        self.wait_for_element(self.btn_fetch_details)
        self.perform_click(self.btn_fetch_details)

    def validate_fixed_line_no_title(self):
        """
            This method is used to validate the fixed line no title
        """
        self.wait_for_element(self.txt_fixed_line_no_title)

    def click_on_check_out_btn(self):
        """
            This method is used to click on check out btn
        """
        self.wait_for_element(self.btn_check_out)
        self.perform_click(self.btn_check_out)

    def click_on_dth_LOB(self):
        """
            This method is used to click on dth lob
        """
        self.perform_click(self.lbl_dth_LOB)

    def enter_customer_details_for_search_by_id(self, dth_id_val: str, customer_mobile_number: str,
                                                alter_no: str, email_address: str):
        """
            This method is used to enter the customer details for search_by_id sub lob
            param: dth_id_val: str
            param: customer_mobile_number: str
            param: alter_no: str
            param: email_address: str
        """
        self.perform_click(self.lbl_search_by_dth_id)
        self.perform_sendkeys(self.txt_dth_id, dth_id_val)
        self.wait_for_element(self.btn_search_details)
        self.perform_click(self.btn_search_details)
        self.wait_for_element(self.txt_customer_mobile_no)
        self.perform_click(self.txt_customer_mobile_no)
        self.perform_sendkeys(self.txt_customer_mobile_no, customer_mobile_number)
        self.perform_sendkeys(self.txt_alternative_mobile_no, alter_no)
        self.perform_sendkeys(self.txt_email_id, email_address)
        self.wait_for_element(self.btn_fetch_details)
        self.perform_click(self.btn_fetch_details)

    def click_on_pos_sale_LOB(self):
        """
            This method is used to click on pos sale lob
        """
        self.perform_click(self.lbl_pos_sale_LOB)

    def enter_customer_details_for_pos_sale(self, performa_no: str, email: str):
        """
            This method is used to enter the customer details for pos sale lob
                param: performa_no: str
                param: email: str
        """
        self.perform_click(self.txt_pos_sale_performa_no)
        self.perform_sendkeys(self.txt_pos_sale_performa_no, performa_no)
        self.wait_for_element(self.btn_fetch_details)
        self.perform_click(self.btn_fetch_details)
        self.perform_click(self.txt_email_id)
        self.perform_sendkeys(self.txt_email_id, email)

    def click_on_postpaid_mobile_LOB(self):
        """
            This method is used to click on the postpaid mobile lob
        """
        self.perform_click(self.lbl_postpaid_mobile_LOB)

    def click_on_postpaid_bill_collection_active(self, ph_no):
        """
            This method is used to enter the phone number on the post_paid_bill_collection_active sub lob
            param: ph_no: str
        """
        self.perform_click(self.lbl_postpaid_bill_collection_active)
        self.perform_sendkeys(self.txt_enter_no_field, ph_no)

    def click_on_fetch_btn(self):
        """
            This method is used to click on the fetch button
        """
        self.perform_click(self.btn_fetch_details)

    def fetch_customer_details_txt(self):
        """
            This method is used to fetch the customer details text from amount screen
            return : str
        """
        return self.fetch_text(self.txt_customer_details)

    def fetch_checkout_btn_txt(self):
        """
            This method is used to fetch the checkout btn text from amount screen
            return : str
        """
        return self.fetch_text(self.btn_check_out)


    def click_on_prepaid_mobile_LOB(self):
        """
            This method is used to click on the prepaid mobile recharge lob
        """
        self.perform_click(self.lbl_prepaid_mobile_LOB)

    def click_on_new_activation_LOB(self):
        """
            This method is used to click on the new activation lob
        """
        self.perform_click(self.lbl_new_activation_LOB)

    def enter_mobile_activation_butterfly_details(self, caf_no, ph_number, order_no):
        """
            This method is used to enter the new activation butterfly details
            param: caf_no: str
            param: ph_number: str
            param: order_no: str
        """
        self.perform_click(self.lbl_new_act_butterfly)
        self.perform_sendkeys(self.txt_caf_no, caf_no)
        self.perform_sendkeys(self.txt_mobile_no, ph_number)
        self.perform_sendkeys(self.txt_order_no, order_no)

    def enter_mobile_number(self, ph_number):
        """
            This method is used to enter the mobile number on the payment page
            param: ph_number: str
        """
        self.perform_sendkeys(self.txt_mobile_no, ph_number)

    def enter_prepaid_recharge_details(self, ph_number, amount):
        """
            This method is used to enter prepaid recharge details
            param: ph_number: str
            param: amount: str
        """
        self.perform_click(self.lbl_prepaid_recharge)
        self.perform_sendkeys(self.txt_mobile_no, ph_number)
        self.perform_sendkeys(self.txt_re_enter_mobile_no, ph_number)
        self.perform_sendkeys(self.txt_amt, amount)
        self.perform_click(self.btn_fetch_details)
