from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage


class HelpSupport(BasePage):
    btn_help_support = (AppiumBy.ID, 'com.ezetap.basicapp:id/nav_help')
    mnu_bar_home_page = (AppiumBy.ACCESSIBILITY_ID, 'Open navigation drawer')
    btn_request_callback = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvRequestCallback')
    btn_request_callback_2 = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnCallBack')
    btn_request_callback_3 = (AppiumBy.XPATH, '//*[@text="Request Callback"]')
    btn_register_a_complaint = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvRegisterComplaint')
    txt_emailid = (AppiumBy.ID, 'com.ezetap.basicapp:id/etEmailId')
    txt_mob_number_complaint_register =  (AppiumBy.ID, 'com.ezetap.basicapp:id/etMobileNumber')
    txt_description = (AppiumBy.ID, 'com.ezetap.basicapp:id/etComments')
    btn_submit = (AppiumBy.XPATH, '//*[@text="Submit"]')
    btn_see_all_complaint = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnSeeAllComplaints')
    btn_whatsapp_support = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvClickHere')
    txt_mobile_number = (AppiumBy.ID, 'com.ezetap.basicapp:id/etNewPhoneNumber')
    txt_callback_request_successful_message_1 =  (AppiumBy.XPATH, '//*[@text="Callback request successful"]')
    txt_callback_request_successful_message_2 = (AppiumBy.XPATH, '//*[@text="We will call you within 30 mins"]')
    txt_complaint_register_successful_message_1 = (AppiumBy.XPATH, '//*[@text="Complaint Successful"]')
    txt_complaint_register_successful_message_2 = (AppiumBy.ID, 'com.ezetap.basicapp:id/description')
    btn_help_support_navbar = (AppiumBy.ID, 'com.ezetap.basicapp:id/nav_help')
    btn_menu_help_support = (AppiumBy.ID, 'com.ezetap.basicapp:id/nav_help_support')
    txt_email_id = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvRegisterComplaint')
    txt_help_and_support = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTitle')
    btn_help_from_top_of_home_screen = (AppiumBy.ID, 'com.ezetap.basicapp:id/rlHelp')

    def __init__(self, driver):
        super().__init__(driver)

    def click_help_support_from_nav_bar(self):
        self.perform_click(self.btn_help_support)

    def click_help_menu(self):
        self.perform_click(self.mnu_bar_home_page)

    def click_request_callback(self, mobile_number):
        self.wait_for_element(self.btn_request_callback)
        self.perform_click(self.btn_request_callback)
        self.wait_for_element(self.btn_request_callback_2)
        self.perform_click(self.btn_request_callback_2)
        self.wait_for_element(self.txt_mobile_number).clear()
        self.perform_sendkeys(self.txt_mobile_number, mobile_number)
        self.perform_click(self.btn_request_callback_3)

    def is_request_callback_successful(self):
        label_1 = self.fetch_text(self.txt_callback_request_successful_message_1)
        label_2 = self.fetch_text(self.txt_callback_request_successful_message_2)
        return label_1, label_2

    def click_register_a_complaint(self, email, mobile_num, random_description):
        self.scroll_to_text('Register a Complaint')
        self.perform_click(self.btn_register_a_complaint)
        self.wait_for_element(self.txt_mob_number_complaint_register).clear()
        self.perform_sendkeys(self.txt_mob_number_complaint_register, mobile_num)
        self.perform_sendkeys(self.txt_emailid, email)
        self.perform_sendkeys(self.txt_description, random_description)
        self.perform_click(self.btn_submit)

    def is_register_complaint_successful(self):
        return self.fetch_text(self.txt_complaint_register_successful_message_1)

    def click_help_navbar(self):
        self.perform_click(self.btn_help_support_navbar)

    def click_help_menu(self):
        self.perform_click(self.mnu_bar_home_page)
        self.perform_click(self.btn_menu_help_support)

    def fetch_text_help_and_support(self):
        self.wait_for_element(self.txt_help_and_support)
        return self.fetch_text(self.txt_help_and_support)

    def click_on_help_from_top_of_home_screen(self):
        self.wait_for_element(self.btn_help_from_top_of_home_screen)
        self.perform_click(self.btn_help_from_top_of_home_screen)
