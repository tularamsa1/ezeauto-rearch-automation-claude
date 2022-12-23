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
def test_d102_102_004():
    """
    Sub Feature Code: NonUI_Common_BQRV4_BQR_ICICI_Direct_Success_Callback
    Sub Feature Description: Generate QR through api and perform success callback for BQRV4 BQR txn of ICICI_Direct pg
    TC naming code description: d102->Dev Project[ICICI_DIRECT_UPI], 102-> BQRV4 BQR, 004->TC004
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
                                            portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        logger.debug(f"Fetching mid,tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid},{terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(500, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqrv4 qr for the amount of {amount} and order id is {order_id}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password,
                "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating qr : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Auth code and rrn for current txn is : {auth_code}, {rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": 'CHARGE', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "BHARATQR",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "txn_type":"CHARGE",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "error_msg": None,
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_status": "Transaction Success", "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "bqr_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                    "bqr_merchant_pan": bqr_m_pan,
                    "bqr_rrn": str(rrn),
                    "bqr_org_code": org_code,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
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
                txn_type_db = result['txn_type'].values[0]
                error_msg_db = result['error_message'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

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
                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db, "bqr_org_code": bqr_org_code_db
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
def test_d102_102_005():
    """
    Sub Feature Code: NonUI_Common_BQRV4_BQR_ICICI_Direct_Failed_Callback
    Sub Feature Description: Generate QR through api and perform failed callback for BQRV4 BQR txn of ICICI_Direct pg
    TC naming code description:d102->Dev Project[ICICI_DIRECT_UPI], 102-> BQRV4 BQR, 005->TC005
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
                                                portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        logger.debug(f"Fetching mid,tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid,tid,terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(101, 200)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqrv4 qr for the amount of {amount} and order id is {order_id}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating qr : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"auth_code and rrn for txn is : {auth_code, rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id, "STATUS_CODE": "02",
                                                                    "STATUS_DESC": "FAILED",
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": 'CHARGE', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
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

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
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
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "BHARATQR",
                    "txn_amt": float(amount),
                    "settle_status": "FAILED",
                    "txn_type":"CHARGE",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "error_msg": "Bharat QR Transaction Failed: ",
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
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
                txn_type_db = result['txn_type'].values[0]
                error_msg_db = str(result['error_message'].values[0])

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
def test_d102_102_034():
    """
    Sub Feature Code: NonUI_Common_BQRV4_BQR_ICICI_Direct_Duplicate_Success_Callback_same_rrn
    Sub Feature Description: Generate QR through api and perform two success callback with same rrn for
    BQRV4 BQR txn of ICICI_Direct pg
    TC naming code description: d102->Dev Project[ICICI_DIRECT_UPI], 102-> BQRV4 BQR, 034->TC034
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
                                                portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        logger.debug(f"Fetching terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(500, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqrv4 qr for the amount of {amount} and order id is {order_id}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating qr : {response}")
            txn_id = response["txnId"]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN from data base : Txn_id : {txn_id},"
                f" Auth code : {auth_code}, RRN : {rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")

            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            txn_id_2 = response["TXN_ID"]
            logger.debug(f"Fetching txnid 2 from api output of callback:{txn_id_2}")
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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": 'CHARGE', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "txn_id": txn_id_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
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
                txn_id_api  = response["txnId"]

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
                    "txn_id": txn_id_api
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "txn_type":"CHARGE",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "error_msg": None,
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_status": "Transaction Success", "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "bqr_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_org_code": org_code,
                    "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id_2,
                    "bqr_merchant_pan": bqr_m_pan,
                    "bqr_rrn": str(rrn)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
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
                txn_type_db = result['txn_type'].values[0]
                error_msg_db = result['error_message'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]

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
                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db
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
def test_d102_102_035():
    """
    Sub Feature Code: NonUI_Common_BQRV4_BQR_ICICI_Direct_Duplicate_Success_Callback_different_rrn_AutoRefund_Enabled
    Sub Feature Description: Generate QR through api and perform two success callback with diffrent rrn
    when auto refund enabled for BQRV4 BQR txn of ICICI_Direct pg
    TC naming code description:d102->Dev Project[ICICI_DIRECT_UPI], 102-> BQRV4 BQR, 035->TC035
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
                                                portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
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

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        logger.debug(f"Fetching mid,tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid},{terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(501, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqrv4 qr for the amount of {amount} and order id is {order_id}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating qr : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT : {txn_id}")

            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Auth code and rrn for txn is : {auth_code, rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            txn_id_callback = 'T'+ txn_id[1:]
            logger.debug(f"txn id for performing second callback is : {txn_id_callback}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id_callback,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code_2}")
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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": 'CHARGE', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": float(amount), "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "REFUND_PENDING", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": 'CHARGE', "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
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

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_2 = response["status"]
                amount_api_2 = float(response["amount"])
                payment_mode_api_2 = response["paymentMode"]
                state_api_2 = response["states"][0]
                rrn_api_2 = response["rrNumber"]
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
                    "pmt_status_2": status_api_2, "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "txn_type":"CHARGE",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "error_msg": None,
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_status": "Transaction Success", "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "bqr_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_org_code": org_code,
                    "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                    "bqr_merchant_pan": bqr_m_pan,
                    "bqr_rrn": str(rrn),
                    "pmt_status_2": "REFUND_PENDING",
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": float(amount),
                    "settle_status_2": "SETTLED",
                    "txn_type_2": "CHARGE",
                    "acquirer_code_2": "HDFC",
                    "bank_code_2": "HDFC",
                    "pmt_gateway_2": "HDFC",
                    "error_msg_2": None,
                    "mid_2": mid,
                    "tid_2": tid,
                    "bqr_pmt_status_2": "Transaction Success", "bqr_pmt_state_2": "REFUND_PENDING",
                    "bqr_txn_amt_2": float(amount),
                    "bqr_txn_type_2": "DYNAMIC_QR", "bqr_terminal_info_id_2": terminal_info_id,
                    "bqr_bank_code_2": "HDFC",
                    "bqr_org_code_2": org_code,
                    "bqr_merchant_config_id_2": bqr_mc_id, "bqr_txn_primary_id_2": txn_id_2,
                    "bqr_merchant_pan_2": bqr_m_pan,
                    "bqr_rrn_2": str(rrn_2),
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
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
                txn_type_db = result['txn_type'].values[0]
                error_msg_db = result['error_message'].values[0]

                query = "select * from txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
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

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_2 = result["status_desc"].iloc[0]
                bqr_state_db_2 = result["state"].iloc[0]
                bqr_amount_db_2 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_2 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_2 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_2 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_2 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_2 = result['org_code'].values[0]
                bqr_merchant_pan_db_2 = result["merchant_pan"].iloc[0]
                bqr_rrn_db_2 = result['rrn'].values[0]

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
                    "error_msg": error_msg_db,
                    "mid": mid_db,
                    "tid": tid_db,
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
                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_pmt_status_2": bqr_status_db_2, "bqr_pmt_state_2": bqr_state_db_2,
                    "bqr_txn_amt_2": bqr_amount_db_2,
                    "bqr_txn_type_2": bqr_txn_type_db_2, "bqr_terminal_info_id_2": bqr_terminal_info_id_db_2,
                    "bqr_bank_code_2": bqr_bank_code_db_2,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_2,
                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_2,
                    "bqr_org_code_2": bqr_org_code_db_2,
                    "bqr_merchant_pan_2": bqr_merchant_pan_db_2,
                    "bqr_rrn_2": bqr_rrn_db_2,
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
def test_d102_102_036():
    """
    Sub Feature Code: NonUI_Common_BQRV4_BQR_ICICI_Direct_Duplicate_Success_Callback_different_rrn_AutoRefund_Disabled
    Sub Feature Description: Generate QR through api and perform two success callback with different rrn when
    auto refund enabled for BQRV4 BQR txn of ICICI_Direct pg
    TC naming code description: d102->Dev Project[ICICI_DIRECT_UPI], 102-> BQRV4 BQR, 036->TC036
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
                                                portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        logger.debug(f"Fetching mid,tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid},{terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(501, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqrv4 qr for the amount of {amount} and order id is {order_id}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating qr : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT : {txn_id}")

            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Auth code and rrn for current txn is : {auth_code, rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            txn_id_callback = 'T'+ txn_id[1:]
            logger.debug(f"Txn id for performing second callback is : {txn_id_callback} ")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id_callback,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"fetched txn id from txn table is : {txn_id_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code_2}")
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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": 'CHARGE', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount), "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "SETTLED", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": 'CHARGE', "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
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

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_2 = response["status"]
                amount_api_2 = float(response["amount"])
                payment_mode_api_2 = response["paymentMode"]
                state_api_2 = response["states"][0]
                rrn_api_2 = response["rrNumber"]
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
                    "pmt_status_2": status_api_2, "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "txn_type":"CHARGE",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "error_msg": None,
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_status": "Transaction Success", "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR", "bqr_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_org_code": org_code,
                    "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                    "bqr_merchant_pan": bqr_m_pan,
                    "bqr_rrn": str(rrn),
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": float(amount),
                    "settle_status_2": "SETTLED",
                    "txn_type_2": "CHARGE",
                    "acquirer_code_2": "HDFC",
                    "bank_code_2": "HDFC",
                    "pmt_gateway_2": "HDFC",
                    "error_msg_2": None,
                    "mid_2": mid,
                    "tid_2": tid,
                    "bqr_pmt_status_2": "Transaction Success", "bqr_pmt_state_2": "SETTLED",
                    "bqr_txn_amt_2": float(amount),
                    "bqr_txn_type_2": "DYNAMIC_QR", "bqr_terminal_info_id_2": terminal_info_id,
                    "bqr_bank_code_2": "HDFC",
                    "bqr_org_code_2": org_code,
                    "bqr_merchant_config_id_2": bqr_mc_id, "bqr_txn_primary_id_2": txn_id_2,
                    "bqr_merchant_pan_2": bqr_m_pan,
                    "bqr_rrn_2": str(rrn_2),
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
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
                txn_type_db = result['txn_type'].values[0]
                error_msg_db = result['error_message'].values[0]

                query = "select * from txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
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

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_2 = result["status_desc"].iloc[0]
                bqr_state_db_2 = result["state"].iloc[0]
                bqr_amount_db_2 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_2 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_2 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_2 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_2 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_2 = result['org_code'].values[0]
                bqr_merchant_pan_db_2 = result["merchant_pan"].iloc[0]
                bqr_rrn_db_2 = result['rrn'].values[0]

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
                    "error_msg": error_msg_db,
                    "mid": mid_db,
                    "tid": tid_db,
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
                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_pmt_status_2": bqr_status_db_2, "bqr_pmt_state_2": bqr_state_db_2,
                    "bqr_txn_amt_2": bqr_amount_db_2,
                    "bqr_txn_type_2": bqr_txn_type_db_2, "bqr_terminal_info_id_2": bqr_terminal_info_id_db_2,
                    "bqr_bank_code_2": bqr_bank_code_db_2,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_2,
                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_2,
                    "bqr_org_code_2": bqr_org_code_db_2,
                    "bqr_merchant_pan_2": bqr_merchant_pan_db_2,
                    "bqr_rrn_2": bqr_rrn_db_2,
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