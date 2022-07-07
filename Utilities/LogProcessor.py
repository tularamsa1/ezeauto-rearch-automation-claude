from DataProvider import GlobalVariables
from PageFactory import Base_Actions
import datetime
from datetime import datetime
env = Base_Actions.get_environment("str_exe_env")


# To Fetch API logs
def fetchAPILogs():
    data_buffer = ''
    startLineNo = GlobalVariables.startLineNumberAPI
    logfileName = Base_Actions.pathToLogFile('api')
    ednLineNo = noOfLine(logfileName)
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
    endLineNo = noOfLine(logfileName)
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
    endLineNo = noOfLine(logfileName)
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
    endLineNo = noOfLine(logfileName)
    command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
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

    end_line_no = fetch_number_of_lines_as_super_user(log_filepath)
    command = "awk " + "'NR>=" + start_line_no + " && " + "NR<=" + end_line_no + " { print }' " + log_filepath
    _ssh_stdin, ssh_stdout, _ssh_stderr = GlobalVariables.ssh.exec_command(command, get_pty=True)
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    return data_buffer


def fetch_number_of_lines_as_super_user(log_filepath:str) -> str:
    """This function takes a log_filepath and login as super user and fetch the total number of lines in the file in string format
    """
    print('logining as superuser using sudo su - ezetap', end='\r')
    GlobalVariables.ssh.exec_command("sudo /bin/su - ezetap", get_pty=True)
    print('logining as superuser using sudo su - ezetap :: Sucessful')
    cmd = f"wc -l {log_filepath}"  # cmd to count the lines in the file
    _ssh_stdin, ssh_stdout, _ssh_stderr = GlobalVariables.ssh.exec_command(cmd, get_pty=True)
    data_buffer = ""
    for line in iter(lambda: ssh_stdout.readline(), ''):
        data_buffer += line
    print(f"Received STDOUT as the following: \n{data_buffer}\n")
    number_of_lines_in_strfmt = data_buffer.strip().split()[0]
    return number_of_lines_in_strfmt


# To get no of lines from the log file
def noOfLine(logFileName):
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
            GlobalVariables.startLineNumberAPI = noOfLine(Base_Actions.pathToLogFile('api'))
        if Base_Actions.is_log_capture_required("bool_capt_log_portal") == "True":
            GlobalVariables.startLineNumberPortal = noOfLine(Base_Actions.pathToLogFile('portal'))
        if Base_Actions.is_log_capture_required("bool_capt_log_middleware") == "True":
            GlobalVariables.startLineNumberMiddlewware = noOfLine(
                Base_Actions.pathToLogFile('middleware'))
        if Base_Actions.is_log_capture_required("bool_capt_log_cnpware") == "True":
            GlobalVariables.startLineNumberCnpware = noOfLine(Base_Actions.pathToLogFile('cnpware'))
        #========================================================================================
        # if Base_Actions.is_log_capture_required("bool_capt_log_config") is True:
        if Base_Actions.is_log_capture_required("bool_capt_log_config") == "True":
            log_filepath_template = Base_Actions.pathToLogFile('config_apps_log_filepath_format')
            config_log_filepath = log_filepath_template.format(date_in_strfmt = datetime.now().date().strftime('%Y_%m_%d'))

            start_line_number_config = fetch_number_of_lines_as_super_user(config_log_filepath)
            start_line_number_config = str(int(start_line_number_config) + 1)
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