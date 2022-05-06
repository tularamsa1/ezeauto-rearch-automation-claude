import datetime
import os
from random import randint
from selenium.webdriver.chrome import webdriver
from allure_commons.types import AttachmentType
import allure
import paramiko
from selenium import webdriver
from appium import webdriver as app_webdriver
from datetime import datetime
import chromedriver_autoinstaller
from openpyxl.styles import Font, PatternFill, Side, Border

from PageFactory import Base_Actions
from Test_Setup import TestSuiteSetup
from Utilities import configReader, DirectoryCreator
from TestCases import server_logs, setUp, Rerun
#from Pages import Base_Actions
from Configuration import  Configuration
from TestCases.server_logs import env
from pathlib import Path
import openpyxl
import pytest
from DataProvider import GlobalVariables
from TestCases import ExcelProcessor
tests_count = 0
passed1 = 0
failed1 = 0
skipped1 = 0
changeHTMLVal = 0
rerunCount = 0
currentTestCase = ""
list_deselected_testcases=[]
now = datetime.now()
starting_time = now.strftime("%H:%M:%S")

# router_ip = '192.168.3.73'    #dev3
router_ip = Base_Actions.environment("ip")  # dev11
router_username = Base_Actions.environment("username")
router_port = Base_Actions.environment("port")
key_filename = Base_Actions.environment("key_filename")
ssh = paramiko.SSHClient()


@pytest.mark.hookwrapper
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    global passed1
    global failed1
    global skipped1
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    setattr(report, "duration_formatter", "%S")  # "%H:%M:%S.%f"
    setattr(item, "rep_" + report.when, report)
    report.description = str(item.function.__doc__)

    if report.outcome == "passed" and report.when == "call":
        passed1 = passed1 + 1

    if report.outcome == "failed" and report.when == "call":
        failed1 = failed1 + 1

    if report.outcome == "skipped":
        skipped1 = skipped1 + 1

    return report



def revert_excel_global_variables():
    GlobalVariables.EXCEL_TC_Exe_Starting_Time = 00
    GlobalVariables.EXCEL_TC_Exe_completed_time = 00

    GlobalVariables.EXCEL_TC_Val_Starting_Time = 00
    GlobalVariables.EXCEL_TC_Val_completed_time = 00

    GlobalVariables.EXCEL_TC_LogColl_Starting_Time = 00
    GlobalVariables.EXCEL_TC_LogColl_completed_time = 00
    GlobalVariables.EXCEL_TC_Execution = "Skip"
    GlobalVariables.EXCEL_API_Val = "N/A"
    GlobalVariables.EXCEL_DB_Val = "N/A"
    GlobalVariables.EXCEL_Portal_Val = "N/A"
    GlobalVariables.EXCEL_App_Val = "N/A"
    GlobalVariables.EXCEL_UI_Val = "N/A"


def setStylesForExcel():
    wb = openpyxl.load_workbook(GlobalVariables.EXCEL_reportFilePath)
    sheet = wb['Sheet1']

    max_row = sheet.max_row

    colNum_overall = ExcelProcessor.getColumnNumberFromName("", sheet, 'OverAll Results')
    colNum_execution = ExcelProcessor.getColumnNumberFromName("", sheet, 'TC Execution')
    colNum_apiVal = ExcelProcessor.getColumnNumberFromName("", sheet, 'API Val')
    colNum_dbVal = ExcelProcessor.getColumnNumberFromName("", sheet, 'DB Val')
    colNum_portalVal = ExcelProcessor.getColumnNumberFromName("", sheet, 'Portal Val')
    colNum_appVal = ExcelProcessor.getColumnNumberFromName("", sheet, 'App Val')
    colNum_uiVal = ExcelProcessor.getColumnNumberFromName("", sheet, 'UI Val')

    column_list = [colNum_overall, colNum_execution, colNum_apiVal, colNum_dbVal, colNum_portalVal, colNum_appVal, colNum_uiVal]

    for column in column_list:
        for row in range(2, max_row + 1):
            if sheet.cell(row, column).value == "Pass":
                sheet.cell(row, column).fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')
            elif sheet.cell(row, column).value == "Fail":
                sheet.cell(row, column).fill = PatternFill(start_color='FF6347', end_color='FF6347', fill_type='solid')

    for i in range(2, sheet.max_row + 1):
        colNum_overallStatus = ExcelProcessor.getColumnNumberFromName("", sheet, 'OverAll Results')
        if sheet.cell(row=i, column=colNum_overallStatus).value == "Broken":
            sheet.cell(row=i, column=colNum_overallStatus).fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

        if sheet.cell(row=i, column=colNum_overallStatus).value == "Deselected":
            sheet.cell(row=i, column=colNum_overallStatus).fill = PatternFill(start_color='FFA500', end_color='FFA500', fill_type='solid')



    # Set width for all cells
    sheet.column_dimensions['A'].width = 70 #Test Case ID
    sheet.column_dimensions['B'].width = 15 #File Name
    sheet.column_dimensions['C'].width = 18 #OverAll Results
    sheet.column_dimensions['D'].width = 15 #TC Execution
    sheet.column_dimensions['E'].width = 15 #API Val
    sheet.column_dimensions['F'].width = 15 #DB Val
    sheet.column_dimensions['G'].width = 15 #Portal Val
    sheet.column_dimensions['H'].width = 15 #App Val
    sheet.column_dimensions['I'].width = 15 #UI Val
    sheet.column_dimensions['J'].width = 22 #Execution Time
    sheet.column_dimensions['K'].width = 22 #Validation Time
    sheet.column_dimensions['L'].width = 20 #Log Coll Time
    sheet.column_dimensions['M'].width = 17 #Total Time


    # Set background color and font style
    fill_pattern = PatternFill(patternType='solid', fgColor='87CEEB')
    font = Font(size=11, bold=True, color="121103")

    for x in range(1, sheet.max_column):
        sheet.cell(row=1, column=x).font = font
        sheet.cell(row=1, column=x).fill = fill_pattern

    # Set border for all the cells
    side = Side(border_style="thin", color="000000")

    border = Border(left=side, right=side, top=side, bottom=side)
    for column in range(1, sheet.max_column + 1):
        for row in range(1, sheet.max_row + 1):
            sheet.cell(row, column).border = border

    wb.save(GlobalVariables.EXCEL_reportFilePath)


# @pytest.fixture(scope="session")  # Executing once before the first test case
# def session_setup(request):
#     print("Session setup level")
#     server_logs.ssh_connection(router_ip, router_port, router_username, key_filename)
#
#     # global appium_service
#     # appium_service = AppiumService()
#     # appium_service.start()
#
#     Configuration.prepareTestCaseDetailsDataFrame(configReader.read_config("ExcelFiles", "FilePath_TestCasesDetail"))
#
#     # Executing once after the last test case
#     def fin():
#         # appium_service.stop()
#         print("Session teardown level")
#         # print("Session Teardown rerunAttempt count is: ", dictFromCsv.get("rerunAttempt"))
#         print("Printing df before starting rerun")
#
#         ssh.close()
#         # appium_service.stop()
#         convert_DF_To_Excel()
#
#     request.addfinalizer(fin)


def convert_DF_To_Excel():
    i = randint(1, 10)
    # file_name = 'MarksData'+str(i)+'.xlsx'
    file_name = 'MarksData.xlsx'

    for ind in GlobalVariables.df_testCasesDetail.index:
        testcase_Execution_value = (GlobalVariables.df_testCasesDetail['TC Execution'][ind])

        if testcase_Execution_value != testcase_Execution_value:  # the value is NaN
            GlobalVariables.df_testCasesDetail.at[ind, 'TC Execution'] = "Deselected"
            GlobalVariables.df_testCasesDetail.at[ind, 'API Val'] = "N/A"
            GlobalVariables.df_testCasesDetail.at[ind, 'DB Val'] = "N/A"
            GlobalVariables.df_testCasesDetail.at[ind, 'Portal Val'] = "N/A"
            GlobalVariables.df_testCasesDetail.at[ind, 'App Val'] = "N/A"
            GlobalVariables.df_testCasesDetail.at[ind, 'UI Val'] = "N/A"
            GlobalVariables.df_testCasesDetail.at[ind, 'Execution Time (sec)'] = 0.0
            GlobalVariables.df_testCasesDetail.at[ind, 'Validation Time (sec)'] = 0.0
            GlobalVariables.df_testCasesDetail.at[ind, 'Log Coll Time (sec)'] = 0.0
            GlobalVariables.df_testCasesDetail.at[ind, 'Total Time (sec)'] = 0.0
    # Converting to excel from DF
    GlobalVariables.df_testCasesDetail.to_excel(file_name)


def startLineNoOfServerLogFile():
    if Base_Actions.enter_data_logs("For_Passed_TCS_fetch_Logs") == "True" or Base_Actions.enter_data_logs(
            "For_Failed_TCS_fetch_Logs") == "True":
        global LogCollTime
        current = datetime.now()
        LogColl_Starting_Time = current.strftime("%H:%M:%S")
        if env.__contains__('dev'):
            if Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                GlobalVariables.startLineNumberAPI = server_logs.noOfLine(Base_Actions.pathToLogFile('api_dev'))
                print("Start startLineNumberAPI no: ", GlobalVariables.startLineNumberAPI)
            if Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                GlobalVariables.startLineNumberPortal = server_logs.noOfLine(Base_Actions.pathToLogFile('portal_dev'))
            if Base_Actions.enter_data_logs("fetch_middleware_Logs") == "True":
                GlobalVariables.startLineNumberMiddlewware = server_logs.noOfLine(
                    Base_Actions.pathToLogFile('middleware_dev'))
            if Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                GlobalVariables.startLineNumberCnpware = server_logs.noOfLine(Base_Actions.pathToLogFile('cnpware_dev'))
        else:
            if Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                GlobalVariables.startLineNumberAPI = server_logs.noOfLine(Base_Actions.pathToLogFile('api'))
            if Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                GlobalVariables.startLineNumberPortal = server_logs.noOfLine(Base_Actions.pathToLogFile('portal'))
            if Base_Actions.enter_data_logs("fetch_middleware_Logs") == "True":
                GlobalVariables.startLineNumberMiddlewware = server_logs.noOfLine(
                    Base_Actions.pathToLogFile('middleware'))
            if Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                GlobalVariables.startLineNumberCnpware = server_logs.noOfLine(Base_Actions.pathToLogFile('cnpware'))

        current = datetime.now()
        LogColl_Ending_Time = current.strftime("%H:%M:%S")
        FMT = '%H:%M:%S'
        totalLogCollectionTime = datetime.strptime(LogColl_Ending_Time, FMT) - datetime.strptime(
            str(LogColl_Starting_Time),
            FMT)
        print("Portal logs coll time: ", str(totalLogCollectionTime))
        # Converting time duration to seconds
        LogCollTime = sum(x * int(t) for x, t in zip([3600, 60, 1], str(totalLogCollectionTime).split(":")))


def updatingHighLevelReportAfterEachTCS():
    workbook = openpyxl.load_workbook(GlobalVariables.EXCEL_reportFilePath)
    sheet = workbook["Sheet1"]
    GlobalVariables.EXCEL_testCaseName = os.environ.get('PYTEST_CURRENT_TEST').replace(" (teardown)", '').split('::')[1]
    print("Testcase name", GlobalVariables.EXCEL_testCaseName)
    print("Exec time: ", GlobalVariables.EXCEL_Tot_Time)
    Overall_Status = 'Broken'
    if GlobalVariables.EXCEL_TC_Execution == 'Pass':

        # Pass or N/A
        if GlobalVariables.EXCEL_API_Val != 'Fail' and GlobalVariables.EXCEL_DB_Val != 'Fail' and GlobalVariables.EXCEL_Portal_Val != 'Fail' and GlobalVariables.EXCEL_UI_Val != 'Fail':
            Overall_Status = 'Pass'

        elif GlobalVariables.EXCEL_API_Val == 'Fail' or GlobalVariables.EXCEL_DB_Val == 'Fail' or GlobalVariables.EXCEL_Portal_Val == 'Fail' or GlobalVariables.EXCEL_UI_Val == 'Fail':
            Overall_Status = 'Fail'
    elif GlobalVariables.EXCEL_TC_Execution == 'Fail':
        Overall_Status = 'Fail'
    rowNumber = ExcelProcessor.getRowNumberFromValue(workbook, sheet, 'Test Case ID',
                                                     GlobalVariables.EXCEL_testCaseName)

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'File Name')
    GlobalVariables.EXCEL_testCaseFileName = sheet.cell(row=rowNumber, column=columnNumber).value

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'OverAll Results')
    sheet.cell(row=rowNumber, column=columnNumber).value = Overall_Status

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'TC Execution')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_TC_Execution

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'API Val')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_API_Val
    print("API VaL: ", GlobalVariables.EXCEL_API_Val)

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'DB Val')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_DB_Val
    print("DB VaL: ", GlobalVariables.EXCEL_DB_Val)

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'Portal Val')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_Portal_Val
    print("Portal VaL: ", GlobalVariables.EXCEL_Portal_Val)

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'App Val')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_App_Val
    print("App VaL: ", GlobalVariables.EXCEL_App_Val)

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'UI Val')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_UI_Val
    print("UI VaL: ", GlobalVariables.EXCEL_UI_Val)

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'Execution Time (sec)')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_Execution_Time

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'Validation Time (sec)')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_Val_time

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'Log Coll Time (sec)')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_LogCollTime

    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'Total Time (sec)')
    sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_Tot_Time

    # Added on Apr 11
    # To add the rerun count after every executed testcases
    # if rerun_at_the_end & rerun_immediately are enabled, rerun_at_the_end will be considered
    # if (rerun_at_the_end is TRUE) OR (rerun_at_the_end & rerun_immediately are TRUE)
    if (configReader.read_config("Validations", "rerun_at_the_end").lower() == "true" and configReader.read_config(
            "Validations", "rerun_immediately").lower() == "false") \
            or (
            configReader.read_config("Validations", "rerun_at_the_end").lower() == "true" and configReader.read_config(
        "Validations", "rerun_immediately").lower() == "true"):
        columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'Rerun Attempts')

        if sheet.cell(row=rowNumber, column=columnNumber).value is None:
            sheet.cell(row=rowNumber, column=columnNumber).value = 0
        else:

            currentRetryCountsheet = sheet.cell(row=rowNumber, column=columnNumber).value
            sheet.cell(row=rowNumber, column=columnNumber).value = currentRetryCountsheet + 1
    # =====================================================================================

    workbook.save(GlobalVariables.EXCEL_reportFilePath)
    workbook.close()

@pytest.fixture(scope="function")  # Executing once before every testcases
def method_setup(request):
    # breakpoint()
    print("Function setup level")

    startLineNoOfServerLogFile()

    current = datetime.now()
    GlobalVariables.EXCEL_TC_Exe_Starting_Time = current.strftime("%H:%M:%S")

    # breakpoint()
    print("***************End of setup")

    # Executing once AFTER every testcases
    def fin():
        print("Function teardown level")
        # Write data to dataframe
        # write_TC_Details_To_Dataframe()

        if Rerun.getRerunCountForAtTheEnd() == 0 and Base_Actions.enter_data_logs("forLastRun_Capture_Logs") == "True":
            # breakpoint()
            print("Rerun.getRerunCountForAtTheEnd(): ", Rerun.getRerunCountForAtTheEnd())
            print("log_on_failure(request)")
            log_on_failure(request)

        if configReader.read_config("Validations",
                                    "rerun_at_the_end").lower() == "true" and Base_Actions.enter_data_logs(
                "forEachRun_Capture_Logs") == "True":
            log_on_failure(request)

        global LogCollTime
        GlobalVariables.EXCEL_LogCollTime = LogCollTime + GlobalVariables.EXCEL_LogCollTime
        GlobalVariables.EXCEL_Tot_Time = int(GlobalVariables.EXCEL_Execution_Time) + int(
            GlobalVariables.EXCEL_Val_time) + int(GlobalVariables.EXCEL_LogCollTime)

        updatingHighLevelReportAfterEachTCS()

        # rerunCount = Rerun.getRerunCount(GlobalVariables.EXCEL_testCaseName)
        if configReader.read_config("Validations", "rerun_immediately").lower() == "true" and Rerun.isRerunRequiredImmediately(GlobalVariables.EXCEL_testCaseName) \
                and configReader.read_config("Validations", "rerun_at_the_end").lower() == "false":

            # Added on Apr 11
            rerunCount = Rerun.getRerunCount(GlobalVariables.EXCEL_testCaseName)

            if Base_Actions.enter_data_logs("forEachRun_Capture_Logs") == "True":
                log_on_failure(request)
            if rerunCount >= 0:
                print(str(rerunCount) + " reruns pending for the test case " + GlobalVariables.EXCEL_testCaseName)
                rerunCount -= 1
                # Rerun.rerunTestImmediately(GlobalVariables.EXCEL_testCaseName, GlobalVariables.EXCEL_testCaseFileName, rerunCount)
                Rerun.rerunTestImmediately(GlobalVariables.EXCEL_testCaseName, GlobalVariables.EXCEL_testCaseFileName,
                                           rerunCount, request)
            else:
                print(str(rerunCount) + " reruns pending for the test case " + GlobalVariables.EXCEL_testCaseName)
                print("Rerun skipped.")

        # Reverting all the global variables back to default values
        # print("Printing portal driver before if condition: ", GlobalVariables.portalDriver)
        # print("Function teardown after rerun method")
        # if GlobalVariables.portalDriver != '':
        #     print("Printing portal driver: ", GlobalVariables.portalDriver)
        #     # GlobalVariables.portalDriver.quit()
        #     GlobalVariables.portalDriver.close()
        #     GlobalVariables.portalDriver = ''
        #     # variables.successApp = False
        # if GlobalVariables.appDriver != '':
        #     GlobalVariables.appDriver.quit()
        #     GlobalVariables.appDriver = ''
        revert_excel_global_variables()

    request.addfinalizer(fin)

def write_TC_Details_To_Dataframe():
    # breakpoint()
    print("################", GlobalVariables.EXCEL_Portal_Val)
    TestCaseName = os.environ.get('PYTEST_CURRENT_TEST').replace(" (teardown)", '').replace("test_sample.py::",
                                                                                            '').replace("TestCase/", '')
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'TC Execution'] = GlobalVariables.EXCEL_TC_Execution
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'API Val'] = GlobalVariables.EXCEL_API_Val
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'DB Val'] = GlobalVariables.EXCEL_DB_Val
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Portal Val'] = GlobalVariables.EXCEL_Portal_Val
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'App Val'] = GlobalVariables.EXCEL_App_Val
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'UI Val'] = GlobalVariables.EXCEL_UI_Val
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Execution Time (sec)'] = GlobalVariables.EXCEL_Execution_Time
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Validation Time (sec)'] = GlobalVariables.EXCEL_Val_time
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Log Coll Time (sec)'] = GlobalVariables.EXCEL_LogCollTime
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Total Time (sec)'] = GlobalVariables.EXCEL_Tot_Time


@pytest.fixture(scope="function")
def ui_driver(request):
    GlobalVariables.portalDriver = chromedriver_autoinstaller.install()
    # Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument('--disable-dev-shm-usage')
    # Run chrome
    GlobalVariables.portalDriver = webdriver.Chrome(options=chrome_options)
    GlobalVariables.portalDriver.maximize_window()


@pytest.fixture(scope="function")
def appium_driver():
    desired_cap = {
        "platformName": "Android",
        "deviceName": "0821045404",
        "udid": "0821045404",
        "appPackage": "com.ezetap.basicapp",
        "appActivity": "com.ezetap.mposX.activity.SplashActivity",
        "ignoreHiddenApiPolicyError": "true",
        "noReset": "true",
        "autoGrantPermissions": "true",
        "MobileCapabilityType.AUTOMATION_NAME": "AutomationName.ANDROID_UIAUTOMATOR2"
    }
    GlobalVariables.appDriver = app_webdriver.Remote("http://localhost:4723/wd/hub", desired_cap)
    GlobalVariables.appDriver.implicitly_wait(30)

def pytest_deselected(items):
    print("INSIDE DESELCTED METHOD")
    global list_deselected_testcases
    for item in items:
        print(item.nodeid)
        testcase = str((item.nodeid)).split('::')[1]
        list_deselected_testcases.append(testcase)


def updateExcel_With_Deselect_And_Broken():
    wb = openpyxl.load_workbook(GlobalVariables.EXCEL_reportFilePath)
    sheet = wb['Sheet1']

    for i in range(2, sheet.max_row + 1):
        colNum_testcase = ExcelProcessor.getColumnNumberFromName("", sheet, 'Test Case ID')
        testcase = (sheet.cell(row=i, column=colNum_testcase)).value
        if testcase in list_deselected_testcases:

            colNum_overallStatus = ExcelProcessor.getColumnNumberFromName("", sheet, 'OverAll Results')
            sheet.cell(row=i, column=colNum_overallStatus).value = "Deselected"

            colNum_execution = ExcelProcessor.getColumnNumberFromName("", sheet, 'TC Execution')
            sheet.cell(row=i, column=colNum_execution).value = "N/A"

            colNum_APIval = ExcelProcessor.getColumnNumberFromName("", sheet, 'API Val')
            sheet.cell(row=i, column=colNum_APIval).value = "N/A"

            colNum_DBval = ExcelProcessor.getColumnNumberFromName("", sheet, 'DB Val')
            sheet.cell(row=i, column=colNum_DBval).value = "N/A"

            colNum_PortalVal = ExcelProcessor.getColumnNumberFromName("", sheet, 'Portal Val')
            sheet.cell(row=i, column=colNum_PortalVal).value = "N/A"

            colNum_AppVal = ExcelProcessor.getColumnNumberFromName("", sheet, 'App Val')
            sheet.cell(row=i, column=colNum_AppVal).value = "N/A"

            colNum_UIval = ExcelProcessor.getColumnNumberFromName("", sheet, 'UI Val')
            sheet.cell(row=i, column=colNum_UIval).value = "N/A"

        else:
            colNum_overallResult = ExcelProcessor.getColumnNumberFromName("", sheet, 'OverAll Results')
            cellValue = (sheet.cell(row=i, column=colNum_overallResult)).value
            if cellValue is None:
                colNum_overallStatus = ExcelProcessor.getColumnNumberFromName("", sheet, 'OverAll Results')
                sheet.cell(row=i, column=colNum_overallStatus).value = "Broken"

                colNum_execution = ExcelProcessor.getColumnNumberFromName("", sheet, 'TC Execution')
                sheet.cell(row=i, column=colNum_execution).value = "N/A"

                colNum_APIval = ExcelProcessor.getColumnNumberFromName("", sheet, 'API Val')
                sheet.cell(row=i, column=colNum_APIval).value = "N/A"

                colNum_DBval = ExcelProcessor.getColumnNumberFromName("", sheet, 'DB Val')
                sheet.cell(row=i, column=colNum_DBval).value = "N/A"

                colNum_PortalVal = ExcelProcessor.getColumnNumberFromName("", sheet, 'Portal Val')
                sheet.cell(row=i, column=colNum_PortalVal).value = "N/A"

                colNum_AppVal = ExcelProcessor.getColumnNumberFromName("", sheet, 'App Val')
                sheet.cell(row=i, column=colNum_AppVal).value = "N/A"

                colNum_UIval = ExcelProcessor.getColumnNumberFromName("", sheet, 'UI Val')
                sheet.cell(row=i, column=colNum_UIval).value = "N/A"

    wb.save(GlobalVariables.EXCEL_reportFilePath)


def log_on_failure(request):
    item = request.node
    if item.rep_call.failed and Base_Actions.enter_data_logs("For_Failed_TCS_fetch_Logs") == "True":
        current = datetime.now()
        GlobalVariables.EXCEL_TC_LogColl_Starting_Time = current.strftime("%H:%M:%S")

        print("In logOnFailure Portal logs coll starting time: ", str(GlobalVariables.EXCEL_TC_LogColl_Starting_Time))

        if Base_Actions.enter_data_logs("capturing_indivisually_Logs") == "True" and Base_Actions.enter_data_logs(
                "forLastRun_Capture_Logs") == "True":

            testCaseID = str(item.nodeid).split('/')
            finalTestCaseID = testCaseID[len(testCaseID) - 1]
            logFileName = str(finalTestCaseID).split('::')[1]
            #logFileName = str(finalTestCaseID).replace("::", "_")

            #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName
            path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
            Path(path).mkdir(parents=True, exist_ok=True)
            print("Fetching Logs first time")

            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
            TCIdWithTimeStampForInsideFile = str(datetime.now().time())

            if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                apiLogs = server_logs.fetchAPILogs()
                rerun_file = Path(path + "/api.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                portalLogs = server_logs.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs("fetch_middleware_Logs") == "True":
                mwareLogs = server_logs.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                cnpWareLogs = server_logs.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

        if Base_Actions.enter_data_logs("capturing_indivisually_Logs") == "True" and Base_Actions.enter_data_logs(
                "forEachRun_Capture_Logs") == "True" and configReader.read_config("Validations",
                                                                                  "rerun_at_the_end").lower() == "true":
            i = int(configReader.read_config("Validations", "rerun_count"))
            j = 0
            print("Fetching Logs 2nd time")

            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

            # Added on 26 Apr
            testCaseID = str(item.nodeid).split('/')
            finalTestCaseID = testCaseID[len(testCaseID) - 1]
            logFileName = str(finalTestCaseID).split('::')[1]
            #logFileName = str(finalTestCaseID).replace("::", "_")

            while i >= 0 and j <= int(configReader.read_config("Validations", "rerun_count")):
                if Rerun.getRerunCountForAtTheEnd() == i:
                    # Added on 26 Apr
                    path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
                    #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName

                    Path(path).mkdir(parents=True, exist_ok=True)

                    if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                        apiLogs = server_logs.fetchAPILogs()
                        rerun_file = Path(path + "/api_Rerun.log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                    if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                        portalLogs = server_logs.fetchPortalLogs()
                        rerun_file = Path(path + "/portal_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                    if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs(
                            "fetch_middleware_Logs") == "True":
                        mwareLogs = server_logs.fetchMiddlewareLogs()
                        rerun_file = Path(
                            path + "/middleware_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                    if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                        cnpWareLogs = server_logs.fetchCnpwareLogs()
                        rerun_file = Path(path + "/cnpware_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                i -= 1
                j += 1

        if Base_Actions.enter_data_logs("capturing_indivisually_Logs") == "True" and Base_Actions.enter_data_logs(
                "forEachRun_Capture_Logs") == "True" and configReader.read_config("Validations",
                                                                                  "rerun_immediately").lower() == "true":

            i = int(configReader.read_config("Validations", "rerun_count"))
            j = 0
            print("Fetching Logs 3rd time")

            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

            # Added on 26 Apr
            testCaseID = str(item.nodeid).split('/')
            finalTestCaseID = testCaseID[len(testCaseID) - 1]
            logFileName = str(finalTestCaseID).split('::')[1]
            #logFileName = str(finalTestCaseID).replace("::", "_")

            while i >= 0 and j <= int(configReader.read_config("Validations", "rerun_count")):
                if Rerun.getRerunCount(str(item.nodeid).split('::')[1]) == i:

                    #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName
                    path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
                    Path(path).mkdir(parents=True, exist_ok=True)

                    if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                        apiLogs = server_logs.fetchAPILogs()
                        rerun_file = Path(path + "/api_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                    if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                        portalLogs = server_logs.fetchPortalLogs()
                        rerun_file = Path(path + "/portal_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                    if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs(
                            "fetch_middleware_Logs") == "True":
                        mwareLogs = server_logs.fetchMiddlewareLogs()
                        rerun_file = Path(
                            path + "/middleware_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                    if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                        cnpWareLogs = server_logs.fetchCnpwareLogs()
                        rerun_file = Path(path + "/cnpware_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                i -= 1
                j += 1

        if Base_Actions.enter_data_logs("capturing_allInOneFile_Logs") == "True" and Base_Actions.enter_data_logs(
                "forLastRun_Capture_Logs") == "True":
            path = DirectoryCreator.getDirectoryPath("ServerLog")+"/"
            #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/"
            print("Inside capturing logs all in one file")
            print("Fetching Logs 4th time")

            Path(path).mkdir(parents=True, exist_ok=True)
            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
            if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                apiLogs = server_logs.fetchAPILogs()
                rerun_file = Path(path + "/api.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                portalLogs = server_logs.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs("fetch_middleware_Logs") == "True":
                mwareLogs = server_logs.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                cnpWareLogs = server_logs.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

        if Base_Actions.enter_data_logs("capturing_allInOneFile_Logs") == "True" and Base_Actions.enter_data_logs(
                "forEachRun_Capture_Logs") == "True":
            path = DirectoryCreator.getDirectoryPath("ServerLog")+"/"
            #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/"
            print("Inside capturing logs all in one file")
            print("Fetching Logs 5th time")

            Path(path).mkdir(parents=True, exist_ok=True)
            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
            if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                apiLogs = server_logs.fetchAPILogs()
                print("TCIdWithTimeStamp", TCIdWithTimeStamp)
                rerun_file = Path(path + "/api.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                portalLogs = server_logs.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs("fetch_middleware_Logs") == "True":
                mwareLogs = server_logs.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                cnpWareLogs = server_logs.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

        setUp.get_Log_Collection_Time()

        if GlobalVariables.successApp == 'Failed' and GlobalVariables.appDriver != '':
            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                          attachment_type=AttachmentType.PNG)
            GlobalVariables.successApp = 'Passed'

        if GlobalVariables.successPortal == 'Failed' and GlobalVariables.portalDriver != '':
            allure.attach(GlobalVariables.portalDriver.get_screenshot_as_png(), name="screenshot",
                          attachment_type=AttachmentType.PNG)
            GlobalVariables.successPortal = 'Passed'

        if GlobalVariables.portalDriver != '':
            # GlobalVariables.portalDriver.quit()
            GlobalVariables.portalDriver.close()
            GlobalVariables.portalDriver = ''
            # variables.successApp = False

        if GlobalVariables.appDriver != '':
            GlobalVariables.appDriver.quit()
            GlobalVariables.appDriver = ''
            # variables.appSS = False

        GlobalVariables.successPortal = "N/A"
        GlobalVariables.successApp = "N/A"


@pytest.fixture(scope='function')
def log_on_success(request):
    yield
    item = request.node

    if item.rep_call.passed and Base_Actions.enter_data_logs("For_Passed_TCS_fetch_Logs") == "True":
        current = datetime.now()
        GlobalVariables.EXCEL_TC_LogColl_Starting_Time = current.strftime("%H:%M:%S")

        print("In logOnSuccess Portal logs coll starting time: ", str(GlobalVariables.EXCEL_TC_LogColl_Starting_Time))

        if Base_Actions.enter_data_logs("capturing_indivisually_Logs") == "True" and Base_Actions.enter_data_logs(
                "forLastRun_Capture_Logs") == "True":

            testCaseID = str(item.nodeid).split('/')
            finalTestCaseID = testCaseID[len(testCaseID) - 1]
            logFileName = str(finalTestCaseID).split('::')[1]
            #logFileName = str(finalTestCaseID).replace("::", "_")

            path = DirectoryCreator.getDirectoryPath("ServerLog")+"/"+ logFileName
  #          path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName
            Path(path).mkdir(parents=True, exist_ok=True)
            print("Fetching Logs first time")

            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
            TCIdWithTimeStampForInsideFile = str(datetime.now().time())

            if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                apiLogs = server_logs.fetchAPILogs()
                rerun_file = Path(path + "/api.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                portalLogs = server_logs.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs("fetch_middleware_Logs") == "True":
                mwareLogs = server_logs.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                cnpWareLogs = server_logs.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

        if Base_Actions.enter_data_logs("capturing_indivisually_Logs") == "True" and Base_Actions.enter_data_logs(
                "forEachRun_Capture_Logs") == "True" and configReader.read_config("Validations",
                                                                                  "rerun_at_the_end").lower() == "true":
            i = int(configReader.read_config("Validations", "rerun_count"))
            j = 0
            print("Fetching Logs 2nd time")

            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

            # Added on 26 Apr
            testCaseID = str(item.nodeid).split('/')
            finalTestCaseID = testCaseID[len(testCaseID) - 1]
            logFileName = str(finalTestCaseID).split('::')[1]
            #logFileName = str(finalTestCaseID).replace("::", "_")

            while i >= 0 and j <= int(configReader.read_config("Validations", "rerun_count")):
                if Rerun.getRerunCountForAtTheEnd() == i:
                    # Added on 26 Apr
                    path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
                    #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName

                    Path(path).mkdir(parents=True, exist_ok=True)

                    if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                        apiLogs = server_logs.fetchAPILogs()
                        rerun_file = Path(path + "/api_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                    if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                        portalLogs = server_logs.fetchPortalLogs()
                        rerun_file = Path(path + "/portal_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                    if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs(
                            "fetch_middleware_Logs") == "True":
                        mwareLogs = server_logs.fetchMiddlewareLogs()
                        rerun_file = Path(
                            path + "/middleware_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                    if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                        cnpWareLogs = server_logs.fetchCnpwareLogs()
                        rerun_file = Path(path + "/cnpware_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                i -= 1
                j += 1

        if Base_Actions.enter_data_logs("capturing_indivisually_Logs") == "True" and Base_Actions.enter_data_logs(
                "forEachRun_Capture_Logs") == "True" and configReader.read_config("Validations",
                                                                                  "rerun_immediately").lower() == "true":

            i = int(configReader.read_config("Validations", "rerun_count"))
            j = 0
            print("Fetching Logs 3rd time")

            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

            # Added on 26 Apr
            testCaseID = str(item.nodeid).split('/')
            finalTestCaseID = testCaseID[len(testCaseID) - 1]
            logFileName = str(finalTestCaseID).split('::')[1]
           # logFileName = str(finalTestCaseID).replace("::", "_")

            while i >= 0 and j <= int(configReader.read_config("Validations", "rerun_count")):
                if Rerun.getRerunCount(str(item.nodeid).split('::')[1]) == i:

                    #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName
                    path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
                    Path(path).mkdir(parents=True, exist_ok=True)

                    if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                        apiLogs = server_logs.fetchAPILogs()
                        rerun_file = Path(path + "/api_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                    if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                        portalLogs = server_logs.fetchPortalLogs()
                        rerun_file = Path(path + "/portal_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                    if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs(
                            "fetch_middleware_Logs") == "True":
                        mwareLogs = server_logs.fetchMiddlewareLogs()
                        rerun_file = Path(
                            path + "/middleware_" + str(datetime.now().time()) + "_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                    if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                        cnpWareLogs = server_logs.fetchCnpwareLogs()
                        rerun_file = Path(path + "/cnpware_Rerun_" + str(j) + ".log")
                        server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                i -= 1
                j += 1

        if Base_Actions.enter_data_logs("capturing_allInOneFile_Logs") == "True" and Base_Actions.enter_data_logs(
                "forLastRun_Capture_Logs") == "True":
            path = DirectoryCreator.getDirectoryPath("ServerLog") + "/"
            #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/"
            print("Inside capturing logs all in one file")
            print("Fetching Logs 4th time")

            Path(path).mkdir(parents=True, exist_ok=True)
            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
            if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                apiLogs = server_logs.fetchAPILogs()
                rerun_file = Path(path + "/api.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                portalLogs = server_logs.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs("fetch_middleware_Logs") == "True":
                mwareLogs = server_logs.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                cnpWareLogs = server_logs.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

        if Base_Actions.enter_data_logs("capturing_allInOneFile_Logs") == "True" and Base_Actions.enter_data_logs(
                "forEachRun_Capture_Logs") == "True":
            path = DirectoryCreator.getDirectoryPath("ServerLog") + "/"
            #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/"
            print("Inside capturing logs all in one file")
            print("Fetching Logs 5th time")

            Path(path).mkdir(parents=True, exist_ok=True)
            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
            if GlobalVariables.apiLogs and Base_Actions.enter_data_logs("fetch_api_Logs") == "True":
                apiLogs = server_logs.fetchAPILogs()
                print("TCIdWithTimeStamp", TCIdWithTimeStamp)
                rerun_file = Path(path + "/api.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.enter_data_logs("fetch_portal_Logs") == "True":
                portalLogs = server_logs.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.enter_data_logs("fetch_middleware_Logs") == "True":
                mwareLogs = server_logs.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True":
                cnpWareLogs = server_logs.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                server_logs.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

        setUp.get_Log_Collection_Time()

        if GlobalVariables.successApp == 'Passed' and GlobalVariables.appDriver != '':
            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                          attachment_type=AttachmentType.PNG)
            GlobalVariables.successApp = 'Passed'

        if GlobalVariables.successPortal == 'Passed' and GlobalVariables.portalDriver != '':
            allure.attach(GlobalVariables.portalDriver.get_screenshot_as_png(), name="screenshot",
                          attachment_type=AttachmentType.PNG)
            GlobalVariables.successPortal = 'Passed'

        if GlobalVariables.portalDriver != '':
            # GlobalVariables.portalDriver.quit()
            GlobalVariables.portalDriver.close()
            GlobalVariables.portalDriver = ''
            # variables.successApp = False

        if GlobalVariables.appDriver != '':
            GlobalVariables.appDriver.quit()
            GlobalVariables.appDriver = ''
            # variables.appSS = False

        GlobalVariables.successPortal = "N/A"
        GlobalVariables.successApp = "N/A"


def pytest_sessionstart(session):
    print("Session setup level")
    TestSuiteSetup.ssh_connection(router_ip, router_port, router_username, key_filename)



def pytest_sessionfinish(session, exitstatus):
    updateExcel_With_Deselect_And_Broken()
    setStylesForExcel()
    print("Session teardown level")

    # Added on Apr 11
    updateExcel_With_Category_And_Subcategory()
    updateExcel_With_RerunAttempts()

    ssh.close()
    # appium_service.stop()
    
# Added on Apr 11
def updateExcel_With_RerunAttempts():
    wb = openpyxl.load_workbook(GlobalVariables.EXCEL_reportFilePath)
    sheet = wb['Sheet1']

    if configReader.read_config("Validations", "rerun_immediately").lower() == "true" and configReader.read_config(
            "Validations", "rerun_at_the_end").lower() == "false":
        colNum_rerunAttempts = ExcelProcessor.getColumnNumberFromName("", sheet, 'Rerun Attempts')
        for i in range(2, sheet.max_row + 1):
            colNum_testcase = ExcelProcessor.getColumnNumberFromName("", sheet, 'Test Case ID')
            testcase = (sheet.cell(row=i, column=colNum_testcase)).value

            rerunCount = Rerun.getRerunCount(testcase)
            if rerunCount >= 0:
                cellValue_rerunAttempts = int(configReader.read_config("Validations", "rerun_count")) - rerunCount
                sheet.cell(row=i, column=colNum_rerunAttempts).value = cellValue_rerunAttempts
            else:
                cellValue_rerunAttempts = configReader.read_config("Validations", "rerun_count")
                sheet.cell(row=i, column=colNum_rerunAttempts).value = int(cellValue_rerunAttempts)

    # If both rerun_at_the_end and rerun_immediately are disabled, setting value as N/A for Rerun Attempts
    if configReader.read_config("Validations", "rerun_at_the_end").lower() == "false" and configReader.read_config(
            "Validations", "rerun_immediately").lower() == "false":
        colNum_RerunAttempts = ExcelProcessor.getColumnNumberFromName("", sheet, 'Rerun Attempts')
        for i in range(2, sheet.max_row + 1):
            sheet.cell(row=i, column=colNum_RerunAttempts).value = "N/A"

    wb.save(GlobalVariables.EXCEL_reportFilePath)


# Added on Apr 11
def updateExcel_With_Category_And_Subcategory():
    wb = openpyxl.load_workbook(GlobalVariables.EXCEL_reportFilePath)
    sheet = wb['Sheet1']

    for i in range(2, sheet.max_row + 1):
        colNum_directoryName = ExcelProcessor.getColumnNumberFromName("", sheet, 'Directory Name')
        directoryName = (sheet.cell(row=i, column=colNum_directoryName)).value

        category = directoryName.split("/")[0]
        subCategory = directoryName.split("/")[1]

        colNum_category = ExcelProcessor.getColumnNumberFromName("", sheet, 'Category')
        colNum_subCategory = ExcelProcessor.getColumnNumberFromName("", sheet, 'Sub-Category')

        cellValue_category = (sheet.cell(row=i, column=colNum_category)).value
        cellValue_subCategory = (sheet.cell(row=i, column=colNum_subCategory)).value

        if cellValue_category is None:
            sheet.cell(row=i, column=colNum_category).value = category

            if cellValue_subCategory is None:
                sheet.cell(row=i, column=colNum_subCategory).value = subCategory

    wb.save(GlobalVariables.EXCEL_reportFilePath)
