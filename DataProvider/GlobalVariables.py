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
start_line_number_portal = ''
start_line_number_API = ''
start_line_number_middleware = ''
start_line_number_cnpware = ''
start_line_number_config = ''
start_line_number_closedloop = ''
start_line_number_q2 = ''
start_line_number_commx = ''
start_line_number_ezestore = ''


api_logs = False
portal_logs = False
cnpware_logs = False
middleware_logs = False
config_logs = False
closedloop_logs = False
q2_logs = False
commx_logs = False
ezestore_logs = False

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
str_device_model = "N/A"
str_firmware_version = "N/A"
str_MPOS_version = "N/A"
str_SA_version = "N/A"
str_device_id = "N/A"
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

ui_page = ''
portal_page = ''
charge_slip_page = ''
context = ''
play_wright = ''
browser = ''
portal_txn_page = ''

# These are to get the total number of fields validated in each category
tot_app_val = 0
tot_api_val = 0
tot_db_val = 0
tot_chargeslip_val = 0