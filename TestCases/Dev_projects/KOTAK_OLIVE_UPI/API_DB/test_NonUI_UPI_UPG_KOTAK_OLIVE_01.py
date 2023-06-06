import random
import sys
from datetime import datetime

import pytest

from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, \
    APIProcessor, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d103_101_009():
    """
    Sub Feature Code: NonUI_Common_UPI_Amt_Mismatch_Through_Success_Callback_KOTAK_OLIVE
    Sub Feature Description: Generate QR through api and perform amount mismatch through success callback for UPI txn
    of KOTAK_OLIVE pg
    TC naming code description: d103: Dev Project[KOTAK_OLIVE_UPI], 101-> UPI, 009->TC009
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_OLIVE', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_OLIVE'"
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = f"select * from ezetap_properties where entity='KOTAK_OLIVE' AND prop_key='trIdStaticValue';"
            logger.debug(f"Query to fetch prop_value from ezetap_properties table for entity: KOTAK_OLIVE and prop_key:"
                         f"trIdStaticValue")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            prop_value = result['prop_value'].iloc[0]
            logger.debug(f"fetching prop_value is : {prop_value}")

            amount = random.randint(300, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating qr : {response}")
            txn_id = response["txnId"]
            tr_in_qrcode_uri = f"KMBM{prop_value}00{txn_id}"
            logger.debug(
                f"Fetching txn_id and tr_id from the API_OUTPUT, txn_id : {txn_id} and tr_id : {tr_in_qrcode_uri}")

            rrn = datetime.now().strftime('%m%d%H%M%S%f')[:-4]
            dt, micro = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
            transaction_timestamp = "%s.%03d" % (dt, int(micro) / 1000)
            logger.debug(f"generated rrn and transaction_timestamp is : {rrn} and {transaction_timestamp}")
            logger.debug(f"changing amount to perform the amount mismatch using callback")
            amount = amount + 1
            api_details = DBProcessor.get_api_details('upi_confirm_kotakolive', request_body={
                "transactionid": tr_in_qrcode_uri,
                "aggregatorcode": "",
                "merchantcode": mid,
                "status": "SUCCESS",
                "statusCode": "00",
                "description": "Testing",
                "remarks": "Testing",
                "transactionreferencenumber": rrn,
                "rrn": rrn,
                "amount": amount,
                "type": "UPI",
                "payervpa": "customervpa",
                "payeevpa": vpa,
                "refid": rrn,
                "transactionTimestamp": transaction_timestamp
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for upi_confirm_kotakolive callback api is : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + txn_id + "';")
            logger.debug(f"query to fetch txn data from the invalid_pg_request table : {query}")
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
            logger.debug(f"Query to fetch ipr_txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
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
            txn_type_db = result['txn_type'].values[0]
            error_msg_db = result['error_message'].values[0]
            rrn_db = result['rr_number'].values[0]

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time_2 = result['created_time'].values[0]
            status_db_2 = result["status"].iloc[0]
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            amount_db_2 = float(result["amount"].iloc[0])
            state_db_2 = result["state"].iloc[0]
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            bank_code_db_2 = result["bank_code"].iloc[0]
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            tid_db_2 = result['tid'].values[0]
            mid_db_2 = result['mid'].values[0]
            txn_type_db_2 = result['txn_type'].values[0]
            error_msg_db_2 = result['error_message'].values[0]

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
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": 'CHARGE', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "PENDING",
                    "txn_amt_2": float(amount-1), "pmt_mode_2": "UPI",
                    "pmt_state_2": "PENDING",
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "KOTAK",
                    "issuer_code_2": "KOTAK",
                    "txn_type_2": 'CHARGE', "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response_list = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response_list}")
                response = [x for x in response_list["txns"] if x["txnId"] == ipr_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                response = [x for x in response_list["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_2 = response["status"]
                amount_api_2 = float(response["amount"])
                payment_mode_api_2 = response["paymentMode"]
                state_api_2 = response["states"][0]
                settlement_status_api_2 = response["settlementStatus"]
                issuer_code_api_2 = response["issuerCode"]
                acquirer_code_api_2 = response["acquirerCode"]
                org_code_api_2 = response["orgCode"]
                mid_api_2 = response["mid"]
                tid_api_2 = response["tid"]
                txn_type_api_2 = response["txnType"]
                date_api_2 = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2, "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
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
                    "pmt_status": "UPG_AUTHORIZED",
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "txn_type":"CHARGE",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "OLIVE",
                    "error_msg": None,
                    "mid": mid,
                    "tid": tid,
                    "upi_txn_ref": tr_in_qrcode_uri,
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "KOTAK_OLIVE",
                    "upi_mc_id": upi_mc_id,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "KOTAK",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": "customervpa",
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                    "rrn": str(rrn),
                    "ipr_error_message": f"The given amount - {amount} doesnt match with the transaction amount.",
                    "pmt_status_2": "PENDING",
                    "pmt_state_2": "PENDING",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount-1),
                    "settle_status_2": "PENDING",
                    "txn_type_2": "CHARGE",
                    "acquirer_code_2": "KOTAK",
                    "bank_code_2": "KOTAK",
                    "pmt_gateway_2": "OLIVE",
                    "error_msg_2": None,
                    "mid_2": mid,
                    "tid_2": tid,
                    "tr_in_qrcode_uri": True,
                    "upi_txn_status_2": "PENDING",
                    "upi_txn_type_2": "PAY_QR",
                    "upi_bank_code_2": "KOTAK_OLIVE",
                    "upi_mc_id_2": upi_mc_id,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + ipr_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_txn_ref_db = result["txn_ref"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]
                upi_qrcode_uri_db = result["qrcode_uri"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "txn_type": txn_type_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "error_msg" : error_msg_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "upi_txn_ref": str(upi_txn_ref_db),
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
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
                    "ipr_error_message": str(ipr_error_message),
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt_2": amount_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "txn_type_2": txn_type_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "error_msg_2": error_msg_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "tr_in_qrcode_uri": tr_in_qrcode_uri in str(upi_qrcode_uri_db),
                    "upi_txn_status_2": upi_status_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

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
def test_d103_101_010():
    """
    Sub Feature Code: NonUI_Common_UPI_UPG_Authorized_KOTAK_OLIVE
    Sub Feature Description: Performing UPI UPG Authorized txn of KOTAK_OLIVE pg
    TC naming code description: d103: Dev Project[KOTAK_OLIVE_UPI], 101-> UPI, 010->TC010
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_OLIVE', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_OLIVE'"
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = f"select * from ezetap_properties where entity='KOTAK_OLIVE' AND prop_key='trIdStaticValue';"
            logger.debug(f"Query to fetch prop_value from ezetap_properties table for entity: KOTAK_OLIVE and prop_key:"
                         f"trIdStaticValue")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            prop_value = result['prop_value'].iloc[0]
            logger.debug(f"fetching prop_value is : {prop_value}")

            amount = random.randint(300, 1000)

            txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            tr_in_qrcode_uri = f"KMBM{prop_value}00{txn_id}"
            logger.debug(f"random and uniquely generated txn_id : {txn_id} and tr_id : {tr_in_qrcode_uri}")

            rrn = datetime.now().strftime('%m%d%H%M%S%f')[:-4]
            dt, micro = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
            transaction_timestamp = "%s.%03d" % (dt, int(micro) / 1000)
            logger.debug(f"generated rrn and transaction_timestamp is : {rrn} and {transaction_timestamp}")

            api_details = DBProcessor.get_api_details('upi_confirm_kotakolive', request_body={
                "transactionid": tr_in_qrcode_uri,
                "aggregatorcode": "",
                "merchantcode": mid,
                "status": "SUCCESS",
                "statusCode": "00",
                "description": "Testing",
                "remarks": "Testing",
                "transactionreferencenumber": rrn,
                "rrn": rrn,
                "amount": amount,
                "type": "UPI",
                "payervpa": "customervpa",
                "payeevpa": vpa,
                "refid": rrn,
                "transactionTimestamp": transaction_timestamp
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for upi_confirm_kotakolive callback api is : {response}")

            query = ("select * from invalid_pg_request where pg_txn_ref ='" + tr_in_qrcode_uri + "';")
            logger.debug(f"query to fetch txn data from the invalid_pg_request table : {query}")
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
            logger.debug(f"Query to fetch ipr_txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
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
            txn_type_db = result['txn_type'].values[0]
            error_msg_db = result['error_message'].values[0]
            rrn_db = result['rr_number'].values[0]

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
                expected_api_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": 'CHARGE', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response_list = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response_list}")
                response = [x for x in response_list["txns"] if x["txnId"] == ipr_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": org_code_api,
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
                    "pmt_status": "UPG_AUTHORIZED",
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "txn_type":"CHARGE",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "OLIVE",
                    "error_msg": None,
                    "mid": mid,
                    "tid": tid,
                    "upi_txn_ref": tr_in_qrcode_uri,
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "KOTAK_OLIVE",
                    "upi_mc_id": upi_mc_id,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "KOTAK",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": "customervpa",
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                    "rrn": str(rrn),
                    "ipr_error_message": f"UPI Txn Id Tampered {tr_in_qrcode_uri}"

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + ipr_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_txn_ref_db = result["txn_ref"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "txn_type": txn_type_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "error_msg" : error_msg_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "upi_txn_ref": str(upi_txn_ref_db),
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
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
                    "ipr_error_message": str(ipr_error_message)
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

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
