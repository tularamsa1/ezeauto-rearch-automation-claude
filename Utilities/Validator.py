from DataProvider import GlobalVariables,GlobalConstants
from Utilities import ConfigReader
import pytest_check as check
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


def validateAgainstPortal(expectedPortal, actualPortal):
    """
    This function is used to validate the expected and actual values fetched from the portal
    :param expectedPortal, actualPortal
    """
    lst_passed_fields = []
    lst_failed_fields = []
    expectedPortal, actualPortal = filter_values("portal", expectedPortal, actualPortal)
    if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
        print("=======   PORTAL Validation Started    =======")
        if len(expectedPortal) == len(actualPortal):
            if expectedPortal == {} and actualPortal == {}:
                print("Expected and actual values are empty.")
                if not GlobalVariables.str_portal_val_result in ("Fail", "Pass"):
                    GlobalVariables.str_portal_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            elif expectedPortal == "" and actualPortal == "":
                print("Expected and actual values are empty.")
                if not GlobalVariables.str_portal_val_result in ("Fail", "Pass"):
                    GlobalVariables.str_portal_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            else:
                if not GlobalVariables.str_portal_val_result == "Fail":
                    GlobalVariables.str_portal_val_result = "Pass"  # To update the testcase result in the Excel report & Validation Table.
                GlobalVariables.bool_ss_portal_val = "Passed"
                for key in expectedPortal:
                    if key in actualPortal:
                        if expectedPortal[key] == actualPortal[key]:
                            lst_passed_fields.append(key)
                        else:
                            lst_failed_fields.append(key)
                            GlobalVariables.str_portal_val_result = "Fail"
                            GlobalVariables.bool_ss_portal_val = "Failed"
                            check.equal(expectedPortal[key], actualPortal[key])
                    else:
                        lst_failed_fields.append(key)
                        print(f"Expected field {key} is not available in the actual values list.")
                        check.equal(f"Expected key {key}", f"Actual key ''", f"Expected field {key} is not available in"
                                                                             f" the actual values list.")
                        GlobalVariables.str_portal_val_result = "Fail"
                print_validation_result(expectedPortal, actualPortal, lst_passed_fields, lst_failed_fields)
        else:
            print("Number of keys in actual and expected dictionaries are different in Portal validation.")
            check.equal(len(expectedPortal), len(actualPortal), "Number of keys in actual and expected dictionaries "
                                                                "are different in Portal validation.")
            print("Expected dict: ", expectedPortal)
            print("Actual dict: ", actualPortal)
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
    lst_passed_fields = []
    lst_failed_fields = []
    expectedApp, actualApp = filter_values("app", expectedApp, actualApp)
    if (ConfigReader.read_config("Validations", "app_validation")) == "True":
        print("=======   APP Validation Started    =======")
        if len(expectedApp) == len(actualApp):
            if expectedApp == {} and actualApp == {}:
                print("Expected and actual values list is empty.")
                if not GlobalVariables.str_app_val_result in ("Fail","Pass"):
                    GlobalVariables.str_app_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            elif expectedApp == "" and actualApp == "":
                print("Expected and actual values list is empty.")
                if not GlobalVariables.str_app_val_result in ("Fail", "Pass"):
                    GlobalVariables.str_app_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            else:
                if not GlobalVariables.str_app_val_result == "Fail":
                    GlobalVariables.str_app_val_result = "Pass"  # To update the testcase result in the Excel report & Validation Table.
                GlobalVariables.bool_ss_app_val = "Passed"
                for key in expectedApp:
                    if key in actualApp:
                        if expectedApp[key] == actualApp[key]:
                            lst_passed_fields.append(key)
                        else:
                            lst_failed_fields.append(key)
                            GlobalVariables.str_app_val_result = "Fail"
                            GlobalVariables.bool_ss_app_val = "Failed"
                            check.equal(expectedApp[key], actualApp[key])
                    else:
                        lst_failed_fields.append(key)
                        print(f"Expected field {key} is not available in the actual values list.")
                        check.equal(f"Expected key {key}", f"Actual key ''", f"Expected field {key} is not available in"
                                                                             f" the actual values list.")
                        GlobalVariables.str_app_val_result = "Fail"
                print_validation_result(expectedApp, actualApp, lst_passed_fields, lst_failed_fields)
        else:
            print("Number of keys in actual and expected dictionaries are different in APP validation.")
            check.equal(len(expectedApp), len(actualApp), "Number of keys in actual and expected dictionaries "
                                                                "are different in App validation.")
            print("Expected dict: ", expectedApp)
            print("Actual dict: ", actualApp)
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
    lst_passed_fields = []
    lst_failed_fields = []
    expectedAPI, actualAPI = filter_values("api", expectedAPI, actualAPI)
    if (ConfigReader.read_config("Validations", "api_validation")) == "True":
        print("=======   API Validation Started    =======")
        if len(expectedAPI) == len(actualAPI):
            if expectedAPI == {} and actualAPI == {}:
                print("Expected and actual values list is empty.")
                if not GlobalVariables.str_api_val_result in ("Fail", "Pass"):
                    GlobalVariables.str_api_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            elif expectedAPI == "" and actualAPI == "":
                print("Expected and actual values list is empty.")
                if not GlobalVariables.str_api_val_result in ("Fail", "Pass"):
                    GlobalVariables.str_api_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            else:
                if not GlobalVariables.str_api_val_result == "Fail":
                    GlobalVariables.str_api_val_result = "Pass"  # To update the testcase result in the Excel report & Validation Table.
                for key in expectedAPI:
                    if key in actualAPI:
                        if expectedAPI[key] == actualAPI[key]:
                            lst_passed_fields.append(key)
                        else:
                            lst_failed_fields.append(key)
                            GlobalVariables.str_api_val_result = "Fail"
                            check.equal(expectedAPI[key], actualAPI[key])
                    else:
                        lst_failed_fields.append(key)
                        print(f"Expected field {key} is not available in the actual values list.")
                        check.equal(f"Expected key {key}", f"Actual key ''", f"Expected field {key} is not available in"
                                                                             f" the actual values list.")
                        GlobalVariables.str_api_val_result = "Fail"
                print_validation_result(expectedAPI, actualAPI, lst_passed_fields, lst_failed_fields)
        else:
            print("Number of keys in actual and expected dictionaries are different in API validation.")
            check.equal(len(expectedAPI), len(actualAPI), "Number of keys in actual and expected dictionaries "
                                                          "are different in API validation.")
            print("Expected dict: ", expectedAPI)
            print("Actual dict: ", actualAPI)
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
    lst_passed_fields = []
    lst_failed_fields = []
    expectedDB, actualDB = filter_values("db", expectedDB, actualDB)
    if (ConfigReader.read_config("Validations", "db_validation")) == "True":
        print("=======   DB Validation Started    =======")
        if len(expectedDB) == len(actualDB):
            if expectedDB == {} and actualDB == {}:
                print("Expected and actual values list is empty.")
                if not GlobalVariables.str_db_val_result in ("Fail","Pass"):
                    GlobalVariables.str_db_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            elif expectedDB == "" and actualDB == "":
                print("Expected and actual values list is empty.")
                if not GlobalVariables.str_db_val_result in ("Fail", "Pass"):
                    GlobalVariables.str_db_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            else:
                if not GlobalVariables.str_db_val_result == "Fail":
                    GlobalVariables.str_db_val_result = "Pass"  # To update the testcase result in the Excel report & Validation Table.
                for key in expectedDB:
                    if key in actualDB:
                        if expectedDB[key] == actualDB[key]:
                            lst_passed_fields.append(key)
                        else:
                            lst_failed_fields.append(key)
                            GlobalVariables.str_db_val_result = "Fail"
                            check.equal(expectedDB[key], actualDB[key])
                    else:
                        lst_failed_fields.append(key)
                        print(f"Expected field {key} is not available in the actual values list.")
                        check.equal(f"Expected key {key}", f"Actual key ''", f"Expected field {key} is not available in"
                                                                             f" the actual values list.")
                        GlobalVariables.str_db_val_result = "Fail"
                print_validation_result(expectedDB, actualDB, lst_passed_fields, lst_failed_fields)
        else:
            print("Number of keys in actual and expected dictionaries are different in DB validation.")
            check.equal(len(expectedDB), len(actualDB), "Number of keys in actual and expected dictionaries "
                                                          "are different in DB validation.")
            print("Expected dict: ", expectedDB)
            print("Actual dict: ", actualDB)
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
    lst_passed_fields = []
    lst_failed_fields = []
    expectedUI, actualUI = filter_values("ui", expectedUI, actualUI)
    if (ConfigReader.read_config("Validations", "ui_validation")) == "True":
        print("=======   UI Validation Started    =======")
        if len(expectedUI) == len(actualUI):
            if expectedUI == {} and actualUI == {}:
                print("Expected and actual values list is empty.")
                if not GlobalVariables.str_ui_val_result in ("Fail", "Pass"):
                    GlobalVariables.str_ui_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            elif expectedUI == "" and actualUI == "":
                print("Expected and actual values list is empty.")
                if not GlobalVariables.str_ui_val_result in ("Fail", "Pass"):
                    GlobalVariables.str_ui_val_result = GlobalConstants.STR_EMPTY_VALIDATION_STATUS
            else:
                if not GlobalVariables.str_ui_val_result == "Fail":
                    GlobalVariables.str_ui_val_result = "Pass"  # To update the testcase result in the Excel report & Validation Table.
                GlobalVariables.bool_ss_app_val = "Passed"
                for key in expectedUI:
                    if key in actualUI:
                        if expectedUI[key] == actualUI[key]:
                            lst_passed_fields.append(key)
                        else:
                            lst_failed_fields.append(key)
                            GlobalVariables.str_ui_val_result = "Fail"
                            GlobalVariables.bool_ss_app_val = "Failed"
                            check.equal(expectedUI[key], actualUI[key])
                    else:
                        lst_failed_fields.append(key)
                        print(f"Expected field {key} is not available in the actual values list.")
                        check.equal(f"Expected key {key}", f"Actual key ''", f"Expected field {key} is not available in"
                                                                             f" the actual values list.")
                        GlobalVariables.str_ui_val_result = "Fail"
                print_validation_result(expectedUI, actualUI, lst_passed_fields, lst_failed_fields)
        else:
            print("Number of keys in actual and expected dictionaries are different in UI validation.")
            check.equal(len(expectedUI), len(actualUI), "Number of keys in actual and expected dictionaries "
                                                        "are different in UI validation.")
            print("Expected dict: ", expectedUI)
            print("Actual dict: ", actualUI)
            GlobalVariables.str_ui_val_result = "Fail"
        print("=======   UI Validation Completed  =======")
    else:
        print("=======   UI Validation Disabled  =======")
        GlobalVariables.str_ui_val_result = "N/A"


def print_validation_result(expected_values: {}, acutal_values: {}, lst_passed_fields, lst_failed_fields):
    if str(ConfigReader.read_config("Validations", "bool_print_val_log_pass")).lower() == "true":
        if lst_passed_fields:
            print("Passed validations:")
            for field in lst_passed_fields:
                try:
                    print(f"Expected value of {field}   : {expected_values[field]}")
                    print(f"Actual value of {field}     : {acutal_values[field]}")
                    print()
                except Exception:
                    print(f"Field {field} is not available in the actual/expected values list.")
    if str(ConfigReader.read_config("Validations", "bool_print_val_log_fail")).lower() == "true":
        if lst_failed_fields:
            print("Failed validations:")
            for field in lst_failed_fields:
                try:
                    print(f"Expected value of {field}   : {expected_values[field]}")
                    print(f"Actual value of {field}     : {acutal_values[field]}")
                    print()
                except Exception:
                    print(f"Field {field} is not available in the actual values list.")


def filter_values(validation_type: str, expected_values: dict, actual_values: dict) -> dict and dict:
    """
    This method is used to filter out the values from the expected and actual values dictionary.
    This takes the expected and actual dictionary as input, reads the configuration and returns the filtered dictionary

    :param validation_type:str, expected_values:dict, actual_values:dict
    :return: dict and dict
    """
    if str(ConfigReader.read_config("selective_validation", "bool_enable_selective_validation")).lower() == "true":
        if str(ConfigReader.read_config("selective_validation", "bool_validate_selected_values")).lower() == "true":
            _lst_select_values_ = get_selected_values(validation_type)
            if "__all__" in _lst_select_values_ and len(_lst_select_values_) == 1:
                pass
            else:
                _lst_select_values_ = [value.strip() for value in _lst_select_values_]
                for value in list(expected_values):
                    if value not in _lst_select_values_:
                        del expected_values[value]
                for value in list(actual_values):
                    if value not in _lst_select_values_:
                        del actual_values[value]
        else:
            _lst_ignore_values_ = get_ignored_values(validation_type)
            if "__all__" in _lst_ignore_values_ and len(_lst_ignore_values_)==1:
                expected_values = {}
                actual_values = {}
            else:
                _lst_ignore_values_ = [value.strip() for value in _lst_ignore_values_]
                for value in list(expected_values):
                    if value in _lst_ignore_values_:
                        del expected_values[value]
                for value in list(actual_values):
                    if value in _lst_ignore_values_:
                        del actual_values[value]
    return expected_values, actual_values


def get_selected_values(validation_type: str) -> list:
    select_values_string = ""
    if validation_type == "api":
        select_values_string = ConfigReader.read_config("selective_validation", "lst_api_select_values")
    elif validation_type == "app":
        select_values_string = ConfigReader.read_config("selective_validation", "lst_app_select_values")
    elif validation_type == "chargeslip":
        select_values_string = ConfigReader.read_config("selective_validation", "lst_chargeslip_select_values")
    elif validation_type == "db":
        select_values_string = ConfigReader.read_config("selective_validation", "lst_db_select_values")
    elif validation_type == "portal":
        select_values_string = ConfigReader.read_config("selective_validation", "lst_portal_select_values")
    elif validation_type == "ui":
        select_values_string = ConfigReader.read_config("selective_validation", "lst_ui_select_values")
    else:
        logger.warn("Type of validation pass is incorrect. Validation filtering skipped.")
        print("Type of validation pass is incorrect. Validation filtering skipped.")

    select_values_string = select_values_string.strip("[]").split(",")
    return select_values_string


def get_ignored_values(validation_type: str) -> list:
    ignored_values_string = ""
    if validation_type == "api":
        ignored_values_string = ConfigReader.read_config("selective_validation", "lst_api_ignore_values")
    elif validation_type == "app":
        ignored_values_string = ConfigReader.read_config("selective_validation", "lst_app_ignore_values")
    elif validation_type == "chargeslip":
        ignored_values_string = ConfigReader.read_config("selective_validation", "lst_chargeslip_ignore_values")
    elif validation_type == "db":
        ignored_values_string = ConfigReader.read_config("selective_validation", "lst_db_ignore_values")
    elif validation_type == "portal":
        ignored_values_string = ConfigReader.read_config("selective_validation", "lst_portal_ignore_values")
    elif validation_type == "ui":
        ignored_values_string = ConfigReader.read_config("selective_validation", "lst_ui_ignore_values")
    else:
        logger.warn("Type of validation pass is incorrect. Validation filtering skipped.")
        print("Type of validation pass is incorrect. Validation filtering skipped.")

    ignored_values_string = ignored_values_string.strip("[]").split(",")
    return ignored_values_string
