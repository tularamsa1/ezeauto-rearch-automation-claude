from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.mpos.app_base_page import BasePage
from Utilities.ConfigReader import read_config
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class LoginPage(BasePage):

    txt_username = (AppiumBy.ID, "com.ezetap.basicapp:id/etUid")
    txt_password =  (AppiumBy.ID, 'com.ezetap.basicapp:id/etPassword')
    btn_login = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnLogin')
    lbl_login = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvHintLogin')
    img_ezetaplogo = (AppiumBy.ID, 'com.ezetap.basicapp:id/imgLogo')
    btn_goToHistory = (AppiumBy.ID, "com.ezetap.basicapp:id/clGotoHistory")
    dtl_env = (AppiumBy.XPATH, '//android.widget.TextView[@text ="DEV11"]')
    txt_auth_password = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvInputEtMpin')
    txt_auth_username = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvInputEtAccId')
    btn_auth_login = (AppiumBy.ID, 'com.ezetap.service.demo:id/btnProceed')
    btn_settings = (AppiumBy.ID, "android:id/button1")
    btn_allow_access = (AppiumBy.ID, "android:id/switch_widget")
    btn_click_on_back = (AppiumBy.XPATH, "//android.widget.ImageButton[@index='0']")
    txt_login_failed_msg = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTitle')

    btn_settings_sample = (AppiumBy.ID, 'com.ezeapi.sample:id/btnSettings')
    txt_merchant_name_sample = (AppiumBy.ID, 'com.ezeapi.sample:id/merchant_name')
    txt_username_sample = (AppiumBy.ID, 'com.ezeapi.sample:id/user_name')
    txt_password_sample = (AppiumBy.ID, 'com.ezeapi.sample:id/password')
    txt_app_mode_sample = (AppiumBy.ID, 'com.ezeapi.sample:id/app_mode')
    btn_set_merchant_sample = (AppiumBy.XPATH, '//android.widget.Button[@text ="Set Merchant"]')

    def __init__(self, driver):
        super().__init__(driver)

    def perform_login(self, username, password):
        if read_config("ParallelExecution", "deviceOnly") == "True":
            self.scroll_to_text(read_config("APIs", "env")).click()

        elif read_config("APIs", "env") in self.fetch_text(self.btn_login):
            pass
        else:
            self.perform_long_press(self.img_ezetaplogo)
            self.scroll_to_text(read_config("APIs", "env")).click()
        self.wait_for_element(self.txt_username).clear()
        self.perform_sendkeys(self.txt_username, username)
        self.wait_for_element(self.txt_password).clear()
        self.perform_sendkeys(self.txt_password, password)
        self.perform_click(self.btn_login)

        try:
            setting_btn_val = self.visibility_of_elements(self.btn_settings)
            if len(setting_btn_val) < 0:
                pass
            else:
                self.perform_click(self.btn_settings)
                self.perform_click(self.btn_allow_access)
                self.perform_click(self.btn_click_on_back)
                self.perform_click(self.btn_login)

        except Exception as e:
            logger.info(f"Settings popup is not displayed")

    def validate_login_page(self):
        return self.wait_for_element(self.lbl_login)

    def perform_cash_additional_auth(self, app_password):
        """
        performs additional authorization when cash txn
        param: password
        """
        self.wait_for_element(self.txt_auth_password).clear()
        self.perform_sendkeys(self.txt_auth_password, app_password)
        self.perform_click(self.btn_auth_login)

    def fetch_login_failed_msg(self):
        """
        fetches text from login failed pop tab in the login page
        return:txt_login_failed_msg:str
        """
        self.wait_for_element(self.txt_login_failed_msg)
        return self.fetch_text(self.txt_login_failed_msg)

    def config_merchant_for_sample_app(self, org_code: str, username: str, password: str):
        """
        This method is used to add merchant details in sample app
        param: org_code: str
        param: username: str
        param: password: str
        """
        self.perform_click(self.btn_settings_sample)
        self.perform_sendkeys(self.txt_merchant_name_sample, org_code)
        self.perform_sendkeys(self.txt_username_sample, username)
        self.perform_sendkeys(self.txt_password_sample, password)
        self.scroll_to_text("Set Merchant")
        self.perform_sendkeys(self.txt_app_mode_sample, read_config("APIs", "env"))
        self.perform_click(self.btn_set_merchant_sample)