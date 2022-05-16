import datetime
import time
from datetime import datetime
from random import randint
import pytest
from DataProvider import GlobalVariables
from Utilities import ReportProcessor, Validator

# API|DB VAL WILL FAIL
from Utilities import ConfigReader
from Utilities.ReportProcessor import updateTestCaseResult


@pytest.mark.usefixtures("log_on_success", "method_setup")
# @pytest.mark.usefixtures("method_ReportProcessor", "session_ReportProcessor")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
# @pytest.mark.flaky(reruns = 2)
def test_success():
    try:
        GlobalVariables.apiLogs = True
        GlobalVariables.portalLogs = True
        GlobalVariables.cnpWareLogs = True
        GlobalVariables.middleWareLogs = False

        msg = ""

        try:
            print("EXECUTING FIRST TEST CASE : SUCCESS")
            time.sleep(1)
            # i = 1/00
            ReportProcessor.get_TC_Exe_Time()  # Get execution time
        except Exception as e:
            print("Exception is: ", e)
            ReportProcessor.get_TC_Exe_Time()
            print("Testcase did not complete due to exception in testcase execution")
            print("")
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            # ReportProcessor.createStatusTable1()
            pytest.fail("Testcase did not complete due to exception in testcase execution")

        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                time.sleep(1)
                expectedAPIVal = {'amount': 90, 'Type': 'CASH', }
                actualAPIVal = {'amount': 90, 'Type': 'CASH', }
                # i = 1 / 00
                Validator.validationAgainstAPI(expectedAPIVal, actualAPIVal)
            except Exception as e:
                print("Exception is: ", e)
                print("API Validation did not complete due to exception")
                msg = msg + "API Validation did not complete due to exception\n"
                print("")
                GlobalVariables.api_ValidationFailureCount += 1
                # expectedAPIVal = "Failed"
                # actualAPIVal = "Failed"
                GlobalVariables.str_api_val_result = "Fail"
                GlobalVariables.bool_val_exe = False
            # ReportProcessor.validationAgainstAPI(expectedAPIVal, actualAPIVal)

        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                time.sleep(1)
                expectedDBVal = {'amount': 90, 'Type': 'CASH',}
                actualDBVal = {'amount': 90, 'Type': 'CASH', }
                # i = 1 / 00
                Validator.validateAgainstDB(expectedDBVal, actualDBVal)
            except Exception as e:
                print("Exception is: ", e)
                print("DB Validation did not complete due to exception in reading values from DB")
                msg = msg + "DB Validation did not complete due to exception in reading values from DB\n"
                print("")
                GlobalVariables.db_ValidationFailureCount += 1
                # expectedDBVal = 'Failed'
                # actualDBVal = 'Failed'
                GlobalVariables.str_db_val_result = "Fail"
                GlobalVariables.bool_val_exe = False
            # ReportProcessor.validateAgainstDB(expectedDBVal, actualDBVal)

        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                time.sleep(1)
                expectedPortalVal = {'amount': 90, 'Type': 'CASH', }
                actualPortalVal = {'amount': 90, 'Type': 'CASH', }
                # i = 1 / 00
                Validator.validateAgainstPortal(expectedPortalVal, actualPortalVal)
            except Exception as e:
                print("Exception is: ", e)
                print("Portal Validation did not complete due to exception in reading values from portal")
                msg = msg + "Portal Validation did not complete due to exception in reading values from portal\n"
                print("")
                GlobalVariables.portal_ValidationFailureCount += 1
                # expectedPortalVal = "Failed"
                # actualPortalVal = "Failed"
                GlobalVariables.str_portal_val_result = "Fail"
                GlobalVariables.bool_val_exe = False
            # ReportProcessor.validateAgainstPortal(expectedPortalVal, actualPortalVal)

    finally:
        ReportProcessor.updateTestCaseResult(msg)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_success_2():
    try:
        GlobalVariables.apiLogs = True
        # GlobalVariables.portalLogs = True
        # GlobalVariables.cnpWareLogs = True
        # GlobalVariables.middleWareLogs = False

        msg = ""

        try:
            print("EXECUTING FIRST TEST CASE : SUCCESS")
            time.sleep(1)
            # i = 1/00
            ReportProcessor.get_TC_Exe_Time()  # Get execution time
        except Exception as e:
            print("Exception is: ", e)
            ReportProcessor.get_TC_Exe_Time()
            print("Testcase did not complete due to exception in testcase execution")
            print("")
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            # ReportProcessor.createStatusTable1()
            pytest.fail("Testcase did not complete due to exception in testcase execution")

        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        try:
            time.sleep(1)
            expectedAPIVal = {'amount': 90, 'Type': 'CASH', }
            actualAPIVal = {'amount': 90, 'Type': 'CASH', }
            # i = 1 / 00
        except Exception as e:
            print("Exception is: ", e)
            print("API Validation did not complete due to exception")
            msg = msg + "API Validation did not complete due to exception\n"
            print("")
            GlobalVariables.api_ValidationFailureCount += 1
            expectedAPIVal = "Failed"
            actualAPIVal = "Failed"
            GlobalVariables.str_api_val_result = "Fail"
            success_Val_Execution = False

        try:
            time.sleep(1)
            expectedDBVal = {'amount': 90, 'Type': 'CASH', }
            actualDBVal = {'amount': 90, 'Type': 'CASH', }
            # i = 1 / 00
        except Exception as e:
            print("Exception is: ", e)
            print("DB Validation did not complete due to exception in reading values from DB")
            msg = msg + "DB Validation did not complete due to exception in reading values from DB\n"
            print("")
            GlobalVariables.db_ValidationFailureCount += 1
            expectedDBVal = 'Failed'
            actualDBVal = 'Failed'
            GlobalVariables.str_db_val_result = "Fail"
            success_Val_Execution = False

        try:
            time.sleep(1)
            expectedPortalVal = {'amount': 90, 'Type': 'CASH', }
            actualPortalVal = {'amount': 90, 'Type': 'CASH', }
            # i = 1 / 00
        except Exception as e:
            print("Exception is: ", e)
            print("Portal Validation did not complete due to exception in reading values from portal")
            msg = msg + "Portal Validation did not complete due to exception in reading values from portal\n"
            print("")
            GlobalVariables.portal_ValidationFailureCount += 1
            expectedPortalVal = "Failed"
            actualPortalVal = "Failed"
            GlobalVariables.str_portal_val_result = "Fail"
            success_Val_Execution = False

        Validator.validationAgainstAPI(expectedAPIVal, actualAPIVal)
        Validator.validateAgainstDB(expectedDBVal, actualDBVal)
        Validator.validateAgainstPortal(expectedPortalVal, actualPortalVal)

    finally:
        ReportProcessor.updateTestCaseResult(msg)


def test_success_1():
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = True
    GlobalVariables.cnpWareLogs = True
    GlobalVariables.middleWareLogs = False
    global success_Val_Execution
    success_Val_Execution = True

    try:
        print("EXECUTING FIRST TEST CASE : SUCCESS")
        time.sleep(1)
        ReportProcessor.get_TC_Exe_Time()  # Get execution time
    except:
        ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

    else:
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        try:
            time.sleep(1)
            expectedAPIValues = "qwerty:qwerty,ABCD:ABCD"
        except:
            print("API|DB Validation did not complete due to exception")
            print("")
            GlobalVariables.api_ValidationFailureCount += 1
            expectedAPIValues = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        try:
            time.sleep(1)
            expectedDBValues = "10.0:10.0,787878:787878"

        except:
            print("DB Validation did not complete due to exception in reading values from DB")
            print("")
            GlobalVariables.db_ValidationFailureCount += 1
            expectedDBValues = "Failed"
            GlobalVariables.EXCEL_DB_Val = "Fail"
            success_Val_Execution = False

        try:
            time.sleep(1)
            i = randint(1, 3)
            expectedPortalValues = str(i) + ":2"
            # expectedPortalValues = "CASH:CASH,909090:909090"
        except:
            print("Portal Validation did not complete due to exception in reading values from portal")
            print("")
            GlobalVariables.portal_ValidationFailureCount += 1
            expectedPortalValues = "Failed"
            GlobalVariables.EXCEL_Portal_Val = "Fail"
            success_Val_Execution = False

        success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")

        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()


@pytest.mark.dbVal
@pytest.mark.apiVal
@pytest.mark.portalVal
@pytest.mark.usefixtures("log_on_failure", "log_on_success")
# @pytest.mark.flaky(reruns = 2)
def test_Exe_Failure(method_ReportProcessor):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = True
    GlobalVariables.cnpWareLogs = True
    GlobalVariables.middleWareLogs = False
    global success_Val_Execution
    success_Val_Execution = True
    time.sleep(2)
    try:
        print("EXECUTING SECOND TEST CASE : EXECUTION FAILURE")
        time.sleep(2)
        # a = randint(1,2)

        ReportProcessor.get_TC_Exe_Time()  # Get execution time
    except:
        ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1

        pytest.fail()

    else:
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        try:
            time.sleep(1)
            # expectedAPIValues = "qwerty:qwerty,zxcv:zxcv"
            a = randint(1, 2)
            expectedAPIValues = str(a) + ":2"
            # expectedAPIValues = str(3)+":2"
        except:
            print("API|DB Validation did not complete due to exception")
            print("")
            GlobalVariables.api_ValidationFailureCount += 1
            expectedAPIValues = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        try:
            time.sleep(1)
            expectedDBValues = "10.0:10.0,787878:787878"
        except:
            print("DB Validation did not complete due to exception in reading values from DB")
            print("")
            GlobalVariables.db_ValidationFailureCount += 1
            expectedDBValues = "Failed"
            GlobalVariables.EXCEL_DB_Val = "Fail"
            success_Val_Execution = False

        try:
            time.sleep(1)
            expectedPortalValues = "CASH:CASH,909090:909090"
        except:
            print("Portal Validation did not complete due to exception in reading values from portal")
            print("")
            GlobalVariables.portal_ValidationFailureCount += 1
            expectedPortalValues = "Failed"
            GlobalVariables.EXCEL_Portal_Val = "Fail"
            success_Val_Execution = False

        success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")

        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()


report = "report" + str(datetime.now())


@pytest.mark.dbVal
# @pytest.mark.apiVal
@pytest.mark.portalVal
@pytest.mark.usefixtures("log_on_failure", "log_on_success")
# @pytest.mark.flaky(reruns = 2)
def test_api_val_exe_failure(method_setup):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = True
    GlobalVariables.cnpWareLogs = True
    GlobalVariables.middleWareLogs = True
    global success_Val_Execution
    success_Val_Execution = True

    try:
        print("EXECUTING THIRD TEST CASE : API|DB VAL EXE FAILURE")
        time.sleep(3)
        ReportProcessor.get_TC_Exe_Time()  # Get execution time
    except:
        ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1

        pytest.fail()

    else:
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        try:
            time.sleep(1)
            # a = 1/0
            # expectedAPIValues = "qwerty:qwerty,zxcv:zxcv"
            i = randint(1, 2)
            expectedAPIValues = str(i) + ":2"
            # expectedAPIValues = str(2) + ":2"
        except:
            print("API|DB Validation did not complete due to exception")
            print("")
            GlobalVariables.api_ValidationFailureCount += 1
            expectedAPIValues = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        try:
            time.sleep(1)
            expectedDBValues = "10.0:10.0,787878:787878"
        except:
            print("DB Validation did not complete due to exception in reading values from DB")
            print("")
            GlobalVariables.db_ValidationFailureCount += 1
            expectedDBValues = "Failed"
            GlobalVariables.EXCEL_DB_Val = "Fail"
            success_Val_Execution = False

        try:
            time.sleep(1)
            expectedPortalValues = "CASH:CASH,909090:909090"
        except:
            print("Portal Validation did not complete due to exception in reading values from portal")
            print("")
            GlobalVariables.portal_ValidationFailureCount += 1
            expectedPortalValues = "Failed"
            GlobalVariables.EXCEL_Portal_Val = "Fail"
            success_Val_Execution = False

        success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")

        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()

# @pytest.mark.usefixtures("log_on_failure","log_on_success")
# def test_DB_Val_Exe_Failure(method_ReportProcessor, session_ReportProcessor):
#     GlobalVariables.apiLogs = False
#     GlobalVariables.portalLogs = False
#     GlobalVariables.cnpWareLogs = False
#     GlobalVariables.middleWareLogs = False
#     global success_Val_Execution
#     success_Val_Execution = True
#
#     try:
#         print("EXECUTING FOURTH TEST CASE : DB VAL EXE FAILURE")
#         time.sleep(2)
#         ReportProcessor.get_TC_Exe_Time() # Get execution time
#     except:
#         ReportProcessor.get_TC_Exe_Time()
#         print("Testcase did not complete due to exception in testcase execution")
#         print("")
#         GlobalVariables.EXCEL_TC_Execution = "Fail"
#         GlobalVariables.Incomplete_ExecutionCount += 1
#
#         pytest.fail()
#
#     else:
#         GlobalVariables.EXCEL_TC_Execution = "Pass"
#         current = datetime.now()
#         GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
#
#
#         try:
#             time.sleep(1)
#             expectedAPIValues = "qwerty:qwerty,zxcv:zxcv"
#         except:
#             print("API|DB Validation did not complete due to exception")
#             print("")
#             GlobalVariables.api_ValidationFailureCount += 1
#             expectedAPIValues = "Failed"
#             GlobalVariables.EXCEL_API_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             a= 1/0
#             expectedDBValues = "10.0:10.0,787878:787878"
#         except:
#             print("DB Validation did not complete due to exception in reading values from DB")
#             print("")
#             GlobalVariables.db_ValidationFailureCount += 1
#             expectedDBValues = "Failed"
#             GlobalVariables.EXCEL_DB_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedPortalValues = "CASH:CASH,909090:909090"
#         except:
#             print("Portal Validation did not complete due to exception in reading values from portal")
#             print("")
#             GlobalVariables.portal_ValidationFailureCount += 1
#             expectedPortalValues = "Failed"
#             GlobalVariables.EXCEL_Portal_Val = "Fail"
#             success_Val_Execution = False
#
#         success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")
#
#         if success_Val_Execution == False:
#             if success == False:
#                 pass
#             else:
#                 pytest.fail()
#
#
#
# @pytest.mark.usefixtures("log_on_failure","log_on_success")
# def test_portal_val_exe_failure(method_ReportProcessor, session_ReportProcessor):
#     GlobalVariables.apiLogs = False
#     GlobalVariables.portalLogs = False
#     GlobalVariables.cnpWareLogs = False
#     GlobalVariables.middleWareLogs = False
#     global success_Val_Execution
#     success_Val_Execution = True
#
#     try:
#         print("EXECUTING FIFTH TEST CASE : PORTAL VAL EXE FAILURE")
#         time.sleep(2)
#         ReportProcessor.get_TC_Exe_Time() # Get execution time
#     except:
#         ReportProcessor.get_TC_Exe_Time()
#         print("Testcase did not complete due to exception in testcase execution")
#         print("")
#         GlobalVariables.EXCEL_TC_Execution = "Fail"
#         GlobalVariables.Incomplete_ExecutionCount += 1
#
#         pytest.fail()
#
#     else:
#         GlobalVariables.EXCEL_TC_Execution = "Pass"
#         current = datetime.now()
#         GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
#
#
#         try:
#             time.sleep(1)
#             expectedAPIValues = "qwerty:qwerty,zxcv:zxcv"
#         except:
#             print("API|DB Validation did not complete due to exception")
#             print("")
#             GlobalVariables.api_ValidationFailureCount += 1
#             expectedAPIValues = "Failed"
#             GlobalVariables.EXCEL_API_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedDBValues = "10.0:10.0,787878:787878"
#         except:
#             print("DB Validation did not complete due to exception in reading values from DB")
#             print("")
#             GlobalVariables.db_ValidationFailureCount += 1
#             expectedDBValues = "Failed"
#             GlobalVariables.EXCEL_DB_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             a =1/0
#             expectedPortalValues = "CASH:CASH,909090:909090"
#         except:
#             print("Portal Validation did not complete due to exception in reading values from portal")
#             print("")
#             GlobalVariables.portal_ValidationFailureCount += 1
#             expectedPortalValues = "Failed"
#             GlobalVariables.EXCEL_Portal_Val = "Fail"
#             success_Val_Execution = False
#
#         success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")
#
#         if success_Val_Execution == False:
#             if success == False:
#                 pass
#             else:
#                 pytest.fail()
#
#
#
# @pytest.mark.usefixtures("log_on_failure","log_on_success")
# def test_api_val_failure(method_ReportProcessor, session_ReportProcessor):
#     GlobalVariables.apiLogs = False
#     GlobalVariables.portalLogs = False
#     GlobalVariables.cnpWareLogs = False
#     GlobalVariables.middleWareLogs = False
#     global success_Val_Execution
#     success_Val_Execution = True
#
#     try:
#         print("EXECUTING SIXTH TEST CASE : API|DB VALIDATION FAILURE")
#         time.sleep(2)
#         ReportProcessor.get_TC_Exe_Time() # Get execution time
#     except:
#         ReportProcessor.get_TC_Exe_Time()
#         print("Testcase did not complete due to exception in testcase execution")
#         print("")
#         GlobalVariables.EXCEL_TC_Execution = "Fail"
#         GlobalVariables.Incomplete_ExecutionCount += 1
#
#         pytest.fail()
#
#     else:
#         GlobalVariables.EXCEL_TC_Execution = "Pass"
#         current = datetime.now()
#         GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
#
#
#         try:
#             time.sleep(1)
#             expectedAPIValues = "qwerty:qwerty,zxcv:abcd"
#         except:
#             print("API|DB Validation did not complete due to exception")
#             print("")
#             GlobalVariables.api_ValidationFailureCount += 1
#             expectedAPIValues = "Failed"
#             GlobalVariables.EXCEL_API_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedDBValues = "10.0:10.0,787878:787878"
#         except:
#             print("DB Validation did not complete due to exception in reading values from DB")
#             print("")
#             GlobalVariables.db_ValidationFailureCount += 1
#             expectedDBValues = "Failed"
#             GlobalVariables.EXCEL_DB_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedPortalValues = "CASH:CASH,909090:909090"
#         except:
#             print("Portal Validation did not complete due to exception in reading values from portal")
#             print("")
#             GlobalVariables.portal_ValidationFailureCount += 1
#             expectedPortalValues = "Failed"
#             GlobalVariables.EXCEL_Portal_Val = "Fail"
#             success_Val_Execution = False
#
#         success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")
#
#         if success_Val_Execution == False:
#             if success == False:
#                 pass
#             else:
#                 pytest.fail()
#
#
#
# @pytest.mark.usefixtures("log_on_failure","log_on_success")
# def test_DB_val_failure(method_ReportProcessor, session_ReportProcessor):
#     GlobalVariables.apiLogs = False
#     GlobalVariables.portalLogs = False
#     GlobalVariables.cnpWareLogs = False
#     GlobalVariables.middleWareLogs = False
#     global success_Val_Execution
#     success_Val_Execution = True
#
#     try:
#         print("EXECUTING SEVENTH TEST CASE : DB VAL FAILURE")
#         time.sleep(2)
#         ReportProcessor.get_TC_Exe_Time() # Get execution time
#     except:
#         ReportProcessor.get_TC_Exe_Time()
#         print("Testcase did not complete due to exception in testcase execution")
#         print("")
#         GlobalVariables.EXCEL_TC_Execution = "Fail"
#         GlobalVariables.Incomplete_ExecutionCount += 1
#
#         pytest.fail()
#
#     else:
#         GlobalVariables.EXCEL_TC_Execution = "Pass"
#         current = datetime.now()
#         GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
#
#
#         try:
#             expectedAPIValues = "qwerty:qwerty,zxcv:zxcv"
#         except:
#             print("API|DB Validation did not complete due to exception")
#             print("")
#             GlobalVariables.api_ValidationFailureCount += 1
#             expectedAPIValues = "Failed"
#             GlobalVariables.EXCEL_API_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedDBValues = "10.0:10.0,787878:12345"
#         except:
#             print("DB Validation did not complete due to exception in reading values from DB")
#             print("")
#             GlobalVariables.db_ValidationFailureCount += 1
#             expectedDBValues = "Failed"
#             GlobalVariables.EXCEL_DB_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedPortalValues = "CASH:CASH,909090:909090"
#         except:
#             print("Portal Validation did not complete due to exception in reading values from portal")
#             print("")
#             GlobalVariables.portal_ValidationFailureCount += 1
#             expectedPortalValues = "Failed"
#             GlobalVariables.EXCEL_Portal_Val = "Fail"
#             success_Val_Execution = False
#
#         success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")
#
#         if success_Val_Execution == False:
#             if success == False:
#                 pass
#             else:
#                 pytest.fail()
#
#
#
#
# @pytest.mark.usefixtures("log_on_failure","log_on_success")
# def test_portal_val_failure(method_ReportProcessor, session_ReportProcessor):
#     GlobalVariables.apiLogs = False
#     GlobalVariables.portalLogs = False
#     GlobalVariables.cnpWareLogs = False
#     GlobalVariables.middleWareLogs = False
#     global success_Val_Execution
#     success_Val_Execution = True
#
#     try:
#         print("EXECUTING EIGHT TEST CASE : PORTAL VAL FAILURE")
#         time.sleep(2)
#         ReportProcessor.get_TC_Exe_Time() # Get execution time
#     except:
#         ReportProcessor.get_TC_Exe_Time()
#         print("Testcase did not complete due to exception in testcase execution")
#         print("")
#         GlobalVariables.EXCEL_TC_Execution = "Fail"
#         GlobalVariables.Incomplete_ExecutionCount += 1
#
#         pytest.fail()
#
#     else:
#         GlobalVariables.EXCEL_TC_Execution = "Pass"
#         current = datetime.now()
#         GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
#
#
#         try:
#             time.sleep(1)
#             expectedAPIValues = "qwerty:qwerty,zxcv:zxcv"
#         except:
#             print("API|DB Validation did not complete due to exception")
#             print("")
#             GlobalVariables.api_ValidationFailureCount += 1
#             expectedAPIValues = "Failed"
#             GlobalVariables.EXCEL_API_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedDBValues = "10.0:10.0,787878:787878"
#         except:
#             print("DB Validation did not complete due to exception in reading values from DB")
#             print("")
#             GlobalVariables.db_ValidationFailureCount += 1
#             expectedDBValues = "Failed"
#             GlobalVariables.EXCEL_DB_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedPortalValues = "CASH:CASH,909090:abcdef"
#         except:
#             print("Portal Validation did not complete due to exception in reading values from portal")
#             print("")
#             GlobalVariables.portal_ValidationFailureCount += 1
#             expectedPortalValues = "Failed"
#             GlobalVariables.EXCEL_Portal_Val = "Fail"
#             success_Val_Execution = False
#
#         success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")
#
#         if success_Val_Execution == False:
#             if success == False:
#                 pass
#             else:
#                 pytest.fail()


#################################################### SANDEEPS's CODE WITHOUT GLOBAL VARIABLES START ##################################################
# @pytest.mark.dbVal
# @pytest.mark.apiVal
# @pytest.mark.portalVal
# def test_success():
#     # GlobalVariables.apiLogs = False
#     # GlobalVariables.portalLogs = False
#     # GlobalVariables.cnpWareLogs = False
#     # GlobalVariables.middleWareLogs = False
#     global success_Val_Execution
#     success_Val_Execution = True
#
#     try:
#         print("EXECUTING FIRST TEST CASE : SUCCESS")
#         time.sleep(1)
#         ReportProcessor.get_TC_Exe_Time() # Get execution time
#     except:
#         ReportProcessor.get_TC_Exe_Time()
#         print("Testcase did not complete due to exception in testcase execution")
#         print("")
#         # GlobalVariables.EXCEL_TC_Execution = "Fail"
#         # GlobalVariables.Incomplete_ExecutionCount += 1
#         pytest.fail()
#
#     else:
#         # GlobalVariables.EXCEL_TC_Execution = "Pass"
#         current = datetime.now()
#         # GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
#
#
#         try:
#             time.sleep(1)
#             expectedAPIValues = "qwerty:qwerty,zxcv:zxcv"
#         except:
#             print("API|DB Validation did not complete due to exception")
#             print("")
#             # GlobalVariables.api_ValidationFailureCount += 1
#             expectedAPIValues = "Failed"
#             # GlobalVariables.EXCEL_API_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedDBValues = "10.0:10.0,787878:787878"
#         except:
#             print("DB Validation did not complete due to exception in reading values from DB")
#             print("")
#             # GlobalVariables.db_ValidationFailureCount += 1
#             expectedDBValues = "Failed"
#             # GlobalVariables.EXCEL_DB_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedPortalValues = "CASH:CASH,909090:909090"
#         except:
#             print("Portal Validation did not complete due to exception in reading values from portal")
#             print("")
#             # GlobalVariables.portal_ValidationFailureCount += 1
#             expectedPortalValues = "Failed"
#             # GlobalVariables.EXCEL_Portal_Val = "Fail"
#             success_Val_Execution = False
#
#         success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")
#
#         if success_Val_Execution == False:
#             if success == False:
#                 pass
#             else:
#                 pytest.fail()
#
# @pytest.mark.dbVal
# @pytest.mark.apiVal
# @pytest.mark.portalVal
# def test_Exe_Failure():
#     # GlobalVariables.apiLogs = False
#     # GlobalVariables.portalLogs = False
#     # GlobalVariables.cnpWareLogs = False
#     # GlobalVariables.middleWareLogs = False
#     global success_Val_Execution
#     success_Val_Execution = True
#
#     try:
#         print("EXECUTING SECOND TEST CASE : EXECUTION FAILURE")
#         time.sleep(1)
#         a = 1/0
#         ReportProcessor.get_TC_Exe_Time() # Get execution time
#     except:
#         ReportProcessor.get_TC_Exe_Time()
#         print("Testcase did not complete due to exception in testcase execution")
#         print("")
#         # GlobalVariables.EXCEL_TC_Execution = "Fail"
#         # GlobalVariables.Incomplete_ExecutionCount += 1
#
#         pytest.fail()
#
#     else:
#         # GlobalVariables.EXCEL_TC_Execution = "Pass"
#         current = datetime.now()
#         # GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
#
#         try:
#             time.sleep(1)
#             expectedAPIValues = "qwerty:qwerty,zxcv:zxcv"
#         except:
#             print("API|DB Validation did not complete due to exception")
#             print("")
#             # GlobalVariables.api_ValidationFailureCount += 1
#             expectedAPIValues = "Failed"
#             # GlobalVariables.EXCEL_API_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedDBValues = "10.0:10.0,787878:787878"
#         except:
#             print("DB Validation did not complete due to exception in reading values from DB")
#             print("")
#             # GlobalVariables.db_ValidationFailureCount += 1
#             expectedDBValues = "Failed"
#             # GlobalVariables.EXCEL_DB_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedPortalValues = "CASH:CASH,909090:909090"
#         except:
#             print("Portal Validation did not complete due to exception in reading values from portal")
#             print("")
#             # GlobalVariables.portal_ValidationFailureCount += 1
#             expectedPortalValues = "Failed"
#             # GlobalVariables.EXCEL_Portal_Val = "Fail"
#             success_Val_Execution = False
#
#         success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")
#
#         if success_Val_Execution == False:
#             if success == False:
#                 pass
#             else:
#                 pytest.fail()
#
#
# @pytest.mark.dbVal
# @pytest.mark.apiVal
# @pytest.mark.portalVal
# def test_api_val_exe_failure():
#     # GlobalVariables.apiLogs = False
#     # GlobalVariables.portalLogs = False
#     # GlobalVariables.cnpWareLogs = False
#     # GlobalVariables.middleWareLogs = False
#     global success_Val_Execution
#     success_Val_Execution = True
#
#     try:
#         print("EXECUTING THIRD TEST CASE : API|DB VAL EXE FAILURE")
#         time.sleep(1)
#         ReportProcessor.get_TC_Exe_Time() # Get execution time
#     except:
#         ReportProcessor.get_TC_Exe_Time()
#         print("Testcase did not complete due to exception in testcase execution")
#         print("")
#         # GlobalVariables.EXCEL_TC_Execution = "Fail"
#         # GlobalVariables.Incomplete_ExecutionCount += 1
#
#         pytest.fail()
#
#     else:
#         # GlobalVariables.EXCEL_TC_Execution = "Pass"
#         current = datetime.now()
#         # GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
#
#         try:
#             time.sleep(1)
#             a = 1/0
#             expectedAPIValues = "qwerty:qwerty,zxcv:zxcv"
#         except:
#             print("API|DB Validation did not complete due to exception")
#             print("")
#             # GlobalVariables.api_ValidationFailureCount += 1
#             expectedAPIValues = "Failed"
#             # GlobalVariables.EXCEL_API_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedDBValues = "10.0:10.0,787878:787878"
#         except:
#             print("DB Validation did not complete due to exception in reading values from DB")
#             print("")
#             # GlobalVariables.db_ValidationFailureCount += 1
#             expectedDBValues = "Failed"
#             # GlobalVariables.EXCEL_DB_Val = "Fail"
#             success_Val_Execution = False
#
#         try:
#             time.sleep(1)
#             expectedPortalValues = "CASH:CASH,909090:909090"
#         except:
#             print("Portal Validation did not complete due to exception in reading values from portal")
#             print("")
#             # GlobalVariables.portal_ValidationFailureCount += 1
#             expectedPortalValues = "Failed"
#             # GlobalVariables.EXCEL_Portal_Val = "Fail"
#             success_Val_Execution = False
#
#         success = ReportProcessor.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, "")
#
#         if success_Val_Execution == False:
#             if success == False:
#                 pass
#             else:
#                 pytest.fail()

####################################### Sandeep Code without Global variables END ###################################################
