import os

apiValidation = True
dbValidation = True
portalValidation = True
appValidation = True
uiValidation = True

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