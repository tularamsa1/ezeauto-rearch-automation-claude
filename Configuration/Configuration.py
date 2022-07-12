from DataProvider import GlobalVariables
from Utilities import ReportProcessor, ResourceAssigner
import configparser


def configureLogCaptureVariables(apiLog : bool, portalLog : bool, cnpwareLog : bool, middlewareLog : bool, config_log: bool):
    GlobalVariables.apiLogs = apiLog
    GlobalVariables.portalLogs = portalLog
    GlobalVariables.cnpWareLogs = cnpwareLog
    GlobalVariables.middleWareLogs = middlewareLog
    GlobalVariables.config_logs = config_log

def executeFinallyBlock(testcaseID):
    ResourceAssigner.releaseAppUser(testcaseID)
    ResourceAssigner.releasePortalUser(testcaseID)
    ResourceAssigner.releaseDeviceInDBusingTestCaseID(testcaseID)
    ResourceAssigner.releaseAppiumServerInDBUsingTestCaseID(testcaseID)

