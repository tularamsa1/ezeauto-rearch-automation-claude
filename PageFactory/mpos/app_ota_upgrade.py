import os
import re
import subprocess
import time
from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.App_BasePage import BasePage
from Utilities import ConfigReader, DBProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class OTA_upgrade(BasePage):
    btn_skip = (AppiumBy.ID, "com.ezetap.basicapp:id/btnSkipAppUpdate")
    btn_update_now = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnUpdateNow')
    txt_update_tap_tittle = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvUpdateTitle')
    txt_download_tab = (AppiumBy.ID, 'android:id/alertTitle')
    btn_install = (AppiumBy.XPATH, '//*[@text="INSTALL"]')
    btn_update = (AppiumBy.XPATH, '//*[@text="Update"]')
    btn_done_2 = (AppiumBy.XPATH, '//*[@text="Done"]')
    btn_done = (AppiumBy.XPATH, '//*[@text="DONE"]')

    def __init__(self, driver):
        super().__init__(driver)

    def click_skip(self):
        self.wait_for_element(self.btn_skip)
        self.perform_click(self.btn_skip)

    def click_on_update_now(self):
        self.wait_for_element(self.btn_update_now)
        self.perform_click(self.btn_update_now)

    def fetch_update_tap_tittle(self):
        self.wait_for_element(self.txt_update_tap_tittle)
        return self.fetch_text(self.txt_update_tap_tittle)

    def fetch_skip_txt_from_skip_button(self):
        self.wait_for_element(self.btn_skip)
        return self.fetch_text(self.btn_skip)

    def validate_downloading_tab(self):
        self.wait_for_element(self.txt_update_tap_tittle)

    def click_on_install(self):
        self.wait_for_element(self.btn_install, time=220)
        time.sleep(5)
        self.perform_click(self.btn_install)

    def click_on_done(self):
        self.perform_click(self.btn_done, time=60)

    def click_on_update_btn(self):
        self.perform_click(self.btn_update, time=180)

    def click_on_done_2(self):
        self.perform_click(self.btn_done_2)


def get_all_file_names(directory_path):
    """
     This function gets all the file name that present in the App directory
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


def find_file_path_by_name(directory_path_to_search, file_name_to_get_path):
    """
    This function gets the path of a mpos or sa apk path
    """
    for root, _, files in os.walk(directory_path_to_search):
        if file_name_to_get_path in files:
            return os.path.join(root, file_name_to_get_path)
    return None


def install_lower_mpos_version(apps_lst: list, given_version_to_pin: str, directory_path: str, id_of_device: str):
    """
    This function compares the version the mpos app version and install the lower version the given version
    """
    logger.debug(f"list of App version :- {apps_lst}")
    for app in apps_lst:
        match = re.search(r'\d+\.\d+\.\d+', app)
        if match:
            version_number = match.group(0)
        else:
            logger.debug("No version number found")
        if version_number < given_version_to_pin:
            if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'false':
                mpos_apk_path = find_file_path_by_name(directory_path, f"MPOSX_{version_number}.apk")
            else:
                mpos_apk_path = find_file_path_by_name(directory_path, f"PAX_MPOSX_{version_number}.apk")
            subprocess.run(['adb', 'uninstall', 'com.ezetap.basicapp'])
            logger.debug('Application uninstallation done successfully.')
            install_command_lower_ver = ["adb", "-s", id_of_device, "install", "-r", "-g", mpos_apk_path]
            result = subprocess.run(install_command_lower_ver, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            if "Success" in result.stdout:
                logger.info("Application installed successfully.")
            else:
                logger.info(f"Failed to install the application: {result.stderr}")
            break


def unpining_mpos_update_version(org_code: str, given_version_to_pin: str, severity: int):
    """
      This function is used to unpin the mpos update version from a particular merchant depends on org_code
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


def pinning_mpos_version_to_merchant(org_code : str, ver_code: str, given_version_to_pin: str, severity: int):
    """
    This function is used to pin the mpos update version from a particular merchant depends on org_code
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
