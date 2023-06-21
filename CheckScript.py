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
        """
        This method is to fetch all the testcases from each sheet of TestCaseDetail.xlsx file
        :param sheet str
        :return testcases_excel_data dict
        """
        print()
        # print("Fetching details from sheet "+sheet+" ...")
        testcases_excel_data = pandas.read_excel(testcases_excel_path, sheet_name=sheet)
        return testcases_excel_data


    def get_test_case_names_from_script(file_path):
        """
        This method is to fetch all the testcases from EzeAuto suite
        :param file_path str
        :return values list
        """
        tot_UI_SA = 0
        tot_UI_Common = 0
        tot_API_SA = 0
        tot_API_Common = 0
        tot_Dev_ICICI_Direct = 0
        tot_Dev_IDFC_IS = 0
        print("Collecting all the testcases from EzeAuto suite ...")
        command = f"pytest --collect-only -q {file_path}"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        values = []
        try:
            for line in output.splitlines():
                if 'Dev_projects/ICICI_DIRECT_UPI' in line:
                    tot_Dev_ICICI_Direct = tot_Dev_ICICI_Direct+1
                if 'Dev_projects/IDFC_Instant_Settlement' in line:
                    tot_Dev_IDFC_IS = tot_Dev_IDFC_IS+1
                if 'Functional/API_DB/Common' in line:
                    tot_API_Common = tot_API_Common+1
                if 'Functional/API_DB/SA' in line:
                    tot_API_SA = tot_API_SA+1
                if 'Functional/UI/Common' in line:
                    tot_UI_Common= tot_UI_Common+1
                if 'Functional/UI/SA' in line:
                    tot_UI_SA= tot_UI_SA+1

                if line.startswith("TestCases/"):
                    values.append(line) # Adding all the testcases from framework to a list
                else:
                    pass
            print()
            total_tc = tot_UI_SA + tot_UI_Common + tot_API_SA + tot_API_Common + tot_Dev_ICICI_Direct + tot_Dev_IDFC_IS
            print("Total number of testcases in 'TestCases' folder in EzeAuto : ", total_tc)
            print()
            print("Number of testcases in Functional/UI/SA in EzeAuto: ",tot_UI_SA)
            print("Number of testcases in Functional/UI/Common in EzeAuto: ", tot_UI_Common)
            print("Number of testcases in Functional/API_DB/SA in EzeAuto: ", tot_API_SA)
            print("Number of testcases in Functional/API_DB/Common in EzeAuto: ", tot_API_Common)
            print("Number of testcases in Dev_projects/ICICI_DIRECT_UPI in EzeAuto: ", tot_Dev_ICICI_Direct)
            print("Number of testcases in Dev_projects/IDFC_Instant_Settlement in EzeAuto: ", tot_Dev_IDFC_IS)
            return values
        except Exception as ex:
            print("EXCEPTION IN COLLECTING TESTCASES FROM FRAMEWORK")
            print(ex)

    newWorkbook = openpyxl.load_workbook(testcases_excel_path)
    sheets = newWorkbook.sheetnames
    testcases_in_script = get_test_case_names_from_script(ConfigReader.read_config_paths("System", "automation_suite_path") + "/TestCases")
    # get_number_of_testcases_from_sheets(newWorkbook)

    print()
    print()
    print("Below are the information of testcases from TestCasesDetail.xlsx file")
    print("----------------------------------------------------------------------")
    for sheet in sheets:
        flag_complete = True
        # print()
        testcases_excel_data = prepare_list_of_testcases(sheet)
        df_testcaseID = testcases_excel_data.get("Test Case ID") # Create DF with testcases from specific single sheet in TestCasesDetails file
        df_testcaseFile = testcases_excel_data.get("File Name") # Create DF with filename from specific single sheet in TestCasesDetails file
        if len(df_testcaseID) > 0:
            print("Number of testcases in sheet "+sheet+": ",len(df_testcaseID))
            for i in range(0, len(df_testcaseID)):
                testcaseID = str((df_testcaseID)[i])
                testcaseFile = str((df_testcaseFile)[i])

                data_in_file = "TestCases/"+testcaseFile+".py::"+testcaseID # Append testcase and filename as similar format as in testcases_in_script

                if data_in_file in testcases_in_script: # If testcase in file is available in EzeAuto
                    testcases_in_script.remove(data_in_file)
                else: # If testcase in file is not available in EzeAuto
                    flag_complete = False
                    print("ERROR: "+ testcaseID + " is not present in EzeAuto/TestCases/" + testcaseFile+".py")

        else: # If no testcases are present in sheet
            flag_complete = False
            print("No data are given in sheet "+sheet)
        if flag_complete:
            print("All the testcases are available in 'TestCases' folder in EzeAuto")
    if len(testcases_in_script)>0: # To get all the testcases that are not added in TestCaseDetail.xlsx file
        print()
        print("Testcases that are not added in TestCasesDetail.xlsx : ")
        total_invalid_tc = 0
        for j in range(0, len(testcases_in_script)):
            print("    "+testcases_in_script[j])
            total_invalid_tc = total_invalid_tc+1
    print("Count of testcases not added in TestCaseDetail.xlsx is : ", total_invalid_tc)
finally:
    print()
    print("EXECUTING FINALLY BLOCK")