import datetime
from datetime import datetime

from DataProvider import GlobalVariables
from PageFactory import Base_Actions
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

env = Base_Actions.get_environment("str_exe_env")


# To Fetch API logs
def fetchAPILogs():
    data_buffer = ''
    startLineNo = GlobalVariables.startLineNumberAPI
    logfileName = Base_Actions.pathToLogFile('api')
    ednLineNo = get_no_of_log_lines(logfileName)
    command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + ednLineNo + " { print }' " + logfileName
    print(command)
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


# To fetch Portal logs
def fetchPortalLogs():
    data_buffer = ''
    startLineNo = GlobalVariables.startLineNumberPortal
    logfileName = Base_Actions.pathToLogFile("portal")
    endLineNo = get_no_of_log_lines(logfileName)
    command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


# To fetch Middleware logs
def fetchMiddlewareLogs():
    data_buffer = ''
    startLineNo = GlobalVariables.startLineNumberMiddlewware
    logfileName = Base_Actions.pathToLogFile("middleware")
    endLineNo = get_no_of_log_lines(logfileName)
    command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


# To fetch CNP ware logs
def fetchCnpwareLogs():
    data_buffer = ''
    startLineNo = GlobalVariables.startLineNumberCnpware
    logfileName = Base_Actions.pathToLogFile("cnpware")
    endLineNo = get_no_of_log_lines(logfileName)
    command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


# To fetch closedloop logs
def fetch_closed_loop_logs():
    data_buffer = ''
    start_line_no = GlobalVariables.start_line_number_closedloop
    logfile_name = Base_Actions.pathToLogFile("closedloop_logfile")
    end_line_no = get_no_of_log_lines(logfile_name)
    command = "awk " + "'NR>=" + start_line_no + " && " + "NR<=" + end_line_no + " { print }' " + logfile_name
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer

def fetch_q2_logs():
    data_buffer = ''
    start_line_no = GlobalVariables.start_line_number_q2
    logfile_name = Base_Actions.pathToLogFile("q2_logfile")
    end_line_no = get_no_of_log_lines(logfile_name)
    command = "awk " + "'NR>=" + start_line_no + " && " + "NR<=" + end_line_no + " { print }' " + logfile_name
    ssh_stdin, ssh_stdout, ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


# To fetch config apps logs
def fetch_config_logs():
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
    if Base_Actions.is_log_capture_required("bool_capt_log_pass") == "True" or Base_Actions.is_log_capture_required(
            "bool_capt_log_fail") == "True":
        global LogCollTime
        current = datetime.now()
        LogColl_Starting_Time = current.strftime("%H:%M:%S")
        if Base_Actions.is_log_capture_required("bool_capt_log_api") == "True":
            GlobalVariables.startLineNumberAPI = get_no_of_log_lines(Base_Actions.pathToLogFile('api'))
        if Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
            GlobalVariables.startLineNumberPortal = get_no_of_log_lines(Base_Actions.pathToLogFile('portal'))
        if Base_Actions.is_log_capture_required("bool_capt_log_middleware") == "True":
            GlobalVariables.startLineNumberMiddlewware = get_no_of_log_lines(
                Base_Actions.pathToLogFile('middleware'))
        if Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
            GlobalVariables.startLineNumberCnpware = get_no_of_log_lines(Base_Actions.pathToLogFile('cnpware'))
        if Base_Actions.is_log_capture_required("bool_capt_log_closedloop") == "True":
            GlobalVariables.start_line_number_closedloop = get_no_of_log_lines(Base_Actions.pathToLogFile('closedloop_logfile'))
        if Base_Actions.is_log_capture_required("bool_capt_log_q2") == "True":
            GlobalVariables.start_line_number_q2 = get_no_of_log_lines(Base_Actions.pathToLogFile('q2_logfile'))
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