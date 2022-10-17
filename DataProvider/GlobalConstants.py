import os

apiValidation = True
dbValidation = True
portalValidation = True
appValidation = True
uiValidation = True

# "EVD" denotes "Empty validation done"
STR_EMPTY_VALIDATION_STATUS = "EVD"

# Column Names in Test Case details excel file
colName_TestCaseID = "Test Case ID"
colName_FileName = "File Name"
colName_Execute = "Execute"
colName_TCexecution = "TC Execution"
colName_APIval = "API Val"
colName_DBval = "DB Val"
colName_Portalval = "Portal Val"
colName_Appval = "App Val"
colName_UIval = "UI Val"
colName_ExecutionTime = "Execution Time (sec)"
colName_ValidationTime = "Validation Time (sec)"
colName_LogCollTime = "Log Coll Time (sec)"
colName_TotalTime = "Total Time (sec)"


EZEAUTO_MAIN_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(EZEAUTO_MAIN_DIR, 'Database')
SQLITE_DB_PATH = os.path.join(DATABASE_DIR, 'ezeauto.db')
RUNTIME_DIR = os.path.join(EZEAUTO_MAIN_DIR, 'Runtime')
DATAPROVIDER_DIR = os.path.join(EZEAUTO_MAIN_DIR, 'DataProvider')
DB_DETAILS_EXCEL_PATH = os.path.join(DATAPROVIDER_DIR, 'db_details.xlsx')

# FileNames
STR_CARD_DETAILS_FILE = "card_details.xlsx"

#ezetap device data info
DEVICE_DATA_TAGS = {"TXN_TYPE": "FE01", "CLEAR_PAN": "FE02", "CLEAR_EXPIRY": "FE03", "ENC_TRACK2": "FE04", "CLEAR_EMV_DATA": "FE05", "PIN_BLOCK": "1F01", "NAME": "FE06", "SERVICE_CODE": "FE08", "ENC_PAN": "FE09", "ENC_EXP": "FE0A", "TRACK1": "FE07", "AID_TAG": "9F06", "TC_TAG": "9F26", "APP_TYPE": "50", "TVR_TAG": "95", "TSI_TAG": "9B", "KSN_PIN":"FE0C","KSN_DATA":"FE0D"}
TWO_DIGIT_TAGS = ["50", "95", "9B",]
TAGS_WITH_LENGTH_IN_HEX = ["FE05", "FE09", "FE0D", "FE06", "FE04", "FE0C"]



ADMIN_USER_ROLES = ["ROLE_CLADMIN","ROLE_CLPROMO","ROLE_ORG_MANAGER","ROLE_TAG_ADMIN","ROLE_CLREFUND"]
APP_USER_ROLES = ["ROLE_CLADMIN","ROLE_CLAGENT", "ROLE_CLAGENT_REFUND", "ROLE_CLAGENTPORTAL", "ROLE_CLAGENTVOID","ROLE_CLREFUND"]
PORTAL_USER_ROLES = ["ROLE_CLSUPPORT", "ROLE_SU"]