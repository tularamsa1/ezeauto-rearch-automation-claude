import os
from datetime import datetime

import openpyxl
import pandas as pd

from PageFactory import Base_Actions
from TestCases import  ExcelProcessor, conftest
from DataProvider import GlobalVariables
from Utilities import configReader, DirectoryCreator

immediateRerun = True


def rerunTestAtTheEnd():
    # print("Rerun count is: ", rerunCount)
    df_rerunTestCases = pd.DataFrame(
        pd.read_excel(GlobalVariables.EXCEL_reportFilePath))

    df_rerunTestCases.set_index("Test Case ID", inplace=True)

    exeFail = []
    apiValFail = []
    dbValFail = []
    portalValFail = []
    uiValFail = []
    appValFail = []
    setOfTest = set()

    # Adding Broken status, Added on Apr 11
    setOfRerunTest = set()

    for ind in df_rerunTestCases.index:
        testCaseName = str(df_rerunTestCases['File Name'][ind]) + ".py::" + str(ind)

        if str(df_rerunTestCases['TC Execution'][ind]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                      "bool_rerun_exe_val") == "True":
            exeFail.append(testCaseName)
            setOfTest.add(testCaseName)
            # Added on Apr 11
            setOfRerunTest.add(str(ind))
        if str(df_rerunTestCases['API Val'][ind]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                 "bool_rerun_api_val") == "True":
            apiValFail.append(testCaseName)
            setOfTest.add(testCaseName)
            setOfRerunTest.add(str(ind))
        if str(df_rerunTestCases['DB Val'][ind]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                "bool_rerun_db_val") == "True":
            dbValFail.append(testCaseName)
            setOfTest.add(testCaseName)
            setOfRerunTest.add(str(ind))
        if str(df_rerunTestCases['Portal Val'][ind]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                    "bool_rerun_portal_val") == "True":
            portalValFail.append(testCaseName)
            setOfTest.add(testCaseName)
            setOfRerunTest.add(str(ind))
        if str(df_rerunTestCases['App Val'][ind]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                 "bool_rerun_app_val") == "True":
            appValFail.append(testCaseName)
            setOfTest.add(testCaseName)
            setOfRerunTest.add(str(ind))
        if str(df_rerunTestCases['UI Val'][ind]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                "bool_rerun_ui_val") == "True":
            uiValFail.append(testCaseName)
            setOfTest.add(testCaseName)
            setOfRerunTest.add(str(ind))

    ls_rerunTestCases = list(setOfTest)
    listToStr = ' '.join([str(elem) for elem in ls_rerunTestCases])

    print("pytest -v " + listToStr + ' --alluredir='+DirectoryCreator.getDirectoryPath("AllureReport"))
    print(list(setOfTest))
    print("List of exe tcs failed", exeFail)
    print("List of apiVal tcs failed", apiValFail)
    print("List of dbVal tcs failed", dbValFail)
    print("List of portalVal tcs failed", portalValFail)
    print("List of appVal tcs failed", appValFail)
    print("List of uiVal tcs failed", uiValFail)
    print(GlobalVariables.df_testCasesDetail)

    if len(listToStr) > 0:
        # To send the testcaseID as a list to change the overall_Status as empty
        ls_TestCasesForRerun = list(setOfRerunTest)
        changeOverallStatusToEmpty(ls_TestCasesForRerun)
        os.system(
            "pytest -v " + listToStr + ' --alluredir='+DirectoryCreator.getDirectoryPath("AllureReport"))


def isRerunRequiredImmediately(testCaseID):
    isRerunRequired = False
    df_rerunTestCases = pd.DataFrame(
        pd.read_excel(GlobalVariables.EXCEL_reportFilePath))

    df_rerunTestCases.set_index("Test Case ID", inplace=True)

    testCaseName = str(df_rerunTestCases['File Name'][testCaseID]) + ".py::" + str(testCaseID)

    if str(df_rerunTestCases['TC Execution'][testCaseID]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                         "bool_rerun_exe_val") == "True":
        isRerunRequired = True
    if str(df_rerunTestCases['API Val'][testCaseID]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                    "bool_rerun_api_val") == "True":
        isRerunRequired = True
    if str(df_rerunTestCases['DB Val'][testCaseID]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                   "bool_rerun_db_val") == "True":
        isRerunRequired = True
    if str(df_rerunTestCases['Portal Val'][testCaseID]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                       "bool_rerun_portal_val") == "True":
        isRerunRequired = True
    if str(df_rerunTestCases['App Val'][testCaseID]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                    "bool_rerun_app_val") == "True":
        isRerunRequired = True
    if str(df_rerunTestCases['UI Val'][testCaseID]).lower() == 'fail' and configReader.read_config("Validations",
                                                                                                   "bool_rerun_ui_val") == "True":
        isRerunRequired = True
    print("Rerun required = " + str(isRerunRequired))
    return isRerunRequired


# To change the value of rerun testcases overall_status to empty in Report excel, so that it will set as Broken in
# case of any connectivity issues
def changeOverallStatusToEmpty(ls_TestCasesForRerun):
    wb = openpyxl.load_workbook(GlobalVariables.EXCEL_reportFilePath)
    sheet = wb['Sheet1']

    for rerun_tesecase in ls_TestCasesForRerun:
        for i in range(2,sheet.max_row+1):
            colNum_testcase = ExcelProcessor.getColumnNumberFromName("", sheet, 'Test Case ID')
            testcase = (sheet.cell(row=i, column=colNum_testcase)).value

            if testcase == rerun_tesecase:
                colNum_overallStatus = ExcelProcessor.getColumnNumberFromName("", sheet, 'OverAll Results')
                sheet.cell(row=i, column=colNum_overallStatus).value = ""
    wb.save(GlobalVariables.EXCEL_reportFilePath)


def rerunTestImmediately(testCaseID, testCaseFileName, rerunCount, request):
    print("Starting the immediate rerun")
    if setRerunCount(testCaseID, rerunCount):
        # make status empty
        rerunCommand = "pytest -v " + testCaseFileName + ".py::" + testCaseID + ' --alluredir='+DirectoryCreator.getDirectoryPath("AllureReport")
        print(rerunCommand)

        if rerunCount >= 0:
            # To send the testcaseID as a list to change the overall_Status as empty
            setOfRerunTest = set()
            setOfRerunTest.add(testCaseID)
            ls_TestCasesForRerun = list(setOfRerunTest)
            changeOverallStatusToEmpty(ls_TestCasesForRerun)

            print("$$$$$$$$$$$$$$$$$$$$ Rerun Immediately #################")
            os.system(rerunCommand)
        if rerunCount == -1 and configReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "false" and Base_Actions.is_log_capture_required("forLastRun_Capture_Logs") == "True":
            # print("log on failure method calling")
            # print("testCaseID", testCaseID)
            # print("getRerunCount(testCaseID)", int(getRerunCount(testCaseID)))
            print("isRerunRequiredImmediately(testCaseID)", isRerunRequiredImmediately(testCaseID))
            conftest.log_on_failure(request)
    else:
        print("Cannot perform rerun since the rerun count is 0 or the rerun sheet is not accessible.")


xl_RerunCountPath = "/home/ezetap/EzeAuto/TestCases/RerunCount.xlsx"


xl_Timestamp = "/home/ezetap/EzeAuto/TestCases/Timestamp.xlsx"


def prepareImmediateRerunExcel():
    # df_overallTClist = pd.read_excel("/home/oem/PycharmProjects/EzeAuto/DataProvider/TestCasesDetail.xlsx")

    # Added on Apr 11
    df_overallTClist = pd.read_excel("/home/ezetap/EzeAuto/TestCases/AllTestcaseSuite.xlsx")

    df_overallTClist.set_index('Test Case ID', inplace=True)
    # df_overallTClist.drop(columns=['File Name', 'Execute'], inplace=True)

    df_overallTClist.drop(columns=['File Name', 'Execute','Unnamed: 0'], inplace=True)

    # Added for adding rerun attempts in Report excel
    df_overallTClist.drop(columns=['Directory Name'], inplace=True)

    reRunCount = []
    for i in range(0, len(df_overallTClist.index)):
        # reRunCount.append(GlobalVariables.int_immediateRerunCount)
        try:
            configuredImmediateRerunCount = int(configReader.read_config("Validations", "int_rerun_count"))
            reRunCount.append(configuredImmediateRerunCount)
        except ValueError:
            print("Configured Immediate Rerun Count is Invalid")
            return None

    df_overallTClist['Rerun Count'] = reRunCount
    df_overallTClist.to_excel(xl_RerunCountPath, sheet_name="Rerun Count")


def prepareAtTheEndRerunExcel():
    df = pd.DataFrame({'Rerun Count': [int(configReader.read_config("Validations", "int_rerun_count"))]})
    print(df)
    writer = pd.ExcelWriter(xl_RerunCountPath, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Rerun At The End', index=False)
    writer.save()


# def suiteTriggringTime():
#     df = pd.DataFrame({'time': [str(datetime.now().time())]})
#     print(df)
#     writer = pd.ExcelWriter(xl_Timestamp, engine='xlsxwriter')
#     df.to_excel(writer, sheet_name='timestamp', index=False)
#     writer.save()


# def getTimeStamp():
#     try:
#         df_TClist = pd.read_excel(xl_Timestamp, sheet_name="timestamp")
#         # df_TClist.set_index('Test Case ID', inplace=True)
#         try:
#             # breakpoint()
#             # print(df_TClist['Rerun Count'][0])
#             return df_TClist['time'][0]
#         except:
#             None
#     except:
#         return -2


def getRerunCount(testCaseID):
    if configReader.read_config("Validations", "bool_rerun_immediately").lower() == "true":
        try:
            df_TClist = pd.read_excel(xl_RerunCountPath, sheet_name="Rerun Count")
            df_TClist.set_index('Test Case ID', inplace=True)
            try:
                return df_TClist['Rerun Count'][testCaseID]
            except:
                None
        except:
            return -2
    if configReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "true":
        try:
            df_TClist = pd.read_excel(xl_RerunCountPath, sheet_name="Rerun At The End")
            # df_TClist.set_index('Test Case ID', inplace=True)
            try:
                # breakpoint()
                # print(df_TClist['Rerun Count'][0])
                return df_TClist['Rerun Count'][0]
            except:
                None
        except:
            return -2


def setRerunCount(testCaseID, rerunCount):
    if configReader.read_config("Validations", "bool_rerun_immediately").lower() == "true":
        try:
            workbook = openpyxl.load_workbook(xl_RerunCountPath)
            sheet = workbook["Rerun Count"]

            rowNumber = ExcelProcessor.getRowNumberFromValue(workbook, sheet, 'Test Case ID',
                                                             testCaseID)
            columnNumber = ExcelProcessor.getColumnNumberFromName(workbook, sheet, 'Rerun Count')
            sheet.cell(row=rowNumber, column=columnNumber).value = rerunCount

            workbook.save(xl_RerunCountPath)
            workbook.close()
            return True
        except:
            return False

    if configReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "true":
        try:
            workbook = openpyxl.load_workbook(xl_RerunCountPath)
            sheet = workbook["Rerun At The End"]

            rowNumber = 2
            columnNumber = 1
            sheet.cell(row=rowNumber, column=columnNumber).value = rerunCount

            workbook.save(xl_RerunCountPath)
            workbook.close()
            return True
        except:
            return False


# def getRerunCountForAtTheEnd():
#     try:
#         df_TClist = pd.read_excel(xl_RerunCountPath, sheet_name="Rerun At The End")
#         # df_TClist.set_index('Test Case ID', inplace=True)
#         try:
#             # breakpoint()
#             # print(df_TClist['Rerun Count'][0])
#             return df_TClist['Rerun Count'][0]
#         except:
#             None
#     except:
#         return -2


# def setRerunCountForAtTheEnd(rerunCount):
#     try:
#         workbook = openpyxl.load_workbook(xl_RerunCountPath)
#         sheet = workbook["Rerun At The End"]
#
#         rowNumber = 2
#         columnNumber = 1
#         sheet.cell(row=rowNumber, column=columnNumber).value = rerunCount
#
#         workbook.save(xl_RerunCountPath)
#         workbook.close()
#         return True
#     except:
#         return False

# prepareImmediateRerunExcel()
