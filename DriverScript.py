import shutil
from termcolor import colored
from Utilities import DirectoryCreator
DirectoryCreator.createExecutionDirectories()
from Utilities import Rerun
from Utilities import ConfigReader
from Configuration import TestSuiteSetup
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.time_calculator import generate_excel_report as update_report_excel_with_timing_info
from Utilities import ReportProcessor

logger = EzeAutoLogger(__name__)

try:
    if TestSuiteSetup.prepareDevicesAndDB():
        TestSuiteSetup.prepare_Consolidated_List_Of_TestcasesFile()
        if ConfigReader.read_config("Validations",
                                    "bool_rerun_immediately").lower() == "true" and ConfigReader.read_config(
                "Validations", "bool_rerun_at_the_end").lower() == "false":
            Rerun.prepareImmediateRerunExcel()
        else:
            print("Immediate rerun is disabled for this execution.")

        TestSuiteSetup.executeSelectedTestCases()

        # RERUN SECTION ==================================================== #
        if Rerun.is_rerun_at_the_end_required():
            rerun_count = int(ConfigReader.read_config("Validations", "int_rerun_count"))
            Rerun.prepareAtTheEndRerunExcel()
            number_of_reruns_so_far = 0
            while rerun_count > 0:
                number_of_reruns_so_far += 1
                rerun_count = rerun_count - 1
                Rerun.setRerunCount("", rerun_count)
                print(colored(f" [ RERUN ATTEMPT NO: {number_of_reruns_so_far} ] " \
                              .rjust(shutil.get_terminal_size().columns, "="), 'yellow'))
                Rerun.rerunTestAtTheEnd()
                if not Rerun.is_previous_attempt_a_failure():
                    break
        # ==================================================== RERUN SECTION #


    else:
        print("Issue in preparing the devices and automation db for execution. Hence could not start execution.")
finally:
    update_report_excel_with_timing_info()
    ReportProcessor.setStylesForExcel()
    TestSuiteSetup.killEmulatorsAndAppiumServers()
