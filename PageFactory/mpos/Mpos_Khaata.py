import time
from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage


class Khaata(BasePage):
    btn_mykhaata = (AppiumBy.XPATH, '(//android.widget.ImageView[@content-desc="Feature logo"])[1]')
    btn_khaata_holders = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvKhaataHolders')
    btn_khaata_enteries = (AppiumBy.ID, 'com.ezetap.basicapp:id/tabKhaataEntries')
    txt_search = (AppiumBy.ID, 'com.ezetap.basicapp:id/searchAutoCompleteTextView')
    btn_search = (AppiumBy.ID, 'com.ezetap.basicapp:id/cvSearch')
    btn_back = (AppiumBy.ID, 'com.ezetap.basicapp:id/imgToolbarBack')
    txt_first_search_result = (AppiumBy.ID, 'com.ezetap.basicapp:id/itemRoot')
    btn_new_khaata_holder = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnNewKhaataHolder')
    txt_khaata_holder_phNo_input = (AppiumBy.ID, 'com.ezetap.basicapp:id/etKhataHolderNumber')
    txt_khaata_holder_name_input = (AppiumBy.ID, 'com.ezetap.basicapp:id/etKhataHolderName')
    lbl_customer = (AppiumBy.ID, 'com.ezetap.basicapp:id/lblCustomer')
    lbl_supplier = (AppiumBy.ID, 'com.ezetap.basicapp:id/lblSupplier')
    lbl_friends = (AppiumBy.ID, 'com.ezetap.basicapp:id/lblFriend')
    lbl_staff = (AppiumBy.ID, 'com.ezetap.basicapp:id/lblDistributor')
    lbl_other = (AppiumBy.ID, 'com.ezetap.basicapp:id/lblOthers')
    btn_cancel = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnCancel')
    btn_proceed = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnProceed')
    txt_khaata_holder_name = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTitle')
    txt_khaata_holder_phNo = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvCustomerPhone')
    txt_khaata_holder_tag = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvCustomerTag')
    txt_you_give_money = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTopYouGaveAmount')
    mnu_khaata_holder = (AppiumBy.ID, 'com.ezetap.basicapp:id/imgMenu')
    lbl_khaata_edit_account = (AppiumBy.XPATH, '//*[@text="Edit account"]')
    lbl_khaata_remove_khaata_holder = (AppiumBy.XPATH, '//*[@text="Remove Khaata Holder"]')
    lbl_clear_khaata_entries = (AppiumBy.XPATH, '//*[@text="Clear Khaata Entries"]')
    lbl_collect_payment = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvCollectPayment')
    txt_enter_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/etAmount')
    btn_you_give = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvYouGaveButton')
    btn_you_got = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvYouGotButton')
    txt_enter_amount_given_or_received = (AppiumBy.ID, 'com.ezetap.basicapp:id/etCashAmount')
    txt_enter_details_for_given_or_received_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/etDetails')
    lbl_calender = (AppiumBy.ID, 'com.ezetap.basicapp:id/cvCalender')
    btn_ok = (AppiumBy.ID, 'android:id/button1')
    btn_reminder = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvReminder')
    btn_send_reminder = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_send_reminder')
    lbl_tap_to_view_and_hide = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnShowHide')
    btn_save = (AppiumBy.XPATH, '//*[@text="Save"]')
    btn_collect_pay = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnCollectPayment')
    lbl_entries = (AppiumBy.XPATH, '(//*[@resource-id="com.ezetap.basicapp:id/clRoot"])[2]')
    btn_delete = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnDelete')
    btn_edit = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnEditDetails')
    txt_description = (AppiumBy.ID, 'com.ezetap.basicapp:id/etDescription')
    btn_filter = (AppiumBy.ID, 'com.ezetap.basicapp:id/cvFilters')
    lbl_by_balance_all = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnBalAll')
    lbl_by_balance_advance = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnBalAdvance')
    lbl_by_balance_due = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnBalDue')
    lbl_by_label_all = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnByLabelAll')
    lbl_by_label_customer = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnByLabelCustomer')
    lbl_by_label_supplier = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnByLabelSupplier')
    lbl_by_label_staff = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnByLabelStaff')
    lbl_by_label_friends = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnByLabelFriend')
    lbl_by_label_others = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnByLabelOthers')
    lbl_sort_by_most_recent = (AppiumBy.ID, 'com.ezetap.basicapp:id/rbMostRecent')
    lbl_sort_by_oldest = (AppiumBy.ID, 'com.ezetap.basicapp:id/rbOldest')
    lbl_sort_by_highest_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/rbHighestAmount')
    lbl_sort_by_name = (AppiumBy.ID, 'com.ezetap.basicapp:id/rbByName')
    btn_apply = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnApply')
    btn_clear = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvClear')
    txt_user_name_inline_error_message = (AppiumBy.ID, 'com.ezetap.basicapp:id/textinput_error')
    txt_entry_account_name = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvName')
    txt_entry_account_tag = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTag')
    txt_entry_message = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTopYouGave')
    txt_entry_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTopYouGaveAmount')
    txt_entry_description = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvDescriptionContent')
    txt_date = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvDate')
    txt_no_khaata_holder_found = (AppiumBy.XPATH, '//*[@text="No Khaata Holder found"]')
    btn_collect_payment_proceeed = (AppiumBy.XPATH, '//*[@text="Proceed"]')
    img_tick_mark = (AppiumBy.ID, 'com.ezetap.basicapp:id/tick1')
    txt_no_khaata_enteries = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvNoKhaataEntries')
    txt_status = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_balace_due')
    txt_reminder_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_amount')
    txt_reminder_holder_number = (AppiumBy.ID,'com.ezetap.basicapp:id/tv_number')
    txt_reminder_holder_name = (AppiumBy.ID,'com.ezetap.basicapp:id/tv_khaata_holder_name')
    txt_amount_status = (AppiumBy.ID,'com.ezetap.basicapp:id/tvTopYouGave')
    txt_amount_in_the_holder_screen = (AppiumBy.ID,'com.ezetap.basicapp:id/tvTopYouGaveAmount')
    txt_payment_mode = (AppiumBy.ID,'com.ezetap.basicapp:id/tvPaidViaData')
    lbl_recent_entry_from_holder_screen = (AppiumBy.ID,'com.ezetap.basicapp:id/clRoot')
    # TOAST_XPATH = (AppiumBy.XPATH, '//android.widget.Toast')

    def __init__(self, driver):
        super().__init__(driver)

    def click_my_khaata(self):
        """
        This method is used to click on the my khaata tab in the main screen
        """
        self.perform_click(self.btn_mykhaata)

    def click_khaata_holders(self):
        self.perform_click(self.btn_khaata_holders)

    def click_khaata_entries(self):
        self.perform_click(self.btn_khaata_enteries)

    def click_first_khaata_holder_search_result(self):
        """
        This method is used to click on the first khaata holder based on the result
        """
        self.perform_click(self.txt_first_search_result)

    def click_proceed_button(self):
        self.perform_click(self.btn_proceed)

    def click_cancel_button(self):
        self.perform_click(self.btn_cancel)

    def click_on_back(self):
        self.perform_click(self.btn_back)

    def click_on_menu(self):
        self.perform_click(self.mnu_khaata_holder)

    def click_remove_khaata_holder(self):
        self.perform_click(self.lbl_khaata_remove_khaata_holder)

    def click_clear_khaata_entries(self):
        """
        This function is used to clear all the entries in the khaata
        """
        self.perform_click(self.lbl_clear_khaata_entries)

    def perform_collect_payment(self, enter_amount: int):
        self.perform_click(self.btn_collect_pay)
        self.wait_for_element(self.txt_enter_amount).clear()
        self.perform_sendkeys(self.txt_enter_amount, enter_amount)
        self.perform_click(self.btn_collect_payment_proceeed)

    def click_on_set_reminder_from_home_holder_screen(self):
        """
        This method is used to send reminder to the khhata holder to pay pending amount
        """
        self.wait_for_element(self.btn_reminder)
        self.perform_click(self.btn_reminder)

    def click_tap_to_view_and_hide(self):
        self.wait_for_element(self.lbl_tap_to_view_and_hide)
        self.perform_click(self.lbl_tap_to_view_and_hide)

    def click_on_recent_entry(self):
        self.wait_for_element(self.lbl_entries)
        self.perform_click(self.lbl_entries)

    def perform_edit_entry(self, amount: str, edit_details: str):
        self.perform_click(self.btn_edit)
        self.wait_for_element(self.txt_enter_amount).clear()
        self.perform_sendkeys(self.txt_enter_amount, amount)
        self.wait_for_element(self.txt_description).clear()
        self.perform_sendkeys(self.txt_description, edit_details)
        self.perform_click(self.btn_proceed)

    def click_delete_entry(self):
        self.perform_click(self.btn_delete)

    def click_on_apply(self):
        self.wait_for_element(self.btn_apply)
        self.perform_click(self.btn_apply)

    def khaata_search(self, name_or_ph_no):
        """
        This function is used to search the khaata holder with phone number or name
        """
        self.wait_for_element(self.btn_search)
        self.perform_click(self.btn_search)
        self.wait_for_element(self.txt_search).clear()
        self.perform_sendkeys(self.txt_search, name_or_ph_no)

    def perform_you_give(self, amount, enter_details: str, date):
        """
         This methods is used to perform you give tnx in the khaata
        """
        time.sleep(2)
        self.wait_for_element(self.btn_you_give)
        self.perform_click(self.btn_you_give)
        self.wait_for_element(self.txt_enter_amount_given_or_received).clear()
        self.perform_sendkeys(self.txt_enter_amount_given_or_received, amount)
        self.wait_for_element(self.txt_enter_details_for_given_or_received_amount).clear()
        self.perform_sendkeys(self.txt_enter_details_for_given_or_received_amount, enter_details)
        self.perform_click(self.lbl_calender)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + date + ''))
        self.perform_click(self.btn_ok)
        self.perform_click(self.btn_save)

    def perform_you_got(self, amount: int, enter_details: str, give_today_date):
        """
         This methods is used to perform you got tnx in the khaata
        """
        time.sleep(2)
        self.wait_for_element(self.btn_you_got)
        self.perform_click(self.btn_you_got)
        self.wait_for_element(self.txt_enter_amount_given_or_received).clear()
        self.perform_sendkeys(self.txt_enter_amount_given_or_received, amount)
        self.wait_for_element(self.txt_enter_details_for_given_or_received_amount).clear()
        self.perform_sendkeys(self.txt_enter_details_for_given_or_received_amount, enter_details)
        self.perform_click(self.lbl_calender)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + give_today_date + ''))
        self.perform_click(self.btn_ok)
        self.perform_click(self.btn_save)

    def perform_edit_account(self, ph_no, name, label_name):
        """
        This method is used to edit the existing khaata holder account
        """
        self.perform_click(self.lbl_khaata_edit_account)
        self.wait_for_element(self.txt_khaata_holder_phNo_input).clear()
        self.perform_sendkeys(self.txt_khaata_holder_phNo_input, ph_no)
        self.wait_for_element(self.txt_khaata_holder_name_input).clear()
        self.perform_sendkeys(self.txt_khaata_holder_name_input, name)
        if label_name == 'Others':
            self.wait_for_element(self.lbl_other)
            self.perform_click(self.lbl_other)
        elif label_name == 'Supplier':
            self.wait_for_element(self.lbl_supplier)
            self.perform_click(self.lbl_supplier)
        elif label_name == 'Friend':
            self.wait_for_element(self.lbl_friends)
            self.perform_click(self.lbl_friends)
        elif label_name == 'Staff':
            self.wait_for_element(self.lbl_staff)
            self.perform_click(self.lbl_staff)
        else:
            self.wait_for_element(self.lbl_customer)
            self.perform_click(self.lbl_customer)

    def create_new_khaata_holder(self, ph_no, name, label_name: str):
        """
        This method is used to create the new khaata holder in khaata
        """
        self.perform_click(self.btn_new_khaata_holder)
        self.wait_for_element(self.txt_khaata_holder_phNo_input).clear()
        self.perform_sendkeys(self.txt_khaata_holder_phNo_input, ph_no)
        self.wait_for_element(self.txt_khaata_holder_name_input).clear()
        self.perform_sendkeys(self.txt_khaata_holder_name_input, name)
        if label_name == 'Others':
            self.wait_for_element(self.lbl_other)
            self.perform_click(self.lbl_other)
        elif label_name == 'Supplier':
            self.wait_for_element(self.lbl_supplier)
            self.perform_click(self.lbl_supplier)
        elif label_name == 'Friend':
            self.wait_for_element(self.lbl_friends)
            self.perform_click(self.lbl_friends)
        elif label_name == 'Staff':
            self.wait_for_element(self.lbl_staff)
            self.perform_click(self.lbl_staff)
        else:
            self.wait_for_element(self.lbl_customer)
            self.perform_click(self.lbl_customer)

    def perform_filter_by_balance(self, enter_filter: str):
        self.perform_click(self.btn_filter)
        if enter_filter == 'All':
            self.wait_for_element(self.lbl_by_balance_all)
            self.perform_click(self.lbl_by_balance_all)
        elif enter_filter == 'Advance':
            self.wait_for_element(self.lbl_by_balance_advance)
            self.perform_click(self.lbl_by_balance_advance)
        elif enter_filter == 'Due':
            self.wait_for_element(self.lbl_by_balance_due)
            self.perform_click(self.lbl_by_balance_due)

    def perform_filter_by_label(self, enter_label: str):
        self.perform_click(self.btn_filter)
        if enter_label == 'All':
            self.wait_for_element(self.lbl_by_label_all)
            self.perform_click(self.lbl_by_label_all)
        elif enter_label == 'Customer':
            self.wait_for_element(self.lbl_by_label_customer)
            self.perform_click(self.lbl_by_label_customer)
        elif enter_label == 'Staff':
            self.wait_for_element(self.lbl_by_label_staff)
            self.perform_click(self.lbl_by_label_staff)
        elif enter_label == 'Friend':
            self.wait_for_element(self.lbl_by_label_friends)
            self.perform_click(self.lbl_by_label_friends)
        elif enter_label == 'Other':
            self.wait_for_element(self.lbl_by_label_others)
            self.perform_click(self.lbl_by_label_others)
        elif enter_label == 'Supplier':
            self.wait_for_element(self.lbl_by_label_supplier)
            self.perform_click(self.lbl_by_label_supplier)

    def perform_filter_by_sorting(self, enter_sort: str):
        self.perform_click(self.btn_filter)
        if enter_sort == 'Most Recent':
            self.wait_for_element(self.lbl_sort_by_most_recent)
            self.perform_click(self.lbl_sort_by_most_recent)
        elif enter_sort == 'Oldest':
            self.wait_for_element(self.lbl_sort_by_oldest)
            self.perform_click(self.lbl_sort_by_oldest)
        elif enter_sort == 'Highest Amount':
            self.wait_for_element(self.lbl_sort_by_highest_amount)
            self.perform_click(self.lbl_sort_by_highest_amount)
        elif enter_sort == 'Name':
            self.wait_for_element(self.lbl_sort_by_name)
            self.perform_click(self.lbl_sort_by_name)

    def date_picker(self, date: str):
        lbl_date = (AppiumBy.ACCESSIBILITY_ID, f"//*[@text='{date}']")
        # perform_click((AppiumBy.ACCESSIBILITY_ID, '' + date + '')
        self.wait_for_element(lbl_date)
        self.perform_click(lbl_date)
        self.perform_click(self.btn_ok)

    def fetch_account_holder_name(self):
        return self.fetch_text(self.txt_entry_account_name)

    def fetch_account_holder_tag(self):
        return self.fetch_text(self.txt_entry_account_tag)

    def fetch_entry_message(self):
        return self.fetch_text(self.txt_entry_message)

    def fetch_entry_amount(self):
        return self.fetch_text(self.txt_entry_amount)

    def fetch_entry_description(self):
        return self.fetch_text(self.txt_entry_description)

    def fetch_date(self):
        return self.fetch_text(self.txt_date)

    def fetch_payment_mode(self):
        return self.fetch_text(self.txt_payment_mode)

    def fetch_user_inline_error_message(self):
        return self.fetch_text(self.txt_user_name_inline_error_message)

    def fetch_khaata_holder_name_from_account(self):
        return self.fetch_text(self.txt_khaata_holder_name)

    def fetch_khaata_holder_phone_number_from_account(self):
        return self.fetch_text(self.txt_khaata_holder_phNo)

    def fetch_khaata_holder_tag_from_account(self):
        return self.fetch_text(self.txt_khaata_holder_tag)

    def fetch_no_search_result_found(self):
        return self.fetch_text(self.txt_no_khaata_holder_found)

    def button_is_enabled(self):
        button = self.wait_for_element(self.btn_proceed)
        return button.is_enabled()

    def check_customer_selected_tick_mark(self):
        self.wait_for_element(self.img_tick_mark)

    def click_on_create_new_khaata_holder(self):
        self.wait_for_element(self.btn_new_khaata_holder)
        self.perform_click(self.btn_new_khaata_holder)

    def fetch_no_khaata_entries(self):
        self.wait_for_element(self.txt_no_khaata_enteries)
        return self.fetch_text(self.txt_no_khaata_enteries)

    def click_on_send_reminder(self):
        self.perform_click(self.btn_send_reminder)

    def validate_sent_reminder_button_is_clickable(self):
        self.wait_for_element_to_be_clickable(self.btn_send_reminder)

    def fetch_holder_mobile_no_from_reminder(self):
        return self.fetch_text(self.txt_reminder_holder_number)

    def fetch_holder_name_from_reminder(self):
        return self.fetch_text(self.txt_reminder_holder_name)

    def validate_khaata_holder_screen(self):
        return self.wait_for_element(self.txt_amount_status)

    def fetch_amount_from_holder_screen(self):
        return self.fetch_text(self.txt_amount_in_the_holder_screen)

    def click_on_entry_from_holder_screen(self):
        self.wait_for_element(self.lbl_recent_entry_from_holder_screen)
        self.perform_click(self.lbl_recent_entry_from_holder_screen)
