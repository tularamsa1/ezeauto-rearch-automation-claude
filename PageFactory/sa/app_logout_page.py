from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage


class Logout(BasePage):
    btn_account = (AppiumBy.ID, 'com.ezetap.basicapp:id/cardViewMerchant')
    mnu_navigation_drawer = (AppiumBy.XPATH, '//android.widget.ImageButton[@content-desc="Open navigation drawer"]')
    btn_setting = (AppiumBy.ID, 'com.ezetap.basicapp:id/clSettingsItem')
    btn_logout = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvHintLogout')
    btn_logout_conformation = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnOk')

    def __init__(self, driver):
        super().__init__(driver)

    def perform_logout(self):
        """
        This method is used to logout from the app when the autoLoginByTokenLogOutEnabled is enabled
        """
        self.perform_click(self.mnu_navigation_drawer)
        self.perform_click(self.btn_account)
        self.perform_click(self.btn_setting)
        self.perform_click(self.btn_logout)
        self.perform_click(self.btn_logout_conformation)


