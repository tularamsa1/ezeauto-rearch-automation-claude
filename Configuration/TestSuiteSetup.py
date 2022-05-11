import os

import pandas as pd
import paramiko
from DataProvider import GlobalVariables
from PageFactory import Base_Actions
from Utilities import ConfigReader

GlobalVariables.ssh = paramiko.SSHClient()
router_ip = Base_Actions.get_environment("str_exe_env_ip")  # dev11
router_username = Base_Actions.get_environment("str_ssh_username")
router_port = Base_Actions.get_environment("int_exe_env_port")
key_filename = Base_Actions.get_environment("str_ssh_key_filename")


# Login to the server
def ssh_connection(ip_address, routerPort, username, key_filename):
    GlobalVariables.ssh.load_system_host_keys()
    GlobalVariables.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        GlobalVariables.ssh.connect(ip_address, port=routerPort, username=username,
                    pkey=paramiko.RSAKey.from_private_key_file(key_filename))
        return True
    except Exception as error_message:
        print("Unable to connect")
        print(error_message)
        return False


def prepare_Consolidated_List_Of_TestcasesFile():
    df_all_rows = pd.DataFrame()

    if os.path.exists(ConfigReader.read_config("ExcelFiles", "FilePath_TestCasesDetail")):
        workbook = pd.read_excel(ConfigReader.read_config("ExcelFiles", "FilePath_TestCasesDetail"), None)
        ls_sheets_functional = workbook.keys()

        # Creating a DF with all testcases
        for sheet in ls_sheets_functional:
            df_testCasesDetail = pd.DataFrame(workbook.get(sheet))
            df_all_rows = pd.concat([df_all_rows, df_testCasesDetail])

    if os.path.exists(ConfigReader.read_config("ExcelFiles", "FilePath_testcases_surfaceUI")):
        workbook = pd.read_excel(ConfigReader.read_config("ExcelFiles", "FilePath_testcases_surfaceUI"), None)
        ls_sheets_surfaceUI = workbook.keys()

        # Creating a DF with all testcases
        for sheet in ls_sheets_surfaceUI:
            df_testCasesDetail = pd.DataFrame(workbook.get(sheet))
            df_all_rows = pd.concat([df_all_rows, df_testCasesDetail])

    print("prepare_Consolidated_List_Of_TestcasesFile")
    print(df_all_rows)
    # Converting DF with all TCs to an excel
    df_all_rows.to_excel("/home/oem/PycharmProjects/EzeAuto/TestCases/AllTestcaseSuite.xlsx")