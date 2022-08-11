import json
from appium import webdriver as app_webdriver

from Utilities import ConfigReader


def start_app():
    device_details = {'DeviceId': 'emulator-5554'}
    appium_server_details = {'PortNumber':'4723'}
    print(" will be using the device " + device_details['DeviceId'])
    print(" will be running on the appium server port " + appium_server_details['PortNumber'])
    if str(ConfigReader.read_config("Applications", "install_apps")).lower() == 'true':
        mpos_app = "/home/ezetap-10182/Downloads/EzeAuto/App/MPOSX_10.0.100.apk"
        # mpos_app = "/home/ezetap-10182/Desktop/Nivin/Documents/APKs/MPOS/ezetap_android.apk"
        sa_app = "/home/ezetap-10182/Downloads/EzeAuto/App/SA_10.16.12.apk"
        lst_applications = [mpos_app, sa_app]
        json_applications = json.dumps(lst_applications)
    else:
        json_applications = ""
    desired_cap = {
        "platformName": "Android",
        "deviceName": device_details['DeviceId'],
        "udid": device_details['DeviceId'],
        "otherApps": json_applications,
        "appPackage": "com.ezetap.basicapp",
        "appActivity": "com.ezetap.mposX.activity.SplashActivity",
        "ignoreHiddenApiPolicyError": "true",
        "noReset": "false",
        "autoGrantPermissions": "true",
        "newCommandTimeout": 7000,
        "MobileCapabilityType.AUTOMATION_NAME": "AutomationName.ANDROID_UIAUTOMATOR2",
        "MobileCapabilityType.NEW_COMMAND_TIMEOUT": "300"
    }
    print("appium server url:", 'http://127.0.0.1:' + appium_server_details['PortNumber'] + '/wd/hub')
    appDriver = app_webdriver.Remote(
        'http://127.0.0.1:' + appium_server_details['PortNumber'] + '/wd/hub', desired_cap)
    print("installation completed")


start_app()