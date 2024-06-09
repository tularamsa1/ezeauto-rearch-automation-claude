import sys
import random
import pytest
from datetime import datetime
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities.execution_log_processor import EzeAutoLogger
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, receipt_validator, date_time_converter

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_343():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_UPI_Partial_Refund_Via_API_AXIS_DIRECT
    Sub Feature Description: TID Dep - Verification of a BQRV4 UPI txn when Partial refund is performed via api for AXIS_DIRECT
    TC naming code description: 100: Payment Method, 102: BQRV4, 343: TC343
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code="AXIS_DIRECT", portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code ='AXIS' and payment_gateway='AXIS';"
        logger.info(f"Query to fetch data for updating status as active in terminal_dependency_config table : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : {merchant_pan}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
        logger.info(f"Query to fetch data for updating status as active in upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the upi_merchant_config table : {tid}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch data from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of terminal_info table : {result}")
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(201, 300)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for UPI Stop Payment : {response}")

            refund_amount = amount - 100
            logger.debug(f"Refund amount is : {refund_amount}")

            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username,
                "password": app_password,
                "amount": refund_amount,
                "originalTransactionId": str(txn_id)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")
            refund_txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the refund api response : {refund_txn_id}")

            query = "select * from txn where id = '" + str(refund_txn_id) + "';"
            logger.debug(f"Query to fetch data from txn table after refund is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table after refund is : {result}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table after refund is : {refund_auth_code}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table after refund is : {refund_txn_type}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table after refund is : {refund_rrn}")
            customer_name_refund = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table after refund is : {customer_name_refund}")
            payer_name_refund = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table after refund is : {payer_name_refund}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table after refund is : {refund_created_time}")
            status_db_refunded = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table after refund is : {status_db_refunded}")
            payment_mode_db_refunded = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table after refund is : {payment_mode_db_refunded}")
            amount_db_refunded = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table after refund is : {amount_db_refunded}")
            state_db_refunded = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table after refund is : {state_db_refunded}")
            payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table after refund is : {payment_gateway_db_refunded}")
            acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table after refund is : {acquirer_code_db_refunded}")
            bank_code_db_refunded = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table after refund is : {bank_code_db_refunded}")
            settlement_status_db_refunded = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table after refund is : {settlement_status_db_refunded}")
            tid_db_refunded = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table after refund is : {tid_db_refunded}")
            mid_db_refunded = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table after refund is : {mid_db_refunded}")
            order_id_db_original = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table after refund is : {order_id_db_original}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_date_time}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table : {txn_type}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Value of org_code obtained from txn table : {org_code_txn}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table : {amount_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table : {status_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {state_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table : {payment_mode_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table : {bank_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table : {payment_gateway_db}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")
            order_id_db_refunded = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table : {order_id_db_refunded}")

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
                date_and_time = date_time_converter.to_app_format(created_date_time)
                refund_date_and_time = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": refund_txn_id,
                    "txn_amt": str(amount) + ".00",
                    "txn_amt_2": "{:.2f}".format(refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name_refund,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name_refund,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "rrn": str(rrn),
                    "date": date_and_time,
                    "date_2": refund_date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching Transaction status from txn history for the txn : {refund_txn_id}, {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching Transaction payment mode from txn history for the txn : {refund_txn_id}, {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching Transaction id from txn history for the txn : {refund_txn_id}, {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.info(f"Fetching Transaction amount from txn history for the txn : {refund_txn_id}, {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {refund_txn_id}, {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {refund_txn_id}, {payment_msg_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {refund_txn_id}, {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from txn history for the txn : {txn_id}, {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from txn history for the txn : {txn_id}, {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from txn history for the txn : {txn_id}, {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from txn history for the txn : {txn_id}, {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status  from txn history for the txn : {txn_id}, {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching payment message from txn history for the txn : {txn_id}, {payment_msg_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from txn history for the txn : {txn_id}, {app_order_id}")
                app_refund_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.debug(f"Fetching refund date and time from txn history for the txn : {txn_id}, {app_refund_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": app_order_id,
                    "order_id_2": app_order_id_refunded,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_refunded
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
                date = date_time_converter.db_datetime(created_date_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": amount,
                    "txn_amt_2": refund_amount,
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "rrn": str(rrn),
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "AXIS",
                    "txn_type_2": refund_txn_type,
                    "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "date": date,
                    "date_2": refund_date,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api_original = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api_original}")
                amount_api_original = float(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api_original}")
                payment_mode_api_original = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api_original}")
                state_api_original = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api_original}")
                settlement_status_api_original = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api_original}")
                rrn_api_original = response_1["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api_original}")
                issuer_code_api_original = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api_original}")
                acquirer_code_api_original = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api_original}")
                org_code_api_original = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api_original}")
                mid_api_original = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api_original}")
                tid_api_original = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api_original}")
                txn_type_api_original = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api_original}")
                date_api_original = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api_original}")
                device_serial_api_original = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api_original}")
                order_id_api_original = response_1["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from txnlist api is : {order_id_api_original}")

                response_2 = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn api is : {response_2}")
                status_api_refunded = response_2["status"]
                logger.debug(f"Value of status obtained from refund txnlist api is : {status_api_refunded}")
                amount_api_refunded = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from refund txnlist api is : {amount_api_refunded}")
                payment_mode_api_refunded = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from refund txnlist api is : {payment_mode_api_refunded}")
                state_api_refunded = response_2["states"][0]
                logger.debug(f"Value of states obtained from refund txnlist api is : {state_api_refunded}")
                settlement_status_api_refunded = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from refund txnlist api is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from refund txnlist api is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from refund txnlist api is : {org_code_api_refunded}")
                mid_api_refunded = response_2["mid"]
                logger.debug(f"Value of mid obtained from refund txnlist api is : {mid_api_refunded}")
                tid_api_refunded = response_2["tid"]
                logger.debug(f"Value of tid obtained from refund txnlist api is : {tid_api_refunded}")
                txn_type_api_refunded = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from refund txnlist api is : {txn_type_api_refunded}")
                date_api_refunded = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from refund txnlist api is : {date_api_refunded}")
                order_id_api_refunded = response_2["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from refund txnlist api is : {order_id_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt": amount_api_original,
                    "txn_amt_2": amount_api_refunded,
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn": str(rrn_api_original),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original, "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "device_serial": device_serial_api_original
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
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": refund_amount,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "AXIS",
                    "acquirer_code_2": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "AXIS",
                    "pmt_gateway_2": "AXIS",
                    "upi_txn_type": "PAY_BQR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "HDFC",
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on refund txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table based on refund txn_id : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table based on refund txn_id : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table based on refund txn_id : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table based on refund txn_id : {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table based on refund txn_id : {upi_mc_id_db_refunded}")

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table based on txn_id : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table based on txn_id : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table based on txn_id : {upi_txn_type_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table based on txn_id : {upi_mc_id_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table based on txn_id : {upi_bank_code_db_original}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table : {bqr_org_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db,
                    "txn_amt_2": amount_db_refunded,
                    "order_id": order_id_db_original,
                    "order_id_2": order_id_db_refunded,
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id": upi_mc_id_db_original,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "device_serial": str(device_serial_db)
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:.2f}".format(refund_amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_date_time)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(refund_created_time)

                expected_chargeslip_values_original = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                                       'RRN': str(rrn),
                                                       'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                                                       'time': txn_time
                                                       }

                expected_chargeslip_values_refunded = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                                       'BASE AMOUNT:': "Rs." + str(refund_amount) + ".00",
                                                       'time': txn_time_2,  'date': txn_date_2
                                                       }

                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(txn_id, {"username": app_username,
                                                                                                     "password": app_password},
                                                                                            expected_chargeslip_values_original)

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(refund_txn_id, {"username": app_username,
                                                                                                            "password": app_password},
                                                                                            expected_chargeslip_values_refunded)

                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_344():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_UPI_Two_Times_Partial_Refund_Via_API_Amount_Greater_Than_Original_Amount_AXIS_DIRECT
    Sub Feature Description: TID Dep - Verification of a BQRV4 UPI partial refund via api when partial refund amount is greater than original amount for AXIS_DIRECT
    TC naming code description: 100: Payment Method, 102: BQRV4, 344: TC344
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code="AXIS_DIRECT", portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code ='AXIS' and payment_gateway='AXIS';"
        logger.info(f"Query to fetch data for updating status as active in terminal_dependency_config table : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : {merchant_pan}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
        logger.info(f"Query to fetch data for updating status as active in upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the upi_merchant_config table : {tid}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch data from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of terminal_info table : {result}")
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 250
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for UPI Stop Payment : {response}")

            refunded_amount =  150
            logger.debug(f"Refund amount is : {refunded_amount}")

            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username,
                "password": app_password,
                "amount": refunded_amount,
                "originalTransactionId": str(txn_id)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for payment refund is: {response}")

            greater_refund_amount = 101
            logger.debug(f"Greater refund amount is : {greater_refund_amount}")

            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username,
                "password": app_password,
                "amount": greater_refund_amount,
                "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api when refund amount is greater than original amount : {response}")
            api_error_message = response["errorMessage"]
            logger.debug(f"Value of errorMessage obtained from refund api when refund amount is greater than original amount response : {api_error_message}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(txn_id) + "'"
            logger.debug(f"Query to fetch data from txn table after refund is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table after refund is : {result}")
            refund_txn_id = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from txn table after refund is : {refund_txn_id}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table after refund is : {refund_txn_type}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table after refund is : {refund_rrn}")
            refund_created_date_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table after refund is : {refund_created_date_time}")
            status_db_refunded = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table after refund is : {status_db_refunded}")
            payment_mode_db_refunded = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table after refund is : {payment_mode_db_refunded}")
            amount_db_refunded = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table after refund is : {amount_db_refunded}")
            state_db_refunded = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table after refund is : {state_db_refunded}")
            payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table after refund is : {payment_gateway_db_refunded}")
            acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table after refund is : {acquirer_code_db_refunded}")
            settlement_status_db_refunded = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table after refund is : {settlement_status_db_refunded}")
            tid_db_refunded = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table after refund is : {tid_db_refunded}")
            mid_db_refunded = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table after refund is : {mid_db_refunded}")
            order_id_db_refunded = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table after refund is : {order_id_db_refunded}")
            auth_code_refunded = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table after refund is : {auth_code_refunded}")
            rrn_refunded = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table after refund is : {rrn_refunded}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_date_time}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table : {txn_type}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Value of org_code obtained from txn table : {org_code_txn}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table : {amount_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table : {status_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {state_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table : {payment_mode_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table : {bank_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table : {payment_gateway_db}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn}")
            order_id_db_original = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table : {order_id_db_original}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")

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
                date_and_time = date_time_converter.to_app_format(created_date_time)
                refund_date_and_time = date_time_converter.to_app_format(refund_created_date_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": refund_txn_id,
                    "txn_amt": str(amount) + ".00",
                    "txn_amt_2": "{:.2f}".format(refunded_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "rrn": str(rrn),
                    "date": date_and_time,
                    "date_2": refund_date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching Transaction status from txn history for the txn : {refund_txn_id}, {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching Transaction payment mode from txn history for the txn : {refund_txn_id}, {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching Transaction id from txn history for the txn : {refund_txn_id}, {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.info(f"Fetching Transaction amount from txn history for the txn : {refund_txn_id}, {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {refund_txn_id}, {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {refund_txn_id}, {payment_msg_refunded}")
                app_refund_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {refund_txn_id}, {app_refund_order_id}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from txn history for the txn : {txn_id}, {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from txn history for the txn : {txn_id}, {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from txn history for the txn : {txn_id}, {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from txn history for the txn : {txn_id}, {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status  from txn history for the txn : {txn_id}, {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching payment message from txn history for the txn : {txn_id}, {payment_msg_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from txn history for the txn : {txn_id}, {app_order_id}")
                app_refund_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.debug(f"Fetching refund date and time from txn history for the txn : {txn_id}, {app_refund_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": app_order_id,
                    "order_id_2": app_refund_order_id,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "date": app_date_and_time,
                    "date_2": app_refund_date_and_time
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
                date_and_time = date_time_converter.db_datetime(created_date_time)
                refund_date_and_time = date_time_converter.db_datetime(refund_created_date_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(refunded_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "rrn": str(rrn),
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": txn_type,
                    "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "AXIS",
                    "txn_type_2": refund_txn_type,
                    "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "date": date_and_time,
                    "date_2": refund_date_and_time,
                    "error_message": f"Transaction declined. Amount entered is more than maximum allowed for the transaction. Maximum Allowed: 100.00",
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api_original = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api_original}")
                amount_api_original = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api_original}")
                payment_mode_api_original = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api_original}")
                rrn_api_original = response_1["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api_original}")
                state_api_original = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api_original}")
                settlement_status_api_original = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api_original}")
                issuer_code_api_original = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api_original}")
                acquirer_code_api_original = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api_original}")
                org_code_api_original = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api_original}")
                mid_api_original = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api_original}")
                tid_api_original = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api_original}")
                txn_type_api_original = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api_original}")
                date_api_original = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api_original}")
                order_id_api_original = response_1["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from txnlist api is : {order_id_api_original}")
                device_serial_api_original = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api_original}")

                response_2 = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn api is : {response_2}")
                status_api_refunded = response_2["status"]
                logger.debug(f"Value of status obtained from refund txnlist api is : {status_api_refunded}")
                amount_api_refunded = int(response_2["amount"])
                logger.debug(f"Value of amount obtained from refund txnlist api is : {amount_api_refunded}")
                payment_mode_api_refunded = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from refund txnlist api is : {payment_mode_api_refunded}")
                state_api_refunded = response_2["states"][0]
                logger.debug(f"Value of states obtained from refund txnlist api is : {state_api_refunded}")
                settlement_status_api_refunded = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from refund txnlist api is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from refund txnlist api is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from refund txnlist api is : {org_code_api_refunded}")
                mid_api_refunded = response_2["mid"]
                logger.debug(f"Value of mid obtained from refund txnlist api is : {mid_api_refunded}")
                tid_api_refunded = response_2["tid"]
                logger.debug(f"Value of tid obtained from refund txnlist api is : {tid_api_refunded}")
                txn_type_api_refunded = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from refund txnlist api is : {txn_type_api_refunded}")
                date_api_refunded = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from refund txnlist api is : {date_api_refunded}")
                order_id_api_refunded = response_2["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from refund txnlist api is : {order_id_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt": str(amount_api_original),
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn": str(rrn_api_original),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original, "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded, "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "error_message": api_error_message,
                    "device_serial": device_serial_api_original
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
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": refunded_amount,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "AXIS",
                    "acquirer_code_2": "AXIS",
                    "bank_code": "AXIS",
                    "bank_code_2": "AXIS_DIRECT",
                    "pmt_gateway": "AXIS",
                    "pmt_gateway_2": "AXIS",
                    "upi_txn_type": "PAY_BQR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "HDFC",
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on refund txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table based on refund txn_id : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table based on refund txn_id : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table based on refund txn_id : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table based on refund txn_id : {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table based on refund txn_id : {upi_mc_id_db_refunded}")

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table based on txn_id : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table based on txn_id : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table based on txn_id : {upi_txn_type_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table based on txn_id : {upi_mc_id_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table based on txn_id : {upi_bank_code_db_original}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table : {bqr_org_code_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db,
                    "bank_code_2": upi_bank_code_db_refunded,
                    "pmt_gateway": payment_gateway_db,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id": upi_mc_id_db_original,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                    "order_id": order_id_db_original,
                    "order_id_2": order_id_db_refunded,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "device_serial": str(device_serial_db)
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_date_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:.2f}".format(refunded_amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                original_txn_date, original_txn_time = date_time_converter.to_chargeslip_format(created_date_time)
                refund_txn_date, refund_txn_time = date_time_converter.to_chargeslip_format(refund_created_date_time)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'date': refund_txn_date, 'time': refund_txn_time,
                    'BASE AMOUNT:': "Rs." + str(refunded_amount) + ".00",
                }
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn), 'date': original_txn_date, 'time': original_txn_time,
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                }
                charge_slip_val_result_1 = receipt_validator.perform_charge_slip_validations(refund_txn_id, {"username": app_username,
                                                                                                             "password": app_password},
                                                                                             expected_charge_slip_values_1)

                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id, {"username": app_username,
                                                                                                      "password": app_password},
                                                                                             expected_charge_slip_values_2)

                if charge_slip_val_result_1 and charge_slip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_345():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_UPI_Two_Times_Successful_Partial_Refund_Via_API_AXIS_DIRECT
    Sub Feature Description: Tid Dep - Verification of two times partial refund for bqrv4 upi txn via api for AXIS_DIRECT
    TC naming code description: 100: Payment Method, 102: BQRV4, 345: TC345
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code="AXIS_DIRECT", portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code ='AXIS' and payment_gateway='AXIS';"
        logger.info(f"Query to fetch data for updating status as active in terminal_dependency_config table : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : {merchant_pan}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
        logger.info(f"Query to fetch data for updating status as active in upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the upi_merchant_config table : {tid}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch data from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of terminal_info table : {result}")
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 250
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for UPI Stop Payment : {response}")

            partial_refunded_amount = 150
            logger.debug(f"Partial Refund amount is : {partial_refunded_amount}")

            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username,
                "password": app_password,
                "amount": partial_refunded_amount,
                "originalTransactionId": str(txn_id)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api when partial refund is performed : {response}")
            partial_refund_txn_id_1 = response["txnId"]
            logger.debug(f"Value of txn_id obatined from refund api when partial refund is performed : {partial_refund_txn_id_1}")

            full_refund_amount = 100
            logger.debug(f"Full refund amount is : {full_refund_amount}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username,
                "password": app_password,
                "amount": full_refund_amount,
                "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api when full refund is performed : {response}")
            partial_refund_txn_id_2 = response["txnId"]
            logger.debug(f"Value of txn_id obtained from refund api when full refund is performed : {partial_refund_txn_id_2}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_date_time}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table : {txn_type}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Value of org_code obtained from txn table : {org_code_txn}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table : {amount_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table : {status_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {state_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table : {payment_mode_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table : {bank_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table : {payment_gateway_db}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn}")
            order_id_db = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table : {order_id_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")

            query = "select * from txn where id = '" + str(partial_refund_txn_id_1) + "';"
            logger.debug(f"Query to fetch txn data of first partial refund from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table for first partial refund is : {result}")
            partial_refund_auth_code_1 = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table for first partial refund is : {partial_refund_auth_code_1}")
            partial_refund_txn_type_1 = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table for first partial refund is : {partial_refund_txn_type_1}")
            partial_refund_rrn_1 = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table for first partial refund is : {partial_refund_rrn_1}")
            partial_refund_created_date_time_1 = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table for first partial refund is : {partial_refund_created_date_time_1}")
            partial_refund_status_db_1 = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table for first partial refund is : {partial_refund_status_db_1}")
            partial_refund_payment_mode_db_1 = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table for first partial refund is : {partial_refund_payment_mode_db_1}")
            partial_refund_amount_db_1 = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table for first partial refund is : {partial_refund_amount_db_1}")
            partial_refund_state_db_1 = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table for first partial refund is : {partial_refund_state_db_1}")
            partial_refund_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table for first partial refund is : {partial_refund_payment_gateway_db_1}")
            partial_refund_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table for first partial refund is : {partial_refund_acquirer_code_db_1}")
            partial_refund_settlement_status_db_1 = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table for first partial refund is : {partial_refund_settlement_status_db_1}")
            partial_refund_tid_db_1 = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table for first partial refund is : {partial_refund_tid_db_1}")
            partial_refund_mid_db_1 = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table for first partial refund is : {partial_refund_mid_db_1}")
            partial_refund_order_id_db_1 = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table for first partial refund is : {partial_refund_order_id_db_1}")
            partial_refund_customer_name_1 = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table for first partial refund is : {partial_refund_customer_name_1}")
            partial_refund_payer_name_1 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table : {partial_refund_payer_name_1} ")

            query = "select * from txn where id = '" + str(partial_refund_txn_id_2) + "';"
            logger.debug(f"Query to fetch txn data of second partial refund from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table for second refund is : {result}")
            partial_refund_auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table for second refund is : {partial_refund_auth_code_2}")
            partial_refund_txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table for second refund is : {partial_refund_txn_type_2}")
            partial_refund_rrn_2 = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table for second refund is : {partial_refund_rrn_2}")
            partial_refund_created_date_time_2 = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table for second refund is : {partial_refund_created_date_time_2}")
            partial_refund_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table for second refund is : {partial_refund_status_db_2}")
            partial_refund_payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table for second refund is : {partial_refund_payment_mode_db_2}")
            partial_refund_amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table for second refund is : {partial_refund_amount_db_2}")
            partial_refund_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table for second refund is : {partial_refund_state_db_2}")
            partial_refund_payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table for second refund is : {partial_refund_payment_gateway_db_2}")
            partial_refund_acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table for second refund is : {partial_refund_acquirer_code_db_2}")
            partial_refund_settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table for second refund is : {partial_refund_settlement_status_db_2}")
            partial_refund_tid_db_2 = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table for second refund is : {partial_refund_tid_db_2}")
            partial_refund_mid_db_2 = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table for second refund is : {partial_refund_mid_db_2}")
            partial_refund_order_id_db_2 = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table for second refund is : {partial_refund_order_id_db_2}")
            partial_refund_customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table for second refund is : {partial_refund_customer_name_2}")
            partial_refund_payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table for second refund is : {partial_refund_payer_name_2}")

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
                date_and_time = date_time_converter.to_app_format(created_date_time)
                partial_refund_date_and_time_1 = date_time_converter.to_app_format(partial_refund_created_date_time_1)
                partial_refund_date_and_time_2 = date_time_converter.to_app_format(partial_refund_created_date_time_2)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED REFUNDED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_status_3": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "pmt_mode_3": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "settle_status_3": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": partial_refund_txn_id_1,
                    "txn_id_3": partial_refund_txn_id_2,
                    "txn_amt": str(amount) + ".00",
                    "txn_amt_2": "{:.2f}".format(partial_refunded_amount),
                    "txn_amt_3": "{:.2f}".format(full_refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": partial_refund_customer_name_1,
                    "customer_name_3": partial_refund_customer_name_2,
                    "payer_name": payer_name,
                    "payer_name_2": partial_refund_payer_name_1,
                    "payer_name_3": partial_refund_payer_name_2,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "order_id_3": order_id,
                    "pmt_msg": "REFUND SUCCESSFUL",
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "pmt_msg_3": "REFUND SUCCESSFUL",
                    "rrn": str(rrn),
                    "date": date_and_time,
                    "date_2": partial_refund_date_and_time_1,
                    "date_3": partial_refund_date_and_time_2
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(partial_refund_txn_id_1)
                app_payment_status_partial_refund_1 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_payment_status_partial_refund_1}")
                app_date_and_time_partial_refund_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_date_and_time_partial_refund_1}")
                app_payment_mode_partial_refund_1 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_payment_mode_partial_refund_1}")
                app_txn_id_partial_refund_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_txn_id_partial_refund_1}")
                app_amount_partial_refund_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_amount_partial_refund_1}")
                app_customer_name_partial_refund_1 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_customer_name_partial_refund_1}")
                app_settlement_status_partial_refund_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_settlement_status_partial_refund_1}")
                app_payer_name_partial_refund_1 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_payer_name_partial_refund_1}")
                app_payment_msg_partial_refund_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_payment_msg_partial_refund_1}")
                app_order_id_partial_refund_1 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the partial_refund_txn_id_1 : {partial_refund_txn_id_1}, {app_order_id_partial_refund_1}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(partial_refund_txn_id_2)
                app_payment_status_partial_refund_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_payment_status_partial_refund_2}")
                app_date_and_time_partial_refund_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_date_and_time_partial_refund_2}")
                app_payment_mode_partial_refund_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_payment_mode_partial_refund_2}")
                app_txn_id_partial_refund_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_txn_id_partial_refund_2}")
                app_amount_partial_refund_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_amount_partial_refund_2}")
                app_customer_name_partial_refund_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_customer_name_partial_refund_2}")
                app_settlement_status_partial_refund_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_settlement_status_partial_refund_2}")
                app_payer_name_partial_refund_2 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_payer_name_partial_refund_2}")
                app_payment_msg_partial_refund_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_payment_msg_partial_refund_2}")
                app_order_id_partial_refund_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the partial_refund_txn_id_2 : {partial_refund_txn_id_2}, {app_order_id_partial_refund_2}")

                actual_app_values = {
                    "pmt_status": app_payment_status,
                    "pmt_status_2": app_payment_status_partial_refund_1,
                    "pmt_status_3": app_payment_status_partial_refund_2,
                    "pmt_mode": app_payment_mode,
                    "pmt_mode_2": app_payment_mode_partial_refund_1,
                    "pmt_mode_3": app_payment_mode_partial_refund_2,
                    "settle_status": app_settlement_status,
                    "settle_status_2": app_settlement_status_partial_refund_1,
                    "settle_status_3": app_settlement_status_partial_refund_2,
                    "txn_id": app_txn_id,
                    "txn_id_2": app_txn_id_partial_refund_1,
                    "txn_id_3": app_txn_id_partial_refund_2,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "txn_amt_2": str(app_amount_partial_refund_1).split(' ')[1],
                    "txn_amt_3": str(app_amount_partial_refund_2).split(' ')[1],
                    "customer_name": app_customer_name,
                    "customer_name_2": app_customer_name_partial_refund_1,
                    "customer_name_3": app_customer_name_partial_refund_2,
                    "payer_name": app_payer_name,
                    "payer_name_2": app_payer_name_partial_refund_1,
                    "payer_name_3": app_payer_name_partial_refund_2,
                    "order_id": app_order_id,
                    "order_id_2": app_order_id_partial_refund_1,
                    "order_id_3": app_order_id_partial_refund_2,
                    "pmt_msg": app_payment_msg,
                    "pmt_msg_2": app_payment_msg_partial_refund_1,
                    "pmt_msg_3": app_payment_msg_partial_refund_2,
                    "rrn": str(app_rrn),
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_partial_refund_1,
                    "date_3": app_date_and_time_partial_refund_2,
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
                date_and_time = date_time_converter.db_datetime(created_date_time)
                partial_refund_date_and_time_1 = date_time_converter.db_datetime(partial_refund_created_date_time_1)
                partial_refund_date_and_time_2 = date_time_converter.db_datetime(partial_refund_created_date_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_status_3": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "pmt_mode_3": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "settle_status_3": "SETTLED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state_3": "REFUNDED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(partial_refunded_amount),
                    "txn_amt_3": str(full_refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": partial_refund_customer_name_1,
                    "customer_name_3": partial_refund_customer_name_2,
                    "payer_name": payer_name,
                    "payer_name_2": partial_refund_payer_name_1,
                    "payer_name_3": partial_refund_payer_name_2,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "order_id_3": order_id,
                    "rrn": str(rrn),
                    "date": date_and_time,
                    "date_2": partial_refund_date_and_time_1,
                    "date_3": partial_refund_date_and_time_2,
                    "acquirer_code": "AXIS",
                    "acquirer_code_2": "AXIS",
                    "acquirer_code_3": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": txn_type,
                    "txn_type_2": partial_refund_txn_type_1,
                    "txn_type_3": partial_refund_txn_type_2,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "mid_3": mid,
                    "tid_3": tid,
                    "org_code": org_code_txn,
                    "org_code_2": org_code_txn,
                    "org_code_3": org_code_txn,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api_original = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api_original}")
                amount_api_original = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api_original}")
                payment_mode_api_original = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api_original}")
                state_api_original = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api_original}")
                settlement_status_api_original = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api_original}")
                rrn_api_original = response_1["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api_original}")
                issuer_code_api_original = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api_original}")
                acquirer_code_api_original = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api_original}")
                org_code_api_original = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api_original}")
                mid_api_original = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api_original}")
                tid_api_original = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api_original}")
                txn_type_api_original = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api_original}")
                date_api_original = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api_original}")
                order_id_api_original = response_1["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from txnlist api is : {order_id_api_original}")
                device_serial_api_original = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api_original}")
                customer_name_api_original = response_1["customerName"]
                logger.debug(f"Value of customerName obtained from txnlist api is : {customer_name_api_original}")
                payer_name_api_original = response_1["payerName"]
                logger.debug(f"Value of payerName obtained from txnlist api is : {payer_name_api_original}")

                response_2 = [x for x in response["txns"] if x["txnId"] == partial_refund_txn_id_1][0]
                logger.debug(f"Response after filtering data of first partial refund txn api is : {response_2}")
                partial_refund_status_api_1 = response_2["status"]
                logger.debug(f"Value of status obtained from first partial refund txnlist api is : {partial_refund_status_api_1}")
                partial_refund_amount_api_1 = int(response_2["amount"])
                logger.debug(f"Value of amount obtained from first partial refund txnlist api is : {partial_refund_amount_api_1}")
                partial_refund_payment_mode_api_1 = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from first partial refund txnlist api is : {partial_refund_payment_mode_api_1}")
                partial_refund_state_api_1 = response_2["states"][0]
                logger.debug(f"Value of states obtained from first partial refund txnlist api is : {partial_refund_state_api_1}")
                partial_refund_settle_status_api_1 = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from first partial refund txnlist api is : {partial_refund_settle_status_api_1}")
                partial_refund_acquirer_code_api_1 = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from first partial refund txnlist api is : {partial_refund_acquirer_code_api_1}")
                partial_refund_org_code_api_1 = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from first partial refund txnlist api is : {partial_refund_org_code_api_1}")
                partial_refund_mid_api_1 = response_2["mid"]
                logger.debug(f"Value of mid obtained from first partial refund txnlist api is : {partial_refund_mid_api_1}")
                partial_refund_tid_api_1 = response_2["tid"]
                logger.debug(f"Value of tid obtained from first partial refund txnlist api is : {partial_refund_tid_api_1}")
                partial_refund_txn_type_api_1 = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from first partial refund txnlist api is : {partial_refund_txn_type_api_1}")
                partial_refund_date_api_1 = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from first partial refund txnlist api is : {partial_refund_date_api_1}")
                partial_refund_order_id_api_1 = response_2["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from first partial refund txnlist api is : {partial_refund_order_id_api_1}")
                partial_refund_customer_name_api_1 = response_2["customerName"]
                logger.debug(f"Value of customerName obtained from first partial refund txnlist api is : {partial_refund_customer_name_api_1}")
                partial_refund_payer_name_api_1 = response_2["payerName"]
                logger.debug(f"Value of payerName obtained from first partial refund txnlist api is : {partial_refund_payer_name_api_1}")

                response_3 = [x for x in response["txns"] if x["txnId"] == partial_refund_txn_id_2][0]
                logger.debug(f"Response after filtering data of second partial refund txn api is : {response_3}")
                partial_refund_status_api_2 = response_3["status"]
                logger.debug(f"Value of status obtained from second refund txnlist api is : {partial_refund_status_api_2}")
                partial_refund_amount_api_2 = int(response_3["amount"])
                logger.debug(f"Value of amount obtained from second refund txnlist api is : {partial_refund_amount_api_2}")
                partial_refund_payment_mode_api_2 = response_3["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from second refund txnlist api is : {partial_refund_payment_mode_api_2}")
                partial_refund_state_api_2 = response_3["states"][0]
                logger.debug(f"Value of states obtained from second refund txnlist api is : {partial_refund_state_api_2}")
                partial_refund_settle_status_api_2 = response_3["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from second refund txnlist api is : {partial_refund_settle_status_api_2}")
                partial_refund_acquirer_code_api_2 = response_3["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from second refund txnlist api is : {partial_refund_acquirer_code_api_2}")
                partial_refund_org_code_api_2 = response_3["orgCode"]
                logger.debug(f"Value of orgCode obtained from second refund txnlist api is : {partial_refund_org_code_api_2}")
                partial_refund_mid_api_2 = response_3["mid"]
                logger.debug(f"Value of mid obtained from second refund txnlist api is : {partial_refund_mid_api_2}")
                partial_refund_tid_api_2 = response_3["tid"]
                logger.debug(f"Value of tid obtained from second refund txnlist api is : {partial_refund_tid_api_2}")
                partial_refund_txn_type_api_2 = response_3["txnType"]
                logger.debug(f"Value of txnType obtained from second refund txnlist api is : {partial_refund_txn_type_api_2}")
                partial_refund_date_api_2 = response_3["createdTime"]
                logger.debug(f"Value of createdTime obtained from second refund txnlist api is : {partial_refund_date_api_2}")
                partial_refund_order_id_api_2 = response_3["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from second refund txnlist api is : {partial_refund_order_id_api_2}")
                partial_refund_customer_name_api_2 = response_3["customerName"]
                logger.debug(f"Value of customerName obtained from second refund txnlist api is : {partial_refund_customer_name_api_2}")
                partial_refund_payer_name_api_2 = response_3["payerName"]
                logger.debug(f"Value of payerName obtained from second refund txnlist api is : {partial_refund_payer_name_api_2}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": partial_refund_status_api_1,
                    "pmt_status_3": partial_refund_status_api_2,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": partial_refund_payment_mode_api_1,
                    "pmt_mode_3": partial_refund_payment_mode_api_2,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": partial_refund_settle_status_api_1,
                    "settle_status_3": partial_refund_settle_status_api_2,
                    "pmt_state": state_api_original,
                    "pmt_state_2": partial_refund_state_api_1,
                    "pmt_state_3": partial_refund_state_api_2,
                    "txn_amt": str(amount_api_original),
                    "txn_amt_2": str(partial_refund_amount_api_1),
                    "txn_amt_3": str(partial_refund_amount_api_2),
                    "customer_name": customer_name_api_original,
                    "customer_name_2": partial_refund_customer_name_api_1,
                    "customer_name_3": partial_refund_customer_name_api_2,
                    "payer_name": payer_name_api_original,
                    "payer_name_2": partial_refund_payer_name_api_1,
                    "payer_name_3": partial_refund_payer_name_api_2,
                    "order_id": order_id_api_original,
                    "order_id_2": partial_refund_order_id_api_1,
                    "order_id_3": partial_refund_order_id_api_2,
                    "rrn": str(rrn_api_original),
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(partial_refund_date_api_1),
                    "date_3": date_time_converter.from_api_to_datetime_format(partial_refund_date_api_2),
                    "acquirer_code": acquirer_code_api_original,
                    "acquirer_code_2": partial_refund_acquirer_code_api_1,
                    "acquirer_code_3": partial_refund_acquirer_code_api_2,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "txn_type_2": partial_refund_txn_type_api_1,
                    "txn_type_3": partial_refund_txn_type_api_2,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "mid_2": partial_refund_mid_api_1,
                    "tid_2": partial_refund_tid_api_1,
                    "mid_3": partial_refund_mid_api_2,
                    "tid_3": partial_refund_tid_api_2,
                    "org_code": org_code_api_original,
                    "org_code_2": partial_refund_org_code_api_1,
                    "org_code_3": partial_refund_org_code_api_2,
                    "device_serial": device_serial_api_original
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
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_status_3": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "pmt_mode_3": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "settle_status_3": "SETTLED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state_3": "REFUNDED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(partial_refunded_amount),
                    "txn_amt_3": str(full_refund_amount),
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_status_3": "REFUNDED",
                    "acquirer_code": "AXIS",
                    "acquirer_code_2": "AXIS",
                    "acquirer_code_3": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "AXIS",
                    "pmt_gateway_2": "AXIS",
                    "pmt_gateway_3": "AXIS",
                    "upi_txn_type": "PAY_BQR",
                    "upi_txn_type_2": "REFUND",
                    "upi_txn_type_3": "REFUND",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_bank_code_3": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "upi_mc_id_3": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "mid_3": mid,
                    "tid_3": tid,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "order_id_3": order_id,
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "HDFC",
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from txn table : {upi_mc_id_db}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table : {bqr_org_code_db}")

                query = "select * from upi_txn where txn_id='" + partial_refund_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on first refund txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table based on first refund txn_id : {result}")
                partial_refund_upi_status_db_1 = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from txn table based on first refund txn_id : {partial_refund_upi_status_db_1}")
                partial_refund_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from txn table based on first refund txn_id : {partial_refund_upi_txn_type_db_1}")
                partial_refund_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from txn table based on first refund txn_id : {partial_refund_upi_bank_code_db_1}")
                partial_refund_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from txn table based on first refund txn_id : {partial_refund_upi_mc_id_db_1}")

                query = "select * from upi_txn where txn_id='" + partial_refund_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on second refund txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table based on second refund txn_id : {result}")
                partial_refund_upi_status_db_2 = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from txn table based on second refund txn_id : {partial_refund_upi_status_db_2}")
                partial_refund_upi_txn_type_db_2 = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from txn table based on second refund txn_id : {partial_refund_upi_txn_type_db_2}")
                partial_refund_upi_bank_code_db_2 = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from txn table based on second refund txn_id : {partial_refund_upi_bank_code_db_2}")
                partial_refund_upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from txn table based on second refund txn_id : {partial_refund_upi_mc_id_db_2}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_status_2": partial_refund_status_db_1,
                    "pmt_status_3": partial_refund_status_db_2,
                    "pmt_mode": payment_mode_db,
                    "pmt_mode_2": partial_refund_payment_mode_db_1,
                    "pmt_mode_3": partial_refund_payment_mode_db_2,
                    "settle_status": settlement_status_db,
                    "settle_status_2": partial_refund_settlement_status_db_1,
                    "settle_status_3": partial_refund_settlement_status_db_2,
                    "pmt_state": state_db,
                    "pmt_state_2": partial_refund_state_db_1,
                    "pmt_state_3": partial_refund_state_db_2,
                    "txn_amt": str(amount_db),
                    "txn_amt_2": str(partial_refund_amount_db_1),
                    "txn_amt_3": str(partial_refund_amount_db_2),
                    "upi_txn_status": upi_status_db,
                    "upi_txn_status_2": partial_refund_upi_status_db_1,
                    "upi_txn_status_3": partial_refund_upi_status_db_2,
                    "acquirer_code": acquirer_code_db,
                    "acquirer_code_2": partial_refund_acquirer_code_db_1,
                    "acquirer_code_3": partial_refund_acquirer_code_db_2,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "pmt_gateway_2": partial_refund_payment_gateway_db_1,
                    "pmt_gateway_3": partial_refund_payment_gateway_db_2,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_txn_type_2": partial_refund_upi_txn_type_db_1,
                    "upi_txn_type_3": partial_refund_upi_txn_type_db_2,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_bank_code_2": partial_refund_upi_bank_code_db_1,
                    "upi_bank_code_3": partial_refund_upi_bank_code_db_2,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_mc_id_2": partial_refund_upi_mc_id_db_1,
                    "upi_mc_id_3": partial_refund_upi_mc_id_db_2,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": partial_refund_mid_db_1,
                    "tid_2": partial_refund_tid_db_1,
                    "mid_3": partial_refund_mid_db_2,
                    "tid_3": partial_refund_tid_db_2,
                    "order_id": order_id_db,
                    "order_id_2": partial_refund_order_id_db_1,
                    "order_id_3": partial_refund_order_id_db_2,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "device_serial": str(device_serial_db)
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(partial_refund_created_date_time_1)
                date_and_time_portal_3 = date_time_converter.to_portal_format(partial_refund_created_date_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2":  "{:.2f}".format(partial_refunded_amount),
                    "username_2": app_username,
                    "txn_id_2": partial_refund_txn_id_1,
                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "REFUNDED",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": "{:.2f}".format(full_refund_amount),
                    "username_3": app_username,
                    "txn_id_3": partial_refund_txn_id_2
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[2]['Date & Time']
                transaction_id = transaction_details[2]['Transaction ID']
                total_amount = transaction_details[2]['Total Amount'].split()
                rr_number = transaction_details[2]['RR Number']
                transaction_type = transaction_details[2]['Type']
                status = transaction_details[2]['Status']
                username = transaction_details[2]['Username']

                date_time_2 = transaction_details[1]['Date & Time']
                transaction_id_2 = transaction_details[1]['Transaction ID']
                total_amount_2 = transaction_details[1]['Total Amount'].split()
                transaction_type_2 = transaction_details[1]['Type']
                status_2 = transaction_details[1]['Status']
                username_2 = transaction_details[1]['Username']

                date_time_3 = transaction_details[0]['Date & Time']
                transaction_id_3 = transaction_details[0]['Transaction ID']
                total_amount_3 = transaction_details[0]['Total Amount'].split()
                transaction_type_3 = transaction_details[0]['Type']
                status_3 = transaction_details[0]['Status']
                username_3 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "date_time_3": date_time_3,
                    "pmt_state_3": str(status_3),
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                partial_refund_txn_date_1, partial_refund_txn_time_1 = date_time_converter.to_chargeslip_format(partial_refund_created_date_time_1)
                partial_refund_txn_date_2, partial_refund_txn_time_2 = date_time_converter.to_chargeslip_format(partial_refund_created_date_time_2)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'date': partial_refund_txn_date_1,
                    'time': partial_refund_txn_time_1,
                    'BASE AMOUNT:': "Rs." + str(partial_refunded_amount) + ".00",
                }
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'date': partial_refund_txn_date_2,
                    'time': partial_refund_txn_time_2,
                    'BASE AMOUNT:': "Rs." + str(full_refund_amount) + ".00",
                }

                charge_slip_val_result_1 = receipt_validator.perform_charge_slip_validations(partial_refund_txn_id_1, {"username": app_username,
                                                                                                                       "password": app_password},
                                                                                             expected_charge_slip_values_1)

                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(partial_refund_txn_id_2, {"username": app_username,
                                                                                                                       "password": app_password},
                                                                                             expected_charge_slip_values_2)

                if charge_slip_val_result_1 and charge_slip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_346():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_UPI_PartialRefund_In_Decimal_Via_API_AXIS_DIRECT
    Sub Feature Description: TID Dep - Verification of a bqrv4 UPI txn when Decimal Partial refund is performed via api for AXIS_DIRECT
    TC naming code description: 100: Payment Method, 102: BQRV4, 346: TC346
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code="AXIS_DIRECT", portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code ='AXIS' and payment_gateway='AXIS';"
        logger.info(f"Query to fetch data for updating status as active in terminal_dependency_config table : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : {merchant_pan}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
        logger.info(f"Query to fetch data for updating status as active in upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the upi_merchant_config table : {tid}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch data from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of terminal_info table : {result}")
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(201, 300)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for UPI Stop Payment : {response}")

            refund_amount = amount - 100.55
            logger.debug(f"Refund amount is : {refund_amount}")

            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username,
                "password": app_password,
                "amount": refund_amount,
                "originalTransactionId": str(txn_id)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for payment refund is: {response}")
            refund_txn_id = response["txnId"]
            logger.debug(f"Value of txn_id obtained from payment refund is: {refund_txn_id}")
            refund_txn_type = response['txnType']
            logger.debug(f"Value of txnType obtained from payment refund is: {refund_txn_type}")
            customer_name_refund = response['customerName']
            logger.debug(f"Value of customerName obtained from payment refund is: {customer_name_refund}")
            payer_name_refund = response['payerName']
            logger.debug(f"Value of payerName obtained from payment refund is: {payer_name_refund}")

            query = "select * from txn where id = '" + str(refund_txn_id) + "';"
            logger.debug(f"Query to fetch data from txn table after refund is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table after refund is : {result}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table after refund is : {refund_created_time}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table after refund is : {refund_rrn}")
            refund_created_date_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table after refund is : {refund_created_date_time}")
            status_db_refunded = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table after refund is : {status_db_refunded}")
            payment_mode_db_refunded = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table after refund is : {payment_mode_db_refunded}")
            amount_db_refunded = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table after refund is : {amount_db_refunded}")
            state_db_refunded = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table after refund is : {state_db_refunded}")
            payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table after refund is : {payment_gateway_db_refunded}")
            acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table after refund is : {acquirer_code_db_refunded}")
            settlement_status_db_refunded = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table after refund is : {settlement_status_db_refunded}")
            tid_db_refunded = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table after refund is : {tid_db_refunded}")
            mid_db_refunded = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table after refund is : {mid_db_refunded}")
            order_id_db_original = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table after refund is : {order_id_db_original}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_date_time}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table : {txn_type}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Value of org_code obtained from txn table : {org_code_txn}")
            amount_db_original = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table : {amount_db_original}")
            status_db_original = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table : {status_db_original}")
            state_db_original = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {state_db_original}")
            payment_mode_db_original = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table : {payment_mode_db_original}")
            acquirer_code_db_original = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db_original}")
            bank_code_db_original = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table : {bank_code_db_original}")
            mid_db_original = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table : {mid_db_original}")
            tid_db_original = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table : {tid_db_original}")
            payment_gateway_db_original = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table : {payment_gateway_db_original}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn}")
            order_id_db_refunded = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table : {order_id_db_refunded}")
            settlement_status_db_original = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table : {settlement_status_db_original}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")

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

        # -----------------------------------------Start of App Validation------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_date_time)
                refund_date_and_time = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id,
                    "txn_id_2": refund_txn_id,
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_amt_2": "{:.2f}".format(refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name_refund,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name_refund,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "rrn": str(rrn),
                    "date": date_and_time,
                    "date_2": refund_date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching Transaction status from txn history for the txn : {refund_txn_id}, {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching Transaction payment mode from txn history for the txn : {refund_txn_id}, {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching Transaction id from txn history for the txn : {refund_txn_id}, {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.info(f"Fetching Transaction amount from txn history for the txn : {refund_txn_id}, {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {refund_txn_id}, {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {refund_txn_id}, {payment_msg_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {refund_txn_id}, {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from txn history for the txn : {txn_id}, {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from txn history for the txn : {txn_id}, {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from txn history for the txn : {txn_id}, {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from txn history for the txn : {txn_id}, {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status  from txn history for the txn : {txn_id}, {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching payment message from txn history for the txn : {txn_id}, {payment_msg_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from txn history for the txn : {txn_id}, {app_order_id}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": app_order_id,
                    "order_id_2": app_order_id_refunded,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_refunded
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
                date = date_time_converter.db_datetime(created_date_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "rrn": str(rrn),
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "AXIS",
                    "txn_type_2": refund_txn_type,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "date": date,
                    "date_2": refund_date,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api_original = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api_original}")
                amount_api_original = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api_original}")
                payment_mode_api_original = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api_original}")
                rrn_api_original = response_1["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api_original}")
                state_api_original = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api_original}")
                settlement_status_api_original = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api_original}")
                issuer_code_api_original = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api_original}")
                acquirer_code_api_original = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api_original}")
                org_code_api_original = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api_original}")
                mid_api_original = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api_original}")
                tid_api_original = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api_original}")
                txn_type_api_original = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api_original}")
                date_api_original = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api_original}")
                order_id_api_original = response_1["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from txnlist api is : {order_id_api_original}")
                device_serial_api_original = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api_original}")

                response_2 = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn api is : {response_2}")
                status_api_refunded = response_2["status"]
                logger.debug(f"Value of status obtained from refund txnlist api is : {status_api_refunded}")
                amount_api_refunded = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from refund txnlist api is : {amount_api_refunded}")
                payment_mode_api_refunded = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from refund txnlist api is : {payment_mode_api_refunded}")
                state_api_refunded = response_2["states"][0]
                logger.debug(f"Value of states obtained from refund txnlist api is : {state_api_refunded}")
                settlement_status_api_refunded = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from refund txnlist api is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from refund txnlist api is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from refund txnlist api is : {org_code_api_refunded}")
                mid_api_refunded = response_2["mid"]
                logger.debug(f"Value of mid obtained from refund txnlist api is : {mid_api_refunded}")
                tid_api_refunded = response_2["tid"]
                logger.debug(f"Value of tid obtained from refund txnlist api is : {tid_api_refunded}")
                txn_type_api_refunded = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from refund txnlist api is : {txn_type_api_refunded}")
                date_api_refunded = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from refund txnlist api is : {date_api_refunded}")
                order_id_api_refunded = response_2["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from refund txnlist api is : {order_id_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt": float(amount_api_original),
                    "txn_amt_2": float(amount_api_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn": str(rrn_api_original),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original, "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded, "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "device_serial": device_serial_api_original
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": float(refund_amount),
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "AXIS",
                    "acquirer_code_2": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "AXIS",
                    "pmt_gateway_2": "AXIS",
                    "upi_txn_type": "PAY_BQR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "HDFC",
                    "device_serial": str(device_serial),
                    "device_serial_2": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on refund txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table based on refund txn_id : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table based on refund txn_id : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table based on refund txn_id : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table based on refund txn_id : {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table based on refund txn_id : {upi_mc_id_db_refunded}")

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table based on txn_id : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table based on txn_id : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table based on txn_id : {upi_txn_type_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table based on txn_id : {upi_mc_id_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table based on txn_id : {upi_bank_code_db_original}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table : {bqr_org_code_db}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
                    "order_id": order_id_db_original,
                    "order_id_2": order_id_db_refunded,
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db_original,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db_original,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db_original,
                    "pmt_gateway": payment_gateway_db_original,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id": upi_mc_id_db_original,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid": mid_db_original,
                    "tid": tid_db_original,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "device_serial": str(device_serial_db),
                    "device_serial_2": str(device_serial_api_original)
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:.2f}".format(refund_amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,

                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                original_txn_date, original_txn_time = date_time_converter.to_chargeslip_format(created_date_time)
                refund_txn_date, refund_txn_time = date_time_converter.to_chargeslip_format(refund_created_time)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'date': refund_txn_date, 'time': refund_txn_time,
                    'BASE AMOUNT:': "Rs." + str(float(refund_amount))
                }
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn), 'date': original_txn_date, 'time': original_txn_time,
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00"
                }
                charge_slip_val_result_1 = receipt_validator.perform_charge_slip_validations(refund_txn_id, {"username": app_username,
                                                                                                             "password": app_password},
                                                                                             expected_charge_slip_values_1)

                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id, {"username": app_username,
                                                                                                      "password": app_password},
                                                                                             expected_charge_slip_values_2)

                if charge_slip_val_result_1 and charge_slip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)