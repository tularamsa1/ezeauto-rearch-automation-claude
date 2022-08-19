import os

apiValidation = True
dbValidation = True
portalValidation = True
appValidation = True
uiValidation = True

#"EVD" denotes "Empty validation done"
STR_EMPTY_VALIDATION_STATUS = "EVD"

#Column Names in Test Case details excel file
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

ADMIN_USER_ROLES = ["ROLE_CLSUPPORT","ROLE_CLADMIN","ROLE_CLAGENT","ROLE_CLAGENT_REFUND","ROLE_CLPROMO","ROLE_ORG_MANAGER","ROLE_CLAGENTPORTAL","ROLE_TAG_ADMIN","ROLE_CLAGENTVOID","ROLE_CLREFUND"]
AGENT_USER_ROLES = ["ROLE_CLAGENT","ROLE_CLAGENT_REFUND","ROLE_CLAGENTPORTAL","ROLE_CLAGENTVOID"]
SUPER_USER_ROLES = ["ROLE_SU"]


#Ezewallet Merchant and User Creds
ORG = "EZEWALLETMERCHANT"
ADMIN_USER = "7777770001"
ADMIN_PASSWORD = "A123456"
AGENT_USER = "7777770002"
AGENT_PASSWORD = "A123456"
ADMIN_USER_ROLES = ["ROLE_CLADMIN","ROLE_CLPROMO","ROLE_ORG_MANAGER","ROLE_TAG_ADMIN","ROLE_CLREFUND"]
APP_USER_ROLES = ["ROLE_CLAGENT", "ROLE_CLAGENT_REFUND", "ROLE_CLAGENTPORTAL", "ROLE_CLAGENTVOID"]
PORTAL_USER_ROLES = ["ROLE_CLSUPPORT", "ROLE_SU"]