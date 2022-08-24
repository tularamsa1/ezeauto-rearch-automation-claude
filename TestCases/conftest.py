import datetime
import fcntl
import json
import os
import time
from random import randint
import shutil
from selenium.webdriver.chrome import webdriver
from allure_commons.types import AttachmentType
import allure
import paramiko
from selenium import webdriver
from appium import webdriver as app_webdriver
from datetime import datetime
import chromedriver_autoinstaller
import DataProvider.GlobalConstants
from Utilities import ReportProcessor, ResourceAssigner
from PageFactory import Base_Actions
from Configuration import TestSuiteSetup
from Utilities import ConfigReader, DirectoryCreator, LogProcessor, Rerun
from pathlib import Path
import openpyxl
import pytest
from termcolor import colored

from DataProvider import GlobalVariables
from Utilities import ExcelProcessor
from Utilities.ReportProcessor import revert_excel_global_variables, setStylesForExcel, \
    updateExcel_With_Deselect_And_Broken, updateExcel_With_RerunAttempts, updateExcel_With_Category_And_Subcategory
from Utilities.time_calculator import EzeAutoTimeCalculator

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

EXCEL_reportFilePath = DirectoryCreator.getDirectoryPath("ExcelReport")+"/Report.xlsx"

# router_ip = '192.168.3.73'    #dev3
router_ip = Base_Actions.get_environment("str_exe_env_ip")  # dev11
router_username = Base_Actions.get_environment("str_ssh_username")
router_port = Base_Actions.get_environment("int_exe_env_port")
key_filename = Base_Actions.get_environment("str_ssh_key_filename")
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
            GlobalVariables.df_testCasesDetail.at[ind, 'ChargeSlip Val'] = "N/A"
            GlobalVariables.df_testCasesDetail.at[ind, 'Execution Time (sec)'] = 0.0
            GlobalVariables.df_testCasesDetail.at[ind, 'Validation Time (sec)'] = 0.0
            GlobalVariables.df_testCasesDetail.at[ind, 'Log Coll Time (sec)'] = 0.0
            GlobalVariables.df_testCasesDetail.at[ind, 'Total Time (sec)'] = 0.0
    # Converting to excel from DF
    GlobalVariables.df_testCasesDetail.to_excel(file_name)


def updatingHighLevelReportAfterEachTCS():
    timer = 0
    while timer < 10:
        try:
            with open(EXCEL_reportFilePath, 'a') as locked_file:
                fcntl.flock(locked_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                workbook = openpyxl.load_workbook(EXCEL_reportFilePath)
                sheet = workbook["Sheet1"]
                GlobalVariables.EXCEL_testCaseName = os.environ.get('PYTEST_CURRENT_TEST').replace(" (teardown)", '').split('::')[1]
                print("Testcase name", GlobalVariables.EXCEL_testCaseName)
                Overall_Status = 'Broken'
                if GlobalVariables.EXCEL_TC_Execution == 'Pass':

                    # Pass or N/A
                    if GlobalVariables.str_api_val_result != 'Fail' \
                        and GlobalVariables.str_app_val_result != 'Fail' \
                            and GlobalVariables.str_db_val_result != 'Fail' \
                                and GlobalVariables.str_portal_val_result != 'Fail' \
                                    and GlobalVariables.str_ui_val_result != 'Fail'\
                                        and GlobalVariables.str_chargeslip_val_result != "Fail":
                        Overall_Status = 'Pass'

                    elif GlobalVariables.str_api_val_result == 'Fail' \
                        or GlobalVariables.str_app_val_result == 'Fail' \
                            or GlobalVariables.str_db_val_result == 'Fail' \
                                or GlobalVariables.str_portal_val_result == 'Fail' \
                                    or GlobalVariables.str_ui_val_result == 'Fail'\
                                        or GlobalVariables.str_chargeslip_val_result == 'Fail':
                        Overall_Status = 'Fail'
                elif GlobalVariables.EXCEL_TC_Execution == 'Fail':
                    Overall_Status = 'Fail'
                    set_dne_status()
                rowNumber = ExcelProcessor.getRowNumberFromValue(workbook, sheet, 'Test Case ID',
                                                                 GlobalVariables.EXCEL_testCaseName)

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'File Name')
                GlobalVariables.EXCEL_testCaseFileName = sheet.cell(row=rowNumber, column=columnNumber).value

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'OverAll Results')
                sheet.cell(row=rowNumber, column=columnNumber).value = Overall_Status

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'TC Execution')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.EXCEL_TC_Execution

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'API Val')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.str_api_val_result
                print("API Val: ", GlobalVariables.str_api_val_result)

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'DB Val')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.str_db_val_result
                print("DB Val: ", GlobalVariables.str_db_val_result)

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'Portal Val')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.str_portal_val_result
                print("Portal Val: ", GlobalVariables.str_portal_val_result)

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'App Val')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.str_app_val_result
                print("App Val: ", GlobalVariables.str_app_val_result)

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'UI Val')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.str_ui_val_result
                print("UI Val: ", GlobalVariables.str_ui_val_result)

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'ChargeSlip Val')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.str_chargeslip_val_result
                print("ChargeSlip Val: ", GlobalVariables.str_chargeslip_val_result)

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'API Resp Code')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.str_api_response_code
                print("API Response Code: ", GlobalVariables.str_api_response_code)

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'API Resp Time(sec)')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.str_api_response_time
                print("API Response Time: ", GlobalVariables.str_api_response_time)

                columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'API Resp Size(kb)')
                sheet.cell(row=rowNumber, column=columnNumber).value = GlobalVariables.str_api_response_size
                print("API Response Size: ", GlobalVariables.str_api_response_size)

                if (ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "true" and ConfigReader.read_config(
                        "Validations", "bool_rerun_immediately").lower() == "false") \
                        or (
                        ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "true" and ConfigReader.read_config(
                    "Validations", "bool_rerun_immediately").lower() == "true"):
                    columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'Rerun Attempts')
                    if sheet.cell(row=rowNumber, column=columnNumber).value is None or sheet.cell(row=rowNumber, column=columnNumber).value == 'N/A':
                        sheet.cell(row=rowNumber, column=columnNumber).value =  0
                    else:

                        currentRetryCountsheet = sheet.cell(row=rowNumber, column=columnNumber).value
                        sheet.cell(row=rowNumber, column=columnNumber).value = currentRetryCountsheet + 1
                # =====================================================================================

                workbook.save(EXCEL_reportFilePath)
                workbook.close()
                fcntl.flock(locked_file, fcntl.LOCK_UN)
                break
        except Exception as e:
            print(f"Unable to update the tc result to report due to error {str(e)}. Retrying..")
            timer += 1
            time.sleep(1)

def set_dne_status():
    if ConfigReader.read_config("Validations", "api_validation").lower() == "true" and 'apiVal' in GlobalVariables.tc_markers:
        GlobalVariables.str_api_val_result = 'DNE'
    if ConfigReader.read_config("Validations", "db_validation").lower() == "true" and 'dbVal' in GlobalVariables.tc_markers:
        GlobalVariables.str_db_val_result = 'DNE'
    if ConfigReader.read_config("Validations", "portal_validation").lower() == "true" and 'portalVal' in GlobalVariables.tc_markers:
        GlobalVariables.str_portal_val_result = 'DNE'
    if ConfigReader.read_config("Validations", "app_validation").lower() == "true" and 'appVal' in GlobalVariables.tc_markers:
        GlobalVariables.str_app_val_result = 'DNE'
    if ConfigReader.read_config("Validations", "ui_validation").lower() == "true" and 'uiVal' in GlobalVariables.tc_markers:
        GlobalVariables.str_ui_val_result = 'DNE'
    if ConfigReader.read_config("Validations", "charge_slip_validation").lower() == "true" and 'chargeSlipVal' in GlobalVariables.tc_markers:
        GlobalVariables.str_chargeslip_val_result = 'DNE'


def captureLogs(request):
    item = request.node
    if Base_Actions.is_log_capture_required("bool_capt_log_different_files") == "True" and Base_Actions.is_log_capture_required("bool_capt_log_pass") == "True":
        if item.rep_call.passed:
            testCaseID = str(item.nodeid).split('/')
            finalTestCaseID = testCaseID[len(testCaseID) - 1]
            logFileName = str(finalTestCaseID).split('::')[1]

            path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
            Path(path).mkdir(parents=True, exist_ok=True)
            print("Fetching Logs first time")

            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

            if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                apiLogs = LogProcessor.fetchAPILogs()
                rerun_file = Path(path + "/api.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                portalLogs = LogProcessor.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required(
                    "bool_capt_log_middleware") == "True":
                mwareLogs = LogProcessor.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

            if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                config_logs = LogProcessor.fetch_config_logs()
                rerun_file = Path(path + "/config.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

            if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                rerun_file = Path(path + "/closedloop.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

            if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                q2_logs = LogProcessor.fetch_q2_logs()
                rerun_file = Path(path + "/q2.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

    if Base_Actions.is_log_capture_required("bool_capt_log_different_files") == "True" and Base_Actions.is_log_capture_required("bool_capt_log_fail") == "True":
        if item.rep_call.failed:
            testCaseID = str(item.nodeid).split('/')
            finalTestCaseID = testCaseID[len(testCaseID) - 1]
            logFileName = str(finalTestCaseID).split('::')[1]

            path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
            Path(path).mkdir(parents=True, exist_ok=True)
            print("Fetching Logs first time")

            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

            if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                apiLogs = LogProcessor.fetchAPILogs()
                rerun_file = Path(path + "/api.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                portalLogs = LogProcessor.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required(
                    "bool_capt_log_middleware") == "True":
                mwareLogs = LogProcessor.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

            if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                config_logs = LogProcessor.fetch_config_logs()
                rerun_file = Path(path + "/config.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

            if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                rerun_file = Path(path + "/closedloop.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

            if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                q2_logs = LogProcessor.fetch_q2_logs()
                rerun_file = Path(path + "/q2.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

    if Base_Actions.is_log_capture_required("bool_capt_log_one_file") == "True" and Base_Actions.is_log_capture_required("bool_capt_log_pass") == "True":
        if item.rep_call.passed:
            path = DirectoryCreator.getDirectoryPath("ServerLog") + "/"
            print("Inside capturing logs all in one file")
            print("Fetching Logs 4th time")

            Path(path).mkdir(parents=True, exist_ok=True)
            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
            if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                apiLogs = LogProcessor.fetchAPILogs()
                rerun_file = Path(path + "/api.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                portalLogs = LogProcessor.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required(
                    "bool_capt_log_middleware") == "True":
                mwareLogs = LogProcessor.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

            if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                config_logs = LogProcessor.fetch_config_logs()
                rerun_file = Path(path + "/config.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

            if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                rerun_file = Path(path + "/closedloop.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

            if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                q2_logs = LogProcessor.fetch_q2_logs()
                rerun_file = Path(path + "/q2.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

    if Base_Actions.is_log_capture_required("bool_capt_log_one_file") == "True" and Base_Actions.is_log_capture_required("bool_capt_log_fail") == "True":
        if item.rep_call.failed:
            path = DirectoryCreator.getDirectoryPath("ServerLog") + "/"
            print("Inside capturing logs all in one file")
            print("Fetching Logs 4th time")

            Path(path).mkdir(parents=True, exist_ok=True)
            TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
            if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                apiLogs = LogProcessor.fetchAPILogs()
                rerun_file = Path(path + "/api.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

            if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                portalLogs = LogProcessor.fetchPortalLogs()
                rerun_file = Path(path + "/portal.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

            if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required(
                    "bool_capt_log_middleware") == "True":
                mwareLogs = LogProcessor.fetchMiddlewareLogs()
                rerun_file = Path(path + "/middleware.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

            if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                rerun_file = Path(path + "/cnpware.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

            if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                config_logs = LogProcessor.fetch_config_logs()
                rerun_file = Path(path + "/config.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

            if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                rerun_file = Path(path + "/closedloop.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

            if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                q2_logs = LogProcessor.fetch_q2_logs()
                rerun_file = Path(path + "/q2.log")
                LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)


@pytest.fixture(scope="function")  # Executing once before every testcases
def method_setup(request):
    if GlobalVariables.time_calc is not None:
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))
    else:
        GlobalVariables.time_calc = EzeAutoTimeCalculator()
        print(colored("Intializaed EzeAutoTimeCalculator in method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.setup.start()
        print(colored("Setup Timer started in method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))

    GlobalVariables.tc_markers = [m.name for m in request.node.iter_markers()]
    GlobalVariables.time_calc.setup.pause()
    print(colored("Setup Timer paused in method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))

    # breakpoint()
    GlobalVariables.time_calc.log_collection.start()
    print(colored("Log Collection Timer started in method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))
    print("Function setup level")
    GlobalVariables.LogCollTime = LogProcessor.startLineNoOfServerLogFile()

    GlobalVariables.time_calc.log_collection.pause()
    print(colored("Log Collection Timer paused in method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))

    # breakpoint()
    print("***************End of setup")

    # Executing once AFTER every testcases
    def fin():
        print()
        # GlobalVariables.time_calc.log_collection.end()
        # print(colored("Log Collection Timer ended in 'fin' of method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))


        GlobalVariables.time_calc.teardown.start()
        print(colored("Teardown Timer started in 'fin' of method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        print("Function teardown level")
        # Write data to dataframe
        # write_TC_Details_To_Dataframe()

        GlobalVariables.time_calc.teardown.pause()
        print(colored("Teardown Timer paused in 'fin' of method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        if isBothRerunNotEnabled():
            captureLogs(request)

        if ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "false" and ConfigReader.read_config("Validations", "bool_rerun_immediately").lower() == "false":
            log_on_failure(request)

        if Rerun.getRerunCount(str(request.node.nodeid).split('::')[1]) == 0 and Base_Actions.is_log_capture_required("bool_capt_log_last_run") == "True"  and ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "true":
            # breakpoint()
            print("Rerun.getRerunCountForAtTheEnd(): ", Rerun.getRerunCount(str(request.node.nodeid).split('::')[1]))
            print("log_on_failure(request)")
            log_on_failure(request)

        if ConfigReader.read_config("Validations",
                                    "bool_rerun_at_the_end").lower() == "true" and Base_Actions.is_log_capture_required(
                "bool_capt_log_each_run") == "True":
            log_on_failure(request)

        GlobalVariables.time_calc.teardown.resume()
        print(colored("Teardown Timer resume in 'fin' of method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        updatingHighLevelReportAfterEachTCS()

        # rerunCount = Rerun.getRerunCount(GlobalVariables.EXCEL_testCaseName)
        if ConfigReader.read_config("Validations", "bool_rerun_immediately").lower() == "true" and Rerun.isRerunRequiredImmediately(GlobalVariables.EXCEL_testCaseName) \
                and ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "false":

            # Added on Apr 11
            rerunCount = Rerun.getRerunCount(GlobalVariables.EXCEL_testCaseName)

            if Base_Actions.is_log_capture_required("bool_capt_log_each_run") == "True":
                GlobalVariables.time_calc.teardown.pause()
                print(colored("Teardown Timer paused in 'fin' of method_setup fixture before logonfailure is called".center(shutil.get_terminal_size().columns, "="), 'cyan'))
                log_on_failure(request)
                GlobalVariables.time_calc.teardown.resume()
                print(colored("Teardown Timer resumed in 'fin' of method_setup fixture after logonfailure is called".center(shutil.get_terminal_size().columns, "="), 'cyan'))


            if rerunCount >= 0:
                # GlobalVariables.time_calc.teardown.pause()
                # print(colored("Teardown Timer paused (since rerun) in 'fin' of method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))
                print(str(rerunCount) + " reruns pending for the test case " + GlobalVariables.EXCEL_testCaseName)
                rerunCount -= 1
                # Rerun.rerunTestImmediately(GlobalVariables.EXCEL_testCaseName, GlobalVariables.EXCEL_testCaseFileName, rerunCount)
                Rerun.rerunTestImmediately(GlobalVariables.EXCEL_testCaseName, GlobalVariables.EXCEL_testCaseFileName,
                                           rerunCount, request)

                # GlobalVariables.time_calc.teardown.resume()
                # print(colored("Teardown Timer resumed (after rerun) in 'fin' of method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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
        GlobalVariables.time_calc.teardown.end()
        print(colored("Teardown Timer ended in 'fin' -> 'method_setup' fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # GlobalVariables.time_calc.save()
        # print(colored("Saved time_calc object in 'fin' of method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))

    request.addfinalizer(fin)


def write_TC_Details_To_Dataframe():
    # breakpoint()
    print("################", GlobalVariables.str_portal_val_result)
    TestCaseName = os.environ.get('PYTEST_CURRENT_TEST').replace(" (teardown)", '').replace("test_sample.py::",
                                                                                            '').replace("TestCase/", '')
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'TC Execution'] = GlobalVariables.EXCEL_TC_Execution
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'API Val'] = GlobalVariables.str_api_val_result
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'DB Val'] = GlobalVariables.str_db_val_result
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Portal Val'] = GlobalVariables.str_portal_val_result
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'App Val'] = GlobalVariables.str_app_val_result
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'UI Val'] = GlobalVariables.str_ui_val_result
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'ChargeSlip Val'] = GlobalVariables.str_chargeslip_val_result
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Execution Time (sec)'] = GlobalVariables.EXCEL_Execution_Time
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Validation Time (sec)'] = GlobalVariables.EXCEL_Val_time
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Log Coll Time (sec)'] = GlobalVariables.EXCEL_LogCollTime
    GlobalVariables.df_testCasesDetail.at[TestCaseName, 'Total Time (sec)'] = GlobalVariables.EXCEL_Tot_Time


@pytest.fixture(scope="function")
def ui_driver(request):
    if GlobalVariables.time_calc is not None:
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in ui_driver function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
    else:
        GlobalVariables.time_calc = EzeAutoTimeCalculator()
        print(colored("Intializaed EzeAutoTimeCalculator in ui_driver".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.setup.start()
        print(colored("Setup Timer started in ui_driver".center(shutil.get_terminal_size().columns, "="), 'cyan'))

    GlobalVariables.portalDriver = chromedriver_autoinstaller.install()
    # Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument('--disable-dev-shm-usage')
    # Run chrome
    GlobalVariables.portalDriver = webdriver.Chrome(options=chrome_options)
    GlobalVariables.portalDriver.maximize_window()
    # GlobalVariables.time_calc.setup.resume()
    # print(colored("Setup Timer resumed in ui_driver function".center(shutil.get_terminal_size().columns, "="), 'cyan'))


    GlobalVariables.time_calc.setup.pause()
    print(colored("Setup Timer paused in ui_driver function".center(shutil.get_terminal_size().columns, "="), 'cyan'))




@pytest.fixture(scope="function")
def appium_driver(request):
    if GlobalVariables.time_calc is not None:
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in appium_driver function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
    else:
        GlobalVariables.time_calc = EzeAutoTimeCalculator()
        print(colored("Intializaed EzeAutoTimeCalculator in appium_driver".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.setup.start()
        print(colored("Setup Timer started in appium_driver".center(shutil.get_terminal_size().columns, "="), 'cyan'))

    testcaseid = request.node.name
    deviceDetails = ResourceAssigner.getDeviceFromDB(testcaseid)
    appiumserverDetails = ResourceAssigner.getAppiumServerFromDB(testcaseid)
    print(testcaseid+" will be using the device "+deviceDetails['DeviceId'])
    print(testcaseid + " will be running on the appium server port " + appiumserverDetails['PortNumber'])
    mposApp = ConfigReader.read_config_paths("System","automation_suite_path")+"/App/"+ConfigReader.read_config("Applications","mpos")
    saApp = ConfigReader.read_config_paths("System","automation_suite_path")+"/App/"+ConfigReader.read_config("Applications","SA")
    lst_applications = [mposApp,saApp]
    json_applications = json.dumps(lst_applications)
    desired_cap = {
        "platformName": "Android",
        "deviceName": deviceDetails['DeviceId'],
        "udid": deviceDetails['DeviceId'],
        "otherApps": json_applications,
        "appPackage": "com.ezetap.basicapp",
        "appActivity": "com.ezetap.mposX.activity.SplashActivity",
        "ignoreHiddenApiPolicyError": "true",
        "noReset": "false",
        "autoGrantPermissions": "true",
        "newCommandTimeout":7000,
        "MobileCapabilityType.AUTOMATION_NAME": "AutomationName.ANDROID_UIAUTOMATOR2",
        "MobileCapabilityType.NEW_COMMAND_TIMEOUT":"300"
    }
    print(desired_cap)
    print("appium server url:", 'http://127.0.0.1:' + appiumserverDetails['PortNumber'] + '/wd/hub')
    GlobalVariables.appDriver = app_webdriver.Remote('http://127.0.0.1:' + appiumserverDetails['PortNumber'] + '/wd/hub', desired_cap)
    # GlobalVariables.appDriver.implicitly_wait(30)

    GlobalVariables.time_calc.setup.pause()
    print(colored("Setup Timer paused in appium_driver function".center(shutil.get_terminal_size().columns, "="), 'cyan'))


def pytest_deselected(items):
    print("INSIDE DESELCTED METHOD")
    for item in items:
        print(item.nodeid)
        testcase = str((item.nodeid)).split('::')[1]
        GlobalVariables.list_deselected_testcases.append(testcase)


def isBothRerunNotEnabled():
    if ConfigReader.read_config("Validations","bool_rerun_at_the_end").lower() == "false" and ConfigReader.read_config("Validations","bool_rerun_immediately").lower() == "false":
        return True
    return False


def log_on_failure(request):
    if GlobalVariables.time_calc.log_collection.is_started and GlobalVariables.time_calc.log_collection.is_paused:
        GlobalVariables.time_calc.log_collection.resume()
        print(colored("Log Collection Timer resumed in 'log_on_failure' function of conftest".center(shutil.get_terminal_size().columns, "="), 'cyan'))
    else:
        GlobalVariables.time_calc.log_collection.start()
        print(colored("Log Collection started in 'log_on_failure' function of conftest".center(shutil.get_terminal_size().columns, "="), 'cyan'))

    item = request.node
    if item.rep_call.failed:
        if Base_Actions.is_log_capture_required("bool_capt_log_fail") == "True":

            if Base_Actions.is_log_capture_required("bool_capt_log_different_files") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_last_run") == "True":

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

                if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                    apiLogs = LogProcessor.fetchAPILogs()
                    rerun_file = Path(path + "/api.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                    portalLogs = LogProcessor.fetchPortalLogs()
                    rerun_file = Path(path + "/portal.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_middleware") == "True":
                    mwareLogs = LogProcessor.fetchMiddlewareLogs()
                    rerun_file = Path(path + "/middleware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                    cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                    rerun_file = Path(path + "/cnpware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                    config_logs = LogProcessor.fetch_config_logs()
                    rerun_file = Path(path + "/config.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                    closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                    rerun_file = Path(path + "/closedloop.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                    q2_logs = LogProcessor.fetch_q2_logs()
                    rerun_file = Path(path + "/q2.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)


            if Base_Actions.is_log_capture_required("bool_capt_log_different_files") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_each_run") == "True" and ConfigReader.read_config("Validations",
                                                                                      "bool_rerun_at_the_end").lower() == "true":
                i = int(ConfigReader.read_config("Validations", "int_rerun_count"))
                j = 0
                print("Fetching Logs 2nd time")

                TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

                # Added on 26 Apr
                testCaseID = str(item.nodeid).split('/')
                finalTestCaseID = testCaseID[len(testCaseID) - 1]
                logFileName = str(finalTestCaseID).split('::')[1]
                #logFileName = str(finalTestCaseID).replace("::", "_")

                while i >= 0 and j <= int(ConfigReader.read_config("Validations", "int_rerun_count")):
                    if Rerun.getRerunCount(str(item.nodeid).split('::')[1]) == i:
                        # Added on 26 Apr
                        path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
                        #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName

                        Path(path).mkdir(parents=True, exist_ok=True)

                        if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                            apiLogs = LogProcessor.fetchAPILogs()
                            rerun_file = Path(path + "/api_Rerun.log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                        if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                            portalLogs = LogProcessor.fetchPortalLogs()
                            rerun_file = Path(path + "/portal_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                        if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required(
                                "bool_capt_log_middleware") == "True":
                            mwareLogs = LogProcessor.fetchMiddlewareLogs()
                            rerun_file = Path(
                                path + "/middleware_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                        if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                            cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                            rerun_file = Path(path + "/cnpware_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                        if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                            config_logs = LogProcessor.fetch_config_logs()
                            rerun_file = Path(path + "/config_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                        if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                            closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                            rerun_file = Path(path + "/closedloop_rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                        if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                            q2_logs = LogProcessor.fetch_q2_logs()
                            rerun_file = Path(path + "/q2_rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)


                    i -= 1
                    j += 1

            if Base_Actions.is_log_capture_required("bool_capt_log_different_files") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_each_run") == "True" and ConfigReader.read_config("Validations",
                                                                                      "bool_rerun_immediately").lower() == "true":

                i = int(ConfigReader.read_config("Validations", "int_rerun_count"))
                j = 0
                print("Fetching Logs 3rd time")

                TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

                # Added on 26 Apr
                testCaseID = str(item.nodeid).split('/')
                finalTestCaseID = testCaseID[len(testCaseID) - 1]
                logFileName = str(finalTestCaseID).split('::')[1]
                #logFileName = str(finalTestCaseID).replace("::", "_")

                while i >= 0 and j <= int(ConfigReader.read_config("Validations", "int_rerun_count")):
                    if Rerun.getRerunCount(str(item.nodeid).split('::')[1]) == i:

                        #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName
                        path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
                        Path(path).mkdir(parents=True, exist_ok=True)

                        if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                            apiLogs = LogProcessor.fetchAPILogs()
                            rerun_file = Path(path + "/api_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                        if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                            portalLogs = LogProcessor.fetchPortalLogs()
                            rerun_file = Path(path + "/portal_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                        if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required(
                                "bool_capt_log_middleware") == "True":
                            mwareLogs = LogProcessor.fetchMiddlewareLogs()
                            rerun_file = Path(
                                path + "/middleware_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                        if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                            cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                            rerun_file = Path(path + "/cnpware_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                        if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                            config_logs = LogProcessor.fetch_config_logs()
                            rerun_file = Path(path + "/config_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                        if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                            closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                            rerun_file = Path(path + "/closedloop_rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                        if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                            q2_logs = LogProcessor.fetch_q2_logs()
                            rerun_file = Path(path + "/q2_rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

                    i -= 1
                    j += 1

            if Base_Actions.is_log_capture_required("bool_capt_log_one_file") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_last_run") == "True":
                path = DirectoryCreator.getDirectoryPath("ServerLog")+"/"
                #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/"
                print("Inside capturing logs all in one file")
                print("Fetching Logs 4th time")

                Path(path).mkdir(parents=True, exist_ok=True)
                TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
                if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                    apiLogs = LogProcessor.fetchAPILogs()
                    rerun_file = Path(path + "/api.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                    portalLogs = LogProcessor.fetchPortalLogs()
                    rerun_file = Path(path + "/portal.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_middleware") == "True":
                    mwareLogs = LogProcessor.fetchMiddlewareLogs()
                    rerun_file = Path(path + "/middleware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                    cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                    rerun_file = Path(path + "/cnpware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                    config_logs = LogProcessor.fetch_config_logs()
                    rerun_file = Path(path + "/config.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                    closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                    rerun_file = Path(path + "/closedloop.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                    q2_logs = LogProcessor.fetch_q2_logs()
                    rerun_file = Path(path + "/q2.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

            if Base_Actions.is_log_capture_required("bool_capt_log_one_file") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_each_run") == "True":
                path = DirectoryCreator.getDirectoryPath("ServerLog")+"/"
                #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/"
                print("Inside capturing logs all in one file")
                print("Fetching Logs 5th time")

                Path(path).mkdir(parents=True, exist_ok=True)
                TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
                if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                    apiLogs = LogProcessor.fetchAPILogs()
                    print("TCIdWithTimeStamp", TCIdWithTimeStamp)
                    rerun_file = Path(path + "/api.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                    portalLogs = LogProcessor.fetchPortalLogs()
                    rerun_file = Path(path + "/portal.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_middleware") == "True":
                    mwareLogs = LogProcessor.fetchMiddlewareLogs()
                    rerun_file = Path(path + "/middleware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                    cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                    rerun_file = Path(path + "/cnpware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                    config_logs = LogProcessor.fetch_config_logs()
                    rerun_file = Path(path + "/config.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                    closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                    rerun_file = Path(path + "/closedloop.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                    q2_logs = LogProcessor.fetch_q2_logs()
                    rerun_file = Path(path + "/q2.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

        if GlobalVariables.bool_ss_app_val == 'Failed' and GlobalVariables.appDriver != '' and Base_Actions.is_ss_capture_required("bool_capt_ss_fail") == "True":
            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="app_screen",
                          attachment_type=AttachmentType.PNG)
            GlobalVariables.bool_ss_app_val = 'Passed'

        if GlobalVariables.bool_ss_portal_val == 'Failed' and GlobalVariables.portalDriver != ''and Base_Actions.is_ss_capture_required("bool_capt_ss_fail") == "True":
            allure.attach(GlobalVariables.portalDriver.get_screenshot_as_png(), name="portal_page",
                          attachment_type=AttachmentType.PNG)
            GlobalVariables.bool_ss_portal_val = 'Passed'

        if GlobalVariables.str_chargeslip_val_result == "Fail" and GlobalVariables.charge_slip_driver != '' and Base_Actions.is_ss_capture_required(
                "bool_capt_ss_fail") == "True":
            allure.attach(GlobalVariables.charge_slip_driver.get_screenshot_as_png(), name="chargeslip",
                          attachment_type=AttachmentType.PNG)

        if GlobalVariables.portalDriver != '':
            # GlobalVariables.portalDriver.quit()
            GlobalVariables.portalDriver.close()
            GlobalVariables.portalDriver = ''
            # variables.successApp = False

        if GlobalVariables.appDriver != '':
            GlobalVariables.appDriver.quit()
            GlobalVariables.appDriver = ''
            # variables.appSS = False

        if GlobalVariables.charge_slip_driver != '':
            GlobalVariables.charge_slip_driver.quit()
            GlobalVariables.charge_slip_driver = ''

        GlobalVariables.bool_ss_portal_val = "N/A"
        GlobalVariables.bool_ss_app_val = "N/A"
    GlobalVariables.time_calc.log_collection.pause()
    print(colored("Log Collection Timer paused in 'log on failure' function in conftest".center(shutil.get_terminal_size().columns, "="), 'cyan'))


@pytest.fixture(scope='function')
def log_on_success(request):
    yield

    if GlobalVariables.time_calc.log_collection.is_started and GlobalVariables.time_calc.log_collection.is_paused:
        GlobalVariables.time_calc.log_collection.resume()
        print(colored("Log Collection resumed in 'log_on_success' function of conftest".center(shutil.get_terminal_size().columns, "="), 'cyan'))
    else:
        GlobalVariables.time_calc.log_collection.start()
        print(colored("Log Collection started in 'log_on_success' function of conftest".center(shutil.get_terminal_size().columns, "="), 'cyan'))

    item = request.node

    if item.rep_call.passed:
        if Base_Actions.is_log_capture_required("bool_capt_log_pass") == "True":

            # if configReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "false" and \
            #         configReader.read_config("Validations", "bool_rerun_immediately").lower() == "false":
            #
            #     testCaseID = str(item.nodeid).split('/')
            #     finalTestCaseID = testCaseID[len(testCaseID) - 1]
            #     # logFileName =  str(finalTestCaseID).replace("::", "_")
            #     logFileName = str(finalTestCaseID).split('::')[1]
            #     path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
            #     #          path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName
            #     Path(path).mkdir(parents=True, exist_ok=True)
            #     print("Fetching Logs zeroth time")
            #
            #     TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
            #
            #     if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
            #         apiLogs = LogProcessor.fetchAPILogs()
            #         rerun_file = Path(path + "/api.log")
            #         LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)
            #
            #     if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required(
            #             "bool_capt_log_portal") == "True":
            #         portalLogs = LogProcessor.fetchPortalLogs()
            #         rerun_file = Path(path + "/portal.log")
            #         LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)
            #
            #     if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required(
            #             "bool_capt_log_middleware") == "True":
            #         mwareLogs = LogProcessor.fetchMiddlewareLogs()
            #         rerun_file = Path(path + "/middleware.log")
            #         LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)
            #
            #     if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required(
            #             "bool_capt_log_cnpware") == "True":
            #         cnpWareLogs = LogProcessor.fetchCnpwareLogs()
            #         rerun_file = Path(path + "/cnpware.log")
            #         LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

            if Base_Actions.is_log_capture_required("bool_capt_log_different_files") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_last_run") == "True":

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

                if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                    apiLogs = LogProcessor.fetchAPILogs()
                    rerun_file = Path(path + "/api.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                    portalLogs = LogProcessor.fetchPortalLogs()
                    rerun_file = Path(path + "/portal.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_middleware") == "True":
                    mwareLogs = LogProcessor.fetchMiddlewareLogs()
                    rerun_file = Path(path + "/middleware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                    cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                    rerun_file = Path(path + "/cnpware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                    config_logs = LogProcessor.fetch_config_logs()
                    rerun_file = Path(path + "/config.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                    closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                    rerun_file = Path(path + "/closedloop.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                    q2_logs = LogProcessor.fetch_q2_logs()
                    rerun_file = Path(path + "/q2.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

            if Base_Actions.is_log_capture_required("bool_capt_log_different_files") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_each_run") == "True" and ConfigReader.read_config("Validations",
                                                                                      "bool_rerun_at_the_end").lower() == "true":
                i = int(ConfigReader.read_config("Validations", "int_rerun_count"))
                j = 0
                print("Fetching Logs 2nd time")

                TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

                # Added on 26 Apr
                testCaseID = str(item.nodeid).split('/')
                finalTestCaseID = testCaseID[len(testCaseID) - 1]
                logFileName = str(finalTestCaseID).split('::')[1]
                #logFileName = str(finalTestCaseID).replace("::", "_")

                while i >= 0 and j <= int(ConfigReader.read_config("Validations", "int_rerun_count")):
                    if Rerun.getRerunCount(str(item.nodeid).split('::')[1]) == i:
                        # Added on 26 Apr
                        path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
                        #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName

                        Path(path).mkdir(parents=True, exist_ok=True)

                        if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                            apiLogs = LogProcessor.fetchAPILogs()
                            rerun_file = Path(path + "/api_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                        if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                            portalLogs = LogProcessor.fetchPortalLogs()
                            rerun_file = Path(path + "/portal_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                        if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required(
                                "bool_capt_log_middleware") == "True":
                            mwareLogs = LogProcessor.fetchMiddlewareLogs()
                            rerun_file = Path(
                                path + "/middleware_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                        if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                            cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                            rerun_file = Path(path + "/cnpware_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                        if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                            config_logs = LogProcessor.fetch_config_logs()
                            rerun_file = Path(path + "/config_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                        if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                            closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                            rerun_file = Path(path + "/closedloop_rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                        if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                            q2_logs = LogProcessor.fetch_q2_logs()
                            rerun_file = Path(path + "/q2_rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

                    i -= 1
                    j += 1

            if Base_Actions.is_log_capture_required("bool_capt_log_different_files") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_each_run") == "True" and ConfigReader.read_config("Validations",
                                                                                      "bool_rerun_immediately").lower() == "true":

                i = int(ConfigReader.read_config("Validations", "int_rerun_count"))
                j = 0
                print("Fetching Logs 3rd time")

                TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())

                # Added on 26 Apr
                testCaseID = str(item.nodeid).split('/')
                finalTestCaseID = testCaseID[len(testCaseID) - 1]
                logFileName = str(finalTestCaseID).split('::')[1]
               # logFileName = str(finalTestCaseID).replace("::", "_")

                while i >= 0 and j <= int(ConfigReader.read_config("Validations", "int_rerun_count")):
                    if Rerun.getRerunCount(str(item.nodeid).split('::')[1]) == i:

                        #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/" + logFileName
                        path = DirectoryCreator.getDirectoryPath("ServerLog") + "/" + logFileName
                        Path(path).mkdir(parents=True, exist_ok=True)

                        if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                            apiLogs = LogProcessor.fetchAPILogs()
                            rerun_file = Path(path + "/api_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                        if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                            portalLogs = LogProcessor.fetchPortalLogs()
                            rerun_file = Path(path + "/portal_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                        if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required(
                                "bool_capt_log_middleware") == "True":
                            mwareLogs = LogProcessor.fetchMiddlewareLogs()
                            rerun_file = Path(
                                path + "/middleware_" + str(datetime.now().time()) + "_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                        if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                            cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                            rerun_file = Path(path + "/cnpware_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                        if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                            config_logs = LogProcessor.fetch_config_logs()
                            rerun_file = Path(path + "/config_Rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                        if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                            closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                            rerun_file = Path(path + "/closedloop_rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                        if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                            q2_logs = LogProcessor.fetch_q2_logs()
                            rerun_file = Path(path + "/q2_rerun_" + str(j) + ".log")
                            LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

                    i -= 1
                    j += 1

            if Base_Actions.is_log_capture_required("bool_capt_log_one_file") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_last_run") == "True":
                path = DirectoryCreator.getDirectoryPath("ServerLog") + "/"
                #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/"
                print("Inside capturing logs all in one file")
                print("Fetching Logs 4th time")

                Path(path).mkdir(parents=True, exist_ok=True)
                TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
                if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                    apiLogs = LogProcessor.fetchAPILogs()
                    rerun_file = Path(path + "/api.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                    portalLogs = LogProcessor.fetchPortalLogs()
                    rerun_file = Path(path + "/portal.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_middleware") == "True":
                    mwareLogs = LogProcessor.fetchMiddlewareLogs()
                    rerun_file = Path(path + "/middleware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                    cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                    rerun_file = Path(path + "/cnpware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                    config_logs = LogProcessor.fetch_config_logs()
                    rerun_file = Path(path + "/config.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                    closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                    rerun_file = Path(path + "/closedloop.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                    q2_logs = LogProcessor.fetch_q2_logs()
                    rerun_file = Path(path + "/q2.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

            if Base_Actions.is_log_capture_required("bool_capt_log_one_file") == "True" and Base_Actions.is_log_capture_required(
                    "bool_capt_log_each_run") == "True":
                path = DirectoryCreator.getDirectoryPath("ServerLog") + "/"
                #path = "/home/oem/PycharmProjects/EzeAuto/ServerLogs/"
                print("Inside capturing logs all in one file")
                print("Fetching Logs 5th time")

                Path(path).mkdir(parents=True, exist_ok=True)
                TCIdWithTimeStamp = str(item.nodeid) + '_' + str(datetime.now().time())
                if GlobalVariables.apiLogs and Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                    apiLogs = LogProcessor.fetchAPILogs()
                    print("TCIdWithTimeStamp", TCIdWithTimeStamp)
                    rerun_file = Path(path + "/api.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, apiLogs)

                if GlobalVariables.portalLogs and Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                    portalLogs = LogProcessor.fetchPortalLogs()
                    rerun_file = Path(path + "/portal.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, portalLogs)

                if GlobalVariables.middleWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_middleware") == "True":
                    mwareLogs = LogProcessor.fetchMiddlewareLogs()
                    rerun_file = Path(path + "/middleware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, mwareLogs)

                if GlobalVariables.cnpWareLogs and Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                    cnpWareLogs = LogProcessor.fetchCnpwareLogs()
                    rerun_file = Path(path + "/cnpware.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, cnpWareLogs)

                if GlobalVariables.config_logs and Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                    config_logs = LogProcessor.fetch_config_logs()
                    rerun_file = Path(path + "/config.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, config_logs)

                if GlobalVariables.closedloop_logs and Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                    closedloop_logs = LogProcessor.fetch_closed_loop_logs()
                    rerun_file = Path(path + "/closedloop.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, closedloop_logs)

                if GlobalVariables.q2_logs and Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                    q2_logs = LogProcessor.fetch_q2_logs()
                    rerun_file = Path(path + "/q2.log")
                    LogProcessor.appendLogs(rerun_file, TCIdWithTimeStamp, q2_logs)

        if GlobalVariables.bool_ss_app_val == 'Passed' and GlobalVariables.appDriver != '' and Base_Actions.is_ss_capture_required("bool_capt_ss_pass") == "True":
            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="app_screen",
                          attachment_type=AttachmentType.PNG)
            GlobalVariables.bool_ss_app_val = 'Passed'

        if GlobalVariables.bool_ss_portal_val == 'Passed' and GlobalVariables.portalDriver != '' and Base_Actions.is_ss_capture_required("bool_capt_ss_pass") == "True":
            allure.attach(GlobalVariables.portalDriver.get_screenshot_as_png(), name="portal_page",
                          attachment_type=AttachmentType.PNG)
            GlobalVariables.bool_ss_portal_val = 'Passed'

        if GlobalVariables.str_chargeslip_val_result == "Pass" and GlobalVariables.charge_slip_driver != '' and Base_Actions.is_ss_capture_required(
                "bool_capt_ss_pass") == "True":
            allure.attach(GlobalVariables.charge_slip_driver.get_screenshot_as_png(), name="chargeslip",
                          attachment_type=AttachmentType.PNG)

        if GlobalVariables.portalDriver != '':
            # GlobalVariables.portalDriver.quit()
            GlobalVariables.portalDriver.close()
            GlobalVariables.portalDriver = ''
            # variables.successApp = False

        if GlobalVariables.appDriver != '':
            GlobalVariables.appDriver.quit()
            GlobalVariables.appDriver = ''
            # variables.appSS = False

        if GlobalVariables.charge_slip_driver != '':
            GlobalVariables.charge_slip_driver.quit()
            GlobalVariables.charge_slip_driver = ''

        GlobalVariables.bool_ss_portal_val = "N/A"
        GlobalVariables.bool_ss_app_val = "N/A"

    GlobalVariables.time_calc.log_collection.pause()
    print(colored("Log Collection Timer paused in 'log on sucess' function in conftest".center(shutil.get_terminal_size().columns, "="), 'cyan'))


    GlobalVariables.time_calc.log_collection.end()
    print(colored("Log Collection Timer ended in 'fin' of method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))


    GlobalVariables.time_calc.save()
    GlobalVariables.time_calc = None
    print(colored("Saved time_calc object in 'fin' of method_setup fixture".center(shutil.get_terminal_size().columns, "="), 'cyan'))



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
