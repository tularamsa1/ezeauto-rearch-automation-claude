import random
import sys
from datetime import datetime

import pytest

from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.portal_remotePayPage import RemotePayTxnPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d103_103_012():
    """
    Sub Feature Code: UI_RP_UPI_Success_Via_Pure_UPI_Collect_Callback_KOTAK_OLIVE
    Sub Feature Description: Verification of a Remote Pay successful upi txn using UPI Collect Callback via KOTAK OLIVE
    TC naming code description: d103: Dev Project[KOTAK_OLIVE_UPI], 103-> RemotePay, 012->TC012
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
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, cnpwareLog=True)

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

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "amount": amount, "externalRefNumber": order_id, "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for Remotepay_Initiate : {response}")

            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_browser.goto(payment_link_url)
                remotePayUpiCollectTxn = RemotePayTxnPage(ui_browser)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")

            query = f"select * from payment_intent where org_code = '{org_code}' AND external_ref = '{order_id}' and " \
                    f"id LIKE '{datetime.utcnow().strftime('%y%m%d')}%' order by created_time desc limit 1; "
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"fetched payment_intent_id is : {payment_intent_id}")

            rrn = datetime.now().strftime('%m%d%H%M%S%f')[:-4]
            dt, micro = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
            transaction_timestamp = "%s.%03d" % (dt, int(micro) / 1000)
            logger.debug(f"generated rrn and transaction_timestamp is : {rrn} and {transaction_timestamp}")
            api_details = DBProcessor.get_api_details('upi_confirm_kotakolive', request_body={
                "transactionid": f"KMBM{prop_value}00{payment_intent_id}",
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

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            created_time = result['created_time'].values[0]
            auth_code = result['auth_code'].values[0]
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
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            external_ref = result['external_ref'].values[0]

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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": 'REMOTE_PAY', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time,
                    "order_id": external_ref
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
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
                order_id_api = response["orderNumber"]

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
                    "order_id": order_id_api
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
                    "txn_type": "REMOTE_PAY",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "OLIVE",
                    "error_msg": None,
                    "mid": mid,
                    "tid": tid,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "KOTAK_OLIVE",
                    "upi_mc_id": upi_mc_id,
                    "upi_customer_ref": rrn,
                    "upi_resp_code": "SUCCESS",
                    "pmt_intent_status": "COMPLETED",
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
                upi_customer_ref_db = result["customer_ref"].iloc[0]
                upi_resp_code_db = result["resp_code"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

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
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_customer_ref": upi_customer_ref_db,
                    "upi_resp_code": upi_resp_code_db,
                    "pmt_intent_status": payment_intent_status,
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
def test_d103_103_013():
    """
    Sub Feature Code: UI_RP_UPI_Failed_Via_Pure_UPI_Collect_Callback_KOTAK_OLIVE
    Sub Feature Description: Verification of a Remote Pay failed upi txn using UPI Collect Callback via KOTAK OLIVE
    TC naming code description: d103: Dev Project[KOTAK_OLIVE_UPI], 103-> RemotePay, 013->TC013
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
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, cnpwareLog=True)

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

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "amount": amount, "externalRefNumber": order_id, "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for Remotepay_Initiate : {response}")

            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_browser.goto(payment_link_url)
                remotePayUpiCollectTxn = RemotePayTxnPage(ui_browser)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")

            query = f"select * from payment_intent where org_code = '{org_code}' AND external_ref = '{order_id}' and " \
                    f"id LIKE '{datetime.utcnow().strftime('%y%m%d')}%' order by created_time desc limit 1; "
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"fetched payment_intent_id is : {payment_intent_id}")

            rrn = datetime.now().strftime('%m%d%H%M%S%f')[:-4]
            dt, micro = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
            transaction_timestamp = "%s.%03d" % (dt, int(micro) / 1000)
            logger.debug(f"generated rrn and transaction_timestamp is : {rrn} and {transaction_timestamp}")
            api_details = DBProcessor.get_api_details('upi_confirm_kotakolive', request_body={
                "transactionid": f"KMBM{prop_value}00{payment_intent_id}",
                "aggregatorcode": "",
                "merchantcode": mid,
                "status": "FAILED",
                "statusCode": "03",
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

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            created_time = result['created_time'].values[0]
            auth_code = result['auth_code'].values[0]
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
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            external_ref = result['external_ref'].values[0]

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
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "FAILED", "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": 'REMOTE_PAY', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time,
                    "order_id": external_ref
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
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
                order_id_api = response["orderNumber"]

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
                    "order_id": order_id_api
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
                    "txn_type": "REMOTE_PAY",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "OLIVE",
                    "error_msg": "UPI Transaction Failed",
                    "mid": mid,
                    "tid": tid,
                    "upi_txn_status": "FAILED",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "KOTAK_OLIVE",
                    "upi_mc_id": upi_mc_id,
                    "upi_customer_ref": rrn,
                    "upi_resp_code": "FAILED",
                    "pmt_intent_status": "COMPLETED",
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
                upi_customer_ref_db = result["customer_ref"].iloc[0]
                upi_resp_code_db = result["resp_code"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

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
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_customer_ref": upi_customer_ref_db,
                    "upi_resp_code": upi_resp_code_db,
                    "pmt_intent_status": payment_intent_status,
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
def test_d103_103_014():
    """
    Sub Feature Code: UI_RP_UPI_Expired_Via_Pure_UPI_Collect_Callback_KOTAK_OLIVE
    Sub Feature Description: Verification of a Remote Pay expired upi txn using UPI Collect Callback via KOTAK OLIVE
    TC naming code description: d103: Dev Project[KOTAK_OLIVE_UPI], 103-> RemotePay, 014->TC014
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
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, cnpwareLog=True)

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

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "amount": amount, "externalRefNumber": order_id, "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for Remotepay_Initiate : {response}")

            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
                # payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_browser.goto(payment_link_url)
                remotePayUpiCollectTxn = RemotePayTxnPage(ui_browser)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")

            query = f"select * from payment_intent where org_code = '{org_code}' AND external_ref = '{order_id}' and " \
                    f"id LIKE '{datetime.utcnow().strftime('%y%m%d')}%' order by created_time desc limit 1; "
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"fetched payment_intent_id is : {payment_intent_id}")

            rrn = datetime.now().strftime('%m%d%H%M%S%f')[:-4]
            dt, micro = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
            transaction_timestamp = "%s.%03d" % (dt, int(micro) / 1000)
            logger.debug(f"generated rrn and transaction_timestamp is : {rrn} and {transaction_timestamp}")
            api_details = DBProcessor.get_api_details('upi_confirm_kotakolive', request_body={
                "transactionid": f"KMBM{prop_value}00{payment_intent_id}",
                "aggregatorcode": "",
                "merchantcode": mid,
                "status": "EXPIRED",
                "statusCode": "02",
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

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            created_time = result['created_time'].values[0]
            auth_code = result['auth_code'].values[0]
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
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            external_ref = result['external_ref'].values[0]

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
                expected_api_values = {
                    "pmt_status": "PENDING",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "PENDING", "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": 'REMOTE_PAY', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time,
                    "order_id": external_ref
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
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
                order_id_api = response["orderNumber"]

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
                    "order_id": order_id_api
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
                    "pmt_status": "PENDING",
                    "pmt_state": "PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "settle_status": "PENDING",
                    "txn_type": "REMOTE_PAY",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "OLIVE",
                    "error_msg": None,
                    "mid": mid,
                    "tid": tid,
                    "upi_txn_status": "PENDING",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "KOTAK_OLIVE",
                    "upi_mc_id": upi_mc_id,
                    "upi_customer_ref": rrn,
                    "upi_resp_code": "EXPIRED",
                    "pmt_intent_status": "ACTIVE",
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
                upi_customer_ref_db = result["customer_ref"].iloc[0]
                upi_resp_code_db = result["resp_code"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

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
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_customer_ref": upi_customer_ref_db,
                    "upi_resp_code": upi_resp_code_db,
                    "pmt_intent_status": payment_intent_status,
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
def test_d103_103_015():
    """
    Sub Feature Code: UI_RP_UPI_Rejected_Via_Pure_UPI_Collect_Callback_KOTAK_OLIVE
    Sub Feature Description: Verification of a Remote Pay rejected upi txn using UPI Collect Callback via KOTAK OLIVE
    TC naming code description: d103: Dev Project[KOTAK_OLIVE_UPI], 103-> RemotePay, 015->TC015
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
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, cnpwareLog=True)

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

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "amount": amount, "externalRefNumber": order_id, "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for Remotepay_Initiate : {response}")

            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
                # payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_browser.goto(payment_link_url)
                remotePayUpiCollectTxn = RemotePayTxnPage(ui_browser)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch txn data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")

            query = f"select * from payment_intent where org_code = '{org_code}' AND external_ref = '{order_id}' and " \
                    f"id LIKE '{datetime.utcnow().strftime('%y%m%d')}%' order by created_time desc limit 1; "
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"fetched payment_intent_id is : {payment_intent_id}")

            rrn = datetime.now().strftime('%m%d%H%M%S%f')[:-4]
            dt, micro = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
            transaction_timestamp = "%s.%03d" % (dt, int(micro) / 1000)
            logger.debug(f"generated rrn and transaction_timestamp is : {rrn} and {transaction_timestamp}")
            api_details = DBProcessor.get_api_details('upi_confirm_kotakolive', request_body={
                "transactionid": f"KMBM{prop_value}00{payment_intent_id}",
                "aggregatorcode": "",
                "merchantcode": mid,
                "status": "REJECTED",
                "statusCode": "01",
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

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            created_time = result['created_time'].values[0]
            auth_code = result['auth_code'].values[0]
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
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            external_ref = result['external_ref'].values[0]

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
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount), "pmt_mode": "UPI",
                    "pmt_state": "FAILED", "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": 'REMOTE_PAY', "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time,
                    "order_id": external_ref
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
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
                order_id_api = response["orderNumber"]

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
                    "order_id": order_id_api
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
                    "txn_type": "REMOTE_PAY",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "OLIVE",
                    "error_msg": "UPI Transaction Rejected",
                    "mid": mid,
                    "tid": tid,
                    "upi_txn_status": "FAILED",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "KOTAK_OLIVE",
                    "upi_mc_id": upi_mc_id,
                    "upi_customer_ref": rrn,
                    "upi_resp_code": "REJECTED",
                    "pmt_intent_status": "COMPLETED",
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
                upi_customer_ref_db = result["customer_ref"].iloc[0]
                upi_resp_code_db = result["resp_code"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

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
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_customer_ref": upi_customer_ref_db,
                    "upi_resp_code": upi_resp_code_db,
                    "pmt_intent_status": payment_intent_status,
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
