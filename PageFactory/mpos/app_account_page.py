from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage


class AccountPage(BasePage):

    mnu_setting = (AppiumBy.ID, 'com.ezetap.basicapp:id/clSettingsItem')
    mnu_Language = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvLanguage')
    rdo_Language = (AppiumBy.ID, 'com.ezetap.basicapp:id/rbLanguage')
    btn_LanguageProceed = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnProceed')
    lbl_SAVersion = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvServiceVersionData')
    btn_logout = (AppiumBy.ID, 'com.ezetap.basicapp:id/clLogout')
    btn_confirmLogout = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnOk')
    txt_mpos_version = (AppiumBy.ID,'com.ezetap.basicapp:id/tvMposVersionData')
    txt_sa_version = (AppiumBy.ID,'com.ezetap.basicapp:id/tvServiceVersionData')
    btn_back = (AppiumBy.ID,'com.ezetap.basicapp:id/tvServiceVersionData')

    def __init__(self, driver):
        super().__init__(driver)

    def click_on_logout(self):
        """
        performs logout from the mpos application
        """
        self.perform_click(self.mnu_setting)
        self.perform_click(self.btn_logout)
        self.perform_click(self.btn_confirmLogout)

    def click_on_setting(self):
        """
        performs click on setting menu
        """
        self.perform_click(self.mnu_setting)

    def click_on_Language(self):
        """
        performs clicking on language menu
        """
        self.perform_click(self.mnu_Language)

    def click_on_eng_Lang(self):
        """
        performs clicking in english language
        """
        self.perform_clickIndex(self.rdo_Language,0)

    def click_on_hindi_Lang(self):
        """
        performs clicking on hindi language
        """
        self.perform_clickIndex(self.rdo_Language,1)

    def click_on_proceed_btn(self):
        """
        performs clicking on proceed button
        """
        self.perform_click(self.btn_LanguageProceed)

    def get_Lang_text(self):
        """
        fetches text from language menu
        """
        return self.fetch_text(self.mnu_Language)

    def get_SA_version(self):
        """
        fetches text of service application version from account page
        """
        return self.fetch_text(self.lbl_SAVersion)

    def fetch_mpos_version(self):
        """
        fetches text of mpos application version from account page
        """
        return self.fetch_text(self.txt_mpos_version)

    def fetch_sa_version(self):
        """
         fetches text of service application version from account page
         """
        return self.fetch_text(self.txt_sa_version)

    def click_on_back(self):
        """
        performs clicking on back buttom
        """
        self.perform_click(self.btn_back)

    def change_language_to_hindi(self):
        self.click_on_setting()
        self.click_on_Language()
        self.click_on_hindi_Lang()
        self.click_on_proceed_btn()

    def change_language_to_english(self):
        self.click_on_setting()
        self.click_on_Language()
        self.click_on_eng_Lang()
        self.click_on_proceed_btn()


