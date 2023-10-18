import re
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_account_page import AccountPage
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_installation import get_device_id, uninstall_mpos_application, get_mpos_app_path, \
    install_mpos_application
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.mpos.app_ota_upgrade import OTA_upgrade, pinning_mpos_version_to_merchant, install_lower_mpos_version, \
    get_all_file_names, unpining_mpos_update_version
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor
from Utilities.android_utilities import get_mpos_version
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_mpos_400_405_001():
    """
    Sub Feature Code:UI_Common_Generic_AppUpdate_Optional_01
    Sub Feature Description: Performing an optional update of the Mpos app successfully
    TC naming co/de description:400: Generic Actions, 405: AppUpdates, 001: TC001
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
        id_of_device = device_id
        given_version_to_pin = ConfigReader.read_config("OtaUpdate", "mpos_version")
        ver_code = ConfigReader.read_config("OtaUpdate", "mpos_version_code")
        directory_path = ConfigReader.read_config_paths("System", "automation_suite_path") + "/App"
        app_list = get_all_file_names(directory_path)
        try:
            if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'true':
                app_file_name = "pax_mpos"
                query = "select * from app_version where org_code='" + str(
                    org_code) + "' and severity = 1 and device_type = 'PAX' AND application_id = 'ezetap_android' and version_name = '" + str(
                    given_version_to_pin) + "';"
                result = DBProcessor.getValueFromDB(query)
                if result.empty:
                    pin_to_merchant = "True"
                    logger.info(f"empty data frame is validated successfully")
                else:
                    severity = int(result['severity'].values[0])
                    version_name = result['version_name'].values[0]
                    application_id = result['application_id'].values[0]
                    status = result['status'].values[0]
                    device_type_db = result['device_type'].values[0]
                    if severity == 1 and version_name == given_version_to_pin and application_id == "ezetap_android" and device_type_db == "PAX":
                        if status == 'INACTIVE':
                            query = "UPDATE app_version SET status = 'ACTIVE' WHERE status = 'INACTIVE' AND severity = 1 AND device_type = 'PAX' AND application_id = 'ezetap_android' AND org_code = '" + str(
                                org_code) + "' and version_name = '" + str(given_version_to_pin) + "';"
                            DBProcessor.setValueToDB(query)
                            logger.debug("updated the status in to active")
                        pin_to_merchant = "False"
                        logger.debug(f"update Pax version is already pinned to the merchant")
                    else:
                        pin_to_merchant = "True"
                        logger.info(f"update Pax version is not pinned to the merchant")
            else:
                app_file_name = "mpos"
                query = "select * from app_version where org_code='" + str(
                    org_code) + "' and severity = 1 AND application_id = 'ezetap_android' and version_name = '" + str(
                    given_version_to_pin) + "' and device_type = 'REGULAR_ANDROID';"
                result = DBProcessor.getValueFromDB(query)
                if result.empty:
                    pin_to_merchant = "True"
                    logger.info(f"empty data frame is validated successfully")
                else:
                    severity = int(result['severity'].values[0])
                    version_name = result['version_name'].values[0]
                    application_id = result['application_id'].values[0]
                    status = result['status'].values[0]
                    device_type_db = result['device_type'].values[0]
                    if severity == 1 and version_name == given_version_to_pin and application_id == "ezetap_android" and device_type_db == "REGULAR_ANDROID":
                        if status == 'INACTIVE':
                            query = "UPDATE app_version SET status = 'ACTIVE' WHERE status = 'INACTIVE' AND severity = 1 AND (device_type = 'REGULAR_ANDROID' or device_type = '') AND  application_id = 'ezetap_android' AND org_code = '" + str(
                                org_code) + "' and version_name = '" + str(given_version_to_pin) + "';"
                            DBProcessor.setValueToDB(query)
                            logger.debug("updated the status in to active")
                        pin_to_merchant = "False"
                        logger.debug(f"update mobile version is already pinned to the merchant")
                    else:
                        pin_to_merchant = "True"
                        logger.info(f"update mobile version is not pinned to the merchant")

            original_mpos_app_version = get_mpos_version(str(id_of_device))
            logger.debug(f"app_version: {original_mpos_app_version}")
            logger.debug(f"given_version: {given_version_to_pin}")
            logger.debug(f"comparison started")
            if given_version_to_pin > original_mpos_app_version:
                if pin_to_merchant == "True":
                    pinning_mpos_version_to_merchant(org_code, ver_code, given_version_to_pin,1)
                else:
                    logger.info(f"version is already pinned to merchant")
            else:
                install_lower_mpos_version(app_list,given_version_to_pin,directory_path,id_of_device)
                logger.debug("Mpos version is greater tha given_pinned_version. So, installing lower version")
                if pin_to_merchant == "True":
                    pinning_mpos_version_to_merchant(org_code, ver_code, given_version_to_pin,1)
                else:
                    logger.info(f"version is already pinned to merchant")
            api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                  "password": portal_password})
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for cache refresh is : {response}")
        except:
            unpining_mpos_update_version(org_code, given_version_to_pin,1)
            api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                  "password": portal_password})
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for cache refresh is : {response}")

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
            try:
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                update_page = OTA_upgrade(app_driver)
                try:
                    update_tab = update_page.fetch_update_tap_tittle()
                    txt_skip = update_page.fetch_skip_txt_from_skip_button()
                except:
                    update_tab = "N/A"
                    txt_skip = "N/A"
                update_page.click_on_update_now()
                try:
                    update_page.click_on_install()
                    logger.debug("clicked on install button")
                except:
                    update_page.click_on_update_btn()
                try:
                    update_page.click_on_done()
                except:
                    update_page.click_on_done_2()
                app_driver.launch_app()
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                account_page = AccountPage(app_driver)
                try:
                    home_page.click_account_menu()
                    mpos_version_details = account_page.fetch_mpos_version()
                except:
                    home_page.click_account_menu()
                    mpos_version_details = account_page.fetch_mpos_version()
                mpos_app_version = [value.replace('v.', '') for value in mpos_version_details.split() if
                                    value.startswith('v.')]
                actual_mpos_version = mpos_app_version[0] if mpos_app_version else 'N/A'
            finally:
                logger.debug(f"unpin the app update is started")
                unpining_mpos_update_version(org_code,given_version_to_pin,1)
                logger.debug(f"Revert to original version")
                mpos_version_in_config_file = ConfigReader.read_config("Applications", app_file_name)
                pattern = r'\d+\.\d+\.\d+'
                matches = re.findall(pattern, mpos_version_in_config_file)
                version = matches[0]
                if original_mpos_app_version == version:
                    try:
                        uninstall_mpos_application()
                        logger.debug('Application uninstallation done successfully.')
                        mpos_path = get_mpos_app_path()
                        install_mpos_application(id_of_device,mpos_path)
                    except:
                        pass
                else:
                    logger.info(
                        f"Revert to original version is Failed because original version and the version under Applications is not same in the config.ini")
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
                    "Update_tab": "App Update",
                    "mpos_version": given_version_to_pin,
                    "skip": "Skip"
                }
                actual_app_values = {
                    "Update_tab": update_tab,
                    "mpos_version": actual_mpos_version,
                    "skip": txt_skip
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_mpos_400_405_002():
    """
    Sub Feature Code: UI_Common_Card_Generic_AppUpdate_Mandatory_01
    Sub Feature Description: Performing a mandatory update of the Mpos app successfully
    TC naming code description:
     TC naming code description:400: Generic Actions, 405: AppUpdates, 002: TC002
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
        id_of_device = device_id
        given_version_to_pin = ConfigReader.read_config("OtaUpdate", "mpos_version")
        ver_code = ConfigReader.read_config("OtaUpdate", "mpos_version_code")
        logger.debug(f"Result:- {result} and type:- {type(result)}")
        directory_path = ConfigReader.read_config_paths("System", "automation_suite_path") + "/App"
        app_list = get_all_file_names(directory_path)
        try:
            if str(ConfigReader.read_config("ParallelExecution", "deviceOnly")).lower() == 'true':
                app_file_name = "pax_mpos"
                query = "select * from app_version where org_code='" + str(
                    org_code) + "' and severity = 0  and device_type = 'PAX' AND application_id = 'ezetap_android' and version_name = '" + str(
                    given_version_to_pin) + "';"
                result = DBProcessor.getValueFromDB(query)
                if result.empty:
                    pin_to_merchant = "True"
                    logger.info(f"empty data frame is validated successfully")
                else:
                    severity = int(result['severity'].values[0])
                    version_name = result['version_name'].values[0]
                    application_id = result['application_id'].values[0]
                    status = result['status'].values[0]
                    device_type_db = result['device_type'].values[0]
                    if severity == 0 and version_name == given_version_to_pin and application_id == "ezetap_android" and device_type_db == "PAX":
                        if status == 'INACTIVE':
                            query = "UPDATE app_version SET status = 'ACTIVE' WHERE status = 'INACTIVE' AND severity = 0 AND device_type = 'PAX' AND application_id = 'ezetap_android' AND org_code = '" + str(
                                org_code) + "' AND version_name = '" + str(given_version_to_pin) + "';"
                            DBProcessor.setValueToDB(query)
                            logger.debug("updated the status in to active")
                        pin_to_merchant = "False"
                        logger.debug(f"update Pax version is already pinned to the merchant")
                    else:
                        pin_to_merchant = "True"
                        logger.info(f"update Pax version is not pinned to the merchant")
            else:
                app_file_name = "mpos"
                query = "select * from app_version where org_code='" + str(
                    org_code) + "' and severity = 0 AND application_id = 'ezetap_android' and version_name = '" + str(
                    given_version_to_pin) + "' and device_type = 'REGULAR_ANDROID';"
                result = DBProcessor.getValueFromDB(query)
                if result.empty:
                    pin_to_merchant = "True"
                    logger.info(f"empty data frame is validated successfully")
                else:
                    severity = int(result['severity'].values[0])
                    version_name = result['version_name'].values[0]
                    application_id = result['application_id'].values[0]
                    status = result['status'].values[0]
                    device_type_db = result['device_type'].values[0]
                    if severity == 0 and version_name == given_version_to_pin and application_id == "ezetap_android" and device_type_db == 'REGULAR_ANDROID':
                        if status == 'INACTIVE':
                            query = "UPDATE app_version SET status = 'ACTIVE' WHERE status = 'INACTIVE' AND severity = 0 AND (device_type = 'REGULAR_ANDROID' or device_type = '') AND  application_id = 'ezetap_android' AND org_code = '" + str(
                                org_code) + "' and version_name = '" + str(given_version_to_pin) + "';"
                            DBProcessor.setValueToDB(query)
                            logger.debug("updated the status in to active")
                        pin_to_merchant = "False"
                        logger.debug(f"update mobile version is already pinned to merchant")
                    else:
                        pin_to_merchant = "True"
                        logger.info(f"update mobile version is not pinned to merchant")

            mpos = get_mpos_version(str(id_of_device))
            original_mpos_app_version = mpos
            logger.debug(f"app_version: {original_mpos_app_version}")
            logger.debug(f"given_version: {given_version_to_pin}")
            logger.debug(f"comparison started")
            if given_version_to_pin > original_mpos_app_version:
                if pin_to_merchant == "True":
                    pinning_mpos_version_to_merchant(org_code, ver_code, given_version_to_pin, 0)
                else:
                    logger.info(f"version is already pinned to merchant")
            else:
                install_lower_mpos_version(app_list,given_version_to_pin,directory_path,id_of_device)
                logger.debug("Mpos version is greater tha given_pinned_version. So, installing lower version")
                if pin_to_merchant == "True":
                    pinning_mpos_version_to_merchant(org_code, ver_code, given_version_to_pin, 0)
                else:
                    logger.info(f"version is already pinned to merchant")
            api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                  "password": portal_password})
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response for DB Refresh: {response}")
        except:
            unpining_mpos_update_version(org_code, given_version_to_pin, 0)
            api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                  "password": portal_password})
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response for DB Refresh: {response}")
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
            try:
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                update_page = OTA_upgrade(app_driver)
                try:
                    update_tab = update_page.fetch_update_tap_tittle()
                except Exception as e:
                    update_tab = f"N/A{e}"
                try:
                    txt_skip = update_page.fetch_skip_txt_from_skip_button()
                except:
                    txt_skip = "N/A"
                update_page.click_on_update_now()
                try:
                    update_page.click_on_install()
                except:
                    update_page.click_on_update_btn()
                try:
                    update_page.click_on_done()
                except:
                    update_page.click_on_done_2()
                app_driver.launch_app()
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.click_account_menu()
                account_page = AccountPage(app_driver)
                mpos_version_details = account_page.fetch_mpos_version()
                mpos_version = [value.replace('v.', '') for value in mpos_version_details.split() if
                                value.startswith('v.')]
                actual_mpos_version = mpos_version[0] if mpos_version else 'N/A'
            finally:
                logger.debug(f"unpin the app update is started")
                unpining_mpos_update_version(org_code, given_version_to_pin, 0)
                logger.debug(f"Revert to original version")
                mpos_version_in_config_file = ConfigReader.read_config("Applications", app_file_name)
                pattern = r'\d+\.\d+\.\d+'
                matches = re.findall(pattern, mpos_version_in_config_file)
                version = matches[0]
                if original_mpos_app_version == version:
                    try:
                        uninstall_mpos_application()
                        logger.debug('Application uninstallation done successfully.')
                        mpos_path = get_mpos_app_path()
                        install_mpos_application(id_of_device, mpos_path)
                    except:
                        pass
                else:
                    logger.info(
                        f"Revert to original version is Failed because original version and the version under Applications is not same in the config.ini")
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
                expected_app_values = {"Update_tab": "App Update",
                                       "mpos_version": given_version_to_pin,
                                       "skip": "N/A"}

                actual_app_values = {"Update_tab": update_tab,
                                     "mpos_version": actual_mpos_version,
                                     "skip": txt_skip}
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
