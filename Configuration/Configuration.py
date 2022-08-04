from DataProvider import GlobalVariables
from Utilities import ReportProcessor, ResourceAssigner
import configparser


def configureLogCaptureVariables(apiLog : bool = False, portalLog : bool = False, cnpwareLog : bool = False, middlewareLog : bool = False, config_log: bool=False, closedloop_log: bool=False):
    GlobalVariables.apiLogs = apiLog
    GlobalVariables.portalLogs = portalLog
    GlobalVariables.cnpWareLogs = cnpwareLog
    GlobalVariables.middleWareLogs = middlewareLog
    GlobalVariables.config_logs = config_log
    GlobalVariables.closedloop_logs = closedloop_log

def executeFinallyBlock(testcaseID):
    ResourceAssigner.releaseAppUser(testcaseID)
    ResourceAssigner.releasePortalUser(testcaseID)
    ResourceAssigner.releaseDeviceInDBusingTestCaseID(testcaseID)
    ResourceAssigner.releaseAppiumServerInDBUsingTestCaseID(testcaseID)

