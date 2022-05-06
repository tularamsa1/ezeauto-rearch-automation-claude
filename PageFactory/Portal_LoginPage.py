from selenium.webdriver.common.by import By

from PageFactory.Portal_BasePage import BasePage
from Utilities import configReader


class PortalLoginPage(BasePage):

    txt_userName = (By.NAME, 'username')
    txt_password = (By.NAME, 'password')
    btn_signIn = (By.NAME, 'Submit')


    def __init__(self, driver):
        super().__init__(driver)

    def perform_login_to_portal(self, username, password):
        url = configReader.read_config("APIs", "baseUrl") + configReader.read_config("APIs", "portalLogin")
        self.driver.get(url)
        self.driver.maximize_window()
        self.wait_for_element(self.txt_userName).clear()
        self.perform_sendkeys(self.txt_userName, username)
        self.wait_for_element(self.txt_password).clear()
        self.perform_sendkeys(self.txt_password, password)
        self.perform_click(self.btn_signIn)
