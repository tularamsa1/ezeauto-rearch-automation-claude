from Utilities import DirectoryCreator
DirectoryCreator.createExecutionDirectories()
print(DirectoryCreator.getDirectoryPath("AllureReport"))
import Rerun
from Configuration import Configuration
from Utilities import configReader

# if both r enabled then add this condition: if configReader.read_config("Validations", "rerun_immediately").lower()
# == "true" and configReader.read_config("Validations", "rerun_at_the_end").lower() == "false":

#print(DirectoryCreator.getDirectoryPath("ExcelReport"))

# print(DirectoryCreator.getDirectoryPath("PDFreport"))
# print(DirectoryCreator.getDirectoryPath("ExecutionLog"))
# print(DirectoryCreator.getDirectoryPath("ServerLog"))


Configuration.prepare_Consolidated_List_Of_TestcasesFile()

if configReader.read_config("Validations", "rerun_immediately").lower() == "true" and configReader.read_config("Validations", "rerun_at_the_end").lower() == "false":
    Rerun.prepareImmediateRerunExcel()

Rerun.suiteTriggringTime()

Configuration.executeSelectedTestCases()

# Rerun
rerunCount = int(configReader.read_config("Validations", "rerun_count"))

if configReader.read_config("Validations", "rerun_at_the_end").lower() == "true":
    Rerun.prepareAtTheEndRerunExcel()
    while rerunCount > 0:
        rerunCount = rerunCount - 1
        Rerun.setRerunCountForAtTheEnd(rerunCount)
        Rerun.rerunTestAtTheEnd()
    Rerun.prepareAtTheEndRerunExcel()