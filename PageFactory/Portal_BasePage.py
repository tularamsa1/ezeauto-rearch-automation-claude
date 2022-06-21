from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:

    def __init__(self, driver):
        self.driver = driver

    def perform_click(self, locator, time = 15):
        WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator)).click()

    def select_from_drop_down(self, locator, value, time=15):
        select = Select(WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator)))
        select.select_by_value(value)



    def fetch_text(self, locator, time = 15):
        return WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator)).text

    def perform_sendkeys(self, locator, value, time = 15):
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(locator)).send_keys(value)

    def wait_for_element(self, locator, time = 15):
        return WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator))

    def wait_for_all_elements(self, locator, time = 15):
        return WebDriverWait(self.driver, time).until(EC.presence_of_all_elements_located(locator))

    def wait_for_element_invisible(self, locator, time = 15):
        return WebDriverWait(self.driver, time).until(EC.invisibility_of_element(locator))

    def wait_for_alert_and_accept(self, time = 15):
        WebDriverWait(self.driver, time).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()


    def perform_touch_action_using_cordinates(self, x1,y1,x2,y2):
        TouchAction(self.driver).press(x=x1, y=y1).move_to(x=x2, y=y2).release().perform()

    def wait_for_alert_and_accept(self, time=15):
        WebDriverWait(self.driver, time).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()

    def wait_for_element_invisible(self, locator, time=15):
        return WebDriverWait(self.driver, time).until(EC.invisibility_of_element(locator))