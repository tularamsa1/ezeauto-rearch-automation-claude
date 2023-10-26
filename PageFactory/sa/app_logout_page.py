from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage


class Logout(BasePage):
    btn_sidemenu = (AppiumBy.XPATH, "//android.widget.ImageButton[@content-desc='Open navigation drawer']")
    btn_account = (AppiumBy.ID, 'com.ezetap.basicapp:id/nav_account')
    btn_arrow = (AppiumBy.ID, 'com.ezetap.basicapp:id/arrow')
    btn_setting = (AppiumBy.ID, 'com.ezetap.basicapp:id/ivArrow')
    btn_logout = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvHintLogout')
    btn_logout_conformation = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnOk')
    btn_logout_arrow = (AppiumBy.ID, 'com.ezetap.basicapp:id/clLogout')

    def __init__(self, driver):
        super().__init__(driver)

    def perform_logout(self):
        """
        This method is used to logout from the app when the autoLoginByTokenLogOutEnabled is enabled
        """
        self.perform_click(self.btn_sidemenu)
        self.perform_click(self.btn_arrow)
        self.perform_click(self.btn_setting)
        self.perform_click(self.btn_logout)
        self.perform_click(self.btn_logout_conformation)

