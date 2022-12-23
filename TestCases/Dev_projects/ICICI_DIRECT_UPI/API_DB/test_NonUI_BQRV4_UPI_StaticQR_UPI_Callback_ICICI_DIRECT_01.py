import random
import sys
import pytest
from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, date_time_converter, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d102_108_005():
    """
    Sub Feature Code: NonUI_Common_StaticQR_BQRV4_UPI_Callback_Success_ICICI_DIRECT
    Sub Feature Description: Performing static QR callback success for BQRV4 via ICICI DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 108: UPI STATIC QR, 005: TC005
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
        logger.debug(f"app_username is : {app_username}")
        app_password = app_cred['Password']
        logger.debug(f"app_password is : {app_password}")

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        logger.debug(f"portal_username is : {portal_username}")
        portal_password = portal_cred['Password']
        logger.debug(f"portal_password is : {portal_password}")

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_employee from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"org_code is : {org_code}")
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"mobile_number is : {mobile_number}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4',
                                                           bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"fetched data from the upi_merchant_config : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa is : {vpa}")
        upi_mc_virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched upi_mc_virtual_tid is : {upi_mc_virtual_tid}")
        upi_mc_virtual_mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched upi_mc_virtual_mid is : {upi_mc_virtual_mid}")

        query = "select * from bharatqr_merchant_config where org_code='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"fetched data from the bharatqr_merchant_config s: {result}")
        terminal_info_id = result["terminal_info_id"].iloc[0]
        logger.debug(f"fetched terminal_info_id is : {terminal_info_id}")
        bqr_mc_id = result["id"].iloc[0]
        logger.debug(f"fetched bqr_mc_id is : {bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].iloc[0]
        logger.debug(f"fetched bqr_m_pan is : {bqr_m_pan}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid is : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid is : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            #to generate the STATIC QR For ICICI DIRECT
            api_details = DBProcessor.get_api_details('static_qrcode_generate_hdfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of static_qrcode_generate_hdfc is : {response}")
            publish_id = response["publishId"]
            logger.debug(f"Response of publish_id is : {publish_id}")
            success_api = response["success"]
            logger.debug(f"Response of success_api is : {success_api}")
            username_api = response["username"]
            logger.debug(f"Response of username_api is : {username_api}")
            mid_api = response["mid"]
            logger.debug(f"Response of mid_api is : {mid_api}")
            tid_api = response["tid"]
            logger.debug(f"Response of tid_api is : {tid_api}")

            amount = random.randint(500,800)
            logger.debug(f"amount is : {amount}")
            rrn = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(f"rrn is : {rrn}")

            #Callback Generator ICICI
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": upi_mc_virtual_mid,
                "subMerchantId": upi_mc_virtual_mid,
                "terminalId": upi_mc_virtual_tid,
                "merchantTranId": publish_id[3:],
                "PayerAmount": "{:.2f}".format(amount),
                "BankRRN": rrn,
                "TxnStatus": "SUCCESS"
            })
            callback_generator_icici_response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of callbackgeneratorUpiICICI is : {callback_generator_icici_response}")

            #ICICI Callback URL: Pass the response obtained from Callback Generator ICICI as a request body
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body= callback_generator_icici_response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of callbackUpiICICI is : {response}")
            merchant_tran_id = response["merchantTranId"]
            logger.debug(f"merchant_tran_id is : {merchant_tran_id}")

            query = "select * from txn where id = '" + merchant_tran_id + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to fetch result is : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")

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
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": 'CHARGE',
                    "mid": upi_mc_virtual_mid,
                    "tid": upi_mc_virtual_tid,
                    "org_code": org_code,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                "username": app_username,
                "password": app_password
                })

                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == merchant_tran_id][0]   #passing the merchant_tran_id here
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"status_api is : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"amount_api is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api is : {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api is : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api is : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api is : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"date_api is : {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
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
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "SETTLED",
                    "txn_type": "CHARGE",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "mid": upi_mc_virtual_mid,
                    "tid": upi_mc_virtual_tid,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" +merchant_tran_id + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table is : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db is : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db is : {payment_mode_db}")
                amount_db = float(result["amount"].iloc[0])
                logger.debug(f"amount_db is : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db is : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db is : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db is : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db is : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db is : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"tid_db is : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"mid_db is : {mid_db}")
                txn_type_db = result['txn_type'].values[0]
                logger.debug(f"txn_type_db is : {txn_type_db}")

                query = "select * from upi_txn where txn_id='" + merchant_tran_id + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table is : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db is : {upi_mc_id_db}")

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
                    "mid": mid_db,
                    "tid": tid_db,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
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
def test_d102_108_006():
    """
    Sub Feature Code: NonUI_Common_StaticQR_BQRV4_UPI_Callback_Failed_ICICI_DIRECT
    Sub Feature Description: Performing static QR callback Failed for BQRV4 via ICICI DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 107: UPI STATIC QR, 006: TC006
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
        logger.debug(f"app_username is : {app_username}")
        app_password = app_cred['Password']
        logger.debug(f"app_password is : {app_password}")

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        logger.debug(f"portal_username is : {portal_username}")
        portal_password = portal_cred['Password']
        logger.debug(f"portal_password is : {portal_password}")

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_employee from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"org_code is : {org_code}")
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"mobile_number is : {mobile_number}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4',
                                                           bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"fetched data from the upi_merchant_config : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa is : {vpa}")
        upi_mc_virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched upi_mc_virtual_tid is : {upi_mc_virtual_tid}")
        upi_mc_virtual_mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched upi_mc_virtual_mid is : {upi_mc_virtual_mid}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"fetched data from the bharatqr_merchant_config s: {result}")
        terminal_info_id = result["terminal_info_id"].iloc[0]
        logger.debug(f"fetched terminal_info_id is : {terminal_info_id}")
        bqr_mc_id = result["id"].iloc[0]
        logger.debug(f"fetched bqr_mc_id is : {bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].iloc[0]
        logger.debug(f"fetched bqr_m_pan is : {bqr_m_pan}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid is : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid is : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            #to generate the STATIC QR For ICICI DIRECT
            api_details = DBProcessor.get_api_details('static_qrcode_generate_hdfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of static_qrcode_generate_hdfc is : {response}")
            publish_id = response["publishId"]
            logger.debug(f"Response of publish_id is : {publish_id}")
            success_api = response["success"]
            logger.debug(f"Response of success_api is : {success_api}")
            username_api = response["username"]
            logger.debug(f"Response of username_api is : {username_api}")
            mid_api = response["mid"]
            logger.debug(f"Response of mid_api is : {mid_api}")
            tid_api = response["tid"]
            logger.debug(f"Response of tid_api is : {tid_api}")

            amount = random.randint(500,800)
            logger.debug(f"amount is : {amount}")
            rrn = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(f"rrn is : {rrn}")

            #Callback Generator ICICI
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": upi_mc_virtual_mid,
                "subMerchantId": upi_mc_virtual_mid,
                "terminalId": upi_mc_virtual_tid,
                "merchantTranId": publish_id[3:],
                "PayerAmount": "{:.2f}".format(amount),
                "BankRRN": rrn,
                "TxnStatus": "FAILED"
            })

            callback_generator_icici_response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of callbackgeneratorUpiICICI is : {callback_generator_icici_response}")

            # ICICI Callback URL: Pass the response obtained from Callback Generator ICICI as a request body
            api_details = DBProcessor.get_api_details('callbackUpiICICI',
                                                      request_body=callback_generator_icici_response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of callbackUpiICICI is : {response}")
            merchant_tran_id = response["merchantTranId"]
            logger.debug(f"merchant_tran_id is : {merchant_tran_id}")

            query = "select * from txn where id = '" + merchant_tran_id + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to fetch result is : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")

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
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": 'CHARGE',
                    "mid": upi_mc_virtual_mid,
                    "tid": upi_mc_virtual_tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == merchant_tran_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"status_api is : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"amount_api is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api is : {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api is : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api is : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api is : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"date_api is : {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
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
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "FAILED",
                    "txn_type": "CHARGE",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "mid": upi_mc_virtual_mid,
                    "tid": upi_mc_virtual_tid,
                    "upi_txn_status": "FAILED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + merchant_tran_id + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table is : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db is : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db is : {payment_mode_db}")
                amount_db = float(result["amount"].iloc[0])
                logger.debug(f"amount_db is : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db is : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db is : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db is : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db is : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db is : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"tid_db is : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"mid_db is : {mid_db}")
                txn_type_db = result['txn_type'].values[0]
                logger.debug(f"txn_type_db is : {txn_type_db}")

                query = "select * from upi_txn where txn_id='" + merchant_tran_id + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table is : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db is : {upi_mc_id_db}")

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
                    "mid": mid_db,
                    "tid": tid_db,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
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
def test_d102_108_007():
    """
    Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Two_Success_Callback_Same_RRN_ICICI_DIRECT
    Sub Feature Description: Verification of a staticQR BQRV4 UPI Two Success Callbacks with same RRN via ICICI_DIRECT
    TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRv4 StaticQR, 007-> Tesctcase ID
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
            logger.debug(f"fetching publish_id, username from api response is : "f"{publish_id}")

            amount = random.randint(225, 300)
            bank_rrn = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            customer_name = "Automation user"
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI first callback generator API
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

            # Call first UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for first callback api is : {response}")
            first_callback_txn_id = response["merchantTranId"]

            # Call UPI second callback generator API
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

            # Call second UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for second callback api is : {response}")
            second_callback_txn_id = response["merchantTranId"]

            query = "select * from txn where id = '" + str(first_callback_txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            txn_amt_db_1 = result['amount'].values[0]
            acquirer_code_db_1 = result['acquirer_code'].values[0]
            cust_name_db_1 = result['customer_name'].values[0]
            bank_code_db_1 = result['bank_code'].values[0]
            org_code_db_1 = result['org_code'].values[0]
            pmt_gateway_db_1 = result['payment_gateway'].values[0]
            pmt_mode_db_1 = result['payment_mode'].values[0]
            settlement_status_db_1 = result['settlement_status'].values[0]
            status_db_1 = result['status'].values[0]
            txn_type_db_1 = result['txn_type'].values[0]
            pmt_state_db_1 = result['state'].iloc[0]
            tid_db_1 = result['tid'].values[0]
            mid_db_1 = result['mid'].values[0]
            rrn_db_1 = result['rr_number'].values[0]
            created_time_db_1 = result['created_time'].values[0]

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
                date = date_time_converter.db_datetime(created_time_db_1)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(bank_rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "org_code": org_code,
                    "date": date,
                    "txn_id": first_callback_txn_id
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
                    if elements["txnId"] == first_callback_txn_id:
                        status_api_1 = elements["status"]
                        amount_api_1 = float(elements["amount"])
                        payment_mode_api_1 = elements["paymentMode"]
                        state_api_1 = elements["states"][0]
                        rrn_api_1 = elements["rrNumber"]
                        settlement_status_api_1 = elements["settlementStatus"]
                        issuer_code_api_1 = elements["issuerCode"]
                        acquirer_code_api_1 = elements["acquirerCode"]
                        orgCode_api_1 = elements["orgCode"]
                        mid_api_1 = elements["mid"]
                        tid_api_1 = elements["tid"]
                        txn_type_api_1 = elements["txnType"]
                        date_api_1 = elements["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api_1,
                    "txn_amt": amount_api_1,
                    "pmt_mode": payment_mode_api_1,
                    "pmt_state": state_api_1,
                    "rrn": rrn_api_1,
                    "settle_status": settlement_status_api_1,
                    "acquirer_code": acquirer_code_api_1,
                    "issuer_code": issuer_code_api_1,
                    "txn_type": txn_type_api_1,
                    "mid": mid_api_1,
                    "tid": tid_api_1,
                    "org_code": orgCode_api_1,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_1),
                    "txn_id": second_callback_txn_id
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
                    "txn_type": "CHARGE",
                    "rrn": str(bank_rrn),
                    "customer_name": customer_name,
                    "org_code": org_code,
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "txn_id": first_callback_txn_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + first_callback_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_1 = result["status"].iloc[0]
                upi_txn_type_db_1 = result["txn_type"].iloc[0]
                upi_bank_code_db_1 = result["bank_code"].iloc[0]
                upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_1,
                    "pmt_state": pmt_state_db_1,
                    "pmt_mode": pmt_mode_db_1,
                    "txn_amt": txn_amt_db_1,
                    "rrn": rrn_db_1,
                    "customer_name": cust_name_db_1,
                    "org_code": org_code_db_1,
                    "txn_type": txn_type_db_1,
                    "upi_txn_status": upi_status_db_1,
                    "settle_status": settlement_status_db_1,
                    "acquirer_code": acquirer_code_db_1,
                    "bank_code": bank_code_db_1,
                    "pmt_gateway": pmt_gateway_db_1,
                    "upi_txn_type": upi_txn_type_db_1,
                    "upi_bank_code": upi_bank_code_db_1,
                    "upi_mc_id": upi_mc_id_db_1,
                    "mid": mid_db_1,
                    "tid": tid_db_1,
                    "txn_id": second_callback_txn_id
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
def test_d102_108_017():
    """
    Sub Feature Code: NonUI_Common_BQRV4_UPI_StaticQR_Two_Success_Callback_Different_RRN_ICICI_DIRECT
    Sub Feature Description: Verification of a staticQR BQRV4 UPI Two Success Callbacks with Different RRN via ICICI_DIRECT
    TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRv4 StaticQR, 017-> Tesctcase ID
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
            logger.debug(f"fetching publish_id, username from api response is : "f"{publish_id}")

            amount = random.randint(225, 300)
            bank_rrn_1 = str(random.randint(100000000000, 999999999999))
            merchant_tran_id = publish_id.split('GTZ')[1]
            customer_name = "Automation user"
            logger.debug(f"initiating upi qr callback for the amount of {amount}")

            # Call UPI first callback generator API
            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn_1,
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

            # Call first UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for first callback api is : {response}")
            first_callback_txn_id = response["merchantTranId"]

            # Call UPI second callback generator API
            bank_rrn_2 = str(random.randint(100000000000, 999999999999))

            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": pg_merchant_id,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "BankRRN": bank_rrn_2,
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

            # Call second UPI callback
            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for second callback api is : {response}")
            second_callback_txn_id = response["merchantTranId"]

            query = "select * from txn where id = '" + str(first_callback_txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            txn_amt_db_1 = result['amount'].values[0]
            acquirer_code_db_1 = result['acquirer_code'].values[0]
            cust_name_db_1 = result['customer_name'].values[0]
            bank_code_db_1 = result['bank_code'].values[0]
            org_code_db_1 = result['org_code'].values[0]
            pmt_gateway_db_1 = result['payment_gateway'].values[0]
            pmt_mode_db_1 = result['payment_mode'].values[0]
            settlement_status_db_1 = result['settlement_status'].values[0]
            status_db_1 = result['status'].values[0]
            txn_type_db_1 = result['txn_type'].values[0]
            pmt_state_db_1 = result['state'].iloc[0]
            tid_db_1 = result['tid'].values[0]
            mid_db_1 = result['mid'].values[0]
            rrn_db_1 = result['rr_number'].values[0]
            created_time_db_1 = result['created_time'].values[0]

            query = "select * from txn where id = '" + str(second_callback_txn_id) + "';"
            logger.debug(f"Query to fetch details of original txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            txn_amt_db_2 = result['amount'].values[0]
            acquirer_code_db_2 = result['acquirer_code'].values[0]
            cust_name_db_2 = result['customer_name'].values[0]
            bank_code_db_2 = result['bank_code'].values[0]
            org_code_db_2 = result['org_code'].values[0]
            pmt_gateway_db_2 = result['payment_gateway'].values[0]
            pmt_mode_db_2 = result['payment_mode'].values[0]
            settlement_status_db_2 = result['settlement_status'].values[0]
            status_db_2 = result['status'].values[0]
            txn_type_db_2 = result['txn_type'].values[0]
            pmt_state_db_2 = result['state'].iloc[0]
            tid_db_2 = result['tid'].values[0]
            mid_db_2 = result['mid'].values[0]
            rrn_db_2 = result['rr_number'].values[0]
            created_time_db_2 = result['created_time'].values[0]

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
                date = date_time_converter.db_datetime(created_time_db_1)
                date_2 = date_time_converter.db_datetime(created_time_db_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(bank_rrn_1),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": "CHARGE",
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(bank_rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "issuer_code_2": "ICICI",
                    "txn_type_2": "CHARGE",
                    "mid_2": virtual_mid,
                    "tid_2": virtual_tid,
                    "org_code_2": org_code,
                    "date_2": date_2
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
                    if elements["txnId"] == first_callback_txn_id:
                        status_api_1 = elements["status"]
                        amount_api_1 = float(elements["amount"])
                        payment_mode_api_1 = elements["paymentMode"]
                        state_api_1 = elements["states"][0]
                        rrn_api_1 = elements["rrNumber"]
                        settlement_status_api_1 = elements["settlementStatus"]
                        issuer_code_api_1 = elements["issuerCode"]
                        acquirer_code_api_1 = elements["acquirerCode"]
                        orgCode_api_1 = elements["orgCode"]
                        mid_api_1 = elements["mid"]
                        tid_api_1 = elements["tid"]
                        txn_type_api_1 = elements["txnType"]
                        date_api_1 = elements["createdTime"]
                for elements in responseInList:
                    if elements["txnId"] == second_callback_txn_id:
                        status_api_2 = elements["status"]
                        amount_api_2 = float(elements["amount"])
                        payment_mode_api_2 = elements["paymentMode"]
                        state_api_2 = elements["states"][0]
                        rrn_api_2 = elements["rrNumber"]
                        settlement_status_api_2 = elements["settlementStatus"]
                        issuer_code_api_2 = elements["issuerCode"]
                        acquirer_code_api_2 = elements["acquirerCode"]
                        orgCode_api_2 = elements["orgCode"]
                        mid_api_2 = elements["mid"]
                        tid_api_2 = elements["tid"]
                        txn_type_api_2 = elements["txnType"]
                        date_api_2 = elements["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api_1,
                    "txn_amt": amount_api_1,
                    "pmt_mode": payment_mode_api_1,
                    "pmt_state": state_api_1,
                    "rrn": rrn_api_1,
                    "settle_status": settlement_status_api_1,
                    "acquirer_code": acquirer_code_api_1,
                    "issuer_code": issuer_code_api_1,
                    "txn_type": txn_type_api_1,
                    "mid": mid_api_1,
                    "tid": tid_api_1,
                    "org_code": orgCode_api_1,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_1),
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": rrn_api_2,
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "txn_type": "CHARGE",
                    "rrn": str(bank_rrn_1),
                    "customer_name": customer_name,
                    "org_code": org_code,
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "txn_type_2": "CHARGE",
                    "rrn_2": str(bank_rrn_2),
                    "customer_name_2": customer_name,
                    "org_code_2": org_code,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "ICICI",
                    "bank_code_2": "ICICI",
                    "pmt_gateway_2": "ICICI",
                    "upi_txn_status_2": "AUTHORIZED",
                    "upi_txn_type_2": "STATIC_QR",
                    "upi_bank_code_2": "ICICI_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": virtual_mid,
                    "tid_2": virtual_tid,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + first_callback_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_1 = result["status"].iloc[0]
                upi_txn_type_db_1 = result["txn_type"].iloc[0]
                upi_bank_code_db_1 = result["bank_code"].iloc[0]
                upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = "select * from upi_txn where txn_id='" + second_callback_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db_1,
                    "pmt_state": pmt_state_db_1,
                    "pmt_mode": pmt_mode_db_1,
                    "txn_amt": txn_amt_db_1,
                    "rrn": rrn_db_1,
                    "customer_name": cust_name_db_1,
                    "org_code": org_code_db_1,
                    "txn_type": txn_type_db_1,
                    "upi_txn_status": upi_status_db_1,
                    "settle_status": settlement_status_db_1,
                    "acquirer_code": acquirer_code_db_1,
                    "bank_code": bank_code_db_1,
                    "pmt_gateway": pmt_gateway_db_1,
                    "upi_txn_type": upi_txn_type_db_1,
                    "upi_bank_code": upi_bank_code_db_1,
                    "upi_mc_id": upi_mc_id_db_1,
                    "mid": mid_db_1,
                    "tid": tid_db_1,
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": pmt_state_db_2,
                    "pmt_mode_2": pmt_mode_db_2,
                    "txn_amt_2": txn_amt_db_2,
                    "rrn_2": rrn_db_2,
                    "customer_name_2": cust_name_db_2,
                    "org_code_2": org_code_db_2,
                    "txn_type_2": txn_type_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "pmt_gateway_2": pmt_gateway_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
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
def test_d102_108_020():
    """
    Sub Feature Code: NonUI_Common_BQRV4_StaticQR_BQR_Callback_Success_ICICI_DIRECT
    Sub Feature Description: Verification of a staticQR BQRV4 BQR callback Success via ICICI_DIRECT
    TC naming code description:: d102->Dev Project[ICICI_DIRECT_UPI], 108->BQRv4 StaticQR, 020-> Tesctcase ID
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
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

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

            # Call generate BQRV4 API
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
            logger.debug(f"fetching publish_id, username from api response is : "f"{publish_id}")

            # amount = random.randint(225, 300)
            # bank_rrn = str(random.randint(100000000000, 999999999999))
            # merchant_tran_id = publish_id.split('GTZ')[1]
            # customer_name = "Automation user"
            # logger.debug(f"initiating upi qr callback for the amount of {amount}")

            amount = random.randint(301, 399)
            logger.debug(f"generated random amount is : {amount}")

            auth_code = "A" + publish_id[-10:]
            rrn_num = "R" + publish_id[-10:]

            # Do BQR callback
            api_details = DBProcessor.get_api_details('callbackHDFC', request_body={
                "PRIMARY_ID": publish_id,
                "SECONDARY_ID": "",
                "MERCHANT_PAN": db_bqr_config_merchant_pan,
                "TXN_ID": publish_id,
                "TXN_AMOUNT": amount,
                "AUTH_CODE": auth_code,
                "RRN": rrn_num,

            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for BQR callback : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(
                rrn_num) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table : {query}")

            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")

            txn_id = result["id"].iloc[0]

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch details of original BQR txn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)

            txn_amt_db = result['amount'].values[0]
            acquirer_code_db = result['acquirer_code'].values[0]
            bank_code_db = result['bank_code'].values[0]
            org_code_db = result['org_code'].values[0]
            pmt_gateway_db = result['payment_gateway'].values[0]
            pmt_mode_db = result['payment_mode'].values[0]
            settlement_status_db = result['settlement_status'].values[0]
            status_db = result['status'].values[0]
            txn_type_db = result['txn_type'].values[0]
            pmt_state_db = result['state'].iloc[0]
            tid_db_1 = result['tid'].values[0]
            mid_db_1 = result['mid'].values[0]
            rrn_db = result['rr_number'].values[0]
            created_time_db_1 = result['created_time'].values[0]

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
                date = date_time_converter.db_datetime(created_time_db_1)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn_num),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date
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
                    if elements["txnId"] == txn_id:
                        status_api_1 = elements["status"]
                        amount_api_1 = float(elements["amount"])
                        payment_mode_api_1 = elements["paymentMode"]
                        state_api_1 = elements["states"][0]
                        rrn_api_1 = elements["rrNumber"]
                        settlement_status_api_1 = elements["settlementStatus"]
                        issuer_code_api_1 = elements["issuerCode"]
                        acquirer_code_api_1 = elements["acquirerCode"]
                        orgCode_api_1 = elements["orgCode"]
                        mid_api_1 = elements["mid"]
                        tid_api_1 = elements["tid"]
                        txn_type_api_1 = elements["txnType"]
                        date_api_1 = elements["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api_1,
                    "txn_amt": amount_api_1,
                    "pmt_mode": payment_mode_api_1,
                    "pmt_state": state_api_1,
                    "rrn": rrn_api_1,
                    "settle_status": settlement_status_api_1,
                    "acquirer_code": acquirer_code_api_1,
                    "issuer_code": issuer_code_api_1,
                    "txn_type": txn_type_api_1,
                    "mid": mid_api_1,
                    "tid": tid_api_1,
                    "org_code": orgCode_api_1,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_1)
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
                    "txn_type": "CHARGE",
                    "rrn": str(rrn_num),
                    "org_code": org_code,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "bqr_status_desc": "Transaction Success",
                    "bqr_txn_type": "STATIC_QR",
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_pan": db_bqr_config_merchant_pan,
                    "bqr_state": "SETTLED",
                    "bqr_rrn": rrn_num,
                    "bqr_auth_code": auth_code,
                    "bqr_txn_amt": amount,
                    "bqr_ref_id": publish_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_status_desc_db = result["status_desc"].iloc[0]
                bqr_mpan_db = result["merchant_pan"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_rrn_db = result["rrn"].iloc[0]
                bqr_auth_code_db = result["txn_auth_code"].iloc[0]
                bqr_amt_db = result["txn_amount"].iloc[0]
                bqr_ref_id_db = result["provider_ref_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": pmt_state_db,
                    "pmt_mode": pmt_mode_db,
                    "txn_amt": txn_amt_db,
                    "txn_type": txn_type_db,
                    "rrn": rrn_db,
                    "org_code": org_code_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": pmt_gateway_db,
                    "bqr_status_desc": bqr_status_desc_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_pan": bqr_mpan_db,
                    "bqr_state": bqr_state_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_auth_code": bqr_auth_code_db,
                    "bqr_txn_amt": bqr_amt_db,
                    "bqr_ref_id": bqr_ref_id_db
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
