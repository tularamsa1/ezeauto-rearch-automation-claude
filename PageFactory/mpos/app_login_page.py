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

    def select_environment(self):
        """
        This is used to select environment in PAXs devices for executing autologin
        """
        self.scroll_to_text(read_config("APIs", "env")).click()

    def perform_login_for_auto_login_functionality(self, username, password, Pax_Device=None):
        """
        Logs into the application, handling both standard and auto-login scenarios.
        Checks device type and manages battery optimize settings popup
        """

        if read_config("ParallelExecution", "deviceOnly") == "True":
            self.scroll_to_text(read_config("APIs", "env")).click()
        elif read_config("APIs", "env") in self.fetch_text(self.btn_login):
            pass
        else:
            self.perform_long_press(self.img_ezetaplogo)
            self.scroll_to_text(read_config("APIs", "env")).click()

        try:
            txt_username_val = self.visibility_of_elements(self.txt_username, time=10)
            if Pax_Device == None and len(txt_username_val) < 0:
                logger.info(f"Pax_Device is None and txt_username_val is null")
                pass
            else:
                self.wait_for_element(self.txt_username).clear()
                self.perform_sendkeys(self.txt_username, username)
                self.wait_for_element(self.txt_password).clear()
                self.perform_sendkeys(self.txt_password, password)
                self.perform_click(self.btn_login)
                logger.info(f"Pax_Device is True and txt_username_val is not null")
        except Exception as e:
            logger.info(f"Pax_Device is null and txt_username_val is not displayed")

        try:
            setting_btn_val = self.visibility_of_elements(self.btn_settings, time=10)
            if Pax_Device == None and len(setting_btn_val) < 0:
                logger.info(f"Pax_Device is False and setting_btn_val is zero to click on battery optimize settings")
                pass
            elif Pax_Device == True and len(setting_btn_val) > 0:
                # click on battery optimize settings
                self.perform_click(self.btn_settings)
                logger.info(f"Pax_Device is True and setting_btn_val is not null to click on battery optimize settings")
        except Exception as e:
            logger.info(f"battery optimize settings popup is not displayed for pax device")
