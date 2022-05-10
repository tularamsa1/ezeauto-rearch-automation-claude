from Utilities import DirectoryCreator
DirectoryCreator.createExecutionDirectories()
from Utilities import Rerun
from Configuration import Configuration, TestSuiteSetup
from Utilities import ConfigReader
from Configuration import Configuration, TestSuiteSetup
from Utilities import configReader

# if both r enabled then add this condition: if configReader.read_config("Validations", "rerun_immediately").lower()
# == "true" and configReader.read_config("Validations", "rerun_at_the_end").lower() == "false":
TestSuiteSetup.prepare_Consolidated_List_Of_TestcasesFile()

if configReader.read_config("Validations", "bool_rerun_immediately").lower() == "true" and configReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "false":
    Rerun.prepareImmediateRerunExcel()

# Rerun.suiteTriggringTime()

TestSuiteSetup.executeSelectedTestCases()

# Rerun
rerunCount = int(ConfigReader.read_config("Validations", "int_rerun_count"))

if ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "true":
    Rerun.prepareAtTheEndRerunExcel()
    while rerunCount > 0:
        rerunCount = rerunCount - 1
        Rerun.setRerunCount("",rerunCount)
        Rerun.rerunTestAtTheEnd()
    Rerun.prepareAtTheEndRerunExcel()