import random
import sys
import time
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_LoginPage import LoginPage
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader,ResourceAssigner, DBProcessor
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_101_327():
    """
        Sub Feature Code: UI_Common_Mpos_Refund_From_POS_UPI_Confirm_Pos_Refund_Feature_Disabled
        Sub Feature Description: Verify the Refund From POS feature is disabled for the user
        TC naming code description: 100: Payment Method, 101: UPI, 327: TC327
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # First fetching the roles for the users
        query = f"select roles from org_employee  where org_code='{org_code}';"
        logger.debug(f"Query to fetch roles value from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        roles = result['roles'].values[0]
        logger.debug(f"Fetching roles value from org_employee table : {roles}")

        # Updating the role to agent - [Note: Agent role should be enabled for user to perform the txn]
        query = f"update org_employee set roles='ROLE_CLAGENT' where org_code='{org_code}'"
        logger.debug(f"Updating the role of user to 'ROLE_CLAGENT' in org_employee table : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Result of the user is updated to 'ROLE_CLAGENT' in org_employee table : {result}")

        refresh_db()
        logger.debug(f"After updating the role of user to 'ROLE_CLAGENT' refreshing the DB")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result to fetch data from upi_merchant_config table : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            amount = random.randint(300, 399)
            logger.debug(f"Randomly generated amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Randomly generated order_id is : {order_id}")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount and order_id is : {amount}, {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            logger.info("Clicked on back button")
            payment_page.click_on_transaction_cancel_yes()
            payment_page.click_on_proceed_homepage()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result obatined for txn table is : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table : {txn_id} ")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_transaction_by_order_id(order_id=order_id)
            logger.debug(f"Clicking on refund button on app side")

            try:
                payment_page.is_refund_txn_btn_visible()
                logger.debug(f"Refund button is invisible")
                refund_button_visible = "Refund button is invisible"
            except Exception as e:
                logger.debug(f"Refund button is still visible")
                refund_button_visible = "Refund button is visible"
                logger.error(f"Refund button is still visible due to : {e}")

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
                    "refund_button": "Refund button is invisible"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "refund_button": refund_button_visible
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        try:
            query = f"update org_employee set roles='ROLE_POS_REFUND,ROLE_CLAGENT' where org_code='{org_code}'"  # ROLE_POS_REFUND,ROLE_CLAGENT
            logger.debug(f"Updating back the role of user to 'ROLE_POS_REFUND,ROLE_CLAGENT' in org_employee table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Result of the user after updating back to 'ROLE_POS_REFUND,ROLE_CLAGENT' in org_employee table : {result}")

            refresh_db()
            logger.debug(f"After updating the role of user to 'ROLE_POS_REFUND,ROLE_CLAGENT' refreshing the DB")
        except Exception as e:
            logger.exception(f"Query updation failed due to expection : {e}")
        Configuration.executeFinallyBlock(testcase_id)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_101_328():
    """
        Sub Feature Code: UI_Common_Mpos_Refund_From_POS_Initiate_Refund_For_Fully_Refunded
        Sub Feature Description: Verify the user cannot initiate a refund for fully refunded transactions
        TC naming code description: 100: Payment Method, 101: UPI, 328: TC328
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from upi_merchant_config table : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id value from upi_merchant_config table : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid value from upi_merchant_config table : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid value from upi_merchant_config table : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            amount = random.randint(300, 399)
            logger.debug(f"Randomly generated amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Randomly generated order_id is : {order_id}")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount and order_id is : {amount}, {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            logger.info("Clicked on back button")
            payment_page.click_on_transaction_cancel_yes()
            payment_page.click_on_proceed_homepage()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table is : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id value from txn table : {txn_id} ")

            home_page.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
            logger.debug(f"Clicking on refund button on app side")
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side")
            payment_page.click_on_refund_full_amt()
            logger.debug(f"Clicked on refund full amount")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button and refunded full amount")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm the refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button")
            time.sleep(5)
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button again")
            home_page.click_on_history()
            logger.debug(f"Clicked on txn history back button to filter the third refund amount")
            txn_history_page.re_login_to_app(username=app_username, password=app_password)
            txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
            logger.debug(f"Re-filtering based on txn_id")
            try:
                payment_page.is_refund_txn_btn_visible()
                logger.debug(f"Refund button is invisible")
                refund_button_visible = "Refund button is invisible"
            except Exception as e:
                logger.debug(f"Refund button is still visible")
                refund_button_visible = "Refund button is visible"
                logger.error(f"Refund button is still visible due to : {e}")

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
                    "refund_button": "Refund button is invisible"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "refund_button": refund_button_visible
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