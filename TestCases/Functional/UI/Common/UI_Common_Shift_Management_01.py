import random
import re
import sys
import time
import pendulum
import pytest
from datetime import datetime, timedelta
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_600_603_001():
    """
    Sub Feature Code: UI_Common_shift_management_end_button_start_date_time_view_summary
    Sub Feature Description: 1. verify shift management dashboard on home screen.
    2. verify shift management dashboard on txn screen.
    3. verify end shift button, start date and time on home page.
    4. verify after ending shift without performing any txn on home page.
    5. verify after ending shift without performing any txn on txn screen.
    6. verify cancel end shift on txn screen.
    7. verify invisibility of view summary when there no txn performed on history page.
    TC naming code description: 600: Payment Method, 603: CARD_DCC, 001: TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('shift_update', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions : {response}")

        api_details = DBProcessor.get_api_details('end_shift', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received from end shift api : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            history_page = TransHistoryPage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            dashboard_enabled = [True if home_page.fetch_shift_management_dashboard_enabled_home_page() else False][0]
            logger.debug(f"dashboard visibility from app home screen : {dashboard_enabled}")
            current_shift = home_page.get_current_shift_on_dashboard_home_page()
            logger.debug(f"current dashboard shift from app home screen : {current_shift}")

            end_shift_button_home_page = home_page.validation_end_shift_button_home_page()
            logger.debug(f"end shift button from app home page : {end_shift_button_home_page}")

            shift_start_data_time = [True if home_page.fetch_shift_start_date_time() else False][0]
            logger.debug(f"shift start date and time from app home page : {shift_start_data_time}")

            home_page.perform_end_shift_home_page()
            home_page.click_yes_proceed()
            current_shift_after_ending = home_page.get_current_shift_on_dashboard_home_page()

            logger.debug(f"current dashboard shift after ending shift from app home screen : {current_shift_after_ending}")
            home_page.click_on_history()
            dashboard_enabled_history_page = [True if history_page.fetch_shift_dashboard_management_enabled_history_page()
                                              else False][0]
            logger.debug(f"dashboard visibility from app history screen : {dashboard_enabled_history_page}")

            current_shift_history_page = history_page.fetch_shift_dashboard_management_enabled_history_page()
            logger.debug(f"current shift in history page : {current_shift_history_page}")

            history_page.perform_end_shift_history_page()
            home_page.click_cancel_to_end_shift()

            current_shift_after_cancel_history_page = history_page.fetch_shift_dashboard_management_enabled_history_page()
            logger.debug(f"current shift after cancel in history page : {current_shift_after_cancel_history_page}")

            time.sleep(3)
            history_page.perform_end_shift_history_page()
            home_page.click_yes_proceed()

            current_shift_after_ending_history_page = history_page.fetch_shift_dashboard_management_enabled_history_page()
            logger.debug(f"current shift after ending in history page : {current_shift_after_ending_history_page}")

            view_summary_app = history_page.validate_view_summary_button_invisibility()
            logger.debug(f"fetching view summary text from app history page : '{view_summary_app}'")

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
                expected_app_values = {
                    "dashboard_visible": True,
                    "dashboard_visible_history_page": True,
                    "current_shift": current_shift,
                    "end_shift": "End Shift",
                    "shift_date_time": True,
                    "cancel_end_shift_status": current_shift_history_page,
                    "proceed_end_shift_status": current_shift_history_page,
                    "invisibility_of_view_summary": True
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "dashboard_visible": dashboard_enabled,
                    "dashboard_visible_history_page": dashboard_enabled_history_page,
                    "current_shift": current_shift_after_ending,
                    "end_shift": end_shift_button_home_page,
                    "shift_date_time": shift_start_data_time,
                    "cancel_end_shift_status": current_shift_after_cancel_history_page,
                    "proceed_end_shift_status": current_shift_after_ending_history_page,
                    "invisibility_of_view_summary": view_summary_app
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

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
def test_common_600_603_002():
    """
    Sub Feature Code: UI_Common_shift_management_end_shift_button_Yes_No_and_new_shift_numbers
    Sub Feature Description: 1. verify end button on home screen.
    2. verify end shift by clicking proceed to end on home screen.
    3. verify end shift button by clicking cancel end shift on home screen.
    4. verify end button on txn screen.
    5. verify end shift by clicking proceed to end on txn screen.
    6. verify end shift button by clicking cancel end shift on txn screen.
    7. verify current shift ended and new shift started.
    TC naming code description: 600: Payment Method, 603: CARD_DCC, 002: TC002
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('shift_update', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions : {response}")

        api_details = DBProcessor.get_api_details('end_shift', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received from end shift api : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            history_page = TransHistoryPage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(10, 500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Cash()
            payment_page.click_on_confirm()
            payment_page.click_on_proceed_homepage()
            home_page.click_grow_your_business()
            current_shift = home_page.get_current_shift_on_dashboard_home_page()
            logger.debug(f"current dashboard shift from app home screen : {current_shift}")

            total_amount_dashboard_home_page = home_page.get_current_shift_amount_home_page()
            logger.debug(f"total amount from dashboard home page : {total_amount_dashboard_home_page}")

            shift_start_date_time_home_page = home_page.fetch_shift_start_date_time()[10::]
            current_datetime = pendulum.now().year
            logger.debug(f"current year : {current_datetime}")
            logger.debug(f"app home page shift start date and time : {shift_start_date_time_home_page}")
            shift_number = re.findall(r'\d+', current_shift)
            logger.debug(f"current shift number {shift_number}")

            home_page.perform_end_shift_home_page()
            home_page.click_cancel_to_end_shift()
            current_shift_after_cancel_home_page = home_page.get_current_shift_on_dashboard_home_page()
            logger.debug(f"current shift after cancel in home page : {current_shift_after_cancel_home_page}")

            # time.sleep(3)
            home_page.perform_end_shift_home_page()
            home_page.click_yes_proceed()
            home_page.close_receipt()
            time.sleep(2)
            current_shift_after_ending = home_page.get_current_shift_on_dashboard_home_page()
            logger.debug(f"after ending the shift fetching current shift from app home page : {current_shift_after_ending}")

            def increment_number(match):
                return str(int(match.group(0)) + 1)

            current_shift_after_ending_1 = re.sub(r'\d+', increment_number, current_shift)
            logger.debug(f"after ending the current shift incrementing the current shift by plus one : {current_shift_after_ending_1}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            posting_date_db = result['posting_date'].values[0]
            logger.debug(f"posting date from txn table db : {posting_date_db}")

            today_start_date_time = pendulum.now().format('YYYY-MM-DD')
            query = (f"select sum(amount) from txn where username = '{app_username}' and org_code = '{org_code}' and "
                     f"process_code = 'Shift_{shift_number[0]}' and modified_time "
                     f"between '{today_start_date_time} 00:00:00' and '{today_start_date_time} 11:59:59'")
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            total_shift_amount_db = str(result.values[0]).strip("[].")
            logger.debug(f"total shift amount from db : {total_shift_amount_db}")

            # second txn to validate history page
            amount = random.randint(10, 500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Cash()
            payment_page.click_on_confirm()
            payment_page.click_on_proceed_homepage()
            home_page.wait_for_home_page_load()
            home_page.click_on_history()

            current_shift_history_page = history_page.fetch_shift_dashboard_management_enabled_history_page()
            logger.debug(f"current shift in history page : {current_shift_history_page}")

            history_page.perform_end_shift_history_page()
            home_page.click_cancel_to_end_shift()
            current_shift_after_cancel_history_page = history_page.fetch_shift_dashboard_management_enabled_history_page()
            logger.debug(f"current shift after cancel in history page : {current_shift_after_cancel_history_page}")

            time.sleep(3)
            history_page.perform_end_shift_history_page()
            home_page.click_yes_proceed()
            home_page.close_receipt()

            current_shift_after_ending_history_page = history_page.fetch_shift_dashboard_management_enabled_history_page()
            logger.debug(f"current shift after ending in history page : {current_shift_after_ending_history_page}")

            def increment_number(match):
                return str(int(match.group(0)) + 1)

            current_shift_after_ending_history_page_1 = re.sub(r'\d+', increment_number, current_shift_history_page)
            logger.debug(f"after ending the current shift incrementing the current shift by plus one : {current_shift_after_ending_1}")

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
                date_and_time = date_time_converter.to_app_format(posting_date_db)
                expected_app_values = {
                    "total_shift_txn_amount": "₹ " + total_shift_amount_db + ".00",
                    # "shift_start_date_time": date_and_time,
                    "cancel_end_shift_status_home_page": current_shift,
                    "proceed_end_shift_status_home_page": current_shift_after_ending,
                    "cancel_end_shift_status_history_page": current_shift_history_page,
                    "proceed_end_shift_status_history_page": current_shift_after_ending_history_page_1
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "total_shift_txn_amount": total_amount_dashboard_home_page,
                    # "shift_start_date_time": shift_start_date_time_home_page,
                    "cancel_end_shift_status_home_page": current_shift_after_cancel_home_page,
                    "proceed_end_shift_status_home_page": current_shift_after_ending_1,
                    "cancel_end_shift_status_history_page": current_shift_after_cancel_history_page,
                    "proceed_end_shift_status_history_page": current_shift_after_ending_history_page
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

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
def test_common_600_603_003():
    """
    Sub Feature Code: UI_Common_shift_management_sale_count_same_amount_filter_payment_mode_and_status
    Sub Feature Description: 1. verify shift number on txn screen.
    2. verify Total sale and total count should be displayed on txn screen.
    3. Verify end shift button on txn screen.
    4. verify all txns wrt to that particular shift on txn screen.
    5. verify view summary button on txn screen.
    6. verify current and previous shift inside the filter screen.
    7. verify payment methods and payment status in the filter screen.
    8. verify view summary button in the txn history page.
    TC naming code description: 600: Payment Method, 603: CARD_DCC, 003: TC003
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('shift_update', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions : {response}")

        api_details = DBProcessor.get_api_details('end_shift', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received from end shift api : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(10, 500)
            logger.debug(f"Entered amount is : {amount}")
            order_id_1 = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id_1}")
            home_page.enter_amount_and_order_number(amount, order_id_1)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id_1)
            payment_page.click_on_Cash()
            payment_page.click_on_confirm()
            payment_page.click_on_proceed_homepage()
            home_page.click_grow_your_business()

            # second txn to validate history page
            amount = random.randint(250, 400)
            logger.debug(f"Entered amount is : {amount}")
            order_id_2 = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id_2}")
            home_page.enter_amount_and_order_number(amount, order_id_2)
            payment_page = PaymentPage(app_driver)
            history_page = TransHistoryPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id_2)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status_refunded = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status_refunded}")
            payment_page.click_on_proceed_homepage()
            home_page.wait_for_home_page_load()
            home_page.click_on_history()

            current_shift = history_page.fetch_shift_dashboard_management_enabled_history_page()
            logger.debug(f"current shift in history page : {current_shift}")

            current_shift_history_page = [True if current_shift else False][0]
            logger.debug(f"current shift name is visible on history page : {current_shift_history_page}")

            shift_number = re.findall(r'\d+', current_shift)
            logger.debug(f"current shift number {shift_number}")

            total_amount_dashboard_history_page = history_page.get_total_shift_amount_history_page()
            logger.debug(f"total amount from dashboard home page : {total_amount_dashboard_history_page}")

            end_shift_button_history_page = history_page.fetch_end_shift_history_page()
            logger.debug(f"fetching end shift button from app history page : {end_shift_button_history_page}")

            order_ids = history_page.fetch_order_ids_from_history_page()
            logger.debug(f"feting all the txns order ids from app history page {order_ids}")

            view_summary_app = history_page.fetch_view_summary()
            logger.debug(f"fetching view summary text from app history page : {view_summary_app}")

            history_page.perform_click_filter()

            payment_mode_and_status = history_page.validate_all_payment_modes_and_status()
            logger.debug(f"all payment modes and status from filter page : {payment_mode_and_status}")
            upi_payment_mode = ["UPI" for ele in payment_mode_and_status if "UPI" in payment_mode_and_status][0]
            logger.debug(f"UPI payment mode from filter page : {upi_payment_mode}")
            success_status = ["Success" for ele in payment_mode_and_status if "Success" in payment_mode_and_status][0]
            logger.debug(f"success status from filter page : {success_status}")

            history_page.perform_click_shift_list()
            list_of_current_previous_shift = history_page.fetching_current_previous_shift()
            logger.debug(f"list of all the shift of the day : {list_of_current_previous_shift}")

            today_start_date_time = pendulum.now().format('YYYY-MM-DD')
            yesterday = pendulum.now().subtract(days=1).format('YYYY-MM-DD')
            query = (f"select sum(amount) from txn where username = '{app_username}' and org_code = '{org_code}' and "
                     f"process_code = 'Shift_{shift_number[0]}' and created_time "
                     f"between '{yesterday} 18:30:00' and '{today_start_date_time} 18:29:59'")
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            total_shift_amount_db = str(result.values[0]).strip("[].")
            logger.debug(f"total shift amount from db : {total_shift_amount_db}")

            today_start_date_time = pendulum.now().format('YYYY-MM-DD')
            yesterday = pendulum.now().subtract(days=1).format('YYYY-MM-DD')
            query = (f"select count(*) from shift_detail where org_code = 'shift_FGH11' and created_time between "
                     f"'{yesterday} 18:30:00' and '{today_start_date_time} 18:29:59'")
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            number_of_shifts = str(result.values).strip("[]")
            logger.debug(f"number shift performed today {number_of_shifts}")

            query = (f"select shift_no from shift_detail where org_code = 'shift_FGH11' and created_time between "
                     f"'{yesterday} 18:30:00' and '{today_start_date_time} 18:29:59'")
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            list_of_shift_numbers_db = []
            for ele in range(int(number_of_shifts)):
                list_of_shift_numbers_db.append(result.values[ele][0])
            logger.debug(f"list of shift numbers fro  db : {list_of_shift_numbers_db}")

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
                expected_app_values = {
                    "current_shift": True,
                    "total_sale": "₹ " + total_shift_amount_db + ".00",
                    "total_shift_txns": [order_id_2, order_id_1],
                    "end_shift": "End Shift",
                    "pmt_mode": "UPI",
                    "pmt_status": "Success",
                    "view_summary": "View Summary",
                    "current_previous_shift": len(list_of_shift_numbers_db)
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "current_shift": current_shift_history_page,
                    "total_sale": total_amount_dashboard_history_page,
                    "total_shift_txns": order_ids,
                    "end_shift": end_shift_button_history_page,
                    "pmt_mode": upi_payment_mode,
                    "pmt_status": success_status,
                    "view_summary": view_summary_app,
                    "current_previous_shift": len(list_of_current_previous_shift)
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

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
def test_common_600_603_004():
    """
    Sub Feature Code: UI_Common_txns_history_based_shift_filter_mode_and_status
    Sub Feature Description: 1. verify based on the shift filter(current/previous) txns should get displayed.
    2. verify filtered txns based on payment method.
    3. verify filtered txns based on payment status.
    TC naming code description: 600: Payment Method, 603: CARD_DCC, 004: TC004
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('shift_update', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions : {response}")

        api_details = DBProcessor.get_api_details('end_shift', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received from end shift api : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(10, 500)
            logger.debug(f"Entered amount is : {amount}")
            order_id_1 = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id_1}")
            home_page.enter_amount_and_order_number(amount, order_id_1)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id_1)
            payment_page.click_on_Cash()
            payment_page.click_on_confirm()
            payment_page.click_on_proceed_homepage()
            home_page.click_grow_your_business()

            # second txn to validate history page
            amount = random.randint(250, 400)
            logger.debug(f"Entered amount is : {amount}")
            order_id_2 = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id_2}")
            home_page.enter_amount_and_order_number(amount, order_id_2)
            payment_page = PaymentPage(app_driver)
            history_page = TransHistoryPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id_2)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status_refunded = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status_refunded}")
            payment_page.click_on_proceed_homepage()
            home_page.wait_for_home_page_load()
            home_page.click_on_history()

            history_page.perform_click_filter()
            history_page.perform_click_apply_filter()
            order_ids = history_page.fetch_order_ids_from_history_page()
            logger.debug(f"feting all the txns order ids from app history page {order_ids}")

            query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id_2}'"
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            history_page.perform_click_filter()
            history_page.perform_click_on_upi_pmt_mode()
            history_page.perform_click_apply_filter()
            history_page.click_on_transaction_by_txn_id(txn_id)
            payment_mode = history_page.fetch_txn_type_text()
            logger.debug(f"fetching payment mode based on filter : {payment_mode}")
            history_page.click_back_Btn_transaction_details()
            time.sleep(2)
            history_page.click_back_Btn()

            history_page.perform_click_filter()
            history_page.perform_click_on_success_status()
            history_page.perform_click_apply_filter()
            GlobalVariables.bool_validate_multiple_txns = False
            history_page.click_on_transaction_by_txn_id(txn_id)
            pmt_status = history_page.fetch_txn_status_text()
            logger.debug(f"based on filter pmt status from app : {pmt_status}")

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
                expected_app_values = {
                    "total_shift_txns": [order_id_2, order_id_1],
                    "pmt_mode": "UPI",
                    "pmt_status": "STATUS:AUTHORIZED"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "total_shift_txns": order_ids,
                    "pmt_mode": payment_mode,
                    "pmt_status": pmt_status
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

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
def test_common_600_603_005():
    """
    Sub Feature Code: UI_Common_shift_management_enable_disable_home_and_txn_history
    Sub Feature Description: 1. verify shift management feature by disabling from user level.
    2. verify again after enabling shift management feature old shift should get end and new shift should be started.
    TC naming code description: 600: Payment Method, 603: CARD_DCC, 005: TC005
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('shift_update', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions : {response}")

        api_details = DBProcessor.get_api_details('end_shift', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received from end shift api : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(10, 500)
            logger.debug(f"Entered amount is : {amount}")
            order_id_1 = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id_1}")
            home_page.enter_amount_and_order_number(amount, order_id_1)
            payment_page = PaymentPage(app_driver)
            history_page = TransHistoryPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id_1)
            payment_page.click_on_Cash()
            payment_page.click_on_confirm()
            payment_page.click_on_proceed_homepage()
            home_page.click_grow_your_business()

            current_shift_before_disable = home_page.get_current_shift_on_dashboard_home_page()
            logger.debug(f"current shift before disable at home page : {current_shift_before_disable}")

            def increment_number(match):
                return str(int(match.group(0)) + 1)

            current_shift_after_enabling_1 = re.sub(r'\d+', increment_number, current_shift_before_disable)
            logger.debug(f"after ending the current shift incrementing the current shift by plus one : {current_shift_after_enabling_1}")

            api_details = DBProcessor.get_api_details('shift_update', request_body={
                "username": app_username,
                "password": app_password,
                "shiftManagementEnabled": False
            })
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for setting preconditions : {response}")

            app_driver.reset()
            login_page.perform_login(username=app_username, password=app_password)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()

            dashboard_enabled = [True if history_page.validate_invisibility_of_dashboard() else False][0]
            logger.debug(f"dashboard invisibility from app home screen : {dashboard_enabled}")

            api_details = DBProcessor.get_api_details('shift_update', request_body={
                "username": app_username,
                "password": app_password,
                "shiftManagementEnabled": True
            })
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for setting preconditions : {response}")
            app_driver.reset()
            login_page.perform_login(username=app_username, password=app_password)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            current_shift_after_enabling = home_page.get_current_shift_on_dashboard_home_page()
            logger.debug(f"current shift after at home page : {current_shift_after_enabling}")

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
                expected_app_values = {
                    "dashboard_invisible": True,
                    "dashboard_visibility": current_shift_after_enabling_1
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "dashboard_invisible": dashboard_enabled,
                    "dashboard_visibility": current_shift_after_enabling
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

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
def test_common_600_603_006():
    """
    Sub Feature Code: UI_Common_view_summary_org_code_shift_num_tid_mid_start_date_time
    Sub Feature Description: 1. verify by clicking on view summary all the txns are visible on page based on payment mode.
    2. verify shift number in the receipt.
    3. verify start date and time in the receipt.
    4. verify shift start and end timings in receipt.
    5. verify mid and tid.
    6. verify merchant name in the receipt.
    7. verify current date in receipt.
    with online pin  (bin:222297)
    TC naming code description: 600: Payment Method, 603: CARD_DCC, 006: TC006
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('shift_update', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions : {response}")

        api_details = DBProcessor.get_api_details('end_shift', request_body={
            "username": app_username,
            "password": app_password,
            "shiftManagementEnabled": True
        })
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received from end shift api : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount_1 = random.randint(250, 400)
            logger.debug(f"Entered amount is : {amount_1}")
            order_id_2 = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id_2}")
            home_page.enter_amount_and_order_number(amount_1, order_id_2)
            payment_page = PaymentPage(app_driver)
            history_page = TransHistoryPage(app_driver)
            payment_page.is_payment_page_displayed(amount_1, order_id_2)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            app_payment_status_refunded = payment_page.fetch_payment_status()
            logger.debug(f"Fetching Transaction status of the transaction : {app_payment_status_refunded}")
            payment_page.click_on_proceed_homepage()
            home_page.wait_for_home_page_load()
            home_page.click_grow_your_business()

            current_shift = home_page.get_current_shift_on_dashboard_home_page()
            logger.debug(f"current shift at home page : {current_shift}")
            current_shift_1 = str(current_shift).split()

            amount_2 = random.randint(10, 500)
            logger.debug(f"Entered amount is : {amount_2}")
            order_id_1 = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id_1}")
            home_page.enter_amount_and_order_number(amount_2, order_id_1)
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount_2, order_id_1)
            payment_page.click_on_Cash()
            payment_page.click_on_confirm()
            payment_page.click_on_proceed_homepage()
            home_page.click_on_history()

            today_start_date_time = pendulum.now().format('YYYY-MM-DD')
            yesterday = pendulum.now().subtract(days=1).format('YYYY-MM-DD')
            query = (f"select * from txn where org_code = '{org_code}' and "
                     f"process_code = '{current_shift_1[0]}_{current_shift_1[1]}' and payment_mode = 'UPI' and "
                     f"created_time between '{yesterday} 18:30:00' and '{today_start_date_time} 18:29:59'")
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            tid_db = result['tid'].values[0]
            logger.debug(f"tid from db  : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"mid from db  : {mid_db}")

            history_page.perform_end_shift_history_page()
            home_page.click_yes_proceed()

            query = (f"select * from shift_detail where org_code = '{org_code}' and shift_no = {current_shift_1[1]} "
                     f"and created_time between '{yesterday} 18:30:00' and '{today_start_date_time} 18:29:59'")
            logger.debug(f"Query to fetch shift details from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"shift created time from db  {created_time}")
            shift_ended_time = result['modified_time'].values[0]
            logger.debug(f"shift ended time from db  {shift_ended_time}")

            input_time_str_started = str(created_time)[:26]
            input_time_created = datetime.strptime(input_time_str_started, "%Y-%m-%dT%H:%M:%S.%f")
            time_difference = timedelta(hours=5, minutes=30)
            converted_time = input_time_created + time_difference
            output_time_str_1 = converted_time.strftime("%H:%M:%S")
            logger.debug(f"created time based on app : {output_time_str_1}")

            input_time_str_ended = str(shift_ended_time)[:26]
            input_time_ended = datetime.strptime(input_time_str_ended, "%Y-%m-%dT%H:%M:%S.%f")
            time_difference = timedelta(hours=5, minutes=30)
            converted_time_ended = input_time_ended + time_difference
            output_time_str_2 = converted_time_ended.strftime("%H:%M:%S")
            logger.debug(f"ended time based on app : {output_time_str_2}")

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
                today_start_date_time = pendulum.now().format('YYYY-MM-DD')
                expected_app_values = {
                    "merchant_code": org_code,
                    "shift_num": current_shift_1[1],
                    "receipt_date": today_start_date_time,
                    "shift_created_time": output_time_str_1,
                    "ended_shift_timed": output_time_str_2,
                    "mid": mid_db,
                    "tid": tid_db,
                    "upi_sale_count": "1",
                    "upi_sale_amount": "₹ " + str(amount_1) + ".00",
                    "upi_total_sale_count": "1",
                    "upi_total_sale_amount": "₹ " + str(amount_1) + ".00",
                    "cash_sale_count": "1",
                    "cash_sale_amount": "₹ " + str(amount_2) + ".00",
                    "cash_total_sale_count": "1",
                    "cash_total_sale_amount": "₹ " + str(amount_2) + ".00"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                merchant_code = history_page.fetch_org_code_summary_page()
                logger.debug(f"merchant code from app summary page : {merchant_code}")
                shift_num = history_page.fetch_shift_num_summary_page()
                logger.debug(f"shift number from app summary page : {shift_num}")
                receipt_date = history_page.fetch_receipt_date_summary_page()
                logger.debug(f"receipt_date from app summary page : {receipt_date}")
                shift_start_date = history_page.fetch_receipt_shift_start_date_summary_page()
                logger.debug(f"shift_start_date from app summary page : {shift_start_date}")
                shift_end_time = history_page.fetch_receipt_shift_end_date_summary_page()
                logger.debug(f"shift_start_date from app summary page : {shift_end_time}")
                mid_receipt = history_page.fetch_receipt_mid_summary_page()
                logger.debug(f"mid_receipt from app summary page : {mid_receipt}")
                tid_receipt = history_page.fetch_receipt_tid_summary_page()
                logger.debug(f"tid_receipt from app summary page : {tid_receipt}")
                upi_pmt_mode_sale_count_app = history_page.fetch_receipt_upi_sale_count_summary_page()
                logger.debug(f"upi_pmt_mode_sale_count_app from app summary page : {upi_pmt_mode_sale_count_app}")
                upi_pmt_mode_sale_amount_app = history_page.fetch_receipt_upi_sale_amount_summary_page()
                logger.debug(f"upi_pmt_mode_sale_amount from app summary page : {upi_pmt_mode_sale_amount_app}")
                upi_pmt_mode_total_sale_count_app = history_page.fetch_receipt_upi_total_sale_count_summary_page()
                logger.debug(f"upi_pmt_mode_total_sale_count from app summary page : {upi_pmt_mode_total_sale_count_app}")
                upi_pmt_mode_total_sale_amount_app = history_page.fetch_receipt_upi_total_sale_amount_summary_page()
                logger.debug(f"upi_pmt_mode_total_sale_amount from app summary page : {upi_pmt_mode_total_sale_amount_app}")
                cash_pmt_mode_sale_count_app = history_page.fetch_receipt_cash_sale_count_summary_page()
                logger.debug(f"cash_pmt_mode_sale_count from app summary page : {cash_pmt_mode_sale_count_app}")
                cash_pmt_mode_sale_amount_app = history_page.fetch_receipt_cash_sale_amount_summary_page()
                logger.debug(f"cash_pmt_mode_sale_amount from app summary page : {cash_pmt_mode_sale_amount_app}")
                cash_pmt_mode_total_sale_count_app = history_page.fetch_receipt_cash_total_sale_count_summary_page()
                logger.debug(f"cash_pmt_mode_total_sale_count from app summary page : {cash_pmt_mode_total_sale_count_app}")
                cash_pmt_mode_total_sale_amount_app = history_page.fetch_receipt_cash_total_sale_amount_summary_page()
                logger.debug(f"cash_pmt_mode_total_sale_amount from app summary page : {cash_pmt_mode_total_sale_amount_app}")

                actual_app_values = {
                    "merchant_code": merchant_code,
                    "shift_num": shift_num,
                    "receipt_date": receipt_date,
                    "shift_created_time": shift_start_date,
                    "ended_shift_timed": shift_end_time,
                    "mid": mid_receipt,
                    "tid": tid_receipt,
                    "upi_sale_count": upi_pmt_mode_sale_count_app,
                    "upi_sale_amount": upi_pmt_mode_sale_amount_app,
                    "upi_total_sale_count": upi_pmt_mode_total_sale_count_app,
                    "upi_total_sale_amount": upi_pmt_mode_total_sale_amount_app,
                    "cash_sale_count": cash_pmt_mode_sale_count_app,
                    "cash_sale_amount": cash_pmt_mode_sale_amount_app,
                    "cash_total_sale_count": cash_pmt_mode_total_sale_count_app,
                    "cash_total_sale_amount": cash_pmt_mode_total_sale_amount_app
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

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