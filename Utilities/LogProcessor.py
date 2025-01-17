import datetime
from datetime import datetime
import subprocess
import os
from Utilities import DirectoryCreator
from DataProvider import GlobalVariables
from PageFactory import Base_Actions
from Utilities.ConfigReader import read_config
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

env = Base_Actions.get_environment("str_exe_env")


def fetch_API_logs() -> str:
    """
    To fetch the API logs
    :return: string
    """
    data_buffer = ''
    start_line_num = GlobalVariables.start_line_number_API
    log_file_name = Base_Actions.pathToLogFile('api')
    end_line_num = get_no_of_log_lines(log_file_name)
    command = "awk " + "'NR>=" + start_line_num + " && " + "NR<=" + end_line_num + " { print }' " + log_file_name
    print(command)
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_portal_logs() -> str:
    """
    To fetch the portal logs
    :return: string
    """
    data_buffer = ''
    start_line_num = GlobalVariables.start_line_number_portal
    log_file_name = Base_Actions.pathToLogFile("portal")
    end_line_num = get_no_of_log_lines(log_file_name)
    command = "awk " + "'NR>=" + start_line_num + " && " + "NR<=" + end_line_num + " { print }' " + log_file_name
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_middleware_logs() -> str:
    """
    To fetch the middleware logs
    :return: string
    """
    data_buffer = ''
    start_line_num = GlobalVariables.start_line_number_middleware
    log_file_name = Base_Actions.pathToLogFile("middleware")
    end_line_num = get_no_of_log_lines(log_file_name)
    command = "awk " + "'NR>=" + start_line_num + " && " + "NR<=" + end_line_num + " { print }' " + log_file_name
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_cnpware_logs() -> str:
    """
    To fetch the cnpware logs
    :return: string
    """
    data_buffer = ''
    start_line_num = GlobalVariables.start_line_number_cnpware
    log_file_name = Base_Actions.pathToLogFile("cnpware")
    end_line_num = get_no_of_log_lines(log_file_name)
    command = "awk " + "'NR>=" + start_line_num + " && " + "NR<=" + end_line_num + " { print }' " + log_file_name
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_closed_loop_logs() -> str:
    """
    To fetch the closedloop logs
    :return: string
    """
    data_buffer = ''
    start_line_no = GlobalVariables.start_line_number_closedloop
    logfile_name = Base_Actions.pathToLogFile("closedloop_logfile")
    end_line_no = get_no_of_log_lines(logfile_name)
    command = "awk " + "'NR>=" + start_line_no + " && " + "NR<=" + end_line_no + " { print }' " + logfile_name
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_q2_logs() -> str:
    """
    To fetch the q2 logs
    :return: string
    """
    data_buffer = ''
    start_line_no = GlobalVariables.start_line_number_q2
    logfile_name = Base_Actions.pathToLogFile("q2_logfile")
    end_line_no = get_no_of_log_lines(logfile_name)
    command = "awk " + "'NR>=" + start_line_no + " && " + "NR<=" + end_line_no + " { print }' " + logfile_name
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_config_logs() -> str:
    """
    To fetch the config logs
    :return: string
    """
    data_buffer = ''
    start_line_no = GlobalVariables.start_line_number_config
    log_filepath_template = Base_Actions.pathToLogFile("config_apps_log_filepath_format")
    date_in_strfmt = datetime.now().date().strftime('%Y_%m_%d')  # 2022_07_07_config_apps_server.log
    log_filepath = log_filepath_template.format(date_in_strfmt = date_in_strfmt)
    
    try:
        end_line_no = fetch_number_of_lines_as_super_user(log_filepath)
        command = "awk " + "'NR>=" + start_line_no + " && " + "NR<=" + end_line_no + " { print }' " + log_filepath
        _ssh_stdin, ssh_stdout, _ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line
    except LogFileNotFoundError as e:
        logger.error(f"LogFileNotFoundError: {e}")
        data_buffer = f"No Log file [{log_filepath}] in server is found"
    except Exception as e:
        logger.critical(f"Some Other Error while executing command over ssh connection. The following is the Error: {e}")
        raise Exception(f"Some Other Error while executing command over ssh connection. The following is the Error: {e}")
    return data_buffer


def fetch_commx_logs() -> str:
    """
    To fetch the commx logs
    :return: string
    """
    data_buffer = ''
    start_line_num = GlobalVariables.start_line_number_commx
    log_file_name = Base_Actions.pathToLogFile('commx')
    end_line_num = get_no_of_log_lines(log_file_name)
    command = "awk " + "'NR>=" + start_line_num + " && " + "NR<=" + end_line_num + " { print }' " + log_file_name
    print(command)
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_ezestore_logs() -> str:
    """
    To fetch the ezestore logs
    :return: string
    """
    data_buffer = ''
    start_line_num = GlobalVariables.start_line_number_ezestore
    log_file_name = Base_Actions.pathToLogFile('ezestore')
    ednLineNo = get_no_of_log_lines(log_file_name)
    command = "awk " + "'NR>=" + start_line_num + " && " + "NR<=" + ednLineNo + " { print }' " + log_file_name
    print(command)
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_khata_logs() -> str:
    """
    To fetch the khata logs
    :return: string
    """
    data_buffer = ''
    start_line_num = GlobalVariables.start_line_number_khata
    log_file_name = Base_Actions.pathToLogFile('khata')
    end_line_no = get_no_of_log_lines(log_file_name)
    command = "awk " + "'NR>=" + start_line_num + " && " + "NR<=" + end_line_no + " { print }' " + log_file_name
    print(command)
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_reward_logs() -> str:
    """
    To fetch the reward logs
    :return: string
    """
    data_buffer = ''
    start_line_num = GlobalVariables.start_line_number_reward
    log_file_name = Base_Actions.pathToLogFile('reward')
    end_line_no = get_no_of_log_lines(log_file_name)
    command = "awk " + "'NR>=" + start_line_num + " && " + "NR<=" + end_line_no + " { print }' " + log_file_name
    print(command)
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_adb_exception_logs():
    try:
        execution_date = datetime.now().strftime("%m-%d")
        logcat_result = subprocess.run(
            ["adb", "logcat", "-d", "*:E"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if logcat_result.returncode != 0:
            print(f"Error fetching logs: {logcat_result.stderr}")
            return
        grep_result = subprocess.run(
            ["grep", "-E", f"^{execution_date} {GlobalVariables.start_time}|{execution_date} {GlobalVariables.end_time}"],
            input=logcat_result.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if grep_result.returncode != 0:
            print(f"Error with grep: {grep_result.stderr}")
        else:
            if grep_result.stdout:
                return grep_result.stdout
            else:
                print("No matching logs found.")
                return None
    except Exception as e:
        print(f"Error: {str(e)}")


class LogFileNotFoundError(Exception):
    pass


def fetch_number_of_lines_as_super_user(log_filepath:str) -> str:
    """This function takes a log_filepath and login as super user and fetch the total number of lines in the file in string format
    """
    print('Logining as superuser using sudo su - ezetap', end='\r')
    GlobalVariables.ssh.exec_command("sudo /bin/su - ezetap", get_pty=True)
    print('Logining as superuser using sudo su - ezetap :: Successful')
    cmd = f"wc -l {log_filepath}"  # cmd to count the lines in the file
    _ssh_stdin, ssh_stdout, _ssh_stderr = GlobalVariables.ssh.exec_command(cmd, get_pty=True)
    data_buffer = ""
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    
    if 'No such file or directory' in data_buffer:
        raise LogFileNotFoundError(data_buffer)
    
    print(f"Received STDOUT as the following: \n{data_buffer}\n")
    number_of_lines_in_strfmt = data_buffer.strip().split()[0]
    return number_of_lines_in_strfmt


# To get no of lines from the log file
def  get_no_of_log_lines(logFileName):
    command = 'wc -l ' + logFileName
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    line = ssh_stdout.readline()
    number = line.split(' ')
    return number[0]


# To append the logs in the respective file
def appendLogs(fileName, testName, logs):
    with open(fileName, "a") as file:
        file.write(testName + "\n")
        file.write(logs + "\n")


def startLineNoOfServerLogFile():
    if read_config("APIs", "env").lower() == "prod":
        pass
    else:
        if Base_Actions.is_log_capture_required("bool_capt_log_pass") == "True" or Base_Actions.is_log_capture_required(
                "bool_capt_log_fail") == "True":
            global LogCollTime
            current = datetime.now()
            LogColl_Starting_Time = current.strftime("%H:%M:%S")
            if Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
                GlobalVariables.start_line_number_API = get_no_of_log_lines(Base_Actions.pathToLogFile('api'))
            if Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
                GlobalVariables.start_line_number_portal = get_no_of_log_lines(Base_Actions.pathToLogFile('portal'))
            if Base_Actions.is_log_capture_required("bool_capt_log_middleware") == "True":
                GlobalVariables.start_line_number_middleware = get_no_of_log_lines(
                    Base_Actions.pathToLogFile('middleware'))
            if Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
                GlobalVariables.start_line_number_cnpware = get_no_of_log_lines(Base_Actions.pathToLogFile('cnpware'))
            if Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
                GlobalVariables.start_line_number_closedloop = get_no_of_log_lines(Base_Actions.pathToLogFile('closedloop_logfile'))
            if Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
                GlobalVariables.start_line_number_q2 = get_no_of_log_lines(Base_Actions.pathToLogFile('q2_logfile'))
            if Base_Actions.is_log_capture_required("bool_capt_log_commx") == "True":
                GlobalVariables.start_line_number_commx = get_no_of_log_lines(Base_Actions.pathToLogFile('commx'))
            if Base_Actions.is_log_capture_required("bool_capt_log_ezestore") == "True":
                GlobalVariables.start_line_number_ezestore = get_no_of_log_lines(Base_Actions.pathToLogFile('ezestore'))
            if Base_Actions.is_log_capture_required("bool_capt_log_khata") == "True":
                GlobalVariables.start_line_number_khata = get_no_of_log_lines(Base_Actions.pathToLogFile('khata'))
            if Base_Actions.is_log_capture_required("bool_capt_log_reward") == "True":
                GlobalVariables.start_line_number_reward = get_no_of_log_lines(Base_Actions.pathToLogFile('reward'))
            #========================================================================================
            # if Base_Actions.is_log_capture_required("bool_capt_log_config") is True:
            if Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
                log_filepath_template = Base_Actions.pathToLogFile('config_apps_log_filepath_format')
                config_log_filepath = log_filepath_template.format(date_in_strfmt = datetime.now().date().strftime('%Y_%m_%d'))

                try:
                    start_line_number_config = fetch_number_of_lines_as_super_user(config_log_filepath)
                    logger.debug(f'The count of lines in config_log file is found: {start_line_number_config}. Therefore {int(start_line_number_config)+1} will be start line number')
                    start_line_number_config = str(int(start_line_number_config) + 1)
                except Exception as e:
                    logger.warning(f'The count of lines in config_log file is not found due to error: {e}')
                    logger.warning('Therefore setting start line number for config log file as 1 (if in case during the execution of current session if new log file is created. setting 1 will handle the scenario)')
                    start_line_number_config = str(1)

                GlobalVariables.start_line_number_config = start_line_number_config

            current = datetime.now()
            LogColl_Ending_Time = current.strftime("%H:%M:%S")
            FMT = '%H:%M:%S'
            try:
                totalLogCollectionTime = datetime.strptime(LogColl_Ending_Time, FMT) - datetime.strptime(
                    str(LogColl_Starting_Time),
                    FMT)
            except Exception as e:
                print("Unable to set the totalLogCollectionTime due to error : "+str(e)+". Hence setting it to 0.")
                totalLogCollectionTime = 0
            print("Portal logs coll time: ", str(totalLogCollectionTime))
            # Converting time duration to seconds
            LogCollTime = sum(x * int(t) for x, t in zip([3600, 60, 1], str(totalLogCollectionTime).split(":")))
            return LogCollTime