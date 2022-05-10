import os
import datetime
import configparser
from Utilities import configReader

automationSuitePath = configReader.read_config("System","automation_suite_path")

def createReportDirectories(currentDate, currentTime):
    try:
        reportDir = {}
        os.chdir(automationSuitePath)
        currentPath = automationSuitePath + "/Reports"
        if os.path.isdir(currentPath) == False:
            os.mkdir(currentPath)
        os.chdir(currentPath)
        currentPath = currentPath+"/ExecutionDate_"+currentDate
        if os.path.isdir(currentPath) == False:
            os.mkdir(currentPath)
        os.chdir(currentPath)
        currentPath = currentPath+"/ExecutionTime_"+currentTime
        os.mkdir(currentPath)
        ls_subDirectories = ["ExcelReport", "AllureReport", "PDFReport"]
        for directory in ls_subDirectories:
            currentPath = currentPath+"/"+directory
            os.mkdir(currentPath)
            reportDir[directory] = currentPath
            currentPath = currentPath.replace("/"+directory, "")
        return reportDir
    except Exception as e:
        print("Unable to create the report directories due to error "+e)
        return None


def createLogDirectories(currentDate, currentTime):
    try:
        logDir = {}
        os.chdir(automationSuitePath)
        currentPath = automationSuitePath + "/Logs"
        if os.path.isdir(currentPath) == False:
            os.mkdir(currentPath)
        os.chdir(currentPath)
        currentPath = currentPath + "/ExecutionDate_" + currentDate
        if os.path.isdir(currentPath) == False:
            os.mkdir(currentPath)
        os.chdir(currentPath)
        currentPath = currentPath + "/ExecutionTime_" + currentTime
        os.mkdir(currentPath)
        ls_subDirectories = ["ExecutionLog", "ServerLog"]
        for directory in ls_subDirectories:
            currentPath = currentPath + "/" + directory
            if os.path.isdir(currentPath)==False:
                os.mkdir(currentPath)
            logDir[directory] = currentPath
            currentPath = currentPath.replace("/" + directory, "")
        return logDir
    except Exception as e:
        print("Unable to create the log directories due to error "+e)
        return None


def createExecutionDirectoriesConfigurationFile(currentDate, currentTime):
    try:
        os.chdir(automationSuitePath)
        currentPath = automationSuitePath + "/" + "Configuration"
        if os.path.isdir(currentPath) == False:
            os.mkdir(currentPath)
        os.chdir(currentPath)
        config = configparser.ConfigParser()
        config['Stamp'] = {"Datestamp" : currentDate, "Timestamp" : currentTime}
        config['Reports'] = {"ExcelReportPath" : "","AllureReportPath" : "","PDFReportPath" : ""}
        config['Logs'] = {"ExecutionLogPath" : "", "ServerLogPath" : ""}
        currentPath = currentPath+"/"+'ExecutionDirectories.conf'
        with open(currentPath,'w') as configFile:
            config.write(configFile)
        return currentPath
    except:
        print("Unable to create Execution directories configuration file")
        return None

def createExecutionDirectories():
    try:
        currentDateTime = datetime.datetime.now()
        currentDate = currentDateTime.strftime("%Y-%m-%d")
        currentTime = currentDateTime.strftime("%H:%M:%S")
        filePath = createExecutionDirectoriesConfigurationFile(currentDate, currentTime)
        directories = createReportDirectories(currentDate, currentTime)
        config = configparser.ConfigParser()
        config.read(filePath)
        config.set('Reports', 'excelreportpath', directories['ExcelReport'])
        config.set('Reports', 'allurereportpath', directories['AllureReport'])
        config.set('Reports', 'pdfreportpath', directories['PDFReport'])
        directories = createLogDirectories(currentDate, currentTime)
        config.set('Logs', 'executionlogpath', directories['ExecutionLog'])
        config.set('Logs', 'serverlogpath', directories['ServerLog'])
        with open(filePath,'w') as configFile:
            config.write(configFile)
        return True
    except:
        print("Execution directories creation failed")
        return False

"""
This method returns the path of the requested directory.
Following values can only be passed as arguments.
1. ExcelReport
2. AllureReport
3. PDFreport
4. ExecutionLog
5. ServerLog
"""
def getDirectoryPath(directoryName):
    filePath = automationSuitePath+"/Configuration/ExecutionDirectories.conf"
    if os.path.isfile(filePath):
        try:
            config = configparser.ConfigParser()
            config.read(filePath)
            if directoryName.lower() == "ExcelReport".lower():
                return config.get("Reports","excelreportpath")
            elif directoryName.lower() == "AllureReport".lower():
                return config.get("Reports","allurereportpath")
            elif directoryName.lower() == "PDFreport".lower():
                return config.get("Reports","pdfreportpath")
            elif directoryName.lower() == "ExecutionLog".lower():
                return config.get("Logs","executionlogpath")
            elif directoryName.lower() == "ServerLog".lower():
                return config.get("Logs","serverlogpath")
        except:
            print("Unable to read the Execution directories file")
            return None
    else:
        print("Execution directories file does not exists. So path cannot be returned.")
        return None


