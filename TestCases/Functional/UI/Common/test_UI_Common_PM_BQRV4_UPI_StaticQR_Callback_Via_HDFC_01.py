import sys
import random
import pytest

from Configuration import testsuite_teardown, Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, Validator, date_time_converter, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_108_003():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Callback_Success_AutoRefund_Enabled_Via_HDFC
    Sub Feature Description: Verifying upi success callback via HDFC when autorefund is enabled
    TC naming code description:
    100: Payment method
    108: BQRV4 Static QR
    003: Testcase ID
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Enable auto refund

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund enabled is : {response}")


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

            # Get config_id, mid, tid and merchant_pan from bharatqr_merchant_config table
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)

            db_bqr_config_id = result['id'].values[0]
            logger.info(f"fetched config id is : {db_bqr_config_id}")

            db_bqr_config_mid = result['mid'].values[0]
            logger.info(f"fetched mid is : {db_bqr_config_mid}")

            db_bqr_conig_tid = result['tid'].values[0]
            logger.info(f"fetched tid is : {db_bqr_conig_tid}")

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

            testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_bqr_config_id)


            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username ,
                "qrCodeFormat" : "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_conig_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            res_generateqr_publish_id = response["publishId"]
            res_generateqr_mid = response["mid"]
            res_generateqr_tid = response["tid"]
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            rrn = random.randint(11111110, 99999999)
            logger.debug(f"generated random rrn number is : {rrn}")

            ref_id = 'RID' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")

            amount = random.randint(300, 399)
            logger.debug(f"generated random amount is : {amount}")

            logger.debug(
                f"replacing the publish_id with {res_generateqr_publish_id}, amount with {amount}.00, ref_id with {ref_id} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('staticqr_upi_callback_curl', curl_data={'ref_id': ref_id,
                                                                                     'amount': str(amount) + ".00",
                                                                                     'publish_id': res_generateqr_publish_id,
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

            db_txn_id = result["id"].iloc[0]
            db_txn_amount = result["amount"].iloc[0]
            db_txn_bank_code = result["bank_code"].iloc[0]
            db_txn_username = result["username"].iloc[0]
            db_txn_tid = result["tid"].iloc[0]
            db_txn_mid = result["mid"].iloc[0]
            db_txn_payment_mode = result["payment_mode"].iloc[0]
            db_txn_external_ref = result["external_ref"].iloc[0]
            db_txn_created_time = result['created_time'].values[0]

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
                # --------------------------------------------------------------------------------------------
                date = date_time_converter.db_datetime(db_txn_created_time)
                expected_api_values = {"pmt_status": "AUTHORIZED",
                                       "txn_amt": float(amount),
                                       "pmt_mode": "BHARATQR",
                                       "pmt_state": "SETTLED",
                                       "rrn": str(rrn),
                                       "settle_status": "SETTLED",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "CHARGE",
                                       "mid": db_bqr_config_mid,
                                       "tid": db_bqr_conig_tid,
                                       "org_code": org_code,
                                       "date": date}
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == db_txn_id][0]
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

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api, "pmt_state": state_api,
                                     "rrn": str(rrn_api), "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api, "issuer_code": issuer_code_api,
                                     "mid": mid_api, "tid": tid_api,
                                     "txn_type": txn_type_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api)}
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
                    "amount" : amount,
                    "bank_code" : "HDFC",
                    "org_code" : org_code,
                    "status" : "AUTHORIZED",
                    "username" : app_username,
                    "tid" : res_generateqr_tid,
                    "mid" : res_generateqr_mid,
                    "txn_ref" : ref_id,
                    "additional_field1" : res_generateqr_publish_id,
                    "additional_field2" : res_generateqr_publish_id,
                    "additional_field3" : ref_id,
                    "payment_mode":"UPI",
                    "resp_code" : "SUCCESS",
                    "txn_type" : "STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id = '" + str(db_txn_id) + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")

                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_upi_txn_txn_ref = result["txn_ref"].iloc[0]
                db_upi_txn_additional_field1 = result["additional_field1"].iloc[0]
                db_upi_txn_additional_field2 = result["additional_field2"].iloc[0]
                db_upi_txn_additional_field3 = result["additional_field3"].iloc[0]
                db_upi_txn_resp_code = result["resp_code"].iloc[0]
                db_upi_txn_org_code = result["org_code"].iloc[0]
                db_upi_txn_status = result["status"].iloc[0]
                db_upi_txn_txn_type = result["txn_type"].iloc[0]

                actual_db_values = {
                    "amount": db_txn_amount,
                    "bank_code": db_txn_bank_code,
                    "org_code": db_upi_txn_org_code,
                    "status": db_upi_txn_status,
                    "username": db_txn_username,
                    "tid": db_txn_tid,
                    "mid": db_txn_mid,
                    "txn_ref": db_upi_txn_txn_ref,
                    "additional_field1": db_upi_txn_additional_field1,
                    "additional_field2": db_upi_txn_additional_field2,
                    "additional_field3": db_upi_txn_additional_field3,
                    "payment_mode":db_txn_payment_mode,
                    "resp_code": db_upi_txn_resp_code,
                    "txn_type": db_upi_txn_txn_type
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(db_txn_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": db_txn_id,
                    "rrn": str(rrn),
                    "customer_name": "Test Payer",
                    "payer_name": "Test Payer",
                    "order_id": db_txn_external_ref,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(db_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {db_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {db_txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {db_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {db_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {db_txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {db_txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {db_txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {db_txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {db_txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {db_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {db_txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(db_txn_created_time)
                expected_values = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date, 'time': txn_time,
                }
                receipt_validator.perform_charge_slip_validations(db_txn_id,
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
def test_common_100_108_004():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_StaticQR_Callback_Success_AutoRefund_Disabled_Via_HDFC
    Sub Feature Description: Verifying upi success callback via HDFC when autorefund is disabled
    TC naming code description:
    100: Payment method
    108: BQRV4 Static QR
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
        # Enable auto refund

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund disabled is : {response}")


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

            # Get config_id, mid, tid and merchant_pan from bharatqr_merchant_config table
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC';"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)

            db_bqr_config_id = result['id'].values[0]
            logger.info(f"fetched config id is : {db_bqr_config_id}")

            db_bqr_config_mid = result['mid'].values[0]
            logger.info(f"fetched mid is : {db_bqr_config_mid}")

            db_bqr_conig_tid = result['tid'].values[0]
            logger.info(f"fetched tid is : {db_bqr_conig_tid}")

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

            testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_bqr_config_id)

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username ,
                "qrCodeFormat" : "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_conig_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            res_generateqr_success = response["success"]
            res_generateqr_username = response["username"]
            res_generateqr_publish_id = response["publishId"]
            res_generateqr_org_code = response["merchantCode"]
            res_generateqr_mid = response["mid"]
            res_generateqr_tid = response["tid"]
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            rrn = random.randint(11111110, 99999999)
            logger.debug(f"generated random rrn number is : {rrn}")

            ref_id = 'RID' + str(rrn)
            logger.debug(f"generated random ref_id is : {ref_id}")

            amount = random.randint(300, 399)
            logger.debug(f"generated random amount is : {amount}")

            logger.debug(
                f"replacing the publish_id with {res_generateqr_publish_id}, amount with {amount}.00, ref_id with {ref_id} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('staticqr_upi_callback_curl', curl_data={'ref_id': ref_id,
                                                                                     'amount': str(amount) + ".00",
                                                                                     'publish_id': res_generateqr_publish_id,
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

            db_txn_id = result["id"].iloc[0]
            db_txn_amount = result["amount"].iloc[0]
            db_txn_bank_code = result["bank_code"].iloc[0]
            db_txn_username = result["username"].iloc[0]
            db_txn_tid = result["tid"].iloc[0]
            db_txn_mid = result["mid"].iloc[0]
            db_txn_payment_mode = result["payment_mode"].iloc[0]
            db_txn_external_ref = result["external_ref"].iloc[0]
            db_txn_created_time = result['created_time'].values[0]

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
                # --------------------------------------------------------------------------------------------
                date = date_time_converter.db_datetime(db_txn_created_time)
                expected_api_values = {"pmt_status": "AUTHORIZED",
                                       "txn_amt": float(amount),
                                       "pmt_mode": "BHARATQR",
                                       "pmt_state": "SETTLED",
                                       "rrn": str(rrn),
                                       "settle_status": "SETTLED",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "CHARGE",
                                       "mid": db_bqr_config_mid,
                                       "tid": db_bqr_conig_tid,
                                       "org_code": org_code,
                                       "date": date}
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == db_txn_id][0]
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

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api, "pmt_state": state_api,
                                     "rrn": str(rrn_api), "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api, "issuer_code": issuer_code_api,
                                     "mid": mid_api, "tid": tid_api,
                                     "txn_type": txn_type_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api)}
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
                    "amount" : amount,
                    "bank_code" : "HDFC",
                    "org_code" : org_code,
                    "status" : "AUTHORIZED",
                    "username" : app_username,
                    "tid" : res_generateqr_tid,
                    "mid" : res_generateqr_mid,
                    "txn_ref" : ref_id,
                    "additional_field1" : res_generateqr_publish_id,
                    "additional_field2" : res_generateqr_publish_id,
                    "additional_field3" : ref_id,
                    "payment_mode":"UPI",
                    "resp_code" : "SUCCESS",
                    "txn_type" : "STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id = '" + str(db_txn_id) + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")

                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_upi_txn_txn_ref = result["txn_ref"].iloc[0]
                db_upi_txn_additional_field1 = result["additional_field1"].iloc[0]
                db_upi_txn_additional_field2 = result["additional_field2"].iloc[0]
                db_upi_txn_additional_field3 = result["additional_field3"].iloc[0]
                db_upi_txn_resp_code = result["resp_code"].iloc[0]
                db_upi_txn_org_code = result["org_code"].iloc[0]
                db_upi_txn_status = result["status"].iloc[0]
                db_upi_txn_txn_type = result["txn_type"].iloc[0]

                actual_db_values = {
                    "amount": db_txn_amount,
                    "bank_code": db_txn_bank_code,
                    "org_code": db_upi_txn_org_code,
                    "status": db_upi_txn_status,
                    "username": db_txn_username,
                    "tid": db_txn_tid,
                    "mid": db_txn_mid,
                    "txn_ref": db_upi_txn_txn_ref,
                    "additional_field1": db_upi_txn_additional_field1,
                    "additional_field2": db_upi_txn_additional_field2,
                    "additional_field3": db_upi_txn_additional_field3,
                    "payment_mode":db_txn_payment_mode,
                    "resp_code": db_upi_txn_resp_code,
                    "txn_type": db_upi_txn_txn_type
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(db_txn_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": db_txn_id,
                    "rrn": str(rrn),
                    "customer_name": "Test Payer",
                    "payer_name": "Test Payer",
                    "order_id": db_txn_external_ref,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(db_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {db_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {db_txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {db_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {db_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {db_txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {db_txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {db_txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {db_txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {db_txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {db_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {db_txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(db_txn_created_time)
                expected_values = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date, 'time': txn_time,
                }
                receipt_validator.perform_charge_slip_validations(db_txn_id,
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