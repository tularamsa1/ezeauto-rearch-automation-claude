import random
import string
import sys
import time
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, \
    APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.appVal
def test_common_prod_001():
    """
    Sub Feature Code: UI_common_P2P_CASH
    Sub Feature Description: Performing a cash txn using P2P to verify the crate database from the txn history and the commx service for P2P.
    TC naming code description: prod: P2P, 001: TC 001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        app_username = "1234554297"
        app_password = "S123456"

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, commx_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id, "true")
            login_page = LoginPage(app_driver)
            login_page.prod_app_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"Logged in to the app")
            logger.info(f"Loaded home page")

            device_serial = GlobalVariables.str_device_id

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification")
            try:
                actual_notification = home_page.check_p2p_notification_prod()
                app_driver.back()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.info(f"P2P notification message on device is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device. Actual notification: {actual_notification}")

            # Start API for Cash
            amount = random.randint(10, 20)
            logger.info(f"Generated amount: {amount}")
            ext_ref_number_bqr = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Generated external reference number of cash:  {ext_ref_number_bqr}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "appKey": "570dfc9f-b9a4-4d9a-8997-48d88d722f84",
                "amount": str(amount),
                "externalRefNumber": ext_ref_number_bqr,
                "pushTo": push_to
            })
            resp_start_bqr = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API for BQR is : {resp_start_bqr}")
            success_status = resp_start_bqr['success']
            logger.debug(f"success status : {success_status}")

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_Cash()
            logger.info("Selected payment mode is cash")
            payment_page.click_on_confirm_prod()
            payment_page.click_on_proceed_homepage_prod()
            time.sleep(5)

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
                    "pmt_mode": "Cash Payment",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "order_id"'': ext_ref_number_bqr,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED"
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_first_amount_field_prod()
                payment_status = txn_history_page.fetch_txn_status_text_prod()
                logger.info(f"Fetching status from txn history for the txn : {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text_prod()
                logger.info(f"Fetching payment mode from txn history for the txn : {payment_mode}")
                app_order_id = txn_history_page.fetch_order_id_text_prod()
                logger.info(f"Fetching order id from txn history for the txn : {app_order_id}")
                app_amount = txn_history_page.fetch_txn_amount_text_prod()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text_prod()
                logger.info(f"Fetching txn status msg from txn history for the txn : {app_payment_msg}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settle status msg from txn history for the txn : {app_settle_status}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "order_id"'': app_order_id,
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settle_status
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "status_success": True,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                                     "status_success": success_status,
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.appVal
def test_common_prod_002():
    """
    Sub Feature Code: UI_Common_Card_Sale_CTLS
    Sub Feature Description:  Performing CTLS card txn
    TC naming code description:  002: CARD_UI, 002: TC003
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_username = "1234554297"
        app_password = "S123456"

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.prod_app_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = 11.11
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.prod_enter_amount_and_order_number_for_card(amt=amount, order_number=order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            time.sleep(3)
            payment_page.click_on_card_payment_mode_prod()
            logger.info("Selected payment mode is Card")
            time.sleep(2)
            payment_page.click_on_proceed_homepage_prod()

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
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "PENDING",
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "order_id": order_id,
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history_prod()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_first_amount_field_prod()
                payment_status = txn_history_page.fetch_txn_status_text_prod()
                logger.info(f"Fetching status from txn history for the txn : {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text_prod()
                logger.info(f"Fetching payment mode from txn history for the txn : {payment_mode}")
                app_order_id = txn_history_page.fetch_order_id_text_prod()
                logger.info(f"Fetching order id from txn history for the txn : {app_order_id}")
                app_amount = txn_history_page.fetch_txn_amount_text_prod()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text_prod()
                logger.info(f"Fetching txn status msg from txn history for the txn : {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settle status msg from txn history for the txn : {app_settlement_status}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "order_id": app_order_id
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
@pytest.mark.apiVal
@pytest.mark.appVal
def test_common_prod_003():
    """
    Sub Feature Code: UI_Common_Card_Sale_CTLS
    Sub Feature Description:  Performing CTLS  void card txn
    TC naming code description:  003: CARD_UI, 003: TC003
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_username = "1234554297"
        app_password = "S123456"

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.prod_app_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = 11.11
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.prod_enter_amount_and_order_number_for_card(amt=amount, order_number=order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            time.sleep(3)
            payment_page.click_on_card_payment_mode_prod()
            logger.info("Selected payment mode is Card")
            time.sleep(2)
            payment_page.click_on_proceed_homepage_prod()

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
                    "pmt_mode": "CARD",
                    "pmt_status": "VOIDED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "order_id": order_id,
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history_prod()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_first_amount_field_prod()
                txn_history_page.click_on_void_card_txn_prod()
                payment_status = txn_history_page.fetch_txn_status_text_prod()
                logger.info(f"Fetching status from txn history for the txn : {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text_prod()
                logger.info(f"Fetching payment mode from txn history for the txn : {payment_mode}")
                app_order_id = txn_history_page.fetch_order_id_text_prod()
                logger.info(f"Fetching order id from txn history for the txn : {app_order_id}")
                app_amount = txn_history_page.fetch_txn_amount_text_prod()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text_prod()
                logger.info(f"Fetching txn status msg from txn history for the txn : {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settle status msg from txn history for the txn : {app_settlement_status}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "order_id": app_order_id
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