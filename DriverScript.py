from Utilities import DirectoryCreator

DirectoryCreator.createExecutionDirectories()
from Utilities import Rerun
from Utilities import ConfigReader
from Configuration import TestSuiteSetup
from Utilities.execution_log_processor import EzeAutoLogger


logger = EzeAutoLogger(__name__)


try:
    if TestSuiteSetup.prepareDevicesAndDB():
        TestSuiteSetup.prepare_Consolidated_List_Of_TestcasesFile()
        if ConfigReader.read_config("Validations", "bool_rerun_immediately").lower() == "true" and ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "false":
            Rerun.prepareImmediateRerunExcel()
        else:
            print("Immediate rerun is disabled for this execution.")
        TestSuiteSetup.executeSelectedTestCases()
        # Rerun
        if ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "true":
            rerunCount = int(ConfigReader.read_config("Validations", "int_rerun_count"))
            Rerun.prepareAtTheEndRerunExcel()
            while rerunCount > 0:
                rerunCount = rerunCount - 1
                Rerun.setRerunCount("", rerunCount)
                Rerun.rerunTestAtTheEnd()
            Rerun.prepareAtTheEndRerunExcel()
    else:
        print("Issue in preparing the devices and automation db for execution. Hence could not start execution.")
finally:
    TestSuiteSetup.killEmulatorsAndAppiumServers()
