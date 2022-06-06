import os

def create_log_directories(currentDate, currentTime, automationSuitePath):
    
    try:
        logDir = {}
        os.chdir(automationSuitePath)
        currentPath = automationSuitePath + "/Logs"
        if not os.path.isdir(currentPath):
            os.mkdir(currentPath)
        os.chdir(currentPath)
        currentPath = currentPath + "/ExecutionDate_" + currentDate
        if not os.path.isdir(currentPath):
            os.mkdir(currentPath)
        os.chdir(currentPath)
        currentPath = currentPath + "/ExecutionTime_" + currentTime
        os.mkdir(currentPath)
        ls_subDirectories = ["ExecutionLog", "ServerLog"]
        for directory in ls_subDirectories:
            currentPath = currentPath + "/" + directory
            if not os.path.isdir(currentPath):
                os.mkdir(currentPath)
            logDir[directory] = currentPath
            currentPath = currentPath.replace("/" + directory, "")
        return logDir
    
    except Exception as e:
        print(f"Unable to create the log directories due to error: {e}")

        return