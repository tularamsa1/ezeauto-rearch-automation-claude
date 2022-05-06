import os

import pandas as pd
import paramiko
import pandas as pd
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


def prepareTestCaseDetailsDataFrame(path):
    dataForDataFrameHeader = {
        'Test Case ID': [],
        'File Name': [],
        'Directory Name': [],
        'Category': [],
        'Sub-Category': [],
        'OverAll Results': [],
        'TC Execution': [],
        'API Val': [],
        'DB Val': [],
        'Portal Val': [],
        'App Val': [],
        'UI Val': [],
        'Execution Time (sec)': [],
        'Validation Time (sec)': [],
        'Log Coll Time (sec)': [],
        'Total Time (sec)': [],
        'Rerun Attempts': []
    }

    GlobalVariables.df_testCasesDetail = pd.DataFrame(dataForDataFrameHeader)

    # Dataframe by default gets created with datatype as float. Converting the same to string
    convert_dict = {'File Name': str,
                    'Directory Name': str,
                    'Category': str,
                    'Sub-Category': str,
                    'TC Execution': str,
                    'API Val': str,
                    'DB Val': str,
                    'Portal Val': str,
                    'App Val': str,
                    'UI Val': str,
                    'Rerun Attempts': str
                    }

    GlobalVariables.df_testCasesDetail = GlobalVariables.df_testCasesDetail.astype(convert_dict)

    df_overallTClist = pd.read_excel(path)
    df_overallTClist.set_index(configReader.read_config("TestcaseDetails_ColumnNames", "colName_TestCaseID"), inplace=True)

    i=0
    for index in df_overallTClist.index:
        if df_overallTClist['Execute'][index] == False or str(df_overallTClist['Execute'][index]).lower() == "false":
            pass
        else:
            GlobalVariables.df_testCasesDetail.at[i, configReader.read_config("TestcaseDetails_ColumnNames", "colName_TestCaseID")] = index
            GlobalVariables.df_testCasesDetail.at[i, 'File Name'] = df_overallTClist['File Name'][index]
            GlobalVariables.df_testCasesDetail.at[i, 'Directory Name'] = df_overallTClist['Directory Name'][index]
        i = i+1
    GlobalVariables.df_testCasesDetail.set_index(configReader.read_config("TestcaseDetails_ColumnNames", "colName_TestCaseID"), inplace=True)
    return GlobalVariables.df_testCasesDetail

