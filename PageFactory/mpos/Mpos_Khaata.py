import base64
from time import sleep

from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage
# from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By
from PIL import Image
import pytesseract
import io
import time


class Khaata(BasePage):
    btn_mykhaata = (AppiumBy.XPATH, '(//android.widget.ImageView[@content-desc="Feature logo"])[1]')
    btn_khaata_holders = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvKhaataHolders')
    btn_khaata_enteries = (AppiumBy.ID, 'com.ezetap.basicapp:id/tabKhaataEntries')
    txt_search = (AppiumBy.ID, 'com.ezetap.basicapp:id/searchAutoCompleteTextView')
    btn_search = (AppiumBy.ID, 'com.ezetap.basicapp:id/cvSearch')
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

    lbl_for_khaata = (AppiumBy.XPATH, '//*[@text="My Khaata"]')
    lbl_no_customer_created = (AppiumBy.XPATH, '//*[@text="No khaata holders created"]')
    lbl_no_customer_created_2 = (AppiumBy.XPATH, '//*[@text="Add your first khaata holder, then add a new entry"]')
    txt_customer_name = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTitle')
    txt_mobile_number = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvCustomerPhone')
    btn_back = (AppiumBy.ID, 'com.ezetap.basicapp:id/imgToolbarBack')
    btn_get_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvYouGaveAmount')
    txt_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTopYouGaveAmount')
    toast_locator = (By.XPATH, '//*[contains(@text, "New Khaata successfully created!")]')
    btn_recent_transaction = (AppiumBy.XPATH, '(//*[@resource-id="com.ezetap.basicapp:id/clRoot"])')
    btn_delete_2 = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnProceed')
    btn_date = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvDate')
    lbl_customer_name_from_entries = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvName')
    lbl_tag_from_entries = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTag')
    btn_previous_month = (AppiumBy.ID, 'android: id / prev')
    txt_label = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvCustomerTag')
    txt_edited_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvYouGaveAmount')
    txt_edited_description = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvDescription')
    # txt_edited_date = (AppiumBy.XPATH, '//*[@resource-id="com.ezetap.basicapp:id/tvName"]')
    txt_edited_date = (AppiumBy.XPATH, '//*[@resource-id ="com.ezetap.basicapp:id/tvDate"]')
    # txt_edited_date = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvName')
    # lbl_customer_details = (By.XPATH, '//*[@resource-id ="com.ezetap.basicapp:id/textView2"]')
    # lbl_customer_details = (AppiumBy.XPATH, '(//*[@class = "android.view.ViewGroup"])[2]')
    lbl_unique_mobile_number = (AppiumBy.ID, 'com.ezetap.basicapp:id/textView2')
    btn_cancel_create_customer = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnCancel')


    def __init__(self, driver):
        super().__init__(driver)

    def click_my_khaata(self):
        """
        This method is used to click on the my khaata tab in the main screen
        """
        self.wait_for_element(self.btn_mykhaata)
        self.perform_click(self.btn_mykhaata)

    def check_lbl_for_khaata(self):
        """
        This method is used to check "my khaata" as label after clicking on My khaata from home screen
        """
        self.wait_for_element(self.lbl_for_khaata)
        khaata_label = self.fetch_text(self.lbl_for_khaata)
        return khaata_label

    def check_khaata_no_customer_created(self):
        """
         it's check messages present on khaata home screen if there is no khaata customer created
         """
        self.wait_for_element(self.lbl_no_customer_created)
        khaata_no_customer_created_label = self.fetch_text(self.lbl_no_customer_created)
        self.wait_for_element(self.lbl_no_customer_created_2)
        khaata_no_customer_created_sub_label = self.fetch_text(self.lbl_no_customer_created_2)
        return khaata_no_customer_created_label, khaata_no_customer_created_sub_label



    def toast_locator_text(self, x1, y1, x2, y2):
        screenshot = self.screenshot()
        cropped_image = Image.open(io.BytesIO(screenshot)).crop((x1, y1, x2, y2))
        original_text = pytesseract.image_to_string(cropped_image)
        splitted_text = original_text.split()
        splitted_text.pop(0)
        extracted_text = ' '.join(splitted_text)
        return extracted_text

    def fetch_customer_name(self):
        self.wait_for_element(self.txt_customer_name)
        customer_name = self.fetch_text(self.txt_customer_name)
        return str(customer_name)

    def fetch_mobile_number(self):
        self.wait_for_element(self.txt_mobile_number)
        mobile_no = self.fetch_text(self.txt_mobile_number)
        return str(mobile_no)

    def fetch_label(self):
        self.wait_for_element(self.txt_label)
        return self.fetch_text(self.txt_label)

    def click_on_back_button(self):
        """
        This method click on back button after doing a khaata transaction
        """
        self.wait_for_element(self.btn_back)
        self.wait_for_element_to_be_clickable(self.btn_back)
        self.perform_click(self.btn_back)

    def fetch_amount_from_entries(self):
        """
        This methhod click on particular khaata txn from khaata entries present on khaata home page and fetches amount from that.
        """
        self.wait_for_element(self.btn_get_amount)
        self.perform_clickIndex(self.btn_get_amount, 0)
        amount = self.fetch_text(self.txt_amount)
        return amount

    def fetch_customer_name_and_label_from_entries(self):

        customer_name = self.fetch_text(self.lbl_customer_name_from_entries)
        customer_label = self.fetch_text(self.lbl_tag_from_entries)
        return customer_name, customer_label

    def fetch_top_entry_from_khaata_entries(self):
        self.wait_for_element(self.btn_get_amount)
        self.perform_clickIndex(self.btn_get_amount, 0)

    def click_on_recent_transaction(self):
        self.wait_for_element(self.btn_recent_transaction)
        self.wait_for_element_to_be_clickable(self.btn_recent_transaction)
        self.perform_click(self.btn_recent_transaction)

    def click_save_for_edited_transaction(self):
        self.wait_for_element(self.btn_save)
        self.wait_for_element_to_be_clickable(self.btn_save)
        self.perform_click(self.btn_save)

    def fetch_edited_amount(self):
        self.wait_for_element(self.txt_edited_amount)
        return self.fetch_text(self.txt_edited_amount)

    def fetch_edited_description(self):
        self.wait_for_element(self.txt_edited_description)
        return self.fetch_text(self.txt_edited_description)

    def fetch_edited_date(self):
        edited_date_without_comma = self.fetch_text(self.txt_edited_date).replace(",", "")
        return edited_date_without_comma

    def fetch_count_of_holders(self):
        self.wait_for_element(self.lbl_unique_mobile_number)
        return self.fetch_elements(self.lbl_unique_mobile_number)

    def click_cancel_from_create_customer(self):
        """
        This methos click on Cancel button present on  "Add new khaata holder" pop up
        """
        self.perform_click(self.btn_cancel_create_customer)

    def click_khaata_holders(self):
        self.perform_click(self.btn_khaata_holders)

    def click_khaata_entries(self):
        """
        This method clicks on khaata entries present on khaata home page
        """
        self.wait_for_element(self.btn_khaata_enteries)
        self.wait_for_element_to_be_clickable(self.btn_khaata_enteries)
        self.perform_click(self.btn_khaata_enteries)

    def click_first_khaata_holder_search_result(self):
        """
        This method is used to click on the first khaata holder based on the result
        """
        self.perform_click(self.txt_first_search_result)

    def click_proceed_button(self):
        """
            This method clicks on proceed button on create new customer screen
         """
        self.perform_click(self.btn_proceed)



    def click_cancel_button(self):
        self.perform_click(self.btn_cancel)

    def click_menu(self):
        self.perform_click(self.mnu_khaata_holder)

    def click_remove_khaata_holder(self):
        self.perform_click(self.lbl_khaata_remove_khaata_holder)

    def click_clear_khaata_entries(self):
        """
        This function is used to clear all the entries in the khaata
        """
        self.perform_click(self.lbl_clear_khaata_entries)

    def perform_collect_payment(self, enter_amount: str):
        self.perform_click(self.btn_collect_pay)
        self.wait_for_element(self.txt_enter_amount).clear()
        self.perform_sendkeys(self.txt_enter_amount, enter_amount)

    def perform_set_reminder(self):
        """
        This method is used to send reminder to the khhata holder to pay pending amount
        """
        self.perform_click(self.btn_reminder)
        self.perform_click(self.btn_send_reminder)

    def click_tap_to_view_and_hide(self):
        self.wait_for_element(self.lbl_tap_to_view_and_hide)
        self.perform_click(self.lbl_tap_to_view_and_hide)

    def click_on_recent_entry(self):
        self.wait_for_element(self.lbl_entries)
        self.perform_click(self.lbl_entries)

    def perform_edit_entry_amount_txn(self, amount):
        self.wait_for_element(self.btn_edit)
        self.perform_click(self.btn_edit)
        self.wait_for_element(self.txt_enter_amount).clear()
        self.perform_sendkeys(self.txt_enter_amount, amount)

    def perform_edit_entry_description(self, edit_details: str):
        self.perform_click(self.btn_edit)
        self.wait_for_element(self.txt_description).clear()
        self.perform_sendkeys(self.txt_description, edit_details)

    def click_on_edit(self):
        self.perform_click(self.btn_edit)

    def click_on_date(self):
        self.perform_click(self.btn_date)


    def click_delete_entry(self):
        self.perform_click(self.btn_delete)
        self.perform_click(self.btn_delete_2)

    def click_on_apply(self):
        self.wait_for_element(self.btn_apply)
        self.perform_click(self.btn_apply)

    def khaata_search(self, name_or_ph_no: str):
        """
        This function is used to search the khaata holder with phone number or name
        """
        self.wait_for_element(self.btn_search)
        self.perform_click(self.btn_search)
        self.wait_for_element(self.txt_search).clear()
        self.perform_sendkeys(self.txt_search, name_or_ph_no)

    def perform_you_give(self, amount: str, enter_details: str):
        """
        This method will perform a you give transaction for existing khaata customer
        """
        time.sleep(6)
        self.wait_for_element(self.btn_you_give)
        self.perform_click(self.btn_you_give)
        self.wait_for_element(self.txt_enter_amount_given_or_received).clear()
        self.perform_sendkeys(self.txt_enter_amount_given_or_received, amount)
        self.wait_for_element(self.txt_enter_details_for_given_or_received_amount).clear()
        self.perform_sendkeys(self.txt_enter_details_for_given_or_received_amount, enter_details)
        self.perform_click(self.btn_save)

    def perform_you_got(self, amount: str, enter_details: str):
        self.wait_for_element(self.btn_you_got)
        self.perform_click(self.btn_you_got)
        self.wait_for_element(self.txt_enter_amount_given_or_received).clear()
        self.perform_sendkeys(self.txt_enter_amount_given_or_received, amount)
        self.wait_for_element(self.txt_enter_details_for_given_or_received_amount).clear()
        self.perform_sendkeys(self.txt_enter_details_for_given_or_received_amount, enter_details)
        self.perform_click(self.lbl_calender)
        # self.perform_click(self.btn_ok)
        # self.perform_click(self.btn_save)

    def perform_edit_account(self, ph_no: int, name: str, label_name: str):
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

    def create_new_khaata_holder(self, ph_no: int, name: str, label_name: str):
        """
        This method is used to create the new khaata customer
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
        lbl_date = (AppiumBy.ACCESSIBILITY_ID, '' + date + '')
        self.perform_click(lbl_date)
        self.perform_click(self.btn_ok)

    def date_picker_for_1st_of_every_month(self, date: str):
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, 'Previous month'))
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + date + ''))
        self.perform_click(self.btn_ok)


