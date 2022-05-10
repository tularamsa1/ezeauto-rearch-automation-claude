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

        current = datetime.now()
        LogColl_Ending_Time = current.strftime("%H:%M:%S")
        FMT = '%H:%M:%S'
        totalLogCollectionTime = datetime.strptime(LogColl_Ending_Time, FMT) - datetime.strptime(
            str(LogColl_Starting_Time),
            FMT)
        print("Portal logs coll time: ", str(totalLogCollectionTime))
        # Converting time duration to seconds
        LogCollTime = sum(x * int(t) for x, t in zip([3600, 60, 1], str(totalLogCollectionTime).split(":")))
        return LogCollTime