import random
import sys
from datetime import datetime
from time import sleep
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_126():
    """
    Sub Feature Code: UI_Common_BQRV4_UPI_success_callback_after_qr_expiry_Auto_Refund_Disabled_HDFC
    Sub Feature Description: Performing a BQRV4 UPI pure upi success callback via HDFC after expiry the qr
     when auto refund is disabled.
    TC naming code description:100-> Payment Method, 102-> BQRV4, 126-> TC126
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]

        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 49.66
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            logger.info("waiting for the time till qr get expired...")
            sleep(60)

            query = "select * from txn where id = '" + str(txn_id) + "'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {txn_id} and {rrn}")
            posting_date = result['created_time'].values[0]

            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': ref_id, 'Txn_id': txn_id,
                                                                 'amount': str(amount),
                                                                 'vpa': vpa, 'rrn': rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result['id'].values[0]
            customer_name_new = result['customer_name'].values[0]
            payer_name_new = result['payer_name'].values[0]
            auth_code_new = result['auth_code'].values[0]
            modified_date_new = result['created_time'].values[0]

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                date_and_time_new = date_time_converter.to_app_format(modified_date_new)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED","txn_amt": str(amount),
                                       "settle_status": "FAILED","txn_id": txn_id,
                                       "order_id": order_id,"msg": "PAYMENT FAILED",
                                       "date": date_and_time,
                                       "pmt_mode_2": "UPI",
                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": str(amount),
                                       "settle_status_2": "SETTLED",
                                       "txn_id_2": txn_id_new,
                                       "rrn_2": str(rrn),
                                       "customer_name_2": customer_name_new,
                                       "payer_name_2": payer_name_new,
                                       "order_id_2": order_id,
                                       "payment_msg_2": "PAYMENT SUCCESSFUL",
                                       "auth_code_2": auth_code_new,
                                       "date_2": date_and_time_new
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)

                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_auth_code_new = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new}, {app_auth_code_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_customer_name_new = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_payer_name_new = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_new}, {app_payer_name_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_new,
                                     "pmt_status_2": payment_status_new.split(':')[1],
                                     "txn_amt_2": app_amount_new.split(' ')[1],
                                     "txn_id_2": app_txn_id_new,
                                     "rrn_2": str(app_rrn_new),
                                     "customer_name_2": app_customer_name_new,
                                     "settle_status_2": app_settlement_status_new,
                                     "payer_name_2": app_payer_name_new,
                                     "order_id_2": app_order_id_new,
                                     "payment_msg_2": app_payment_msg_new,
                                     "auth_code_2": app_auth_code_new,
                                     "date_2": app_date_and_time_new
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
                date = date_time_converter.db_datetime(posting_date)
                date_new = date_time_converter.db_datetime(posting_date)
                expected_api_values = {"pmt_status": "EXPIRED","txn_amt": float(amount),"pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED","settle_status": "FAILED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date,
                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                                       "pmt_state_2": "SETTLED", "rrn_2": str(app_rrn_new),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "HDFC",
                                       "issuer_code_2": "HDFC",
                                       "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                                       "org_code_2": org_code,
                                       "auth_code_2": auth_code_new,
                                       "date_2": date_new,
                                       "order_id_2": order_id,
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new = response["status"]
                amount_api_new = float(response["amount"])
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                orgCode_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                auth_code_api_new = response["authCode"]
                date_api_new = response["createdTime"]
                order_id_api_new = response["orderNumber"]


                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_2": status_api_new, "txn_amt_2": amount_api_new,
                                     "pmt_mode_2": payment_mode_api_new,
                                     "pmt_state_2": state_api_new, "rrn_2": str(rrn_api_new),
                                     "settle_status_2": settlement_status_api_new,
                                     "acquirer_code_2": acquirer_code_api_new,
                                     "issuer_code_2": issuer_code_api_new,
                                     "txn_type_2": txn_type_api_new, "mid_2": mid_api_new, "tid_2": tid_api_new,
                                     "org_code_2": orgCode_api_new,
                                     "auth_code_2": auth_code_api_new,
                                     "order_id_2": order_id_api_new,
                                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_new)
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "BHARATQR","pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED","acquirer_code" : "HDFC", "bank_name" : "HDFC Bank",
                                      "mid" :mid, "tid" : tid, "pmt_gateway": "HDFC",
                                      "settle_status": "FAILED",
                                      "bqr_pmt_status": "FAILURE", "bqr_pmt_state": "EXPIRED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": bqr_m_pan,
                                      "bqr_org_code": org_code,
                                      "pmt_status_2": "AUTHORIZED",
                                      "pmt_state_2": "SETTLED",
                                      "pmt_mode_2": "UPI",
                                      "txn_amt_2": float(amount),
                                      "upi_txn_status_2": "AUTHORIZED",
                                      "settle_status_2": "SETTLED",
                                      "acquirer_code_2": "HDFC",
                                      "bank_code_2": "HDFC",
                                      "payment_gateway_2": "HDFC",
                                      "upi_txn_type_2": "PAY_BQR",
                                      "upi_bank_code_2": "HDFC",
                                      "upi_mc_id_2": upi_mc_id,
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "order_id_2": order_id,
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].iloc[0]
                payment_mode_db_new = result["payment_mode"].iloc[0]
                amount_db_new = float(result["amount"].iloc[0])
                state_db_new = result["state"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_code_db_new = result["bank_code"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]
                tid_db_new = result['tid'].values[0]
                mid_db_new = result['mid'].values[0]
                order_id_db_new = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]
                upi_mc_id_db_new = result["upi_mc_id"].iloc[0]


                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_org_code": bqr_org_code_db,
                                    "pmt_status_2": status_db_new,
                                    "pmt_state_2": state_db_new,
                                    "pmt_mode_2": payment_mode_db_new,
                                    "txn_amt_2": amount_db_new,
                                    "upi_txn_status_2": upi_status_db_new,
                                    "settle_status_2": settlement_status_db_new,
                                    "acquirer_code_2": acquirer_code_db_new,
                                    "bank_code_2": bank_code_db_new,
                                    "payment_gateway_2": payment_gateway_db_new,
                                    "upi_txn_type_2": upi_txn_type_db_new,
                                    "upi_bank_code_2": upi_bank_code_db_new,
                                    "upi_mc_id_2": upi_mc_id_db_new,
                                    "mid_2": mid_db_new,
                                    "tid_2": tid_db_new,
                                    "order_id_2": order_id_db_new,
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
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                #
                # Write the test case Portal validation code block here. Set this to pass if not required.
                #
                actual_portal_values = {}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(modified_date_new)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount), 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': auth_code_new
                }
                receipt_validator.perform_charge_slip_validations(txn_id_new,
                                                                  {"username": app_username, "password": app_password},
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_127():
    """
    Sub Feature Code: UI_Common_BQRV4_UPI_success_callback_after_qr_expiry_Auto_Refund_Enabled
    Sub Feature Description: Performing a BQRV4 pure upi success callback via HDFC after expiry the qr
     when auto refund is enabled.
    TC naming code description:100-> Payment Method, 102-> BQRV4, 127-> TC127
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]

        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 49.66
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating Bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            logger.info("waiting for the time till qr get expired...")
            sleep(63)

            query = "select * from txn where id = '" + str(txn_id) + "'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {txn_id} and {rrn}")
            created_time = result['created_time'].values[0]

            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': ref_id, 'Txn_id': txn_id,
                                                                 'amount': str(amount),
                                                                 'vpa': vpa, 'rrn': rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result['id'].values[0]
            customer_name_new = result['customer_name'].values[0]
            payer_name_new = result['payer_name'].values[0]
            auth_code_new = result['auth_code'].values[0]
            created_time_new = result['created_time'].values[0]

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
                date_and_time_new = date_time_converter.to_app_format(created_time_new)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED","txn_amt": str(amount),
                                       "settle_status": "FAILED","txn_id": txn_id,
                                       "order_id": order_id,"msg": "PAYMENT FAILED",
                                       "date": date_and_time,
                                       "pmt_mode_2": "UPI",
                                       "pmt_status_2": "REFUND_PENDING",
                                       "txn_amt_2": str(amount),
                                       "settle_status_2": "SETTLED",
                                       "txn_id_2": txn_id_new,
                                       "rrn_2": str(rrn),
                                       "customer_name_2": customer_name_new,
                                       "payer_name_2": payer_name_new,
                                       "order_id_2": order_id,
                                       "payment_msg_2": "PAYMENT SUCCESSFUL",
                                       "auth_code_2": auth_code_new,
                                       "date_2": date_and_time_new
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)

                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_auth_code_new = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new}, {app_auth_code_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_customer_name_new = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_payer_name_new = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_new}, {app_payer_name_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_new,
                                     "pmt_status_2": payment_status_new.split(':')[1],
                                     "txn_amt_2": app_amount_new.split(' ')[1],
                                     "txn_id_2": app_txn_id_new,
                                     "rrn_2": str(app_rrn_new),
                                     "customer_name_2": app_customer_name_new,
                                     "settle_status_2": app_settlement_status_new,
                                     "payer_name_2": app_payer_name_new,
                                     "order_id_2": app_order_id_new,
                                     "payment_msg_2": app_payment_msg_new,
                                     "auth_code_2": app_auth_code_new,
                                     "date_2": app_date_and_time_new
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
                date_new = date_time_converter.db_datetime(created_time_new)
                expected_api_values = {"pmt_status": "EXPIRED","txn_amt": float(amount),"pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED","settle_status": "FAILED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date,
                                       "pmt_status_2": "REFUND_PENDING",
                                       "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                                       "pmt_state_2": "REFUND_PENDING", "rrn_2": str(app_rrn_new),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "HDFC",
                                       "issuer_code_2": "HDFC",
                                       "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                                       "org_code_2": org_code,
                                       "auth_code_2": auth_code_new,
                                       "date_2": date_new,
                                       "order_id_2": order_id
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new = response["status"]
                amount_api_new = float(response["amount"])
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                orgCode_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                auth_code_api_new = response["authCode"]
                date_api_new = response["createdTime"]
                order_id_api_new = response["orderNumber"]


                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_2": status_api_new, "txn_amt_2": amount_api_new,
                                     "pmt_mode_2": payment_mode_api_new,
                                     "pmt_state_2": state_api_new, "rrn_2": str(rrn_api_new),
                                     "settle_status_2": settlement_status_api_new,
                                     "acquirer_code_2": acquirer_code_api_new,
                                     "issuer_code_2": issuer_code_api_new,
                                     "txn_type_2": txn_type_api_new, "mid_2": mid_api_new, "tid_2": tid_api_new,
                                     "org_code_2": orgCode_api_new,
                                     "auth_code_2": auth_code_api_new,
                                     "order_id_2": order_id_api_new,
                                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_new)
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "BHARATQR","pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED","acquirer_code" : "HDFC", "bank_name" : "HDFC Bank",
                                      "mid" :mid, "tid" : tid, "pmt_gateway": "HDFC",
                                      "settle_status": "FAILED",
                                      "bqr_pmt_status": "FAILURE", "bqr_pmt_state": "EXPIRED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": bqr_m_pan,
                                      "bqr_org_code": org_code,
                                      "pmt_status_2": "REFUND_PENDING",
                                      "pmt_state_2": "REFUND_PENDING",
                                      "pmt_mode_2": "UPI",
                                      "txn_amt_2": float(amount),
                                      "upi_txn_status_2": "REFUND_PENDING",
                                      "settle_status_2": "SETTLED",
                                      "acquirer_code_2": "HDFC",
                                      "bank_code_2": "HDFC",
                                      "payment_gateway_2": "HDFC",
                                      "upi_txn_type_2": "PAY_BQR",
                                      "upi_bank_code_2": "HDFC",
                                      "upi_mc_id_2": upi_mc_id,
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "order_id_2": order_id,

                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].iloc[0]
                payment_mode_db_new = result["payment_mode"].iloc[0]
                amount_db_new = float(result["amount"].iloc[0])
                state_db_new = result["state"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_code_db_new = result["bank_code"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]
                tid_db_new = result['tid'].values[0]
                mid_db_new = result['mid'].values[0]
                order_id_db_new = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]
                upi_mc_id_db_new = result["upi_mc_id"].iloc[0]


                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_org_code": bqr_org_code_db,
                                    "pmt_status_2": status_db_new,
                                    "pmt_state_2": state_db_new,
                                    "pmt_mode_2": payment_mode_db_new,
                                    "txn_amt_2": amount_db_new,
                                    "upi_txn_status_2": upi_status_db_new,
                                    "settle_status_2": settlement_status_db_new,
                                    "acquirer_code_2": acquirer_code_db_new,
                                    "bank_code_2": bank_code_db_new,
                                    "payment_gateway_2": payment_gateway_db_new,
                                    "upi_txn_type_2": upi_txn_type_db_new,
                                    "upi_bank_code_2": upi_bank_code_db_new,
                                    "upi_mc_id_2": upi_mc_id_db_new,
                                    "mid_2": mid_db_new,
                                    "tid_2": tid_db_new,
                                    "order_id_2": order_id_db_new
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
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                #
                # Write the test case Portal validation code block here. Set this to pass if not required.
                #
                actual_portal_values = {}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_new)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount), 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': auth_code_new
                }
                receipt_validator.perform_charge_slip_validations(txn_id_new,
                                                                  {"username": app_username, "password": app_password},
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_128():
    """
    Sub Feature Code: UI_Common_BQRV4_UPI_two_callback_after_qr_expiry_Auto_Refund_Disabled_HDFC
    Sub Feature Description: Performing a pure Bqrv4 upi two callback via tid dep HDFC after expiry the qr
     when auto refund is disabled.
    TC naming code description:100-> Payment Method, 102-> BQRV4, 128-> TC128
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]

        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 49.66
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                 })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            logger.info("waiting for the time till qr get expired...")
            sleep(63)

            query = "select * from txn where id = '" + str(txn_id) + "'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {txn_id} and {rrn}")
            posting_date = result['created_time'].values[0]

            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': ref_id, 'Txn_id': txn_id,
                                                                 'amount': str(amount),
                                                                 'vpa': vpa, 'rrn': rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result['id'].values[0]
            customer_name_new = result['customer_name'].values[0]
            payer_name_new = result['payer_name'].values[0]
            auth_code_new = result['auth_code'].values[0]
            modified_date_new = result['created_time'].values[0]

            rrn_new_2 = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': ref_id, 'Txn_id': txn_id,
                                                                 'amount': str(amount),
                                                                 'vpa': vpa, 'rrn': rrn_new_2
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new_3 = result['id'].values[0]
            customer_name_new_3 = result['customer_name'].values[0]
            payer_name_new_3 = result['payer_name'].values[0]
            auth_code_new_3 = result['auth_code'].values[0]
            modified_date_new_3 = result['created_time'].values[0]

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                date_and_time_new = date_time_converter.to_app_format(modified_date_new)
                date_and_time_new_3 = date_time_converter.to_app_format(modified_date_new_3)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED","txn_amt": str(amount),
                                       "settle_status": "FAILED","txn_id": txn_id,
                                       "order_id": order_id,"msg": "PAYMENT FAILED",
                                       "date": date_and_time,
                                       "pmt_mode_2": "UPI",
                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": str(amount),
                                       "settle_status_2": "SETTLED",
                                       "txn_id_2": txn_id_new,
                                       "rrn_2": str(rrn),
                                       "customer_name_2": customer_name_new,
                                       "payer_name_2": payer_name_new,
                                       "order_id_2": order_id,
                                       "payment_msg_2": "PAYMENT SUCCESSFUL",
                                       "auth_code_2": auth_code_new,
                                       "date_2": date_and_time_new,
                                       "pmt_mode_3": "UPI",
                                       "pmt_status_3": "AUTHORIZED",
                                       "txn_amt_3": str(amount),
                                       "settle_status_3": "SETTLED",
                                       "txn_id_3": txn_id_new_3,
                                       "rrn_3": str(rrn_new_2),
                                       "customer_name_3": customer_name_new_3,
                                       "payer_name_3": payer_name_new_3,
                                       "order_id_3": order_id,
                                       "payment_msg_3": "PAYMENT SUCCESSFUL",
                                       "auth_code_3": auth_code_new_3,
                                       "date_3": date_and_time_new_3
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)

                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_auth_code_new = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new}, {app_auth_code_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_customer_name_new = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_payer_name_new = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_new}, {app_payer_name_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new_3)

                payment_status_new_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new_3}, {payment_status_new_3}")
                app_date_and_time_new_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new_3}, {app_date_and_time_new_3}")
                app_auth_code_new_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new_3}, {app_auth_code_new_3}")
                payment_mode_new_3 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id_new_3}, {payment_mode_new_3}")
                app_txn_id_new_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_3}, {app_txn_id_new_3}")
                app_amount_new_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new_3}, {app_amount_new_3}")
                app_customer_name_new_3 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_new_3}, {app_customer_name_new_3}")
                app_settlement_status_new_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new_3}, {app_settlement_status_new_3}")
                app_payer_name_new_3 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {txn_id_new_3}, {app_payer_name_new_3}")
                app_payment_msg_new_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new_3}, {app_payment_msg_new_3}")
                app_order_id_new_3 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {txn_id_new_3}, {app_order_id_new_3}")
                app_rrn_new_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new_3}, {app_rrn_new_3}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_new,
                                     "pmt_status_2": payment_status_new.split(':')[1],
                                     "txn_amt_2": app_amount_new.split(' ')[1],
                                     "txn_id_2": app_txn_id_new,
                                     "rrn_2": str(app_rrn_new),
                                     "customer_name_2": app_customer_name_new,
                                     "settle_status_2": app_settlement_status_new,
                                     "payer_name_2": app_payer_name_new,
                                     "order_id_2": app_order_id_new,
                                     "payment_msg_2": app_payment_msg_new,
                                     "auth_code_2": app_auth_code_new,
                                     "date_2": app_date_and_time_new,
                                     "pmt_mode_3": payment_mode_new_3,
                                     "pmt_status_3": payment_status_new_3.split(':')[1],
                                     "txn_amt_3": app_amount_new_3.split(' ')[1],
                                     "txn_id_3": app_txn_id_new_3,
                                     "rrn_3": str(app_rrn_new_3),
                                     "customer_name_3": app_customer_name_new_3,
                                     "settle_status_3": app_settlement_status_new_3,
                                     "payer_name_3": app_payer_name_new_3,
                                     "order_id_3": app_order_id_new_3,
                                     "payment_msg_3": app_payment_msg_new_3,
                                     "auth_code_3": app_auth_code_new_3,
                                     "date_3": app_date_and_time_new_3
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
                date = date_time_converter.db_datetime(posting_date)
                date_new = date_time_converter.db_datetime(modified_date_new)
                date_new_3 = date_time_converter.db_datetime(modified_date_new_3)
                expected_api_values = {"pmt_status": "EXPIRED","txn_amt": float(amount),"pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED","settle_status": "FAILED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date,
                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                                       "pmt_state_2": "SETTLED", "rrn_2": str(rrn),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "HDFC",
                                       "issuer_code_2": "HDFC",
                                       "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                                       "org_code_2": org_code,
                                       "auth_code_2": auth_code_new,
                                       "date_2": date_new,
                                       "order_id_2": order_id,
                                       "pmt_status_3": "AUTHORIZED",
                                       "txn_amt_3": float(amount), "pmt_mode_3": "UPI",
                                       "pmt_state_3": "SETTLED", "rrn_3": str(rrn_new_2),
                                       "settle_status_3": "SETTLED",
                                       "acquirer_code_3": "HDFC",
                                       "issuer_code_3": "HDFC",
                                       "txn_type_3": "CHARGE", "mid_3": mid, "tid_3": tid,
                                       "org_code_3": org_code,
                                       "auth_code_3": auth_code_new,
                                       "date_3": date_new_3,
                                       "order_id_3": order_id

                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new = response["status"]
                amount_api_new = float(response["amount"])
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                orgCode_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                auth_code_api_new = response["authCode"]
                date_api_new = response["createdTime"]
                order_id_api_new = response["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_new_3][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_3 = response["status"]
                amount_api_new_3 = float(response["amount"])
                payment_mode_api_new_3 = response["paymentMode"]
                state_api_new_3 = response["states"][0]
                rrn_api_new_3 = response["rrNumber"]
                settlement_status_api_new_3 = response["settlementStatus"]
                issuer_code_api_new_3 = response["issuerCode"]
                acquirer_code_api_new_3 = response["acquirerCode"]
                orgCode_api_new_3 = response["orgCode"]
                mid_api_new_3 = response["mid"]
                tid_api_new_3 = response["tid"]
                txn_type_api_new_3 = response["txnType"]
                auth_code_api_new_3 = response["authCode"]
                date_api_new_3 = response["createdTime"]
                order_id_api_new_3 = response["orderNumber"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_2": status_api_new, "txn_amt_2": amount_api_new,
                                     "pmt_mode_2": payment_mode_api_new,
                                     "pmt_state_2": state_api_new, "rrn_2": str(rrn_api_new),
                                     "settle_status_2": settlement_status_api_new,
                                     "acquirer_code_2": acquirer_code_api_new,
                                     "issuer_code_2": issuer_code_api_new,
                                     "txn_type_2": txn_type_api_new, "mid_2": mid_api_new, "tid_2": tid_api_new,
                                     "org_code_2": orgCode_api_new,
                                     "auth_code_2": auth_code_api_new,
                                     "order_id_2": order_id_api_new,
                                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_new),
                                     "pmt_status_3": status_api_new_3, "txn_amt_3": amount_api_new_3,
                                     "pmt_mode_3": payment_mode_api_new_3,
                                     "pmt_state_3": state_api_new_3, "rrn_3": str(rrn_api_new_3),
                                     "settle_status_3": settlement_status_api_new_3,
                                     "acquirer_code_3": acquirer_code_api_new_3,
                                     "issuer_code_3": issuer_code_api_new_3,
                                     "txn_type_3": txn_type_api_new_3, "mid_3": mid_api_new_3, "tid_3": tid_api_new_3,
                                     "org_code_3": orgCode_api_new_3,
                                     "auth_code_3": auth_code_api_new_3,
                                     "order_id_3": order_id_api_new_3,
                                     "date_3": date_time_converter.from_api_to_datetime_format(date_api_new_3)

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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "BHARATQR","pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED","acquirer_code" : "HDFC", "bank_name" : "HDFC Bank",
                                      "mid" :mid, "tid" : tid, "pmt_gateway": "HDFC",
                                      "settle_status": "FAILED",
                                      "bqr_pmt_status": "FAILURE", "bqr_pmt_state": "EXPIRED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": bqr_m_pan,
                                      "bqr_org_code": org_code,
                                      "pmt_status_2": "AUTHORIZED",
                                      "pmt_state_2": "SETTLED",
                                      "pmt_mode_2": "UPI",
                                      "txn_amt_2": float(amount),
                                      "upi_txn_status_2": "AUTHORIZED",
                                      "settle_status_2": "SETTLED",
                                      "acquirer_code_2": "HDFC",
                                      "bank_code_2": "HDFC",
                                      "payment_gateway_2": "HDFC",
                                      "upi_txn_type_2": "PAY_BQR",
                                      "upi_bank_code_2": "HDFC",
                                      "upi_mc_id_2": upi_mc_id,
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "order_id_2": order_id,
                                      "pmt_status_3": "AUTHORIZED",
                                      "pmt_state_3": "SETTLED",
                                      "pmt_mode_3": "UPI",
                                      "txn_amt_3": float(amount),
                                      "upi_txn_status_3": "AUTHORIZED",
                                      "settle_status_3": "SETTLED",
                                      "acquirer_code_3": "HDFC",
                                      "bank_code_3": "HDFC",
                                      "payment_gateway_3": "HDFC",
                                      "upi_txn_type_3": "PAY_BQR",
                                      "upi_bank_code_3": "HDFC",
                                      "upi_mc_id_3": upi_mc_id,
                                      "mid_3": mid,
                                      "tid_3": tid,
                                      "order_id_3": order_id

                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].iloc[0]
                payment_mode_db_new = result["payment_mode"].iloc[0]
                amount_db_new = float(result["amount"].iloc[0])
                state_db_new = result["state"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_code_db_new = result["bank_code"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]
                tid_db_new = result['tid'].values[0]
                mid_db_new = result['mid'].values[0]
                order_id_db_new = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]
                upi_mc_id_db_new = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_new_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new_3 = result["status"].iloc[0]
                payment_mode_db_new_3 = result["payment_mode"].iloc[0]
                amount_db_new_3 = float(result["amount"].iloc[0])
                state_db_new_3 = result["state"].iloc[0]
                payment_gateway_db_new_3 = result["payment_gateway"].iloc[0]
                acquirer_code_db_new_3 = result["acquirer_code"].iloc[0]
                bank_code_db_new_3 = result["bank_code"].iloc[0]
                settlement_status_db_new_3 = result["settlement_status"].iloc[0]
                tid_db_new_3 = result['tid'].values[0]
                mid_db_new_3 = result['mid'].values[0]
                order_id_db_new_3 = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new_3 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_3 = result["status"].iloc[0]
                upi_txn_type_db_new_3 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_3 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_3 = result["upi_mc_id"].iloc[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_org_code": bqr_org_code_db,
                                    "pmt_status_2": status_db_new,
                                    "pmt_state_2": state_db_new,
                                    "pmt_mode_2": payment_mode_db_new,
                                    "txn_amt_2": amount_db_new,
                                    "upi_txn_status_2": upi_status_db_new,
                                    "settle_status_2": settlement_status_db_new,
                                    "acquirer_code_2": acquirer_code_db_new,
                                    "bank_code_2": bank_code_db_new,
                                    "payment_gateway_2": payment_gateway_db_new,
                                    "upi_txn_type_2": upi_txn_type_db_new,
                                    "upi_bank_code_2": upi_bank_code_db_new,
                                    "upi_mc_id_2": upi_mc_id_db_new,
                                    "mid_2": mid_db_new,
                                    "tid_2": tid_db_new,
                                    "order_id_2": order_id_db_new,
                                    "pmt_status_3": status_db_new_3,
                                    "pmt_state_3": state_db_new_3,
                                    "pmt_mode_3": payment_mode_db_new_3,
                                    "txn_amt_3": amount_db_new_3,
                                    "upi_txn_status_3": upi_status_db_new_3,
                                    "settle_status_3": settlement_status_db_new_3,
                                    "acquirer_code_3": acquirer_code_db_new_3,
                                    "bank_code_3": bank_code_db_new_3,
                                    "payment_gateway_3": payment_gateway_db_new_3,
                                    "upi_txn_type_3": upi_txn_type_db_new_3,
                                    "upi_bank_code_3": upi_bank_code_db_new_3,
                                    "upi_mc_id_3": upi_mc_id_db_new_3,
                                    "mid_3": mid_db_new_3,
                                    "tid_3": tid_db_new_3,
                                    "order_id_3": order_id_db_new_3

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
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                #
                # Write the test case Portal validation code block here. Set this to pass if not required.
                #
                actual_portal_values = {}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(modified_date_new)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount), 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': auth_code_new
                }
                receipt_validator.perform_charge_slip_validations(txn_id_new,
                                                                  {"username": app_username, "password": app_password},
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_129():
    """
    Sub Feature Code: UI_Common_BQRV4_UPI_two_callback_after_qr_expiry_Auto_Refund_Enabled_HDFC
    Sub Feature Description: Performing two bqrv4 upi callback via HDFC after expiry the qr when auto refund enabled
     when auto refund is enabled.
    TC naming code description:100-> Payment Method, 102-> BQRV4, 118-> TC118
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]

        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 49.66
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the stop payment : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            logger.info("waiting for the time till qr get expired...")
            sleep(63)

            query = "select * from txn where id = '" + str(txn_id) + "'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {txn_id} and {rrn}")
            posting_date = result['created_time'].values[0]

            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': ref_id, 'Txn_id': txn_id,
                                                                 'amount': str(amount),
                                                                 'vpa': vpa, 'rrn': rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result['id'].values[0]
            customer_name_new = result['customer_name'].values[0]
            payer_name_new = result['payer_name'].values[0]
            auth_code_new = result['auth_code'].values[0]
            modified_date_new = result['created_time'].values[0]

            rrn_new_2 = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': ref_id, 'Txn_id': txn_id,
                                                                 'amount': str(amount),
                                                                 'vpa': vpa, 'rrn': rrn_new_2
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for the callback : {response}")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new_3 = result['id'].values[0]
            customer_name_new_3 = result['customer_name'].values[0]
            payer_name_new_3 = result['payer_name'].values[0]
            auth_code_new_3 = result['auth_code'].values[0]
            modified_date_new_3 = result['created_time'].values[0]

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                date_and_time_new = date_time_converter.to_app_format(modified_date_new)
                date_and_time_new_3 = date_time_converter.to_app_format(modified_date_new_3)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED","txn_amt": str(amount),
                                       "settle_status": "FAILED","txn_id": txn_id,
                                       "order_id": order_id,"msg": "PAYMENT FAILED",
                                       "date": date_and_time,
                                       "pmt_mode_2": "UPI",
                                       "pmt_status_2": "REFUND_PENDING",
                                       "txn_amt_2": str(amount),
                                       "settle_status_2": "SETTLED",
                                       "txn_id_2": txn_id_new,
                                       "rrn_2": str(rrn),
                                       "customer_name_2": customer_name_new,
                                       "payer_name_2": payer_name_new,
                                       "order_id_2": order_id,
                                       "payment_msg_2": "PAYMENT SUCCESSFUL",
                                       "auth_code_2": auth_code_new,
                                       "date_2": date_and_time_new,
                                       "pmt_mode_3": "UPI",
                                       "pmt_status_3": "REFUND_PENDING",
                                       "txn_amt_3": str(amount),
                                       "settle_status_3": "SETTLED",
                                       "txn_id_3": txn_id_new_3,
                                       "rrn_3": str(rrn_new_2),
                                       "customer_name_3": customer_name_new_3,
                                       "payer_name_3": payer_name_new_3,
                                       "order_id_3": order_id,
                                       "payment_msg_3": "PAYMENT SUCCESSFUL",
                                       "auth_code_3": auth_code_new_3,
                                       "date_3": date_and_time_new_3
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)

                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_auth_code_new = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new}, {app_auth_code_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_customer_name_new = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_payer_name_new = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_new}, {app_payer_name_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new_3)

                payment_status_new_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new_3}, {payment_status_new_3}")
                app_date_and_time_new_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new_3}, {app_date_and_time_new_3}")
                app_auth_code_new_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new_3}, {app_auth_code_new_3}")
                payment_mode_new_3 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id_new_3}, {payment_mode_new_3}")
                app_txn_id_new_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_3}, {app_txn_id_new_3}")
                app_amount_new_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new_3}, {app_amount_new_3}")
                app_customer_name_new_3 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_new_3}, {app_customer_name_new_3}")
                app_settlement_status_new_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new_3}, {app_settlement_status_new_3}")
                app_payer_name_new_3 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {txn_id_new_3}, {app_payer_name_new_3}")
                app_payment_msg_new_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new_3}, {app_payment_msg_new_3}")
                app_order_id_new_3 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {txn_id_new_3}, {app_order_id_new_3}")
                app_rrn_new_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new_3}, {app_rrn_new_3}")  # behavior is diff on both emulator and device (Number/NUMBER)


                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_new,
                                     "pmt_status_2": payment_status_new.split(':')[1],
                                     "txn_amt_2": app_amount_new.split(' ')[1],
                                     "txn_id_2": app_txn_id_new,
                                     "rrn_2": str(app_rrn_new),
                                     "customer_name_2": app_customer_name_new,
                                     "settle_status_2": app_settlement_status_new,
                                     "payer_name_2": app_payer_name_new,
                                     "order_id_2": app_order_id_new,
                                     "payment_msg_2": app_payment_msg_new,
                                     "auth_code_2": app_auth_code_new,
                                     "date_2": app_date_and_time_new,
                                     "pmt_mode_3": payment_mode_new_3,
                                     "pmt_status_3": payment_status_new_3.split(':')[1],
                                     "txn_amt_3": app_amount_new_3.split(' ')[1],
                                     "txn_id_3": app_txn_id_new_3,
                                     "rrn_3": str(app_rrn_new_3),
                                     "customer_name_3": app_customer_name_new_3,
                                     "settle_status_3": app_settlement_status_new_3,
                                     "payer_name_3": app_payer_name_new_3,
                                     "order_id_3": app_order_id_new_3,
                                     "payment_msg_3": app_payment_msg_new_3,
                                     "auth_code_3": app_auth_code_new_3,
                                     "date_3": app_date_and_time_new_3
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
                date = date_time_converter.db_datetime(posting_date)
                date_new = date_time_converter.db_datetime(modified_date_new)
                date_new_3 = date_time_converter.db_datetime(modified_date_new_3)
                expected_api_values = {"pmt_status": "EXPIRED","txn_amt": float(amount),"pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED","settle_status": "FAILED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date,
                                       "pmt_status_2": "REFUND_PENDING",
                                       "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                                       "pmt_state_2": "REFUND_PENDING", "rrn_2": str(rrn),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "HDFC",
                                       "issuer_code_2": "HDFC",
                                       "txn_type_2": "CHARGE", "mid_2": mid, "tid_2": tid,
                                       "org_code_2": org_code,
                                       "auth_code_2": auth_code_new,
                                       "date_2": date_new,
                                       "order_id_2": order_id,
                                       "pmt_status_3": "REFUND_PENDING",
                                       "txn_amt_3": float(amount), "pmt_mode_3": "UPI",
                                       "pmt_state_3": "REFUND_PENDING", "rrn_3": str(rrn_new_2),
                                       "settle_status_3": "SETTLED",
                                       "acquirer_code_3": "HDFC",
                                       "issuer_code_3": "HDFC",
                                       "txn_type_3": "CHARGE", "mid_3": mid, "tid_3": tid,
                                       "org_code_3": org_code,
                                       "auth_code_3": auth_code_new,
                                       "date_3": date_new_3,
                                       "order_id_3": order_id
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new = response["status"]
                amount_api_new = float(response["amount"])
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                orgCode_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                auth_code_api_new = response["authCode"]
                date_api_new = response["createdTime"]
                order_id_api_new = response["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_new_3][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_3 = response["status"]
                amount_api_new_3 = float(response["amount"])
                payment_mode_api_new_3 = response["paymentMode"]
                state_api_new_3 = response["states"][0]
                rrn_api_new_3 = response["rrNumber"]
                settlement_status_api_new_3 = response["settlementStatus"]
                issuer_code_api_new_3 = response["issuerCode"]
                acquirer_code_api_new_3 = response["acquirerCode"]
                orgCode_api_new_3 = response["orgCode"]
                mid_api_new_3 = response["mid"]
                tid_api_new_3 = response["tid"]
                txn_type_api_new_3 = response["txnType"]
                auth_code_api_new_3 = response["authCode"]
                date_api_new_3 = response["createdTime"]
                order_id_api_new_3 = response["orderNumber"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_2": status_api_new, "txn_amt_2": amount_api_new,
                                     "pmt_mode_2": payment_mode_api_new,
                                     "pmt_state_2": state_api_new, "rrn_2": str(rrn_api_new),
                                     "settle_status_2": settlement_status_api_new,
                                     "acquirer_code_2": acquirer_code_api_new,
                                     "issuer_code_2": issuer_code_api_new,
                                     "txn_type_2": txn_type_api_new, "mid_2": mid_api_new, "tid_2": tid_api_new,
                                     "org_code_2": orgCode_api_new,
                                     "auth_code_2": auth_code_api_new,
                                     "order_id_2": order_id_api_new,
                                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_new),
                                     "pmt_status_3": status_api_new_3, "txn_amt_3": amount_api_new_3,
                                     "pmt_mode_3": payment_mode_api_new_3,
                                     "pmt_state_3": state_api_new_3, "rrn_3": str(rrn_api_new_3),
                                     "settle_status_3": settlement_status_api_new_3,
                                     "acquirer_code_3": acquirer_code_api_new_3,
                                     "issuer_code_3": issuer_code_api_new_3,
                                     "txn_type_3": txn_type_api_new_3, "mid_3": mid_api_new_3, "tid_3": tid_api_new_3,
                                     "org_code_3": orgCode_api_new_3,
                                     "auth_code_3": auth_code_api_new_3,
                                     "order_id_3": order_id_api_new_3,
                                     "date_3": date_time_converter.from_api_to_datetime_format(date_api_new_3)
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "BHARATQR","pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED","acquirer_code" : "HDFC", "bank_name" : "HDFC Bank",
                                      "mid" :mid, "tid" : tid, "pmt_gateway": "HDFC",
                                      "settle_status": "FAILED",
                                      "bqr_pmt_status": "FAILURE", "bqr_pmt_state": "EXPIRED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": bqr_m_pan,
                                      "bqr_org_code": org_code,
                                      "pmt_status_2": "REFUND_PENDING",
                                      "pmt_state_2": "REFUND_PENDING",
                                      "pmt_mode_2": "UPI",
                                      "txn_amt_2": float(amount),
                                      "upi_txn_status_2": "REFUND_PENDING",
                                      "settle_status_2": "SETTLED",
                                      "acquirer_code_2": "HDFC",
                                      "bank_code_2": "HDFC",
                                      "payment_gateway_2": "HDFC",
                                      "upi_txn_type_2": "PAY_BQR",
                                      "upi_bank_code_2": "HDFC",
                                      "upi_mc_id_2": upi_mc_id,
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "order_id_2": order_id,
                                      "pmt_status_3": "REFUND_PENDING",
                                      "pmt_state_3": "REFUND_PENDING",
                                      "pmt_mode_3": "UPI",
                                      "txn_amt_3": float(amount),
                                      "upi_txn_status_3": "REFUND_PENDING",
                                      "settle_status_3": "SETTLED",
                                      "acquirer_code_3": "HDFC",
                                      "bank_code_3": "HDFC",
                                      "payment_gateway_3": "HDFC",
                                      "upi_txn_type_3": "PAY_BQR",
                                      "upi_bank_code_3": "HDFC",
                                      "upi_mc_id_3": upi_mc_id,
                                      "mid_3": mid,
                                      "tid_3": tid,
                                      "order_id_3": order_id
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].iloc[0]
                payment_mode_db_new = result["payment_mode"].iloc[0]
                amount_db_new = float(result["amount"].iloc[0])
                state_db_new = result["state"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_code_db_new = result["bank_code"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]
                tid_db_new = result['tid'].values[0]
                mid_db_new = result['mid'].values[0]
                order_id_db_new = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]
                upi_mc_id_db_new = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_new_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new_3 = result["status"].iloc[0]
                payment_mode_db_new_3 = result["payment_mode"].iloc[0]
                amount_db_new_3 = float(result["amount"].iloc[0])
                state_db_new_3 = result["state"].iloc[0]
                payment_gateway_db_new_3 = result["payment_gateway"].iloc[0]
                acquirer_code_db_new_3 = result["acquirer_code"].iloc[0]
                bank_code_db_new_3 = result["bank_code"].iloc[0]
                settlement_status_db_new_3 = result["settlement_status"].iloc[0]
                tid_db_new_3 = result['tid'].values[0]
                mid_db_new_3 = result['mid'].values[0]
                order_id_db_new_3 = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new_3 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_3 = result["status"].iloc[0]
                upi_txn_type_db_new_3 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_3 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_3 = result["upi_mc_id"].iloc[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_org_code": bqr_org_code_db,
                                    "pmt_status_2": status_db_new,
                                    "pmt_state_2": state_db_new,
                                    "pmt_mode_2": payment_mode_db_new,
                                    "txn_amt_2": amount_db_new,
                                    "upi_txn_status_2": upi_status_db_new,
                                    "settle_status_2": settlement_status_db_new,
                                    "acquirer_code_2": acquirer_code_db_new,
                                    "bank_code_2": bank_code_db_new,
                                    "payment_gateway_2": payment_gateway_db_new,
                                    "upi_txn_type_2": upi_txn_type_db_new,
                                    "upi_bank_code_2": upi_bank_code_db_new,
                                    "upi_mc_id_2": upi_mc_id_db_new,
                                    "mid_2": mid_db_new,
                                    "tid_2": tid_db_new,
                                    "order_id_2": order_id_db_new,
                                    "pmt_status_3": status_db_new_3,
                                    "pmt_state_3": state_db_new_3,
                                    "pmt_mode_3": payment_mode_db_new_3,
                                    "txn_amt_3": amount_db_new_3,
                                    "upi_txn_status_3": upi_status_db_new_3,
                                    "settle_status_3": settlement_status_db_new_3,
                                    "acquirer_code_3": acquirer_code_db_new_3,
                                    "bank_code_3": bank_code_db_new_3,
                                    "payment_gateway_3": payment_gateway_db_new_3,
                                    "upi_txn_type_3": upi_txn_type_db_new_3,
                                    "upi_bank_code_3": upi_bank_code_db_new_3,
                                    "upi_mc_id_3": upi_mc_id_db_new_3,
                                    "mid_3": mid_db_new_3,
                                    "tid_3": tid_db_new_3,
                                    "order_id_3": order_id_db_new_3
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
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                #
                # Write the test case Portal validation code block here. Set this to pass if not required.
                #
                actual_portal_values = {}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(modified_date_new)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount), 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': auth_code_new
                }
                receipt_validator.perform_charge_slip_validations(txn_id_new,
                                                                  {"username": app_username, "password": app_password},
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_130():
    """
    Sub Feature Code: UI_Common_BQRV4_UPI_amount_mismatch_Via_Pure_UPI_Success_Callback_HDFC
    Sub Feature Description: Performing a amount mismatch using pure upi success callback via HDFC
    TC naming code description:100-> Payment Method, 102->BQRV4 UPI, 130-> TC130
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            logger.debug(f"upi_mc_id from upi_merchant_config table : {upi_mc_id}")
            mid = result['mid'].values[0]
            logger.debug(f"mid from upi_merchant_config table : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"tid from upi_merchant_config table : {tid}")

            amount = random.randint(201, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    })
            response = APIProcessor.send_request(api_details)

            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)
            logger.debug(f"generated random ref_id number is : {ref_id}")

            amount = amount + 1
            logger.debug(f"changing the amount to perform the mismatch scenario")
            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} "
                f"in the curl_data")
            logger.info("performing pure upi success callback for HDFC PG to perform amount_mismatch/upg_authorized")
            api_details = DBProcessor.get_api_details('upi_success_curl', curl_data={
                    'ref_id': ref_id, 'Txn_id': txn_id, 'amount': str(amount) + ".00", 'vpa': vpa, 'rrn': rrn
                })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"encrypted data output is : {data_buffer}")
            logger.debug(f"preparing the request payload data to trigger the "
                         f"/api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes', request_body={
                'pgMerchantId': str(pg_merchant_id), 'meRes': str(data_buffer)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for callBackUpiMerchantRes : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + txn_id + "';")
            logger.debug(f"query to fetch data from the invalid_pg_request table : {query}")
            result = DBProcessor.getValueFromDB(query)
            ipr_txn_id = result['txn_id'].iloc[0]
            logger.debug(f"captured txn_id from invalid_pg_request table is : {ipr_txn_id}")
            ipr_payment_mode = result["payment_mode"].iloc[0]
            logger.debug(f"captured payment_mode from invalid_pg_request : {ipr_payment_mode}")
            ipr_bank_code = result["bank_code"].iloc[0]
            logger.debug(f"captured bank_code from invalid_pg_request : {ipr_bank_code}")
            ipr_org_code = result["org_code"].iloc[0]
            logger.debug(f"captured org_code from invalid_pg_request : {ipr_org_code}")
            ipr_amount = result["amount"].iloc[0]
            logger.debug(f"captured txn_amount from invalid_pg_request : {ipr_amount}")
            ipr_rrn = result["rrn"].iloc[0]
            logger.debug(f"captured rrn from invalid_pg_request : {ipr_rrn}")
            ipr_mid = result["mid"].iloc[0]
            logger.debug(f"captured mid from invalid_pg_request : {ipr_mid}")
            ipr_tid = result["tid"].iloc[0]
            logger.debug(f"captured tid from invalid_pg_request : {ipr_tid}")
            ipr_config_id = result["config_id"].iloc[0]
            logger.debug(f"captured config_id from invalid_pg_request : {ipr_config_id}")
            ipr_vpa = result["vpa"].iloc[0]
            logger.debug(f"captured vpa from invalid_pg_request : {ipr_vpa}")
            ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
            logger.debug(f"captured pg_merchant_id from invalid_pg_request : {ipr_pg_merchant_id}")
            ipr_error_message = result["error_message"].iloc[0]
            logger.debug(f"captured error_message from invalid_pg_request : {ipr_error_message}")

            query = "select * from txn where id = '" + ipr_txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            logger.debug(f"captured auth_code from txn table is : {auth_code}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"captured org_code from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"captured txn_type from txn table is : {txn_type}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"captured posting_date from txn table is : {posting_date}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"captured external_ref from txn table is : {external_ref}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            logger.debug(f"captured upi_mc_id from upi_merchant_config table : {upi_mc_id}")
            mid = result['mid'].values[0]
            logger.debug(f"captured mid from upi_merchant_config table : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"captured tid from upi_merchant_config table : {tid}")

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "txn_id": ipr_txn_id,
                    "txn_amt": str(amount),
                    "rrn": str(rrn),
                    "order_id": external_ref,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "auth_code": str(auth_code)
                }

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(ipr_txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {ipr_txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {ipr_txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {ipr_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {ipr_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {ipr_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {ipr_txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {ipr_txn_id}, {app_order_id}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {ipr_txn_id}, {app_auth_code}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_rrn}")  # behavior is diff on
                # both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "auth_code": app_auth_code
                }

                logger.debug(f"actualAppValues: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "auth_code": str(auth_code)
                    # "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for original_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == ipr_txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        date_api = elements["postingDate"]
                        auth_code_api = elements["authCode"]
                        # device_serial_api = response["deviceSerial"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "auth_code": str(auth_code_api),
                    # "device_serial": str(device_serial_api)
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
                    "pmt_status": "UPG_AUTHORIZED",
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "HDFC",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                    "rrn": str(rrn),
                    # "device_serial": str(device_serial),
                    "ipr_error_message": "Input parameter invalid: "+str(txn_id)
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = "select * from txn where id='" + ipr_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                rrn_db = result['rr_number'].values[0]
                # device_serial_db = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + ipr_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_vpa": ipr_vpa,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                    "rrn": str(rrn_db),
                    # "device_serial": str(device_serial_db),
                    "ipr_error_message": str(ipr_error_message)
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
                expected_portal_values = {}
                actual_portal_values = {}
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)