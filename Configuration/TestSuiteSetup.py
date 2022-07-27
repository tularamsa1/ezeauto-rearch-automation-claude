import configparser
import datetime
import json
import os
import subprocess
import threading
import time

import chromedriver_autoinstaller
import geckodriver_autoinstaller
import pandas as pd
import paramiko
from appium import webdriver as app_webdriver
from appium.webdriver.appium_service import AppiumService
from selenium import webdriver

from DataProvider import GlobalVariables
from PageFactory import Base_Actions
from Utilities import DirectoryCreator
from Utilities import ResourceAssigner, ConfigReader
from DataProvider.GlobalConstants import RUNTIME_DIR, DATAPROVIDER_DIR
from Utilities.android_utilities import get_the_list_of_currently_not_started_avds, start_emulator
from Utilities.execution_log_processor import EzeAutoLogger


logger = EzeAutoLogger(__name__)

GlobalVariables.ssh = paramiko.SSHClient()
router_ip = Base_Actions.get_environment("str_exe_env_ip")  # dev11
router_username = Base_Actions.get_environment("str_ssh_username")
router_port = Base_Actions.get_environment("int_exe_env_port")
key_filename = Base_Actions.get_environment("str_ssh_key_filename")

EXCEL_reportFilePath = DirectoryCreator.getDirectoryPath("ExcelReport") + "/Report.xlsx"


def prepareTestCaseDetailsDataFrame(path):
    columns = [
        'Test Case ID', 'Sub Feature Code', 'File Name', 'Directory Name', 'Category', 'Sub-Category',
        'OverAll Results',
        'TC Execution', 'API Val', 'DB Val', 'Portal Val', 'App Val', 'UI Val', 'ChargeSlip Val',
        'Execution Time (sec)', 'Validation Time (sec)', 'Log Coll Time (sec)', 'Total Time (sec)',
        'Rerun Attempts']

    df_overall_testcases_list = pd.read_excel(path, index_col=0) \
        [['Test Case ID', 'Sub Feature Code', 'File Name', 'Directory Name', 'Execute']]

    df_filtered = df_overall_testcases_list[df_overall_testcases_list.Execute == 1]

    # adding the extra columns that are not found in excel file. 
    # instead you could add those columns while first time writing the excel file
    for col in columns:
        if col not in df_filtered.columns:
            df_filtered[col] = "N/A"


    df_testCasesDetail = df_filtered.drop(columns=['Execute']).set_index("Test Case ID")
    return df_testCasesDetail  # GlobalVariables.df_testCasesDetail


# def prepareTestCaseDetailsDataFrame(path):
#     # Defining the columns of dataframe
#     dataForDataFrameHeader = {
#         'Test Case ID': [],
#         'Sub Feature Code': [],  # ==============
#         'File Name': [],
#         'Directory Name': [],
#         'Category': [],
#         'Sub-Category': [],
#         'OverAll Results': [],
#         'TC Execution': [],
#         'API Val': [],
#         'DB Val': [],
#         'Portal Val': [],
#         'App Val': [],
#         'UI Val': [],
#         'ChargeSlip Val' : [],
#         'Execution Time (sec)': [],
#         'Validation Time (sec)': [],
#         'Log Coll Time (sec)': [],
#         'Total Time (sec)': [],
#         'Rerun Attempts': []
#     }

#     GlobalVariables.df_testCasesDetail = pd.DataFrame(dataForDataFrameHeader)

#     # Dataframe by default gets created with datatype as float. Converting the same to string
#     convert_dict = {'File Name': str,  # doubts
#                     'Directory Name': str,
#                     'Category': str,
#                     'Sub-Category': str,
#                     'TC Execution': str,
#                     'API Val': str,
#                     'DB Val': str,
#                     'Portal Val': str,
#                     'App Val': str,
#                     'UI Val': str,
#                     'ChargeSlip Val': str,
#                     'Rerun Attempts': str,
#                     }

#     GlobalVariables.df_testCasesDetail = GlobalVariables.df_testCasesDetail.astype(convert_dict)

#     df_overallTClist = pd.read_excel(path)
#     df_overallTClist.set_index(ConfigReader.read_config("TestcaseDetails_ColumnNames", "colName_TestCaseID"), inplace=True)

#     i=0
#     for index in df_overallTClist.index:
#         if df_overallTClist['Execute'][index] == False or str(df_overallTClist['Execute'][index]).lower() == "false":
#             pass
#         else:
#             GlobalVariables.df_testCasesDetail.at[i, ConfigReader.read_config("TestcaseDetails_ColumnNames", "colName_TestCaseID")] = index
#             GlobalVariables.df_testCasesDetail.at[i, 'File Name'] = df_overallTClist['File Name'][index]
#             GlobalVariables.df_testCasesDetail.at[i, 'Directory Name'] = df_overallTClist['Directory Name'][index]
#         i = i+1
#     GlobalVariables.df_testCasesDetail.set_index(ConfigReader.read_config("TestcaseDetails_ColumnNames", "colName_TestCaseID"), inplace=True)
#     return GlobalVariables.df_testCasesDetail


def ssh_connection(ip_address, routerPort, username, key_filename):
    GlobalVariables.ssh.load_system_host_keys()
    GlobalVariables.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # getting ssh private key file password if it is encrypted
    try:
        ssh_private_key_password = ConfigReader.read_config("SSH", "ssh_private_key_password")
    except Exception as e:
        print(e)  # later change this is to log the warning
        ssh_private_key_password = None

    try:
        GlobalVariables.ssh.connect(ip_address, port=routerPort, username=username,
                                    pkey=paramiko.RSAKey.from_private_key_file(key_filename,
                                                                               password=ssh_private_key_password))
        return True
    except Exception as error_message:
        print("Unable to connect")
        print(error_message)
        return False


def getValidationConfig():
    if ConfigReader.read_config("Validations", "api_validation") == True and ConfigReader.read_config("Validations",
                                                                                                      "db_validation") == True and ConfigReader.read_config(
            "Validations", "portal_validation") == True and ConfigReader.read_config("Validations",
                                                                                     "app_validation") == True and ConfigReader.read_config(
            "Validations", "ui_validation") == True and ConfigReader.read_config("Validations",
                                                                                 "charge_slip_validation") == True:
        commandString = ""
    elif ConfigReader.read_config("Validations", "api_validation") == False and ConfigReader.read_config("Validations",
                                                                                                         "db_validation") == False and ConfigReader.read_config(
            "Validations", "portal_validation") == False and ConfigReader.read_config("Validations",
                                                                                      "app_validation") == False and ConfigReader.read_config(
            "Validations", "ui_validation") == False and ConfigReader.read_config("Validations",
                                                                                  "charge_slip_validation") == False:
        commandString = ""
    else:
        commandString = '-m "'
        if (ConfigReader.read_config("Validations", "api_validation")).lower() == "true":
            if commandString == '-m "':
                commandString = commandString + "apiVal"
            else:
                commandString = commandString + " or apiVal"

        if (ConfigReader.read_config("Validations", "db_validation")).lower() == "true":
            if commandString == '-m "':
                commandString = commandString + "dbVal"
            else:
                commandString = commandString + " or dbVal"
        if (ConfigReader.read_config("Validations", "portal_validation")).lower() == "true":
            if commandString == '-m "':
                commandString = commandString + "portalVal"
            else:
                commandString = commandString + " or portalVal"
        if (ConfigReader.read_config("Validations", "app_validation")).lower() == "true":
            if commandString == '-m "':
                commandString = commandString + "appVal"
            else:
                commandString = commandString + " or appVal"
        if (ConfigReader.read_config("Validations", "ui_validation")).lower() == "true":
            if commandString == '-m "':
                commandString = commandString + "uiVal"
            else:
                commandString = commandString + " or uiVal"
        if (ConfigReader.read_config("Validations", "charge_slip_validation")).lower() == "true":
            if commandString == '-m "':
                commandString = commandString + "chargeSlipVal"
            else:
                commandString = commandString + " or chargeSlipVal"
        commandString = commandString + '"'

    return commandString


"""
This method is used to start the desired number of servers.
This takes the number of servers to be started as input and returns list of ports that were actually started.
Following conditions are checked before considering a port to be assigned
i) Port number range should be between 4720 and 4740
ii) If the port is already in use.
"""


def startAppiumServers(numberOfAppiumServers: int):
    portNumber = 4720
    blockedPorts = []
    for i in range(0, numberOfAppiumServers):
        foundPort = False
        while foundPort == False:
            if portNumber <= 4740:
                if is_port_in_use(portNumber):
                    portNumber = portNumber + 1
                else:
                    try:
                        thread = threading.Thread(target=startAppiumServer, args=[portNumber])
                        thread.start()
                        blockedPorts.append(portNumber)
                        portNumber = portNumber + 1
                        foundPort = True
                    except Exception as e:
                        print(e)
                        portNumber = portNumber + 1
            else:
                return blockedPorts
    return blockedPorts


"""
This method will simply create an object for the appium service and start the appium server using the inbuild method
This has been kept outside the start appium servers because this needs a separate thread to operate.
This takes an integer as input for the port number on which the server needs to be started.
"""


def startAppiumServer(portNumber: int):
    appium_server = AppiumService()
    appium_server.start(args=['-p ' + str(portNumber)])


"""
This method is used to check the availability of the port.
It returns true if port is available and returns false in case of unavailability.
Takes an integer as input to get the port which needs to be checked.
"""


def is_port_in_use(port: int):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


"""
This method is used to kill the appium server running on a specific port
It takes the list of port numbers as input and kills the servers one by one from the list.
"""


def killEmulatorsAndAppiumServers():
    try:
        os.system("pkill -9 -f appium")
        os.system('adb devices | grep emulator | cut -f1 | while read line; do adb -s $line emu kill; done')
    except Exception as e:
        print(e)


def getDevicesList():
    try:
        adb_ouput = subprocess.check_output(["adb", "devices"])
        encoding = 'utf-8'
        devices = str(adb_ouput, encoding)
        lst = (devices.split("\n"))
        ListOfDevices = pd.DataFrame(lst)
        ListOfDevices.columns = ["devices"]

        try:
            ListOfDevices[["device", "status"]] = ListOfDevices.devices.str.split(pat="\t", expand=True)
            DevicesList = pd.DataFrame().assign(Devices=ListOfDevices['device'], Status=ListOfDevices['status'])
            print('\n')
            # this will remove the rows with empty cells.
            DevicesList.dropna(inplace=True)
            # rows, columns = DevicesList.shape
            l2 = []
            for index, row in DevicesList.iterrows():
                if row["Status"] == "device":
                    l1 = [row["Devices"]]
                    l2.append(l1)
                else:
                    print("Device in not connected properly or " + row["Devices"] + " is unauthorized.\n")
            flat_list = [item for sublist in l2 for item in sublist]
            if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == "true":
                for item in flat_list:
                    if item.__contains__("emulator"):
                        flat_list.remove(item)
            print("Available devices are: ", flat_list)
            return flat_list

        except:
            print("No physical devices connected or emulators running currently.")

    except subprocess.CalledProcessError as e:
        print("No physical devices connected or emulators running currently.")
        print(e.returncode)


def start_emulators(number_of_emulators_to_start):
    currently_not_started_avds = get_the_list_of_currently_not_started_avds()  

    for i in range(number_of_emulators_to_start):
        if currently_not_started_avds:
            avd_name = currently_not_started_avds.pop(0)  # pop will remove that avd_name from the avds list also
            logger.debug(f"Trying to start emulator with avd name '{avd_name}'")
            return_code = start_emulator(avd_name)
            
            if return_code:
                logger.error(f"Some Error [return code: {return_code}] \
                    while running shell command to start emulator '{avd_name}'")
            else:
                logger.info(f"'{avd_name}' started succesfully!")
        else:
            number_of_threads_for_which_emulators_are_unavailable = number_of_emulators_to_start - i
            logger.warning(f"No more emulators are available for next {number_of_threads_for_which_emulators_are_unavailable} threads. " +
                f"Currently only {i} emulators started. Therefore breaking the loop")
            break
    time.sleep(10)


def prepare_Consolidated_List_Of_TestcasesFile():  # later change function-name to snakecase
    input_xl_filenames = ['TestCasesDetail.xlsx', 'TestCases_SurfaceUI.xlsx']
    output_xl_filename = 'AllTestcaseSuite.xlsx'

    input_xl_filepaths = [os.path.join(DATAPROVIDER_DIR, filename) for filename in input_xl_filenames]
    output_runtime_all_tc_details_xl_url = os.path.join(RUNTIME_DIR, output_xl_filename)

    def xl_sheets_2_combined_df(input_xl_path):  # function to combine sheets of input excel file one df
        xl = pd.read_excel(input_xl_path, sheet_name=None, index_col=0) if os.path.isfile(input_xl_path) else None  # , index_col=0
        combined_excel = pd.concat([xl[key] for key in xl.keys()]) if xl else pd.DataFrame()  # concating all sheets of input excel file to one df
        combined_excel = combined_excel.reset_index()\
            .drop(
                columns=[col for col in combined_excel.columns if col.startswith("Unnamed:")])
        return combined_excel

    df =  pd.concat([xl_sheets_2_combined_df(input_xl_path) for input_xl_path in input_xl_filepaths])  # concating 2 excel files to one df
    df_filtered = df[df.Execute.isin([1, True, "True", 'true'])].reset_index(drop=False)  # .drop(columns=['Execute',])  # this should be done later
    df_filtered.drop(columns=['index','level_0'], inplace=True)
    df_filtered.to_excel(output_runtime_all_tc_details_xl_url, index=True)  # later make index=False


def executeSelectedTestCases():
    # Creating DF only with the testcases to be executed
    df_testcases = prepareTestCaseDetailsDataFrame(
        ConfigReader.read_config_paths("System", "automation_suite_path") + "/Runtime/AllTestcaseSuite.xlsx")
    df_testcases.to_excel(EXCEL_reportFilePath)
    os.chdir(ConfigReader.read_config_paths("System", "automation_suite_path") + "/TestCases")
    execution_command = prepareTestExecutionCommand(df_testcases)
    if execution_command is None:
        print("No Testcases selected for exection. Hence Execution is aborted")
    else:
        os.system(execution_command)


def calculateTestCasesCountForParallelExecution():
    config = configparser.ConfigParser()
    config.read(ConfigReader.read_config_paths("System", "automation_suite_path") + "/Configuration/config.ini")
    testCasesCount = config.get("ParallelExecution", "NumberOfTestCases")
    try:
        testCasesCount = int(testCasesCount)
        if testCasesCount < 1:
            testCasesCount = 1
        elif testCasesCount > 5:
            print("Maximum of only 5 test cases can be run in parallel.")
            testCasesCount = 5
    except Exception as e:
        print("Count of test cases is configured with a non-integer value. Hence sequential execution is initiated.")
        testCasesCount = 1
    if testCasesCount == 1:
        return ""
    else:
        return "-n" + str(testCasesCount) + " "


def prepareTestExecutionCommand(testCasesDetailDataFrame):
    commandString = "python3.8 -m pytest -v -s "
    for ind in testCasesDetailDataFrame.index:
        commandString = commandString + testCasesDetailDataFrame['File Name'][ind] + ".py" + "::" + ind + " "
    if commandString == "python3.8 -m pytest -v -s ":
        return None
    else:
        commandString = commandString + getValidationConfig() +" "+calculateTestCasesCountForParallelExecution()+'--alluredir=' + DirectoryCreator.getDirectoryPath("AllureReport") + ' --capture=tee-sys'
        print(commandString)
        return commandString


def getThreadCount():
    config = configparser.ConfigParser()
    config.read(ConfigReader.read_config_paths("System", "automation_suite_path") + "/Configuration/config.ini")
    testCasesCount = config.get("ParallelExecution", "NumberOfTestCases")
    try:
        testCasesCount = int(testCasesCount)
        if testCasesCount < 1:
            testCasesCount = 1
        elif testCasesCount > 5:
            print("Maximum of only 5 test cases can be run in parallel.")
            testCasesCount = 5
    except Exception as e:
        print("Count of test cases is configured with a non-integer value. Hence sequential execution is initiated.")
        testCasesCount = 1
    return testCasesCount


def prepareDevicesAndDB():
    global devices, appiumServerCount
    devices = getDevicesList()
    if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == "true":
        if devices == None:
            print("No physical device is connected. \
            So cannot start the execution since device only option is configured.")
            return False
        else:
            appiumServerCount = len(devices) + 1
    else:
        if devices == None:
            print("Attempting to start emulators")
            additionalEmulatorsRequired = getThreadCount()
        else:
            additionalEmulatorsRequired = getThreadCount() - len(devices)

        if (additionalEmulatorsRequired > 0):
            start_emulators(additionalEmulatorsRequired)
        appiumServerCount = getThreadCount() + 1
    appium_server_ports = startAppiumServers(appiumServerCount)
    ResourceAssigner.clearAssignerTables()
    devices = getDevicesList()
    if devices == None:
        print("Attempt to start the emulators failed.")
        print("No devices available. Hence DB update operation for adding devices is skipped.")
    else:
        ResourceAssigner.updateDevicesInDB(devices)
    ResourceAssigner.updateAppiumServersInDB(appium_server_ports)
    # lst_appUsersDetails = [{"Username": "7204644777", "Password": "A123456"}, {"Username": "7204644333", "Password": "A123456"},
    #          {"Username": "7204644666", "Password": "A123456"}]
    # portalUsersDetails = [{"Username": "7204644777", "Password": "A123456"}, {"Username": "7204644333", "Password": "A123456"},
    #             {"Username": "7204644666", "Password": "A123456"}]
    # ResourceAssigner.updateAppUsersInDB(lst_appUsersDetails)
    # ResourceAssigner.updatePortalUsersInDB(portalUsersDetails)
    return True


def initialize_portal_driver():
    """
    This method is used for initializing the chrome driver for the portal operations
    """
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


def initialize_firefox_driver():
    """
    This method is used for initializing the firefox driver.
    """
    GlobalVariables.portalDriver = geckodriver_autoinstaller.install()
    GlobalVariables.portalDriver = webdriver.Firefox()
    GlobalVariables.portalDriver.maximize_window()
    return GlobalVariables.portalDriver


def initialize_app_driver(request):
    """
    This method is used for initializing the app driver for the app operations
    """
    # test_case_id = request.node.name
    function_start_time = datetime.datetime.now()
    test_case_id = request
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
        "autoGrantPermissions": "true",
        "newCommandTimeout": 7000,
        "MobileCapabilityType.AUTOMATION_NAME": "AutomationName.ANDROID_UIAUTOMATOR2",
        "MobileCapabilityType.NEW_COMMAND_TIMEOUT": "300"
    }
    print("appium server url:", 'http://127.0.0.1:' + appium_server_details['PortNumber'] + '/wd/hub')
    GlobalVariables.appDriver = app_webdriver.Remote(
        'http://127.0.0.1:' + appium_server_details['PortNumber'] + '/wd/hub', desired_cap)
    function_end_time = datetime.datetime.now()
    print("Time taken for appium driver initialization is : ", str(function_end_time-function_start_time))
    return GlobalVariables.appDriver


