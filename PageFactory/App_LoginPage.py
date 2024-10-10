from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage
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
    btn_allow_premission = (AppiumBy.ID, "com.android.packageinstaller:id/permission_allow_button")

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

    def perform_login_for_pax(self, username, password, Pax_Device=None):
        if read_config("ParallelExecution", "deviceOnly") == "True":
            self.scroll_to_text(read_config("APIs", "env")).click()
        elif read_config("APIs", "env") in self.fetch_text(self.btn_login):
            pass
        else:
            self.perform_long_press(self.img_ezetaplogo)
            self.scroll_to_text(read_config("APIs", "env")).click()

        try:
            setting_btn_val = self.visibility_of_elements(self.btn_settings, time=10)
            if Pax_Device == None and len(setting_btn_val) < 0:
                logger.info(f"Pax_Device is False and setting_btn_val is null")
                pass
            elif Pax_Device == True and len(setting_btn_val) > 0:
                # click on go to settings
                self.perform_click(self.btn_settings)
                # click on Allow permission
                self.perform_click(self.btn_allow_access)
                # click on allow media, photo and files on your device
                self.perform_click(self.btn_allow_permission)
                # click on allow manage device calls
                self.perform_click(self.btn_allow_permission)
                # click on allow device location
                self.perform_click(self.btn_allow_permission)
                logger.info(f"Pax_Device is True and setting_btn_val is not null")
        except Exception as e:
            logger.info(f"Settings popup is not displayed for pax device")

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

    def validate_login_page(self):
        return self.wait_for_element(self.lbl_login)

    def perform_cash_additional_auth(self, app_password):
        self.wait_for_element(self.txt_auth_password).clear()
        self.perform_sendkeys(self.txt_auth_password, app_password)
        self.perform_click(self.btn_auth_login)
