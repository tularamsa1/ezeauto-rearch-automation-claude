import random
import sys
import pytest
from Configuration import testsuite_teardown, Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, Validator, date_time_converter, \
    receipt_validator

from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_108_005():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Full_Refund_Via_HDFC
    Sub Feature Description: Verifying full BQRV4 UPI static qr refund using api for HDFC
    TC naming code description:100: Payment method, 108: BQRV4 Static QR, 005: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
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
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Get config_id, mid, tid and merchant_pan from bharatqr_merchant_config table
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_bqr_config_id = result['id'].values[0]
            logger.info(f"fetched config id is : {db_bqr_config_id}")
            db_bqr_config_mid = result['mid'].values[0]
            logger.info(f"fetched mid is : {db_bqr_config_mid}")
            db_bqr_config_tid = result['tid'].values[0]
            logger.info(f"fetched tid is : {db_bqr_config_tid}")
            db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
            logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

            # Get vpa from upi_merchant_config table
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_upi_config_vpa = result['vpa'].values[0]
            logger.info(f"fetched vpa is : {db_upi_config_vpa}")
            db_upi_config_merchant_id = result['pgMerchantId'].values[0]
            logger.info(f"fetched merchantId is : {db_upi_config_merchant_id}")
            db_upi_config_id = result['id'].values[0]
            logger.info(f"fetched id is : {db_upi_config_id}")

            # Delete existing staticQR entry from staticqr_intent table
            testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_bqr_config_id)

            # Call Generate Static QR API
            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]

            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            rrn = random.randint(11111110, 99999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = 'RID' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")
            amount = random.randint(300, 399)
            logger.debug(f"generated random amount is : {amount}")
            status = "SUCCESS"
            logger.debug(f"Payment status is : {status}")
            status_code = "00"
            logger.debug(f"Status code is : {status_code}")

            logger.debug(
                f"replacing the publish_id with {publish_id}, amount with {amount}.00, ref_id with {ref_id}, statusCode with {status_code}, status with {status}  and rrn with {rrn} in the curl_data")

            api_details = DBProcessor.get_api_details('staticqr_upi_callback_curl', curl_data={'ref_id': ref_id,
                                                                                               'amount': str(
                                                                                                   amount) + ".00",
                                                                                               'publish_id': publish_id,
                                                                                               'status': status,
                                                                                               'statusCode': status_code,
                                                                                               'rrn': rrn})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")

            # UPI callback API
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(db_upi_config_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the callBackUpiMerchantRes : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                rrn) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            orig_txn_id = result["id"].iloc[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            auth_code = result['auth_code'].values[0]
            created_time_orig_txn = result["created_time"].values[0]

            logger.debug(
                f"preparing the request payload data to trigger the unified refund for UPI")

            # Calling unified refund API for UPI refund
            api_details = DBProcessor.get_api_details('Refund_cash_Payment', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "originalTransactionId": orig_txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upi refund : {response}")
            second_txn_id = response["txnId"]

            query = "select * from txn where id = '" + str(second_txn_id) + "'; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            rrn_new_2 = result['rr_number'].values[0]
            customer_name_new_2 = result['customer_name'].values[0]
            payer_name_new_2 = result['payer_name'].values[0]
            auth_code_new_2 = result['auth_code'].values[0]
            created_time_second_txn = result["created_time"].values[0]
            order_id = result['external_ref'].values[0]

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
                date_and_time = date_time_converter.to_app_format(created_time_orig_txn)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_second_txn)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED REFUNDED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": orig_txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": str("%.2f" % amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": second_txn_id,
                    "rrn_2": str(rrn_new_2),
                    "customer_name_2": customer_name_new_2,
                    "payer_name_2": payer_name_new_2,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_new_2,
                    "date_2": date_and_time_new_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {orig_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {orig_txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {orig_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {orig_txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {orig_txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {orig_txn_id}, {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {orig_txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {orig_txn_id}, {app_payment_msg}")
                # app_order_id = txn_history_page.fetch_order_id_text()
                # logger.info(f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(second_txn_id)

                payment_status_new_2 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {second_txn_id}, {payment_status_new_2}")
                app_date_and_time_new_2 = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {second_txn_id}, {app_date_and_time_new_2}")
                app_auth_code_new_2 = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {second_txn_id}, {app_auth_code_new_2}")
                payment_mode_new_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {second_txn_id}, {payment_mode_new_2}")
                app_txn_id_new_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {second_txn_id}, {app_txn_id_new_2}")
                app_amount_new_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(
                    f"Fetching txn amount from txn history for the txn : {second_txn_id}, {app_amount_new_2}")
                app_customer_name_new_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {second_txn_id}, {app_customer_name_new_2}")
                app_settlement_status_new_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {second_txn_id}, {app_settlement_status_new_2}")
                app_payer_name_new_2 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {second_txn_id}, {app_payer_name_new_2}")
                app_payment_msg_new_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {second_txn_id}, {app_payment_msg_new_2}")
                # app_order_id_new_2 = txn_history_page.fetch_order_id_text()
                # logger.info(
                #     f"Fetching txn order_id from txn history for the txn : {second_txn_id}, {app_order_id_new_2}")
                app_rrn_new_2 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {second_txn_id}, {app_rrn_new_2}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode,
                                     "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1],
                                     "txn_id": app_txn_id,
                                     "rrn": str(app_rrn),
                                     "customer_name": app_customer_name,
                                     "settle_status": app_settlement_status,
                                     "payer_name": app_payer_name,
                                     "pmt_msg": app_payment_msg,
                                     "auth_code": app_auth_code,
                                     "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_new_2,
                                     "pmt_status_2": payment_status_new_2.split(':')[1],
                                     "txn_amt_2": app_amount_new_2.split(' ')[1],
                                     "txn_id_2": app_txn_id_new_2,
                                     "rrn_2": str(app_rrn_new_2),
                                     "customer_name_2": app_customer_name_new_2,
                                     "settle_status_2": app_settlement_status_new_2,
                                     "payer_name_2": app_payer_name_new_2,
                                     "payment_msg_2": app_payment_msg_new_2,
                                     "auth_code_2": app_auth_code_new_2,
                                     "date_2": app_date_and_time_new_2
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
                date_new = date_time_converter.db_datetime(created_time_orig_txn)
                date_new_2 = date_time_converter.db_datetime(created_time_second_txn)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "REFUNDED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_new,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED", "rrn_2": str(rrn_new_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "mid_2": db_bqr_config_mid,
                    "tid_2": db_bqr_config_tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_new_2,
                    "date_2": date_new_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == orig_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_api = response["createdTime"]
                order_id_api = response["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == second_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_2 = response["status"]
                amount_api_new_2 = float(response["amount"])
                payment_mode_api_new_2 = response["paymentMode"]
                state_api_new_2 = response["states"][0]
                rrn_api_new_2 = response["rrNumber"]
                settlement_status_api_new_2 = response["settlementStatus"]
                acquirer_code_api_new_2 = response["acquirerCode"]
                orgCode_api_new_2 = response["orgCode"]
                mid_api_new_2 = response["mid"]
                tid_api_new_2 = response["tid"]
                txn_type_api_new_2 = response["txnType"]
                auth_code_api_new_2 = response["authCode"]
                date_api_new_2 = response["createdTime"]
                order_id_api_new_2 = response["orderNumber"]

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2, "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2, "rrn_2": str(rrn_api_new_2),
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2, "mid_2": mid_api_new_2, "tid_2": tid_api_new_2,
                    "org_code_2": orgCode_api_new_2,
                    "auth_code_2": auth_code_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2),
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
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": db_upi_config_id,
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "payment_gateway_2": "HDFC",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id_2": db_upi_config_id,
                    "mid_2": db_bqr_config_mid,
                    "tid_2": db_bqr_config_tid,

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = float(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new_2 = result["status"].iloc[0]
                payment_mode_db_new_2 = result["payment_mode"].iloc[0]
                amount_db_new_2 = float(result["amount"].iloc[0])
                state_db_new_2 = result["state"].iloc[0]
                payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
                settlement_status_db_new_2 = result["settlement_status"].iloc[0]
                tid_db_new_2 = result['tid'].values[0]
                mid_db_new_2 = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_2 = result["status"].iloc[0]
                upi_txn_type_db_new_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_2 = result["upi_mc_id"].iloc[0]

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
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "upi_txn_status_2": upi_status_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "mid_2": mid_db_new_2,
                    "tid_2": tid_db_new_2,
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
                    date_and_time_portal = date_time_converter.to_portal_format(created_time_orig_txn)
                    date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_second_txn)

                    expected_portal_values = {
                        "date_time": date_and_time_portal,
                        "pmt_state": "AUTHORIZED_REFUNDED",
                        "pmt_type": "UPI",
                        "txn_amt": f"{str(amount)}.00",
                        "username": app_username,
                        "txn_id": orig_txn_id,
                        "rrn": str(rrn),

                        "date_time_2": date_and_time_portal_2,
                        "pmt_state_2": "REFUNDED",
                        "pmt_type_2": "UPI",
                        "txn_amt_2": f"{str(amount)}.00",
                        "username_2": app_username,
                        "txn_id_2": second_txn_id,
                        "auth_code_2": auth_code_new_2,
                        "rrn_2": rrn_new_2

                    }
                    logger.debug(f"expected_portal_values : {expected_portal_values}")

                    transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id
                                                                             )
                    date_time_2 = transaction_details[0]['Date & Time']
                    transaction_id_2 = transaction_details[0]['Transaction ID']
                    total_amount_2 = transaction_details[0]['Total Amount'].split()
                    rr_number_2 = transaction_details[0]['RR Number']
                    transaction_type_2 = transaction_details[0]['Type']
                    status_2 = transaction_details[0]['Status']
                    username_2 = transaction_details[0]['Username']
                    auth_code_portal_2 = transaction_details[0]['Auth Code']

                    date_time = transaction_details[1]['Date & Time']
                    transaction_id = transaction_details[1]['Transaction ID']
                    total_amount = transaction_details[1]['Total Amount'].split()
                    rr_number = transaction_details[1]['RR Number']
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
                        "rrn": rr_number,

                        "date_time_2": date_time_2,
                        "pmt_state_2": str(status_2),
                        "pmt_type_2": transaction_type_2,
                        "txn_amt_2": total_amount_2[1],
                        "username_2": username_2,
                        "txn_id_2": transaction_id_2,
                        "auth_code_2": auth_code_portal_2,
                        "rrn_2": rr_number_2,

                    }

                    logger.debug(f"actual_portal_values : {actual_portal_values}")

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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_second_txn)
                expected_values = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn_new_2), 'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date, 'time': txn_time,
                }
                receipt_validator.perform_charge_slip_validations(second_txn_id,
                                                                  {"username": app_username,
                                                                   "password": app_password},
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_108_006():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Partial_Refund_Via_HDFC
    Sub Feature Description: Verifying an BQRV4 upi static QR partial refund via HDFC
    TC naming code description: 100: Payment method, 108: BQRV4 static QR, 006: testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
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

            # Get config_id, mid, tid and merchant_pan from bharatqr_merchant_config table
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_bqr_config_id = result['id'].values[0]
            logger.info(f"fetched config id is : {db_bqr_config_id}")
            db_bqr_config_mid = result['mid'].values[0]
            logger.info(f"fetched mid is : {db_bqr_config_mid}")
            db_bqr_config_tid = result['tid'].values[0]
            logger.info(f"fetched tid is : {db_bqr_config_tid}")
            db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
            logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")
            db_bqr_config_terminal_info_id = result["terminal_info_id"].iloc[0]
            logger.info(f"fetched terminal_info_id is : {db_bqr_config_terminal_info_id}")

            # Get vpa from upi_merchant_config table
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_upi_config_vpa = result['vpa'].values[0]
            logger.info(f"fetched vpa is : {db_upi_config_vpa}")
            db_upi_config_merchant_id = result['pgMerchantId'].values[0]
            logger.info(f"fetched merchantId is : {db_upi_config_merchant_id}")
            db_upi_config_id = result['id'].values[0]
            logger.info(f"fetched config id is : {db_upi_config_id}")

            # Delete existing staticQR entry from staticqr_intent table
            testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_bqr_config_id)

            # Call Generate Static QR API
            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]

            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            rrn = random.randint(11111110, 99999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = 'RID' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")
            amount = random.randint(300, 399)
            logger.debug(f"generated random amount is : {amount}")
            status = "SUCCESS"
            logger.debug(f"Payment status is : {status}")
            statusCode = "00"
            logger.debug(f"Status code is : {statusCode}")

            logger.debug(
                f"replacing the publish_id with {publish_id}, amount with {amount}.00, ref_id with {ref_id}, statusCode with {statusCode}, status with {status}  and rrn with {rrn} in the curl_data")

            api_details = DBProcessor.get_api_details('staticqr_upi_callback_curl', curl_data={'ref_id': ref_id,
                                                                                               'amount': str(
                                                                                                   amount) + ".00",
                                                                                               'publish_id': publish_id,
                                                                                               'status': status,
                                                                                               'statusCode': statusCode,
                                                                                               'rrn': rrn})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")

            # UPI callback API
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(db_upi_config_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the callBackUpiMerchantRes : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                rrn) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            orig_txn_id = result["id"].iloc[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            auth_code = result['auth_code'].values[0]
            created_time_orig_txn = result["created_time"].values[0]

            logger.debug(
                f"preparing the request payload data to trigger the unified refund for UPI")

            refund_amount = amount - 100

            # Calling unified refund API for UPI refund
            api_details = DBProcessor.get_api_details('Refund_cash_Payment', request_body={
                "username": app_username,
                "password": app_password,
                "amount": refund_amount,
                "originalTransactionId": orig_txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upi refund : {response}")
            second_txn_id = response["txnId"]

            query = "select * from txn where id = '" + str(second_txn_id) + "'; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            rrn_new_2 = result['rr_number'].values[0]
            customer_name_new_2 = result['customer_name'].values[0]
            payer_name_new_2 = result['payer_name'].values[0]
            auth_code_new_2 = result['auth_code'].values[0]
            created_time_second_txn = result["created_time"].values[0]
            order_id = result['external_ref'].values[0]

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
                date_and_time = date_time_converter.to_app_format(created_time_orig_txn)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_second_txn)

                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": orig_txn_id,
                    "txn_id_2": second_txn_id,
                    "txn_amt": str("%.2f" % amount),
                    "txn_amt_2": str("%.2f" % refund_amount),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn),
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "date_2": date_and_time_new_2
                }
                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(second_txn_id)

                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")
                # app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                # logger.info(
                #      f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {orig_txn_id}, {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                # app_order_id_original = transactions_history_page.fetch_order_id_text()
                # logger.info(
                #     f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id_original}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time}")

                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")

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
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "auth_code": app_auth_code_original,
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_refunded
                }

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id {testcase_id}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_new = date_time_converter.db_datetime(created_time_orig_txn)
                date_new_2 = date_time_converter.db_datetime(created_time_second_txn)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_new,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(refund_amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "rrn_2": str(rrn_new_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "mid_2": db_bqr_config_mid,
                    "tid_2": db_bqr_config_tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_new_2,
                    "date_2": date_new_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == orig_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == second_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_2 = response["status"]
                amount_api_new_2 = float(response["amount"])
                payment_mode_api_new_2 = response["paymentMode"]
                state_api_new_2 = response["states"][0]
                rrn_api_new_2 = response["rrNumber"]
                settlement_status_api_new_2 = response["settlementStatus"]
                acquirer_code_api_new_2 = response["acquirerCode"]
                orgCode_api_new_2 = response["orgCode"]
                mid_api_new_2 = response["mid"]
                tid_api_new_2 = response["tid"]
                txn_type_api_new_2 = response["txnType"]
                auth_code_api_new_2 = response["authCode"]
                date_api_new_2 = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2, "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2, "rrn_2": str(rrn_api_new_2),
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2, "mid_2": mid_api_new_2, "tid_2": tid_api_new_2,
                    "org_code_2": orgCode_api_new_2,
                    "auth_code_2": auth_code_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2),
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
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": db_upi_config_id,
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(refund_amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "payment_gateway_2": "HDFC",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id_2": db_upi_config_id,
                    "mid_2": db_bqr_config_mid,
                    "tid_2": db_bqr_config_tid

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = float(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new_2 = result["status"].iloc[0]
                payment_mode_db_new_2 = result["payment_mode"].iloc[0]
                amount_db_new_2 = float(result["amount"].iloc[0])
                state_db_new_2 = result["state"].iloc[0]
                payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
                settlement_status_db_new_2 = result["settlement_status"].iloc[0]
                tid_db_new_2 = result['tid'].values[0]
                mid_db_new_2 = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_2 = result["status"].iloc[0]
                upi_txn_type_db_new_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_2 = result["upi_mc_id"].iloc[0]

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
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "upi_txn_status_2": upi_status_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "mid_2": mid_db_new_2,
                    "tid_2": tid_db_new_2
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time_orig_txn)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_second_txn)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": orig_txn_id,
                    "rrn": str(rrn),
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(refund_amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": second_txn_id,
                    "auth_code_2": auth_code_new_2,
                    "rrn_2": rrn_new_2

                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id
                                                                         )
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                auth_code_portal_2 = transaction_details[0]['Auth Code']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']

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
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2

                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_second_txn)
                expected_values = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn_new_2), 'BASE AMOUNT:': "Rs." + str(refund_amount) + ".00",
                    'date': txn_date, 'time': txn_time,
                }
                receipt_validator.perform_charge_slip_validations(second_txn_id,
                                                                  {"username": app_username,
                                                                   "password": app_password},
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
def test_common_100_108_007():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Refund_Posted_Via_HDFC
    Sub Feature Description: Verifying BQRV4 static QR upi refund posted via HDFC
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 007: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
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

            # Get config_id, mid, tid and merchant_pan from bharatqr_merchant_config table
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_bqr_config_id = result['id'].values[0]
            logger.info(f"fetched config id is : {db_bqr_config_id}")
            db_bqr_config_mid = result['mid'].values[0]
            logger.info(f"fetched mid is : {db_bqr_config_mid}")
            db_bqr_config_tid = result['tid'].values[0]
            logger.info(f"fetched tid is : {db_bqr_config_tid}")
            db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
            logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

            # Get vpa from upi_merchant_config table
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_upi_config_vpa = result['vpa'].values[0]
            logger.info(f"fetched vpa is : {db_upi_config_vpa}")
            db_upi_config_merchant_id = result['pgMerchantId'].values[0]
            logger.info(f"fetched merchantId is : {db_upi_config_merchant_id}")
            db_upi_config_id = result['id'].values[0]
            logger.info(f"fetched upi config id is : {db_upi_config_id}")

            # Delete existing staticQR entry from staticqr_intent table
            testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_bqr_config_id)

            # Call Generate Static QR API
            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            rrn = random.randint(11111110, 99999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = 'RID' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")
            amount = 555
            logger.debug(f"amount is : {amount}")
            status = "SUCCESS"
            logger.debug(f"Payment status is : {status}")
            statusCode = "00"
            logger.debug(f"Status code is : {statusCode}")

            logger.debug(
                f"replacing the publish_id with {publish_id}, amount with {amount}.00, ref_id with {ref_id}, statusCode with {statusCode}, status with {status}  and rrn with {rrn} in the curl_data")

            api_details = DBProcessor.get_api_details('staticqr_upi_callback_curl', curl_data={'ref_id': ref_id,
                                                                                               'amount': str(
                                                                                                   amount) + ".00",
                                                                                               'publish_id': publish_id,
                                                                                               'status': status,
                                                                                               'statusCode': statusCode,
                                                                                               'rrn': rrn})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")

            # UPI callback API
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(db_upi_config_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the callBackUpiMerchantRes : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                rrn) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            orig_txn_id = result["id"].iloc[0]
            auth_code = result['auth_code'].values[0]
            created_time_orig_txn = result["created_time"].values[0]
            external_ref = result["external_ref"].values[0]
            logger.debug(f"external ref is  : {external_ref}")

            logger.debug(
                f"preparing the request payload data to trigger the unified refund for UPI")

            # Calling unified refund API for UPI refund
            api_details = DBProcessor.get_api_details('Refund_cash_Payment', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "originalTransactionId": orig_txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upi refund : {response}")
            second_txn_id = response["txnId"]

            query = "select * from txn where id = '" + str(second_txn_id) + "'; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            created_time_second_txn = result["created_time"].values[0]

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
                date_and_time = date_time_converter.to_app_format(created_time_orig_txn)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_second_txn)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": orig_txn_id,
                    "rrn": str(rrn),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_POSTED",
                    "txn_amt_2": str("%.2f" % amount),
                    "settle_status_2": "REVPENDING",
                    "txn_id_2": second_txn_id,
                    "pmt_msg_2": "REFUND PENDING",
                    "date_2": date_and_time_new_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {orig_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {orig_txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {orig_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {orig_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {orig_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {orig_txn_id}, {app_payment_msg}")
                # app_order_id = txn_history_page.fetch_order_id_text()
                # logger.info(f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(second_txn_id)

                payment_status_new_2 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {second_txn_id}, {payment_status_new_2}")
                app_date_and_time_new_2 = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {second_txn_id}, {app_date_and_time_new_2}")
                payment_mode_new_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {second_txn_id}, {payment_mode_new_2}")
                app_txn_id_new_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {second_txn_id}, {app_txn_id_new_2}")
                app_amount_new_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(
                    f"Fetching txn amount from txn history for the txn : {second_txn_id}, {app_amount_new_2}")
                app_settlement_status_new_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {second_txn_id}, {app_settlement_status_new_2}")
                app_payment_msg_new_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {second_txn_id}, {app_payment_msg_new_2}")
                # app_order_id_new_2 = txn_history_page.fetch_order_id_text()
                # logger.info(
                #     f"Fetching txn order_id from txn history for the txn : {second_txn_id}, {app_order_id_new_2}")
                actual_app_values = {"pmt_mode": payment_mode,
                                     "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1],
                                     "txn_id": app_txn_id,
                                     "rrn": str(app_rrn),
                                     "settle_status": app_settlement_status,
                                     "pmt_msg": app_payment_msg,
                                     "auth_code": app_auth_code,
                                     "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_new_2,
                                     "pmt_status_2": payment_status_new_2.split(':')[1],
                                     "txn_amt_2": app_amount_new_2.split(' ')[1],
                                     "txn_id_2": app_txn_id_new_2,
                                     "settle_status_2": app_settlement_status_new_2,
                                     "pmt_msg_2": app_payment_msg_new_2,
                                     "date_2": app_date_and_time_new_2
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
                date_orig_txn = date_time_converter.db_datetime(created_time_orig_txn)
                date_second_txn = date_time_converter.db_datetime(created_time_second_txn)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_orig_txn,
                    "pmt_status_2": "REFUND_POSTED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUND_INITIATED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "date_2": date_second_txn
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == orig_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == second_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_2 = response["status"]
                amount_api_new_2 = float(response["amount"])
                payment_mode_api_new_2 = response["paymentMode"]
                state_api_new_2 = response["states"][0]
                settlement_status_api_new_2 = response["settlementStatus"]
                acquirer_code_api_new_2 = response["acquirerCode"]
                orgCode_api_new_2 = response["orgCode"]
                txn_type_api_new_2 = response["txnType"]
                date_api_new_2 = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2, "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2,
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2,
                    "org_code_2": orgCode_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2),
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
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUND_POSTED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "pmt_gateway_2": "HDFC",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "HDFC",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id": db_upi_config_id,
                    "upi_mc_id_2": db_upi_config_id,
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(
                    result["amount"].iloc[0])
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(
                    result["amount"].iloc[0])
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
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
                    "tid": tid_db_original
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time_orig_txn)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_second_txn)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": orig_txn_id,
                    "rrn": str(rrn),
                    "auth_code": auth_code,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUND_POSTED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str("%.2f" % amount),
                    "username_2": app_username,
                    "txn_id_2": second_txn_id

                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                auth_code_portal = transaction_details[1]['Auth Code']

                actual_portal_values = {

                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal,

                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,

                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
def test_common_100_108_008():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Refund_Failed_Via_HDFC
    Sub Feature Description: Verifying BQRV4 UPI static QR refund failed via HDFC
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 008: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
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

            # Get config_id, mid, tid and merchant_pan from bharatqr_merchant_config table
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_bqr_config_id = result['id'].values[0]
            logger.info(f"fetched config id is : {db_bqr_config_id}")
            db_bqr_config_mid = result['mid'].values[0]
            logger.info(f"fetched mid is : {db_bqr_config_mid}")
            db_bqr_config_tid = result['tid'].values[0]
            logger.info(f"fetched tid is : {db_bqr_config_tid}")
            db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
            logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

            # Get vpa from upi_merchant_config table
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_upi_config_vpa = result['vpa'].values[0]
            logger.info(f"fetched vpa is : {db_upi_config_vpa}")
            db_upi_config_merchant_id = result['pgMerchantId'].values[0]
            logger.info(f"fetched merchantId is : {db_upi_config_merchant_id}")
            db_upi_config_id = result['id'].values[0]
            logger.info(f"fetched upi config id is : {db_upi_config_id}")

            # Delete existing staticQR entry from staticqr_intent table
            testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_bqr_config_id)

            # Call Generate Static QR API
            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            rrn = random.randint(11111110, 99999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = 'RID' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")
            amount = 333
            logger.debug(f"amount is : {amount}")
            status = "SUCCESS"
            logger.debug(f"Payment status is : {status}")
            statusCode = "00"
            logger.debug(f"Status code is : {statusCode}")

            logger.debug(
                f"replacing the publish_id with {publish_id}, amount with {amount}.00, ref_id with {ref_id}, statusCode with {statusCode}, status with {status}  and rrn with {rrn} in the curl_data")

            api_details = DBProcessor.get_api_details('staticqr_upi_callback_curl', curl_data={'ref_id': ref_id,
                                                                                               'amount': str(
                                                                                                   amount) + ".00",
                                                                                               'publish_id': publish_id,
                                                                                               'status': status,
                                                                                               'statusCode': statusCode,
                                                                                               'rrn': rrn})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")

            # UPI callback API
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(db_upi_config_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the callBackUpiMerchantRes : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                rrn) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            orig_txn_id = result["id"].iloc[0]
            auth_code = result['auth_code'].values[0]
            created_time_orig_txn = result["created_time"].values[0]
            external_ref = result["external_ref"].values[0]

            logger.debug(
                f"preparing the request payload data to trigger the unified refund for UPI")

            # Calling unified refund API for UPI refund
            api_details = DBProcessor.get_api_details('Refund_cash_Payment', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "originalTransactionId": orig_txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upi refund : {response}")
            second_txn_id = response["txnId"]

            query = "select * from txn where id = '" + str(second_txn_id) + "'; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            created_time_second_txn = result["created_time"].values[0]

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
                date_and_time = date_time_converter.to_app_format(created_time_orig_txn)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_second_txn)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": orig_txn_id,
                    "rrn": str(rrn),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "FAILED",
                    "txn_amt_2": str("%.2f" % amount),
                    "settle_status_2": "FAILED",
                    "txn_id_2": second_txn_id,
                    "pmt_msg_2": "PAYMENT FAILED",
                    "date_2": date_and_time_new_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {orig_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {orig_txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {orig_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {orig_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {orig_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {orig_txn_id}, {app_payment_msg}")
                # app_order_id = txn_history_page.fetch_order_id_text()
                # logger.info(f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(second_txn_id)

                payment_status_new_2 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {second_txn_id}, {payment_status_new_2}")
                app_date_and_time_new_2 = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {second_txn_id}, {app_date_and_time_new_2}")
                payment_mode_new_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {second_txn_id}, {payment_mode_new_2}")
                app_txn_id_new_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {second_txn_id}, {app_txn_id_new_2}")
                app_amount_new_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(
                    f"Fetching txn amount from txn history for the txn : {second_txn_id}, {app_amount_new_2}")
                app_settlement_status_new_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {second_txn_id}, {app_settlement_status_new_2}")
                app_payment_msg_new_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {second_txn_id}, {app_payment_msg_new_2}")
                # app_order_id_new_2 = txn_history_page.fetch_order_id_text()
                # logger.info(
                #     f"Fetching txn order_id from txn history for the txn : {second_txn_id}, {app_order_id_new_2}")

                actual_app_values = {"pmt_mode": payment_mode,
                                     "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1],
                                     "txn_id": app_txn_id,
                                     "rrn": str(app_rrn),
                                     "settle_status": app_settlement_status,
                                     "pmt_msg": app_payment_msg,
                                     "auth_code": app_auth_code,
                                     "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_new_2,
                                     "pmt_status_2": payment_status_new_2.split(':')[1],
                                     "txn_amt_2": app_amount_new_2.split(' ')[1],
                                     "txn_id_2": app_txn_id_new_2,
                                     "settle_status_2": app_settlement_status_new_2,
                                     "pmt_msg_2": app_payment_msg_new_2,
                                     "date_2": app_date_and_time_new_2
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
                date_orig_txn = date_time_converter.db_datetime(created_time_orig_txn)
                date_second_txn = date_time_converter.db_datetime(created_time_second_txn)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date_orig_txn,
                    "pmt_status_2": "FAILED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "FAILED",
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "date_2": date_second_txn
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == orig_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_api = response["createdTime"]
                order_id_api = response["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == second_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_2 = response["status"]
                amount_api_new_2 = float(response["amount"])
                payment_mode_api_new_2 = response["paymentMode"]
                state_api_new_2 = response["states"][0]
                # rrn_api_new_2 = response["rrNumber"]
                settlement_status_api_new_2 = response["settlementStatus"]
                # issuer_code_api_new_2 = response["issuerCode"]
                acquirer_code_api_new_2 = response["acquirerCode"]
                orgCode_api_new_2 = response["orgCode"]
                # mid_api_new_2 = response["mid"]
                # tid_api_new_2 = response["tid"]
                txn_type_api_new_2 = response["txnType"]
                # auth_code_api_new_2 = response["authCode"]
                date_api_new_2 = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    # "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2, "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2,
                    # "rrn_2": str(rrn_api_new_2),
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    # "issuer_code_2": issuer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2,
                    # "mid_2": mid_api_new_2, "tid_2": tid_api_new_2,
                    "org_code_2": orgCode_api_new_2,
                    # "auth_code_2": auth_code_api_new_2,
                    # "order_id_2": order_id_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2),
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
                    "pmt_status_2": "FAILED",
                    "pmt_state_2": "FAILED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "FAILED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "FAILED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "pmt_gateway_2": "HDFC",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "HDFC",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id": db_upi_config_id,
                    "upi_mc_id_2": db_upi_config_id,
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
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
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time_orig_txn)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_second_txn)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": orig_txn_id,
                    "rrn": str(rrn),
                    "auth_code": auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "FAILED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str("%.2f" % amount),
                    "username_2": app_username,
                    "txn_id_2": second_txn_id,

                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         external_ref
                                                                         )
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                auth_code_portal = transaction_details[1]['Auth Code']

                actual_portal_values = {

                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal,

                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,

                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_108_009():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Refund_With_Decimal_Via_HDFC
    Sub Feature Description: Verifying BQRV4 static QR upi refund with decimal value using api for IDFC
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 009: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
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

            # Get config_id, mid, tid and merchant_pan from bharatqr_merchant_config table
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_bqr_config_id = result['id'].values[0]
            logger.info(f"fetched config id is : {db_bqr_config_id}")
            db_bqr_config_mid = result['mid'].values[0]
            logger.info(f"fetched mid is : {db_bqr_config_mid}")
            db_bqr_config_tid = result['tid'].values[0]
            logger.info(f"fetched tid is : {db_bqr_config_tid}")
            db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
            logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

            # Get vpa from upi_merchant_config table
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            db_upi_config_vpa = result['vpa'].values[0]
            logger.info(f"fetched vpa is : {db_upi_config_vpa}")
            db_upi_config_merchant_id = result['pgMerchantId'].values[0]
            logger.info(f"fetched merchantId is : {db_upi_config_merchant_id}")
            db_upi_config_id = result['id'].values[0]
            logger.info(f"fetched upi config id is : {db_upi_config_merchant_id}")

            # Delete existing staticQR entry from staticqr_intent table
            testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_bqr_config_id)

            # Call Generate Static QR API
            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            rrn = random.randint(11111110, 99999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = 'RID' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")
            amount = random.randint(300, 399)
            logger.debug(f"generated random amount is : {amount}")
            status = "SUCCESS"
            logger.debug(f"Payment status is : {status}")
            statusCode = "00"
            logger.debug(f"Status code is : {statusCode}")

            logger.debug(
                f"replacing the publish_id with {publish_id}, amount with {amount}.00, ref_id with {ref_id}, statusCode with {statusCode}, status with {status}  and rrn with {rrn} in the curl_data")

            api_details = DBProcessor.get_api_details('staticqr_upi_callback_curl', curl_data={'ref_id': ref_id,
                                                                                               'amount': str(
                                                                                                   amount) + ".00",
                                                                                               'publish_id': publish_id,
                                                                                               'status': status,
                                                                                               'statusCode': statusCode,
                                                                                               'rrn': rrn})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")

            # UPI callback API
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(db_upi_config_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the callBackUpiMerchantRes : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                rrn) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            orig_txn_id = result["id"].iloc[0]
            auth_code = result['auth_code'].values[0]
            created_time_orig_txn = result["created_time"].values[0]
            external_ref = result["external_ref"].values[0]

            logger.debug(
                f"preparing the request payload data to trigger the unified refund for UPI")

            refund_amount = amount - 100.50

            # Calling unified refund API for UPI refund
            api_details = DBProcessor.get_api_details('Refund_cash_Payment', request_body={
                "username": app_username,
                "password": app_password,
                "amount": refund_amount,
                "originalTransactionId": orig_txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upi refund : {response}")
            second_txn_id = response["txnId"]

            query = "select * from txn where id = '" + str(second_txn_id) + "'; "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            rrn_new_2 = result['rr_number'].values[0]
            created_time_second_txn = result["created_time"].values[0]

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
                date_and_time = date_time_converter.to_app_format(created_time_orig_txn)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_second_txn)

                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": orig_txn_id,
                    "txn_id_2": second_txn_id,
                    "txn_amt": str("%.2f" % amount),
                    "txn_amt_2": str("%.2f" % refund_amount),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn),
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "date_2": date_and_time_new_2
                }
                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(second_txn_id)

                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")
                # app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                # logger.info(
                #     f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {orig_txn_id}, {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                # app_order_id_original = transactions_history_page.fetch_order_id_text()
                # logger.info(
                #     f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id_original}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time}")

                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")

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
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "auth_code": app_auth_code_original,
                    "date": app_date_and_time,
                    "date_2": app_date_and_time_refunded
                }

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id {testcase_id}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_orig_txn = date_time_converter.db_datetime(created_time_orig_txn)
                date_second_txn = date_time_converter.db_datetime(created_time_second_txn)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "amt": float(amount),
                    "amt_2": float(refund_amount),
                    "rrn": str(rrn),
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "org_code": org_code,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "mid_2": db_bqr_config_mid,
                    "tid_2": db_bqr_config_tid,
                    "org_code_2": org_code,
                    "auth_code": auth_code,
                    "date": date_orig_txn,
                    "date_2": date_second_txn
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == orig_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                amount_api_original = float(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]
                state_api_original = response["states"][0]
                settlement_status_api_original = response["settlementStatus"]
                issuer_code_api_original = response["issuerCode"]
                acquirer_code_api_original = response["acquirerCode"]
                org_code_api_original = response["orgCode"]
                mid_api_original = response["mid"]
                tid_api_original = response["tid"]
                txn_type_api_original = response["txnType"]
                auth_code_api_original = response["authCode"]
                date_api_original = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == second_txn_id][0]
                status_api_refunded = response["status"]
                amount_api_refunded = float(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "amt": amount_api_original,
                    "amt_2": amount_api_refunded,
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
                    "auth_code": auth_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")
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
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": db_upi_config_id,
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(refund_amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "payment_gateway_2": "HDFC",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id_2": db_upi_config_id,
                    "mid_2": db_bqr_config_mid,
                    "tid_2": db_bqr_config_tid

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = float(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new_2 = result["status"].iloc[0]
                payment_mode_db_new_2 = result["payment_mode"].iloc[0]
                amount_db_new_2 = float(result["amount"].iloc[0])
                state_db_new_2 = result["state"].iloc[0]
                payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
                settlement_status_db_new_2 = result["settlement_status"].iloc[0]
                tid_db_new_2 = result['tid'].values[0]
                mid_db_new_2 = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_2 = result["status"].iloc[0]
                upi_txn_type_db_new_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_2 = result["upi_mc_id"].iloc[0]

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
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "upi_txn_status_2": upi_status_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "mid_2": mid_db_new_2,
                    "tid_2": tid_db_new_2
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time_orig_txn)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_second_txn)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": orig_txn_id,
                    "rrn": str(rrn),
                    "auth_code": auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str("%.2f" % refund_amount),
                    "username_2": app_username,
                    "txn_id_2": second_txn_id,

                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         external_ref
                                                                         )
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                auth_code_portal = transaction_details[1]['Auth Code']

                actual_portal_values = {

                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal,

                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,

                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_second_txn)
                expected_values = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn_new_2), 'BASE AMOUNT:': "Rs." + str(refund_amount) + "0",
                    'date': txn_date, 'time': txn_time,
                }
                receipt_validator.perform_charge_slip_validations(second_txn_id,
                                                                  {"username": app_username,
                                                                   "password": app_password},
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
