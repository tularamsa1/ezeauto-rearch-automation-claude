# These values are for updating number of each type of validations (API|DB, Portal, DB and App) in html report
import openpyxl
from Utilities import DirectoryCreator, configReader

#These variables are for adding to the second table (Validation) in HTML report
from Utilities import configReader

Incomplete_ExecutionCount = 0
api_ValidationFailureCount = 0
db_ValidationFailureCount = 0
portal_ValidationFailureCount = 0
app_ValidationFailureCount = 0
ui_ValidationFailureCount = 0


# These values are for log collection and SS
startLineNumberPortal = ''
startLineNumberAPI = ''
startLineNumberMiddlewware = ''
startLineNumberCnpware = ''
apiLogs = False
portalLogs = False
cnpWareLogs = False
middleWareLogs = False

# portalSS = False


#These values are for creating final excel report

EXCEL_fileName = "/home/oem/PycharmProjects/EzeAuto/TestData/ExcelDetails.xlsx"
EXCEL_workbook = None
EXCEL_rowNumber = 2

EXCEL_TC_Exe_Starting_Time = 00
EXCEL_TC_Exe_completed_time = 00

EXCEL_TC_Val_Starting_Time = 00
EXCEL_TC_Val_completed_time = 00

EXCEL_TC_LogColl_Starting_Time = 00
EXCEL_TC_LogColl_completed_time = 00

EXCEL_testCaseName = "Default Testcase"
EXCEL_TC_Execution = "Skip"
EXCEL_API_Val = "N/A"
EXCEL_DB_Val = "N/A"
EXCEL_Portal_Val = "N/A"
EXCEL_App_Val = "N/A"
EXCEL_UI_Val = "N/A"
EXCEL_Execution_Time = 00
EXCEL_Val_time = 00
EXCEL_LogCollTime = 00
EXCEL_Tot_Time = 00
EXCEL_testCaseFileName = ''

# For screenshots of App and Portal
appSS = False
portalSS = False
bool_ss_app_val = "N/A"
bool_ss_portal_val = "N/A"
appDriver = ''
portalDriver = ''

passed1 = 0
count = 1


df_testCasesDetail = ""
#EXCEL_reportFilePath = "/home/oem/PycharmProjects/EzeAuto/TestCase/Report.xlsx"
path = DirectoryCreator.getDirectoryPath("ExcelReport")+"/Report.xlsx"
EXCEL_reportFilePath = path
print("Excel Report path:",EXCEL_reportFilePath)


# rerunCount = 3
# int_immediateRerunCount = 1


portal_username = ''
portal_password = ''

app_username = ''
app_password = ''
ssh = ''