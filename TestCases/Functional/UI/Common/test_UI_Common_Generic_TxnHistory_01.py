import random
import sys
from datetime import datetime
from datetime import date
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_summary import Trans_summary
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_400_409_001():
    """
    Sub Feature Code: UI_Sa_Generic_TxnHistory_Txn_Summary
    Sub Feature Description: Verify that the transaction summary data is as expected on the transaction summary screen.
    TC naming code description: 400: GenericActions, 409: TransactionHistory, 002: TC002
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
                                                           portal_pw=portal_password, payment_mode="UPI")
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
            home_page.check_home_page_logo()
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
            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND created_time LIKE '{today}%'AND 
                                                payment_mode = 'CASH';""".format(org_code=org_code, today=date.today())
            logger.debug(f"Query to fetch total amount of cash txn from database : {query}")
            cash_result = DBProcessor.getValueFromDB(query)
            total_cash_amount = cash_result['sum(amount)'].values[0]
            cash_result_int = int(total_cash_amount) if total_cash_amount is not None else 0
            logger.debug(f"total_cash_amount : {total_cash_amount}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'UPI' 
            AND settlement_status='SETTLED' AND created_time LIKE '{today}%';""".format(org_code=org_code,
                                                                                        today=date.today())
            logger.debug(f"Query to fetch total amount of upi txn from database : {query}")
            result_upi = DBProcessor.getValueFromDB(query)
            total_upi_amount = result_upi['sum(amount)'].values[0]
            upi_result_int = int(total_upi_amount) if total_upi_amount is not None else 0
            logger.debug(f"total_upi_amount : {total_upi_amount}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'BHARATQR' 
            AND settlement_status='SETTLED' AND created_time LIKE '{today}%';""".format(org_code=org_code,
                                                                                        today=date.today())
            logger.debug(f"Query to fetch total amount of Bqr txn from database : {query}")
            result_bqr = DBProcessor.getValueFromDB(query)
            total_bqr_amount = result_bqr['sum(amount)'].values[0]
            bqr_result_int = int(total_bqr_amount) if total_bqr_amount is not None else 0
            logger.debug(f"total_bqr_amount : {total_bqr_amount}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'CARD' 
                       AND settlement_status='SETTLED' AND created_time LIKE '{today}%';""".format(org_code=org_code,
                                                                                                   today=date.today())
            logger.debug(f"Query to fetch total amount of CARD txn from database : {query}")
            result_card = DBProcessor.getValueFromDB(query)
            total_amount_card = result_card['sum(amount)'].values[0]
            logger.debug(f"total_amount_card : {total_amount_card}")
            total_amount_card_1 = [0 if total_amount_card == None else total_amount_card]
            logger.debug(f"total_amount_card after if condition : {total_amount_card_1[0]}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'remotepay' 
                       AND settlement_status='SETTLED' AND created_time LIKE '{today}%';""".format(org_code=org_code,
                                                                                                   today=date.today())
            logger.debug(f"Query to fetch total amount of CNP txn from database : {query}")
            result_cnp = DBProcessor.getValueFromDB(query)
            total_amount_cnp = result_cnp['sum(amount)'].values[0]
            logger.debug(f"total_amount_cnp : {total_amount_cnp}")
            total_amount_cnp_1 = [0 if total_amount_cnp == None else total_amount_cnp]
            logger.debug(f"total_amount_cnp after if condition : {total_amount_cnp_1[0]}")

            query = """SELECT sum(amount) FROM txn WHERE org_code = '{org_code}'AND payment_mode = 'CHEQUE' 
                       AND settlement_status='POSTED' AND created_time LIKE '{today}%';""".format(org_code=org_code,
                                                                                                  today=date.today())
            logger.debug(f"Query to fetch total amount of cheque txn from database : {query}")
            result_cheque = DBProcessor.getValueFromDB(query)
            total_amount_cheque = result_cheque['sum(amount)'].values[0]
            logger.debug(f"total_amount_cheque : {result_cheque}")
            total_amount_cheque_1 = [0 if total_amount_cheque == None else total_amount_cheque]
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
            data = [
                {'id': 'CASH', 'amount': cash_result_int},
                {'id': 'UPI', 'amount': upi_result_int},
                {'id': 'BHARAT QR', 'amount': bqr_result_int},
                {'id': 'CARD', 'amount': total_amount_card_1[0]},
                {'id': 'PAY LINK', 'amount': total_amount_cnp_1[0]},
                {'id': 'CHEQUE', 'amount': total_amount_cheque_1[0]}
            ]
            sorted_data = sorted(data, key=lambda x: x['amount'], reverse=True)
            top_3 = sorted_data[:3]
            remaining = sorted_data[3:]
            cumulative_amount_others = sum(entry['amount'] for entry in remaining)
            top_3_ids = [entry['id'] for entry in sorted_data[:3]]
            top_payment_mode_1 = top_3_ids[0]
            top_payment_mode_2 = top_3_ids[1]
            top_payment_mode_3 = top_3_ids[2]
            top_amount_1 = top_3[0]['amount']
            top_amount_2 = top_3[1]['amount']
            top_amount_3 = top_3[2]['amount']
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
                    "payment_mode_1": str(top_payment_mode_1),
                    "payment_mode_2": str(top_payment_mode_2),
                    "payment_mode_3": str(top_payment_mode_3),
                    "other_mode": str(None) if cumulative_amount_others == 0 else "OTHERS",
                    "top_amount_1": str(top_amount_1).rstrip("0").rstrip("."),
                    "top_amount_2": str(top_amount_2).rstrip("0").rstrip("."),
                    "top_amount_3": str(top_amount_3).rstrip("0").rstrip("."),
                    "other_amount": str(0) if cumulative_amount_others == 0 else str(cumulative_amount_others)
                }
                logger.debug(f"expected values : {expected_app_values}")
                home_page.click_on_history()
                trans_summary = Trans_summary(app_driver)
                trans_summary.click_on_txn_summary()
                total_volume_amount = trans_summary.fetch_total_volume().split(" ")[1]
                total_sales_count = trans_summary.fetch_total_sales()
                payment_mode_and_amount_1 = trans_summary.fetch_first_highest_payment_mode_and_amount()
                primary_payment_mode_1, primary_amount_1 = trans_summary.extract_data(input_str=payment_mode_and_amount_1)
                payment_mode_and_amount_2 = trans_summary.fetch_second_highest_payment_mode_and_amount()
                payment_mode_2, amount_2 = trans_summary.extract_data(input_str=payment_mode_and_amount_2)
                payment_mode_and_amount_3 = trans_summary.fetch_third_highest_payment_mode_and_amount()
                payment_mode_3, amount_3 = trans_summary.extract_data(input_str=payment_mode_and_amount_3)
                try:
                    others_entity = trans_summary.fetch_other_payment_mode_and_amount()
                    others_mode, others_amount = trans_summary.extract_data(input_str=others_entity)
                except:
                    others_mode = None
                    others_amount = 0

                actual_app_values = {
                    "sales_volume": str(total_volume_amount).replace(",", "").rstrip("0").rstrip("."),
                    "total_sales": str(total_sales_count),
                    "payment_mode_1": str(primary_payment_mode_1).strip(),
                    "payment_mode_2": str(payment_mode_2).strip(),
                    "payment_mode_3": str(payment_mode_3).strip(),
                    "other_mode": str(others_mode).strip(),
                    "top_amount_1":primary_amount_1.replace(",", "").rstrip("0").rstrip("."),
                    "top_amount_2": amount_2.replace(",", "").rstrip("0").rstrip("."),
                    "top_amount_3": amount_3.replace(",", "").rstrip("0").rstrip("."),
                    "other_amount": others_amount.replace(",", "").rstrip("0").rstrip(".")
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
