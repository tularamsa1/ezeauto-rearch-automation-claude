import threading

import pandas as pd
import os

from appium.webdriver.appium_service import AppiumService
from DataProvider import GlobalVariables, GlobalConstants
from Utilities import ConfigReader, DirectoryCreator

def prepareTestCaseDetailsDataFrame(path):
    # Defining the columns of dataframe

    # dataForDataFrameHeader = {
    #     'Test Case ID' : [],
    #     'File Name': [],
    #     'OverAll Results':[],
    #     'TC Execution': [],
    #     'API Val': [],
    #     'DB Val': [],
    #     'Portal Val': [],
    #     'App Val': [],
    #     'UI Val': [],
    #     'Execution Time (sec)': [],
    #     'Validation Time (sec)': [],
    #     'Log Coll Time (sec)': [],
    #     'Total Time (sec)': []
    # }

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


def prepareTestExecutionCommand(testCasesDetailDataFrame):
    # With Directory
    # commandString = commandString + testCasesDetailDataFrame['Directory Name'][ind]+ "/" +
    # testCasesDetailDataFrame['File Name'][ind] + ".py" + "::" + ind + " "

    commandString = "pytest -v -s "
    for ind in testCasesDetailDataFrame.index:
        commandString = commandString + testCasesDetailDataFrame['File Name'][ind] + ".py" + "::" + ind + " "
    # commandString = commandString + getValidationConfig() + " --html=0001dgsf.html --self-contained-html --css=test.html --tb=no --show-capture=stdout --capture=tee-sys"
    # commandString = commandString + getValidationConfig() + ' -n3 --alluredir="./march11"  --cache-clear --lf'
    commandString = commandString + getValidationConfig() + ' --alluredir='+ DirectoryCreator.getDirectoryPath("AllureReport") +' --capture=tee-sys'
    # commandString = commandString + getValidationConfig() + ' -n3 --alluredir="/home/oem/PycharmProjects/PortalAutomation_04/PortalAutomation/TestCase/allure" --capture=tee-sys'
    print(commandString)
    return commandString


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


# Added on Apr 11
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

    print("prepare_Consolidated_List_Of_TestcasesFile")
    print(df_all_rows)
    # Converting DF with all TCs to an excel
    df_all_rows.to_excel(str(ConfigReader.read_config_paths("System", "automation_suite_path") + "/TestCases/AllTestcaseSuite.xlsx"))


# Preparing Report excel
# Initiating pytest execution
def executeSelectedTestCases():
    # Creating DF only with the testcases to be executed
    df_testcases = prepareTestCaseDetailsDataFrame(str(ConfigReader.read_config_paths("System", "automation_suite_path") + "/TestCases/AllTestcaseSuite.xlsx"))
    df_testcases.to_excel(GlobalVariables.EXCEL_reportFilePath)
    os.chdir(ConfigReader.read_config_paths("System", "automation_suite_path") + "/TestCases")
    os.system(prepareTestExecutionCommand(df_testcases))



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


def killAppiumServers():
    try:
        os.system("pkill -9 -f appium")
    except Exception as e:
        print(e)