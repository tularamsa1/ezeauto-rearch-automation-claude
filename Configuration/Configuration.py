import pytest

from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, ReportProcessor

from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


def configureLogCaptureVariables(apiLog : bool = False, portalLog : bool = False, cnpwareLog : bool = False, middlewareLog : bool = False, config_log: bool=False, closedloop_log: bool=False, q2_log: bool=False):
    GlobalVariables.apiLogs = apiLog
    GlobalVariables.portalLogs = portalLog
    GlobalVariables.cnpWareLogs = cnpwareLog
    GlobalVariables.middleWareLogs = middlewareLog
    GlobalVariables.config_logs = config_log
    GlobalVariables.closedloop_logs = closedloop_log
    GlobalVariables.q2_logs = q2_log


def executeFinallyBlock(testcase_Id):
    fail_testcase = False
    logger.info(f"Starting execution of finally block for the test case : {testcase_Id}")
    if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
        GlobalVariables.time_calc.execution.pause()
        logger.debug(
            f"Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function : {testcase_Id}")

    if GlobalVariables.time_calc.execution.is_started:
        GlobalVariables.time_calc.execution.resume()
        logger.debug(f"Execution Timer resumed in finally block of testcase function : {testcase_Id}")
    ResourceAssigner.releaseAppUser(testcase_Id)
    ResourceAssigner.releasePortalUser(testcase_Id)
    ResourceAssigner.releaseDeviceInDBusingTestCaseID(testcase_Id)
    ResourceAssigner.releaseAppiumServerInDBUsingTestCaseID(testcase_Id)

    if not GlobalVariables.setupCompletedSuccessfully:
        print("Test case setup itself failed.")
        logger.error("Test case pre condition setup itself failed.")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        fail_testcase = True
    else:
        ReportProcessor.updateTestCaseResult('')

    if GlobalVariables.time_calc.execution.is_started or GlobalVariables.time_calc.execution.is_paused:
        GlobalVariables.time_calc.execution.end()
        logger.debug("Execution Timer end in finally block of testcase function")
    logger.info(f"Completed execution of finally block for the test case : {testcase_Id}")
    logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_Id}")

    if fail_testcase:
        pytest.fail("Failing the test case in finally block since a failure was observed due to unhandled exception.")


def perform_exe_exception(testcase_id):
    if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
        GlobalVariables.time_calc.execution.pause()
        logger.debug(
            f"Execution Timer paused in except block (bcz not paused in try block) of testcase function : {testcase_id}")
    GlobalVariables.time_calc.execution.resume()
    logger.debug(f"Execution Timer resumed in except block of testcase function : {testcase_id}")

    ReportProcessor.capture_ss_when_app_val_exe_failed()  # If In the execution or try block app driver is not initialized then we can remove this line
    ReportProcessor.capture_ss_when_portal_val_exe_failed()  # If In the execution or try block portal driver is not initialized then we can remove this line
    GlobalVariables.EXCEL_TC_Execution = "Fail"

    GlobalVariables.time_calc.execution.pause()
    logger.debug(f"Execution Timer paused in except block of testcase function before pytest fails : {testcase_id}")
    logger.exception(f"Execution is completed for the test case : {testcase_id}")


def perform_app_val_exception(testcase_id, exception_caught):
    ReportProcessor.capture_ss_when_app_val_exe_failed()
    print("App Validation failed due to exception - " + str(exception_caught))
    logger.exception(f"App Validation failed due to exception - {exception_caught}")
    GlobalVariables.bool_val_exe = False
    GlobalVariables.str_app_val_result = "Fail"


def perform_api_val_exception(testcase_id, exception_caught):
    print("API Validation failed due to exception - " + str(exception_caught))
    logger.exception(f"API Validation failed due to exception : {exception_caught} ")
    GlobalVariables.bool_val_exe = False
    GlobalVariables.str_api_val_result = "Fail"


def perform_db_val_exception(testcase_id, exception_caught):
    print("DB Validation failed due to exception - " + str(exception_caught))
    logger.exception(f"DB Validation failed due to exception :  {exception_caught}")
    GlobalVariables.bool_val_exe = False
    GlobalVariables.str_db_val_result = 'Fail'


def perform_portal_val_exception(testcase_id, exception_caught):
    ReportProcessor.capture_ss_when_portal_val_exe_failed()
    print("Portal Validation failed due to exception - " + str(exception_caught))
    logger.exception(f"Portal Validation failed due to exception : {exception_caught}")
    GlobalVariables.bool_val_exe = False
    GlobalVariables.str_portal_val_result = 'Fail'


def perform_charge_slip_val_exception(testcase_id, exception_caught):
    ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
    print("Charge Slip Validation failed due to exception - " + str(exception_caught))
    logger.exception(f"Charge Slip Validation failed due to exception : {exception_caught}")
    GlobalVariables.bool_val_exe = False
    GlobalVariables.str_chargeslip_val_result = "Fail"


def perform_ui_val_exception(testcase_id, exception_caught):
    pass
