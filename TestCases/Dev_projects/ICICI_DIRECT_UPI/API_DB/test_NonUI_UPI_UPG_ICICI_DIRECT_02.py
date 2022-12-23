import random
import sys
from datetime import datetime

import pytest

from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d102_101_037():
    """
    Sub Feature Code: NonUI_Common_PM_UPI_UPG_REFUNDED_Via_API_when_UPGRefund_&_UPGAutoRefund_Enabled_ICICI_DIRECT
    Sub Feature Description: Performing a upg txn using upi success callback when upg refund and upg auto refund is
    enabled and refund the same txn using api via ICICI DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 101:- UPI, 037:- TC037
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
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

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result for upi_merchant_config table is : {result}")
            upi_mc_id = result['id'].values[0]
            logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
            virtual_tid = result['virtual_tid'].values[0]
            logger.debug(f"fetched virtual_tid : {virtual_tid}")
            virtual_mid = result['virtual_mid'].values[0]
            logger.debug(f"fetched virtual_mid : {virtual_mid}")
            vpa = result['vpa'].values[0]
            logger.debug(f"fetched vpa : {vpa}")

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating upi qr : {response}")
            txn_id = str(response["txnId"]).split('E')[0] + 'E' + str(random.randint(111111111, 999999999))
            logger.debug(f"Fetching txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            rrn = txn_id.split('E')[1]
            logger.debug(f"generated random rrn number to perform first callback is : {rrn}")

            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid, "subMerchantId": virtual_mid, "terminalId": virtual_tid,
                "PayerAmount": str(amount), "BankRRN": rrn, "merchantTranId": str(txn_id), "PayerVA": str(vpa)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + txn_id + "';")
            logger.debug(f"query to fetch data from invalid_pg_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            ipr_txn_id = result['txn_id'].iloc[0]
            logger.debug(f"fetched txn_id is : {ipr_txn_id}")

            query = "select * from txn where id = '" + str(ipr_txn_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")

            logger.debug(f"performing refund for the txn_id : {ipr_txn_id}")
            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "amount": amount, "originalTransactionId": str(ipr_txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")
            txn_id_2 = response['txnId']
            logger.debug(f"fetching txn id from the response after triggering the refund api is : {txn_id_2}")

            query = "select * from txn where id = '" + str(txn_id_2) + "';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref_2 = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {rrn_2}")

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
                refund_date = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "UPG_AUTH_REFUNDED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "UPG_REFUNDED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": txn_type, "mid": virtual_mid, "tid": virtual_tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "UPG_REFUNDED",
                    "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "UPG_REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "txn_type_2": txn_type_2, "mid_2": virtual_mid, "tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date_2": refund_date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == ipr_txn_id][0]
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
                elements = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {elements}")
                refund_status_api = elements["status"]
                refund_amount_api = float(elements["amount"])
                refund_payment_mode_api = elements["paymentMode"]
                refund_state_api = elements["states"][0]
                refund_settlement_status_api = elements["settlementStatus"]
                refund_acquirer_code_api = elements["acquirerCode"]
                refund_orgCode_api = elements["orgCode"]
                refund_mid_api = elements["mid"]
                refund_tid_api = elements["tid"]
                refund_txn_type_api = elements["txnType"]
                refund_date_api = elements["createdTime"]

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
                    "pmt_status_2": refund_status_api,
                    "txn_amt_2": refund_amount_api, "pmt_mode_2": refund_payment_mode_api,
                    "pmt_state_2": refund_state_api,
                    "settle_status_2": refund_settlement_status_api,
                    "acquirer_code_2": refund_acquirer_code_api,
                    "txn_type_2": refund_txn_type_api, "mid_2": refund_mid_api, "tid_2": refund_tid_api,
                    "org_code_2": refund_orgCode_api,
                    "date_2": date_time_converter.from_api_to_datetime_format(refund_date_api)
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
                    "pmt_status": "UPG_AUTH_REFUNDED",
                    "pmt_state": "UPG_REFUNDED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "upi_txn_status": "UPG_AUTH_REFUNDED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "ICICI",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": float(amount),
                    "ipr_mid": virtual_mid,
                    "ipr_tid": virtual_tid,
                    "ipr_vpa": vpa,
                    "ipr_config_id": upi_mc_id,
                    "rrn": str(rrn),
                    "pmt_status_2": "UPG_REFUNDED",
                    "pmt_state_2": "UPG_REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "upi_txn_status_2": "UPG_REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": virtual_mid,
                    "tid_2": virtual_tid,
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = "select * from txn where id='" + ipr_txn_id + "'"
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
                rrn_db = result['rr_number'].values[0]
                issuer_code = result['issuer_code'].values[0]

                query = "select * from upi_txn where txn_id='" + ipr_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = ("select * from invalid_pg_request where request_id ='" + txn_id + "';")
                logger.debug(f"query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                ipr_payment_mode = result["payment_mode"].iloc[0]
                ipr_bank_code = result["bank_code"].iloc[0]
                ipr_org_code = result["org_code"].iloc[0]
                ipr_amount = result["amount"].iloc[0]
                ipr_rrn = result["rrn"].iloc[0]
                ipr_mid = result["mid"].iloc[0]
                ipr_tid = result["tid"].iloc[0]
                ipr_config_id = result["config_id"].iloc[0]
                ipr_vpa = result["vpa"].iloc[0]

                query = "select * from txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                refund_status_db = result["status"].iloc[0]
                refund_payment_mode_db = result["payment_mode"].iloc[0]
                refund_amount_db = float(result["amount"].iloc[0])
                refund_state_db = result["state"].iloc[0]
                refund_payment_gateway_db = result["payment_gateway"].iloc[0]
                refund_acquirer_code_db = result["acquirer_code"].iloc[0]
                refund_settlement_status_db = result["settlement_status"].iloc[0]
                refund_tid_db = result['tid'].values[0]
                refund_mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                refund_upi_status_db = result["status"].iloc[0]
                refund_upi_txn_type_db = result["txn_type"].iloc[0]
                refund_upi_bank_code_db = result["bank_code"].iloc[0]
                refund_upi_mc_id_db = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
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
                    "rrn": str(rrn_db),
                    "pmt_status_2": refund_status_db,
                    "pmt_state_2": refund_state_db,
                    "pmt_mode_2": refund_payment_mode_db,
                    "txn_amt_2": refund_amount_db,
                    "upi_txn_status_2": refund_upi_status_db,
                    "settle_status_2": refund_settlement_status_db,
                    "acquirer_code_2": refund_acquirer_code_db,
                    "pmt_gateway_2": refund_payment_gateway_db,
                    "upi_txn_type_2": refund_upi_txn_type_db,
                    "upi_bank_code_2": refund_upi_bank_code_db,
                    "upi_mc_id_2": refund_upi_mc_id_db,
                    "mid_2": refund_mid_db,
                    "tid_2": refund_tid_db,
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
