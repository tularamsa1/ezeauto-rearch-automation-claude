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
    lbl_navigation = (By.ID, 'com.ezetap.basicapp:id/logoToolbar')
    mnu_account = (By.ID, 'com.ezetap.basicapp:id/nav_account')
    txt_enterAmountField = (By.ID, 'com.ezetap.basicapp:id/tvAmountCard')
    btn_pay = (By.ID, "com.ezetap.basicapp:id/btnPay")
    btn_goToHistory = (By.ID, "com.ezetap.basicapp:id/btnHistory")
    img_companyLogo = (By.XPATH, '//android.widget.ImageView[@content-desc="Company Logo"]')
    tab_history = (By.ID, 'com.ezetap.basicapp:id/btnHistory')
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
    txt_home = (By.XPATH, "(//*[@resource-id ='com.ezetap.basicapp:id/tabText'])[1]")
    btn_collect_payment = (By.XPATH, "//*[@text = 'Collect Payment']")
    btn_other = (By.XPATH, "//android.widget.TextView[@text='Other']")

    btn_svm_violation = (By.XPATH, '//android.widget.Button[@text="SWM Violation"]')
    btn_plastic_ban_enforcement = (By.XPATH, '//android.widget.Button[@text="Plastic Ban Enforcement"]')
    btn_non_compliance_at_public_gathering = (
    By.XPATH, '//android.widget.Button[@text="Non Compliance at Public Gathering"]')
    btn_public_nuisance = (By.XPATH, '//android.widget.Button[@text="Public Nuisance"]')
    btn_non_segregation_of_waste = (By.XPATH, '//android.widget.Button[@text="Non Segregation of Waste"]')
    btn_unauthorized_handing_over_of_wast = (
    By.XPATH, '//android.widget.Button[@text="Unauthorized Handing Over of Waste"]')
    btn_mixing_of_segregated_waste_by_bbmp_staff = (
    By.XPATH, '//android.widget.Button[@text="Mixing of segregated waste by BBMP staff"]')
    btn_street_vendor = (By.XPATH, '//android.widget.Button[@text="Street Vendor"]')
    btn_burning_of_wast_Unauthroized_burial = (
    By.XPATH, '//android.widget.Button[@text="Burning of Waste/Unauthroized Burial"]')
    btn_construction_demolition_waste = (By.XPATH, '//android.widget.Button[@text="Construction/Demolition Waste"]')
    btn_other_offences = (By.XPATH, '//android.widget.Button[@text="Other Offences"]')

    btn_not_wearing_mask = (By.XPATH, '//android.widget.Button[@text="Not Wearing Mask"]')
    btn_violating_social_distancing = (By.XPATH, '//android.widget.Button[@text="Violating Social distancing"]')
    btn_littering = (By.XPATH, '//android.widget.Button[@text="Littering"]')
    btn_spitting = (By.XPATH, '//android.widget.Button[@text="SPITTING"]')
    btn_urinating = (By.XPATH, '//android.widget.Button[@text="Urinating"]')
    btn_open_defecation = (By.XPATH, '//android.widget.Button[@text="Open Defecation"]')
    btn_other_public_nuisance = (By.XPATH, '//android.widget.Button[@text="Other Public Nuisance"]')
    btn_domestic = (By.XPATH, '//android.widget.Button[@text="Domestic"]')
    txt_name = (By.XPATH, '//android.widget.EditText[@text="Name"]')
    txt_phone_number = (By.XPATH, '//android.widget.EditText[@text="Mobile Number"]')
    txt_ward_number = (By.XPATH, '//android.widget.EditText[@text="Enter Ward Number"]')
    txt_enter_locality_name = (By.XPATH, '//android.widget.EditText[@text="Enter Locality Name"]')
    btn_bulk_waste_generator = (By.XPATH, '//android.widget.Button[@text="Bulk Waste Generator"]')
    btn_small_commercial_establishment = (By.XPATH, "//android.widget.Button[@text='SMALL COMMERCIAL ESTABLISHMENT']")
    txt_enter_details_and_pay_screen_title = (By.XPATH, '//android.widget.TextView[@text="Enter Details and Pay"]')
    txt_fine_for_title = (By.XPATH, "//android.widget.TextView[@text='SMALL COMMERCIAL EST. VIOLATION']")
    btn_fish_poultry_slaughterhouse = (By.XPATH, '//android.widget.Button[@text="Fish, poultry & slaughterhouse"]')
    txt_fine_tittle_for_fish_poultry_slaughterhouse = \
        (By.XPATH, '//android.widget.TextView[@text="Fish, poultry and slaughterhouse Violation"]')
    txt_fine_tittle_for_not_wearing_mask = (By.XPATH, '//android.widget.TextView[@text="Not Wearing Mask"]')
    btn_fine_tittle_for_not_wearing_mask = (By.XPATH, '//android.widget.Button[@text="Not Wearing Mask"]')
    txt_fine_amount = (By.XPATH, "//*[@text='Fine Amount']/following-sibling::android.widget.TextView")

    txt_eze_wallet = (By.XPATH, "//android.widget.CheckedTextView[@text='Eze Wallet']")
    txt_balance = (By.ID, "com.ezetap.basicapp:id/tv_balance_value")
    txt_withdraw_funds = (By.XPATH, "//android.widget.TextView[@text='Withdraw Funds']")
    txt_quick_action = (By.ID, 'com.ezetap.basicapp:id/tv_quick_action')
    txt_common_ele_to_fetch_tittle = (By.ID, 'com.ezetap.basicapp:id/tvTitle')
    btn_transfer_funds = (By.ID, 'com.ezetap.basicapp:id/tv_transfer_funds')
    txt_enter_agent_mobile_no = (By.ID, 'com.ezetap.basicapp:id/etAgentID')
    txt_top_up_amt = (By.ID, 'com.ezetap.basicapp:id/etAmount')
    txt_agency_names_tittle = (By.XPATH, '//android.widget.TextView[@text="Agency Names"]')
    txt_agency_name = (By.ID, 'com.ezetap.basicapp:id/txtAgentName')
    btn_confirm = (By.ID, 'com.ezetap.basicapp:id/btnConfirm')
    txt_txn_success = (By.XPATH, '//android.widget.TextView[@text="Transaction Successful"]')
    txt_txn_message = (By.XPATH, '//android.widget.TextView[@text="Your transaction has been completed"]')
    txt_txn_no = (By.ID, 'com.ezetap.basicapp:id/txtTrxId')
    txt_updated_balance = (By.ID, 'com.ezetap.basicapp:id/txtUpdatedBalc')
    btn_cancel = (By.ID, 'com.ezetap.basicapp:id/btnClose')
    btn_go_to_wallet_screen = (By.ID, 'com.ezetap.basicapp:id/txtBack')
    btn_agency_transaction = (By.ID, 'com.ezetap.basicapp:id/tv_transaction')
    txt_see_more_options = (By.ID, "com.ezetap.basicapp:id/iv_see_more")
    txt_mobile_number = (By.ID, 'com.ezetap.basicapp:id/tv_mobile_no_value')
    txt_agency_calendar = (By.ID, 'com.ezetap.basicapp:id/mtrl_picker_title_text')
    btn_ok = (By.XPATH, "//android.widget.Button[@text='OK']")
    btn_search_by_date = (By.ID, 'com.ezetap.basicapp:id/tv_search_by_date')
    btn_agency_passbook = (By.ID, 'com.ezetap.basicapp:id/tv_passbook')
    btn_search_by_date_in_agency_or_agent_passbook = (By.ID, 'com.ezetap.basicapp:id/tvSearchByDate')
    btn_cancel_in_agency_passbook = (By.ID, 'com.ezetap.basicapp:id/cancel_button')
    txt_topup_amount = (By.ID, 'com.ezetap.basicapp:id/etAmount')
    btn_topup_proceed = (By.ID, "com.ezetap.basicapp:id/btnTopupProceed")
    txt_my_password = (By.XPATH, "//android.widget.TextView[@text='My Passbook']")
    btn_upi_payment_mode = (By.ID, 'com.ezetap.basicapp:id/paymentUPI')
    btn_agent_passbook = (By.ID, 'com.ezetap.basicapp:id/textView10')
    btn_agent_transaction = (By.ID, 'com.ezetap.basicapp:id/textView12')
    txt_last_top_up = (By.ID, 'com.ezetap.basicapp:id/tv_last_topup_value')
    txt_last_top_up_on = (By.ID, 'com.ezetap.basicapp:id/tv_last_topup_on_value')
    txt_ezewallet_mobile_no = (By.ID, 'com.ezetap.basicapp:id/tv_mobile_no_value')
    txt_agency_balance_in_txn_history = (By.XPATH,
                                         '(//*[@text="Agency Balance"]/following-sibling::android.widget.TextView)[1]')
    txt_no_txn_msg = (By.ID, 'com.ezetap.basicapp:id/textView2')

    txt_calendar = (By.ID, "com.ezetap.basicapp:id/ivCalender")
    txt_closing_bal = (By.ID, "com.ezetap.basicapp:id/txtCloseBalc")
    txt_agent_mobile_no = (By.ID, "com.ezetap.basicapp:id/etAgentID")
    txt_transfer_amt = (By.ID, "com.ezetap.basicapp:id/etAmount")
    txt_recharge = (By.ID, "com.ezetap.basicapp:id/btnCustom")
    txt_recharge_amt = (By.XPATH, "//android.widget.EditText[@text='Enter Recharge Amount']")
    txt_recharge_mobile_no = (By.XPATH, "//android.widget.EditText[@text='Mobile Number']")
    txt_go_to_wallet = (By.XPATH, "//android.widget.TextView[@text='Go To Wallet']")
    txt_amt_customer_details = (By.ID, "com.ezetap.basicapp:id/txtAmount")
    txt_mobile_no_customer_details = (By.ID, "com.ezetap.basicapp:id/txtWalletId")
    txt_self_top_ups = (By.ID, "com.ezetap.basicapp:id/txtSelfTopup")
    tab_history_config = (By.ID, "com.ezetap.basicapp:id/nav_txn_history")
    btn_pre_auth = (By.XPATH, "//android.widget.TextView[@text='Pre-Auth']")
    txt_grow_your_business = (By.XPATH, "//android.widget.TextView[@resource-id='com.ezetap.basicapp:id/tabText']")

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
        try:
            if self.wait_for_visibility_of_element_text(self.btn_collect_payment, ele_text="Collect Payment"):
                self.perform_click(self.btn_collect_payment)
        except:
            self.perform_click(self.btn_other)
        self.perform_click(self.txt_orderNo)
        self.perform_sendkeys(self.txt_orderNo, order_number)
        self.perform_click(self.btn_paymentProceed)

    def enter_amount_order_number_and_customer_details(self, amt, order_number, mobilenum, email):
        self.perform_click(self.txt_enterAmountField)
        list = self.type_amount(amt)
        for i in list:
            self.perform_click(i)
        try:
            if self.wait_for_visibility_of_element_text(self.btn_collect_payment, ele_text="Collect Payment"):
                self.perform_click(self.btn_collect_payment)
        except:
            self.perform_click(self.btn_other)
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
        try:
            if self.wait_for_visibility_of_element_text(self.btn_collect_payment, ele_text="Collect Payment"):
                self.perform_click(self.btn_collect_payment)
        except:
            self.perform_click(self.btn_other)
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
        try:
            if self.wait_for_visibility_of_element_text(self.btn_collect_payment, ele_text="Collect Payment"):
                self.perform_click(self.btn_collect_payment)
        except:
            self.perform_click(self.btn_other)
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
        self.perform_click(self.btn_pre_auth)
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
        try:
            if self.wait_for_visibility_of_element_text(self.btn_collect_payment, ele_text="Collect Payment"):
                self.perform_click(self.btn_collect_payment)
        except:
            self.perform_click(self.btn_other)
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

    def check_for_home_page(self):
        """
        This method is used to verify the home page
        """
        return self.fetch_text(self.txt_home, 30)

    def navigate_to_home(self):
        """
        This method is used to navigate home screen
        """
        self.perform_click(self.txt_home)

    def fetch_all_bbmp_violation(self):
        """
        This method is used to fetch all the fine names text and storing it in list
        return : list
        """
        return [self.fetch_text(bbmp_violation_type) for bbmp_violation_type in
                [self.btn_svm_violation, self.btn_plastic_ban_enforcement, self.btn_non_compliance_at_public_gathering]]

    def fetch_all_fine_names_of_swm_violation(self):
        """
        This method is used to fetch all the fine names text of SWM Violation and storing it in list
        return : list
        """
        return [self.fetch_text(swm_spot_fines) for swm_spot_fines in
                [self.btn_public_nuisance, self.btn_non_segregation_of_waste,
                 self.btn_unauthorized_handing_over_of_wast, self.btn_mixing_of_segregated_waste_by_bbmp_staff,
                 self.btn_street_vendor, self.btn_burning_of_wast_Unauthroized_burial,
                 self.btn_construction_demolition_waste, self.btn_other_offences]]

    def fetch_all_fine_names_of_public_nuisance(self):
        """
        This method is used to fetch all the fine names text of public nuisance and storing it in list
        return : list
        """
        return [self.fetch_text(public_nuisance_fine_types) for public_nuisance_fine_types in
                [self.btn_not_wearing_mask, self.btn_violating_social_distancing, self.btn_littering, self.btn_spitting,
                 self.btn_urinating, self.btn_open_defecation, self.btn_other_offences]]

    def validate_fine_tittle_for_not_wearing_mask(self):
        """
        This method is used to validate the fine tittle in the enter details & pay screen
        """
        self.wait_for_element(self.txt_fine_tittle_for_not_wearing_mask)

    def click_on_svm_violation(self):
        """
        This method is used to click on the SWM Violation
        """
        self.perform_click(self.btn_svm_violation)

    def click_on_public_nuisance(self):
        """
        This method is used to click on the public nuisance of the SWM violation
        """
        self.perform_click(self.btn_public_nuisance)

    def click_on_non_segregation_of_waste(self):
        """
        This method is used to click on the Non Segregation of waste of the SWM violation
        """
        self.perform_click(self.btn_non_segregation_of_waste)

    def click_on_small_commercial_establishment(self):
        """
        This method is used to click on the small commercial establishment of the Non Segregation of waste
        """
        self.perform_click(self.btn_small_commercial_establishment)

    def validate_enter_details_and_pay_screen_title(self):
        """
        This method is used to validate the Enter details and pay Screen
        """
        self.wait_for_element(self.txt_enter_details_and_pay_screen_title)

    def validate_fine_for_title(self):
        """
        This method is used to validate the tittle for fine
        """
        self.wait_for_element(self.txt_fine_for_title)

    def enter_details_for_domestic(self, name, ph_number, ward_no, locality):
        """
        This method is used to enter the required details in the Enter details and pay Screen after clicking on the Domestic
        param: name: str
        param: ph_number: str
        param: ward_no : str
        param: locality : str
        """
        self.perform_click(self.btn_domestic)
        self.perform_sendkeys(self.txt_name, name)
        self.perform_sendkeys(self.txt_phone_number, ph_number)
        self.perform_sendkeys(self.txt_ward_number, ward_no)
        self.perform_sendkeys(self.txt_enter_locality_name, locality)

    def enter_details_for_small_commercial_establishment(self, name, ph_number, ward_no, locality):
        """
        This method is used to enter the required details in the Enter details and pay Screen after clicking on the small commercial establishment
        param: name: str
        param: ph_number: str
        param: ward_no : str
        param: locality : str
        """
        self.perform_click(self.btn_small_commercial_establishment)
        self.perform_sendkeys(self.txt_name, name)
        self.perform_sendkeys(self.txt_phone_number, ph_number)
        self.perform_sendkeys(self.txt_ward_number, ward_no)
        self.perform_sendkeys(self.txt_enter_locality_name, locality)

    def enter_details_for_bulk_waste_generator(self, name, ph_number, ward_no, locality):
        """
       This method is used to enter the required details in the Enter details and pay Screen after clicking on the bulk waste generator
       param: name: str
       param: ph_number: str
       param: ward_no : str
       param: locality : str
       """
        self.perform_click(self.btn_bulk_waste_generator)
        self.perform_sendkeys(self.txt_name, name)
        self.perform_sendkeys(self.txt_phone_number, ph_number)
        self.perform_sendkeys(self.txt_ward_number, ward_no)
        self.perform_sendkeys(self.txt_enter_locality_name, locality)

    def click_on_unauthorized_handing_over_of_wast(self):
        """
        This method is used to click on the unauthorized handing over of waste button
        """
        self.perform_click(self.btn_unauthorized_handing_over_of_wast)

    def click_on_fish_poultry_slaughterhouse(self):
        """
        This method is used to click on the fish, poultry and slaughterhouse button
        """
        self.perform_click(self.btn_fish_poultry_slaughterhouse)

    def validate_fine_tittle_for_fish_poultry_slaughterhouse(self):
        """
        This method is used to validate the fine tittle in the enter details & pay screen
        """
        self.wait_for_element(self.txt_fine_tittle_for_fish_poultry_slaughterhouse)

    def click_on_prepaid_recharge(self):
        """
            This method is used to click on prepaid recharge btn
        """
        self.perform_click(self.lbl_prepaid_recharge)

    def click_on_not_wearing_mask(self):
        """
         This method is used to click on not wearing mask btn
        """
        self.perform_click(self.btn_fine_tittle_for_not_wearing_mask)

    def fetch_amount_from_enter_details_and_pay_screen(self):
        return int(self.fetch_text(self.txt_fine_amount))

    def click_on_eze_wallet(self):
        """
            This method is used to click on ezewallet
        """
        self.wait_for_element(self.txt_eze_wallet)
        self.perform_click(self.txt_eze_wallet)

    def fetch_balance_txt(self):
        """
            This method is used to fetch the balance text from ezewallet
            return : str
        """
        self.wait_for_element(self.txt_balance)
        return self.fetch_text(self.txt_balance)

    def click_on_withdraw_funds(self):
        """
            This method is used to click on withdraw funds
        """
        self.wait_for_element(self.txt_withdraw_funds)
        self.perform_click(self.txt_withdraw_funds)

    def validate_quick_action_under_ezewallet_screen(self):
        """
        This method is used to Verify quick action is present under ezewalet screen or not and fetchs the text
        return : str
        """
        self.wait_for_element(self.txt_quick_action)
        return self.fetch_text(self.txt_quick_action)

    def validate_withdraw_funds_screen(self):
        """
        This method is used to validate withdraw funds screen
        """
        self.wait_for_element(self.txt_withdraw_funds)

    def validate_eze_wallet_screen(self):
        """
        This method is used to validate eze wallet screen
        """
        self.wait_for_element(self.txt_common_ele_to_fetch_tittle)

    def fetch_eze_wallet_screen(self):
        """
        This method is used to fetch text from  eze wallet tittle
        return: str
        """
        return self.fetch_text(self.txt_common_ele_to_fetch_tittle)

    def fetch_txn_status(self):
        """
        This method is used to fetch the txn status in the txn screen
        """
        return self.fetch_text(self.txt_txn_success)

    def fetch_txn_message(self):
        """
        This method is used to fetch the txn message in the txn screen
        """
        return self.fetch_text(self.txt_txn_message)

    def fetch_txn_number(self):
        """
        This method is used to fetch the txn id in the txn screen
        """
        return self.fetch_text(self.txt_txn_no)

    def fetch_updated_balance(self):
        """
        This method is used to fetch the updated balance in the txn screen
        """
        return self.fetch_text(self.txt_updated_balance)

    def click_on_transfer_funds(self):
        """
        This method is used is to click on the transfer funds
        """
        self.wait_for_element(self.btn_transfer_funds)
        self.perform_click(self.btn_transfer_funds)

    def validate_transfer_funds_screen(self):
        """
        This method is used to verify transfer funds screen and fetches text
        return: str
        """
        self.wait_for_element(self.txt_common_ele_to_fetch_tittle)
        return self.fetch_text(self.txt_common_ele_to_fetch_tittle)

    def validate_transfer_funds_wallet_id_and_transfer_amount_input_field(self):
        """
        This method is used to verify agent wallet id and amount input field in the transfer funds screen
        """
        self.wait_for_element(self.txt_enter_agent_mobile_no)
        self.wait_for_element(self.txt_top_up_amt)

    def fetch_agency_name_txt(self):
        """
        This method is used to fetch agency name
        return : str
        """
        return self.fetch_text(self.txt_agency_name)

    def validate_proceed_button(self):
        """
        This method is used to check whether proceed button is enabled or not
        """
        button = self.wait_for_element(self.btn_langProceed)
        return button.is_enabled()

    def enter_agent_wallet_id(self, agent_wallet_id):
        """
        This method is used to enter agent wallet id
        param: agent_wallet_id : str
        """
        self.wait_for_element(self.txt_enter_agent_mobile_no)
        self.perform_sendkeys(self.txt_enter_agent_mobile_no, agent_wallet_id)

    def enter_transfer_funds_amount(self, amount):
        """
           This method is used to enter amount
           param: amount : str
        """
        self.wait_for_element(self.txt_top_up_amt)
        self.perform_sendkeys(self.txt_top_up_amt, amount)

    def click_on_confirm_btn(self):
        """
        This method is used to click on the confirm button
        """
        self.wait_for_element(self.btn_confirm)
        self.perform_click(self.btn_confirm)

    def perform_transfer_funds_from_agency_to_agent(self, agent_wallet_id, transfer_amount):
        """
        This method used to transfer funds from agency to agent wallet
        param: agent_wallet_id : str
        param: transfer_amount : str
        """
        self.wait_for_element(self.txt_enter_agent_mobile_no)
        self.perform_sendkeys(self.txt_enter_agent_mobile_no, agent_wallet_id)
        self.perform_sendkeys(self.txt_top_up_amt, transfer_amount)
        self.perform_click(self.btn_langProceed)

    def click_on_cancel_btn(self):
        """
        This method is used to click on the close in the confirm details screen
        """
        self.wait_for_element(self.btn_cancel)
        self.perform_click(self.btn_cancel)

    def click_on_go_to_wallet_btn(self):
        """
        This method is used to click on the go to wallet button
        """
        self.perform_click(self.btn_go_to_wallet_screen)

    def click_on_agency_transaction_option_under_quick_action(self):
        """
        This method is used to click on the agency transaction
        """
        self.wait_for_element(self.btn_agency_transaction)
        self.perform_click(self.btn_agency_transaction)

    def validate_agency_transaction_screen(self):
        """
        This method is used to verify agency transaction screen and fetches text
        """
        self.wait_for_element(self.txt_common_ele_to_fetch_tittle)
        return self.fetch_text(self.txt_common_ele_to_fetch_tittle)

    def fetch_mobile_number(self):
        """
        This method is used to fetch mobile number
        return : str
        """
        return self.fetch_text(self.txt_mobile_number)

    def click_on_see_more_btn(self):
        """
        This method is used to click on the see more button
        """
        self.perform_click(self.txt_see_more_options)

    def validate_calendar_in_agency_transaction_screen(self):
        """
        This method is used to verify calendar in the agency transaction screen
        """
        self.wait_for_element(self.txt_agency_calendar)

    def click_on_given_date(self, date):
        """
        This method is used to click on the given date
        """
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + date + ''))

    def validate_ok_button(self):
        """
        This method is used to verify whether ok button is enabled or not
        """
        button = self.wait_for_element(self.btn_ok)
        return button.is_enabled()

    def click_on_ok_btn(self):
        """
        This method is used to click ok
        """
        self.perform_click(self.btn_ok)

    def click_on_search_by_date(self):
        """
        This method is used to click on the search by date
        """
        self.perform_click(self.btn_search_by_date)

    def click_on_agency_passbook(self):
        """
        This method is used to click on the agency passbook under quick action
        """
        self.wait_for_element(self.btn_agency_passbook)
        self.perform_click(self.btn_agency_passbook)

    def validate_agency_passbook_screen(self):
        """
        This method is used to verify agency passbook screen and fetches text
        return : str
        """
        self.wait_for_element(self.txt_common_ele_to_fetch_tittle)
        return self.fetch_text(self.txt_common_ele_to_fetch_tittle)

    def click_on_search_by_date_in_agency_or_agent_passbook_screen(self):
        """
        This method is used to click on the search by date in the agency or agent passbook screen
        """
        self.perform_click(self.btn_search_by_date_in_agency_or_agent_passbook)

    def validate_future_date(self, future_date):
        """
        This method is used to verify future date in calendar is clickable or not
        """
        button = self.wait_for_element((AppiumBy.ACCESSIBILITY_ID, '' + future_date + ''))
        return button.is_enabled

    def click_on_agency_passbook_cancel_btn(self):
        """
        This method is used to click on the cancel button
        """
        self.perform_click(self.btn_cancel_in_agency_passbook)

    def validate_topup_field_and_proceed_btn(self):
        """
        This method is used to validate top-up field and proceed button for agent
        """
        self.wait_for_element(self.txt_topup_amount)
        self.wait_for_element(self.btn_topup_proceed)

    def perform_top_up(self, amount):
        """
        This method is used to perform successful top up
        """
        self.perform_sendkeys(self.txt_topup_amount, amount)
        self.perform_click(self.btn_topup_proceed)
        self.perform_click(self.btn_upi_payment_mode)

    def validate_top_up_proceed_button(self):
        """
        This method is used to check whether proceed button is enabled or not
        return boolean
        """
        button = self.wait_for_element(self.btn_topup_proceed)
        return button.is_enabled()

    def validate_agent_passbook(self):
        """
        This method is used to verify agent passbook under quick action and fetches text
        """
        self.wait_for_element(self.btn_agent_passbook)
        return self.fetch_text(self.btn_agent_passbook)

    def validate_agent_transaction(self):
        """
        This method is used to verify agent transaction under quick action amd fetches text
        """
        self.wait_for_element(self.btn_agent_transaction)
        return self.fetch_text(self.btn_agent_transaction)

    def fetch_agent_balance(self):
        """
        This method is used to fetch agent balance in the eze wallet screen
        return : str
        """
        return self.fetch_text(self.txt_balance)

    def fetch_last_top_up(self):
        """
        This method is used to fetch agent last top up in the eze wallet screen
        return: str
        """
        self.wait_for_element(self.txt_last_top_up)
        return self.fetch_text(self.txt_last_top_up)

    def fetch_last_top_up_on(self):
        """
            This method is used to fetch agent last top up on in the eze wallet screen
            return: str
        """
        self.wait_for_element(self.txt_last_top_up_on)
        return self.fetch_text(self.txt_last_top_up_on)

    def fetch_mobile_no(self):
        """
        This method is used to fetch agent mobile number in the eze wallet screen
        return: str
        """
        self.wait_for_element(self.txt_ezewallet_mobile_no)
        return self.fetch_text(self.txt_ezewallet_mobile_no)

    def click_on_my_passbook(self):
        """
        This method is used to click on my passbook under quick action
        """
        self.wait_for_element(self.txt_my_password)
        self.perform_click(self.txt_my_password)

    def fetch_agency_transaction_amount(self, transfer_mode):
        """
        This method is used to fetch agency amount transaction to agent in the txn history
        param: transfer_mode: str
        return: str
        """
        txt_transfer_amount = (
        By.XPATH, f'(//*[@text="{transfer_mode}"]/following-sibling::android.widget.TextView)[1]')
        return self.fetch_text(txt_transfer_amount)

    def fetch_agency_transaction_date(self, transfer_mode):
        """
        This method is used to fetch date of agency transfer amount in the txn history
        param: transfer_mode: str
        return: str
        """
        txt_transfer_funds_date = (
            By.XPATH, f'(//*[@text="{transfer_mode}"]/following-sibling::android.widget.TextView)[2]')
        return self.fetch_text(txt_transfer_funds_date)

    def fetch_agency_balance_from_txn_history(self):
        """
        This method is used to fetch agency balance from the txn history
        return: str
        """
        return self.fetch_text(self.txt_agency_balance_in_txn_history)

    def fetch_no_transaction_msg(self):
        """
        This method is used to fetch massage when there is no txn for the selected date
        return: str
        """
        return self.fetch_text(self.txt_no_txn_msg)

    def fetch_self_top_ups_value(self):
        """
            This method is used to fetch self top_ups values
            return : str
        """
        self.wait_for_element(self.txt_self_top_ups)
        return self.fetch_text(self.txt_self_top_ups)

    def enter_top_up_my_wallet_details(self, top_up_amt):
        """
            This method is used to enter top_up amount and click on proceed button
        """
        self.wait_for_element(self.txt_top_up_amt)
        self.perform_sendkeys(self.txt_top_up_amt, top_up_amt)
        self.wait_for_element(self.btn_topup_proceed)
        self.perform_click(self.btn_topup_proceed)

    def click_on_calender_and_select_date(self, current_date):
        """
            This method is used click on calendar and select the date
            param: current_date: str
        """
        select_date = (By.XPATH, f"//android.widget.TextView[@text='{current_date}']")
        self.wait_for_element(self.txt_calendar)
        self.perform_click(self.txt_calendar)
        self.wait_for_element(select_date)
        self.perform_click(select_date)
        self.wait_for_element(self.btn_ok)
        self.perform_click(self.btn_ok)

    def click_on_see_more_options(self):
        """
            This method is used to click on see more options
        """
        self.wait_for_element(self.txt_see_more_options)
        self.perform_click(self.txt_see_more_options)

    def fetch_closing_balance(self):
        """
            This method is used to fetch closing balance value
            return : str
        """
        self.wait_for_element(self.txt_closing_bal)
        return self.fetch_text(self.txt_closing_bal)

    def enter_mobile_no_and_transfer_amt(self, agent_mobile_no, transfer_amt):
        """
            This method is used to enter withdraw funds details like mobile no, transfer amount
            param: agent_mobile_no: str
            param: transfer_amt: str
        """
        self.wait_for_element(self.txt_agent_mobile_no)
        self.perform_click(self.txt_agent_mobile_no)
        self.perform_sendkeys(self.txt_agent_mobile_no, agent_mobile_no)
        self.perform_sendkeys(self.txt_transfer_amt, transfer_amt)

    def enter_agency_recharge_details(self, recharge_amt, recharge_mobile_no):
        """
            This method is used to enter agency recharge details like recharge amount, mobile
            param: recharge_amt: str
            param: recharge_mobile_no: str
        """
        self.wait_for_element(self.txt_recharge)
        self.perform_click(self.txt_recharge)
        self.wait_for_element(self.txt_recharge_amt)
        self.perform_click(self.txt_recharge_amt)
        self.perform_sendkeys(self.txt_recharge_amt, recharge_amt)
        self.wait_for_element(self.txt_recharge_mobile_no)
        self.perform_click(self.txt_recharge_mobile_no)
        self.perform_sendkeys(self.txt_recharge_mobile_no, recharge_mobile_no)

    def click_on_go_to_wallet(self):
        """
            This method is used to click on go to wallet
        """
        self.wait_for_element(self.txt_go_to_wallet)
        self.perform_click(self.txt_go_to_wallet)

    def validate_withdraw_fund_title(self):
        """
            This method is used validate withdraw funds
        """
        self.wait_for_element(self.txt_withdraw_funds)

    def fetch_amount_txt(self):
        """
            This method is used fetch amount text
            return : str
        """
        self.wait_for_element(self.txt_amt_customer_details)
        return self.fetch_text(self.txt_amt_customer_details)

    def fetch_customer_mobile_no(self):
        """
            This method is used fetch mobile no
            return : str
        """
        self.wait_for_element(self.txt_mobile_no_customer_details)
        return self.fetch_text(self.txt_mobile_no_customer_details)

    def click_on_history_config(self):
        """
        This method is used to click on the history button in the home screen
        """
        self.perform_click(self.tab_history_config)

    def click_grow_your_business(self):
        self.wait_for_element(self.txt_grow_your_business)
        self.perform_click(self.txt_grow_your_business)