import re
import sys
import pytest
from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_installation import get_device_id, check_sa_installed_or_not, get_sa_app_path, \
    get_mpos_app_path, install_sa_application, check_mpos_installed_or_not, uninstall_mpos_application, \
    install_mpos_application
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor
from Utilities.android_utilities import get_mpos_version
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_mpos_400_404_001():
    """
    Sub Feature Code: UI_mpos_Generic_AppInstallation_Verification_01
    Sub Feature Description: Verify the successful installation of the MPOS app
    TC naming code description:400: Generic Actions,404: App Installation,001: TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")
        testsuite_teardown.revert_org_settings_default(org_code, portal_un=portal_username,
                                                       portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        device_id = get_device_id()
        id_of_devices = device_id
        logger.debug(f"getting device id:- {id_of_devices}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'true':
                mpos_version = ConfigReader.read_config("Applications", "pax_mpos")
            else:
                mpos_version = ConfigReader.read_config("Applications", "mpos")
            sa_path = get_sa_app_path()
            mpos_path = get_mpos_app_path()
            result = check_sa_installed_or_not()
            if result ==  "True":
                logger.debug("Sa is already installed")
            else:
                install_sa_application(id_of_devices, sa_path)
                logger.debug("Sa installed successfully")
            logger.debug("Pre-check is completed for Sa is installed or not")
            logger.debug("Pre-check is Started for Mpos is installed or not")
            mpos_result = check_mpos_installed_or_not()
            if mpos_result == "True":
                uninstall_mpos_application()
            else:
                 logger.debug(f"mpos is not installed")
            install_mpos_application(id_of_devices,mpos_path)
            logger.debug("Mpos installed successfully")
            version_match = re.search(r'(\d+\.\d+\.\d+)', mpos_version)
            if version_match:
                version_number = version_match.group(1)
                logger.debug(f"Version number: {version_number}")
            else:
                logger.info("Version number not found in the filename.")
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_app_values = {
                    'mpos': str(version_number),
                }
                actual_mpos_version = get_mpos_version(id_of_devices)
                actual_app_values = {
                    'mpos': str(actual_mpos_version),
                }
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
