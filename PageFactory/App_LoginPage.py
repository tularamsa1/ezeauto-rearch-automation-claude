from selenium.webdriver.common.by import By
from PageFactory.App_BasePage import BasePage
from Utilities.configReader import read_config


class LoginPage(BasePage):

    txt_username = (By.ID, "com.ezetap.basicapp:id/etUid")
    txt_password =  (By.ID, 'com.ezetap.basicapp:id/etPassword')
    btn_login = (By.ID, 'com.ezetap.basicapp:id/btnLogin')
    lbl_login = (By.ID, 'com.ezetap.basicapp:id/tvHintLogin')
    img_ezetaplogo = (By.ID, 'com.ezetap.basicapp:id/imgLogo')
    btn_goToHistory = (By.ID, "com.ezetap.basicapp:id/clGotoHistory")
    dtl_env = (By.XPATH, '//android.widget.TextView[@text ="DEV11"]')

    def __init__(self, driver):
        super().__init__(driver)

    def perform_login(self, username, password):
        if read_config("APIs", "env") in self.fetch_text(self.btn_login):
            pass
        else:
            self.perform_long_press(self.img_ezetaplogo)
            self.scroll_to_text(read_config("APIs", "env")).click()
        self.wait_for_element(self.txt_username).clear()
        self.perform_sendkeys(self.txt_username, username)
        self.wait_for_element(self.txt_password).clear()
        self.perform_sendkeys(self.txt_password, password)
        self.perform_click(self.btn_login)

    def validate_login_page(self):
        return self.wait_for_element(self.lbl_login)
