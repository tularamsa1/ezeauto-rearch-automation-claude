import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_txn_history_summary import TxnSummary
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, date_time_converter, \
    card_processor, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_L3_5150_409_001():
    """
    Sub Feature Code: L3_5150_Txn_Summary_PM_Cash_Card
    Sub Feature Description: Verify that the transaction summary data is as expected on the transaction summary screen for cash and card payments in new MPOS.
    TC naming code description: L3_5150: L3_Ticket_Id, 409: TransactionHistory, 001: TC001
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

        testsuite_teardown.revert_org_settings_default(org_code=org_code, portal_un=portal_username,
                                                       portal_pw=portal_password)

        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # --------------------------------------PreConditions(Completed)----------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(10, 1000)
            logger.debug(f"Amount used for card txn : {amount}")
            card_details = card_processor.get_card_details_from_excel("EMV_DEBIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="HDFC",
                                                              payment_gateway="HDFC"),
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "amount": str(amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success:
                txn_id = response['txnId']
                confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "ezetapDeviceData": confirm_data[
                                                                            "Ezetap Device Data"],
                                                                        "txnId": txn_id,
                                                                        })
                confirm_response = APIProcessor.send_request(api_details)
                confirm_success = confirm_response['success']
                logger.debug(f"Card txn passed status : {confirm_success}")
            else:
                logger.error("Card payment Failed")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            logger.debug(f"Started performing cash txn")
            cash_order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.wait_to_load_shift_management_block()
            shift = home_page.shift_title()
            logger.debug(f"Shift Management Title : {shift}")
            home_page.enter_amount_and_order_number(amount, cash_order_id)
            logger.debug(f"Entered amount for cash txn is : {amount}")
            logger.debug(f"Entered order_id for cash txn is : {cash_order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, cash_order_id)
            payment_page.click_on_Cash()
            payment_page.click_on_confirm()
            payment_page.click_on_proceed_homepage()

            query = f"select * from shift_detail where username='{app_username}' and shift_no='{shift[len(shift) - 1]}' and shift_status='IN_PROGRESS' order by created_time desc;"
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"result:{result}")
            logger.debug(f"Query : {query}")
            created_time_of_shift = result["created_time"].values[0]
            created_time_of_shift_db = date_time_converter.db_datetime(created_time_of_shift)
            logger.debug(f"created time of shift to DB format: {created_time_of_shift_db}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND process_code = '{shift}' AND
                                                payment_mode = 'CASH' AND created_time >= '{shift_start_time}';""".format(
                org_code=org_code, shift=shift, shift_start_time=created_time_of_shift_db)
            logger.debug(f"Query to fetch total amount of cash txn from database : {query}")
            cash_result = DBProcessor.getValueFromDB(query)
            total_cash_amount = cash_result['sum(amount)'].values[0]
            cash_result_int = total_cash_amount if total_cash_amount is not None else 0
            logger.debug(f"total_cash_amount : {cash_result_int}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND process_code = '{shift}' AND payment_mode = 'CARD' AND status='AUTHORIZED' AND created_time >= '{shift_start_time}';""".format(
                org_code=org_code, shift=shift, shift_start_time=created_time_of_shift_db)
            logger.debug(f"Query to fetch total amount of CARD txn from database : {query}")
            result_card = DBProcessor.getValueFromDB(query)
            total_amount_card = result_card['sum(amount)'].values[0]
            logger.debug(f"total_amount_card : {total_amount_card}")
            total_amount_card_1 = [0 if total_amount_card is None else total_amount_card]
            logger.debug(f"total_amount_card after if condition : {total_amount_card_1[0]}")

            total_amount = cash_result_int + total_amount_card_1[0]
            logger.debug(f"cumulative total amount of all the tnx : {total_amount}")

            query = """SELECT count(*) FROM txn WHERE org_code = '{org_code}'AND (settlement_status='SETTLED' or settlement_status='POSTED' or settlement_status='PENDING')
                        AND created_time >= '{shift_start_time}';""".format(org_code=org_code,
                                                                            shift_start_time=created_time_of_shift_db)
            logger.debug(f"Query to fetch total number of txn from database : {query}")
            result_sales_count = DBProcessor.getValueFromDB(query)
            total_sales = result_sales_count['count(*)'].values[0]
            logger.debug(f"total sales count : {total_sales}")

            amount_cash = str(cash_result_int).rstrip("0").rstrip(".")
            amount_card = str(total_amount_card_1[0]).rstrip("0").rstrip(".")

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
                    "sales_volume": str(total_amount).rstrip("0").rstrip("."),
                    "total_sales": str(total_sales),
                    "pmt_mode": "CASH",
                    "pmt_mode_2": "CARD",
                    "amt": amount_cash,
                    "amt_2": amount_card
                }

                logger.debug(f"expected values : {expected_app_values}")
                home_page.click_on_history()
                trans_summary = TxnSummary(app_driver)
                trans_summary.click_on_txn_summary()
                total_volume_amount = trans_summary.fetch_total_volume().split(" ")[0]
                logger.debug(f"total_volume_amount is {total_volume_amount}")
                total_sales_count = trans_summary.fetch_total_sales()
                logger.debug(f"total_sales_count is {total_sales_count} ")

                primary_amount_1, primary_payment_mode_1 = trans_summary.fetch_fourth_highest_payment_mode_and_amount()
                amount_2, payment_mode_2 = trans_summary.fetch_card_payment_mode_and_amount()

                actual_app_values = {
                    "sales_volume": str(total_volume_amount),
                    "total_sales": str(total_sales_count),
                    "pmt_mode": str(primary_payment_mode_1).strip(),
                    "pmt_mode_2": str(payment_mode_2).strip(),
                    "amt": primary_amount_1,
                    "amt_2": amount_2,
                }
                logger.debug(f"actual app values: {actual_app_values}")
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
