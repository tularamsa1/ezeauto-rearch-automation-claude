from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:

    def __init__(self, driver):
        self.driver = driver

    def perform_click(self, locator, time=15):
        WebDriverWait(self.driver, time).until(EC.element_to_be_clickable(locator)).click()

    def perform_clickIndex(self, locator,Index, time=15):
        WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located(locator))[Index].click()

    def fetch_text(self, locator, time=15):
        return WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator)).text

    def perform_sendkeys(self, locator, value, time=15):
        WebDriverWait(self.driver, time).until(EC.visibility_of_element_located(locator)).send_keys(value)

    def wait_for_element(self, locator, time=15):
        return WebDriverWait(self.driver, time).until(EC.visibility_of_element_located(locator))

    def wait_for_element_to_be_clickable(self, locator, time=15):
        return WebDriverWait(self.driver, time).until(EC.element_to_be_clickable(locator))

    def wait_for_all_elements(self, locator, time=15):
        return WebDriverWait(self.driver, time).until(EC.presence_of_all_elements_located(locator))

    def perform_touch_action_using_cordinates(self, x1,y1,x2,y2):
        TouchAction(self.driver).press(x=x1, y=y1).move_to(x=x2, y=y2).release().perform()

    def perform_long_press(self, locator):
        element = self.wait_for_element(locator)
        actions = TouchAction(self.driver)
        actions.long_press(element)
        actions.perform()

    def perform_swipeUp(self, swipes):
        for i in range(1, swipes + 1):
            self.driver.swipe(514, 600, 514, 200, 1000)

    def scroll_to_text(self, text):
        try:
            element = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollIntoView(new UiSelector().text("' + text + '").instance(0));')
            return element
        except NoSuchElementException:
            print('it was not found')
            return None
        except Exception as e:
            print("Unexpected error:", e)
            return None

