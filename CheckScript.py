import openpyxl
import pandas
from Utilities import DirectoryCreator
DirectoryCreator.createExecutionDirectories()
from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger
import subprocess

logger = EzeAutoLogger(__name__)
testcases_excel_path = ConfigReader.read_config_paths("System", "automation_suite_path") + "/DataProvider/TestCasesDetail.xlsx"

try:
    def prepare_list_of_testcases(sheet):
        print()
        print("Fetching details from sheet : ",sheet)
        testcases_excel_data = pandas.read_excel(testcases_excel_path, sheet_name=sheet)
        return testcases_excel_data


    def get_test_case_names_from_script(file_path):
        command = f"pytest --collect-only -q {file_path}"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        values = []
        try:
            for line in output.splitlines():
                values.append(line) # Adding all the testcases from framework to a list
            return values
        except Exception as sss:
            print("EXCEPTION IN COLLECTING TESTCASES FROM FRAMEWORK")
            print(sss)


    newWorkbook = openpyxl.load_workbook(testcases_excel_path)
    sheets = newWorkbook.sheetnames
    testcases_in_script = get_test_case_names_from_script(ConfigReader.read_config_paths("System", "automation_suite_path") + "/TestCases")

    for sheet in sheets:
        testcases_excel_data = prepare_list_of_testcases(sheet)
        df_testcaseID = testcases_excel_data.get("Test Case ID") # Create DF with testcases from specific single sheet in TestCasesDetails file
        df_testcaseFile = testcases_excel_data.get("File Name") # Create DF with filename from specific single sheet in TestCasesDetails file
        if len(df_testcaseID) > 0:
            for i in range(0, len(df_testcaseID)):
                testcaseID = str((df_testcaseID)[i])
                testcaseFile = str((df_testcaseFile)[i])

                data_in_file = "TestCases/"+testcaseFile+".py::"+testcaseID # Append testcase and filename as similar format as in testcases_in_script

                if data_in_file in testcases_in_script: # If testcase is available in framework
                    pass
                else:
                    print("The testcase " + testcaseID + " is not present in file " + testcaseFile)
        else: # If not testcases are present in sheet
            print("No Data in sheet : "+sheet)
finally:
    print("EXECUTING FINALLY BLOCK")