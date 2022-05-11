from Utilities import DirectoryCreator
DirectoryCreator.createExecutionDirectories()
from Utilities import Rerun
from Configuration import Configuration, TestSuiteSetup
from Utilities import ConfigReader

Configuration.prepare_Consolidated_List_Of_TestcasesFile()

if ConfigReader.read_config("Validations", "bool_rerun_immediately").lower() == "true" and ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "false":
    Rerun.prepareImmediateRerunExcel()

Configuration.executeSelectedTestCases()

# Rerun
rerunCount = int(ConfigReader.read_config("Validations", "int_rerun_count"))

if ConfigReader.read_config("Validations", "bool_rerun_at_the_end").lower() == "true":
    Rerun.prepareAtTheEndRerunExcel()
    while rerunCount > 0:
        rerunCount = rerunCount - 1
        Rerun.setRerunCount("",rerunCount)
        Rerun.rerunTestAtTheEnd()
    Rerun.prepareAtTheEndRerunExcel()