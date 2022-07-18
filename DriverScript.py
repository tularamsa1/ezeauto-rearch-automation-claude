from Utilities import DirectoryCreator
DirectoryCreator.createExecutionDirectories()
from Utilities import Rerun
from Utilities import ConfigReader, merchant_creator
from Configuration import TestSuiteSetup
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.time_calculator import generate_excel_report
from Utilities import ReportProcessor

logger = EzeAutoLogger(__name__)

try:
    if TestSuiteSetup.prepareDevicesAndDB():
        merchant_creator.create_merchants_with_users()
        TestSuiteSetup.prepare_Consolidated_List_Of_TestcasesFile()
        if ConfigReader.read_config("Validations", "bool_rerun_immediately").lower() == "true" and ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "false":
            Rerun.prepareImmediateRerunExcel()
        else:
            print("Immediate rerun is disabled for this execution.")
        
        TestSuiteSetup.executeSelectedTestCases()
        # Rerun
        count_up_rerun = 0
        if ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "true":
            rerunCount = int(ConfigReader.read_config("Validations", "int_rerun_count"))
            Rerun.prepareAtTheEndRerunExcel()
            while rerunCount > 0:
                count_up_rerun += 1
                rerunCount = rerunCount - 1
                Rerun.setRerunCount("", rerunCount)
                print(f" [ RERUN ATTEMPT NO: {count_up_rerun} ] ".center(150, "#"))
                Rerun.set_rerun_at_the_end_count_up_to_report_excel_file(count_up_rerun)
                count_reverse = Rerun.rerunTestAtTheEnd()
                if count_reverse == 0:
                    break
            
            Rerun.prepareAtTheEndRerunExcel()
    else:
        print("Issue in preparing the devices and automation db for execution. Hence could not start execution.")
finally:
    generate_excel_report()
    ReportProcessor.setStylesForExcel()
    TestSuiteSetup.killEmulatorsAndAppiumServers()

