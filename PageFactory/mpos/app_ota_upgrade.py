import os
import re
import subprocess
from PageFactory.App_BasePage import BasePage
from appium.webdriver.common.appiumby import AppiumBy
from Utilities import ConfigReader, DBProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class OTA_upgrade(BasePage):
    btn_skip = (AppiumBy.ID, "com.ezetap.basicapp:id/btnSkipAppUpdate")
    btn_update_now = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnUpdateNow')
    txt_update_tap_tittle = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvUpdateTitle')
    txt_download_tab = (AppiumBy.ID, 'android:id/alertTitle')
    btn_install_emulator = (AppiumBy.ID, "android:id/button1")
    btn_done = (AppiumBy.XPATH, '//*[@text="Done"]')
    btn_install_pax = (AppiumBy.ID, 'com.android.packageinstaller:id/ok_button')
    btn_done_pax = (AppiumBy.ID, 'com.android.packageinstaller:id/done_button')
    btn_settings = (AppiumBy.XPATH, '//*[@text="Settings"]')
    btn_allow_access = (AppiumBy.ID, "android:id/switch_widget")
    btn_click_on_back = (AppiumBy.XPATH, "//android.widget.ImageButton[@index='0']")

    def __init__(self, driver):
        super().__init__(driver)

    def click_skip(self):
        """
        performs clicking on the skip button
        """
        self.wait_for_element(self.btn_skip)
        self.perform_click(self.btn_skip)

    def click_on_update_now(self):
        """
        performs clicking on the update now button
        """
        self.perform_click(self.btn_update_now)

    def fetch_update_tap_tittle(self):
        """
        fetches tittle text from the update tab
        return: str
        """
        self.wait_for_element(self.txt_update_tap_tittle)
        return self.fetch_text(self.txt_update_tap_tittle)

    def fetch_skip_txt_from_skip_button(self):
        """
        fetches text from skip button
        return: str
        """
        self.wait_for_element(self.btn_skip)
        return self.fetch_text(self.btn_skip)

    def validate_update_tab(self):
        """
        Verifies the availability of the update tab
        """
        self.wait_for_element(self.txt_update_tap_tittle)

    def click_on_install(self):
        """
        performs clicking on the install button after the updated version is downloaded
        """
        self.handle_install_unknown_permission_setting(time= 60)
        self.wait_for_element(self.btn_install_emulator, time=60)
        self.perform_click(self.btn_install_emulator)

    def click_on_done(self):
        """
        performs clicking on the done button
        """
        self.perform_click(self.btn_done)

    def click_on_install_btn_pax(self):
        """
        performs clicking on the update button after the updated version is downloaded in pax
        """
        self.handle_install_unknown_permission_setting(time= 240)
        self.wait_for_element(self.btn_install_pax, time=240)
        self.perform_click(self.btn_install_pax)

    def click_on_done_pax(self):
        """
        performs clicking on the done button in pax
        """
        self.perform_click(self.btn_done_pax)

    def handle_install_unknown_permission_setting(self, time: int):
        """
        This function is used to handle setting of install unknown apps
        param: time: int
        """
        try:
            setting_btn_val = self.visibility_of_elements(self.btn_settings, time= time )
            if len(setting_btn_val) < 0:
                pass
            else:
                self.perform_click(self.btn_settings)
                self.perform_click(self.btn_allow_access)
                self.perform_click(self.btn_click_on_back)
        except:
            logger.info(f"Settings popup to give permission to install unknown application is not displayed")


def get_all_mpos_apk_file_names(directory_path: str):
    """
     This function gets all the file name that present in the App directory
     param: directory_path: str
     return: list
    """
    file_names = os.listdir(directory_path)
    apps_lst = []
    for file_name in file_names:
        if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'false':
            if file_name.startswith("MPOSX"):
                apps_lst.append(file_name)
        else:
            if file_name.startswith("PAX_MPOSX"):
                apps_lst.append(file_name)
    return apps_lst


def find_file_path_by_name(directory_path_to_search: str, file_name_to_get_path: str):
    """
    This function gets the path of a mpos or sa apk path
    param: directory_path_to_search : str
    param: file_name_to_get_path : str
    """
    for root, _, files in os.walk(directory_path_to_search):
        if file_name_to_get_path in files:
            return os.path.join(root, file_name_to_get_path)
    return None


def install_lower_mpos_version(apps_lst: list, given_version_to_pin: str, directory_path: str, id_of_device: str):
    """
    This function compares the version the mpos app version and install the lower version the given version
    param: apps_lst : list
    param : given_version_to_pin: str
    param: directory_path: str
    param:  id_of_device: str
    """
    logger.debug(f"list of App version :- {apps_lst}")
    given_version_to_pin_int = int(given_version_to_pin.replace(".", ""))
    for app in apps_lst:
        match = re.search(r'\d+\.\d+\.\d+', app)
        if match:
            version_number = match.group(0)
            version_number_int = int(version_number.replace(".", ""))
        else:
            logger.debug("No version number found")
        if version_number_int < given_version_to_pin_int:
            if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'false':
                mpos_apk_path = find_file_path_by_name(directory_path, f"MPOSX_{version_number}.apk")
            else:
                mpos_apk_path = find_file_path_by_name(directory_path, f"PAX_MPOSX_{version_number}.apk")
            result_uninstall = subprocess.run(['adb', 'uninstall', 'com.ezetap.basicapp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            if "Success" in result_uninstall.stdout:
                logger.info("Application uninstalled successfully.")
            else:
                logger.info(f"Failed to uninstall the application: {result_uninstall.stderr}")
            install_command_lower_ver = ["adb", "-s", id_of_device, "install", "-r", "-g", mpos_apk_path]
            result = subprocess.run(install_command_lower_ver, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            if "Success" in result.stdout:
                logger.info("Application installed successfully.")
            else:
                logger.info(f"Failed to install the application: {result.stderr}")
            break
        else:
            logger.info(f"The provided version number :{version_number}, is higher than the specified version: {given_version_to_pin},")


def unpining_mpos_update_version(org_code: str, given_version_to_pin: str, severity: int):
    """
      This function is used to unpin the mpos update version from a particular merchant depends on org_code
      param: org_code: str
      param: given_version_to_pin: str
      param: severity: int
    """
    if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'true':
        device_type = 'PAX'
        query = "UPDATE app_version SET status = 'INACTIVE' WHERE status = 'ACTIVE' AND severity = '" + str(
            severity) + "' AND application_id = 'ezetap_android' AND org_code = '" + str(
            org_code) + "' AND device_type= '" + str(device_type) + "' and version_name = '" + str(
            given_version_to_pin) + "';"
        logger.info(f"query to unpin {query}")
        DBProcessor.setValueToDB(query)
    else:
        device_type = ['REGULAR_ANDROID', '']
        for device in device_type:
            query = "UPDATE app_version SET status = 'INACTIVE' WHERE status = 'ACTIVE' AND severity = '" + str(
                severity) + "' AND application_id = 'ezetap_android' AND org_code = '" + str(
                org_code) + "' AND device_type= '" + str(device) + "' and version_name = '" + str(
                given_version_to_pin) + "';"
            logger.info(f"query to unpin {query}")
            DBProcessor.setValueToDB(query)


def pinning_mpos_version_to_merchant(org_code: str, ver_code: str, given_version_to_pin: str, severity: int):
    """
    This function is used to pin the mPOS update version for a specific merchant based on the org_code. In the case of pinning
    to a merchant to receive updates in an emulator, there can be some configuration setups. For a regular Android application
    setup, the device_type can be either 'Regular Android' or left empty (''). Therefore, as a best practice, we perform two
    pins for the app update.
    param: org_code: str
    param: ver_code: str
    param: given_version_to_pin: str
    param: severity: int
    """
    device_type = 'PAX'
    if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'true':
        query = "INSERT INTO app_version (created_by, created_time, modified_by, modified_time, org_code, application_id" \
                ", file_size, notes, severity, status, version_code, version_name, device_type) VALUES ('ezetap_automation', now()," \
                " 'ezetap_automation', now(), '" + str(
            org_code) + "', 'ezetap_android', 16943729, 'OTA Mpos update test', '" + str(severity) + "', 'ACTIVE', " \
                                                                                                     "'" + str(
            ver_code) + "', '" + str(given_version_to_pin) + "', '" + str(
            device_type) + "');"
        DBProcessor.setValueToDB(query)
        logger.info(f"update version is pinned to merchant successfully")
    else:
        device_type = ['REGULAR_ANDROID', '']
        for device in device_type:
            query = "INSERT INTO app_version (created_by, created_time, modified_by, modified_time, org_code, application_id" \
                    ", file_size, notes, severity, status, version_code, version_name, device_type) VALUES ('ezetap_automation', now()," \
                    " 'ezetap_automation', now(), '" + str(
                org_code) + "', 'ezetap_android', 16943729, 'OTA Mpos update test', '" + str(severity) + "', 'ACTIVE', " \
                                                                                                         "'" + str(
                ver_code) + "', '" + str(given_version_to_pin) + "', '" + str(
                device) + "');"
            DBProcessor.setValueToDB(query)
            logger.info(f"update version is pinned to merchant successfully(Emulator)")


def get_all_sa_apk_file_name(directory_path: str):
    """
    This function give all the sa file name present in the app directory
    param: directory_path: str
    return: list
    """
    file_names = os.listdir(directory_path)
    apps_lst = []
    for file_name in file_names:
        if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'false':
            if file_name.startswith("SA"):
                apps_lst.append(file_name)
        else:
            if file_name.startswith("PAX_SA"):
                apps_lst.append(file_name)
    logger.debug(f"apps_lst contains the file names that start with SA: {apps_lst}")
    return apps_lst


def install_sa_lower_version(apps_lst: list, given_version_to_pin: str, directory_path: str, id_of_device: str):
    """
    This function compares the version the sa app version and install the lower sa version than given version
    param: apps_lst: list
    param:  given_version_to_pin: str
    param: directory_path: str
    param: id_of_device: str
    """
    logger.debug(f"list of App version :- {apps_lst}")
    given_version_to_pin_int = int(given_version_to_pin.replace(".", ""))
    for app in apps_lst:
        match = re.search(r'\d+\.\d+\.\d+', app)
        if match:
            version_number = match.group(0).replace(".","")
        else:
            logger.debug("No version number found")
        if int(version_number) < given_version_to_pin_int:
            if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'false':
                sa_apk_path = find_file_path_by_name(directory_path, f"SA_{version_number}.apk")
            else:
                sa_apk_path = find_file_path_by_name(directory_path, f"PAX_SA_{version_number}.apk")
            result_uninstall = subprocess.run(['adb', 'uninstall', 'com.ezetap.service.demo'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            if "Success" in result_uninstall.stdout:
                logger.info("Application uninstalled successfully.")
            else:
                logger.info(f"Failed to uninstall the application: {result_uninstall.stderr}")
            install_command_lower_ver = ["adb", "-s", id_of_device, "install", "-r", "-g", sa_apk_path]
            result = subprocess.run(install_command_lower_ver, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            if "Success" in result.stdout:
                logger.info(" SA Application installed successfully.")
            else:
                logger.info(f"Failed to install the application: {result.stderr}")
            break
        else:
            logger.info(f"The provided version number :{version_number}, is higher than the specified version: {given_version_to_pin},")


def unpining_sa_update_version(org_code: str, given_version_to_pin: str, severity: int):
    """
        This function is used to unpin the sa update version from a particular merchant depends on org_code
        param:org_code: str
        param: given_version_to_pin: str
        param:  severity: int
      """
    if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'true':
        device_type = 'PAX'
        query = "UPDATE app_version SET status = 'INACTIVE' WHERE status = 'ACTIVE' AND severity = '" + str(
            severity) + "' AND application_id = 'ezetap_android_service' AND org_code = '" + str(
            org_code) + "' and version_name = '" + str(given_version_to_pin) + "' AND device_type= '" + str(
            device_type) + "' ;"
        DBProcessor.setValueToDB(query)
        logger.info("unpinning the new Sa update version to merchant is done successfully for Pax")
    else:
        device_type = ['REGULAR_ANDROID', '']
        for device in device_type:
            query = "UPDATE app_version SET status = 'INACTIVE' WHERE status = 'ACTIVE' AND severity = '" + str(
                severity) + "' AND application_id = 'ezetap_android_service' AND org_code = '" + str(
                org_code) + "' and version_name = '" + str(given_version_to_pin) + "' AND device_type= '" + str(
                device) + "' ;"
            DBProcessor.setValueToDB(query)
        logger.info("unpinning the new Sa update version to merchant is done successfully For emulator")


def pinning_sa_version_to_merchant(org_code: str, ver_code: str, given_version_to_pin: str, severity: int):
    """
    This function is used to pin the SA update version for a specific merchant based on the org_code. In the case of pinning
    to a merchant to receive updates in an emulator, there can be some configuration setups. For a regular Android application
    setup, the device_type can be either 'Regular Android' or left empty (''). Therefore, as a best practice, we perform two
    pins for the app update.
    param: org_code: str
    param: ver_code: str
    param: given_version_to_pin: str
    param:  severity: int
    """
    if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'true':
        device_type = 'PAX'
        query = "INSERT INTO app_version (created_by, created_time, modified_by, modified_time, org_code, application_id" \
                ", file_size, notes, severity, status, version_code, version_name, device_type) VALUES ('ezetap_automation', now()," \
                " 'ezetap_automation', now(), '" + str(
            org_code) + "', 'ezetap_android_service', 16943729, 'OTA test', '" + str(severity) + "', 'ACTIVE', " \
                                                                                                 "'" + str(
            ver_code) + "', '" + str(given_version_to_pin) + "', '" + str(
            device_type) + "');"
        DBProcessor.setValueToDB(query)
        logger.info(f"update version is pinned to merchant successfully")
    else:
        device_type = ['REGULAR_ANDROID', '']
        for device in device_type:
            query = "INSERT INTO app_version (created_by, created_time, modified_by, modified_time, org_code, application_id" \
                    ", file_size, notes, severity, status, version_code, version_name, device_type) VALUES ('ezetap_automation', now()," \
                    " 'ezetap_automation', now(), '" + str(
                org_code) + "', 'ezetap_android_service', 16943729, 'OTA test', '" + str(severity) + "', 'ACTIVE', " \
                                                                                                     "'" + str(
                ver_code) + "', '" + str(given_version_to_pin) + "', '" + str(
                device) + "');"
            DBProcessor.setValueToDB(query)
            logger.info(f"update version is pinned to merchant successfully (emulator)")
