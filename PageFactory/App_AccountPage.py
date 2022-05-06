from selenium.webdriver.common.by import By
from PageFactory.App_BasePage import BasePage


class AccountPage(BasePage):


    mnu_setting = (By.ID, 'com.ezetap.basicapp:id/clSettingsItem')
    mnu_Language = (By.ID, 'com.ezetap.basicapp:id/tvLanguage')
    rdo_Language = (By.ID, 'com.ezetap.basicapp:id/rbLanguage')
    btn_LanguageProceed = (By.ID, 'com.ezetap.basicapp:id/btnProceed')
    lbl_SAVersion = (By.ID, 'com.ezetap.basicapp:id/tvServiceVersionData')
    btn_logout = (By.ID, 'com.ezetap.basicapp:id/clLogout')
    btn_confirmLogout = (By.ID, 'com.ezetap.basicapp:id/btnOk')

    def __init__(self, driver):
        super().__init__(driver)

    def click_on_logout(self):
        self.perform_click(self.mnu_setting)
        self.perform_click(self.btn_logout)
        self.perform_click(self.btn_confirmLogout)

    def click_on_setting(self):
        self.perform_click(self.mnu_setting)

    def click_on_Language(self):
        self.perform_click(self.mnu_Language)

    def click_on_eng_Lang(self):
        self.perform_clickIndex(self.rdo_Language,0)

    def click_on_hindi_Lang(self):
        self.perform_clickIndex(self.rdo_Language,1)

    def click_on_proceed_btn(self):
        self.perform_click(self.btn_LanguageProceed)

    def get_Lang_text(self):
        return self.fetch_text(self.mnu_Language)

    def get_SA_version(self):
        return self.fetch_text(self.lbl_SAVersion)



