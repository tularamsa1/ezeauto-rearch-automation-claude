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
    
    # Login error message popup elements
    img_error_dummy = (AppiumBy.ID, 'com.ezetap.basicapp:id/imgDummy')
    lyt_error_message = (AppiumBy.ID, 'com.ezetap.basicapp:id/layout_message')
    lbl_error_message = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_message')    
    btn_error_close = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnClose')
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
        elif read_config("ParallelExecution", "deviceOnly") == "False":
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

        except Exception:
            logger.info("Settings popup is not displayed")

    def prod_app_login(self, username, password):
        """ Loging into the prod app """
        self.wait_for_element(self.txt_username).clear()
        self.perform_sendkeys(self.txt_username, username)
        self.wait_for_element(self.txt_password).clear()
        self.perform_sendkeys(self.txt_password, password)
        self.perform_click(self.btn_login)

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
        try:
            logger.info("Fetching login failed message title")
            self.wait_for_element(self.txt_login_failed_msg)
            error_title = self.fetch_text(self.txt_login_failed_msg)
            logger.info(f"Fetched login failed message title: {error_title}")
            return error_title
        except Exception as e:
            logger.error(f"Failed to fetch login failed message title: {str(e)}")
            raise

    def is_error_layout_displayed(self):
        """
        Checks if the error message layout is displayed.
        :return: True if error layout is displayed, False otherwise
        """
        try:
            logger.info("Checking if error layout is displayed")
            element = self.wait_for_element(self.lyt_error_message)
            is_displayed = element.is_displayed()
            logger.info(f"Error layout displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Error layout not found or not displayed: {str(e)}")
            return False

    def is_error_image_displayed(self):
        """
        Checks if the error dummy image is displayed.
        :return: True if image is displayed, False otherwise
        """
        try:
            logger.info("Checking if error image is displayed")
            element = self.wait_for_element(self.img_error_dummy)
            is_displayed = element.is_displayed()
            logger.info(f"Error image displayed: {is_displayed}")
            return is_displayed
        except Exception as e:
            logger.warning(f"Error image not found or not displayed: {str(e)}")
            return False

    def fetch_error_title(self):
        """
        Fetches the title text from the error popup.
        :return: Error title as a string
        """
        try:
            logger.info("Fetching error title from popup")
            self.wait_for_element(self.txt_login_failed_msg)
            error_title = str(self.fetch_text(self.txt_login_failed_msg))
            logger.info(f"Fetched error title: {error_title}")
            return error_title
        except Exception as e:
            logger.error(f"Failed to fetch error title: {str(e)}")
            raise

    def fetch_error_message(self):
        """
        Fetches the message text from the error popup.
        :return: Error message as a string
        """
        try:
            logger.info("Fetching error message from popup")
            self.wait_for_element(self.lbl_error_message)
            error_message = str(self.fetch_text(self.lbl_error_message))
            logger.info(f"Fetched error message: {error_message}")
            return error_message
        except Exception as e:
            logger.error(f"Failed to fetch error message: {str(e)}")
            raise

    def close_error_popup(self):
        """
        Clicks the close button to dismiss the error popup.
        """
        try:
            logger.info("Closing error popup")
            self.wait_for_element(self.btn_error_close)
            self.perform_click(self.btn_error_close)
            logger.info("Error popup closed successfully")
        except Exception as e:
            logger.error(f"Failed to close error popup: {str(e)}")
            raise

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
            if Pax_Device is None and len(txt_username_val) < 0:
                logger.info("Pax_Device is None and txt_username_val is null")
                pass
            else:
                self.wait_for_element(self.txt_username).clear()
                self.perform_sendkeys(self.txt_username, username)
                self.wait_for_element(self.txt_password).clear()
                self.perform_sendkeys(self.txt_password, password)
                self.perform_click(self.btn_login)
                logger.info("Pax_Device is True and txt_username_val is not null")
        except Exception:
            logger.info("Pax_Device is null and txt_username_val is not displayed")

        try:
            setting_btn_val = self.visibility_of_elements(self.btn_settings, time=10)
            if Pax_Device is None and len(setting_btn_val) < 0:
                logger.info("Pax_Device is False and setting_btn_val is zero to click on battery optimize settings")
                pass
            elif Pax_Device and len(setting_btn_val) > 0:
                # click on battery optimize settings
                self.perform_click(self.btn_settings)
                logger.info("Pax_Device is True and setting_btn_val is not null to click on battery optimize settings")
        except Exception:
            logger.info("battery optimize settings popup is not displayed for pax device")
