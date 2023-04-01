# from appium.webdriver.common.touch_action import TouchAction
# from selenium.webdriver.support.select import Select
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
#
# class BasePage:
#
#     def __init__(self, driver):
#         self.driver = driver
#
#     def perform_click(self, locator, time = 45):
#         WebDriverWait(self.driver, time).until(EC.element_to_be_clickable(locator)).click()
#
#     def perform_click1(self, locator, time = 45):
#         WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator)).click()
#
#     def perform_click1(self, locator, time = 45):
#         WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator)).click()
#
#     def select_from_drop_down(self, locator, value, time=45):
#         select = Select(WebDriverWait(self.driver, time).until(EC.visibility_of_element_located(locator)))
#         select.select_by_value(value)
#
#     def fetch_text(self, locator, time = 45):
#         return WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator)).text
#
#     def perform_sendkeys(self, locator, value, time = 45):
#         WebDriverWait(self.driver, 45).until(EC.visibility_of_element_located(locator)).send_keys(value)
#
#     def wait_for_element(self, locator, time = 60):
#         return WebDriverWait(self.driver, time).until(EC.visibility_of_element_located(locator))
#
#     def wait_for_visibility_of_Element(self, locator, time = 45):
#         return WebDriverWait(self.driver, time).until(EC.visibility_of_element_located(locator))
#
#     def wait_for_all_elements(self, locator, time = 45):
#         return WebDriverWait(self.driver, time).until(EC.presence_of_all_elements_located(locator))
#
#     def wait_for_element_invisible(self, locator, time = 45):
#         return WebDriverWait(self.driver, time).until(EC.invisibility_of_element(locator))
#
#     def wait_for_alert_and_accept(self, time = 45):
#         WebDriverWait(self.driver, time).until(EC.alert_is_present())
#         self.driver.switch_to.alert.accept()
#
#     def wait_for_alert_read_text_and_accept(self, time = 45):
#         WebDriverWait(self.driver, time).until(EC.alert_is_present())
#         alert = self.driver.switch_to.alert
#         text = alert.text
#         alert.accept()
#         return text
#
#     def perform_click_cnp(self, locator, time=45):
#         WebDriverWait(self.driver, time).until(EC.element_to_be_clickable(locator)).click()
#
#     def perform_touch_action_using_cordinates(self, x1,y1,x2,y2):
#         TouchAction(self.driver).press(x=x1, y=y1).move_to(x=x2, y=y2).release().perform()
#
#     def perform_clear_text(self, locator, time=45):
#         WebDriverWait(self.driver, time).until(EC.element_to_be_clickable(locator)).clear()

from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url)

    def perform_click(self, locator):
        self.page.wait_for_selector(selector=locator, timeout=45000, state="visible").click(timeout=45000)

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
        # self.page.wait_for_load_state('networkidle', timeout=60000)
        # self.page.on("dialog", lambda dialog: print(dialog.message))
        # self.page.get_by_role("button").click(timeout=45000) # Will hang here
#     def wait_for_alert_read_text_and_accept(self, time = 45):
#         WebDriverWait(self.driver, time).until(EC.alert_is_present())
#         alert = self.driver.switch_to.alert
#         text = alert.text
#         alert.accept()
#         return text

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
    # def perform_touch_action_using_cordinates(self, x1,y1,x2,y2):
    #         TouchAction(self.driver).press(x=x1, y=y1).move_to(x=x2, y=y2).release().perform()

    # def perform_clear_text(self, locator):
    #     self.page.wait_for_selector(selector=locator, timeout=45000, state="visible")
