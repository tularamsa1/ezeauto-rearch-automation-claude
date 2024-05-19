import sys
import time
import pytest
import random
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_311():
    """
    Sub Feature Code: UI_Common_PM_UPI_ICICI_Direct_Success_Callback_After_QR_Expiry_Auto_Refund_Disabled
    Sub Feature Description: Generate QR through API and perform success callback after qr expiry for UPI txn via
    ICICI_Direct pg when auto refund is disabled
    TC naming code description: 100: Payment Method, 101: UPI, 311: TC311
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        #Setting UPI QR Expiry
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received from preconditions for UPI QR Expiry : {response}")

        # query = "select * from upi_merchant_config where org_code ='" + str(
        #     org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"

        query = f"select * from upi_merchant_config where org_code='{str(org_code)}' and " \
                f"status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT';"
        logger.debug(f"Query to fetch data from the upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id obtained from upi_merchant_config table is : {upi_mc_id}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of virtual_tid obtained from upi_merchant_config table is : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of virtual_mid obtained from upi_merchant_config table is : {virtual_mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Value of amount and order_id is: {amount}, {order_id}")

            api_details = DBProcessor.get_api_details('upiqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating upi qr : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id value after initiating upi qr : {txn_id}")

            logger.info("Waiting for the time till qr get expired...")
            time.sleep(60)

            query = f"select * from txn where id='{str(txn_id)}';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            status_db = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = float(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid from txn table is : {mid_db}")
            order_id_db = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id_db}")
            error_msg_db = result['error_message'].values[0]
            logger.debug(f"fetched error_message from txn table is : {error_msg_db}")
            rr_number = result['rr_number'].values[0]
            logger.debug(f"fetched rr_number from txn table is : {rr_number}")

            rrn_2 = txn_id.split('E')[1]
            logger.debug(f"rrn number is generated randomly : {rrn_2}")

            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "PayerAmount": str(amount),
                "BankRRN": rrn_2,
                "merchantTranId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI',request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback api is : {response}")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}'" \
                    f" AND orig_txn_id = '{str(txn_id)}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch txn data from txn table after performing the callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to result obtained from txn table after performing the callback : {query}")
            txn_id_2 = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table after performing the callback : {txn_id_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table after performing the callback : {txn_type_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table after performing the callback : {created_time_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table after performing the callback : {auth_code_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table after performing the callback : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table after performing the callback : {payer_name_2}")
            status_2 = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table after performing the callback : {status_2}")
            payment_mode_2 = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table after performing the callback : {payment_mode_2}")
            txn_amount_2 = float(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table after performing the callback : {txn_amount_2}")
            state_2 = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table after performing the callback : {state_2}")
            payment_gateway_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway from txn table after performing the callback : {payment_gateway_2}")
            acquirer_code_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table after performing the callback : {acquirer_code_2}")
            bank_code_2 = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table after performing the callback : {bank_code_2}")
            settlement_status_2 = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table after performing the callback : {settlement_status_2}")
            tid_db_2 = result['tid'].values[0]
            logger.debug(f"fetched tid from txn table after performing the callback : {tid_db_2}")
            mid_db_2 = result['mid'].values[0]
            logger.debug(f"fetched mid from txn table after performing the callback : {mid_db_2}")
            order_id_2 = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table after performing the callback : {order_id_2}")
            error_msg_2 = result['error_message'].values[0]
            logger.debug(f"fetched error_message from txn table after performing the callback : {error_msg_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"fetched posting_date from txn table after performing the callback : {posting_date_2}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                expected_app_values = {
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "pmt_status": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "rrn": rr_number,
                    "date": date_and_time,
                    "txn_id": txn_id,

                    "txn_amt_2": "{:.2f}".format(amount),
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "pmt_mode_2": "UPI",
                    "txn_id_2": txn_id_2,
                    "date_2": date_and_time_2,
                    "settle_status_2": "SETTLED",
                    "payer_name": payer_name_2,
                    "customer_name": customer_name_2
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the first txn_id : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the first txn_id  : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the first txn_id  : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the first txn_id  : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the first txn_id  : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the first txn_id  : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the first txn_id  : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the first txn_id  : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the second txn_id : {txn_id_2}, {app_date_and_time_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the second txn_id : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the second txn_id : {txn_id_2}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the second txn_id : {txn_id_2}, {app_amount_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the second txn_id : {txn_id_2}, {app_customer_name_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the second txn_id : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the second txn_id : {txn_id_2}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the second txn_id : {txn_id_2}, {app_order_id_2}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rrn": str(app_rrn),

                    "txn_amt_2":  app_amount_2.split(' ')[1],
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "date_2": app_date_and_time_2,
                    "settle_status_2": app_settlement_status_2,
                    "payer_name": app_payer_name_2,
                    "customer_name": app_customer_name_2
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
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "org_code": org_code,
                    "date": date,
                    "order_id": order_id,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "issuer_code_2": "ICICI",
                    "txn_type_2": txn_type_2,
                    "mid_2": virtual_mid,
                    "tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date_2": date_2,
                    "order_id_2": order_id
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                #txn list for QR Generation
                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for txn_id is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received from txnlist is : {response}")
                response_in_list = response["txns"]
                logger.debug(f"list of txns from txnlist api is : {response_in_list}")
                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for qr generation is : {status_api}")
                        amount_api = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for qr generation is : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for qr generation is : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for qr generation is : {state_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for qr generation is : {settlement_status_api}")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for qr generation is : {issuer_code_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for qr generation is : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for qr generation is : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for qr generation is : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for qr generation is : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for qr generation is : {txn_type_api}")
                        date_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for qr generation is : {date_api}")
                        txn_order_id_api = elements["orderNumber"]
                        logger.debug(f"Value of orderNumber obtained from txnlist api for qr generation is : {txn_order_id_api}")

                #txn list for callback
                for elements in response_in_list:
                    if elements["txnId"] == txn_id_2:
                        status_api_2 = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for second txn_id is : {status_api_2}")
                        amount_api_2 = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for second txn_id is : {amount_api_2}")
                        payment_mode_api_2 = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for second txn_id is : {payment_mode_api_2}")
                        state_api_2 = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for second txn_id is : {state_api_2}")
                        rrn_api_2 = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for second txn_id is : {rrn_api_2}")
                        settlement_status_api_2 = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for second txn_id is : {settlement_status_api_2}")
                        issuer_code_api_2 = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for second txn_id is : {issuer_code_api_2}")
                        acquirer_code_api_2 = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for second txn_id is : {acquirer_code_api_2}")
                        org_code_api_2 = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for second txn_id is : {org_code_api_2}")
                        mid_api_2 = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for second txn_id is : {mid_api_2}")
                        tid_api_2 = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for second txn_id is : {tid_api_2}")
                        txn_type_api_2 = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for second txn_id is : {txn_type_api_2}")
                        date_api_2 = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for second txn_id is : {date_api_2}")
                        customer_name_api_2 = elements["customerName"]
                        logger.debug(f"Value of customerName obtained from txnlist api for second txn_id is : {customer_name_api_2}")
                        payer_name_api_2 = elements["payerName"]
                        logger.debug(f"Value of payerName obtained from txnlist api for second txn_id is : {payer_name_api_2}")
                        txn_order_id_api_2 = elements["orderNumber"]
                        logger.debug(f"Value of orderNumber obtained from txnlist api for second txn_id is : {txn_order_id_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "order_id": txn_order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "order_id_2": txn_order_id_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2)
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
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "upi_txn_status": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "order_id": order_id,
                    "error_msg": None,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "bank_code_2": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "upi_txn_type_2": "PAY_QR",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": virtual_mid,
                    "tid_2": virtual_tid,
                    "order_id_2": order_id,
                    "error_msg_2": None,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table for first txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result obtained from upi_txn table for first txn_id : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table for first txn_id : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table for first txn_id : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table for first txn_id : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table for first txn_id : {upi_mc_id_db}")

                query = f"select * from upi_txn where txn_id='{txn_id_2}'"
                logger.debug(f"Query to fetch data from upi_txn table for second txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result obtained from upi_txn table for second txn_id : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table for first txn_id : {upi_status_db_2}")
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table for first txn_id : {upi_txn_type_db_2}")
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table for first txn_id : {upi_bank_code_db_2}")
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table for first txn_id : {upi_mc_id_db_2}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "order_id": order_id_db,
                    "error_msg": error_msg_db,
                    "pmt_status_2": status_2,
                    "pmt_state_2": state_2,
                    "pmt_mode_2": payment_mode_2,
                    "txn_amt_2": txn_amount_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "settle_status_2": settlement_status_2,
                    "acquirer_code_2": acquirer_code_2,
                    "bank_code_2": bank_code_2,
                    "pmt_gateway_2": payment_gateway_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "order_id_2": order_id_2,
                    "error_msg_2": error_msg_2,
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "rrn_2": str(rrn_2),
                    "txn_id_2": txn_id_2,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_1 = transaction_details[0]['Date & Time']
                transaction_id_1 = transaction_details[0]['Transaction ID']
                total_amount_1 = transaction_details[0]['Total Amount'].split()
                transaction_type_1 = transaction_details[0]['Type']
                status_1 = transaction_details[0]['Status']
                username_1 = transaction_details[0]['Username']
                rrn_1 = transaction_details[0]['RR Number']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,

                    "date_time_2": date_time_1,
                    "pmt_state_2": str(status_1),
                    "pmt_type_2": transaction_type_1,
                    "txn_amt_2": total_amount_1[1],
                    "username_2": username_1,
                    "rrn_2": rrn_1,
                    "txn_id_2": transaction_id_1,
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(posting_date_db=posting_date_2)
                expected_charge_slip_values = {
                    'payment_option': 'SALE',
                    'MID': virtual_mid,
                    'TID': virtual_tid,
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date_2,
                }
                logger.debug(f"expected_values : {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id_2,{"username": app_username,
                                                                            "password": app_password},
                                                                  expected_charge_slip_values)
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