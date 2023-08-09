import sys
from time import sleep
import pytest
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.sa.App_CardPage import CardPage
from PageFactory.sa.App_PaymentPage import PaymentPage
from PageFactory.mpos.App_HomePage import HomePage
from PageFactory.mpos.App_LoginPage import LoginPage
from PageFactory.sa.App_TransHistoryPage import TransHistoryPage
from Utilities import Validator,ConfigReader, DBProcessor,ResourceAssigner,  date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_card():
    """
        Sub Feature Code: authorised txn, void an authorised txn, failed txn with error message
        Sub Feature Description: Verification of authorised txn, void an authorised txn and failed txn with error message
        TC naming code description:
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

        # testsuite_teardown.revert_payment_settings_default(org_code, 'AXIS', portal_username, portal_password, 'BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            device_serial = "D7373736700"
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = 455
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_for_card(amount, order_id, device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(app_driver)
            card_page.select_cardtype("ATOS_TLE_EMVCTLS_CREDIT_VISA")

            # ============ card txn based on specific amounts for diff failed scenarios ======================
            # error_code = card_page.fetch_error_code_text()
            # error_mssg = card_page.fetch_error_message_text()

            # print(error_code)
            # print(error_mssg)
            # card_page.click_on_ok_error_mssg()

            sleep(2)
            payment_page.click_on_proceed_homepage()

            query = "select * from txn where org_code ='" + str(
                org_code) + "' AND payment_mode = 'CARD' AND device_serial='"+device_serial+"' AND external_ref='"+order_id+"' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time = result['created_time'].values[0]
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {txn_created_time}")

            rrn = result['rr_number'].values[0]
            auth_code = result['auth_code'].values[0]
            batch_number = result['batch_number'].values[0]
            tid = result['tid'].values[0]
            mid = result['mid'].values[0]
            customer_name = result['customer_name'].values[0]

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
        # # -----------------------------------------Start of App Validation---------------------------------
        # if (ConfigReader.read_config("Validations", "app_validation")) == "True":
        #     logger.info(f"Started APP validation for the test case : {testcase_id}")
        #     date_and_time = date_time_converter.to_app_format(txn_created_time)
        #     try:
        #         expected_app_values = {
        #             "pmt_mode": "CARD",
        #             "pmt_status": "AUTHORIZED",
        #             "txn_amt": "{:.2f}".format(amount),
        #             "settle_status": "PENDING",
        #             "txn_id": txn_id,
        #             "pmt_msg": "PAYMENT SUCCESSFUL",
        #             "date": date_and_time,
        #             "rr_number": rrn,
        #             "auth_code": auth_code,
        #             "customer_name": customer_name,
        #             "batch_number": batch_number,
        #             "mid": mid,
        #             "tid": tid,
        #             "card_type_desc": "*3493 CTLS"
        #         }
        #         logger.debug(f"expectedAppValues: {expected_app_values}")
        #
        #         home_page.click_on_history()
        #         txn_history_page = TransHistoryPage(app_driver)
        #         txn_history_page.click_on_transaction_by_order_id(order_id)
        #         payment_status = txn_history_page.fetch_txn_status_text()
        #         payment_mode = txn_history_page.fetch_txn_type_text()
        #         app_txn_id = txn_history_page.fetch_txn_id_text()
        #         app_amount = txn_history_page.fetch_txn_amount_text()
        #         app_settlement_status = txn_history_page.fetch_settlement_status_text()
        #         app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
        #         app_date_and_time = txn_history_page.fetch_date_time_text()
        #         app_rrn = txn_history_page.fetch_RRN_text()
        #         app_auth_code = txn_history_page.fetch_auth_code_text()
        #         app_batch_no = txn_history_page.fetch_batch_number_text()
        #         app_customer_name = txn_history_page.fetch_customer_name_text()
        #         app_mid = txn_history_page.fetch_mid_text()
        #         app_tid = txn_history_page.fetch_tid_text()
        #         app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
        #
        #
        #         actual_app_values = {
        #             "pmt_mode": payment_mode,
        #             "pmt_status": payment_status.split(':')[1],
        #             "txn_amt": app_amount.split(' ')[1],
        #             "txn_id": app_txn_id,
        #             "settle_status": app_settlement_status,
        #             "pmt_msg": app_payment_msg,
        #             "date": app_date_and_time,
        #             "rr_number": app_rrn,
        #             "auth_code": app_auth_code,
        #             "customer_name": app_customer_name,
        #             "batch_number": app_batch_no,
        #             "mid": app_mid,
        #             "tid": app_tid,
        #             "card_type_desc": app_card_type_desc
        #         }
        #         logger.debug(f"actual_app_values: {actual_app_values}")
        #
        #         Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
        #     except Exception as e:
        #         Configuration.perform_app_val_exception(testcase_id, e)
        #     logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            date_and_time = date_time_converter.to_app_format(txn_created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": customer_name,
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*3493 CTLS"
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
                # ============== Void an authorized txn ====================
                # txn_history_page.click_on_void_card_txn()

                payment_status = txn_history_page.fetch_txn_status_text()
                payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_auth_code = txn_history_page.fetch_auth_code_text()
                app_batch_no = txn_history_page.fetch_batch_number_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_mid = txn_history_page.fetch_mid_text()
                app_tid = txn_history_page.fetch_tid_text()
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rr_number": app_rrn,
                    "auth_code": app_auth_code,
                    "customer_name": app_customer_name,
                    "batch_number": app_batch_no,
                    "mid": app_mid,
                    "tid": app_tid,
                    "card_type_desc": app_card_type_desc
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