import json
import chromedriver_autoinstaller
from appium import webdriver as app_webdriver
from selenium import webdriver

from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, ConfigReader


def ui_driver():
    GlobalVariables.portalDriver = chromedriver_autoinstaller.install()
    # Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument('--disable-dev-shm-usage')
    # Run chrome
    GlobalVariables.portalDriver = webdriver.Chrome(options=chrome_options)
    GlobalVariables.portalDriver.maximize_window()
    return GlobalVariables.portalDriver


def appium_driver(request):
    test_case_id = request.node.name
    device_details = ResourceAssigner.getDeviceFromDB(test_case_id)
    appium_server_details = ResourceAssigner.getAppiumServerFromDB(test_case_id)
    print(test_case_id + " will be using the device " + device_details['DeviceId'])
    print(test_case_id + " will be running on the appium server port " + appium_server_details['PortNumber'])
    mpos_app = ConfigReader.read_config_paths("System", "automation_suite_path") + "/App/" + ConfigReader.read_config(
        "Applications", "mpos")
    sa_app = ConfigReader.read_config_paths("System", "automation_suite_path") + "/App/" + ConfigReader.read_config(
        "Applications", "SA")
    lst_applications = [mpos_app, sa_app]
    json_applications = json.dumps(lst_applications)
    desired_cap = {
        "platformName": "Android",
        "deviceName": device_details['DeviceId'],
        "udid": device_details['DeviceId'],
        "otherApps": json_applications,
        "appPackage": "com.ezetap.basicapp",
        "appActivity": "com.ezetap.mposX.activity.SplashActivity",
        "ignoreHiddenApiPolicyError": "true",
        "noReset": "false",
        "isHeadless":"ture",
        "autoGrantPermissions": "true",
        "newCommandTimeout": 7000,
        "MobileCapabilityType.AUTOMATION_NAME": "AutomationName.ANDROID_UIAUTOMATOR2",
        "MobileCapabilityType.NEW_COMMAND_TIMEOUT": "300"
    }
    print("appium server url:", 'http://127.0.0.1:' + appium_server_details['PortNumber'] + '/wd/hub')
    GlobalVariables.appDriver = app_webdriver.Remote(
        'http://127.0.0.1:' + appium_server_details['PortNumber'] + '/wd/hub', desired_cap)
    return GlobalVariables.appDriver
