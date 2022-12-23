import random
import sys
import pytest
from Configuration import testsuite_teardown, Configuration
from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, date_time_converter, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d102_108_008():
    """
    Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Refund_Success_ICICI_DIRECT
    Sub Feature Description: Verification of a staticQR BQRV4 UPI Success Refund transaction via ICICI_DIRECT
    TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRV4 StaticQR, 008-> Tesctcase ID
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
        logger.info(f"fetched virtual_tid is : {virtual_tid}")

        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and " \
                                                                                       "bank_code='HDFC' "
        result = DBProcessor.getValueFromDB(query)
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Completed)------------------------------------
        # -----------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Call generate QR API
            api_details = DBProcessor.get_api_details('static_qrcode_generate_hdfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            username_api = response["username"]
            logger.debug(f"fetching publish_id, username from api response is : "f"{publish_id},{username_api}")

            amount = random.randint(225, 300)
            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            customer_name = "Automation user_1"
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI callback generator API
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn,
                "merchantTranId": merchant_tran_id,
                "TxnInitDate": "20221107153216",
                "TxnCompletionDate": "221123064745654",
                "PayerAmount": amount,
                "PayerName": customer_name,
                "PayerMobile": "0000000000",
                "PayerVA": "bhaisahab@icici",
                "TxnStatus": "SUCCESS"
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callbackgeneratorUpiICICI api is : {response}")

            # Call UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            orig_txn_id = response["merchantTranId"]

            # Call refund API
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "originalTransactionId": str(orig_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")

            refund_txn_id = response['txnId']

            query = "select * from txn where id = '" + str(orig_txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            orig_txn_amt = result['amount'].values[0]
            orig_acquirer_code = result['acquirer_code'].values[0]
            orig_bank_code = result['bank_code'].values[0]
            orig_issuer_code = result['issuer_code'].values[0]
            orig_pmt_gateway = result['payment_gateway'].values[0]
            orig_pmt_mode = result['payment_mode'].values[0]
            orig_settlement_status = result['settlement_status'].values[0]
            orig_status = result['status'].values[0]
            orig_txn_type = result['txn_type'].values[0]
            orig_bank_name = result['bank_name'].values[0]
            orig_state = result['state'].iloc[0]
            orig_tid = result['tid'].values[0]
            orig_mid = result['mid'].values[0]
            orig_rr_number = result['rr_number'].values[0]
            orig_created_time = result['created_time'].values[0]

            query = "select * from txn where id = '" + str(refund_txn_id) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            refund_txn_amt = result['amount'].values[0]
            refund_acquirer_code = result['acquirer_code'].values[0]
            refund_cust_name = result['customer_name'].values[0]
            refund_mid = result['mid'].values[0]
            refund_tid = result['tid'].values[0]
            refund_org_code = result['org_code'].values[0]
            refund_ref_txn_id = result['ref_txn_id'].values[0]
            refund_pmt_gateway = result['payment_gateway'].values[0]
            refund_pmt_mode = result['payment_mode'].values[0]
            refund_settlement_status = result['settlement_status'].values[0]
            refund_status = result['status'].values[0]
            refund_txn_type = result['txn_type'].values[0]
            refund_username = result['username'].values[0]
            refund_state = result['state'].iloc[0]
            refund_created_time = result['created_time'].values[0]

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
                date_original = date_time_converter.db_datetime(orig_created_time)
                date_refund = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "txn_amt": float(amount),
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "org_code": org_code,
                    "pmt_mode": "UPI",
                    "rrn": bank_rrn,
                    "settle_status": "SETTLED",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "txn_type": "CHARGE",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "date": date_original,
                    "txn_amt_2": float(amount),
                    "cust_name_2": customer_name,
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "orig_txn_id_2": orig_txn_id,
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "SETTLED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "txn_type_2": "REFUND",
                    "txn_type_desc_2": "Refund",
                    "acquirer_code_2": "ICICI",
                    "date_2": date_refund,
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

                orig_api_status = response["status"]
                orig_api_amount = float(response["amount"])
                orig_api_payment_mode = response["paymentMode"]
                orig_api_state = response["states"][0]
                orig_api_rrn = response["rrNumber"]
                orig_api_settlement_status = response["settlementStatus"]
                orig_api_issuer_code = response["issuerCode"]
                orig_api_acquirer_code = response["acquirerCode"]
                orig_api_org_code = response["orgCode"]
                orig_api_mid = response["mid"]
                orig_api_tid = response["tid"]
                orig_api_txn_type = response["txnType"]
                orig_api_date = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                refund_api_status = response["status"]
                refund_api_original_txn_id = response["origTxnId"]
                refund_api_cust_name = response["customerName"]
                refund_api_amount = float(response["amount"])
                refund_api_payment_mode = response["paymentMode"]
                refund_api_state = response["states"][0]
                refund_api_settlement_status = response["settlementStatus"]
                refund_api_acquirer_code = response["acquirerCode"]
                refund_api_org_code = response["orgCode"]
                refund_api_mid = response["mid"]
                refund_api_tid = response["tid"]
                refund_api_txn_type = response["txnType"]
                refund_api_txn_type_desc = response["txnTypeDesc"]
                refund_api_date = response["createdTime"]

                actual_api_values = {
                    "txn_amt": orig_api_amount,
                    "virtual_mid": orig_api_mid,
                    "virtual_tid": orig_api_tid,
                    "org_code": orig_api_org_code,
                    "pmt_mode": orig_api_payment_mode,
                    "rrn": orig_api_rrn,
                    "settle_status": orig_api_settlement_status,
                    "pmt_status": orig_api_status,
                    "pmt_state": orig_api_state,
                    "txn_type": orig_api_txn_type,
                    "acquirer_code": orig_api_acquirer_code,
                    "issuer_code": orig_api_issuer_code,
                    "date": date_time_converter.from_api_to_datetime_format(orig_api_date),
                    "txn_amt_2": refund_api_amount,
                    "cust_name_2": refund_api_cust_name,
                    "virtual_mid_2": refund_api_mid,
                    "virtual_tid_2": refund_api_tid,
                    "org_code_2": refund_api_org_code,
                    "orig_txn_id_2": refund_api_original_txn_id,
                    "pmt_mode_2": refund_api_payment_mode,
                    "settle_status_2": refund_api_settlement_status,
                    "pmt_status_2": refund_api_status,
                    "pmt_state_2": refund_api_state,
                    "txn_type_2": refund_api_txn_type,
                    "txn_type_desc_2": refund_api_txn_type_desc,
                    "acquirer_code_2": refund_api_acquirer_code,
                    "date_2": date_time_converter.from_api_to_datetime_format(refund_api_date),
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
                    "txn_amt": amount,
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "issuer_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_type": "CHARGE",
                    "bank_name": "ICICI Bank",
                    "pmt_state": "REFUNDED",
                    "virtual_tid": virtual_tid,
                    "virtual_mid": virtual_mid,
                    "rrn": bank_rrn,
                    "txn_amt_2": amount,
                    "acquirer_code_2": "ICICI",
                    "customer_name_2": customer_name,
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "ref_txn_id_2": orig_txn_id,
                    "pmt_gateway_2": "ICICI",
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "SETTLED",
                    "pmt_status_2": "REFUNDED",
                    "txn_type_2": "REFUND",
                    "username_2": app_username,
                    "pmt_state_2": "REFUNDED",
                    "upi_org_code": org_code,
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_mc_id": upi_mc_id,
                    "upi_txn_type": "STATIC_QR",
                    "upi_add_field1_2": publish_id,
                    "upi_add_field2_2": merchant_tran_id,
                    "upi_org_code_2": org_code,
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_status_2": "REFUNDED",
                    "upi_mc_id_2": upi_mc_id,
                    "upi_txn_type_2": "REFUND"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                orig_upi_org_code = result["org_code"].iloc[0]
                orig_upi_bank_code = result["bank_code"].iloc[0]
                orig_upi_status = result["status"].iloc[0]
                orig_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                orig_upi_txn_type = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                refund_upi_add_field1 = result["additional_field1"].iloc[0]
                refund_upi_add_field2 = result["additional_field2"].iloc[0]
                refund_upi_org_code = result["org_code"].iloc[0]
                refund_upi_bank_code = result["bank_code"].iloc[0]
                refund_upi_status = result["status"].iloc[0]
                refund_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                refund_upi_txn_type = result["txn_type"].iloc[0]

                actual_db_values = {
                    "txn_amt": orig_txn_amt,
                    "acquirer_code": orig_acquirer_code,
                    "bank_code": orig_bank_code,
                    "issuer_code": orig_issuer_code,
                    "pmt_gateway": orig_pmt_gateway,
                    "pmt_mode": orig_pmt_mode,
                    "settle_status": orig_settlement_status,
                    "pmt_status": orig_status,
                    "txn_type": orig_txn_type,
                    "bank_name": orig_bank_name,
                    "pmt_state": orig_state,
                    "virtual_tid": orig_tid,
                    "virtual_mid": orig_mid,
                    "rrn": orig_rr_number,
                    "txn_amt_2": refund_txn_amt,
                    "acquirer_code_2": refund_acquirer_code,
                    "customer_name_2": refund_cust_name,
                    "virtual_mid_2": refund_mid,
                    "virtual_tid_2": refund_tid,
                    "org_code_2": refund_org_code,
                    "ref_txn_id_2": refund_ref_txn_id,
                    "pmt_gateway_2": refund_pmt_gateway,
                    "pmt_mode_2": refund_pmt_mode,
                    "settle_status_2": refund_settlement_status,
                    "pmt_status_2": refund_status,
                    "txn_type_2": refund_txn_type,
                    "username_2": refund_username,
                    "pmt_state_2": refund_state,
                    "upi_org_code": orig_upi_org_code,
                    "upi_bank_code": orig_upi_bank_code,
                    "upi_txn_status": orig_upi_status,
                    "upi_mc_id": orig_upi_upi_mc_id,
                    "upi_txn_type": orig_upi_txn_type,
                    "upi_add_field1_2": refund_upi_add_field1,
                    "upi_add_field2_2": refund_upi_add_field2,
                    "upi_org_code_2": refund_upi_org_code,
                    "upi_bank_code_2": refund_upi_bank_code,
                    "upi_status_2": refund_upi_status,
                    "upi_mc_id_2": refund_upi_upi_mc_id,
                    "upi_txn_type_2": refund_upi_txn_type
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
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
def test_d102_108_009():
    """
     Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Refund_Failed_ICICI_DIRECT
     Sub Feature Description: Verification of a staticQR BQRV4 UPI failed Refund transaction via ICICI_DIRECT
     TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRV4 StaticQR, 009-> Testcase ID
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
        logger.info(f"fetched virtual_tid is : {virtual_tid}")

        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and " \
                                                                                       "bank_code='HDFC' "
        result = DBProcessor.getValueFromDB(query)
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Completed)------------------------------------
        # ------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Call generate QR API
            api_details = DBProcessor.get_api_details('static_qrcode_generate_hdfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            username_api = response["username"]
            logger.debug(f"fetching publish_id, username from api response is : "f"{publish_id},{username_api}")

            amount = random.uniform(202.19, 202.80)
            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            customer_name = "Automation user"
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI callback generator API
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn,
                "merchantTranId": merchant_tran_id,
                "TxnInitDate": "20221107153216",
                "TxnCompletionDate": "221123064745654",
                "PayerAmount": amount,
                "PayerName": customer_name,
                "PayerMobile": "0000000000",
                "PayerVA": "bhaisahab@icici",
                "TxnStatus": "SUCCESS"
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callbackgeneratorUpiICICI api is : {response}")

            # Call UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")
            orig_txn_id = response["merchantTranId"]

            # Call refund API
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "originalTransactionId": str(orig_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")
            refund_txn_id = response['txnId']

            query = "select * from txn where id = '" + str(orig_txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            orig_txn_amt = result['amount'].values[0]
            orig_acquirer_code = result['acquirer_code'].values[0]
            orig_bank_code = result['bank_code'].values[0]
            orig_issuer_code = result['issuer_code'].values[0]
            orig_pmt_gateway = result['payment_gateway'].values[0]
            orig_pmt_mode = result['payment_mode'].values[0]
            orig_settlement_status = result['settlement_status'].values[0]
            orig_status = result['status'].values[0]
            orig_txn_type = result['txn_type'].values[0]
            orig_bank_name = result['bank_name'].values[0]
            orig_state = result['state'].iloc[0]
            orig_tid = result['tid'].values[0]
            orig_mid = result['mid'].values[0]
            orig_rr_number = result['rr_number'].values[0]
            orig_created_time = result['created_time'].values[0]

            query = "select * from txn where id = '" + str(refund_txn_id) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            refund_txn_amt = result['amount'].values[0]
            refund_acquirer_code = result['acquirer_code'].values[0]
            refund_cust_name = result['customer_name'].values[0]
            refund_org_code = result['org_code'].values[0]
            refund_ref_txn_id = result['ref_txn_id'].values[0]
            refund_pmt_gateway = result['payment_gateway'].values[0]
            refund_pmt_mode = result['payment_mode'].values[0]
            refund_settlement_status = result['settlement_status'].values[0]
            refund_status = result['status'].values[0]
            refund_txn_type = result['txn_type'].values[0]
            refund_username = result['username'].values[0]
            refund_state = result['state'].iloc[0]
            refund_created_time = result['created_time'].values[0]

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
                date_original = date_time_converter.db_datetime(orig_created_time)
                date_refund = date_time_converter.db_datetime(refund_created_time)

                expected_api_values = {
                    "txn_amt": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "org_code": org_code,
                    "pmt_mode": "UPI",
                    "rrn": bank_rrn,
                    "settle_status": "SETTLED",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "txn_type": "CHARGE",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "date": date_original,
                    "txn_amt_2": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "customer_name_2": customer_name,
                    "org_code_2": org_code,
                    "orig_txn_id_2": orig_txn_id,
                    "pmt_mode_2": "UPI",
                    "settle_status_2": "FAILED",
                    "pmt_status_2": "FAILED",
                    "pmt_state_2": "FAILED",
                    "txn_type_2": "REFUND",
                    "txn_type_desc_2": "Refund",
                    "acquirer_code_2": "ICICI",
                    "date_2": date_refund,
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

                orig_api_status = response["status"]
                orig_api_amount = float(response["amount"])
                orig_api_payment_mode = response["paymentMode"]
                orig_api_state = response["states"][0]
                orig_api_rrn = response["rrNumber"]
                orig_api_settlement_status = response["settlementStatus"]
                orig_api_issuer_code = response["issuerCode"]
                orig_api_acquirer_code = response["acquirerCode"]
                orig_api_org_code = response["orgCode"]
                orig_api_mid = response["mid"]
                orig_api_tid = response["tid"]
                orig_api_txn_type = response["txnType"]
                orig_api_date = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                refund_api_status = response["status"]
                refund_api_original_txn_id = response["origTxnId"]
                refund_api_cust_name = response["customerName"]
                refund_api_amount = float(response["amount"])
                refund_api_payment_mode = response["paymentMode"]
                refund_api_state = response["states"][0]
                refund_api_settlement_status = response["settlementStatus"]
                refund_api_acquirer_code = response["acquirerCode"]
                refund_api_org_code = response["orgCode"]
                refund_api_txn_type = response["txnType"]
                refund_api_txn_type_desc = response["txnTypeDesc"]
                refund_api_date = response["createdTime"]

                actual_api_values = {
                    "txn_amt": orig_api_amount,
                    "virtual_mid": orig_api_mid,
                    "virtual_tid": orig_api_tid,
                    "org_code": orig_api_org_code,
                    "pmt_mode": orig_api_payment_mode,
                    "rrn": orig_api_rrn,
                    "settle_status": orig_api_settlement_status,
                    "pmt_status": orig_api_status,
                    "pmt_state": orig_api_state,
                    "txn_type": orig_api_txn_type,
                    "acquirer_code": orig_api_acquirer_code,
                    "issuer_code": orig_api_issuer_code,
                    "date": date_time_converter.from_api_to_datetime_format(orig_api_date),
                    "txn_amt_2": refund_api_amount,
                    "customer_name_2": refund_api_cust_name,
                    "org_code_2": refund_api_org_code,
                    "orig_txn_id_2": refund_api_original_txn_id,
                    "pmt_mode_2": refund_api_payment_mode,
                    "settle_status_2": refund_api_settlement_status,
                    "pmt_status_2": refund_api_status,
                    "pmt_state_2": refund_api_state,
                    "txn_type_2": refund_api_txn_type,
                    "txn_type_desc_2": refund_api_txn_type_desc,
                    "acquirer_code_2": refund_api_acquirer_code,
                    "date_2": date_time_converter.from_api_to_datetime_format(refund_api_date),
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
                    "txn_amt": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "bank_name": "ICICI Bank",
                    "virtual_tid": virtual_tid,
                    "virtual_mid": virtual_mid,
                    "rrn": bank_rrn,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_org_code": org_code,
                    "txn_type_2": "REFUND",
                    "username_2": app_username,
                    "customer_name_2": customer_name,
                    "org_code_2": org_code,
                    "pmt_status_2": "FAILED",
                    "pmt_state_2": "FAILED",
                    "pmt_mode_2": "UPI",
                    "ref_txn_id_2": orig_txn_id,
                    "txn_amt_2": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "upi_txn_status_2": "FAILED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "upi_add_field1_2": publish_id,
                    "upi_add_field2_2": merchant_tran_id,
                    "upi_org_code_2": org_code
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                orig_upi_org_code = result["org_code"].iloc[0]
                orig_upi_bank_code = result["bank_code"].iloc[0]
                orig_upi_status = result["status"].iloc[0]
                orig_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                orig_upi_txn_type = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                refund_upi_add_field1 = result["additional_field1"].iloc[0]
                refund_upi_add_field2 = result["additional_field2"].iloc[0]
                refund_upi_org_code = result["org_code"].iloc[0]
                refund_upi_bank_code = result["bank_code"].iloc[0]
                refund_upi_status = result["status"].iloc[0]
                refund_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                refund_upi_txn_type = result["txn_type"].iloc[0]

                actual_db_values = {
                    "txn_amt": orig_txn_amt,
                    "acquirer_code": orig_acquirer_code,
                    "bank_code": orig_bank_code,
                    "issuer_code": orig_issuer_code,
                    "pmt_gateway": orig_pmt_gateway,
                    "pmt_mode": orig_pmt_mode,
                    "settle_status": orig_settlement_status,
                    "pmt_status": orig_status,
                    "txn_type": orig_txn_type,
                    "bank_name": orig_bank_name,
                    "pmt_state": orig_state,
                    "virtual_tid": orig_tid,
                    "virtual_mid": orig_mid,
                    "rrn": orig_rr_number,
                    "txn_amt_2": refund_txn_amt,
                    "acquirer_code_2": refund_acquirer_code,
                    "customer_name_2": refund_cust_name,
                    "org_code_2": refund_org_code,
                    "ref_txn_id_2": refund_ref_txn_id,
                    "pmt_gateway_2": refund_pmt_gateway,
                    "pmt_mode_2": refund_pmt_mode,
                    "settle_status_2": refund_settlement_status,
                    "pmt_status_2": refund_status,
                    "txn_type_2": refund_txn_type,
                    "username_2": refund_username,
                    "pmt_state_2": refund_state,
                    "upi_org_code": orig_upi_org_code,
                    "upi_bank_code": orig_upi_bank_code,
                    "upi_txn_status": orig_upi_status,
                    "upi_mc_id": orig_upi_upi_mc_id,
                    "upi_txn_type": orig_upi_txn_type,
                    "upi_add_field1_2": refund_upi_add_field1,
                    "upi_add_field2_2": refund_upi_add_field2,
                    "upi_org_code_2": refund_upi_org_code,
                    "upi_bank_code_2": refund_upi_bank_code,
                    "upi_txn_status_2": refund_upi_status,
                    "upi_mc_id_2": refund_upi_upi_mc_id,
                    "upi_txn_type_2": refund_upi_txn_type
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
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
def test_d102_108_010():
    """
     Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Refund_Posted_ICICI_DIRECT
     Sub Feature Description: Verification of a staticQR BQRV4 UPI Refund_posted transaction via ICICI_DIRECT
     TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRV4 StaticQR, 010-> Testcase ID
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
        logger.info(f"fetched virtual_tid is : {virtual_tid}")

        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # ----------------------------------------PreConditions(Completed)-----------------------------
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Call generate QR API
            api_details = DBProcessor.get_api_details('static_qrcode_generate_hdfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            username_api = response["username"]
            logger.debug(f"fetching publish_id, username from api response is : "f"{publish_id},{username_api}")

            amount = random.uniform(201.11, 201.20)
            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            customer_name = "Automation user"
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI callback generator API
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn,
                "merchantTranId": merchant_tran_id,
                "TxnInitDate": "20221107153216",
                "TxnCompletionDate": "221123064745654",
                "PayerAmount": amount,
                "PayerName": customer_name,
                "PayerMobile": "0000000000",
                "PayerVA": "bhaisahab@icici",
                "TxnStatus": "SUCCESS"
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callbackgeneratorUpiICICI api is : {response}")

            # Call UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            orig_txn_id = response["merchantTranId"]

            # Call refund API
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "originalTransactionId": str(orig_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")

            refund_txn_id = response['txnId']

            query = "select * from txn where id = '" + str(orig_txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            orig_txn_amt = result['amount'].values[0]
            orig_acquirer_code = result['acquirer_code'].values[0]
            orig_bank_code = result['bank_code'].values[0]
            orig_cust_name = result['customer_name'].values[0]
            orig_issuer_code = result['issuer_code'].values[0]
            orig_pmt_gateway = result['payment_gateway'].values[0]
            orig_pmt_mode = result['payment_mode'].values[0]
            orig_settlement_status = result['settlement_status'].values[0]
            orig_status = result['status'].values[0]
            orig_txn_type = result['txn_type'].values[0]
            orig_bank_name = result['bank_name'].values[0]
            orig_state = result['state'].iloc[0]
            orig_tid = result['tid'].values[0]
            orig_mid = result['mid'].values[0]
            orig_rr_number = result['rr_number'].values[0]
            orig_created_time = result['created_time'].values[0]

            query = "select * from txn where id = '" + str(refund_txn_id) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            refund_txn_amt = result['amount'].values[0]
            refund_acquirer_code = result['acquirer_code'].values[0]
            refund_cust_name = result['customer_name'].values[0]
            refund_org_code = result['org_code'].values[0]
            refund_ref_txn_id = result['ref_txn_id'].values[0]
            refund_pmt_gateway = result['payment_gateway'].values[0]
            refund_pmt_mode = result['payment_mode'].values[0]
            refund_settlement_status = result['settlement_status'].values[0]
            refund_status = result['status'].values[0]
            refund_txn_type = result['txn_type'].values[0]
            refund_username = result['username'].values[0]
            refund_state = result['state'].iloc[0]
            refund_created_time = result['created_time'].values[0]

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
                date_original = date_time_converter.db_datetime(orig_created_time)
                date_refund = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": bank_rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "org_code": org_code,
                    "date": date_original,
                    "pmt_status_2": "REFUND_POSTED",
                    "txn_amt_2": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUND_INITIATED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "ICICI",
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "date_2": date_refund,
                    "customer_name_2": customer_name,
                    "orig_txn_id_2": orig_txn_id,
                    "txn_type_desc_2": "Refund",
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

                orig_api_status = response["status"]
                orig_api_amount = float(response["amount"])
                orig_api_payment_mode = response["paymentMode"]
                orig_api_state = response["states"][0]
                orig_api_rrn = response["rrNumber"]
                orig_api_settlement_status = response["settlementStatus"]
                orig_api_issuer_code = response["issuerCode"]
                orig_api_acquirer_code = response["acquirerCode"]
                orig_api_org_code = response["orgCode"]
                orig_api_mid = response["mid"]
                orig_api_tid = response["tid"]
                orig_api_txn_type = response["txnType"]
                orig_api_date = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                refund_api_status = response["status"]
                refund_api_original_txn_id = response["origTxnId"]
                refund_api_cust_name = response["customerName"]
                refund_api_amount = float(response["amount"])
                refund_api_payment_mode = response["paymentMode"]
                refund_api_state = response["states"][0]
                refund_api_settlement_status = response["settlementStatus"]
                refund_api_acquirer_code = response["acquirerCode"]
                refund_api_org_code = response["orgCode"]
                refund_api_txn_type = response["txnType"]
                refund_api_txn_type_desc = response["txnTypeDesc"]
                refund_api_date = response["createdTime"]

                actual_api_values = {
                    "txn_amt": orig_api_amount,
                    "virtual_mid": orig_api_mid,
                    "virtual_tid": orig_api_tid,
                    "org_code": orig_api_org_code,
                    "pmt_mode": orig_api_payment_mode,
                    "rrn": orig_api_rrn,
                    "settle_status": orig_api_settlement_status,
                    "pmt_status": orig_api_status,
                    "pmt_state": orig_api_state,
                    "txn_type": orig_api_txn_type,
                    "acquirer_code": orig_api_acquirer_code,
                    "issuer_code": orig_api_issuer_code,
                    "date": date_time_converter.from_api_to_datetime_format(orig_api_date),
                    "txn_amt_2": refund_api_amount,
                    "customer_name_2": refund_api_cust_name,
                    "org_code_2": refund_api_org_code,
                    "orig_txn_id_2": refund_api_original_txn_id,
                    "pmt_mode_2": refund_api_payment_mode,
                    "settle_status_2": refund_api_settlement_status,
                    "pmt_status_2": refund_api_status,
                    "pmt_state_2": refund_api_state,
                    "txn_type_2": refund_api_txn_type,
                    "txn_type_desc_2": refund_api_txn_type_desc,
                    "acquirer_code_2": refund_api_acquirer_code,
                    "date_2": date_time_converter.from_api_to_datetime_format(refund_api_date),
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
                    "customer_name": customer_name,
                    "txn_amt": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "bank_name": "ICICI Bank",
                    "rrn": bank_rrn,
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "customer_name_2": customer_name,
                    "org_code_2": org_code,
                    "ref_txn_id_2": orig_txn_id,
                    "txn_type_2": "REFUND",
                    "username_2": app_username,
                    "upi_org_code": org_code,
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_mc_id": upi_mc_id,
                    "upi_txn_type": "STATIC_QR",
                    "upi_add_field1_2": publish_id,
                    "upi_add_field2_2": merchant_tran_id,
                    "upi_org_code_2": org_code,
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_txn_status_2": "REFUND_POSTED",
                    "upi_mc_id_2": upi_mc_id,
                    "upi_txn_type_2": "REFUND"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                orig_upi_org_code = result["org_code"].iloc[0]
                orig_upi_bank_code = result["bank_code"].iloc[0]
                orig_upi_status = result["status"].iloc[0]
                orig_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                orig_upi_txn_type = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                refund_upi_add_field1 = result["additional_field1"].iloc[0]
                refund_upi_add_field2 = result["additional_field2"].iloc[0]
                refund_upi_org_code = result["org_code"].iloc[0]
                refund_upi_bank_code = result["bank_code"].iloc[0]
                refund_upi_status = result["status"].iloc[0]
                refund_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                refund_upi_txn_type = result["txn_type"].iloc[0]

                actual_db_values = {
                    "txn_amt": orig_txn_amt,
                    "acquirer_code": orig_acquirer_code,
                    "bank_code": orig_bank_code,
                    "issuer_code": orig_issuer_code,
                    "pmt_gateway": orig_pmt_gateway,
                    "pmt_mode": orig_pmt_mode,
                    "settle_status": orig_settlement_status,
                    "pmt_status": orig_status,
                    "customer_name": orig_cust_name,
                    "txn_type": orig_txn_type,
                    "bank_name": orig_bank_name,
                    "pmt_state": orig_state,
                    "virtual_tid": orig_tid,
                    "virtual_mid": orig_mid,
                    "rrn": orig_rr_number,
                    "txn_amt_2": refund_txn_amt,
                    "acquirer_code_2": refund_acquirer_code,
                    "customer_name_2": refund_cust_name,
                    "org_code_2": refund_org_code,
                    "ref_txn_id_2": refund_ref_txn_id,
                    "pmt_gateway_2": refund_pmt_gateway,
                    "pmt_mode_2": refund_pmt_mode,
                    "settle_status_2": refund_settlement_status,
                    "pmt_status_2": refund_status,
                    "txn_type_2": refund_txn_type,
                    "username_2": refund_username,
                    "pmt_state_2": refund_state,
                    "upi_org_code": orig_upi_org_code,
                    "upi_bank_code": orig_upi_bank_code,
                    "upi_txn_status": orig_upi_status,
                    "upi_mc_id": orig_upi_upi_mc_id,
                    "upi_txn_type": orig_upi_txn_type,
                    "upi_add_field1_2": refund_upi_add_field1,
                    "upi_add_field2_2": refund_upi_add_field2,
                    "upi_org_code_2": refund_upi_org_code,
                    "upi_bank_code_2": refund_upi_bank_code,
                    "upi_txn_status_2": refund_upi_status,
                    "upi_mc_id_2": refund_upi_upi_mc_id,
                    "upi_txn_type_2": refund_upi_txn_type
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
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
def test_d102_108_011():
    """
     Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Partial_Refund_ICICI_DIRECT
     Sub Feature Description: Verification of a staticQR BQRV4 UPI partial Refund transaction via ICICI_DIRECT
     TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRV4 StaticQR, 011-> Testcase ID
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
        logger.info(f"fetched virtual_tid is : {virtual_tid}")

        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------
        # -----------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Call generate QR API
            api_details = DBProcessor.get_api_details('static_qrcode_generate_hdfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            username_api = response["username"]
            logger.debug(f"fetching publish_id, username from api response is : "f"{publish_id},{username_api}")

            amount = random.randint(225, 300)
            refund_amount = amount - 10

            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            customer_name = "Automation user"
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI callback generator API
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn,
                "merchantTranId": merchant_tran_id,
                "TxnInitDate": "20221107153216",
                "TxnCompletionDate": "221123064745654",
                "PayerAmount": amount,
                "PayerName": customer_name,
                "PayerMobile": "0000000000",
                "PayerVA": "bhaisahab@icici",
                "TxnStatus": "SUCCESS"
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callbackgeneratorUpiICICI api is : {response}")

            # Call UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")
            orig_txn_id = response["merchantTranId"]

            # Call refund API
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(refund_amount),
                                                                    "originalTransactionId": str(orig_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")
            refund_txn_id = response['txnId']

            query = "select * from txn where id = '" + str(orig_txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            orig_txn_amt = result['amount'].values[0]
            orig_acquirer_code = result['acquirer_code'].values[0]
            orig_bank_code = result['bank_code'].values[0]
            orig_issuer_code = result['issuer_code'].values[0]
            orig_pmt_gateway = result['payment_gateway'].values[0]
            orig_pmt_mode = result['payment_mode'].values[0]
            orig_settlement_status = result['settlement_status'].values[0]
            orig_status = result['status'].values[0]
            orig_txn_type = result['txn_type'].values[0]
            orig_bank_name = result['bank_name'].values[0]
            orig_state = result['state'].iloc[0]
            orig_tid = result['tid'].values[0]
            orig_mid = result['mid'].values[0]
            orig_rr_number = result['rr_number'].values[0]
            orig_created_time = result['created_time'].values[0]

            query = "select * from txn where id = '" + str(refund_txn_id) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            refund_txn_amt = result['amount'].values[0]
            refund_acquirer_code = result['acquirer_code'].values[0]
            refund_cust_name = result['customer_name'].values[0]
            refund_mid = result['mid'].values[0]
            refund_tid = result['tid'].values[0]
            refund_org_code = result['org_code'].values[0]
            refund_ref_txn_id = result['ref_txn_id'].values[0]
            refund_pmt_gateway = result['payment_gateway'].values[0]
            refund_pmt_mode = result['payment_mode'].values[0]
            refund_settlement_status = result['settlement_status'].values[0]
            refund_status = result['status'].values[0]
            refund_txn_type = result['txn_type'].values[0]
            refund_username = result['username'].values[0]
            refund_state = result['state'].iloc[0]
            refund_created_time = result['created_time'].values[0]

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
                date_original = date_time_converter.db_datetime(orig_created_time)
                date_refund = date_time_converter.db_datetime(refund_created_time)

                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": bank_rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "org_code": org_code,
                    "date": date_original,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(refund_amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "txn_type_2": "REFUND",
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date_2": date_refund,
                    "customer_name_2": customer_name,
                    "orig_txn_id_2": orig_txn_id,
                    "txn_type_desc_2": "Refund",
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

                orig_api_status = response["status"]
                orig_api_amount = float(response["amount"])
                orig_api_payment_mode = response["paymentMode"]
                orig_api_state = response["states"][0]
                orig_api_rrn = response["rrNumber"]
                orig_api_settlement_status = response["settlementStatus"]
                orig_api_issuer_code = response["issuerCode"]
                orig_api_acquirer_code = response["acquirerCode"]
                orig_api_org_code = response["orgCode"]
                orig_api_mid = response["mid"]
                orig_api_tid = response["tid"]
                orig_api_txn_type = response["txnType"]
                orig_api_date = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                refund_api_status = response["status"]
                refund_api_original_txn_id = response["origTxnId"]
                refund_api_cust_name = response["customerName"]
                refund_api_amount = float(response["amount"])
                refund_api_payment_mode = response["paymentMode"]
                refund_api_state = response["states"][0]
                refund_api_settlement_status = response["settlementStatus"]
                refund_api_acquirer_code = response["acquirerCode"]
                refund_api_org_code = response["orgCode"]
                refund_api_mid = response["mid"]
                refund_api_tid = response["tid"]
                refund_api_txn_type = response["txnType"]
                refund_api_txn_type_desc = response["txnTypeDesc"]
                refund_api_date = response["createdTime"]

                actual_api_values = {
                    "txn_amt": orig_api_amount,
                    "virtual_mid": orig_api_mid,
                    "virtual_tid": orig_api_tid,
                    "org_code": orig_api_org_code,
                    "pmt_mode": orig_api_payment_mode,
                    "rrn": orig_api_rrn,
                    "settle_status": orig_api_settlement_status,
                    "pmt_status": orig_api_status,
                    "pmt_state": orig_api_state,
                    "txn_type": orig_api_txn_type,
                    "acquirer_code": orig_api_acquirer_code,
                    "issuer_code": orig_api_issuer_code,
                    "date": date_time_converter.from_api_to_datetime_format(orig_api_date),
                    "txn_amt_2": refund_api_amount,
                    "customer_name_2": refund_api_cust_name,
                    "virtual_mid_2": refund_api_mid,
                    "virtual_tid_2": refund_api_tid,
                    "org_code_2": refund_api_org_code,
                    "orig_txn_id_2": refund_api_original_txn_id,
                    "pmt_mode_2": refund_api_payment_mode,
                    "settle_status_2": refund_api_settlement_status,
                    "pmt_status_2": refund_api_status,
                    "pmt_state_2": refund_api_state,
                    "txn_type_2": refund_api_txn_type,
                    "txn_type_desc_2": refund_api_txn_type_desc,
                    "acquirer_code_2": refund_api_acquirer_code,
                    "date_2": date_time_converter.from_api_to_datetime_format(refund_api_date),
                }

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
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "upi_txn_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(refund_amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "pmt_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "bank_name": "ICICI Bank",
                    "rrn": bank_rrn,
                    "customer_name_2": customer_name,
                    "org_code_2": org_code,
                    "ref_txn_id_2": orig_txn_id,
                    "txn_type_2": "REFUND",
                    "username_2": app_username,
                    "upi_org_code": org_code,
                    "upi_add_field1_2": publish_id,
                    "upi_add_field2_2": merchant_tran_id,
                    "upi_org_code_2": org_code,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                orig_upi_org_code = result["org_code"].iloc[0]
                orig_upi_bank_code = result["bank_code"].iloc[0]
                orig_upi_status = result["status"].iloc[0]
                orig_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                orig_upi_txn_type = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                refund_upi_add_field1 = result["additional_field1"].iloc[0]
                refund_upi_add_field2 = result["additional_field2"].iloc[0]
                refund_upi_org_code = result["org_code"].iloc[0]
                refund_upi_bank_code = result["bank_code"].iloc[0]
                refund_upi_status = result["status"].iloc[0]
                refund_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                refund_upi_txn_type = result["txn_type"].iloc[0]

                actual_db_values = {
                    "txn_amt": orig_txn_amt,
                    "acquirer_code": orig_acquirer_code,
                    "bank_code": orig_bank_code,
                    "issuer_code": orig_issuer_code,
                    "pmt_gateway": orig_pmt_gateway,
                    "pmt_mode": orig_pmt_mode,
                    "settle_status": orig_settlement_status,
                    "pmt_status": orig_status,
                    "txn_type": orig_txn_type,
                    "bank_name": orig_bank_name,
                    "pmt_state": orig_state,
                    "virtual_tid": orig_tid,
                    "virtual_mid": orig_mid,
                    "rrn": orig_rr_number,
                    "txn_amt_2": refund_txn_amt,
                    "acquirer_code_2": refund_acquirer_code,
                    "customer_name_2": refund_cust_name,
                    "virtual_mid_2": refund_mid,
                    "virtual_tid_2": refund_tid,
                    "org_code_2": refund_org_code,
                    "ref_txn_id_2": refund_ref_txn_id,
                    "pmt_gateway_2": refund_pmt_gateway,
                    "pmt_mode_2": refund_pmt_mode,
                    "settle_status_2": refund_settlement_status,
                    "pmt_status_2": refund_status,
                    "txn_type_2": refund_txn_type,
                    "username_2": refund_username,
                    "pmt_state_2": refund_state,
                    "upi_org_code": orig_upi_org_code,
                    "upi_bank_code": orig_upi_bank_code,
                    "upi_txn_status": orig_upi_status,
                    "upi_mc_id": orig_upi_upi_mc_id,
                    "upi_txn_type": orig_upi_txn_type,
                    "upi_add_field1_2": refund_upi_add_field1,
                    "upi_add_field2_2": refund_upi_add_field2,
                    "upi_org_code_2": refund_upi_org_code,
                    "upi_bank_code_2": refund_upi_bank_code,
                    "upi_txn_status_2": refund_upi_status,
                    "upi_mc_id_2": refund_upi_upi_mc_id,
                    "upi_txn_type_2": refund_upi_txn_type
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
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
def test_d102_108_012():
    """
     Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Partial_Refund_Failed_ICICI_DIRECT
     Sub Feature Description: Verification of a staticQR BQRV4 UPI partial Refund Failed transaction via ICICI_DIRECT
     TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRV4 StaticQR, 012-> Testcase ID
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
        logger.info(f"fetched virtual_tid is : {virtual_tid}")

        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual_mid is : {virtual_mid}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Completed)----------------------------------------
        # ---------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Call generate QR API
            api_details = DBProcessor.get_api_details('static_qrcode_generate_hdfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            username_api = response["username"]
            logger.debug(f"fetching publish_id, username from api response is : "f"{publish_id},{username_api}")

            amount = random.uniform(202.19, 202.80)
            refund_amount = amount - 0.02

            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            customer_name = "Automation user"
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI callback generator API
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn,
                "merchantTranId": merchant_tran_id,
                "TxnInitDate": "20221107153216",
                "TxnCompletionDate": "221123064745654",
                "PayerAmount": amount,
                "PayerName": customer_name,
                "PayerMobile": "0000000000",
                "PayerVA": "bhaisahab@icici",
                "TxnStatus": "SUCCESS"
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callbackgeneratorUpiICICI api is : {response}")

            # Call UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")
            orig_txn_id = response["merchantTranId"]

            # Call refund API
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(refund_amount),
                                                                    "originalTransactionId": str(orig_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")
            refund_txn_id = response['txnId']

            query = "select * from txn where id = '" + str(orig_txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            orig_txn_amt = result['amount'].values[0]
            orig_acquirer_code = result['acquirer_code'].values[0]
            orig_bank_code = result['bank_code'].values[0]
            orig_issuer_code = result['issuer_code'].values[0]
            orig_pmt_gateway = result['payment_gateway'].values[0]
            orig_pmt_mode = result['payment_mode'].values[0]
            orig_settlement_status = result['settlement_status'].values[0]
            orig_status = result['status'].values[0]
            orig_txn_type = result['txn_type'].values[0]
            orig_bank_name = result['bank_name'].values[0]
            orig_state = result['state'].iloc[0]
            orig_tid = result['tid'].values[0]
            orig_mid = result['mid'].values[0]
            orig_rr_number = result['rr_number'].values[0]
            orig_created_time = result['created_time'].values[0]

            query = "select * from txn where id = '" + str(refund_txn_id) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            refund_txn_amt = result['amount'].values[0]
            refund_acquirer_code = result['acquirer_code'].values[0]
            refund_cust_name = result['customer_name'].values[0]
            refund_org_code = result['org_code'].values[0]
            refund_ref_txn_id = result['ref_txn_id'].values[0]
            refund_pmt_gateway = result['payment_gateway'].values[0]
            refund_pmt_mode = result['payment_mode'].values[0]
            refund_settlement_status = result['settlement_status'].values[0]
            refund_status = result['status'].values[0]
            refund_txn_type = result['txn_type'].values[0]
            refund_username = result['username'].values[0]
            refund_state = result['state'].iloc[0]
            refund_created_time = result['created_time'].values[0]

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
                date_original = date_time_converter.db_datetime(orig_created_time)
                date_refund = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": bank_rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "org_code": org_code,
                    "date": date_original,
                    "pmt_status_2": "FAILED",
                    "txn_amt_2": float(str(refund_amount).split('.')[0] + '.' + str(refund_amount).split('.')[1][:2]),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "FAILED",
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "ICICI",
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "date_2": date_refund,
                    "customer_name_2": customer_name,
                    "orig_txn_id_2": orig_txn_id,
                    "txn_type_desc_2": "Refund",
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

                orig_api_status = response["status"]
                orig_api_amount = float(response["amount"])
                orig_api_payment_mode = response["paymentMode"]
                orig_api_state = response["states"][0]
                orig_api_rrn = response["rrNumber"]
                orig_api_settlement_status = response["settlementStatus"]
                orig_api_issuer_code = response["issuerCode"]
                orig_api_acquirer_code = response["acquirerCode"]
                orig_api_org_code = response["orgCode"]
                orig_api_mid = response["mid"]
                orig_api_tid = response["tid"]
                orig_api_txn_type = response["txnType"]
                orig_api_date = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                refund_api_status = response["status"]
                refund_api_original_txn_id = response["origTxnId"]
                refund_api_cust_name = response["customerName"]
                refund_api_amount = float(response["amount"])
                refund_api_payment_mode = response["paymentMode"]
                refund_api_state = response["states"][0]
                refund_api_settlement_status = response["settlementStatus"]
                refund_api_acquirer_code = response["acquirerCode"]
                refund_api_org_code = response["orgCode"]
                refund_api_txn_type = response["txnType"]
                refund_api_txn_type_desc = response["txnTypeDesc"]
                refund_api_date = response["createdTime"]

                actual_api_values = {
                    "txn_amt": orig_api_amount,
                    "virtual_mid": orig_api_mid,
                    "virtual_tid": orig_api_tid,
                    "org_code": orig_api_org_code,
                    "pmt_mode": orig_api_payment_mode,
                    "rrn": orig_api_rrn,
                    "settle_status": orig_api_settlement_status,
                    "pmt_status": orig_api_status,
                    "pmt_state": orig_api_state,
                    "txn_type": orig_api_txn_type,
                    "acquirer_code": orig_api_acquirer_code,
                    "issuer_code": orig_api_issuer_code,
                    "date": date_time_converter.from_api_to_datetime_format(orig_api_date),
                    "txn_amt_2": refund_api_amount,
                    "customer_name_2": refund_api_cust_name,
                    "org_code_2": refund_api_org_code,
                    "orig_txn_id_2": refund_api_original_txn_id,
                    "pmt_mode_2": refund_api_payment_mode,
                    "settle_status_2": refund_api_settlement_status,
                    "pmt_status_2": refund_api_status,
                    "pmt_state_2": refund_api_state,
                    "txn_type_2": refund_api_txn_type,
                    "txn_type_desc_2": refund_api_txn_type_desc,
                    "acquirer_code_2": refund_api_acquirer_code,
                    "date_2": date_time_converter.from_api_to_datetime_format(refund_api_date),
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
                    "txn_amt": float(str(amount).split('.')[0] + '.' + str(amount).split('.')[1][:2]),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "bank_name": "ICICI Bank",
                    "rrn": bank_rrn,
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_org_code": org_code,
                    "pmt_state_2": "FAILED",
                    "pmt_mode_2": "UPI",
                    "customer_name_2": customer_name,
                    "txn_amt_2": float(str(refund_amount).split('.')[0] + '.' + str(refund_amount).split('.')[1][:2]),
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "pmt_status_2": "FAILED",
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "ref_txn_id_2": orig_txn_id,
                    "username_2": app_username,
                    "upi_add_field1_2": publish_id,
                    "upi_add_field2_2": merchant_tran_id,
                    "upi_org_code_2": org_code,
                    "upi_txn_status_2": "FAILED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                orig_upi_org_code = result["org_code"].iloc[0]
                orig_upi_bank_code = result["bank_code"].iloc[0]
                orig_upi_status = result["status"].iloc[0]
                orig_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                orig_upi_txn_type = result["txn_type"].iloc[0]

                query = "select * from upi_txn where txn_id='" + refund_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                refund_upi_add_field1 = result["additional_field1"].iloc[0]
                refund_upi_add_field2 = result["additional_field2"].iloc[0]
                refund_upi_org_code = result["org_code"].iloc[0]
                refund_upi_bank_code = result["bank_code"].iloc[0]
                refund_upi_status = result["status"].iloc[0]
                refund_upi_upi_mc_id = result["upi_mc_id"].iloc[0]
                refund_upi_txn_type = result["txn_type"].iloc[0]

                actual_db_values = {
                    "txn_amt": orig_txn_amt,
                    "acquirer_code": orig_acquirer_code,
                    "bank_code": orig_bank_code,
                    "issuer_code": orig_issuer_code,
                    "pmt_gateway": orig_pmt_gateway,
                    "pmt_mode": orig_pmt_mode,
                    "settle_status": orig_settlement_status,
                    "pmt_status": orig_status,
                    "txn_type": orig_txn_type,
                    "bank_name": orig_bank_name,
                    "pmt_state": orig_state,
                    "virtual_tid": orig_tid,
                    "virtual_mid": orig_mid,
                    "rrn": orig_rr_number,
                    "txn_amt_2": refund_txn_amt,
                    "acquirer_code_2": refund_acquirer_code,
                    "customer_name_2": refund_cust_name,
                    "org_code_2": refund_org_code,
                    "ref_txn_id_2": refund_ref_txn_id,
                    "pmt_gateway_2": refund_pmt_gateway,
                    "pmt_mode_2": refund_pmt_mode,
                    "settle_status_2": refund_settlement_status,
                    "pmt_status_2": refund_status,
                    "txn_type_2": refund_txn_type,
                    "username_2": refund_username,
                    "pmt_state_2": refund_state,
                    "upi_org_code": orig_upi_org_code,
                    "upi_bank_code": orig_upi_bank_code,
                    "upi_txn_status": orig_upi_status,
                    "upi_mc_id": orig_upi_upi_mc_id,
                    "upi_txn_type": orig_upi_txn_type,
                    "upi_add_field1_2": refund_upi_add_field1,
                    "upi_add_field2_2": refund_upi_add_field2,
                    "upi_org_code_2": refund_upi_org_code,
                    "upi_bank_code_2": refund_upi_bank_code,
                    "upi_txn_status_2": refund_upi_status,
                    "upi_mc_id_2": refund_upi_upi_mc_id,
                    "upi_txn_type_2": refund_upi_txn_type
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)