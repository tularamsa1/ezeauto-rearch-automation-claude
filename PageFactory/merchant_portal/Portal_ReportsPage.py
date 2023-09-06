from PageFactory.Portal_BasePage import BasePage
from Utilities.Generic_processor import extract_table_data


class TransHistoryPage(BasePage):
    txt_reports = '//p[text()="Reports"]'
    btn_txn = '//p[text()="Transactions"]'
    btn_daily = "//p[text()='Daily']"
    btn_weekly = "//p[text()='Weekly']"
    btn_monthly = "//p[text()='Monthly']"
    btn_logout = "//p[text()='Logout']"
    tbl_data = "//div[@class='txnReportsTable_loaderContainer__om+oI']/following-sibling::div[1]"
    btn_calender = "//div[@class='rs-picker-toggle rs-btn rs-btn-default rs-btn-lg']"
    btn_this_week = "//button[text()='This week']"
    btn_last_week = "//button[text()='Last week']"
    btn_past_2_weeks = "//button[text()='Past 2 weeks']"
    btn_this_month = "//button[text()='This month']"
    btn_last_30_days = "//button[text()='Last 30 days']"
    btn_last_month = "//button[text()='Last month']"
    btn_last_90_days = "//button[text()='Last 90 days']"
    btn_apply = "//button[text()='Apply']"
    btn_search = '//button[text()="Search"]'
    btn_clear = "//button[text()='Clear']"

    ddl_transaction_status = "//span[text()='Transaction Status']"
    btn_advance_filter = '//*[@id="advancedFilterContainer"]/div/div[2]/button'
    ddl_card_type = "//span[text()='Card Type']"
    ddl_card_brand = "//span[text()='CardBrand']"
    ddl_payment_mode = "//span[text()='Payment Mode']"
    ddl_select_an_option = "//span[text()='Select an Option']"
    txt_enter_option = '//input[@placeholder="Please choose an option"]'
    img_logo = '//div[@class="logo"]/img'
    ddl_all_locations = "//span[text()='All Locations']"
    ddl_user = "//span[text()='User']"
    # txt_location_search = "//input[@placeholder='Search']"
    lbl_dashboard = "//p[text()='Dashboard']"

    lbl_no_txn_message = "//p[text()='There are no transactions to display']"
    btn_next = "//div[child::img[@alt='next']]"
    btn_last_page = "//div[child::img[@alt='next']]/preceding-sibling::div[1]"

    lbl_select_search = "//div[@aria-haspopup='listbox']"
    lbl_username = "//span[contains(text(),'Username')]"
    lbl_search = "//img[@alt='search']/preceding-sibling::input"
    img_search = "//img[@alt='search']"
    lbl_order_number = "//span[contains(text(),'OrderNumber')]"

    def __init__(self, page):
        super().__init__(page)
        self.wait_till_dashboard_text_visible()

    def wait_till_dashboard_text_visible(self):
        """
        This method is used to wait until dashboard page is loaded
        """
        self.wait_for_element(self.lbl_dashboard)

    def click_on_reports(self):
        self.perform_click(self.txt_reports)

    def click_on_transactions(self):
        self.perform_click(self.btn_txn)

    def click_on_daily(self):
        self.perform_click(self.btn_daily)

    def click_on_weekly(self):
        self.perform_click(self.btn_weekly)

    def click_on_monthly(self):
        self.perform_click(self.btn_monthly)

    def click_on_calender(self):
        self.perform_click(self.btn_calender)

    def click_on_apply(self):
        self.perform_click(self.btn_apply)

    def perform_logout(self):
        """
        This method is used to perform logout
        """
        self.page.on("dialog", lambda dialog: dialog.accept())
        self.perform_click(self.btn_logout)

    def select_txn_period_this_week(self):
        """
        This method is used to select transaction period for this week
        """
        self.click_on_calender()
        self.perform_click(self.btn_this_week)
        self.click_on_apply()

    def select_txn_period_last_week(self):
        """
        This method is used to select transaction period for last week
        """
        self.click_on_calender()
        self.perform_click(self.btn_last_week)
        self.click_on_apply()

    def select_txn_period_past_2_weeks(self):
        """
        This method is used to select transaction period for past 2 weeks
        """
        self.click_on_calender()
        self.perform_click(self.btn_past_2_weeks)
        self.click_on_apply()

    def select_txn_period_this_month(self):
        """
        This method is used to select transaction period for this month
        """
        self.click_on_calender()
        self.perform_click(self.btn_this_month)
        self.click_on_apply()

    def select_txn_period_last_30_days(self):
        """
        This method is used to select transaction period for last 30 days
        """
        self.click_on_calender()
        self.perform_click(self.btn_last_30_days)
        self.click_on_apply()

    def select_txn_period_last_month(self):
        """
        This method is used to select transaction period for last month
        """
        self.click_on_calender()
        self.perform_click(self.btn_last_month)
        self.click_on_apply()

    def select_txn_period_last_90_days(self):
        """
        This method is used to select transaction period for last 90 days
        """
        self.click_on_calender()
        self.perform_click(self.btn_last_90_days)
        self.click_on_apply()

    def search_based_on_username(self, username: str):
        """
        This method is used to perform search based on username
        """
        self.click_on_search_box()
        self.select_username()
        self.enter_search_value(username)
        self.perform_search()

    def search_based_on_order_number(self, order_number: str):
        """
        This method is used to perform search based on order number
        """
        self.click_on_search_box()
        self.select_order_number()
        self.enter_search_value(order_number)
        self.perform_search()

    def get_attribute_element(self):
        """
        This method is used to get the class name of element
        """
        class_name = self.page.get_attribute(self.btn_next, "class")
        return class_name

    def get_transaction_details_first_last_page(self):
        """
        This method is used to fetch the transaction data on the first page and the last page
        """
        txn_details_first_page = self.get_transaction_details()
        if self.page.is_visible(self.lbl_no_txn_message):
            return None
        else:
            class_name = self.get_attribute_element()
            while class_name != "reportsPagination_disabled__Lte8v":
                self.perform_click(self.btn_last_page)
                self.wait_for_given_timeout(2000)
                class_name = self.get_attribute_element()
                if class_name != "reportsPagination_disabled__Lte8v":
                    self.perform_click(self.btn_next)
            else:
                txn_details_last_page = self.get_transaction_details()
            txn_details_final = txn_details_first_page + txn_details_last_page
            return txn_details_final

    def get_transaction_details(self):
        """
        This method is used to fetch the transaction data on the first page and the last page
        """
        self.wait_for_given_timeout(2000)
        table_element = self.get_tables_data()
        table_html = table_element.inner_html()
        transaction_details = extract_table_data(table_html)
        return transaction_details

    def click_on_search_btn(self):
        self.perform_click(self.btn_search)

    def click_on_clear_btn(self):
        self.perform_click(self.btn_clear)

    def click_on_advance_filter(self):
        """
        This method is used to click on Advance Filter button
        """
        self.perform_click(self.btn_advance_filter)

    def search_based_on_card_type(self, option: str):
        """
        This method is used to select the card type to be searched
        """
        self.perform_click(self.ddl_card_type)
        lbl_card_type_option = f"//label[text()='{option}']"
        self.perform_click(lbl_card_type_option)
        self.click_on_razorpay_logo()

    def search_based_on_card_brand(self, option: str):
        """
        This method is used to select the card brand to be searched
        """
        self.perform_click(self.ddl_card_brand)
        lbl_card_brand_option = f"//label[text()='{option}']"
        self.perform_click(lbl_card_brand_option)
        self.click_on_razorpay_logo()

    def search_based_on_payment_mode(self, option: str):
        """
        This method is used to select the payment mode to be searched
        """
        self.perform_click(self.ddl_payment_mode)
        lbl_payment_mode_option = f"//label[text()='{option}']"
        self.perform_click(lbl_payment_mode_option)
        self.click_on_razorpay_logo()

    def search_based_on_location(self, location: str):
        """
        This method is used to select the location to be searched
        """
        self.perform_click(self.ddl_all_locations)
        self.page.query_selector('//input[@placeholder="Search"]').fill(location)
        lbl_location = f"//span[text()='{location}']"
        self.perform_click(lbl_location)
        self.click_on_razorpay_logo()

    def search_based_on_user(self, user: str):
        """
        This method is used to select the user to be searched
        """
        self.perform_click(self.ddl_user)
        lbl_user = f"//label[text()='{user}']"
        self.perform_click(lbl_user)
        self.click_on_razorpay_logo()

    def search_based_on_transaction_status(self, option: str):
        """
        This method is used to select the transaction status to be searched
        """
        self.perform_click(self.ddl_transaction_status)
        lbl_transaction_status_options = f"//label[text()='{option}']"
        self.perform_click(lbl_transaction_status_options)

    def select_option(self, option: str, value: str):
        """
        This method is used to select the option to be searched such as Order Number, Device, Auth code etc.
        """
        self.perform_click(self.ddl_select_an_option)
        lbl_option = f"//span[text()='{option}']"
        self.perform_click(lbl_option)
        self.click_on_razorpay_logo()
        txt_placeholder = f"Enter the {option}"
        self.page.get_by_placeholder(txt_placeholder).fill(value)

    def get_tables_data(self):
        return self.search_element(self.tbl_data)

    def click_on_razorpay_logo(self):
        self.perform_click(self.img_logo)

    def click_on_search_box(self):
        self.perform_click(self.lbl_select_search)

    def select_username(self):
        self.perform_click(self.lbl_username)

    def select_order_number(self):
        self.perform_click(self.lbl_order_number)

    def click_on_search(self):
        self.perform_click(self.lbl_search)

    def enter_search_value(self, value):
        self.perform_clear(self.lbl_search)
        self.perform_fill(self.lbl_search, value)

    def perform_search(self):
        self.perform_click(self.img_search)

    def perform_clear(self, lbl_search):
        self.page.wait_for_selector(selector=lbl_search, timeout=45000, state="visible").fill("")