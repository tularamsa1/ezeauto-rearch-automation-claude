import os
import threading
import pandas as pd
import configparser
import subprocess
import time
import paramiko
from PageFactory import Base_Actions
from appium.webdriver.appium_service import AppiumService
from DataProvider import GlobalVariables
from Utilities import ConfigReader, DirectoryCreator, ResourceAssigner

GlobalVariables.ssh = paramiko.SSHClient()
router_ip = Base_Actions.get_environment("str_exe_env_ip")  # dev11
router_username = Base_Actions.get_environment("str_ssh_username")
router_port = Base_Actions.get_environment("int_exe_env_port")
key_filename = Base_Actions.get_environment("str_ssh_key_filename")


EXCEL_reportFilePath = DirectoryCreator.getDirectoryPath("ExcelReport")+"/Report.xlsx"


def prepareTestCaseDetailsDataFrame(path):
    # Defining the columns of dataframe
    dataForDataFrameHeader = {
        'Test Case ID': [],
        'File Name': [],
        'Directory Name': [],
        'Category': [],
        'Sub-Category': [],
        'OverAll Results': [],
        'TC Execution': [],
        'API Val': [],
        'DB Val': [],
        'Portal Val': [],
        'App Val': [],
        'UI Val': [],
        'Execution Time (sec)': [],
        'Validation Time (sec)': [],
        'Log Coll Time (sec)': [],
        'Total Time (sec)': [],
        'Rerun Attempts': []
    }

    GlobalVariables.df_testCasesDetail = pd.DataFrame(dataForDataFrameHeader)

    # Dataframe by default gets created with datatype as float. Converting the same to string
    convert_dict = {'File Name': str,
                    'Directory Name': str,
                    'Category': str,
                    'Sub-Category': str,
                    'TC Execution': str,
                    'API Val': str,
                    'DB Val': str,
                    'Portal Val': str,
                    'App Val': str,
                    'UI Val': str,
                    'Rerun Attempts': str
                    }

    GlobalVariables.df_testCasesDetail = GlobalVariables.df_testCasesDetail.astype(convert_dict)

    df_overallTClist = pd.read_excel(path)
    df_overallTClist.set_index(ConfigReader.read_config("TestcaseDetails_ColumnNames", "colName_TestCaseID"), inplace=True)

    i=0
    for index in df_overallTClist.index:
        if df_overallTClist['Execute'][index] == False or str(df_overallTClist['Execute'][index]).lower() == "false":
            pass
        else:
            GlobalVariables.df_testCasesDetail.at[i, ConfigReader.read_config("TestcaseDetails_ColumnNames", "colName_TestCaseID")] = index
            GlobalVariables.df_testCasesDetail.at[i, 'File Name'] = df_overallTClist['File Name'][index]
            GlobalVariables.df_testCasesDetail.at[i, 'Directory Name'] = df_overallTClist['Directory Name'][index]
        i = i+1
    GlobalVariables.df_testCasesDetail.set_index(ConfigReader.read_config("TestcaseDetails_ColumnNames", "colName_TestCaseID"), inplace=True)
    return GlobalVariables.df_testCasesDetail


def ssh_connection(ip_address, routerPort, username, key_filename):
    GlobalVariables.ssh.load_system_host_keys()
    GlobalVariables.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        GlobalVariables.ssh.connect(ip_address, port=routerPort, username=username,
                    pkey=paramiko.RSAKey.from_private_key_file(key_filename))
        return True
    except Exception as error_message:
        print("Unable to connect")
        print(error_message)
        return False


def getValidationConfig():
    if ConfigReader.read_config("Validations", "api_validation") == True and ConfigReader.read_config("Validations", "db_validation") == True and ConfigReader.read_config("Validations", "portal_validation") == True and ConfigReader.read_config("Validations", "app_validation") == True and ConfigReader.read_config("Validations", "ui_validation") == True :
        commandString = ""
    elif ConfigReader.read_config("Validations", "api_validation") == False and ConfigReader.read_config("Validations", "db_validation") == False and ConfigReader.read_config("Validations", "portal_validation") == False and ConfigReader.read_config("Validations", "app_validation") == False and ConfigReader.read_config("Validations", "ui_validation") == False :
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
        commandString= commandString+'"'

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
            if portNumber<=4740:
                if is_port_in_use(portNumber):
                    portNumber = portNumber+1
                else:
                    try:
                        thread = threading.Thread(target = startAppiumServer, args=[portNumber])
                        thread.start()
                        blockedPorts.append(portNumber)
                        portNumber = portNumber + 1
                        foundPort = True
                    except Exception as e:
                        print(e)
                        portNumber = portNumber+1
            else:
                return blockedPorts
    return blockedPorts
"""
This method will simply create an object for the appium service and start the appium server using the inbuild method
This has been kept outside the start appium servers because this needs a separate thread to operate.
This takes an integer as input for the port number on which the server needs to be started.
"""
def startAppiumServer(portNumber:int):
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
            ListOfDevices[["device", "status"]] = ListOfDevices.devices.str.split(pat="\t",expand=True)
            DevicesList = pd.DataFrame().assign(Devices=ListOfDevices['device'], Status=ListOfDevices['status'])
            print('\n')
            #this will remove the rows with empty cells.
            DevicesList.dropna(inplace = True)
            # rows, columns = DevicesList.shape
            l2=[]
            for index, row in DevicesList.iterrows():
                if row["Status"] == "device":
                    l1 = [row["Devices"]]
                    l2.append(l1)
                else:
                    print("Device in not connected properly or "+row["Devices"]+" is unauthorized.\n")
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


def startEmulators(noOfEmulatorsToStart):
    try:
        b=1
        adb_ouput = subprocess.check_output(["emulator", "-list-avds"])
        encoding = 'utf-8'
        devices = str(adb_ouput, encoding)
        lst = (devices.split("\n"))
        emulatorsList = ' '.join(lst).split()
        emulatorsCount = len(emulatorsList)

        if noOfEmulatorsToStart <= emulatorsCount:
            for emulator in emulatorsList:
                if b <= noOfEmulatorsToStart:
                    try:
                        os.system(os.getenv("ANDROID_HOME")+"/emulator/emulator -avd "+emulator+" &")
                        print(emulator+" started successfully")
                        b += 1

                    except Exception as e:
                        print(str(e))
                else:
                    break
            time.sleep(10)
        else:
            print("Configured Emulators are less than no of processes.")
    except Exception as e:
        print(e)


def prepare_Consolidated_List_Of_TestcasesFile():
    df_all_rows = pd.DataFrame()

    if os.path.exists(ConfigReader.read_config_paths("ExcelFiles", "FilePath_TestCasesDetail")):
        workbook = pd.read_excel(ConfigReader.read_config_paths("ExcelFiles", "FilePath_TestCasesDetail"), None)
        ls_sheets_functional = workbook.keys()

        # Creating a DF with all testcases
        for sheet in ls_sheets_functional:
            df_testCasesDetail = pd.DataFrame(workbook.get(sheet))
            df_all_rows = pd.concat([df_all_rows, df_testCasesDetail])

    if os.path.exists(ConfigReader.read_config_paths("ExcelFiles", "FilePath_testcases_surfaceUI")):
        workbook = pd.read_excel(ConfigReader.read_config_paths("ExcelFiles", "FilePath_testcases_surfaceUI"), None)
        ls_sheets_surfaceUI = workbook.keys()

        # Creating a DF with all testcases
        for sheet in ls_sheets_surfaceUI:
            df_testCasesDetail = pd.DataFrame(workbook.get(sheet))
            df_all_rows = pd.concat([df_all_rows, df_testCasesDetail])

    # print("prepare_Consolidated_List_Of_TestcasesFile")
    # print(df_all_rows)
    # Converting DF with all TCs to an excel
    df_all_rows.to_excel(ConfigReader.read_config_paths("System","automation_suite_path")+"/Runtime/AllTestcaseSuite.xlsx")


def executeSelectedTestCases():
    # Creating DF only with the testcases to be executed
    df_testcases = prepareTestCaseDetailsDataFrame(ConfigReader.read_config_paths("System", "automation_suite_path")+"/Runtime/AllTestcaseSuite.xlsx")
    df_testcases.to_excel(EXCEL_reportFilePath)
    os.chdir(ConfigReader.read_config_paths("System", "automation_suite_path")+"/TestCases")
    os.system(prepareTestExecutionCommand(df_testcases))


def calculateTestCasesCountForParallelExecution():
    config = configparser.ConfigParser()
    config.read(ConfigReader.read_config_paths("System","automation_suite_path")+"/Configuration/config.ini")
    testCasesCount = config.get("ParallelExecution","NumberOfTestCases")
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
        return "-n"+str(testCasesCount)+" "



def prepareTestExecutionCommand(testCasesDetailDataFrame):

    commandString = "pytest -v -s "
    for ind in testCasesDetailDataFrame.index:
        commandString = commandString + testCasesDetailDataFrame['File Name'][ind] + ".py" + "::" + ind + " "
    commandString = commandString + getValidationConfig() +" "+calculateTestCasesCountForParallelExecution()+'--alluredir=' + DirectoryCreator.getDirectoryPath("AllureReport") + ' --capture=tee-sys'
    print(commandString)
    return commandString

def getThreadCount():
    config = configparser.ConfigParser()
    config.read(ConfigReader.read_config_paths("System","automation_suite_path")+"/Configuration/config.ini")
    testCasesCount = config.get("ParallelExecution","NumberOfTestCases")
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
            print("No physical device is connected. So cannot start the execution since device only option is configured.")
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
            startEmulators(additionalEmulatorsRequired)
        appiumServerCount = getThreadCount() + 1
    appium_server_ports = startAppiumServers(appiumServerCount)
    ResourceAssigner.clearAssignerTables()
    if devices == None:
        devices = getDevicesList()
    if devices == None :
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