from DataProvider import GlobalVariables
from Utilities import ConfigReader
import pytest_check as check

def validateAgainstPortal(expectedPortal, actualPortal):
    """
    This function is used to validate the expected and actual values fetched from the portal
    :param expectedPortal, actualPortal
    """
    if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
        print("=======   PORTAL Validation Started    =======")
        if len(expectedPortal) == len(actualPortal):
            if expectedPortal == {} and actualPortal == {}:
                GlobalVariables.str_portal_val_result = "N/A"
            elif expectedPortal == "" and actualPortal == "":
                GlobalVariables.str_portal_val_result = "N/A"
            else:
                GlobalVariables.str_portal_val_result = "Pass" # To update the testcase result in the Excel report & Validation Table.
                GlobalVariables.bool_ss_portal_val = "Passed"
                for key in expectedPortal:
                    if key in actualPortal:
                        if expectedPortal[key] == actualPortal[key]:
                            if str(ConfigReader.read_config("Validations", "bool_print_val_log_pass")).lower() == "true":
                                print("Expected value from PORTAL for the " + str(key) + ": ", expectedPortal[key])
                                print("Actual value from PORTAL for the " + str(key) + ": ", actualPortal[key])
                        else:
                            if str(ConfigReader.read_config("Validations", "bool_print_val_log_fail")).lower() == "true":
                                print("Expected value from PORTAL for the " + str(key) + ": ", expectedPortal[key])
                                print("Actual value from PORTAL for the " + str(key) + ": ", actualPortal[key])
                            GlobalVariables.str_portal_val_result = "Fail"
                            GlobalVariables.bool_ss_portal_val = "Failed"
                            check.equal(expectedPortal[key], actualPortal[key])
                    else:
                        print("key not in actual: ", key not in actualPortal)
                        print("Both expected and actual dictionary are having different keys")
                        GlobalVariables.str_portal_val_result = "Fail"
                        break
        else:
            print("Number of keys in actual and expected dictionaries are different.")
            print("Expected Portal dict: ", expectedPortal)
            print("Actual Portal dict: ", actualPortal)
            GlobalVariables.str_portal_val_result = "Fail"
        print("=======   PORTAL Validation Completed  =======")
    else:
        print("=======   PORTAL Validation Disabled  =======")
        GlobalVariables.str_portal_val_result = "N/A"


def validateAgainstAPP(expectedApp, actualApp):
    """
    This function is used to validate the expected and actual values fetched from the app
    :param expectedApp, actualApp
    """
    if (ConfigReader.read_config("Validations", "app_validation")) == "True":
        print("=======   APP Validation Started    =======")
        if len(expectedApp) == len(actualApp):
            if expectedApp == {} and actualApp == {}:
                GlobalVariables.str_app_val_result = "N/A"
            elif expectedApp == "" and actualApp == "":
                GlobalVariables.str_app_val_result = "N/A"
            else:
                GlobalVariables.str_app_val_result = "Pass" # To update the testcase result in the Excel report & Validation Table.
                GlobalVariables.bool_ss_app_val = "Passed"
                for key in expectedApp:
                    if key in actualApp:
                        if expectedApp[key] == actualApp[key]:
                            if str(ConfigReader.read_config("Validations", "bool_print_val_log_pass")).lower() == "true":
                                print("Expected value from App for the " + str(key) + ": ", expectedApp[key])
                                print("Actual value from App for the " + str(key) + ": ", actualApp[key])
                        else:
                            if str(ConfigReader.read_config("Validations", "bool_print_val_log_fail")).lower() == "true":
                                print("Expected value from App for the " + str(key) + ": ", expectedApp[key])
                                print("Actual value from App for the " + str(key) + ": ", actualApp[key])
                            GlobalVariables.str_app_val_result = "Fail"
                            GlobalVariables.bool_ss_app_val = "Failed"
                            check.equal(expectedApp[key], actualApp[key])
                    else:
                        print("key not in actual: ", key not in actualApp)
                        print("Both expected and actual dictionary are having different keys")
                        GlobalVariables.str_app_val_result = "Fail"
                        break
        else:
            print("Number of keys in actual and expected dictionaries are different.")
            print("Expected App dict: ", expectedApp)
            print("Actual App dict: ", actualApp)
            GlobalVariables.str_app_val_result = "Fail"
        print("=======   APP Validation Completed  =======")
    else:
        print("=======   APP Validation Disabled  =======")
        GlobalVariables.str_app_val_result = "N/A"


def validationAgainstAPI(expectedAPI, actualAPI):
    """
    This function is used to validate the expected and actual values fetched from the api
    :param expectedAPI, actualAPI
    """
    if (ConfigReader.read_config("Validations", "api_validation")) == "True":
        print("=======   API Validation Started    =======")
        if len(expectedAPI) == len(actualAPI):
            if expectedAPI == {} and actualAPI == {}:
                GlobalVariables.str_api_val_result = "N/A"
            elif expectedAPI == "" and actualAPI == "":
                GlobalVariables.str_api_val_result = "N/A"
            else:
                GlobalVariables.str_api_val_result = "Pass" # To update the testcase result in the Excel report & Validation Table.
                for key in expectedAPI:
                    if key in actualAPI:
                        if expectedAPI[key] == actualAPI[key]:
                            if str(ConfigReader.read_config("Validations", "bool_print_val_log_pass")).lower() == "true":
                                print("Expected value from Api for the " + str(key) + ": ", expectedAPI[key])
                                print("Actual value from Api for the " + str(key) + ": ", actualAPI[key])
                        else:
                            if str(ConfigReader.read_config("Validations", "bool_print_val_log_fail")).lower() == "true":
                                print("Expected value from Api for the " + str(key) + ": ", expectedAPI[key])
                                print("Actual value from Api for the " + str(key) + ": ", actualAPI[key])
                            GlobalVariables.str_api_val_result = "Fail"
                            check.equal(expectedAPI[key], actualAPI[key])
                    else:
                        print("key not in actual: ", key not in actualAPI)
                        print("Both expected and actual dictionary are having different keys")
                        GlobalVariables.str_api_val_result = "Fail"
                        break
        else:
            print("Number of keys in actual and expected dictionaries are different.")
            print("Expected Api dict: ", expectedAPI)
            print("Actual Api dict: ", actualAPI)
            GlobalVariables.str_api_val_result = "Fail"
        print("=======   API Validation Completed  =======")
    else:
        print("=======   API Validation Disabled  =======")
        GlobalVariables.str_api_val_result = "N/A"


def validateAgainstDB(expectedDB, actualDB):

    """
    This function is used to validate the expected and actual values fetched from the DB
    :param expectedDB, actualDB
    """
    if (ConfigReader.read_config("Validations", "db_validation")) == "True":
        print("=======   DB Validation Started    =======")
        if len(expectedDB) == len(actualDB):
            if expectedDB == {} and actualDB == {}:
                GlobalVariables.str_db_val_result = "N/A"
            elif expectedDB == "" and actualDB == "":
                GlobalVariables.str_db_val_result = "N/A"
            else:
                GlobalVariables.str_db_val_result = "Pass" # To update the testcase result in the Excel report & Validation Table.
                for key in expectedDB:
                    if key in actualDB:
                        if expectedDB[key] == actualDB[key]:
                            if str(ConfigReader.read_config("Validations", "bool_print_val_log_pass")).lower() == "true":
                                print("Expected value from DB for the " + str(key) + ": ", expectedDB[key])
                                print("Actual value from DB for the " + str(key) + ": ", actualDB[key])
                        else:
                            if str(ConfigReader.read_config("Validations", "bool_print_val_log_fail")).lower() == "true":
                                print("Expected value from DB for the " + str(key) + ": ", expectedDB[key])
                                print("Actual value from DB for the " + str(key) + ": ", actualDB[key])
                            GlobalVariables.str_db_val_result = "Fail"
                            check.equal(expectedDB[key], actualDB[key])
                    else:
                        print("key not in actual: ", key not in actualDB)
                        print("Both expected and actual dictionary are having different keys")
                        GlobalVariables.str_db_val_result = "Fail"
                        break
        else:
            print("Number of keys in actual and expected dictionaries are different.")
            print("Expected DB dict: ", expectedDB)
            print("Actual DB dict: ", actualDB)
            GlobalVariables.str_db_val_result = "Fail"
        print("=======   DB Validation Completed  =======")
    else:
        print("=======   DB Validation Disabled  =======")
        GlobalVariables.str_db_val_result = "N/A"


def validateAgainstUI(expectedUI, actualUI):
    """
     This function is used to validate the expected and actual values fetched from the UI
     :param expectedUI, actualUI
     """
    if (ConfigReader.read_config("Validations", "ui_validation")) == "True":
        print("=======   UI Validation Started    =======")
        if len(expectedUI) == len(actualUI):
            if expectedUI == {} and actualUI == {}:
                GlobalVariables.str_ui_val_result = "N/A"
            elif expectedUI == "" and actualUI == "":
                GlobalVariables.str_ui_val_result = "N/A"
            else:
                GlobalVariables.str_ui_val_result = "Pass"  # To update the testcase result in the Excel report & Validation Table.
                GlobalVariables.bool_ss_app_val = "Passed"
                for key in expectedUI:
                    if key in actualUI:
                        if expectedUI[key] == actualUI[key]:
                            if str(ConfigReader.read_config("Validations",
                                                            "bool_print_val_log_pass")).lower() == "true":
                                print("Expected value from UI for the " + str(key) + ": ", expectedUI[key])
                                print("Actual value from UI for the " + str(key) + ": ", actualUI[key])
                        else:
                            if str(ConfigReader.read_config("Validations",
                                                            "bool_print_val_log_fail")).lower() == "true":
                                print("Expected value from UI for the " + str(key) + ": ", expectedUI[key])
                                print("Actual value from UI for the " + str(key) + ": ", actualUI[key])
                            GlobalVariables.str_ui_val_result = "Fail"
                            GlobalVariables.bool_ss_app_val = "Failed"
                            check.equal(expectedUI[key], actualUI[key])
                    else:
                        print("key not in actual: ", key not in actualUI)
                        print("Both expected and actual dictionary are having different keys")
                        GlobalVariables.str_ui_val_result = "Fail"
                        break
        else:
            print("Number of keys in actual and expected dictionaries are different.")
            print("Expected UI dict: ", expectedUI)
            print("Actual UI dict: ", actualUI)
            GlobalVariables.str_ui_val_result = "Fail"
        print("=======   UI Validation Completed  =======")
    else:
        print("=======   UI Validation Disabled  =======")
        GlobalVariables.str_ui_val_result = "N/A"



