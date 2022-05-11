from DataProvider import GlobalVariables
from Utilities.ReportProcessor import createStatusTable
from Utilities import ConfigReader
import pytest_check as check

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
    if (ConfigReader.read_config("Validations", "api_validation")) == "True":
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
    if (ConfigReader.read_config("Validations", "db_validation")) == "True":
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
    if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
        if values != "" and values!="Failed":
            print("======= Portal Validation Started   =======")
            Separate_values = values.split(",")
            success = "Pass"
            GlobalVariables.EXCEL_Portal_Val = "Pass"
            GlobalVariables.bool_ss_portal_val = "Passed"
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
                    GlobalVariables.bool_ss_portal_val = "Failed"
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
    if (ConfigReader.read_config("Validations", "app_validation")) == "True":
        if values != "" and values!="Failed":
            print("=======   App Validation Started    =======")
            Separate_values = values.split(",")
            success = "Pass"
            GlobalVariables.EXCEL_App_Val = "Pass"
            GlobalVariables.bool_ss_app_val = "Passed"

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
                    GlobalVariables.bool_ss_app_val = "Failed" # SS Value
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
    if (ConfigReader.read_config("Validations", "ui_validation")) == "True":
        if values != "" and values!="Failed":
            print("=======   UI Validation Started     =======")
            Separate_values = values.split(",")
            success = "Pass"
            GlobalVariables.EXCEL_UI_Val = "Pass"
            GlobalVariables.bool_ss_app_val = "Passed"           #Need discussion

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
                    GlobalVariables.bool_ss_app_val = "Failed" # SS Value           #Need discussion
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

#---------------------------------------------------
'''
def validateAgainstPortal(expectedPortal, actualPortal):
    if (configReader.read_config("Validations", "portal_validation")) == "True":
        print("=======   PORTAL Validation Started    =======")
        if len(expectedPortal) == len(actualPortal) and expectedPortal != "" and actualPortal != ""  and expectedPortal != "Failed" and actualPortal != "Failed":
            GlobalVariables.str_portal_val_result = "Pass" # To update the testcase result in the Excel report & Validation Table.
            GlobalVariables.bool_ss_portal_val = "Passed"
            for key in expectedPortal:
                if key in actualPortal:
                    if expectedPortal[key] == actualPortal[key]:
                        pass
                    else:
                        print("expectedVal from PORTAL for the " + str(key) + ": ", expectedPortal[key])
                        print("actualVal from PORTAL for the " + str(key) + ": ", actualPortal[key])
                        GlobalVariables.str_portal_val_result = "Fail"
                        GlobalVariables.bool_ss_portal_val = "Failed"
                        check.equal(expectedPortal[key], actualPortal[key])
                else:
                    print("key not in actual: ", key not in actualPortal)
                    print("Both expected and actual dictionary are having different keys")
                    GlobalVariables.str_portal_val_result = "Fail"
                    break
        elif expectedPortal == "" or actualPortal == "":
            GlobalVariables.str_portal_val_result = "N/A"
        elif len(expectedPortal) == len(actualPortal) and expectedPortal != "" and actualPortal != ""  and expectedPortal != "Failed" or actualPortal != "Failed":
            print("Both expected and actual dictionary are having different no. of keys")
            print("Expected Portal dict: ", expectedPortal)
            print("Actual Portal dict: ", actualPortal)
            GlobalVariables.str_portal_val_result = "Fail"
        print("=======   PORTAL Validation Completed  =======")
    else:
        print("Both expected and actual dictionary are not equal")
        print("=======   PORTAL Validation Disabled  =======")
        GlobalVariables.str_portal_val_result = "N/A"


def validateAgainstAPP(expectedApp, actualApp):
    if (configReader.read_config("Validations", "app_validation")) == "True":
        print("=======   APP Validation Started    =======")
        if len(expectedApp) == len(actualApp) and expectedApp != "" and actualApp != "" and expectedApp != "Failed" and actualApp != "Failed":
            GlobalVariables.str_app_val_result = "Pass"
            GlobalVariables.bool_ss_app_val = "Passed"
            for key in expectedApp:
                if key in actualApp:
                    if expectedApp[key] == actualApp[key]:
                        pass
                    else:
                        print("expectedVal from APP for the " + str(key) + ": ", expectedApp[key])
                        print("actualVal from APP for the " + str(key) + ": ", actualApp[key])
                        GlobalVariables.str_app_val_result = "Fail"
                        GlobalVariables.bool_ss_app_val = "Failed"
                        check.equal(expectedApp[key], actualApp[key])
                else:
                    print("key not in actual: ", key not in actualApp)
                    print("Both expected and actual dictionary are having different keys")
                    GlobalVariables.str_app_val_result = "Fail"
                    break
        elif expectedApp == "" or actualApp == "" or expectedApp is None or actualApp is None:
            GlobalVariables.str_app_val_result = "N/A"
        elif len(expectedApp) == len(actualApp) and expectedApp != "" and actualApp != "" and expectedApp != "Failed" or actualApp != "Failed":
            print("Both expected and actual dictionary are having different no. of keys")
            print("Expected APP dict: ", expectedApp)
            print("Actual APP dict: ", actualApp)
            GlobalVariables.str_app_val_result = "Fail"
        print("=======   APP Validation Completed  =======")
    else:
        print("Both expected and actual dictionary are not equal")
        print("=======   APP Validation Disabled  =======")
        GlobalVariables.str_app_val_result = "N/A"


def validationAgainstAPI(expectedAPI, actualAPI):
    if (configReader.read_config("Validations", "api_validation")) == "True":
        print("=======   API Validation Started    =======")
        if len(expectedAPI) == len(actualAPI) and expectedAPI != "" and actualAPI != "" and expectedAPI != "Failed" and actualAPI != "Failed":
            GlobalVariables.str_api_val_result = "Pass"
            for key in expectedAPI:
                if key in actualAPI:
                    if expectedAPI[key] == actualAPI[key]:
                        pass
                    else:
                        print("expectedVal from API for the " + str(key) + ": ", expectedAPI[key])
                        print("actualVal from API for the " + str(key) + ": ", actualAPI[key])
                        GlobalVariables.str_api_val_result = "Fail"
                        check.equal(expectedAPI[key], actualAPI[key])
                else:
                    print("key not in actual: ", key not in actualAPI)
                    print("Both expected and actual dictionary are having different keys")
                    GlobalVariables.str_api_val_result = "Fail"
                    break
        elif expectedAPI == "" or actualAPI == "":
            GlobalVariables.str_api_val_result =  "N/A"
        elif len(expectedAPI) != len(actualAPI) and expectedAPI != "" and actualAPI != "" and expectedAPI != "Failed" or actualAPI != "Failed":
            print("Both expected and actual dictionary are having different no. of keys")
            print("Expected API dict: ", expectedAPI)
            print("Actual API dict: ", actualAPI)
            GlobalVariables.str_api_val_result = "Fail"
        print("=======   API Validation Completed  =======")
    else:
        print("Both expected and actual dictionary are not equal")
        print("=======   API Validation Disabled  =======")
        GlobalVariables.str_api_val_result = "N/A"


def validateAgainstDB(expectedDB, actualDB):
    if (configReader.read_config("Validations", "db_validation")) == "True":
        print("=======   DB Validation Started    =======")
        if len(expectedDB) == len(actualDB) and expectedDB != "" and actualDB != "" and expectedDB != "Failed" and actualDB != "Failed":
            GlobalVariables.str_db_val_result = "Pass"
            for key in expectedDB:
                if key in actualDB:
                    if expectedDB[key] == actualDB[key]:
                        pass
                    else:
                        print("expectedVal from DB for the " + str(key) + ": ", expectedDB[key])
                        print("actualVal from DB for the " + str(key) + ": ", actualDB[key])
                        GlobalVariables.str_db_val_result = "Fail"
                        check.equal(expectedDB[key], actualDB[key])
                else:
                    print("key not in actual: ", key not in actualDB)
                    print("Both expected and actual dictionary are having different keys")
                    GlobalVariables.str_db_val_result = "Fail"
                    break
        elif expectedDB == "" or actualDB == "":
            GlobalVariables.str_db_val_result = "N/A"
        elif len(expectedDB) != len(actualDB) and expectedDB != "" and actualDB != "" and expectedDB != "Failed" or actualDB != "Failed":
            print("Both expected and actual dictionary are having different no. of keys")
            print("Expected DB dict: ", expectedDB)
            print("Actual DB dict: ", actualDB)
            GlobalVariables.str_db_val_result = "Fail"
        print("=======   DB Validation Completed  =======")
    else:
        print("Both expected and actual dictionary are not equal")
        print("=======   DB Validation Disabled  =======")
        GlobalVariables.str_db_val_result = "N/A"


def validateAgainstUI(expectedUI, actualUI):
    if (configReader.read_config("Validations", "ui_validation")) == "True":
        print("=======   UI Validation Started    =======")
        if len(expectedUI) == len(actualUI) and expectedUI != "" and actualUI != "" and expectedUI != "Failed" and actualUI != "Failed":
            GlobalVariables.str_ui_val_result = "Pass"
            GlobalVariables.bool_ss_app_val = "Passed"
            for key in expectedUI:
                if key in actualUI:
                    if expectedUI[key] == actualUI[key]:
                        pass
                    else:
                        print("expectedVal from UI for the " + str(key) + ": ", expectedUI[key])
                        print("actualVal from UI for the " + str(key) + ": ", actualUI[key])
                        GlobalVariables.str_ui_val_result = "Fail"
                        GlobalVariables.bool_ss_app_val = "Failed"
                        check.equal(expectedUI[key], actualUI[key])
                else:
                    print("key not in actual: ", key not in actualUI)
                    print("Both expected and actual dictionary are having different keys")
                    GlobalVariables.str_ui_val_result = "Fail"
                    break
        elif expectedUI == "" or actualUI == "":
            GlobalVariables.str_ui_val_result = "N/A"
        elif len(expectedUI) != len(actualUI) and expectedUI != "" and actualUI != "" and expectedUI != "Failed" or actualUI != "Failed":
            print("Both expected and actual dictionary are having different no. of keys")
            print("Expected UI dict: ", expectedUI)
            print("Actual UI dict: ", actualUI)
            GlobalVariables.str_ui_val_result = "Fail"
        print("=======   DB Validation Completed  =======")
    else:
        print("Both expected and actual dictionary are not equal")
        print("=======   DB Validation Disabled  =======")
        GlobalVariables.str_ui_val_result = "N/A"


def createStatusTable():
    apiVal = GlobalVariables.str_api_val_result
    dbVal = GlobalVariables.str_db_val_result
    portalVal = GlobalVariables.str_portal_val_result
    appVal = GlobalVariables.str_app_val_result
    uiVal = GlobalVariables.str_ui_val_result

    get_TC_Val_Time()
    print("portalVal: ", portalVal)
    print("")
    print("")

    # VALIDATION TABLE DETAILS
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

    if appVal == "Failed":
        myTable.add_row(["UI Validation", "Fail"])
    else:
        myTable.add_row(["UI Validation", uiVal])

    myTable.align = 'l'
    print(myTable)
    print("")
    print("")

    myTable1 = PrettyTable()
    myTable1.title = 'Debugging Info'
    myTable1.header = True
    myTable1.field_names = ["Type", "API", "Middleware", "Cnpware", "Portal", "App"]

    if Base_Actions.is_log_capture_required("bool_capt_log_fail") == "True" or Base_Actions.is_log_capture_required(
            "bool_capt_log_pass") == "True":
        if Base_Actions.is_log_capture_required("bool_capt_log_api") == "True" and GlobalVariables.apiLogs:
            apiLogs = 'Yes'
        else:
            apiLogs = 'No'
        if Base_Actions.is_log_capture_required(
                "bool_capt_log_middleware") == "True" and GlobalVariables.middleWareLogs:
            mWareLogs = 'Yes'
        else:
            mWareLogs = 'No'
        if Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True" and GlobalVariables.cnpWareLogs:
            cnpWareLogs = 'Yes'
        else:
            cnpWareLogs = 'No'
        if Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True" and GlobalVariables.portalLogs:
            portalLogs = 'Yes'
        else:
            portalLogs = 'No'
    else:
        apiLogs = 'No'
        mWareLogs = 'No'
        cnpWareLogs = 'No'
        portalLogs = 'No'

    if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == "Fail" or GlobalVariables.str_portal_val_result == "Fail" or GlobalVariables.str_app_val_result == "Fail" or GlobalVariables.str_ui_val_result == "Fail":
        myTable1.add_row(["Log Captured", apiLogs, mWareLogs, cnpWareLogs, portalLogs, "N/A"])
    else:
        myTable1.add_row(["Log Captured", apiLogs, mWareLogs, cnpWareLogs, portalLogs, "N/A"])

    # SCREENSHOT INFO
    appSS = 'No'
    portalSS = 'No'

    if Base_Actions.is_ss_capture_required("bool_capt_ss_pass") == "True":
        if GlobalVariables.bool_ss_portal_val == "Passed" or portalVal == 'Pass':
            portalSS = 'Yes'
        if GlobalVariables.bool_ss_app_val == "Passed" or appVal == 'Pass':
            appSS = 'Yes'

    if Base_Actions.is_ss_capture_required("bool_capt_ss_fail") == "True":
        if GlobalVariables.bool_ss_portal_val == "Failed" or portalVal == 'Failed':
            portalSS = 'Yes'

        if GlobalVariables.bool_ss_app_val == "Failed" or appVal == 'Failed':
            appSS = 'Yes'

    myTable1.add_row(["Screenshot Captured", "N/A", "N/A", "N/A", portalSS, appSS])
    myTable1.align = 'l'

    print(myTable1)
    print("")
    '''

