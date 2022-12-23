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
def test_d102_108_013():
    """
    Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Partial_Refund_Amt_Greater_Than_Original_ICICI_DIRECT
    Sub Feature Description: Verification of a staticQR BQRV4 UPI partial Refund with amount greater than actual via ICICI_DIRECT
    TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRv4 StaticQR, 013-> Testcase ID
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
        # -----------------------------PreConditions(Completed)-----------------------------
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

            amount = random.randint(225, 300)
            amount_new_2 = amount - 100
            greater_refund_amount = 101

            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            cust_name = "Automation user"
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI callback generator API
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn,
                "merchantTranId": merchant_tran_id,
                "TxnInitDate":"20221107153216",
                "TxnCompletionDate":"221123064745654",
                "PayerAmount": amount,
                "PayerName": cust_name,
                "PayerMobile":"0000000000",
                "PayerVA":"bhaisahab@icici",
                "TxnStatus":"SUCCESS"
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callbackgeneratorUpiICICI api is : {response}")

            # Call UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            txn_id = response["merchantTranId"]

            # Do first refund
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount_new_2),
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for first refund txn : {response}")
            txn_id_2 = response['txnId']

            #Doing second refund
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(greater_refund_amount),
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for second refund txn : {response}")
            error_message_api = response["errorMessage"]
            logger.debug(f"Error msg of payment refund for refund amount greater than"
                         f" original amt is : {error_message_api}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

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
            rrn = result['rr_number'].values[0]
            customer_name = result['customer_name'].values[0]
            created_time = result['created_time'].values[0]

            query = "select * from txn where id = '" + str(txn_id_2) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            customer_name_new_2 = result['customer_name'].values[0]
            created_time_new_2 = result['created_time'].values[0]
            status_db_new_2 = result["status"].iloc[0]
            payment_mode_db_new_2 = result["payment_mode"].iloc[0]
            amount_db_new_2 = float(result["amount"].iloc[0])
            state_db_new_2 = result["state"].iloc[0]
            payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
            acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
            settlement_status_db_new_2 = result["settlement_status"].iloc[0]
            tid_db_new_2 = result['tid'].values[0]
            mid_db_new_2 = result['mid'].values[0]

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
                date_new = date_time_converter.db_datetime(created_time)
                date_new_2 = date_time_converter.db_datetime(created_time_new_2)
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
                    "date": date_new,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount_new_2),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "txn_type_2": "REFUND",
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date_2": date_new_2,
                    "error_message": "Amount to refund is greater than refundable amount."
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
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
                response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_2 = response["status"]
                amount_api_new_2 = float(response["amount"])
                payment_mode_api_new_2 = response["paymentMode"]
                state_api_new_2 = response["states"][0]
                settlement_status_api_new_2 = response["settlementStatus"]
                acquirer_code_api_new_2 = response["acquirerCode"]
                orgCode_api_new_2 = response["orgCode"]
                mid_api_new_2 = response["mid"]
                tid_api_new_2 = response["tid"]
                txn_type_api_new_2 = response["txnType"]
                date_api_new_2 = response["createdTime"]

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
                    "virtual_mid": mid_api,
                    "virtual_tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2,
                    "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2,
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2,
                    "virtual_mid_2": mid_api_new_2,
                    "virtual_tid_2": tid_api_new_2,
                    "org_code_2": orgCode_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2),
                    "error_message": str(error_message_api),
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
                    "customer_name": cust_name,
                    "rrn": bank_rrn,
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "payment_gateway": "ICICI",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount_new_2),
                    "customer_name_2": cust_name,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "payment_gateway_2": "ICICI",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
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
                    "customer_name": customer_name,
                    "txn_amt": amount_db,
                    "rrn": rrn,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "virtual_mid": mid_db,
                    "virtual_tid": tid_db,
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "customer_name_2": customer_name_new_2,
                    "upi_txn_status_2": upi_status_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "virtual_mid_2": mid_db_new_2,
                    "virtual_tid_2": tid_db_new_2
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
def test_d102_108_014():
    """
    Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Partial_Refund_With_Decimal_Amt_ICICI_DIRECT
    Sub Feature Description: Verification of a staticQR BQRV4 UPI partial Refund with decimal amount via ICICI_DIRECT
    TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRv4 StaticQR, 014-> Testcase ID
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
        # -----------------------------------------PreConditions(Completed)-----------------------------
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

            amount = random.randint(225, 300)
            refund_amount = amount - 10.50

            cust_name = "Automation user"
            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI callback generator API
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn,
                "merchantTranId": merchant_tran_id,
                "TxnInitDate":"20221107153216",
                "TxnCompletionDate":"221123064745654",
                "PayerAmount": amount,
                "PayerName": cust_name,
                "PayerMobile":"0000000000",
                "PayerVA":"bhaisahab@icici",
                "TxnStatus":"SUCCESS"
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callbackgeneratorUpiICICI api is : {response}")

            # Call UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")
            txn_id = response["merchantTranId"]

            # Call refund API
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(refund_amount),
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")
            second_txn_id = response['txnId']

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            customer_name = result['customer_name'].values[0]
            created_time = result['created_time'].values[0]
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

            query = "select * from txn where id = '" + str(second_txn_id) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            customer_name_new_2 = result['customer_name'].values[0]
            created_time_new_2 = result['created_time'].values[0]
            status_db_new_2 = result["status"].iloc[0]
            payment_mode_db_new_2 = result["payment_mode"].iloc[0]
            amount_db_new_2 = float(result["amount"].iloc[0])
            state_db_new_2 = result["state"].iloc[0]
            payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
            acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
            settlement_status_db_new_2 = result["settlement_status"].iloc[0]
            tid_db_new_2 = result['tid'].values[0]
            mid_db_new_2 = result['mid'].values[0]

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
                date_new = date_time_converter.db_datetime(created_time)
                date_new_2 = date_time_converter.db_datetime(created_time_new_2)
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
                    "date": date_new,
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
                    "date_2": date_new_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
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
                mid_api_new_2 = response["mid"]
                tid_api_new_2 = response["tid"]
                txn_type_api_new_2 = response["txnType"]
                date_api_new_2 = response["createdTime"]

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
                    "virtual_mid": mid_api,
                    "virtual_tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2,
                    "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2,
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2,
                    "virtual_mid_2": mid_api_new_2,
                    "virtual_tid_2": tid_api_new_2,
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
                    "customer_name": cust_name,
                    "rrn": bank_rrn,
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "payment_gateway": "ICICI",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(refund_amount),
                    "settle_status_2": "SETTLED",
                    "customer_name_2": cust_name,
                    "acquirer_code_2": "ICICI",
                    "payment_gateway_2": "ICICI",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

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
                    "customer_name": customer_name,
                    "rrn": str(rrn),
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "virtual_mid": mid_db,
                    "virtual_tid": tid_db,
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "upi_txn_status_2": upi_status_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "customer_name_2": customer_name_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "virtual_mid_2": mid_db_new_2,
                    "virtual_tid_2": tid_db_new_2,
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
def test_d102_108_015():
    """
    Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Partial_Refund_Two_Times_ICICI_DIRECT
    Sub Feature Description: Verification of a staticQR BQRV4 UPI complete refund by doing two partial Refunds via ICICI_DIRECT
    TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRv4 StaticQR, 015-> Testcase ID
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
        # ------------------------------------------------PreConditions(Completed)-----------------------------
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

            amount = random.randint(225, 300)
            first_refund_amount = amount - 10
            second_refund_amount = 10

            cust_name = "Automation user"
            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI callback generator API
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn,
                "merchantTranId": merchant_tran_id,
                "TxnInitDate":"20221107153216",
                "TxnCompletionDate":"221123064745654",
                "PayerAmount": amount,
                "PayerName": cust_name,
                "PayerMobile":"0000000000",
                "PayerVA":"bhaisahab@icici",
                "TxnStatus":"SUCCESS"
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callbackgeneratorUpiICICI api is : {response}")

            # Call UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            txn_id = response["merchantTranId"]

            # Do First Refund
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(first_refund_amount),
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")
            txn_id_2 = response['txnId']

            # Do Second Refund
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                     request_body={"username": app_username, "password": app_password,
                                                                   "amount": str(second_refund_amount),
                                                                   "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")
            txn_id_3 = response['txnId']

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            rrn_db = result['rr_number'].values[0]
            customer_name_db = result['customer_name'].values[0]
            created_time_db = result['created_time'].values[0]
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

            query = "select * from txn where id = '" + str(txn_id_2) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            customer_name_db_new_2 = result['customer_name'].values[0]
            created_time_db_new_2 = result['created_time'].values[0]
            status_db_new_2 = result["status"].iloc[0]
            payment_mode_db_new_2 = result["payment_mode"].iloc[0]
            amount_db_new_2 = float(result["amount"].iloc[0])
            state_db_new_2 = result["state"].iloc[0]
            payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
            acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
            settlement_status_db_new_2 = result["settlement_status"].iloc[0]
            tid_db_new_2 = result['tid'].values[0]
            mid_db_new_2 = result['mid'].values[0]

            query = "select * from txn where id = '" + str(txn_id_3) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            customer_name_db_new_3 = result['customer_name'].values[0]
            created_time_db_new_3 = result['created_time'].values[0]
            status_db_new_3 = result["status"].iloc[0]
            payment_mode_db_new_3 = result["payment_mode"].iloc[0]
            amount_db_new_3 = float(result["amount"].iloc[0])
            state_db_new_3 = result["state"].iloc[0]
            payment_gateway_db_new_3 = result["payment_gateway"].iloc[0]
            acquirer_code_db_new_3 = result["acquirer_code"].iloc[0]
            settlement_status_db_new_3 = result["settlement_status"].iloc[0]
            tid_db_new_3 = result['tid'].values[0]
            mid_db_new_3 = result['mid'].values[0]

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
                date_new = date_time_converter.db_datetime(created_time_db)
                date_new_2 = date_time_converter.db_datetime(created_time_db_new_2)
                date_new_3 = date_time_converter.db_datetime(created_time_db_new_3)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "REFUNDED",
                    "rrn": bank_rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "org_code": org_code,
                    "date": date_new,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(first_refund_amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "txn_type_2": "REFUND",
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date_2": date_new_2,
                    "pmt_status_3": "REFUNDED",
                    "txn_amt_3": float(second_refund_amount),
                    "pmt_mode_3": "UPI",
                    "pmt_state_3": "REFUNDED",
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "ICICI",
                    "txn_type_3": "REFUND",
                    "virtual_mid_3": virtual_mid,
                    "virtual_tid_3": virtual_tid,
                    "org_code_3": org_code,
                    "date_3": date_new_3
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
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
                response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_2 = response["status"]
                amount_api_new_2 = float(response["amount"])
                payment_mode_api_new_2 = response["paymentMode"]
                state_api_new_2 = response["states"][0]
                settlement_status_api_new_2 = response["settlementStatus"]
                acquirer_code_api_new_2 = response["acquirerCode"]
                orgCode_api_new_2 = response["orgCode"]
                mid_api_new_2 = response["mid"]
                tid_api_new_2 = response["tid"]
                txn_type_api_new_2 = response["txnType"]
                date_api_new_2 = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_3][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_3 = response["status"]
                amount_api_new_3 = float(response["amount"])
                payment_mode_api_new_3 = response["paymentMode"]
                state_api_new_3 = response["states"][0]
                settlement_status_api_new_3 = response["settlementStatus"]
                acquirer_code_api_new_3 = response["acquirerCode"]
                orgCode_api_new_3 = response["orgCode"]
                mid_api_new_3 = response["mid"]
                tid_api_new_3 = response["tid"]
                txn_type_api_new_3 = response["txnType"]
                date_api_new_3 = response["createdTime"]

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
                    "virtual_mid": mid_api,
                    "virtual_tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2,
                    "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2,
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2,
                    "virtual_mid_2": mid_api_new_2,
                    "virtual_tid_2": tid_api_new_2,
                    "org_code_2": orgCode_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2),
                    "pmt_status_3": status_api_new_3,
                    "txn_amt_3": amount_api_new_3,
                    "pmt_mode_3": payment_mode_api_new_3,
                    "pmt_state_3": state_api_new_3,
                    "settle_status_3": settlement_status_api_new_3,
                    "acquirer_code_3": acquirer_code_api_new_3,
                    "txn_type_3": txn_type_api_new_3,
                    "virtual_mid_3": mid_api_new_3,
                    "virtual_tid_3": tid_api_new_3,
                    "org_code_3": orgCode_api_new_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_new_3),

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
                    "rrn": bank_rrn,
                    "pmt_mode": "UPI",
                    "customer_name": cust_name,
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "payment_gateway": "ICICI",
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "customer_name_2": cust_name,
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(first_refund_amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "payment_gateway_2": "ICICI",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                    "pmt_status_3": "REFUNDED",
                    "pmt_state_3": "REFUNDED",
                    "pmt_mode_3": "UPI",
                    "txn_amt_3": float(second_refund_amount),
                    "settle_status_3": "SETTLED",
                    "customer_name_3": cust_name,
                    "acquirer_code_3": "ICICI",
                    "payment_gateway_3": "ICICI",
                    "upi_txn_status_3": "REFUNDED",
                    "upi_txn_type_3": "REFUND",
                    "upi_bank_code_3": "ICICI_DIRECT",
                    "upi_mc_id_3": upi_mc_id,
                    "virtual_mid_3": virtual_mid,
                    "virtual_tid_3": virtual_tid,

                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_2 = result["status"].iloc[0]
                upi_txn_type_db_new_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_2 = result["upi_mc_id"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_3 = result["status"].iloc[0]
                upi_txn_type_db_new_3 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_3 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_3 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "rrn": rrn_db,
                    "customer_name": customer_name_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "virtual_mid": mid_db,
                    "virtual_tid": tid_db,
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "customer_name_2": customer_name_db_new_2,
                    "upi_txn_status_2": upi_status_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "virtual_mid_2": mid_db_new_2,
                    "virtual_tid_2": tid_db_new_2,
                    "pmt_status_3": status_db_new_3,
                    "pmt_state_3": state_db_new_3,
                    "pmt_mode_3": payment_mode_db_new_3,
                    "customer_name_3": customer_name_db_new_3,
                    "txn_amt_3": amount_db_new_3,
                    "upi_txn_status_3": upi_status_db_new_3,
                    "settle_status_3": settlement_status_db_new_3,
                    "acquirer_code_3": acquirer_code_db_new_3,
                    "payment_gateway_3": payment_gateway_db_new_3,
                    "upi_txn_type_3": upi_txn_type_db_new_3,
                    "upi_bank_code_3": upi_bank_code_db_new_3,
                    "upi_mc_id_3": upi_mc_id_db_new_3,
                    "virtual_mid_3": mid_db_new_3,
                    "virtual_tid_3": tid_db_new_3,
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
def test_d102_108_016():
    """
    Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Partial_Refund_WholeAmt_And_Decimal_ICICI_DIRECT
    Sub Feature Description: Verification of a staticQR BQRV4 UPI partial Refund Two Times with whole amt and decimal via ICICI_DIRECT
    TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRv4 StaticQR, 016-> Testcase ID
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
        # -----------------------------------------PreConditions(Completed)-----------------------------
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

            amount = random.randint(225, 300)
            first_refund_amount = amount - 10
            second_refund_amount = 5.05

            cust_name = "Automation user"
            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
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
                "PayerName": cust_name,
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

            txn_id = response["merchantTranId"]

            # Do First Refund
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(first_refund_amount),
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")
            txn_id_2 = response['txnId']

            # Do Second Refund
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                     request_body={"username": app_username, "password": app_password,
                                                                   "amount": str(second_refund_amount),
                                                                   "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request for refund txn : {response}")
            txn_id_3 = response['txnId']

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            rrn_db = result['rr_number'].values[0]
            customer_name_db = result['customer_name'].values[0]
            created_time_db = result['created_time'].values[0]
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

            query = "select * from txn where id = '" + str(txn_id_2) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            customer_name_db_new_2 = result['customer_name'].values[0]
            created_time_db_new_2 = result['created_time'].values[0]
            status_db_new_2 = result["status"].iloc[0]
            payment_mode_db_new_2 = result["payment_mode"].iloc[0]
            amount_db_new_2 = float(result["amount"].iloc[0])
            state_db_new_2 = result["state"].iloc[0]
            payment_gateway_db_new_2 = result["payment_gateway"].iloc[0]
            acquirer_code_db_new_2 = result["acquirer_code"].iloc[0]
            settlement_status_db_new_2 = result["settlement_status"].iloc[0]
            tid_db_new_2 = result['tid'].values[0]
            mid_db_new_2 = result['mid'].values[0]

            query = "select * from txn where id = '" + str(txn_id_3) + "';"
            logger.debug(f"Query to fetch details of second txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            customer_name_db_new_3 = result['customer_name'].values[0]
            created_time_db_new_3 = result['created_time'].values[0]
            status_db_new_3 = result["status"].iloc[0]
            payment_mode_db_new_3 = result["payment_mode"].iloc[0]
            amount_db_new_3 = float(result["amount"].iloc[0])
            state_db_new_3 = result["state"].iloc[0]
            payment_gateway_db_new_3 = result["payment_gateway"].iloc[0]
            acquirer_code_db_new_3 = result["acquirer_code"].iloc[0]
            settlement_status_db_new_3 = result["settlement_status"].iloc[0]
            tid_db_new_3 = result['tid'].values[0]
            mid_db_new_3 = result['mid'].values[0]

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
                date_new = date_time_converter.db_datetime(created_time_db)
                date_new_2 = date_time_converter.db_datetime(created_time_db_new_2)
                date_new_3 = date_time_converter.db_datetime(created_time_db_new_3)

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
                    "date": date_new,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(first_refund_amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "txn_type_2": "REFUND",
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date_2": date_new_2,
                    "pmt_status_3": "REFUNDED",
                    "txn_amt_3": float(second_refund_amount),
                    "pmt_mode_3": "UPI",
                    "pmt_state_3": "REFUNDED",
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "ICICI",
                    "txn_type_3": "REFUND",
                    "virtual_mid_3": virtual_mid,
                    "virtual_tid_3": virtual_tid,
                    "org_code_3": org_code,
                    "date_3": date_new_3
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
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
                response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_2 = response["status"]
                amount_api_new_2 = float(response["amount"])
                payment_mode_api_new_2 = response["paymentMode"]
                state_api_new_2 = response["states"][0]
                settlement_status_api_new_2 = response["settlementStatus"]
                acquirer_code_api_new_2 = response["acquirerCode"]
                orgCode_api_new_2 = response["orgCode"]
                mid_api_new_2 = response["mid"]
                tid_api_new_2 = response["tid"]
                txn_type_api_new_2 = response["txnType"]
                date_api_new_2 = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_3][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new_3 = response["status"]
                amount_api_new_3 = float(response["amount"])
                payment_mode_api_new_3 = response["paymentMode"]
                state_api_new_3 = response["states"][0]
                settlement_status_api_new_3 = response["settlementStatus"]
                acquirer_code_api_new_3 = response["acquirerCode"]
                orgCode_api_new_3 = response["orgCode"]
                mid_api_new_3 = response["mid"]
                tid_api_new_3 = response["tid"]
                txn_type_api_new_3 = response["txnType"]
                date_api_new_3 = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": rrn_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "virtual_mid": mid_api,
                    "virtual_tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new_2,
                    "txn_amt_2": amount_api_new_2,
                    "pmt_mode_2": payment_mode_api_new_2,
                    "pmt_state_2": state_api_new_2,
                    "settle_status_2": settlement_status_api_new_2,
                    "acquirer_code_2": acquirer_code_api_new_2,
                    "txn_type_2": txn_type_api_new_2,
                    "virtual_mid_2": mid_api_new_2,
                    "virtual_tid_2": tid_api_new_2,
                    "org_code_2": orgCode_api_new_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new_2),
                    "pmt_status_3": status_api_new_3,
                    "txn_amt_3": amount_api_new_3,
                    "pmt_mode_3": payment_mode_api_new_3,
                    "pmt_state_3": state_api_new_3,
                    "settle_status_3": settlement_status_api_new_3,
                    "acquirer_code_3": acquirer_code_api_new_3,
                    "txn_type_3": txn_type_api_new_3,
                    "virtual_mid_3": mid_api_new_3,
                    "virtual_tid_3": tid_api_new_3,
                    "org_code_3": orgCode_api_new_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_new_3),
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
                    "customer_name": cust_name,
                    "rrn": bank_rrn,
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "payment_gateway": "ICICI",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "virtual_mid": virtual_mid,
                    "virtual_tid": virtual_tid,
                    "pmt_status_2": "REFUNDED",
                    "customer_name_2": cust_name,
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(first_refund_amount),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "payment_gateway_2": "ICICI",
                    "upi_txn_status_2": "REFUNDED",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "virtual_mid_2": virtual_mid,
                    "virtual_tid_2": virtual_tid,
                    "pmt_status_3": "REFUNDED",
                    "customer_name_3": cust_name,
                    "pmt_state_3": "REFUNDED",
                    "pmt_mode_3": "UPI",
                    "txn_amt_3": float(second_refund_amount),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "ICICI",
                    "payment_gateway_3": "ICICI",
                    "upi_txn_status_3": "REFUNDED",
                    "upi_txn_type_3": "REFUND",
                    "upi_bank_code_3": "ICICI_DIRECT",
                    "upi_mc_id_3": upi_mc_id,
                    "virtual_mid_3": virtual_mid,
                    "virtual_tid_3": virtual_tid,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_2 = result["status"].iloc[0]
                upi_txn_type_db_new_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_2 = result["upi_mc_id"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_3 = result["status"].iloc[0]
                upi_txn_type_db_new_3 = result["txn_type"].iloc[0]
                upi_bank_code_db_new_3 = result["bank_code"].iloc[0]
                upi_mc_id_db_new_3 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "rrn": rrn_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "customer_name": customer_name_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "virtual_mid": mid_db,
                    "virtual_tid": tid_db,
                    "pmt_status_2": status_db_new_2,
                    "pmt_state_2": state_db_new_2,
                    "customer_name_2": customer_name_db_new_2,
                    "pmt_mode_2": payment_mode_db_new_2,
                    "txn_amt_2": amount_db_new_2,
                    "upi_txn_status_2": upi_status_db_new_2,
                    "settle_status_2": settlement_status_db_new_2,
                    "acquirer_code_2": acquirer_code_db_new_2,
                    "payment_gateway_2": payment_gateway_db_new_2,
                    "upi_txn_type_2": upi_txn_type_db_new_2,
                    "upi_bank_code_2": upi_bank_code_db_new_2,
                    "upi_mc_id_2": upi_mc_id_db_new_2,
                    "virtual_mid_2": mid_db_new_2,
                    "virtual_tid_2": tid_db_new_2,
                    "pmt_status_3": status_db_new_3,
                    "pmt_state_3": state_db_new_3,
                    "customer_name_3": customer_name_db_new_3,
                    "pmt_mode_3": payment_mode_db_new_3,
                    "txn_amt_3": amount_db_new_3,
                    "upi_txn_status_3": upi_status_db_new_3,
                    "settle_status_3": settlement_status_db_new_3,
                    "acquirer_code_3": acquirer_code_db_new_3,
                    "payment_gateway_3": payment_gateway_db_new_3,
                    "upi_txn_type_3": upi_txn_type_db_new_3,
                    "upi_bank_code_3": upi_bank_code_db_new_3,
                    "upi_mc_id_3": upi_mc_id_db_new_3,
                    "virtual_mid_3": mid_db_new_3,
                    "virtual_tid_3": tid_db_new_3,
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