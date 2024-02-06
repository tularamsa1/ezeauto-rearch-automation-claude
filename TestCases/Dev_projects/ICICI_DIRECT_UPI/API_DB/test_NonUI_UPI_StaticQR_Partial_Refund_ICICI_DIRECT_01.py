import random
import sys
from datetime import datetime
import pytest

from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d102_107_010():
    """
    Sub Feature Code: NonUI_Common_UPI_StaticQR_ICICI_Direct_Partial_Refund_Via_API
    Sub Feature Description: Initiate upi static QR via api and perform a partial refund using api for ICICI_DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 107: Static QR UPI, 010: TC010
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched virtual_tid : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            logger.info("generating upi static qr via icici direct")
            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "upiMerchantConfigId": str(upi_mc_id),
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            success_api = response["success"]
            username_api = response["username"]
            org_code_api = response["merchantCode"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

            amount = random.randint(301, 1000)
            rrn = str(random.randint(100000000000, 999999999999))
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid, "subMerchantId": virtual_mid, "terminalId": virtual_tid,
                "PayerAmount": str(amount),
                "BankRRN": rrn, "merchantTranId": str(publish_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and rr_number = '" + str(
                rrn) + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {rrn}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")

            refund_amount = amount - 100.00
            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": refund_amount, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            refund_txn_id = response['txnId']
            logger.debug(f"fetched txn_id_refunded from txn table is : {refund_txn_id}")
            logger.debug(f"Response received for paymentRefund api is : {response}")

            query = "select * from txn where id='" + refund_txn_id + "';"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            refund_rrn = result['rr_number'].iloc[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched refund_customer_name from txn table is : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched refund_payer_name from txn table is : {refund_payer_name}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")
            refund_external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched refund_external_ref from txn table is : {refund_external_ref}")

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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
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
                    "customer_name_2": refund_customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": refund_payer_name,
                    "order_id": external_ref,
                    "order_id_2": refund_external_ref,
                    "rrn": str(rrn),
                    "rrn_2": str(refund_rrn),
                    "acquirer_code": "ICICI",
                    "acquirer_code_2": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": txn_type,
                    "mid": virtual_mid, "tid": virtual_tid,
                    "org_code": org_code,
                    "txn_type_2": refund_txn_type,
                    "mid_2": virtual_mid, "tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date": date,
                    "date_2": refund_date,
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
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
                order_id_api_original = response["orderNumber"]
                customer_name_api = response["customerName"]
                payer_name_api = response["payerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = float(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                rrn_api_refunded = response["rrNumber"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["createdTime"]
                order_id_api_refunded = response["orderNumber"]
                customer_name_api_refunded = response["customerName"]
                payer_name_api_refunded = response["payerName"]

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
                    "customer_name": customer_name_api,
                    "customer_name_2": customer_name_api_refunded,
                    "payer_name": payer_name_api,
                    "payer_name_2": payer_name_api_refunded,
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
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
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(refund_amount),
                    "order_id": external_ref,
                    "order_id_2": refund_external_ref,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "ICICI",
                    "error_msg": None,
                    "error_msg_2": None,
                    "acquirer_code_2": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "mid_2": virtual_mid,
                    "tid_2": virtual_tid,
                    "rrn": rrn
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = result["amount"].iloc[0]
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]
                order_id_db_refunded = result['external_ref'].values[0]
                error_msg_db_refunded = result['error_message'].values[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = result["amount"].iloc[0]
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]
                order_id_db_original = result['external_ref'].values[0]
                error_msg_db_original = result['error_message'].values[0]
                rrn_db_original = result['rr_number'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
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
                    "error_msg": error_msg_db_original,
                    "error_msg_2": error_msg_db_refunded,
                    "rrn": rrn_db_original
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
def test_d102_107_011():
    """
    Sub Feature Code: NonUI_Common_UPI_StaticQR_ICICI_Direct_Partial_Refund_Failed_Via_API
    Sub Feature Description: Initiate upi static QR via api and perform partial refund failed using api for ICICI_DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 107: Static QR UPI, 011: TC011
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched virtual_tid : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            logger.info("generating upi static qr via icici direct")
            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "upiMerchantConfigId": str(upi_mc_id),
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            success_api = response["success"]
            username_api = response["username"]
            org_code_api = response["merchantCode"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

            amount = random.randint(301, 1000)
            rrn = str(random.randint(100000000000, 999999999999))
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid, "subMerchantId": virtual_mid, "terminalId": virtual_tid,
                "PayerAmount": str(amount),
                "BankRRN": rrn, "merchantTranId": str(publish_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and rr_number = '" + str(
                rrn) + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            logger.debug(f"Result for the query {query} is : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {rrn}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")

            refund_amount = 201.01
            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": refund_amount, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            refund_txn_id = response['txnId']
            logger.debug(f"fetched txn_id_refunded from txn table is : {refund_txn_id}")
            logger.debug(f"Response received for paymentRefund api is : {response}")

            query = "select * from txn where id='" + refund_txn_id + "';"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            refund_rrn = result['rr_number'].iloc[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched refund_customer_name from txn table is : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched refund_payer_name from txn table is : {refund_payer_name}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")
            refund_external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched refund_external_ref from txn table is : {refund_external_ref}")

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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "FAILED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "FAILED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "FAILED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": refund_customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": refund_payer_name,
                    "order_id": external_ref,
                    "order_id_2": refund_external_ref,
                    "rrn": str(rrn),
                    "acquirer_code": "ICICI",
                    "acquirer_code_2": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": txn_type,
                    "mid": virtual_mid, "tid": virtual_tid,
                    "org_code": org_code,
                    "txn_type_2": refund_txn_type,
                    "org_code_2": org_code,
                    "date": date,
                    "date_2": refund_date,
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
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
                order_id_api_original = response["orderNumber"]
                customer_name_api = response["customerName"]
                payer_name_api = response["payerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = float(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["createdTime"]
                order_id_api_refunded = response["orderNumber"]
                customer_name_api_refunded = response["customerName"]
                payer_name_api_refunded = response["payerName"]

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
                    "customer_name": customer_name_api,
                    "customer_name_2": customer_name_api_refunded,
                    "payer_name": payer_name_api,
                    "payer_name_2": payer_name_api_refunded,
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
                    "org_code_2": org_code_api_refunded,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
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
                    "pmt_status_2": "FAILED",
                    "pmt_state_2": "FAILED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(refund_amount),
                    "order_id": external_ref,
                    "order_id_2": refund_external_ref,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "FAILED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "FAILED",
                    "acquirer_code": "ICICI",
                    "error_msg": None,
                    "error_msg_2": None,
                    "acquirer_code_2": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "rrn": rrn
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = result["amount"].iloc[0]
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                order_id_db_refunded = result['external_ref'].values[0]
                error_msg_db_refunded = result['error_message'].values[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = result["amount"].iloc[0]
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]
                order_id_db_original = result['external_ref'].values[0]
                error_msg_db_original = result['error_message'].values[0]
                rrn_db_original = result['rr_number'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
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
                    "error_msg": error_msg_db_original,
                    "error_msg_2": error_msg_db_refunded,
                    "rrn": rrn_db_original
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
def test_d102_107_012():
    """
    Sub Feature Code: NonUI_Common_UPI_StaticQR_ICICI_Direct_Partial_Refund_via_api_amount_greater_than_original_amount
    Sub Feature Description: Initiate upi static QR via api and performing UPI partial refund via api when partial
    refund amount is greater than original amount for ICICI_DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 107: Static QR UPI, 012: TC012
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched virtual_tid : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            logger.info("generating upi static qr via icici direct")
            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "upiMerchantConfigId": str(upi_mc_id),
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            success_api = response["success"]
            username_api = response["username"]
            org_code_api = response["merchantCode"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

            amount = 300
            rrn = str(random.randint(100000000000, 999999999999))
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid, "subMerchantId": virtual_mid, "terminalId": virtual_tid,
                "PayerAmount": str(amount),
                "BankRRN": rrn, "merchantTranId": str(publish_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and rr_number = '" + str(
                rrn) + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")

            refund_amount = 150
            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username, "password": app_password, "amount": refund_amount,
                "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")
            refund_txn_id = response['txnId']
            logger.debug(f"fetching refund txn_id from the response is : {refund_txn_id}")

            query = "select * from txn where id='" + refund_txn_id + "';"
            logger.debug(f"Query to fetch refunded txn data from txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query : {query} is {result}")
            refund_rrn = result['rr_number'].iloc[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id_refunded from txn table is : {refund_txn_id}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")
            refund_external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched refund_external_ref from txn table is : {refund_external_ref}")

            greater_refund_amount = 151
            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password, "amount": greater_refund_amount,
                "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(
                f"Response received from refund api when refund amount is greater than original amount : {response}")
            api_error_message = response["errorMessage"]

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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.db_datetime(created_time)
                refund_date_and_time = date_time_converter.db_datetime(refund_created_time)
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
                    "order_id": external_ref,
                    "order_id_2": refund_external_ref,
                    "rrn": str(rrn),
                    "rrn_2": str(refund_rrn),
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": txn_type,
                    "mid": virtual_mid, "tid": virtual_tid,
                    "org_code": org_code,
                    "acquirer_code_2": "ICICI",
                    "txn_type_2": refund_txn_type,
                    "mid_2": virtual_mid, "tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date": date_and_time,
                    "date_2": refund_date_and_time,
                    "err_msg": f"Transaction declined. Amount entered is more than maximum allowed for the transaction. Maximum Allowed: 150.00"
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                elements = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {elements}")
                status_api_original = elements["status"]
                amount_api_original = float(elements["amount"])
                payment_mode_api_original = elements["paymentMode"]
                rrn_api_original = elements["rrNumber"]
                state_api_original = elements["states"][0]
                settlement_status_api_original = elements["settlementStatus"]
                issuer_code_api_original = elements["issuerCode"]
                acquirer_code_api_original = elements["acquirerCode"]
                org_code_api_original = elements["orgCode"]
                mid_api_original = elements["mid"]
                tid_api_original = elements["tid"]
                txn_type_api_original = elements["txnType"]
                date_api_original = elements["createdTime"]
                order_id_api_original = elements["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                elements = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {elements}")
                status_api_refunded = elements["status"]
                amount_api_refunded = float(elements["amount"])
                payment_mode_api_refunded = elements["paymentMode"]
                rrn_api_refunded = elements["rrNumber"]
                state_api_refunded = elements["states"][0]
                settlement_status_api_refunded = elements["settlementStatus"]
                acquirer_code_api_refunded = elements["acquirerCode"]
                org_code_api_refunded = elements["orgCode"]
                mid_api_refunded = elements["mid"]
                tid_api_refunded = elements["tid"]
                txn_type_api_refunded = elements["txnType"]
                date_api_refunded = elements["createdTime"]
                order_id_api_refunded = elements["orderNumber"]

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
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
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
                    "err_msg": api_error_message
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
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
                    "txn_amt": float(amount),
                    "txn_amt_2": float(refund_amount),
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "ICICI",
                    "acquirer_code_2": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "mid_2": virtual_mid,
                    "tid_2": virtual_tid,
                    "order_id": external_ref,
                    "order_id_2": refund_external_ref,
                    "rrn": rrn
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + refund_txn_id + "'"
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
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]
                order_id_db_refunded = result['external_ref'].values[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id + "'"
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
                order_id_db_original = result['external_ref'].values[0]
                rrn_db_original = result['rr_number'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
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
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                    "order_id": order_id_db_original,
                    "order_id_2": order_id_db_refunded,
                    "rrn": rrn_db_original,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
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
def test_d102_107_013():
    """
    Sub Feature Code: NonUI_Common_UPI_StaticQR_ICICI_Direct_Partial_Refund_In_Decimal_Via_API
    Sub Feature Description: Initiate upi static QR via api and perform a partial refund in decimal using api for
    ICICI_DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 107: Static QR UPI, 013: TC013
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched virtual_tid : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            logger.info("generating upi static qr via icici direct")
            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "upiMerchantConfigId": str(upi_mc_id),
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            success_api = response["success"]
            username_api = response["username"]
            org_code_api = response["merchantCode"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

            amount = random.randint(301, 1000)
            rrn = str(random.randint(100000000000, 999999999999))
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid, "subMerchantId": virtual_mid, "terminalId": virtual_tid,
                "PayerAmount": str(amount),
                "BankRRN": rrn, "merchantTranId": str(publish_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and rr_number = '" + str(
                rrn) + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")

            refund_amount = amount - 100.55
            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": refund_amount, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")
            refund_txn_id = response['txnId']
            logger.debug(f"fetching refund txn_id from the response is : {refund_txn_id}")

            query = "select * from txn where id='" + refund_txn_id + "' and orig_txn_id ='" + str(txn_id) + "';"
            logger.debug(f"Query to fetch refund txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"result for the query : {query} is : {result}")
            refund_rrn = result['rr_number'].iloc[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched refund_customer_name from txn table is : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched refund_payer_name from txn table is : {refund_payer_name}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched refund_org_code_txn from txn table is : {refund_org_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")
            refund_external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched refund_external_ref from txn table is : {refund_external_ref}")

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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
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
                    "customer_name_2": refund_customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": refund_payer_name,
                    "order_id": external_ref,
                    "order_id_2": refund_external_ref,
                    "rrn": str(rrn),
                    "rrn_2": str(refund_rrn),
                    "acquirer_code": "ICICI",
                    "acquirer_code_2": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": txn_type,
                    "mid": virtual_mid, "tid": virtual_tid,
                    "org_code": org_code,
                    "txn_type_2": refund_txn_type,
                    "mid_2": virtual_mid, "tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date": date,
                    "date_2": refund_date,
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
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
                order_id_api_original = response["orderNumber"]
                customer_name_api = response["customerName"]
                payer_name_api = response["payerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = float(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                rrn_api_refunded = response["rrNumber"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["createdTime"]
                order_id_api_refunded = response["orderNumber"]
                customer_name_api_refunded = response["customerName"]
                payer_name_api_refunded = response["payerName"]

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
                    "customer_name": customer_name_api,
                    "customer_name_2": customer_name_api_refunded,
                    "payer_name": payer_name_api,
                    "payer_name_2": payer_name_api_refunded,
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
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
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(refund_amount),
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "ICICI",
                    "error_msg": None,
                    "error_msg_2": None,
                    "acquirer_code_2": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "mid_2": virtual_mid,
                    "tid_2": virtual_tid,
                    "rrn": rrn,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = result["amount"].iloc[0]
                state_db_refunded = result["state"].iloc[0]
                payment_gateway_db_refunded = result["payment_gateway"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]
                error_msg_db_refunded = result['error_message'].values[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = result["amount"].iloc[0]
                state_db_original = result["state"].iloc[0]
                payment_gateway_db_original = result["payment_gateway"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]
                tid_db_original = result['tid'].values[0]
                mid_db_original = result['mid'].values[0]
                error_msg_db_original = result['error_message'].values[0]
                rrn_db_original = result['rr_number'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
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
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                    "error_msg": error_msg_db_original,
                    "error_msg_2": error_msg_db_refunded,
                    "rrn": rrn_db_original,
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
def test_d102_107_014():
    """
    Sub Feature Code: NonUI_Common_UPI_StaticQR_ICICI_Direct_2_times_successful_Partial_Refund_Via_API
    Sub Feature Description: Initiate upi static QR via api and perform two times partial refund using api for ICICI_DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 107: Static QR UPI, 014: TC014
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched virtual_tid : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            logger.info("generating upi static qr via icici direct")
            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "upiMerchantConfigId": str(upi_mc_id),
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            success_api = response["success"]
            username_api = response["username"]
            org_code_api = response["merchantCode"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

            amount = 250
            partial_refunded_amount = 150
            full_refund_amount = 100

            rrn = str(random.randint(100000000000, 999999999999))
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid, "subMerchantId": virtual_mid, "terminalId": virtual_tid,
                "PayerAmount": str(amount),
                "BankRRN": rrn, "merchantTranId": str(publish_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and rr_number = '" + str(
                rrn) + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching original_customer_name from txn table : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching original_payer_name from txn table : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching original_auth_code from txn table : {auth_code} ")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching original_txn_type from txn table : {txn_type} ")
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_date_time from txn table : {created_date_time} ")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": partial_refunded_amount, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")
            partial_refund_txn_id_1 = response["txnId"]
            logger.debug(
                f"Fetching txn_id from the response of paymentRefund api, partial_refund_txn_id_1 : {partial_refund_txn_id_1}")

            query = "select * from txn where id = '" + str(partial_refund_txn_id_1) + "';"
            logger.debug(f"Query to fetch txn data of first partial refund from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            partial_refund_auth_code_1 = result['auth_code'].values[0]
            logger.debug(f"Fetching partial_refund_auth_code_1 from txn table : {partial_refund_auth_code_1} ")
            partial_refund_txn_type_1 = result['txn_type'].values[0]
            logger.debug(f"Fetching partial_refund_txn_type_1 from txn table : {partial_refund_txn_type_1} ")
            partial_refund_rrn_1 = result['rr_number'].iloc[0]
            logger.debug(f"Fetching partial_refund_rrn_1 from txn table : {partial_refund_rrn_1} ")
            partial_refund_created_date_time_1 = result['created_time'].values[0]
            logger.debug(
                f"Fetching partial_refund_created_date_time_1 from txn table : {partial_refund_created_date_time_1} ")
            partial_refund_customer_name_1 = result['customer_name'].values[0]
            logger.debug(f"Fetching partial_refund_customer_name_1 from txn table : {partial_refund_customer_name_1} ")
            partial_refund_payer_name_1 = result['payer_name'].values[0]
            logger.debug(f"Fetching partial_refund_payer_name_1 from txn table : {partial_refund_payer_name_1} ")
            partial_refund_external_ref_1 = result['external_ref'].values[0]
            logger.debug(f"fetched partial_refund_external_ref_1 from txn table is : {partial_refund_external_ref_1}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": full_refund_amount, "originalTransactionId": str(txn_id)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")
            partial_refund_txn_id_2 = response["txnId"]
            logger.debug(
                f"Fetching txn_id from the response of paymentRefund api, partial_refund_txn_id_2 : {partial_refund_txn_id_2}")

            query = "select * from txn where id = '" + str(partial_refund_txn_id_2) + "';"
            logger.debug(f"Query to fetch txn data of 2nd partial refund from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            partial_refund_auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching partial_refund_auth_code_2 from txn table : {partial_refund_auth_code_2} ")
            partial_refund_txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching partial_refund_txn_type_2 from txn table : {partial_refund_txn_type_2} ")
            partial_refund_rrn_2 = result['rr_number'].iloc[0]
            logger.debug(f"Fetching partial_refund_rrn_2 from txn table : {partial_refund_rrn_2} ")
            partial_refund_created_date_time_2 = result['created_time'].values[0]
            logger.debug(
                f"Fetching partial_refund_created_date_time_2 from txn table : {partial_refund_created_date_time_2} ")
            partial_refund_customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching partial_refund_customer_name_2 from txn table : {partial_refund_customer_name_2} ")
            partial_refund_payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching partial_refund_payer_name_2 from txn table : {partial_refund_payer_name_2} ")
            partial_refund_external_ref_2 = result['external_ref'].values[0]
            logger.debug(f"fetched partial_refund_external_ref_2 from txn table is : {partial_refund_external_ref_2}")

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
                    "txn_amt": float(amount),
                    "txn_amt_2": float(partial_refunded_amount),
                    "txn_amt_3": float(full_refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": partial_refund_customer_name_1,
                    "customer_name_3": partial_refund_customer_name_2,
                    "payer_name": payer_name,
                    "payer_name_2": partial_refund_payer_name_1,
                    "payer_name_3": partial_refund_payer_name_2,
                    "order_id": external_ref,
                    "order_id_2": partial_refund_external_ref_1,
                    "order_id_3": partial_refund_external_ref_2,
                    "rrn": str(rrn),
                    "rrn_2": str(partial_refund_rrn_1),
                    "rrn_3": str(partial_refund_rrn_2),
                    "date": date_and_time,
                    "date_2": partial_refund_date_and_time_1,
                    "date_3": partial_refund_date_and_time_2,
                    "acquirer_code": "ICICI",
                    "acquirer_code_2": "ICICI",
                    "acquirer_code_3": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": txn_type,
                    "txn_type_2": partial_refund_txn_type_1,
                    "txn_type_3": partial_refund_txn_type_2,
                    "mid": virtual_mid, "tid": virtual_tid,
                    "mid_2": virtual_mid, "tid_2": virtual_tid,
                    "mid_3": virtual_mid, "tid_3": virtual_tid,
                    "org_code": org_code,
                    "org_code_2": org_code,
                    "org_code_3": org_code,
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                elements = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {elements}")

                status_api_original = elements["status"]
                amount_api_original = float(elements["amount"])
                payment_mode_api_original = elements["paymentMode"]
                rrn_api_original = elements["rrNumber"]
                state_api_original = elements["states"][0]
                settlement_status_api_original = elements["settlementStatus"]
                issuer_code_api_original = elements["issuerCode"]
                acquirer_code_api_original = elements["acquirerCode"]
                org_code_api_original = elements["orgCode"]
                mid_api_original = elements["mid"]
                tid_api_original = elements["tid"]
                txn_type_api_original = elements["txnType"]
                date_api_original = elements["createdTime"]
                order_id_api_original = elements["orderNumber"]
                customer_name_api_original = elements["customerName"]
                payer_name_api_original = elements["payerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                elements = [x for x in response["txns"] if x["txnId"] == partial_refund_txn_id_1][0]
                logger.debug(f"Response after filtering data of current txn is : {elements}")

                partial_refund_status_api_1 = elements["status"]
                partial_refund_amount_api_1 = float(elements["amount"])
                partial_refund_payment_mode_api_1 = elements["paymentMode"]
                partial_refund_rrn_api_1 = elements["rrNumber"]
                partial_refund_state_api_1 = elements["states"][0]
                partial_refund_settle_status_api_1 = elements["settlementStatus"]
                partial_refund_acquirer_code_api_1 = elements["acquirerCode"]
                partial_refund_org_code_api_1 = elements["orgCode"]
                partial_refund_mid_api_1 = elements["mid"]
                partial_refund_tid_api_1 = elements["tid"]
                partial_refund_txn_type_api_1 = elements["txnType"]
                partial_refund_date_api_1 = elements["createdTime"]
                partial_refund_order_id_api_1 = elements["orderNumber"]
                partial_refund_customer_name_api_1 = elements["customerName"]
                partial_refund_payer_name_api_1 = elements["payerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                elements = [x for x in response["txns"] if x["txnId"] == partial_refund_txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {elements}")

                partial_refund_status_api_2 = elements["status"]
                partial_refund_amount_api_2 = float(elements["amount"])
                partial_refund_payment_mode_api_2 = elements["paymentMode"]
                partial_refund_rrn_api_2 = elements["rrNumber"]
                partial_refund_state_api_2 = elements["states"][0]
                partial_refund_settle_status_api_2 = elements["settlementStatus"]
                partial_refund_acquirer_code_api_2 = elements["acquirerCode"]
                partial_refund_org_code_api_2 = elements["orgCode"]
                partial_refund_mid_api_2 = elements["mid"]
                partial_refund_tid_api_2 = elements["tid"]
                partial_refund_txn_type_api_2 = elements["txnType"]
                partial_refund_date_api_2 = elements["createdTime"]
                partial_refund_order_id_api_2 = elements["orderNumber"]
                partial_refund_customer_name_api_2 = elements["customerName"]
                partial_refund_payer_name_api_2 = elements["payerName"]

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
                    "txn_amt": amount_api_original,
                    "txn_amt_2": partial_refund_amount_api_1,
                    "txn_amt_3": partial_refund_amount_api_2,
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
                    "rrn_2": str(partial_refund_rrn_api_1),
                    "rrn_3": str(partial_refund_rrn_api_2),
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
                    "mid": mid_api_original, "tid": tid_api_original,
                    "mid_2": partial_refund_mid_api_1, "tid_2": partial_refund_tid_api_1,
                    "mid_3": partial_refund_mid_api_2, "tid_3": partial_refund_tid_api_2,
                    "org_code": org_code_api_original,
                    "org_code_2": partial_refund_org_code_api_1,
                    "org_code_3": partial_refund_org_code_api_2,
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
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
                    "txn_amt": float(amount),
                    "txn_amt_2": float(partial_refunded_amount),
                    "txn_amt_3": float(full_refund_amount),
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_status_3": "REFUNDED",
                    "acquirer_code": "ICICI",
                    "acquirer_code_2": "ICICI",
                    "acquirer_code_3": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "pmt_gateway_3": "ICICI",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_txn_type_3": "REFUND",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_bank_code_3": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "upi_mc_id_3": upi_mc_id,
                    "mid": virtual_mid, "tid": virtual_tid,
                    "mid_2": virtual_mid, "tid_2": virtual_tid,
                    "mid_3": virtual_mid, "tid_3": virtual_tid,
                    "rrn": rrn,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = result["amount"].iloc[0]
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                rrn_db = result['rr_number'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + partial_refund_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_status_db_1 = result["status"].iloc[0]
                partial_refund_payment_mode_db_1 = result["payment_mode"].iloc[0]
                partial_refund_amount_db_1 = result["amount"].iloc[0]
                partial_refund_state_db_1 = result["state"].iloc[0]
                partial_refund_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                partial_refund_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                partial_refund_settlement_status_db_1 = result["settlement_status"].iloc[0]
                partial_refund_tid_db_1 = result['tid'].values[0]
                partial_refund_mid_db_1 = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + partial_refund_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_upi_status_db_1 = result["status"].iloc[0]
                partial_refund_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                partial_refund_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                partial_refund_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + partial_refund_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_status_db_2 = result["status"].iloc[0]
                partial_refund_payment_mode_db_2 = result["payment_mode"].iloc[0]
                partial_refund_amount_db_2 = result["amount"].iloc[0]
                partial_refund_state_db_2 = result["state"].iloc[0]
                partial_refund_payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                partial_refund_acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                partial_refund_settlement_status_db_2 = result["settlement_status"].iloc[0]
                partial_refund_tid_db_2 = result['tid'].values[0]
                partial_refund_mid_db_2 = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + partial_refund_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_upi_status_db_2 = result["status"].iloc[0]
                partial_refund_upi_txn_type_db_2 = result["txn_type"].iloc[0]
                partial_refund_upi_bank_code_db_2 = result["bank_code"].iloc[0]
                partial_refund_upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

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
                    "txn_amt": float(amount_db),
                    "txn_amt_2": float(partial_refund_amount_db_1),
                    "txn_amt_3": float(partial_refund_amount_db_2),
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
                    "mid": mid_db, "tid": tid_db,
                    "mid_2": partial_refund_mid_db_1, "tid_2": partial_refund_tid_db_1,
                    "mid_3": partial_refund_mid_db_2, "tid_3": partial_refund_tid_db_2,
                    "rrn": rrn_db,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
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
def test_d102_107_015():
    """
    Sub Feature Code: NonUI_Common_UPI_StaticQR_ICICI_Direct_First_refund_whole_amt_and_2nd_with_decimal_Via_API
    Sub Feature Description: Initiate upi static QR via api and perform two times partial refund (First refund whole amt
    and second with decimal) using api for ICICI_DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 107: Static QR UPI, 015: TC015
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched virtual_tid : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 250
            partial_refunded_amount = 150
            full_refund_amount = 98.05

            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            logger.info("generating upi static qr via icici direct")
            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "upiMerchantConfigId": str(upi_mc_id),
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            success_api = response["success"]
            username_api = response["username"]
            org_code_api = response["merchantCode"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

            rrn = str(random.randint(100000000000, 999999999999))
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid, "subMerchantId": virtual_mid, "terminalId": virtual_tid,
                "PayerAmount": str(amount),
                "BankRRN": rrn, "merchantTranId": str(publish_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and rr_number = '" + str(
                rrn) + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching original_customer_name from txn table : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching original_payer_name from txn table : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching original_auth_code from txn table : {auth_code} ")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching original_txn_type from txn table : {txn_type} ")
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_date_time from txn table : {created_date_time} ")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": partial_refunded_amount, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")
            partial_refund_txn_id_1 = response["txnId"]
            logger.debug(
                f"Fetching txn_id from the response of paymentRefund api, partial_refund_txn_id_1 : {partial_refund_txn_id_1}")

            query = "select * from txn where id = '" + str(partial_refund_txn_id_1) + "';"
            logger.debug(f"Query to fetch txn data of first partial refund from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            partial_refund_auth_code_1 = result['auth_code'].values[0]
            logger.debug(f"Fetching partial_refund_auth_code_1 from txn table : {partial_refund_auth_code_1} ")
            partial_refund_txn_type_1 = result['txn_type'].values[0]
            logger.debug(f"Fetching partial_refund_txn_type_1 from txn table : {partial_refund_txn_type_1} ")
            partial_refund_rrn_1 = result['rr_number'].iloc[0]
            logger.debug(f"Fetching partial_refund_rrn_1 from txn table : {partial_refund_rrn_1} ")
            partial_refund_created_date_time_1 = result['created_time'].values[0]
            logger.debug(
                f"Fetching partial_refund_created_date_time_1 from txn table : {partial_refund_created_date_time_1} ")
            partial_refund_customer_name_1 = result['customer_name'].values[0]
            logger.debug(f"Fetching partial_refund_customer_name_1 from txn table : {partial_refund_customer_name_1} ")
            partial_refund_payer_name_1 = result['payer_name'].values[0]
            logger.debug(f"Fetching partial_refund_payer_name_1 from txn table : {partial_refund_payer_name_1} ")
            partial_refund_external_ref_1 = result['external_ref'].values[0]
            logger.debug(f"fetched partial_refund_external_ref_1 from txn table is : {partial_refund_external_ref_1}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": full_refund_amount, "originalTransactionId": str(txn_id)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")
            partial_refund_txn_id_2 = response["txnId"]
            logger.debug(
                f"Fetching txn_id from the response of paymentRefund api, partial_refund_txn_id_2 : {partial_refund_txn_id_2}")

            query = "select * from txn where id = '" + str(partial_refund_txn_id_2) + "';"
            logger.debug(f"Query to fetch txn data of 2nd partial refund from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result for the query {query} is : {result}")
            partial_refund_auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching partial_refund_auth_code_2 from txn table : {partial_refund_auth_code_2} ")
            partial_refund_txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching partial_refund_txn_type_2 from txn table : {partial_refund_txn_type_2} ")
            partial_refund_rrn_2 = result['rr_number'].iloc[0]
            logger.debug(f"Fetching partial_refund_rrn_2 from txn table : {partial_refund_rrn_2} ")
            partial_refund_created_date_time_2 = result['created_time'].values[0]
            logger.debug(
                f"Fetching partial_refund_created_date_time_2 from txn table : {partial_refund_created_date_time_2} ")
            partial_refund_customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching partial_refund_customer_name_2 from txn table : {partial_refund_customer_name_2} ")
            partial_refund_payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching partial_refund_payer_name_2 from txn table : {partial_refund_payer_name_2} ")
            partial_refund_external_ref_2 = result['external_ref'].values[0]
            logger.debug(f"fetched partial_refund_external_ref_2 from txn table is : {partial_refund_external_ref_2}")

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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.db_datetime(created_date_time)
                partial_refund_date_and_time_1 = date_time_converter.db_datetime(partial_refund_created_date_time_1)
                partial_refund_date_and_time_2 = date_time_converter.db_datetime(partial_refund_created_date_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_status_3": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "pmt_mode_3": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "settle_status_3": "SETTLED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state_3": "REFUNDED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(partial_refunded_amount),
                    "txn_amt_3": float(full_refund_amount),
                    "customer_name": customer_name,
                    "customer_name_2": partial_refund_customer_name_1,
                    "customer_name_3": partial_refund_customer_name_2,
                    "payer_name": payer_name,
                    "payer_name_2": partial_refund_payer_name_1,
                    "payer_name_3": partial_refund_payer_name_2,
                    "order_id": external_ref,
                    "order_id_2": partial_refund_external_ref_1,
                    "order_id_3": partial_refund_external_ref_2,
                    "rrn": str(rrn),
                    "rrn_2": str(partial_refund_rrn_1),
                    "rrn_3": str(partial_refund_rrn_2),
                    "date": date_and_time,
                    "date_2": partial_refund_date_and_time_1,
                    "date_3": partial_refund_date_and_time_2,
                    "acquirer_code": "ICICI",
                    "acquirer_code_2": "ICICI",
                    "acquirer_code_3": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": txn_type,
                    "txn_type_2": partial_refund_txn_type_1,
                    "txn_type_3": partial_refund_txn_type_2,
                    "mid": virtual_mid, "tid": virtual_tid,
                    "mid_2": virtual_mid, "tid_2": virtual_tid,
                    "mid_3": virtual_mid, "tid_3": virtual_tid,
                    "org_code": org_code,
                    "org_code_2": org_code,
                    "org_code_3": org_code,
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                elements = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {elements}")

                status_api_original = elements["status"]
                amount_api_original = float(elements["amount"])
                payment_mode_api_original = elements["paymentMode"]
                rrn_api_original = elements["rrNumber"]
                state_api_original = elements["states"][0]
                settlement_status_api_original = elements["settlementStatus"]
                issuer_code_api_original = elements["issuerCode"]
                acquirer_code_api_original = elements["acquirerCode"]
                org_code_api_original = elements["orgCode"]
                mid_api_original = elements["mid"]
                tid_api_original = elements["tid"]
                txn_type_api_original = elements["txnType"]
                date_api_original = elements["createdTime"]
                order_id_api_original = elements["orderNumber"]
                customer_name_api_original = elements["customerName"]
                payer_name_api_original = elements["payerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                elements = [x for x in response["txns"] if x["txnId"] == partial_refund_txn_id_1][0]
                logger.debug(f"Response after filtering data of current txn is : {elements}")

                partial_refund_status_api_1 = elements["status"]
                partial_refund_amount_api_1 = float(elements["amount"])
                partial_refund_payment_mode_api_1 = elements["paymentMode"]
                partial_refund_rrn_api_1 = elements["rrNumber"]
                partial_refund_state_api_1 = elements["states"][0]
                partial_refund_settle_status_api_1 = elements["settlementStatus"]
                partial_refund_acquirer_code_api_1 = elements["acquirerCode"]
                partial_refund_org_code_api_1 = elements["orgCode"]
                partial_refund_mid_api_1 = elements["mid"]
                partial_refund_tid_api_1 = elements["tid"]
                partial_refund_txn_type_api_1 = elements["txnType"]
                partial_refund_date_api_1 = elements["createdTime"]
                partial_refund_order_id_api_1 = elements["orderNumber"]
                partial_refund_customer_name_api_1 = elements["customerName"]
                partial_refund_payer_name_api_1 = elements["payerName"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                elements = [x for x in response["txns"] if x["txnId"] == partial_refund_txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {elements}")

                partial_refund_status_api_2 = elements["status"]
                partial_refund_amount_api_2 = float(elements["amount"])
                partial_refund_payment_mode_api_2 = elements["paymentMode"]
                partial_refund_rrn_api_2 = elements["rrNumber"]
                partial_refund_state_api_2 = elements["states"][0]
                partial_refund_settle_status_api_2 = elements["settlementStatus"]
                partial_refund_acquirer_code_api_2 = elements["acquirerCode"]
                partial_refund_org_code_api_2 = elements["orgCode"]
                partial_refund_mid_api_2 = elements["mid"]
                partial_refund_tid_api_2 = elements["tid"]
                partial_refund_txn_type_api_2 = elements["txnType"]
                partial_refund_date_api_2 = elements["createdTime"]
                partial_refund_order_id_api_2 = elements["orderNumber"]
                partial_refund_customer_name_api_2 = elements["customerName"]
                partial_refund_payer_name_api_2 = elements["payerName"]

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
                    "txn_amt": amount_api_original,
                    "txn_amt_2": partial_refund_amount_api_1,
                    "txn_amt_3": partial_refund_amount_api_2,
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
                    "rrn_2": str(partial_refund_rrn_api_1),
                    "rrn_3": str(partial_refund_rrn_api_2),
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
                    "mid": mid_api_original, "tid": tid_api_original,
                    "mid_2": partial_refund_mid_api_1, "tid_2": partial_refund_tid_api_1,
                    "mid_3": partial_refund_mid_api_2, "tid_3": partial_refund_tid_api_2,
                    "org_code": org_code_api_original,
                    "org_code_2": partial_refund_org_code_api_1,
                    "org_code_3": partial_refund_org_code_api_2,
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_status_3": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "pmt_mode_3": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "settle_status_3": "SETTLED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state_3": "REFUNDED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(partial_refunded_amount),
                    "txn_amt_3": float(full_refund_amount),
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_status_3": "REFUNDED",
                    "acquirer_code": "ICICI",
                    "acquirer_code_2": "ICICI",
                    "acquirer_code_3": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "pmt_gateway_3": "ICICI",
                    "upi_txn_type": "STATIC_QR",
                    "upi_txn_type_2": "REFUND",
                    "upi_txn_type_3": "REFUND",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_bank_code_3": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "upi_mc_id_3": upi_mc_id,
                    "mid": virtual_mid, "tid": virtual_tid,
                    "mid_2": virtual_mid, "tid_2": virtual_tid,
                    "mid_3": virtual_mid, "tid_3": virtual_tid,
                    "rrn": rrn,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = result["amount"].iloc[0]
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                rrn_db = result['rr_number'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + partial_refund_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_status_db_1 = result["status"].iloc[0]
                partial_refund_payment_mode_db_1 = result["payment_mode"].iloc[0]
                partial_refund_amount_db_1 = result["amount"].iloc[0]
                partial_refund_state_db_1 = result["state"].iloc[0]
                partial_refund_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                partial_refund_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                partial_refund_settlement_status_db_1 = result["settlement_status"].iloc[0]
                partial_refund_tid_db_1 = result['tid'].values[0]
                partial_refund_mid_db_1 = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + partial_refund_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_upi_status_db_1 = result["status"].iloc[0]
                partial_refund_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                partial_refund_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                partial_refund_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + partial_refund_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_status_db_2 = result["status"].iloc[0]
                partial_refund_payment_mode_db_2 = result["payment_mode"].iloc[0]
                partial_refund_amount_db_2 = result["amount"].iloc[0]
                partial_refund_state_db_2 = result["state"].iloc[0]
                partial_refund_payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                partial_refund_acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                partial_refund_settlement_status_db_2 = result["settlement_status"].iloc[0]
                partial_refund_tid_db_2 = result['tid'].values[0]
                partial_refund_mid_db_2 = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + partial_refund_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                partial_refund_upi_status_db_2 = result["status"].iloc[0]
                partial_refund_upi_txn_type_db_2 = result["txn_type"].iloc[0]
                partial_refund_upi_bank_code_db_2 = result["bank_code"].iloc[0]
                partial_refund_upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

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
                    "txn_amt": float(amount_db),
                    "txn_amt_2": float(partial_refund_amount_db_1),
                    "txn_amt_3": float(partial_refund_amount_db_2),
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
                    "mid": mid_db, "tid": tid_db,
                    "mid_2": partial_refund_mid_db_1, "tid_2": partial_refund_tid_db_1,
                    "mid_3": partial_refund_mid_db_2, "tid_3": partial_refund_tid_db_2,
                    "rrn": rrn_db,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
