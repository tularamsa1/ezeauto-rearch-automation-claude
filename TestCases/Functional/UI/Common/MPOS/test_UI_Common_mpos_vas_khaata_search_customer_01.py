import sys
import random
import time
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.mpos.Mpos_Khaata import Khaata
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_mpos_600_601_017():
    """
    Sub Feature Code: UI_mpos_vas_Khaata_Search_Customer_Name_01
    Sub Feature Description: Verifiy the customer search results by entering the customer name
    TC naming code description: 600: value_added_services, 601: khaata, 017: TC017
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code=None, portal_un=portal_username,
                                                           portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["enableKhataForMerchants"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)

        logger.debug(f"Response received for setting preconditions is : {response}")
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
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            ph_number_1 = random.randint(6124568645, 6910536941)
            logger.debug(f"Generating random phone number: {ph_number_1}")
            ph_number_2 = random.randint(7224568645, 7910536941)
            logger.debug(f"Generating random phone number: {ph_number_2}")
            ph_number_3 = random.randint(8124568645, 9910536941)
            logger.debug(f"Generating random phone number: {ph_number_3}")
            khaata_holder_name_1 = f"ezetap{random.randint(100, 300)}"
            logger.debug(f"Generating random user name: {khaata_holder_name_1}")
            khaata_holder_name_2 = f"ezetap{random.randint(400, 500)}"
            logger.debug(f"Generating random user name: {khaata_holder_name_2}")
            khaata_holder_name_3 = f"ezetap{random.randint(1, 50)}"
            logger.debug(f"Generating random user name: {khaata_holder_name_3}")
            khaata = Khaata(app_driver)
            khaata.click_my_khaata()
            khaata.create_new_khaata_holder(ph_number_1, khaata_holder_name_1, 'Friend')
            khaata.click_proceed_button()
            logger.debug(f"New khaata holder is created with phone number : {ph_number_1}")
            time.sleep(2)
            khaata.click_on_back()
            khaata.create_new_khaata_holder(ph_number_2, khaata_holder_name_2, 'Supplier')
            khaata.click_proceed_button()
            logger.debug(f"New khaata holder is created with phone number : {ph_number_2}")
            time.sleep(2)
            khaata.click_on_back()
            khaata.create_new_khaata_holder(ph_number_3, khaata_holder_name_3, 'Customer')
            khaata.click_proceed_button()
            logger.debug(f"New khaata holder is created with phone number : {ph_number_3}")
            time.sleep(2)
            khaata.click_on_back()
            khaata.khaata_search(khaata_holder_name_3)
            time.sleep(3)
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
                    "customer_name": khaata_holder_name_3,
                    "label":  "Customer",
                    "mobile_number":   str(ph_number_3)
                }
                khaata.click_first_khaata_holder_search_result()
                time.sleep(2)
                khaata_holder_name = khaata.fetch_khaata_holder_name_from_account()
                khaata_holder_tag = khaata.fetch_khaata_holder_tag_from_account()
                khaata_holder_ph_number = khaata.fetch_khaata_holder_phone_number_from_account()
                actual_app_values = {
                    "customer_name": khaata_holder_name,
                    "label": khaata_holder_tag,
                    "mobile_number": str(khaata_holder_ph_number)
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
def test_mpos_600_601_018():
    """
    Sub Feature Code: UI_mpos_vas_Khaata_Search_Customer_Mobile_01
    Sub Feature Description: Verifiy the customer by entering the mobile number
    TC naming code description: 600: value_added_services, 601: khaata, 018: TC018
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code=None, portal_un=portal_username,
                                                           portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["enableKhataForMerchants"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
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
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            ph_number_1 = random.randint(7124568645, 9910536941)
            logger.debug(f"Generating random phone number: {ph_number_1}")
            ph_number_2 = random.randint(6944568645, 8810536941)
            logger.debug(f"Generating random phone number: {ph_number_2}")
            ph_number_3 = random.randint(8774568645, 9190536941)
            logger.debug(f"Generating random phone number: {ph_number_3}")
            khaata_holder_name_1 = f"ezetap{random.randint(1, 9999)}"
            logger.debug(f"Generating random user name: {khaata_holder_name_1}")
            khaata_holder_name_2 = f"ezetap{random.randint(1, 9999)}"
            logger.debug(f"Generating random user name: {khaata_holder_name_2}")
            khaata_holder_name_3 = f"ezetap{random.randint(1, 9999)}"
            logger.debug(f"Generating random user name: {khaata_holder_name_3}")
            khaata = Khaata(app_driver)
            khaata.click_my_khaata()
            khaata.create_new_khaata_holder(ph_number_1, khaata_holder_name_1, 'Customer')
            khaata.click_proceed_button()
            logger.debug(f"New khaata holder is created with phone number : {ph_number_1}")
            time.sleep(2)
            khaata.click_on_back()
            khaata.create_new_khaata_holder(ph_number_2, khaata_holder_name_2, 'Supplier')
            khaata.click_proceed_button()
            logger.debug(f"New khaata holder is created with phone number : {ph_number_2}")
            time.sleep(2)
            khaata.click_on_back()
            khaata.create_new_khaata_holder(ph_number_3, khaata_holder_name_3, 'Staff')
            khaata.click_proceed_button()
            logger.debug(f"New khaata holder is created with phone number : {ph_number_3}")
            time.sleep(2)
            khaata.click_on_back()
            khaata.khaata_search(ph_number_2)
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
                    "Customer_name": khaata_holder_name_2,
                    "label":  "Supplier",
                    "mobile_number":   str(ph_number_2)
                }
                khaata.click_first_khaata_holder_search_result()
                time.sleep(2)
                khaata_holder_name = khaata.fetch_khaata_holder_name_from_account()
                khaata_holder_tag = khaata.fetch_khaata_holder_tag_from_account()
                khaata_holder_ph_number = khaata.fetch_khaata_holder_phone_number_from_account()
                actual_app_values = {
                    "Customer_name": khaata_holder_name,
                    "label": khaata_holder_tag,
                    "mobile_number": str(khaata_holder_ph_number)
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
def test_mpos_600_601_019():
    """
    Sub Feature Code: UI_mpos_vas_Khaata_Search_Customer_NonExisting_01
    Sub Feature Description: Verifiy the customer by entering the customer name which doesn't exist
    TC naming code description: 600: value_added_services, 601: khaata, 019: TC019
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code=None, portal_un=portal_username,
                                                           portal_pw=portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["enableKhataForMerchants"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
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
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            ph_number_1 = random.randint(7124568645, 8360536941)
            logger.debug(f"Generating random phone number: {ph_number_1}")
            ph_number_2 = random.randint(6524568645, 7410536941)
            logger.debug(f"Generating random phone number: {ph_number_2}")
            ph_number_3 = random.randint(8624568645, 9100536941)
            logger.debug(f"Generating random phone number: {ph_number_3}")
            khaata_holder_name_1 = f"ezetap{random.randint(700, 9999)}"
            logger.debug(f"Generating random user name: {khaata_holder_name_1}")
            khaata_holder_name_2 = f"ezetap{random.randint(600, 9999)}"
            logger.debug(f"Generating random user name: {khaata_holder_name_2}")
            khaata_holder_name_3 = f"ezetap{random.randint(500, 9999)}"
            logger.debug(f"Generating random user name: {khaata_holder_name_3}")
            no_customer = "#@#$^*@@#(($"
            khaata = Khaata(app_driver)
            khaata.click_my_khaata()
            khaata.create_new_khaata_holder(ph_number_1, khaata_holder_name_1, 'Friend')
            khaata.click_proceed_button()
            logger.debug(f"New khaata holder is created with phone number : {ph_number_1}")
            time.sleep(2)
            khaata.click_on_back()
            khaata.create_new_khaata_holder(ph_number_2, khaata_holder_name_2, 'Supplier')
            khaata.click_proceed_button()
            logger.debug(f"New khaata holder is created with phone number : {ph_number_2}")
            time.sleep(2)
            khaata.click_on_back()
            khaata.create_new_khaata_holder(ph_number_3, khaata_holder_name_3, 'Customer')
            khaata.click_proceed_button()
            logger.debug(f"New khaata holder is created with phone number : {ph_number_3}")
            time.sleep(2)
            khaata.click_on_back()
            khaata.khaata_search(no_customer)
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
                    "message": "No Khaata Holder found"
                }
                error_message = khaata.fetch_no_search_result_found()
                actual_app_values = {
                    "message": error_message
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


