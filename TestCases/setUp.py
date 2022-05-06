import pymysql
import requests
import json
import logging
import pandas as pd
import sshtunnel
from prettytable import PrettyTable
import pytest_check as check

from PageFactory import Base_Actions
from Utilities import configReader
from Utilities.Util_Logs import Logger
log = Logger(__name__, logging.INFO)
from DataProvider import GlobalVariables
from datetime import datetime


# import datetime



def post(payload, API):
    url = configReader.read_config("APIs", "baseUrl") + configReader.read_config("APIs", API)
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    json_resp = json.loads(resp.text)
    # print("")
    # print("")
    # log.logger.info("================= Execution Logs : " + API + " API response =================")
    # log.logger.info(str(json_resp))
    # assert json_resp['success'] == True, "API call for " + API + " failed. Response:" + str(json_resp)
    return json_resp


def getValueFromDB(query):

    envi = configReader.read_config("APIs", "env")

    tunnel = sshtunnel.SSHTunnelForwarder(ssh_address_or_host=envi.lower(), remote_bind_address=('localhost', 3306))
    tunnel.start()
    conn = pymysql.connect(host='localhost', user='ezedemo', passwd='abc123', database='ezetap_demo',
                           port=tunnel.local_bind_port)

    data = pd.read_sql_query(query, conn)
    conn.close()
    tunnel.close()
    return data


def get_TC_Exe_Time():
    current = datetime.now()
    GlobalVariables.EXCEL_TC_Exe_completed_time = current.strftime("%H:%M:%S")
    FMT = '%H:%M:%S'
    totalExecutionTime = datetime.strptime(GlobalVariables.EXCEL_TC_Exe_completed_time, FMT) - datetime.strptime(str(
        GlobalVariables.EXCEL_TC_Exe_Starting_Time), FMT)

    # Converting time duration to seconds
    GlobalVariables.EXCEL_Execution_Time = sum(x * int(t) for x, t in zip([3600, 60, 1], str(totalExecutionTime).split(":")))

    # Converting time duration to milliseconds
    # GlobalVariables.EXCEL_Execution_Time = Exe_Time_Sec * 1000


def get_TC_Val_Time():
    current = datetime.now()
    GlobalVariables.EXCEL_TC_Val_completed_time = current.strftime("%H:%M:%S")
    print("TC Val completed time:", GlobalVariables.EXCEL_TC_Val_completed_time)
    FMT = '%H:%M:%S'
    totalValidationTime = datetime.strptime(GlobalVariables.EXCEL_TC_Val_completed_time, FMT) - datetime.strptime(str(
        GlobalVariables.EXCEL_TC_Val_Starting_Time), FMT)

    # Converting time duration to seconds
    GlobalVariables.EXCEL_Val_time = sum(x * int(t) for x, t in zip([3600, 60, 1], str(totalValidationTime).split(":")))

    # Converting time duration to milliseconds
    # GlobalVariables.EXCEL_Val_time = Val_Time_Sec * 1000


def get_Log_Collection_Time():
    current = datetime.now()
    GlobalVariables.EXCEL_TC_Val_completed_time = current.strftime("%H:%M:%S")
   # GlobalVariables.EXCEL_TC_Val_completed_time = current.strftime("%H:%M:%S")
    FMT = '%H:%M:%S'
    print("Log collection end time: ", GlobalVariables.EXCEL_TC_Val_completed_time)

    totalValidationTime = datetime.strptime(GlobalVariables.EXCEL_TC_Val_completed_time, FMT) - datetime.strptime(str(
        GlobalVariables.EXCEL_TC_LogColl_Starting_Time), FMT)

    # Converting time duration to seconds
    GlobalVariables.EXCEL_LogCollTime = sum(x * int(t) for x, t in zip([3600, 60, 1], str(totalValidationTime).split(":")))

    # Converting time duration to milliseconds
    # GlobalVariables.EXCEL_LogCollTime = Val_Time_Sec * 1000


def validateValues(APIRespValues, DBValues, PortalValues, APPValues):
    apiResult = validateAgainstAPIResp(APIRespValues)
    dbResult = validateAgainstDB(DBValues)
    portalResult = validateAgainstPortal(PortalValues)
    appResult = validateAgainstAPP(APPValues)

    createStatusTable(validateAgainstAPIResp(APIRespValues), validateAgainstDB(DBValues),
                    validateAgainstPortal(PortalValues), validateAgainstAPP(APPValues))


    # createStatusTable(apiResult, dbResult, portalResult, appResult)
    # if apiResult == "Fail" or dbResult == "Fail" or portalResult == "Fail" or appResult =="Fail" :
    #     return False
    # else:
    #     return True

def validateAgainstAPIResp(values):   #expected:actual,expected:actual,expected:actual
    if (configReader.read_config("Validations", "api_validation")) == "True":
        if values != "" and values!="Failed":
            print("=======   API Validation Started    =======")
            Separate_values = values.split(",")
            success = "Pass"
            GlobalVariables.EXCEL_API_Val = "Pass"
            for val in Separate_values:
                expectedVal = val.split(":")[0]
                actualVal = val.split(":")[1]
                if expectedVal == actualVal:
                    pass
                else:
                    print("expectedVal from API: " + expectedVal)
                    print("actualVal from API: " + actualVal)
                    success = "Fail"
                    GlobalVariables.EXCEL_API_Val = "Fail"
                    GlobalVariables.api_ValidationFailureCount += 1
                    check.equal(expectedVal, actualVal)
                    break
            print("=======   API Validation Completed  =======")
            print("")
            return success
        elif values=="":
            return "N/A"
        elif values == "Failed":
            return "Failed"
    else:
        print("API Validation Is Disabled")
        print("")
        return "N/A"


def validateAgainstDB(values):
    if (configReader.read_config("Validations", "db_validation")) == "True":
        if values != "" and values!="Failed":
            print("=======   DB Validation Started     =======")
            Separate_values = values.split(",")
            success = "Pass"
            GlobalVariables.EXCEL_DB_Val = "Pass"

            for val in Separate_values:

                expectedVal = val.split(":")[0]
                actualVal = val.split(":")[1]

                if expectedVal == actualVal:
                    pass
                else:
                    print("expectedVal from DB: " + expectedVal)
                    print("actualVal from DB  : " + actualVal)
                    success = "Fail"
                    GlobalVariables.EXCEL_DB_Val = "Fail"
                    GlobalVariables.db_ValidationFailureCount += 1
                    check.equal(expectedVal, actualVal)
                    break
            print("=======   DB Validation Completed   =======")
            print("")
            return success
        elif values=="":
            return "N/A"
        elif values == "Failed":
            return "Failed"
    else:
        print("DB Validation Is Disabled")
        print("")
        return "N/A"


def validateAgainstPortal(values):
    if (configReader.read_config("Validations", "portal_validation")) == "True":
        if values != "" and values!="Failed":
            print("======= Portal Validation Started   =======")
            Separate_values = values.split(",")
            success = "Pass"
            GlobalVariables.EXCEL_Portal_Val = "Pass"
            GlobalVariables.successPortal = "Passed"
            for val in Separate_values:
                expectedVal = val.split(":")[0]
                actualVal = val.split(":")[1]

                if expectedVal == actualVal:
                    print("Portal Validation result: ", GlobalVariables.EXCEL_Portal_Val)  # //////
                    pass
                else:
                    print("expectedVal from Portal: " + expectedVal)
                    print("actualVal from Portal  : " + actualVal)
                    success = "Fail"
                    GlobalVariables.EXCEL_Portal_Val = "Fail"
                    GlobalVariables.successPortal = "Failed"
                    GlobalVariables.portal_ValidationFailureCount += 1
                    check.equal(expectedVal, actualVal)
                    break
            print("======= Portal Validation Completed =======")
            print("")
            return success
        elif values == "":
            return "N/A"
        elif values == "Failed":
            return "Failed"
    else:
        print("Portal Validation Is Disabled")
        print("")
        return "N/A"


def validateAgainstAPP(values):
    if (configReader.read_config("Validations", "app_validation")) == "True":
        if values != "" and values!="Failed":
            print("=======   App Validation Started    =======")
            Separate_values = values.split(",")
            success = "Pass"
            GlobalVariables.EXCEL_App_Val = "Pass"
            GlobalVariables.successApp = "Passed"

            for val in Separate_values:
                expectedVal = val.split(":")[0]
                actualVal = val.split(":")[1]

                if expectedVal == actualVal:
                    pass
                else:
                    print("expectedVal from app: " + expectedVal)
                    print("actualVal from app  : " + actualVal)
                    success = "Fail"
                    GlobalVariables.EXCEL_App_Val = "Fail"
                    GlobalVariables.successApp = "Failed" # SS Value
                    GlobalVariables.app_ValidationFailureCount += 1
                    check.equal(expectedVal,actualVal)
                    break
            print("=======   App Validation Completed  =======")
            print("")
            return success
        elif values == "":
            return "N/A"
        elif values == "Failed":
            return "Failed"
    else:
        print("App Validation Is Disabled")
        print("")
        return "N/A"


def validateAgainstUI(values):
    if (configReader.read_config("Validations", "ui_validation")) == "True":
        if values != "" and values!="Failed":
            print("=======   UI Validation Started     =======")
            Separate_values = values.split(",")
            success = "Pass"
            GlobalVariables.EXCEL_UI_Val = "Pass"
            GlobalVariables.successApp = "Passed"           #Need discussion

            for val in Separate_values:
                expectedVal = val.split(":")[0]
                actualVal = val.split(":")[1]

                if expectedVal == actualVal:
                    pass
                else:
                    print("expectedVal from UI: " + expectedVal)
                    print("actualVal from UI  : " + actualVal)
                    success = "Fail"
                    GlobalVariables.EXCEL_UI_Val = "Fail"
                    GlobalVariables.successApp = "Failed" # SS Value           #Need discussion
                    GlobalVariables.ui_ValidationFailureCount += 1
                    check.equal(expectedVal,actualVal)
                    break
            print("=======   UI Validation Completed   =======")
            print("")
            return success
        elif values=="":
            return "N/A"
        elif values == "Failed":
            return "Failed"
    else:
        print("UI Validation Is Disabled")
        print("")
        return "N/A"


def createStatusTable(apiVal, dbVal, portalVal, appVal):
    get_TC_Val_Time()

    print("")
    print("")

    #VALIDATION TABLE DETAILS
    myTable = PrettyTable(["Validation Type", "Validation Status"])
    myTable.title = 'Validation Details'



    if apiVal == "Failed":
        myTable.add_row(["API Validation", "Fail"])
    else:
        myTable.add_row(["API Validation", apiVal])

    if dbVal == "Failed":
        myTable.add_row(["DB Validation", "Fail"])
    else:
        myTable.add_row(["DB Validation", dbVal])

    if portalVal == "Failed":
        myTable.add_row(["Portal Validation", "Fail"])
    else:
        myTable.add_row(["Portal Validation", portalVal])

    if appVal == "Failed":
        myTable.add_row(["App Validation", "Fail"])
    else:
        myTable.add_row(["App Validation", appVal])
    myTable.add_row(["UI Validation", "N/A"])

    myTable.align = 'l'
    print(myTable)
    print("")
    print("")


    myTable1 = PrettyTable()
    myTable1.title = 'Debugging Info'
    myTable1.header = True
    myTable1.field_names = ["Type", "API", "Middleware", "Cnpware", "Portal", "App"]

    # LOG INFO
    # if GlobalVariables.apiLogs:
    #     apiLogs = 'Yes'
    # else:
    #     apiLogs = 'No'
    # if GlobalVariables.middleWareLogs:
    #     mWareLogs = 'Yes'
    # else:
    #     mWareLogs = 'No'
    # if GlobalVariables.cnpWareLogs:
    #     cnpWareLogs = 'Yes'
    # else:
    #     cnpWareLogs = 'No'
    # if GlobalVariables.portalLogs:
    #     portalLogs = 'Yes'
    # else:
    #     portalLogs = 'No'

    if Base_Actions.enter_data_logs("For_Failed_TCS_fetch_Logs") == "True" or Base_Actions.enter_data_logs(
            "For_Passed_TCS_fetch_Logs") == "True":
        if Base_Actions.enter_data_logs("fetch_api_Logs") == "True" and GlobalVariables.apiLogs:
            apiLogs = 'Yes'
        else:
            apiLogs = 'No'
        if Base_Actions.enter_data_logs("fetch_middleware_Logs") == "True" and GlobalVariables.middleWareLogs:
            mWareLogs = 'Yes'
        else:
            mWareLogs = 'No'
        if Base_Actions.enter_data_logs("fetch_cnpware_Logs") == "True" and GlobalVariables.cnpWareLogs:
            cnpWareLogs = 'Yes'
        else:
            cnpWareLogs = 'No'
        if Base_Actions.enter_data_logs("fetch_portal_Logs") == "True" and GlobalVariables.portalLogs:
            portalLogs = 'Yes'
        else:
            portalLogs = 'No'
    else:
        apiLogs = 'No'
        mWareLogs = 'No'
        cnpWareLogs = 'No'
        portalLogs = 'No'

    # if BaseActions.enter_data_logs("fetch_ss") == "False":
    # if BaseActions.enter_data_logs("For_Failed_TCS_fetch_Logs") == "True" or BaseActions.enter_data_logs("For_Passed_TCS_fetch_Logs") == "True":
    if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.EXCEL_API_Val == "Fail" or GlobalVariables.EXCEL_DB_Val == "Fail" or GlobalVariables.EXCEL_Portal_Val == "Fail" or GlobalVariables.EXCEL_App_Val == "Fail" or GlobalVariables.EXCEL_UI_Val == "Fail":
        myTable1.add_row(["Log Captured", apiLogs, mWareLogs, cnpWareLogs, portalLogs, "N/A"])
        # else:
        #     myTable1.add_row(["Log Captured", 'NO', 'NO', 'NO', 'NO', "N/A"])
    else:
        myTable1.add_row(["Log Captured", apiLogs, mWareLogs, cnpWareLogs, portalLogs, "N/A"])


    # SCREENSHOT INFO
    appSS = 'N/A'
    portalSS = 'N/A'
    if Base_Actions.enter_data_logs("fetch_ss") == "True":
        if GlobalVariables.successPortal != "N/A":
            portalSS = 'Yes'
        if GlobalVariables.successApp != "N/A":
            appSS = 'Yes'

    if Base_Actions.enter_data_logs("fetch_ss") == "False":
        if GlobalVariables.successPortal == "Failed":
            portalSS = 'Yes'
        else:
            portalSS = "N/A"

        if GlobalVariables.successApp == "Failed":
            appSS = 'Yes'
        else:
            appSS = "N/A"

    myTable1.add_row(["Screenshot Captured", "N/A", "N/A", "N/A", portalSS, appSS])
    myTable1.align = 'l'

    print(myTable1)
    print("")

'''

def validateValues(expectedPortal, actualPortal,  expectedDB, actualDB, expectedAPI, actualAPI, expectedApp, actualApp):
    apiResult = validateAgainstAPI(expectedAPI, actualAPI)
    dbResult = validateAgainstDB(expectedDB, actualDB)
    portalResult = validateAgainstPortal(expectedPortal, actualPortal)
    appResult = validateAgainstAPP(expectedApp, actualApp)

    createStatusTable(apiResult, dbResult, portalResult, appResult)
    if apiResult == "Fail" or dbResult == "Fail" or portalResult == "Fail" or appResult == "Fail":
        return False
    else:
        return True


def validateAgainstPortal(expectedPortal, actualPortal):
    if (configReader.read_config("Validations", "portal_validation")) == "True":
        if len(expectedPortal) == len(actualPortal) and expectedPortal != "" and actualPortal != "":
            print("=======   PORTAL Validation Started    =======")
            match = "Pass"
            for key in expectedPortal:
                if key in actualPortal:
                    # print("key in actual: ", key in actualPortal)
                    if expectedPortal[key] == actualPortal[key]:
                        # print("Expected and Actual are equal, PORTAL validation passed")
                        match = "Pass"
                    else:
                        print("expectedVal from API for the " + str(key) + ": ", expectedPortal[key])
                        print("actualVal from API for the " + str(key) + ": ", actualPortal[key])
                        print("Expected and Actual are not equal, PORTAL validation failed")
                        check.equal(expectedPortal[key], actualPortal[key])
                        match = "Fail"
                else:
                    print("key not in actual: ", key not in actualPortal)
                    print("Both expected and actual dictionary are having different keys")
                    match = "Fail"
                    break
            print("=======   PORTAL Validation Completed  =======")
            return match
        elif expectedPortal == "" or actualPortal == "":
            return "N/A"
        elif expectedPortal == "Failed" or actualPortal == "Failed":
            return "Failed"
    else:
        print("Both expected and actual dictionary are not equal")
        print("=======   PORTAL Validation Disabled  =======")
        return "Fail"


def validateAgainstAPP(expectedApp, actualApp):
    if (configReader.read_config("Validations", "app_validation")) == "True":
        if len(expectedApp) == len(actualApp) and expectedApp != "" and actualApp != "":
            print("=======   APP Validation Started    =======")
            match = "Pass"
            for key in expectedApp:
                if key in actualApp:
                    # print("key in actual: ", key in actualApp)
                    if expectedApp[key] == actualApp[key]:
                        # print("Expected and Actual are equal, APP validation passed")
                        match = "Pass"
                    else:
                        print("expectedVal from API for the " + str(key) + ": ", expectedApp[key])
                        print("actualVal from API for the " + str(key) + ": ", actualApp[key])
                        print("Expected and Actual are not equal, APP validation failed")
                        check.equal(expectedApp[key], actualApp[key])
                        match = "Fail"
                else:
                    print("key not in actual: ", key not in actualApp)
                    print("Both expected and actual dictionary are having different keys")
                    match = "Fail"
                    break
            print("=======   APP Validation Completed  =======")
            return match
        elif expectedApp == "" or actualApp == "":
            return "N/A"
        elif expectedApp == "Failed" or actualApp == "Failed":
            return "Failed"
    else:
        print("Both expected and actual dictionary are not equal")
        print("=======   APP Validation Disabled  =======")
        return "Fail"


def validateAgainstAPI(expectedAPI, actualAPI):
    if (configReader.read_config("Validations", "api_validation")) == "True":
        if len(expectedAPI) == len(actualAPI) and expectedAPI != "" and actualAPI != "":
            print("=======   API Validation Started    =======")
            match = "Pass"
            for key in expectedAPI:
                if key in actualAPI:
                    # print("key in actual: ", key in actual)
                    if expectedAPI[key] == actualAPI[key]:
                        # print("Expected and Actual are equal, API validation passed")
                        match = "Pass"
                    else:
                        print("expectedVal from API for the " + str(key) + ": ", expectedAPI[key])
                        print("actualVal from API for the " + str(key) + ": ", actualAPI[key])
                        print("Expected and Actual are not equal, API validation failed")
                        check.equal(expectedAPI[key], actualAPI[key])
                        match = "Fail"
                else:
                    print("key not in actual: ", key not in actualAPI)
                    print("Both expected and actual dictionary are having different keys")
                    match = "Fail"
                    break
            print("=======   API Validation Completed  =======")
            return match
        elif expectedAPI == "" or actualAPI == "":
            return "N/A"
        elif expectedAPI == "Failed" or actualAPI == "Failed":
            return "Failed"
    else:
        print("Both expected and actual dictionary are not equal")
        print("=======   API Validation Disabled  =======")
        return "Fail"


def validateAgainstDB(expectedDB, actualDB):
    if (configReader.read_config("Validations", "db_validation")) == "True":
        if len(expectedDB) == len(actualDB) and expectedDB != "" and actualDB != "":
            print("=======   DB Validation Started    =======")
            match = "Pass"
            for key in expectedDB:
                if key in actualDB:
                    # print("key in actual: ", key in actualDB)
                    if expectedDB[key] == actualDB[key]:
                        # print("Expected and Actual are equal, DB validation passed")
                        match = "Pass"
                    else:
                        print("expectedVal from API for the " + str(key) + ": ", expectedDB[key])
                        print("actualVal from API for the " + str(key) + ": ", actualDB[key])
                        print("Expected and Actual are not equal, DB validation failed")
                        check.equal(expectedDB[key], actualDB[key])
                        match = "Fail"
                else:
                    print("key not in actual: ", key not in actualDB)
                    print("Both expected and actual dictionary are having different keys")
                    match = "Fail"
                    break
            print("=======   DB Validation Completed  =======")
            return match
        elif expectedDB == "" or actualDB == "":
            return "N/A"
        elif expectedDB == "Failed" or actualDB == "Failed":
            return "Failed"
    else:
        print("Both expected and actual dictionary are not equal")
        print("=======   DB Validation Disabled  =======")
        return "Fail"
        '''


