import sqlite3
import subprocess
from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

dbPath = ConfigReader.read_config_paths("System", "automation_suite_path") + "/Database/ezeauto.db"


def get_device_id():
    """
    This function will give the available device id
    return: device_id
    """
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute("SELECT DeviceId,DeviceName FROM devices WHERE Status = 'Available';")
    devices = cursor.fetchall()
    return devices[0][0]


def get_sa_app_path():
    """
    This function is used to get the sa application path
    return: sa_path
    """
    if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'true':
        sa_path = ConfigReader.read_config_paths("System",
                                                 "automation_suite_path") + "/App/" + ConfigReader.read_config(
            "Applications", "pax_SA")
        return sa_path
    else:

        sa_path = ConfigReader.read_config_paths("System",
                                                 "automation_suite_path") + "/App/" + ConfigReader.read_config(
            "Applications", "SA")

        return sa_path


def get_mpos_app_path():
    """
    This function is used to get the mpos application path
    return: mpos_path
    """
    if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'true':
        mpos_apk_path = ConfigReader.read_config_paths("System",
                                                       "automation_suite_path") + "/App/" + ConfigReader.read_config(
            "Applications", "pax_mpos")
        return mpos_apk_path
    else:
        mpos_apk_path = ConfigReader.read_config_paths("System",
                                                       "automation_suite_path") + "/App/" + ConfigReader.read_config(
            "Applications", "mpos")
        return mpos_apk_path


def check_sa_installed_or_not():
    """
     This function checks whether sa is installed or not
     return: bool value
    """
    adb_command_sa = ["adb", "shell", "pm", "list", "packages", "com.ezetap.service.demo"]
    result_sa = subprocess.run(adb_command_sa, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if "com.ezetap.service.demo" in str(result_sa.stdout):
        return "True"
    else:
        logger.info(f"SA is Not Installed with version")
        return "False"


def check_mpos_installed_or_not():
    """
    This function checks whether mpos installed or not
    return: bool values
    """
    adb_command_mpos = ["adb", "shell", "pm", "list", "packages", "com.ezetap.basicapp"]
    result = subprocess.run(adb_command_mpos, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if "com.ezetap.basicapp" in str(result.stdout):
        return "True"
    else:
        logger.info("Mpos Application is not installed")
        return "False"


def install_sa_application(id_of_devices: str, sa_path: str):
    """
    This function installs the SA application
    param: id_of_devices
    param: sa_path
    """
    install_command = ["adb", "-s", id_of_devices, "install", "-r", "-g", sa_path]
    result = subprocess.run(install_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if "Success" in result.stdout:
        logger.debug("Application installed successfully.")
    else:
        logger.debug(f"Failed to install the application: {result.stderr}")


def install_mpos_application(id_of_devices: str, mpos_apk_path: str):
    """
      This function installs the MPOS application
      param: id_of_devices
      param: mpos_apk_path
    """
    install_command = ["adb", "-s", id_of_devices, "install", "-r", "-g", mpos_apk_path]
    result = subprocess.run(install_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if "Success" in result.stdout:
        logger.debug("Application installed successfully.")
    else:
        logger.debug(f"Failed to install the application: {result.stderr}")


def uninstall_mpos_application():
    """
    This function is used to uninstall the Mpos application
    """
    subprocess.run(['adb', 'uninstall', 'com.ezetap.basicapp'])
    logger.info(f"uninstallation of Mpos is done")
