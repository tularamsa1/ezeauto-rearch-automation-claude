import time
from Configuration import TestSuiteSetup
from DataProvider import GlobalVariables
from datetime import datetime, timedelta
from PageFactory.merchant_portal.Portal_BasePage import BasePage
from PageFactory.merchant_portal.Portal_LoginPage import PortalLoginPage
from Utilities.Generic_processor import extract_table_data


class PortalTransHistoryPage(BasePage):
    # txt_reports = "//p[contains(text(),'Reports')]"
    # btn_txn = '//p[text()="Transactions"]'
    # lbl_select_search = "//span[contains(text(),'Search')]"
    # lbl_oder_number = "//span[contains(text(),'OrderNumber')]"
    # lbl_search = "//body/div[@id='root']//div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/input[1]"
    # btn_search = "//body/div[@id='root']//div[1]/div[3]/div[2]//div[1]/img[1]"
    # tbl_data = "//div[@class='txnReportsTable_loaderContainer__om+oI']/following-sibling::div[1]"
    lbl_date_picker = "//div[@icon='[object Object]']//span[1]"
    lbl_current_date = "(//div[@class='rs-calendar-table'])[1]"
    lbl_submit = "//button[text()='Apply']"
    lbl_month = "//body/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]//div[1]/button[2]"
    lbl_next_month = "//body/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]//div[1]/button[2]"
    lbl_select_search = "//div[@aria-haspopup='listbox']"
    lbl_username = "//span[contains(text(),'Username')]"
    lbl_search = "//img[@alt='search']/preceding-sibling::input"
    img_search = "//img[@alt='search']"
    lbl_order_number = "//span[contains(text(),'OrderNumber')]"
    txt_reports = '//p[text()="Reports"]'
    btn_txn = '//p[text()="Transactions"]'
    tbl_data = "//div[@class='txnReportsTable_loaderContainer__om+oI']/following-sibling::div[1]"
    btn_search = '//button[text()="Search"]'

    def __init__(self, page):
        super().__init__(page)

    def click_on_reports(self):
        self.perform_click(self.txt_reports)

    def click_on_txn(self):
        self.perform_click(self.btn_txn)

    def click_on_search_box(self):
        self.perform_click(self.lbl_select_search)

    def select_order_number(self):
        self.perform_click(self.lbl_order_number)

    def click_on_search(self):
        self.perform_click(self.lbl_search)

    def enter_order_number(self, order_number):
        self.perform_clear(self.lbl_search)
        self.perform_fill(self.lbl_search, order_number)

    def perform_search(self):
        self.perform_click(self.btn_search)

    def date_picket_expand(self):
        self.perform_click(self.lbl_date_picker)

    def apply_selected_submit(self):
        self.perform_click(self.lbl_submit)

    def get_tables_data(self):
        return self.search_element(self.tbl_data)

    def wait_for_time_in_milli(self, time_in_milli):
        self.wait_for_given_timeout(time_in_milli)

    def getting_month_from_datepiker(self):
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        today_formatted = today.strftime(
            "%B %d %Y")  # Replace the format string according to your date picker's expected format
        print(f"todays: {today_formatted}")
        yesterday_formatted = yesterday.strftime(
            "%B %d %Y")  # Replace the format string according to your date picker's expected format

        # " " + today_formatted + " (Today)", " " + yesterday_formatted

        current_month = datetime.now().strftime("%B %Y")
        print(str(current_month))
        month = self.fetch_text(self.lbl_month)
        next_month = self.fetch_text(self.lbl_next_month)
        if month == current_month:
            self.perform_click("//div[@title='" + " " + yesterday_formatted + "']")
            self.date_selector(yesterday_formatted, self.lbl_current_date)
            time.sleep(1)
            self.perform_click("//div[@title='" + " " + today_formatted + " (Today)" + "']")
            self.date_selector(today_formatted, self.lbl_current_date)
            time.sleep(1)

        else:
            self.perform_click()
            self.date_selector(today)
            time.sleep(1)
            self.perform_click()
            self.date_selector()

    def perform_clear(self, lbl_search):
        self.page.wait_for_selector(selector=lbl_search, timeout=45000, state="visible").fill("")


def get_transaction_details_for_portal(app_un: str = None, app_pw: str = None, order_id: str = None) -> list:
    """
    This method initiates the browser to get the txn details from merchant portal.
    Once it is logged in then it gets the txn details from extract_table_data() and returns list.

    :param app_un: str
    :param app_pw: str
    :param order_id: order_id
    :return: list
    """
    GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
    login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
    login_page_portal.perform_login_to_portal(username=app_un, password=app_pw)
    GlobalVariables.portal_txn_page = PortalTransHistoryPage(GlobalVariables.portal_page)
    GlobalVariables.portal_txn_page.click_on_reports()
    GlobalVariables.portal_txn_page.click_on_txn()
    # portal_txn_page.date_picket_expand()
    # portal_txn_page.getting_month_from_datepiker()
    # portal_txn_page.apply_selected_submit()
    GlobalVariables.portal_txn_page.click_on_search_box()
    GlobalVariables.portal_txn_page.select_order_number()
    GlobalVariables.portal_txn_page.click_on_search()
    GlobalVariables.portal_txn_page.select_order_number()
    GlobalVariables.portal_txn_page.enter_order_number(order_id)
    GlobalVariables.portal_txn_page.perform_search()
    GlobalVariables.portal_txn_page.wait_for_given_timeout(2000)
    table_element = GlobalVariables.portal_txn_page.get_tables_data()
    table_html = table_element.inner_html()
    transaction_details = extract_table_data(table_html)
    return transaction_details


def get_txn_details_for_diff_order_id(order_id: str = None) -> list:
    """
    This method will use the existing browser to get the txn details from merchant portal for different order Id.
    Once it is logged in then it gets the txn details from extract_table_data() and returns list.

    :param order_id: order_id
    :return: list
    """
    GlobalVariables.portal_txn_page.enter_order_number(order_id)
    GlobalVariables.portal_txn_page.perform_search()
    GlobalVariables.portal_txn_page.wait_for_given_timeout(2000)
    table_element = GlobalVariables.portal_txn_page.get_tables_data()
    table_html = table_element.inner_html()
    transaction_details = extract_table_data(table_html)
    return transaction_details
