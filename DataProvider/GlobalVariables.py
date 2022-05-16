# These values are for updating number of each type of validations (API|DB, Portal, DB and App) in html report
from DataProvider.GlobalConstants import EXCEL_reportFilePath

bool_val_exe = True

#These variables are for adding to the second table (Validation) in HTML report

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

EXCEL_TC_Exe_Starting_Time = 00
EXCEL_TC_Exe_completed_time = 00

EXCEL_TC_Val_Starting_Time = 00
EXCEL_TC_Val_completed_time = 00

EXCEL_TC_LogColl_Starting_Time = 00
EXCEL_TC_LogColl_completed_time = 00

EXCEL_testCaseName = "Default Testcase"
EXCEL_TC_Execution = "Skip"
str_api_val_result = "N/A"
str_db_val_result = "N/A"
str_portal_val_result = "N/A"
str_app_val_result = "N/A"
str_ui_val_result = "N/A"
EXCEL_Execution_Time = 00
EXCEL_Val_time = 00
EXCEL_LogCollTime = 00
EXCEL_Tot_Time = 00
EXCEL_testCaseFileName = ''

# For screenshots of App and Portal

bool_ss_app_val = "N/A"
bool_ss_portal_val = "N/A"
appDriver = ''
portalDriver = ''

passed1 = 0
count = 1


df_testCasesDetail = ""
#EXCEL_reportFilePath = "/home/oem/PycharmProjects/EzeAuto/TestCase/Report.xlsx"

portal_username = ''
portal_password = ''

app_username = ''
app_password = ''
ssh = ''

LogCollTime = 0
list_deselected_testcases=[]