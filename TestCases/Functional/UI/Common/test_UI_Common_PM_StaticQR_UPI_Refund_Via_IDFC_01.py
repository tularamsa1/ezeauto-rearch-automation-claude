import random
import sys
import pytest
import requests

from Configuration import Configuration, testsuite_teardown, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import Validator, DBProcessor, ConfigReader, date_time_converter, APIProcessor, ResourceAssigner, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_107_019():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Full_Refund_Via_IDFC
    Sub Feature Description: Verifying staticQR UPI full refund using api for IDFC
    TC naming code description:: 100: payment method, 107: UPI Static QR, 019: Testcase ID
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get vpa from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"

        result = DBProcessor.getValueFromDB(query)

        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")

        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")

        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            res_generateqr_publish_id = response["publishId"]

            # Generate HMAC and MerchCreds
            amount = random.randint(201, 399)
            logger.debug(f"generated random amount is : {amount}")

            orig_cust_ref_id = random.randint(11111110, 99999999)

            logger.debug(f"generated random org_cust_ref_id is : {orig_cust_ref_id}")

            ResCode = "000"
            req_merch_creds = "fCef5gQC8s861hBigj+NX7QTY7HuNjbRncLxYnphVJA="
            req_hmac = "8066ac67ef88ea969f0ca50a2c5f43b9ac298ab761b94e778e25d015faaf89b6"

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body={
                "MerchantCredential": req_merch_creds,
                "ResCode": ResCode,
                "HMAC": req_hmac,
                "Amount": amount,
                "PayeeVirAddr": db_upi_config_vpa,
                "MerchantID": db_upi_config_mid,
                "OrgCustRefId": orig_cust_ref_id,
                "OrgTxnRefId": res_generateqr_publish_id,
                "TerminalID": db_upi_config_tid, })
            response1 = APIProcessor.send_request(api_details)
            logger.debug(f"First response received for hmac_merch_cred api is : {response}")
            response_merch_creds = response1.text.replace("\n", "")

            sub_string1 = "MerchantCreds="
            sub_string2 = "HMAC="

            index1 = response_merch_creds.index(sub_string1)
            index2 = response_merch_creds.index(sub_string2)
            generated_merch_creds = response_merch_creds[index1 + len(sub_string1): index2]
            logger.debug(f"Generated MerchCreds is : {generated_merch_creds}")

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body=
            {"MerchantCredential": generated_merch_creds,
             "ResCode": ResCode,
             "HMAC": req_hmac,
             "Amount": amount,
             "PayeeVirAddr": db_upi_config_vpa,
             "MerchantID": db_upi_config_mid,
             "OrgCustRefId": orig_cust_ref_id,
             "OrgTxnRefId": res_generateqr_publish_id,
             "TerminalID": db_upi_config_tid, })
            response2 = APIProcessor.send_request(api_details)
            response_hmac = response2.text

            res = response_hmac.split('HMAC=', 1)
            generated_hmac = res[1]

            logger.debug(f"Second response received : {str(response_hmac)}")
            logger.debug(f"Value of HMAC is : {generated_hmac}")

            req_payload3 = {"MerchantCredential": generated_merch_creds,
                            "ResCode": ResCode,
                            "HMAC": generated_hmac,
                            "Amount": amount,
                            "PayeeVirAddr": db_upi_config_vpa,
                            "MerchantID": db_upi_config_mid,
                            "OrgCustRefId": orig_cust_ref_id,
                            "OrgTxnRefId": res_generateqr_publish_id,
                            "TerminalID": db_upi_config_tid,
                            }

            # UPI Callback
            api_details = DBProcessor.get_api_details('staticQR_UPI_IDFC_callback', request_body=req_payload3)
            response = APIProcessor.send_request(api_details)

            logger.debug(f"Response received for staticQR_UPI_IDFC_callback api is : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                orig_cust_ref_id) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")

            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")

            orig_txn_id = result["id"].iloc[0]
            txn_created_time_orig = result['created_time'].values[0]

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

            rrn_second_txn = result['rr_number'].values[0]
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
                date_and_time = date_time_converter.to_app_format(txn_created_time_orig)
                date_and_time_new = date_time_converter.to_app_format(created_time_second_txn)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": orig_txn_id,
                    "rrn": str(orig_cust_ref_id),
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": str("%.2f" % amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": second_txn_id,
                    "rrn_2": str(rrn_second_txn),
                    "payment_msg_2": "PAYMENT VOIDED/REFUNDED",
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

                txn_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {orig_txn_id}, {app_payment_status}")

                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time}")

                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {orig_txn_id}, {app_payment_mode}")

                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_txn_id}")

                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {orig_txn_id}, {app_amount}")

                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {orig_txn_id}, {app_settlement_status}")

                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {orig_txn_id}, {app_payment_msg}")

                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(second_txn_id)

                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {second_txn_id}, {payment_status_new}")

                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {second_txn_id}, {app_date_and_time_new}")

                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {second_txn_id}, {payment_mode_new}")

                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {second_txn_id}, {app_txn_id_new}")

                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {second_txn_id}, {app_amount_new}")

                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {second_txn_id}, {app_settlement_status_new}")

                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {second_txn_id}, {app_payment_msg_new}")

                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {second_txn_id}, {app_order_id_new}")

                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {second_txn_id}, {app_rrn_new}")

                actual_app_values = {"pmt_mode": app_payment_mode,
                                     "pmt_status": app_payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1],
                                     "txn_id": app_txn_id,
                                     "rrn": str(app_rrn),
                                     "settle_status": app_settlement_status,
                                     "pmt_msg": app_payment_msg,
                                     "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_new,
                                     "pmt_status_2": payment_status_new.split(':')[1],
                                     "txn_amt_2": app_amount_new.split(' ')[1],
                                     "txn_id_2": app_txn_id_new,
                                     "rrn_2": str(app_rrn_new),
                                     "settle_status_2": app_settlement_status_new,
                                     "payment_msg_2": app_payment_msg_new,
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
                date_orig = date_time_converter.db_datetime(txn_created_time_orig)
                date_new = date_time_converter.db_datetime(created_time_second_txn)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "REFUNDED",
                    "rrn": str(orig_cust_ref_id),
                    "settle_status": "SETTLED",
                    "acquirer_code": "IDFC",
                    "issuer_code": "IDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date_orig,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "IDFC",
                    "txn_type_2": "REFUND",
                    "mid_2": db_upi_config_mid,
                    "tid_2": db_upi_config_tid,
                    "org_code_2": org_code,
                    "date_2": date_new
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
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")

                response = [x for x in response["txns"] if x["txnId"] == second_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

                status_api_new = response["status"]
                amount_api_new = float(response["amount"])
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                settlement_status_api_new = response["settlementStatus"]
                acquirer_code_api_new = response["acquirerCode"]
                orgCode_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                date_api_new = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new, "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "txn_type_2": txn_type_api_new,
                    "mid_2": mid_api_new,
                    "tid_2": tid_api_new,
                    "org_code_2": orgCode_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new),
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
                    "acquirer_code": "IDFC",
                    "bank_code": "IDFC",
                    "payment_gateway": "IDFC_FDC",
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "IDFC",
                    "upi_mc_id": db_upi_config_id,
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "IDFC",
                    "payment_gateway_2": "IDFC_FDC",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "IDFC",
                    "upi_mc_id_2": db_upi_config_id,
                    "mid_2": db_upi_config_mid,
                    "tid_2": db_upi_config_tid
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

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_second_txn)
                expected_values = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn_second_txn), 'BASE AMOUNT:': "Rs." + str(amount) + ".00",
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
def test_common_100_107_020():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Partial_Refund_Via_IDFC
    Sub Feature Description: Verifying staticQR UPI partial refund using api for IDFC
    TC naming code description:: 100: payment method, 107: UPI Static QR, 020: Testcase ID
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get vpa from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"

        result = DBProcessor.getValueFromDB(query)

        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")

        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")

        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            res_generateqr_publish_id = response["publishId"]

            # Generate HMAC and MerchCreds
            amount = random.randint(201, 399)
            logger.debug(f"generated random amount is : {amount}")

            orig_cust_ref_id = random.randint(11111110, 99999999)

            logger.debug(f"generated random org_cust_ref_id is : {orig_cust_ref_id}")

            ResCode = "000"
            req_merch_creds = "fCef5gQC8s861hBigj+NX7QTY7HuNjbRncLxYnphVJA="
            req_hmac = "8066ac67ef88ea969f0ca50a2c5f43b9ac298ab761b94e778e25d015faaf89b6"

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body={
                "MerchantCredential": req_merch_creds,
                "ResCode": ResCode,
                "HMAC": req_hmac,
                "Amount": amount,
                "PayeeVirAddr": db_upi_config_vpa,
                "MerchantID": db_upi_config_mid,
                "OrgCustRefId": orig_cust_ref_id,
                "OrgTxnRefId": res_generateqr_publish_id,
                "TerminalID": db_upi_config_tid, })
            response1 = APIProcessor.send_request(api_details)
            logger.debug(f"First response received for hmac_merch_cred api is : {response}")
            response_merch_creds = response1.text.replace("\n", "")

            sub_string1 = "MerchantCreds="
            sub_string2 = "HMAC="

            index1 = response_merch_creds.index(sub_string1)
            index2 = response_merch_creds.index(sub_string2)
            generated_merch_creds = response_merch_creds[index1 + len(sub_string1): index2]
            logger.debug(f"Generated MerchCreds is : {generated_merch_creds}")

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body=
                {"MerchantCredential": generated_merch_creds,
                 "ResCode": ResCode,
                 "HMAC": req_hmac,
                 "Amount": amount,
                 "PayeeVirAddr": db_upi_config_vpa,
                 "MerchantID": db_upi_config_mid,
                 "OrgCustRefId": orig_cust_ref_id,
                 "OrgTxnRefId": res_generateqr_publish_id,
                 "TerminalID": db_upi_config_tid, })
            response2 = APIProcessor.send_request(api_details)
            response_hmac = response2.text

            res = response_hmac.split('HMAC=', 1)
            generated_hmac = res[1]

            logger.debug(f"Second response received : {str(response_hmac)}")
            logger.debug(f"Value of HMAC is : {generated_hmac}")

            req_payload3 = {"MerchantCredential": generated_merch_creds,
                            "ResCode": ResCode,
                            "HMAC": generated_hmac,
                            "Amount": amount,
                            "PayeeVirAddr": db_upi_config_vpa,
                            "MerchantID": db_upi_config_mid,
                            "OrgCustRefId": orig_cust_ref_id,
                            "OrgTxnRefId": res_generateqr_publish_id,
                            "TerminalID": db_upi_config_tid,
                            }

            # UPI Callback
            api_details = DBProcessor.get_api_details('staticQR_UPI_IDFC_callback', request_body=req_payload3)
            response = APIProcessor.send_request(api_details)

            logger.debug(f"Response received for staticQR_UPI_IDFC_callback api is : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                orig_cust_ref_id) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")

            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")

            orig_txn_id = result["id"].iloc[0]
            auth_code = result['auth_code'].values[0]
            created_time_orig_txn = result["created_time"].values[0]

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
            auth_code_new_2 = result['auth_code'].values[0]
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
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(orig_cust_ref_id),
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
                home_page.check_home_page_logo()
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

                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_rrn_original}")

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
                app_order_id_original = transactions_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id_original}")
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
                    "pmt_state": "SETTLED", "rrn": str(orig_cust_ref_id),
                    "settle_status": "SETTLED",
                    "acquirer_code": "IDFC",
                    "issuer_code": "IDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date_new,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(refund_amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "rrn_2": str(rrn_new_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "IDFC",
                    "txn_type_2": "REFUND",
                    "mid_2": db_upi_config_mid,
                    "tid_2": db_upi_config_tid,
                    "org_code_2": org_code,
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
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2, "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2, "rrn_2": str(rrn_api_new_2),
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2, "mid_2": mid_api_new_2, "tid_2": tid_api_new_2,
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
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "IDFC",
                    "bank_code": "IDFC",
                    "payment_gateway": "IDFC_FDC",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "IDFC",
                    "upi_mc_id": db_upi_config_id,
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(refund_amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "IDFC",
                    "payment_gateway_2": "IDFC_FDC",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "IDFC",
                    "upi_mc_id_2": db_upi_config_id,
                    "mid_2": db_upi_config_mid,
                    "tid_2": db_upi_config_tid,
                    "rrn": str(orig_cust_ref_id)

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
                rrn_number = result["rr_number"].iloc[0]

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
                    "rrn": str(rrn_number)
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

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
def test_common_100_107_021():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Refund_Posted_Via_IDFC
    Sub Feature Description: Verifying staticQR UPI refund reposted using api for IDFC
    TC naming code description:: 100: payment method, 107: UPI Static QR, 021: Testcase ID
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Get vpa from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"

        result = DBProcessor.getValueFromDB(query)

        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")

        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")

        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            res_generateqr_publish_id = response["publishId"]

            # Generate HMAC and MerchCreds
            # amount = random.randfloat(201.11, 201.20)
            amount = 201.11
            logger.debug(f"generated random amount is : {amount}")

            orig_cust_ref_id = random.randint(11111110, 99999999)

            logger.debug(f"generated random org_cust_ref_id is : {orig_cust_ref_id}")

            ResCode = "000"
            req_merch_creds = "fCef5gQC8s861hBigj+NX7QTY7HuNjbRncLxYnphVJA="
            req_hmac = "8066ac67ef88ea969f0ca50a2c5f43b9ac298ab761b94e778e25d015faaf89b6"

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body={
                "MerchantCredential": req_merch_creds,
                "ResCode": ResCode,
                "HMAC": req_hmac,
                "Amount": amount,
                "PayeeVirAddr": db_upi_config_vpa,
                "MerchantID": db_upi_config_mid,
                "OrgCustRefId": orig_cust_ref_id,
                "OrgTxnRefId": res_generateqr_publish_id,
                "TerminalID": db_upi_config_tid, })
            response1 = APIProcessor.send_request(api_details)
            logger.debug(f"First response received for hmac_merch_cred api is : {response}")
            response_merch_creds = response1.text.replace("\n", "")

            sub_string1 = "MerchantCreds="
            sub_string2 = "HMAC="

            index1 = response_merch_creds.index(sub_string1)
            index2 = response_merch_creds.index(sub_string2)
            generated_merch_creds = response_merch_creds[index1 + len(sub_string1): index2]
            logger.debug(f"Generated MerchCreds is : {generated_merch_creds}")

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body=
            {"MerchantCredential": generated_merch_creds,
             "ResCode": ResCode,
             "HMAC": req_hmac,
             "Amount": amount,
             "PayeeVirAddr": db_upi_config_vpa,
             "MerchantID": db_upi_config_mid,
             "OrgCustRefId": orig_cust_ref_id,
             "OrgTxnRefId": res_generateqr_publish_id,
             "TerminalID": db_upi_config_tid, })
            response2 = APIProcessor.send_request(api_details)
            response_hmac = response2.text

            res = response_hmac.split('HMAC=', 1)
            generated_hmac = res[1]

            logger.debug(f"Second response received : {str(response_hmac)}")
            logger.debug(f"Value of HMAC is : {generated_hmac}")

            req_payload3 = {"MerchantCredential": generated_merch_creds,
                            "ResCode": ResCode,
                            "HMAC": generated_hmac,
                            "Amount": amount,
                            "PayeeVirAddr": db_upi_config_vpa,
                            "MerchantID": db_upi_config_mid,
                            "OrgCustRefId": orig_cust_ref_id,
                            "OrgTxnRefId": res_generateqr_publish_id,
                            "TerminalID": db_upi_config_tid,
                            }

            # UPI Callback
            api_details = DBProcessor.get_api_details('staticQR_UPI_IDFC_callback', request_body=req_payload3)
            response = APIProcessor.send_request(api_details)

            logger.debug(f"Response received for staticQR_UPI_IDFC_callback api is : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                orig_cust_ref_id) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")

            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")

            orig_txn_id = result["id"].iloc[0]
            txn_created_time_orig = result['created_time'].values[0]

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

            rrn_second_txn = result['rr_number'].values[0]
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
                date_and_time = date_time_converter.to_app_format(txn_created_time_orig)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_second_txn)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": orig_txn_id,
                    "rrn": str(orig_cust_ref_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_POSTED",
                    "txn_amt_2": str("%.2f" % amount),
                    "settle_status_2": "REVPENDING",
                    "txn_id_2": second_txn_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_new_2
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

                txn_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {orig_txn_id}, {payment_status}")

                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time}")

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

                actual_app_values = {"pmt_mode": payment_mode,
                                     "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1],
                                     "txn_id": app_txn_id,
                                     "rrn": str(app_rrn),
                                     "settle_status": app_settlement_status,
                                     "pmt_msg": app_payment_msg,
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
                date_orig_txn = date_time_converter.db_datetime(txn_created_time_orig)
                date_second_txn = date_time_converter.db_datetime(created_time_second_txn)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(orig_cust_ref_id),
                    "settle_status": "SETTLED",
                    "acquirer_code": "IDFC",
                    "issuer_code": "IDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date_orig_txn,
                    "pmt_status_2": "REFUND_POSTED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUND_INITIATED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "IDFC",
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
                    "txn_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUND_POSTED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code": "IDFC",
                    "acquirer_code_2": "IDFC",
                    "bank_code": "IDFC",
                    "pmt_gateway": "IDFC_FDC",
                    "pmt_gateway_2": "IDFC_FDC",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "IDFC",
                    "upi_bank_code_2": "IDFC",
                    "upi_mc_id": db_upi_config_id,
                    "upi_mc_id_2": db_upi_config_id,
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = float(
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
                amount_db_original = float(
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
def test_common_100_107_022():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Refund_Failed_Via_IDFC
    Sub Feature Description: Verifying staticQR UPI refund failed using api for IDFC
    TC naming code description:: 100: payment method, 107: UPI Static QR, 022: Testcase ID
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Get vpa from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"

        result = DBProcessor.getValueFromDB(query)

        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")

        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")

        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            res_generateqr_publish_id = response["publishId"]

            # Generate HMAC and MerchCreds
            amount = 201.01
            logger.debug(f"generated random amount is : {amount}")

            orig_cust_ref_id = random.randint(11111110, 99999999)

            logger.debug(f"generated random org_cust_ref_id is : {orig_cust_ref_id}")

            ResCode = "000"
            req_merch_creds = "fCef5gQC8s861hBigj+NX7QTY7HuNjbRncLxYnphVJA="
            req_hmac = "8066ac67ef88ea969f0ca50a2c5f43b9ac298ab761b94e778e25d015faaf89b6"

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body={
                "MerchantCredential": req_merch_creds,
                "ResCode": ResCode,
                "HMAC": req_hmac,
                "Amount": amount,
                "PayeeVirAddr": db_upi_config_vpa,
                "MerchantID": db_upi_config_mid,
                "OrgCustRefId": orig_cust_ref_id,
                "OrgTxnRefId": res_generateqr_publish_id,
                "TerminalID": db_upi_config_tid, })
            response1 = APIProcessor.send_request(api_details)
            logger.debug(f"First response received for hmac_merch_cred api is : {response}")
            response_merch_creds = response1.text.replace("\n", "")

            sub_string1 = "MerchantCreds="
            sub_string2 = "HMAC="

            index1 = response_merch_creds.index(sub_string1)
            index2 = response_merch_creds.index(sub_string2)
            generated_merch_creds = response_merch_creds[index1 + len(sub_string1): index2]
            logger.debug(f"Generated MerchCreds is : {generated_merch_creds}")

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body=
            {"MerchantCredential": generated_merch_creds,
             "ResCode": ResCode,
             "HMAC": req_hmac,
             "Amount": amount,
             "PayeeVirAddr": db_upi_config_vpa,
             "MerchantID": db_upi_config_mid,
             "OrgCustRefId": orig_cust_ref_id,
             "OrgTxnRefId": res_generateqr_publish_id,
             "TerminalID": db_upi_config_tid, })
            response2 = APIProcessor.send_request(api_details)
            response_hmac = response2.text

            res = response_hmac.split('HMAC=', 1)
            generated_hmac = res[1]

            logger.debug(f"Second response received : {str(response_hmac)}")
            logger.debug(f"Value of HMAC is : {generated_hmac}")

            req_payload3 = {"MerchantCredential": generated_merch_creds,
                            "ResCode": ResCode,
                            "HMAC": generated_hmac,
                            "Amount": amount,
                            "PayeeVirAddr": db_upi_config_vpa,
                            "MerchantID": db_upi_config_mid,
                            "OrgCustRefId": orig_cust_ref_id,
                            "OrgTxnRefId": res_generateqr_publish_id,
                            "TerminalID": db_upi_config_tid,
                            }

            # UPI Callback
            api_details = DBProcessor.get_api_details('staticQR_UPI_IDFC_callback', request_body=req_payload3)
            response = APIProcessor.send_request(api_details)

            logger.debug(f"Response received for staticQR_UPI_IDFC_callback api is : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                orig_cust_ref_id) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")

            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")

            orig_txn_id = result["id"].iloc[0]
            txn_created_time_orig = result['created_time'].values[0]

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

            rrn_second_txn = result['rr_number'].values[0]
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
                date_and_time = date_time_converter.to_app_format(txn_created_time_orig)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_second_txn)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": orig_txn_id,
                    "rrn": str(orig_cust_ref_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
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
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {orig_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time}")
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
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id}")
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
                app_order_id_new_2 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {second_txn_id}, {app_order_id_new_2}")

                actual_app_values = {"pmt_mode": payment_mode,
                                     "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1],
                                     "txn_id": app_txn_id,
                                     "rrn": str(app_rrn),
                                     "settle_status": app_settlement_status,
                                     "pmt_msg": app_payment_msg,
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
                date_orig_txn = date_time_converter.db_datetime(txn_created_time_orig)
                date_second_txn = date_time_converter.db_datetime(created_time_second_txn)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(orig_cust_ref_id),
                    "settle_status": "SETTLED",
                    "acquirer_code": "IDFC",
                    "issuer_code": "IDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "date": date_orig_txn,
                    "pmt_status_2": "FAILED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "FAILED",
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "IDFC",
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
                    "acquirer_code": "IDFC",
                    "acquirer_code_2": "IDFC",
                    "bank_code": "IDFC",
                    "pmt_gateway": "IDFC_FDC",
                    "pmt_gateway_2": "IDFC_FDC",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "IDFC",
                    "upi_bank_code_2": "IDFC",
                    "upi_mc_id": db_upi_config_id,
                    "upi_mc_id_2": db_upi_config_id,
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + second_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = float(result["amount"].iloc[0])
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
                amount_db_original = float(result["amount"].iloc[0])
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
def test_common_100_107_023():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Refund_With_Decimal_Via_IDFC
    Sub Feature Description: Verifying staticQR UPI refund with decimal using api for IDFC
    TC naming code description:: 100: payment method, 107: UPI Static QR, 023: Testcase ID
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Get vpa from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"

        result = DBProcessor.getValueFromDB(query)

        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")

        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")

        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            res_generateqr_publish_id = response["publishId"]

            # Generate HMAC and MerchCreds
            amount = random.randint(201, 399)
            logger.debug(f"generated random amount is : {amount}")

            orig_cust_ref_id = random.randint(11111110, 99999999)

            logger.debug(f"generated random org_cust_ref_id is : {orig_cust_ref_id}")

            ResCode = "000"
            req_merch_creds = "fCef5gQC8s861hBigj+NX7QTY7HuNjbRncLxYnphVJA="
            req_hmac = "8066ac67ef88ea969f0ca50a2c5f43b9ac298ab761b94e778e25d015faaf89b6"

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body={
                "MerchantCredential": req_merch_creds,
                "ResCode": ResCode,
                "HMAC": req_hmac,
                "Amount": amount,
                "PayeeVirAddr": db_upi_config_vpa,
                "MerchantID": db_upi_config_mid,
                "OrgCustRefId": orig_cust_ref_id,
                "OrgTxnRefId": res_generateqr_publish_id,
                "TerminalID": db_upi_config_tid, })
            response1 = APIProcessor.send_request(api_details)
            logger.debug(f"First response received for hmac_merch_cred api is : {response}")
            response_merch_creds = response1.text.replace("\n", "")

            sub_string1 = "MerchantCreds="
            sub_string2 = "HMAC="

            index1 = response_merch_creds.index(sub_string1)
            index2 = response_merch_creds.index(sub_string2)
            generated_merch_creds = response_merch_creds[index1 + len(sub_string1): index2]
            logger.debug(f"Generated MerchCreds is : {generated_merch_creds}")

            api_details = DBProcessor.get_api_details('hmac_merch_cred', request_body=
            {"MerchantCredential": generated_merch_creds,
             "ResCode": ResCode,
             "HMAC": req_hmac,
             "Amount": amount,
             "PayeeVirAddr": db_upi_config_vpa,
             "MerchantID": db_upi_config_mid,
             "OrgCustRefId": orig_cust_ref_id,
             "OrgTxnRefId": res_generateqr_publish_id,
             "TerminalID": db_upi_config_tid, })
            response2 = APIProcessor.send_request(api_details)
            response_hmac = response2.text

            res = response_hmac.split('HMAC=', 1)
            generated_hmac = res[1]

            logger.debug(f"Second response received : {str(response_hmac)}")
            logger.debug(f"Value of HMAC is : {generated_hmac}")

            req_payload3 = {"MerchantCredential": generated_merch_creds,
                            "ResCode": ResCode,
                            "HMAC": generated_hmac,
                            "Amount": amount,
                            "PayeeVirAddr": db_upi_config_vpa,
                            "MerchantID": db_upi_config_mid,
                            "OrgCustRefId": orig_cust_ref_id,
                            "OrgTxnRefId": res_generateqr_publish_id,
                            "TerminalID": db_upi_config_tid,
                            }

            # UPI Callback
            api_details = DBProcessor.get_api_details('staticQR_UPI_IDFC_callback', request_body=req_payload3)
            response = APIProcessor.send_request(api_details)

            logger.debug(f"Response received for staticQR_UPI_IDFC_callback api is : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                orig_cust_ref_id) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")

            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")

            orig_txn_id = result["id"].iloc[0]
            auth_code = result['auth_code'].values[0]
            created_time_orig_txn = result["created_time"].values[0]

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
            auth_code_new_2 = result['auth_code'].values[0]
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
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "rrn": str(orig_cust_ref_id),
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
                home_page.check_home_page_logo()
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
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(orig_txn_id)

                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_rrn_original}")
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
                app_order_id_original = transactions_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id_original}")
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
                    "rrn": str(orig_cust_ref_id),
                    "acquirer_code": "IDFC",
                    "issuer_code": "IDFC",
                    "txn_type": "CHARGE",
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "org_code": org_code,
                    "acquirer_code_2": "IDFC",
                    "txn_type_2": "REFUND",
                    "mid_2": db_upi_config_mid,
                    "tid_2": db_upi_config_tid,
                    "org_code_2": org_code,
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
                    "acquirer_code": "IDFC",
                    "bank_code": "IDFC",
                    "payment_gateway": "IDFC_FDC",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "IDFC",
                    "upi_mc_id": db_upi_config_id,
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(refund_amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "IDFC",
                    "payment_gateway_2": "IDFC_FDC",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "IDFC",
                    "upi_mc_id_2": db_upi_config_id,
                    "mid_2": db_upi_config_mid,
                    "tid_2": db_upi_config_tid

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
