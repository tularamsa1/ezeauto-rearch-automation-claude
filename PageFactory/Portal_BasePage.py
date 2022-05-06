from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:

    def __init__(self, driver):
        self.driver = driver

    def perform_click(self, locator):
        WebDriverWait(self.driver, 12).until(EC.presence_of_element_located(locator)).click()

    def fetch_text(self, locator, time = 12):
        return WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator)).text

    def perform_sendkeys(self, locator, value):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator)).send_keys(value)

    def wait_for_element(self, locator):
        return WebDriverWait(self.driver, 12).until(EC.presence_of_element_located(locator))

    def wait_for_all_elements(self, locator):
        return WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located(locator))

    def perform_touch_action_using_cordinates(self, x1,y1,x2,y2):
        TouchAction(self.driver).press(x=x1, y=y1).move_to(x=x2, y=y2).release().perform()
