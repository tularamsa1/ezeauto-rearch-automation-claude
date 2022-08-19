# These values are for updating number of each type of validations (API|DB, Portal, DB and App) in html report

bool_val_exe = True
setupCompletedSuccessfully = False

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
start_line_number_config = ''
start_line_number_closedloop = ''
start_line_number_q2 = ''


apiLogs = False
portalLogs = False
cnpWareLogs = False
middleWareLogs = False
config_logs = False
closedloop_logs = False
q2_logs = False

# portalSS = False


#These values are for creating final excel report
time_calc = None


# EXCEL_TC_Exe_Starting_Time = 00
# EXCEL_TC_Exe_completed_time = 00

# EXCEL_TC_Val_Starting_Time = 00
# EXCEL_TC_Val_completed_time = 00

# EXCEL_TC_LogColl_Starting_Time = 00
# EXCEL_TC_LogColl_completed_time = 00

EXCEL_testCaseName = "Default Testcase"
EXCEL_TC_Execution = "Skip"
str_api_val_result = "N/A"
str_db_val_result = "N/A"
str_portal_val_result = "N/A"
str_app_val_result = "N/A"
str_ui_val_result = "N/A"
str_chargeslip_val_result = "N/A"
str_api_response_code = "N/A"
str_api_response_time = "N/A"
str_api_response_size = "N/A"
EXCEL_Execution_Time = 00
EXCEL_Val_time = 00
EXCEL_LogCollTime = 00
EXCEL_Tot_Time = 00
EXCEL_testCaseFileName = ''

# For screenshots of App and Portal

bool_ss_app_val = "N/A"
bool_ss_portal_val = "N/A"
bool_ss_chargeslip_val = "N/A"
appDriver = ''
portalDriver = ''
charge_slip_driver = ''

passed1 = 0
count = 1

tc_markers = ""

df_testCasesDetail = ""

portal_username = ''
portal_password = ''

app_username = ''
app_password = ''
ssh = ''

LogCollTime = 0
list_deselected_testcases=[]

#Ezewallet Variables - Used in the fetch Recon scripts to calculate the amount and count of txns that is performed.
cash_txn_id = 0
selftopup_amt = 0
selftopup_count = 0
transfer_amt = 0
transfer_count = 0
withdraw_amt = 0
withdraw_count = 0
refund_amt = 0
refund_count = 0
collection_amt = 0
collection_count = 0


#Card Bin info
AXIS_VISA_DEBIT_BIN = "800001"
AXIS_MASTER_DEBIT_BIN = "800002"
AXIS_RUPAY_DEBIT_BIN = "800003"
AXIS_VISA_CREDIT_BIN = "800005"
AXIS_MASTER_CREDIT_BIN = "800006"
AXIS_RUPAY_CREDIT_BIN = "800007"





