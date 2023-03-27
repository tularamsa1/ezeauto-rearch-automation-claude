# import openpyxl
# import pandas
# from Utilities import DirectoryCreator
# DirectoryCreator.createExecutionDirectories()
# from Utilities import ConfigReader
# from Utilities.execution_log_processor import EzeAutoLogger
# import subprocess
#
# logger = EzeAutoLogger(__name__)
# testcases_excel_path = ConfigReader.read_config_paths("System", "automation_suite_path") + "/DataProvider/TestCasesDetail.xlsx"
#
# try:
#     def prepare_list_of_testcases(sheet):
#         print()
#         print("Fetching details from sheet : ",sheet)
#         testcases_excel_data = pandas.read_excel(testcases_excel_path, sheet_name=sheet)
#         return testcases_excel_data
#
#
#     def get_test_case_names_from_script(file_path):
#         command = f"pytest --collect-only {file_path}"
#         result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         output = result.stdout.decode('utf-8')
#         test_case_names = []
#         for line in output.splitlines():
#             if line.__contains__("<Function"):
#                 try:
#                     sub_string1 = "<Function "
#                     sub_string2 = ">"
#
#                     index1 = line.index(sub_string1)
#                     index2 = line.index(sub_string2)
#                     testcase = line[index1 + len(sub_string1): index2]
#                     test_case_names.append(testcase)
#                 except Exception as sss:
#                     print("EXCEPTION")
#                     print(line)
#         return test_case_names
#
#
#     newWorkbook = openpyxl.load_workbook(testcases_excel_path)
#
#     sheets = newWorkbook.sheetnames
#
#     for sheet in sheets:
#         testcases_excel_data = prepare_list_of_testcases(sheet).to_dict()
#         dict_testcaseID = testcases_excel_data.get("Test Case ID")
#         dict_testcaseFile = testcases_excel_data.get("File Name")
#         if len(dict_testcaseID) > 0:
#             for i in range(0, len(dict_testcaseID)):
#                 testcaseID = (dict_testcaseID)[i]
#                 testcaseFile = (dict_testcaseFile)[i]
#                 testcases_in_script = get_test_case_names_from_script("/home/automation/EzeAuto/TestCases/"+testcaseFile+".py")
#                 if testcaseID in testcases_in_script:
#                     pass
#                 else:
#                     print("The testcase " + testcaseID + " is not present in file " + testcaseFile)
#         else:
#             print("No Data in sheet : "+sheet)
#
#
# finally:
#     print("EXECUTING FINALLY BLOCK")


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
                values.append(line)
            return values
        except Exception as sss:
            print("EXCEPTION IN COLLECTING TESTCASES FROM FRAMEWORK")
            print(sss)


    newWorkbook = openpyxl.load_workbook(testcases_excel_path)
    sheets = newWorkbook.sheetnames
    testcases_in_script = get_test_case_names_from_script(ConfigReader.read_config_paths("System", "automation_suite_path") + "/TestCases")

    for sheet in sheets:
        testcases_excel_data = prepare_list_of_testcases(sheet)
        df_testcaseID = testcases_excel_data.get("Test Case ID")
        df_testcaseFile = testcases_excel_data.get("File Name")
        if len(df_testcaseID) > 0:
            for i in range(0, len(df_testcaseID)):
                testcaseID = str((df_testcaseID)[i])
                testcaseFile = str((df_testcaseFile)[i])

                data_in_file = "TestCases/"+testcaseFile+".py::"+testcaseID

                if data_in_file in testcases_in_script:
                    pass
                else:
                    print("The testcase " + testcaseID + " is not present in file " + testcaseFile)
        else:
            print("No Data in sheet : "+sheet)
finally:
    print("EXECUTING FINALLY BLOCK")