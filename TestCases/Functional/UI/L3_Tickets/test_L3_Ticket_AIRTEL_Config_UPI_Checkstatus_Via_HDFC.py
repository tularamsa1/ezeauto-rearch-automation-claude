import random
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_L3_5008_101_001():
    """
    Sub Feature Code: L3_5008_Airtel_Config_UPI_Success_Checkstatus_HDFC
    Sub Feature Description: Performing UPI Successful txn Via CheckStatus through app for HDFC pg for Airtel Merchant.
    TC naming code description: L3_5008: L3_Ticket_Id, 101: UPI, 001: TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code, mobile_number from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code and mobile_number from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Value of org_code from org_employee table is: {org_code}")
        usr_mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Value of mobile_number from org_employee table is: {usr_mobile_number}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'HDFC' and name = 'AIRTEL' and acc_label_id=(select id from label where " \
                f"name='postpaid' and org_code ='{org_code}');"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table is: {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table is: {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table is: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ------------------------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(201, 900)
            logger.info(f"generating random amount : {amount}")
            mobile_no = random.randint(7800500000, 9999999999)
            logger.info(f"generating random mobile number : {mobile_no}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            logger.info("Logging in the MPOSX application")
            login_page.perform_login(app_username, app_password)
            logger.info("Waiting for Home Page to load")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            # home_page.check_home_page_logo()
            logger.info(f"Clicking on start button")
            home_page.click_on_start_btn()
            payment_page = PaymentPage(app_driver)
            logger.info(f"Clicking on postpaid button")
            payment_page.click_on_post_paid_btn()
            logger.info(f"Clicking on bill collection - active button")
            payment_page.click_on_bill_coll_active_btn()
            logger.info(f"Enter mobile number and click on fetch details button")
            payment_page.enter_mobile_no_and_fetch_details(mobile_no)
            logger.info(f"Enter amount and click on checkout button")
            payment_page.enter_amount_and_checkout(amount)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Fetch order_id and click on proceed to home page")
            order_id = payment_page.fetch_order_id_from_success_page()
            logger.info(f"fetching order id : {order_id}")
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref='{str(order_id)}';"
            logger.debug(f"Query to fetch details from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from txn table: {txn_id}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from txn table, rrn : {rrn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table: {created_time}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table: {posting_date}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table: {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer name from txn table: {payer_name}")
            status_db = result["status"].values[0]
            logger.info(f"Fetching status from txn table: {status_db}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table: {auth_code}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
            amount_db = float(result["amount"].values[0])
            logger.info(f"Fetching amount from txn table: {amount_db}")
            state_db = result["state"].values[0]
            logger.info(f"Fetching state from txn table: {state_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
            bank_code_db = result["bank_code"].values[0]
            logger.info(f"Fetching bank code from txn table: {bank_code_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            txn_type_db = result["txn_type"].values[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].values[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].values[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from txn table: {rrn_db}")
            bank_name_db = result['bank_name'].values[0]
            logger.debug(f"Fetching bank_name from txn table: {bank_name_db}")
            error_msg_db = str(result['error_message'].values[0])
            logger.debug(f"Fetching error message from txn table: {error_msg_db}")
            user_mobile_db = result['user_mobile'].values[0]
            logger.debug(f"Fetching user mobile number from txn table: {user_mobile_db}")

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
        # -----------------------------------------Start of App Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                logger.info("Clicking on history button")
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("Selecting txn by filtering the search with txn id")
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                order_id_app = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {order_id_app}")
                customer_name_app = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer name from txn history for the txn : {order_id_app}")
                payer_name_app = transactions_history_page.fetch_payer_name_text()
                logger.info(f"Fetching payer name from txn history for the txn : {order_id_app}")
                txn_id_app = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn id from txn history for the txn :, {txn_id_app}")
                status_app = transactions_history_page.fetch_txn_status_text().replace('STATUS:', '')
                logger.info(f"Fetching status from txn history for the txn : {status_app}")
                settlement_status_app = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {settlement_status_app}")
                rrn_app = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {rrn_app}")
                auth_code_app = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {auth_code_app}")
                date_and_time_app = transactions_history_page.fetch_date_time_text()
                logger.info(f" Fetching date from txn history for the txn: {date_and_time_app}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "customer_name": customer_name_app,
                    "payer_name": payer_name_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "date": date_and_time_app,
                    "auth_code": auth_code
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": order_id,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response: {status_api}")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response: {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api response: {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response: {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response: {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response: {txn_type_api}")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response: {order_id_api}")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response: {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": rrn_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "bank_name": "HDFC Bank",
                    "error_msg": "None",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payer_name": payer_name,
                    "pmt_gateway": "HDFC",
                    "rrn": rrn,
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "user_mobile": usr_mobile_number
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status  from upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type from upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code from upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from upi_txn table : {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "bank_name": bank_name_db,
                    "error_msg": error_msg_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payer_name": payer_name,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rrn_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "user_mobile": user_mobile_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

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
                    "pmt_type": "UPI",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn)
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"Fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal
                }

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)