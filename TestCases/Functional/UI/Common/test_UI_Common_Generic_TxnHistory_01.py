import random
import sys
from datetime import datetime
from datetime import date
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_filters_page import FiltersPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.sa.app_txn_history_summary import TxnSummary
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, date_time_converter, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_400_409_001():
    """
    Sub Feature Code: UI_Sa_Generic_TxnHistory_Txn_Summary
    Sub Feature Description: Verify that the transaction summary data is as expected on the transaction summary screen.
    TC naming code description: 400: GenericActions, 409: TransactionHistory, 001: TC001
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
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code="HDFC", portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode="BQRV4")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["appMaxRows"] = "3000"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False)
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
            # home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            logger.debug(f"Started performing cash txn")
            amount_cash = random.randint(1, 1000)
            cash_order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.wait_to_load_today_sales()
            home_page.enter_amount_and_order_number(amount_cash, cash_order_id)
            logger.debug(f"Entered amount for cash txn is : {amount_cash}")
            logger.debug(f"Entered order_id for cash txn is : {cash_order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount_cash, cash_order_id)
            payment_page.click_on_Cash()
            payment_page.click_on_confirm()
            payment_page.click_on_proceed_homepage()
            logger.debug(f"completed cash txn")

            logger.debug(f"started performing upi txn ")
            amount_upi = random.randint(201, 300)
            upi_order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.wait_to_load_today_sales()
            home_page.enter_amount_and_order_number(amount_upi, upi_order_id)
            logger.debug(f"Entered amount for upi txn is : {amount_upi}")
            logger.debug(f"Entered order_id for upi txn is : {upi_order_id}")
            payment_page.is_payment_page_displayed(amount_upi, upi_order_id)
            payment_page.click_on_Upi_paymentMode()
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            payment_page.click_on_proceed_homepage()
            logger.debug(f"completed upi txn")

            logger.debug(f"started performing BQRV4 txn")
            amount_bqr = random.randint(401, 500)
            bqr_order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.wait_to_load_today_sales()
            home_page.enter_amount_and_order_number(amount_bqr, bqr_order_id)
            logger.debug(f"Entered amount for Upi txn is : {amount_bqr}")
            logger.debug(f"Entered order_id for upi txn is : {bqr_order_id}")
            payment_page.is_payment_page_displayed(amount_bqr, bqr_order_id)
            payment_page.click_on_Bqr_paymentMode()
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            payment_page.click_on_proceed_homepage()
            logger.debug(f"completed BQR txn")

            # home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            logger.debug(f"started performing cheque txn")
            amount_cheque = random.randint(401, 430)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(amount_cheque, order_id)
            logger.debug(f"Entered amount is : {amount_cheque}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount_cheque, order_id)
            payment_page.click_on_cheque()
            logger.info("Selected payment mode is cheque")
            payment_page.fill_cheque_number(123456)
            payment_page.fill_bank_name("Allahabad Bank")
            x, y = payment_page.get_relative_coordinate_for_bank()
            payment_page.perform_click_to_bank(x, y)
            today_date = datetime.today().date().strftime("%d %B %Y")
            logger.debug(f"Generating today's date: {today_date}")
            payment_page.click_on_date(today_date)
            payment_page.fill_ifsc_code("ALLA0210329")
            x1, y1 = payment_page.get_relative_coordinate_for_ifsc_code()
            payment_page.perform_touch_action_on_cheque_home_page(x1, y1)
            payment_page.click_on_cheque_submit()
            payment_page.click_on_proceed_homepage()
            logger.debug(f"completed cheque txn")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND created_time LIKE '{today}%'AND
                                                payment_mode = 'CASH';""".format(org_code=org_code, today=date.today())
            logger.debug(f"Query to fetch total amount of cash txn from database : {query}")
            cash_result = DBProcessor.getValueFromDB(query)
            total_cash_amount = cash_result['sum(amount)'].values[0]
            cash_result_int = int(total_cash_amount) if total_cash_amount is not None else 0
            logger.debug(f"total_cash_amount : {cash_result_int}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'UPI'
            AND settlement_status='SETTLED' AND status='AUTHORIZED' AND created_time LIKE '{today}%';""".format(
                org_code=org_code,
                today=date.today())
            logger.debug(f"Query to fetch total amount of upi txn from database : {query}")
            result_upi = DBProcessor.getValueFromDB(query)
            total_upi_amount = result_upi['sum(amount)'].values[0]
            upi_result_int = int(total_upi_amount) if total_upi_amount is not None else 0
            logger.debug(f"total_upi_amount is: {upi_result_int}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'BHARATQR'
            AND settlement_status='SETTLED' AND status='AUTHORIZED' AND created_time LIKE '{today}%';""".format(
                org_code=org_code,
                today=date.today())
            logger.debug(f"Query to fetch total amount of Bqr txn from database : {query}")
            result_bqr = DBProcessor.getValueFromDB(query)
            total_bqr_amount = result_bqr['sum(amount)'].values[0]
            bqr_result_int = int(total_bqr_amount) if total_bqr_amount is not None else 0
            logger.debug(f"total_bqr_amount is: {bqr_result_int}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'CARD'
                       AND settlement_status='SETTLED' AND status='AUTHORIZED' AND created_time LIKE '{today}%';""".format(
                org_code=org_code,
                today=date.today())
            logger.debug(f"Query to fetch total amount of CARD txn from database : {query}")
            result_card = DBProcessor.getValueFromDB(query)
            total_amount_card = result_card['sum(amount)'].values[0]
            logger.debug(f"total_amount_card : {total_amount_card}")
            total_amount_card_1 = [0 if total_amount_card is None else total_amount_card]
            logger.debug(f"total_amount_card after if condition : {total_amount_card_1[0]}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'remotepay'
                       AND settlement_status='SETTLED' AND status='AUTHORIZED' AND created_time LIKE '{today}%';""".format(
                org_code=org_code,
                today=date.today())
            logger.debug(f"Query to fetch total amount of CNP txn from database : {query}")
            result_cnp = DBProcessor.getValueFromDB(query)
            total_amount_cnp = result_cnp['sum(amount)'].values[0]
            logger.debug(f"total_amount_cnp : {total_amount_cnp}")
            total_amount_cnp_1 = [0 if total_amount_cnp is None else total_amount_cnp]
            logger.debug(f"total_amount_cnp after if condition : {total_amount_cnp_1[0]}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'CHEQUE'
                       AND settlement_status='POSTED' AND status='AUTHORIZED' AND created_time LIKE '{today}%';""".format(
                org_code=org_code,
                today=date.today())
            logger.debug(f"Query to fetch total amount of cheque txn from database : {query}")
            result_cheque = DBProcessor.getValueFromDB(query)
            total_amount_cheque = result_cheque['sum(amount)'].values[0]
            logger.debug(f"total_amount_cheque : {result_cheque}")
            total_amount_cheque_1 = [0 if total_amount_cheque is None else total_amount_cheque]
            logger.debug(f"total_amount_cheque after if condition : {total_amount_cheque_1[0]}")

            total_amount = total_cash_amount + total_upi_amount + total_bqr_amount + total_amount_card_1[0] \
                           + total_amount_cnp_1[0] + total_amount_cheque_1[0]
            logger.debug(f"cumulative total amount of all the tnx : {total_amount}")

            query = """SELECT count(*) FROM txn WHERE org_code = '{org_code}'AND (settlement_status='SETTLED' or settlement_status='POSTED')
                        AND created_time LIKE '{today}%';""".format(org_code=org_code, today=date.today())
            logger.debug(f"Query to fetch total number of tnx txn from database : {query}")
            result_sales_count = DBProcessor.getValueFromDB(query)
            total_sales = result_sales_count['count(*)'].values[0]
            logger.debug(f"total sales count : {total_sales}")
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
                    "sales_volume": str(total_amount).rstrip("0").rstrip("."),
                    "total_sales": str(total_sales),
                    "pmt_mode": "CHEQUE",
                    "pmt_mode_2": "CASH",
                    "pmt_mode_3": "UPI",
                    "pmt_mode_4": "BHARATQR",
                    "pmt_mode_5": "None" if total_amount_cnp_1 == [0] else "CNP",
                    "pmt_mode_6": "None" if total_amount_card_1 == [0] else "CARD",
                    "amt": str(total_amount_cheque_1[0]).rstrip("0").rstrip("."),
                    "amt_2": str(total_cash_amount).rstrip("0").rstrip("."),
                    "amt_3": str(upi_result_int).rstrip("0").rstrip("."),
                    "amt_4":  str(bqr_result_int).rstrip("0").rstrip("."),
                    "amt_5": "0" if total_amount_cnp_1 == [0] else str(total_amount_cnp_1[0]).rstrip("0").rstrip("."),
                    "amt_6": "0" if total_amount_card_1 == [0] else str(total_amount_card_1[0]).rstrip("0").rstrip(".")
                }
                logger.debug(f"expected values : {expected_app_values}")
                home_page.click_on_history()
                trans_summary = TxnSummary(app_driver)
                trans_summary.click_on_txn_summary()
                total_volume_amount = trans_summary.fetch_total_volume()
                logger.debug(f"total_volume_amount is {total_volume_amount}")
                total_sales_count = trans_summary.fetch_total_sales()
                logger.debug(f"total_sales_count is {total_sales_count} ")
                bqr_amt, brq_pmt = trans_summary.fetch_second_highest_payment_mode_and_amount()
                logger.debug(f"txn_amt_1 and pmt_amt_1 for BHARATQR is {bqr_amt}, {brq_pmt}")
                cash_amt, cash_pmt = trans_summary.fetch_fourth_highest_payment_mode_and_amount()
                logger.debug(f"txn_amt_2 and pmt_amt_2  for CASH is {cash_amt}, {cash_pmt}")
                cheque_amt, cheque_pmt = trans_summary.fetch_third_highest_payment_mode_and_amount()
                logger.debug(f"txn_amt_2 and pmt_amt_2  for CHEQUE is {cheque_amt}, {cheque_pmt}")
                upi_amt, upi_pmt = trans_summary.fetch_first_highest_payment_mode_and_amount()
                logger.debug(f"txn_amt and pmt_mode for UPI is {upi_amt}, {upi_pmt}")
                try:
                    cnp_amt, cnp_pmt = trans_summary.fetch_cnp_payment_mode_and_amount()
                    logger.debug(f"txn_amt and pmt_mode for CNP is {cnp_amt}, {cnp_pmt}")
                except:
                    cnp_pmt = "None"
                    cnp_amt = "0"
                try:
                    card_amt, card_pmt = trans_summary.fetch_card_payment_mode_and_amount()
                    logger.debug(f"txn_amt and pmt_mode for CARD is {card_amt}, {card_pmt}")
                except:
                    card_pmt = "None"
                    card_amt = "0"

                actual_app_values = {
                    "sales_volume": total_volume_amount,
                    "total_sales": total_sales_count,
                    "pmt_mode": cheque_pmt,
                    "pmt_mode_2": cash_pmt,
                    "pmt_mode_3": upi_pmt,
                    "pmt_mode_4": brq_pmt,
                    "pmt_mode_5": cnp_pmt,
                    "pmt_mode_6": card_pmt,
                    "amt": cheque_amt,
                    "amt_2": cash_amt,
                    "amt_3": upi_amt,
                    "amt_4": bqr_amt,
                    "amt_5": cnp_amt,
                    "amt_6": card_amt
                }
                logger.debug(f"actual app values: {actual_app_values}")
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
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_400_409_002():
    """
    Sub Feature Code: UI_Sa_Generic Actions_TxnHistory_Filters
    Sub Feature Description: Verify the transaction Filters are working on the Transaction History screen.
    TC naming code description: 400: Generic Actions, 409: Transaction History, 002: TC002
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
        testsuite_teardown.revert_payment_settings_default(org_code, bank_code="HDFC", portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode="BQRV4")
        testsuite_teardown.revert_org_settings_default(org_code, portal_username, portal_password)
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)
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
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            logger.debug(f"Started performing cash txn")
            amount_cash = random.randint(1, 100)
            cash_order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.wait_to_load_today_sales()
            home_page.enter_amount_and_order_number(amount_cash, cash_order_id)
            logger.debug(f"Entered amount for cash txn is : {amount_cash}")
            logger.debug(f"Entered order_id for cash txn is : {cash_order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount_cash, cash_order_id)
            payment_page.click_on_Cash()
            payment_page.click_on_confirm()
            payment_page.click_on_proceed_homepage()
            home_page.navigate_to_home()
            logger.debug(f"completed cash txn")
            logger.debug(f"started performing UPI txn ")
            home_page.wait_to_load_today_sales()
            amount_upi = random.randint(201, 300)
            upi_order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(amount_upi, upi_order_id)
            logger.debug(f"Entered amount for upi txn is : {amount_upi}")
            logger.debug(f"Entered order_id for upi txn is : {upi_order_id}")
            payment_page.is_payment_page_displayed(amount_upi, upi_order_id)
            payment_page.click_on_Upi_paymentMode()
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            payment_page.click_on_proceed_homepage()
            home_page.navigate_to_home()
            logger.debug(f"completed upi txn")
            home_page.wait_to_load_today_sales()
            logger.debug(f"started performing BQRV4 txn")
            amount_bqr = random.randint(401, 500)
            bqr_order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(amount_bqr, bqr_order_id)
            logger.debug(f"Entered amount for BQRV4 txn is : {amount_bqr}")
            logger.debug(f"Entered order_id for BQRV4 txn is : {bqr_order_id}")
            payment_page.is_payment_page_displayed(amount_bqr, bqr_order_id)
            payment_page.click_on_Bqr_paymentMode()
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            payment_page.click_on_proceed_homepage()
            logger.debug(f"completed BQRV4 txn")
            home_page.navigate_to_home()
            home_page.click_on_history()
            transactions_history_page = TransHistoryPage(app_driver)
            logger.debug(f"performing filter on the txn history")
            transactions_history_page.click_filter()
            filter_page = FiltersPage(app_driver)
            filter_page.click_on_payment_method_cash()
            filter_page.click_on_txn_status_success()
            filter_page.click_on_apply_filter()
            logger.debug(f"Applied filter for cash txn")
            query = "select * from txn where org_code='" + org_code + "' and " \
                                                                      "external_ref='" + cash_order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of cash txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Response received to fetch cash txn details is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching tnx_id from the txn table : tnx_id : {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : created_time : {created_time}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code : {org_code_txn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code : {auth_code}")
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
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "Cash Payment",
                    "pmt_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "txn_id": txn_id,
                    "order_id": cash_order_id,
                    "txn_amt": f"{amount_cash}.00",
                    "date": date_and_time
                }
                logger.debug(f"Expected App Values : {expected_app_values} ")

                filter_page.click_on_first_txn_after_filtration()
                payment_status = transactions_history_page.fetch_txn_status_text().split(':')
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = transactions_history_page.fetch_txn_amount_text().split(" ")
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status[1],
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "txn_amt": app_amount[1],
                    "date": app_date_and_time
                }
                logger.debug(f"Actual App Values : {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount_cash,
                    "pmt_mode": "CASH",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "org_code": org_code_txn,
                    "date": date,
                    "order_id": cash_order_id
                }
                logger.debug(f"Expected Api Values : {expected_api_values}")
                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                org_code_api = response["orgCode"]
                date_api = response["createdTime"]
                order_id_api = response["orderNumber"]

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "order_id": order_id_api
                }
                logger.debug(f"Actual Api Values : {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CASH",
                    "txn_amt": amount_cash,
                    "settle_status": "SETTLED",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                status_db = result["status"].values[0]
                payment_mode_db = result["payment_mode"].values[0]
                amount_db = int(result["amount"].values[0])
                state_db = result["state"].iloc[0]
                settlement_status_db = result["settlement_status"].values[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CASH",
                    "txn_amt": f"{amount_cash}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, cash_order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.info(f"fetched date time from portal {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type}")
                status = transaction_details[0]['Status']
                logger.info(f"fetched status {status}")
                username = transaction_details[0]['Username']
                logger.info(f"fetched username from portal {username}")
                portal_auth_code = transaction_details[0]['Auth Code']
                logger.info(f"fetched auth_code from portal {auth_code}")
                portal_rrn = transaction_details[0]['RR Number']
                logger.info(f"fetched rrn from portal {portal_rrn}")
                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": status,
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": portal_auth_code,
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {'PAID BY:': 'CASH', 'merchant_ref_no': 'Ref # ' + str(cash_order_id),
                                   'BASE AMOUNT:': "Rs." + str(amount_cash) + ".00", 'date': txn_date,
                                   'time': txn_time,
                                   }
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
