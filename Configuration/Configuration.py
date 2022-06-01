from DataProvider import GlobalVariables
from Utilities import ReportProcessor, ResourceAssigner
import configparser


def configureLogCaptureVariables(apiLog : bool, portalLog : bool, cnpwareLog : bool, middlewareLog : bool):
    GlobalVariables.apiLogs = apiLog
    GlobalVariables.portalLogs = portalLog
    GlobalVariables.cnpWareLogs = cnpwareLog
    GlobalVariables.middleWareLogs = middlewareLog

def executeFinallyBlock(testcaseID):
    ResourceAssigner.releaseUserInDBUsingTestCaseID(testcaseID)
    ResourceAssigner.releaseDeviceInDBusingTestCaseID(testcaseID)
    ResourceAssigner.releaseAppiumServerInDBUsingTestCaseID(testcaseID)

