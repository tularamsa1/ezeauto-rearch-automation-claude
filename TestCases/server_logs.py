import paramiko

from DataProvider import GlobalVariables
from PageFactory import Base_Actions

ssh = paramiko.SSHClient()
env = Base_Actions.environment("env")

# router_ip = '192.168.3.73'    #dev3
router_ip = '192.168.3.81'    #dev11
router_username = 'vineethb'
router_port = 22
key_filename = '/home/oem/.ssh/vineeth_ssh'
# ssh = paramiko.SSHClient()


# Login to the server
def ssh_connection(ip_address, routerPort, username, key_filename):
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip_address, port=routerPort, username=username,
                    pkey=paramiko.RSAKey.from_private_key_file(key_filename))
        return True
    except Exception as error_message:
        print("Unable to connect")
        print(error_message)
        return False


# To Fetch API logs
def fetchAPILogs():
    data_buffer = ''
    startLineNo = GlobalVariables.startLineNumberAPI
    if env.__contains__('dev'):
        typeOfLog = 'api_' + env[:3]
        logfileName = Base_Actions.pathToLogFile(typeOfLog)
        ednLineNo = noOfLine(logfileName)
        command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + ednLineNo + " { print }' " + logfileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line
        return data_buffer
    else:
        typeOfLog = 'api'
        logfileName = Base_Actions.pathToLogFile(typeOfLog)
        ednLineNo = noOfLine(logfileName)
        command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + ednLineNo + " { print }' " + logfileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line
        return data_buffer


# To fetch Portal logs
def fetchPortalLogs():
    data_buffer = ''
    startLineNo = GlobalVariables.startLineNumberPortal
    if env.__contains__('dev'):
        typeOfLog = 'portal_' + env[:3]
        logfileName = Base_Actions.pathToLogFile(typeOfLog)
        endLineNo = noOfLine(logfileName)
        command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line
        return data_buffer
    else:
        typeOfLog = 'portal'
        logfileName = Base_Actions.pathToLogFile(typeOfLog)
        endLineNo = noOfLine(logfileName)
        command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line
        return data_buffer


# To fetch Middleware logs
def fetchMiddlewareLogs():
    data_buffer = ''
    startLineNo = GlobalVariables.startLineNumberMiddlewware
    if env.__contains__('dev'):
        typeOfLog = 'middleware_' + env[:3]
        logfileName = Base_Actions.pathToLogFile(typeOfLog)
        endLineNo = noOfLine(logfileName)
        command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line
        return data_buffer
    else:
        typeOfLog = 'middleware'
        logfileName = Base_Actions.pathToLogFile(typeOfLog)
        endLineNo = noOfLine(logfileName)
        command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line
        return data_buffer


# To fetch CNP ware logs
def fetchCnpwareLogs():
    data_buffer = ''
    startLineNo = GlobalVariables.startLineNumberCnpware
    if env.__contains__('dev'):
        typeOfLog = 'cnpware_' + env[:3]
        logfileName = Base_Actions.pathToLogFile(typeOfLog)
        endLineNo = noOfLine(logfileName)
        command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line
        return data_buffer
    else:
        typeOfLog = 'cnpware'
        logfileName = Base_Actions.pathToLogFile(typeOfLog)
        endLineNo = noOfLine(logfileName)
        command = "awk " + "'NR>=" + startLineNo + " && " + "NR<=" + endLineNo + " { print }' " + logfileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line
        return data_buffer


# To get no of lines from the log file
def noOfLine(logFileName):
    command = 'wc -l ' + logFileName
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
    line = ssh_stdout.readline()
    number = line.split(' ')
    return number[0]


# To append the logs in the respective file
def appendLogs(fileName, testName, logs):
    with open(fileName, "a") as file:
        file.write(testName + "\n")
        file.write(logs + "\n")


# ssh_connection(router_ip, router_port, router_username, key_filename)
# print(noOfLine('/var/log/ezetap/api/api.log'))
