import time

from PageFactory.Portal_BasePage import BasePage


class PortalDashboardPage(BasePage):
    lbl_dashboard = "//p[text()='Dashboard']"
    lbl_total_sales = "//p[text()='Total Sales']/..//p[contains(@class,'totalXFlexContainer_valueFormat')]"
    lbl_total_txns = "//p[text()='Total Transactions']/..//p[contains(@class,'totalXFlexContainer_valueFormat')]"
    lbl_merchant_name = "//p[contains(@class,'merchantDetails_merchantName')]"
    lbl_merchant_details = "//div[contains(@class, 'merchantDetails_merchantDetailsContainer')]"
    txt_merchant_number = "//div[contains(@class,'merchantPopUp_merchantPopupDetails')]/following-sibling::div//div"
    lbl_calendar = "//span[@class='rs-picker-toggle-value']"
    lbl_all_locations = "//span[text()='All Locations']"
    input_location_search_box = "//input[@placeholder='Search']"
    chk_location_checkbox = "//span[text()='{}']/..//span[@class='rs-checkbox-wrapper']"
    lbl_logo = "//div[@class='logo']"
    btn_period_type = "//button[text()='{}']"
    btn_apply = "//button[text()='Apply']"
    lbl_txn_by_details = "//p[text()='{}']/parent::div/parent::div"
    lbl_rgb_color_by_type = "//p[text()='{}']/..//div[contains(@class,'transactionType_box')]"
    blb_sales_overview_date_range = "//p[contains(@class,'salesOverview_dateRange')]"
    lbl_sales_overview_description = "(//div[contains(@class,'salesOverview_description')]/child::p)[1]"
    lbl_sales_overview_description1 = "(//div[contains(@class,'salesOverview_description')]/child::p)[2]"
    lbl_sales_overview_description2 = "(//div[contains(@class,'salesOverview_description')]/child::p)[3]"
    lbl_sales_overview_indicator = "//div[contains(@class,'salesOverview_indicators')]"
    txt_country_head = "(//span[contains(@class,'entityFlexContainer')])[{}]"
    lbl_chart = "//div[contains(@class,'tooltipContainer_box__Bya3-')]"
    lbl_device_usage = "//p[contains(@class,'deviceUsageChart')]"
    lst_view_by = "//div[contains(@class,'ezeDropdown_dropdownContainer')]"
    rdo_text = "//p[text()='{}']"
    lbl_performance_matrix_calendar = "(//span[@class='rs-picker-toggle-value'])[2]"
    lbl_txns_by_type_daterange = "//p[contains(@class,'transactionByType_dateRange')]"
    lbl_select_arrow_location = "//div[@title='{}']/..//div[@role='button']"
    lbl_select_location = "//span[text()='{}']"
    lbl_profile = "//div[@class='profileImage']//img[@alt='logo']"
    lbl_user_profile_values = "//div[contains(@class, 'userProfileInfo_userData')]"
    btn_logout = "//p[text()='Logout']"
    lbl_login_to_dashboard = "//p[text()='Login to Dashboard']"

    this_week = "This week"
    last_week = "Last week"
    past_2_weeks = "Past 2 weeks"
    this_month = "This month"
    last_30_days = "Last 30 days"
    last_month = "Last month"
    last_90_days = "Last 90 days"

    def __init__(self, page):
        super().__init__(page)
        self.wait_till_dashboard_text_visible()

    def wait_till_dashboard_text_visible(self):  # change to clickable
        """ This method will waits for dashboard text to be visible in merchant portal dashboard page """
        self.wait_for_element(self.lbl_dashboard)

    def click_on_dashboard(self):
        """ Clicks on dashboard element """
        self.perform_click(self.lbl_dashboard)

    def fetch_total_sales(self):
        """ Fetching total sales of the merchant and returns total sales """
        for i in range(30):
            total_sale = self.fetch_text(self.lbl_total_sales)
            ele = "".join([i for i in total_sale.split()[1] if i.isalnum()])
            if int(ele) > 0:
                return total_sale
            else:
                self.wait_for_given_timeout(1000)
                continue
        return False

    def fetch_total_number_of_txns(self):
        """ Fetching total number of txns of the merchant and returns total no. of txns """
        for i in range(30):
            total_txns = self.fetch_text(self.lbl_total_txns).replace(",", "")
            if int(total_txns) > 0:
                return total_txns
            else:
                self.wait_for_given_timeout(1000)
                continue
        return False

    def click_merchant_name(self):
        """ Clicks on merchant name """
        self.perform_click(self.lbl_merchant_name)

    def fetch_merchant_details(self):
        """ Fetching merchant details and returns merchant details """
        return self.fetch_text(self.lbl_merchant_details)

    def fetch_merchant_number(self):
        """ Fetching merchant number and returns merchant number """
        return self.fetch_text(self.txt_merchant_number)

    def click_calendar(self):
        """ Clicks on calender """
        self.perform_click(self.lbl_calendar)

    def select_period_type(self, period_type: str):
        """ Selecting the specified time period """
        self.perform_click(self.btn_period_type.format(period_type))

    def click_apply_btn(self):
        """" Clicks on apply button """
        self.perform_click(self.btn_apply)

    def select_txn_period_for_this_week(self):
        """ Selecting this week time period and applying filter. """
        self.select_period_type(self.this_week)
        self.click_apply_btn()

    def select_txn_period_for_last_week(self):
        """ Selecting last week time period and applying filter """
        self.select_period_type(self.last_week)
        self.click_apply_btn()

    def select_txn_period_of_past_two_weeks(self):
        """ Selecting past 2 weeks time period and applying filter. """
        self.select_period_type(self.past_2_weeks)
        self.click_apply_btn()

    def select_txn_period_for_this_month(self):
        """ Selecting this month time period and applying filter. """
        self.select_period_type(self.this_month)
        self.click_apply_btn()

    def select_txn_period_for_last_30_days(self):
        """ Selecting last 30 days time period and applying filter. """
        self.select_period_type(self.last_30_days)
        self.click_apply_btn()

    def select_txn_period_for_last_month(self):
        """ selecting last month time period and applying filter. """
        self.select_period_type(self.last_month)
        self.click_apply_btn()

    def select_txn_period_for_last_90_days(self):
        """ selecting last 90 days time period and applying filter. """
        self.select_period_type(self.last_90_days)
        self.click_apply_btn()

    def select_location_by_search_box(self, location: str):
        """
        This method will selects the location by passing the location into the search box and filters dashboard
        page based on location.
        """
        self.perform_click(self.lbl_all_locations)
        self.perform_fill(self.input_location_search_box, location.title())
        self.perform_click(self.chk_location_checkbox.format(location.title()))
        self.perform_click(self.lbl_logo)

    def select_location_by_values(self, locations: list):
        """
        This method will selects the location by navigation through the dropdown values and filters dashboard page
        based on location.
        """
        self.perform_click(self.lbl_all_locations)
        for location in locations:
            if self.page.is_visible(self.lbl_select_arrow_location.format(location.title())):
                self.perform_click(self.lbl_select_arrow_location.format(location.title()))
            else:
                self.perform_click(self.lbl_select_location.format(locations[-1].title()))
                self.perform_click(self.lbl_logo)

    def fetch_txn_details_by_type(self, by_type: str):
        """ This method will fetch and return the txn details based on specified by_type """
        if self.page.is_visible(self.lbl_txn_by_details.format(by_type.title())):
            txn_details_by_type = self.fetch_text(self.lbl_txn_by_details.format(by_type.title()))
        else:
            txn_details_by_type = self.fetch_text(self.lbl_txn_by_details.format(by_type.upper()))
        return txn_details_by_type

    def fetch_sales_overview_date_range(self):
        """ Fetching the sales overview date range and returns the date range """
        return self.fetch_text(self.blb_sales_overview_date_range)

    def fetch_previous_sales_dates_and_amount(self):
        """ Fetching the previous sales and returning the previous sales """
        for i in range(5):
            previous_total_sale = self.fetch_text(self.lbl_sales_overview_description)
            sale = "".join([i for i in previous_total_sale.split("-")[-1].split()[1] if i.replace(",", "")])
            if float(sale.split()[-1]) > 0:
                return previous_total_sale
            else:
                self.wait_for_given_timeout(1000)
                continue
        return previous_total_sale

    def fetch_current_sales_dates_and_amount(self):
        """ Fetching the current sales and returning the current sales """
        for i in range(30):
            current_total_sale = self.fetch_text(self.lbl_sales_overview_description1)
            sale = "".join([i for i in current_total_sale.split("-")[-1].split()[1] if i.replace(",", "")])
            if float(sale.split()[-1]) > 0:
                return current_total_sale
            else:
                self.wait_for_given_timeout(1000)
                continue
        return False

    def fetch_overall_sales_and_amount(self):
        """ Fetching the overall sales and returning the overall sales """
        if self.page.is_visible(self.lbl_sales_overview_description2):
            return self.fetch_text(self.lbl_sales_overview_description2)
        else:
            return "0.00"

    def fetch_sales_overview_indicators_dates(self):
        """ Fetching the sales overview date indicators and returns the date indicators """
        return self.fetch_text(self.lbl_sales_overview_indicator).split()

    def fetch_org_structure(self):
        """ Fetching org structure and returning org structure """
        org_structure = []
        for i in range(1, 4):
            ele = self.fetch_text(self.txt_country_head.format(i))
            org_structure.append(ele)
        return org_structure

    def fetch_txn_by_type_date_range(self):
        """ Fetching the txn by type date range and returns the date range """
        return self.fetch_text(self.lbl_txns_by_type_daterange)

    def fetch_rgb_color_code_by_type(self, by_type: str):
        """ This method will fetch and returns the rgb color code for specified by_type """
        if self.page.is_visible(self.lbl_rgb_color_by_type.format(by_type.title())):
            rgb_color_code = self.page.get_attribute(self.lbl_rgb_color_by_type.format(by_type.title()), "style")
        else:
            rgb_color_code = self.page.get_attribute(self.lbl_rgb_color_by_type.format(by_type.upper()), "style")
        return rgb_color_code

    def fetch_device_usage_date_range(self):
        """ This method will fetch and returns the device usage date range """
        return self.fetch_text(self.lbl_device_usage)

    def click_view_by(self):
        """ clicks on view by """
        self.perform_click(self.lst_view_by)

    def select_view_by_performance_matrix(self, location: str):
        """ This method will select the specified location and gives the filtered view """
        self.click_view_by()
        self.perform_click(self.rdo_text.format(location.upper()))

    def click_performance_matrix_select_date(self):
        """ Clicks on performance matrix calendar """
        self.perform_click(self.lbl_performance_matrix_calendar)

    def overall_status_validation_db(self, amount: str):
        if amount == "0.00":
            return "0.00"
        elif "-" in amount:
            return "down"
        else:
            return "up"

    def click_profile(self):
        self.perform_click(self.lbl_profile)

    def fetch_user_profile_details(self):
        return self.fetch_text(self.lbl_user_profile_values)

    def perform_logout(self):
        """
        This method is used to perform logout
        """
        self.page.on("dialog", lambda dialog: dialog.accept())
        self.perform_click(self.btn_logout)

    def validation_login_to_dashboard_page(self):
        self.wait_for_element(self.lbl_login_to_dashboard)




