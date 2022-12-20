import random
import sys
from datetime import datetime
import pytest
from Configuration import testsuite_teardown, Configuration
from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, date_time_converter, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d102_102_071():
    """
    Sub Feature Code: NonUI_Common_BQRV4_BQR_ICICI_Direct_UPG_Refund_Success_Amt_mismatch_Upg_Autorefund_disabled
    Sub Feature Description: Generate QR through api and perform upg success refund for BQRV4 BQR amount mismatch of ICICI_Direct pg
    TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 102->BQRV4 BQR, 071-> Tesctcase ID
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4',
                                                           bank_code_bqr='HDFC')

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

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(
            f"Response received for setting preconditions upgRefundEnabled enabled and upgAutoRefundEnabled disabled is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                                                       "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        merchant_id = result["visa_merchant_id_primary"].iloc[0]

        logger.debug(f"Fetching mid, tid, terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid},{tid},{terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # -----------------------------Start of Test Execution------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.choice([51, 52, 53, 54])
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")

            # Generate QR
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating qr : {response}")
            txn_id = response["txnId"]
            orig_auth_code = "AE" + txn_id.split('E')[1]
            orig_rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN from data base : Txn_id : {txn_id},"
                f" Auth code : {orig_auth_code}, RRN : {orig_rrn}")

            # Do callback
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id,
                                                                    "AUTH_CODE": orig_auth_code, "RRN": orig_rrn,
                                                                    "MERCHANT_PAN": merchant_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for callback : {response}")
            query = ("select * from invalid_pg_request where request_id ='" + txn_id + "';")
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_upg = result['txn_id'].values[0]
            logger.debug(f"fetched upg_txn_id from txn table is : {txn_id_upg}")
            query = "select * from txn where id = '" + txn_id_upg + "';"
            logger.debug(f"Query to fetch txn details from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn_db = result['rr_number'].values[0]
            org_code_db = result['org_code'].values[0]
            created_time_db = result['created_time'].values[0]
            auth_code_db = result['auth_code'].values[0]

            logger.debug(f"fetched upg_txn_id from txn table is : {txn_id_upg}")
            logger.debug(f"fetched rrn from txn table is : {rrn_db}")
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_db}")
            logger.debug(f"fetched created_time from txn table is : {created_time_db}")
            logger.debug(f"fetched auth_code from txn table is : {auth_code_db}")

            # Do refund for UPG txn
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id_upg)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for  refund api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and orig_txn_id ='" + str(txn_id_upg) + "' "
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)

            refunded_txn_id = result["id"].iloc[0]
            refund_created_time_db = result['created_time'].values[0]

            logger.debug(f"Fetching Refund txn_id from db query : {refunded_txn_id} ")

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
                date = date_time_converter.db_datetime(created_time_db)
                date_2 = date_time_converter.db_datetime(refund_created_time_db)

                expected_api_values = {
                    "pmt_status": "UPG_AUTH_REFUNDED",
                    "pmt_status_2": "UPG_REFUNDED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_mode_2": "BHARATQR",
                    "pmt_state": "UPG_REFUNDED",
                    "pmt_state_2": "UPG_REFUNDED",
                    "rrn": str(orig_rrn),
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "txn_type_2": "REFUND",
                    "mid": mid,
                    "mid_2": mid,
                    "tid": tid,
                    "tid_2": tid,
                    "org_code": org_code,
                    "org_code_2": org_code,
                    "date": date,
                    "date_2": date_2
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response1 = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")

                response = [x for x in response1["txns"] if x["txnId"] == txn_id_upg][0]
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

                response = [x for x in response1["txns"] if x["txnId"] == refunded_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

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
                    "pmt_status": status_api,
                     "pmt_status_2": status_api_refunded,
                     "txn_amt": amount_api,
                     "txn_amt_2": amount_api_refunded,
                     "pmt_mode": payment_mode_api,
                     "pmt_mode_2": payment_mode_api_refunded,
                     "pmt_state": state_api,
                     "pmt_state_2": state_api_refunded,
                     "rrn": str(rrn_api),
                     "settle_status": settlement_status_api,
                     "settle_status_2": settlement_status_api_refunded,
                     "acquirer_code": acquirer_code_api,
                     "acquirer_code_2": acquirer_code_api_refunded,
                     "issuer_code": issuer_code_api,
                     "mid": mid_api,
                     "mid_2": mid_api_refunded,
                     "txn_type": txn_type_api,
                     "txn_type_2": txn_type_api_refunded,
                     "tid": tid_api,
                     "tid_2": tid_api_refunded,
                     "org_code": org_code_api,
                     "org_code_2": org_code_api_refunded,
                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
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
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_status": "UPG_AUTH_REFUNDED",
                    "pmt_state": "UPG_REFUNDED",
                    "acquirer_code": "HDFC",
                    "bank_name": "HDFC Bank",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "HDFC",
                    "rrn": str(orig_rrn),
                    "settle_status": "SETTLED",
                    "bqr_pmt_status": "success",
                    "bqr_pmt_state": "UPG_REFUNDED",
                    "bqr_txn_amt": float(amount),
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id,
                    "bqr_txn_primary_id": txn_id_upg,
                    "bqr_merchant_pan": merchant_id,
                    "bqr_rrn": str(orig_rrn),
                    "bqr_org_code": org_code,
                    "ipr_auth_code": orig_auth_code,
                    "ipr_pmt_mode": "BHARATQR",
                    "ipr_bank_code": "HDFC",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(orig_rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_config_id": bqr_mc_id,
                    "ipr_pg_merchant_id": merchant_id,
                }
                query = "select * from txn where id='" + txn_id_upg + "'"
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
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id_upg + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = ("select * from invalid_pg_request where request_id ='" + txn_id + "';")
                logger.debug(f"query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                ipr_payment_mode = result["payment_mode"].iloc[0]
                ipr_bank_code = result["bank_code"].iloc[0]
                ipr_org_code = result["org_code"].iloc[0]
                ipr_amount = result["amount"].iloc[0]
                ipr_rrn = result["rrn"].iloc[0]
                ipr_auth_code = result["auth_code"].iloc[0]
                ipr_mid = result["mid"].iloc[0]
                ipr_tid = result["tid"].iloc[0]
                ipr_config_id = result["config_id"].iloc[0]
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_name": bank_name_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rr_number_db,
                    "settle_status": settlement_status_db,
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_auth_code": ipr_auth_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
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