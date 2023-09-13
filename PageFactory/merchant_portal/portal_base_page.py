from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url)

    def wait_for_given_timeout(self, time_in_mill):
        self.page.wait_for_timeout(time_in_mill)

    def search_element(self, locator):
        self.page.wait_for_selector('//div[@class="txnReportsTable_reportsHeader__diLm-"]/following-sibling::div[1]')
        return self.page.wait_for_selector("div.txnReportsTable_reportsTable__qUa1D table")

    def perform_click(self, locator):
        self.page.wait_for_selector(selector=locator, timeout=45000, state="visible").click(timeout=45000)

    def perform_date_Selection(self, locator):
        self.page.wait_for_selector(selector=locator, timeout=45000, state="visible")
        self.page.query_selector(selector=locator).click(timeout=45000)

    def perform_click_hidden(self, locator):
        self.page.wait_for_selector(selector=locator, timeout=45000, state="hidden").click(timeout=45000)

    def fetch_text(self, locator):
        return self.page.wait_for_selector(selector=locator, timeout=45000, state="visible").inner_text()

    def perform_fill(self, locator, value):
        self.page.wait_for_selector(selector=locator, timeout=45000, state="visible").fill(value)

    def wait_for_element(self, locator):
        return self.page.wait_for_selector(selector=locator, timeout=45000, state="visible")

    def wait_for_all_elements(self):
        return self.page.wait_for_load_state('networkidle', timeout=60000)

    def wait_for_load_state(self):
        return self.page.wait_for_load_state('domcontentloaded', timeout=300000)

    def wait_for_element_invisible(self, locator):
        return self.page.wait_for_selector(selector=locator, timeout=45000, state="hidden")

    def wait_for_alert_and_accept(self):
        self.page.wait_for_load_state('domcontentloaded', timeout=60000)
        self.page.expect_popup(timeout=45000)
        self.page.on("dialog", lambda dialog: dialog.accept())

    def perform_click_cnp(self, locator):
        self.page.wait_for_selector(selector=locator, timeout=45000, state="visible").click(timeout=45000)
        # self.page.wait_for_selector(selector=locator, timeout=45000, state="attached").click()

    def select_from_drop_down(self, locator, value):
        self.page.wait_for_selector(selector=locator, timeout=45000, state="visible").select_option(value)

    def select_from_drop_down_combobox(self, value):
        # In Playwright, a combobox is a type of input element that allows users to select one option from a dropdown
        # list of predefined options. It's also known as a "select" element.
        self.page.get_by_role("combobox").select_option(value)

    def click_submit_button(self):
        self.page.get_by_role("button", name="Submit").click(timeout=45000)

    def date_selector(self, date, selectors):
        # self.page.get_by_title(date).click(timeout=45000)
        self.page.type(text=date, selector=selectors)
