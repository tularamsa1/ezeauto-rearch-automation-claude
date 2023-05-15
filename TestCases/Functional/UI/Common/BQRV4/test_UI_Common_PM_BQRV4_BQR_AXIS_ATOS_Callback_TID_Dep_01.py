import sys
from time import sleep
import pytest
import random
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import Validator,ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner,  date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_290():
    """
    Sub Feature code: TID_Dep_UI_Common_BQRV4_BQR_Callback_Success_AXIS_ATOS
    Sub Feature Description: TID Dep - Verification of a BQR Success with one Callback via AXIS_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 290: TC290
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='BHARATQR' and payment_gateway='ATOS';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='AXIS'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        logger.info(f"mid from bharatqr_merchant_config:  {mid}")
        tid = result["tid"].iloc[0]
        logger.info(f"tid from bharatqr_merchant_config:  {tid}")
        terminal_info_id = result["terminal_info_id"].iloc[0]
        logger.info(f"terminal_info_id from bharatqr_merchant_config: {terminal_info_id}")
        bqr_mc_id = result["id"].iloc[0]
        logger.info(f"bqr_mc_id from bharatqr_merchant_config: {bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].iloc[0]
        logger.info(f"bqr_m_pan from bharatqr_merchant_config: {bqr_m_pan}")
        vtid = result["virtual_tid"].iloc[0]
        logger.info(f"vtid from bharatqr_merchant_config: {vtid}")
        vmid = result["virtual_mid"].iloc[0]
        logger.info(f"vmid from bharatqr_merchant_config: {vmid}")

        query = "select device_serial from terminal_info where tid = '" + str(vtid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetching device_serial : {device_serial}")

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
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(401, 999)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)

            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching txn_id, posting date from the txn table :{txn_id}, {created_time}")

            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id ='"+txn_id+"';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            provide_ref_id = result["provider_ref_id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id},"
                f" Auth code : {auth_code}, RRN : {rrn}, Primary id : {provide_ref_id}")

            api_details = DBProcessor.get_api_details('callback_Bqr_AXIS',
                                                      request_body={"primary_id": provide_ref_id,
                                                                    "secondary_id":provide_ref_id,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no":rrn,
                                                                    "mid":mid, "mpan": bqr_m_pan,
                                                                    "settlement_amount": str(amount)
                                                                    }
                                                      )
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for BQR call back : {response}")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            logger.info(f"auth_code from txn table: {auth_code}")
            rrn = result['rr_number'].iloc[0]
            logger.info(f"rrn from txn table: {rrn}")
            created_time = result['created_time'].values[0]
            logger.info(f"created_time from txn table: {created_time}")
            customer_name = result['customer_name'].values[0]
            logger.info(f"customer_name from txn table: {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.info(f"payer_name from txn table: {payer_name}")

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
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")

                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")

                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")

                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")

                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")

                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")

                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")

                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")

                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "auth_code": app_auth_code,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time
                 }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date,
                    "nonce_status": "OPEN",
                    "device_serial": device_serial
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
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
                auth_code_api = response["authCode"]
                date_api = response["createdTime"]
                device_serial_api = response['deviceSerial']
                nonce_status_api = response['nonceStatus']

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,"mid": mid_api,
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "nonce_status":nonce_status_api,
                    "device_serial": device_serial_api
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "acquirer_code" : "AXIS",
                    "bank_name" : "Axis Bank",
                    "payer_name": payer_name,
                    "mid" :mid,
                    "tid" : tid,
                    "pmt_gateway": "ATOS",
                    "rrn" : str(rrn),
                    "settle_status": "SETTLED",
                    "device_serial":device_serial,
                    "txn_type": "CHARGE",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "AXIS",
                    "bqr_merchant_config_id": bqr_mc_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "bqr_auth_code":auth_code,
                    "bqr_rrn":rrn,
                    "bqr_merchant_pan":"ME" + txn_id.split('E')[1],
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                payer_name_db = result["payer_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                device_serial_db = result["device_serial"].iloc[0]
                txn_type_db = result["txn_type"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]
                bqr_auth_code_db = result['txn_auth_code'].values[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_m_pan_db = result['merchant_pan'].values[0]

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code" : acquirer_code_db,
                    "bank_name" : bank_name_db,
                    "payer_name": payer_name_db,
                    "mid" :mid_db,
                    "tid" : tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn" : rr_number_db,
                    "settle_status": settlement_status_db,
                    "device_serial":device_serial_db,
                    "txn_type": txn_type_db,

                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_auth_code":bqr_auth_code_db,
                    "bqr_rrn":bqr_rrn_db,
                    "bqr_merchant_pan":bqr_m_pan_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {
                    'PAID BY:': 'BHARATQR',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': auth_code
                }
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
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
def test_common_100_102_292():
    """
    Sub Feature code: TID_Dep_UI_Common_BQRV4_BQR_Callback_After_expired_Success_AXIS_ATOS
    Sub Feature Description: TID Dep - Verification of a BQR Callback After Expiry via AXIS_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 292: TC292
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='BHARATQR' and payment_gateway='ATOS';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='AXIS'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        vtid = result["virtual_tid"].iloc[0]
        vmid = result["virtual_mid"].iloc[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan, virtual_mid, virtual_tid  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}, {vmid}, {vtid}")

        query = "select device_serial from terminal_info where tid = '" + str(vtid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetching device_serial : {device_serial}")

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
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(401, 999)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)

            orig_txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {orig_txn_id}")

            query = "select * from txn where id = '" + str(orig_txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching txn_id, posting date from the txn table :{orig_txn_id}, {created_time}")

            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id ='"+orig_txn_id+"';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            provide_ref_id = result["provider_ref_id"].iloc[0]
            auth_code = "AE" + orig_txn_id.split('E')[1]
            rrn = "RE" + orig_txn_id.split('E')[1]
            logger.debug(f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {orig_txn_id},"
                f" Auth code : {auth_code}, RRN : {rrn}, Primary id : {provide_ref_id}")
            logger.info(f"Waiting for 60 seconds till expiry time ...")
            sleep(60)
            api_details = DBProcessor.get_api_details('callback_Bqr_AXIS',
                                                      request_body={"primary_id": provide_ref_id,
                                                                    "secondary_id":provide_ref_id,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no":rrn,
                                                                    "mid":mid, "mpan": bqr_m_pan,
                                                                    "settlement_amount": str(amount)
                                                                    }
                                                      )
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for BQR call back : {response}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch authorized txn_id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            auth_code_1 = result['auth_code'].values[0]
            rrn_1 = result['rr_number'].iloc[0]
            created_time_1 = result['created_time'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]

            logger.debug(f"Fetching auth_code, rrn, created_time, customer name and payer name from database for "
                         f"current merchant:{auth_code_1}, {rrn_1}, {created_time_1}, {customer_name}, {payer_name}")

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
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_1 = date_time_converter.to_app_format(created_time_1)
                expected_app_values = {
                    "pmt_mode_1": "BHARAT QR",
                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": "{:.2f}".format(amount),
                    "settle_status_1": "SETTLED",
                    "txn_id_1": txn_id,
                    "rrn_1": str(rrn),
                    "customer_name_1": customer_name,
                    "order_id_1": order_id,
                    "pmt_msg_1": "PAYMENT SUCCESSFUL",
                    "auth_code_1": auth_code_1,
                    "date_1": date_and_time_1,

                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": orig_txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status_1}")
                app_auth_code_1 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code_1}")
                payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode_1}")
                app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id_1}")
                app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount_1}")
                app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_1}")
                app_customer_name_1 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name_1}")
                app_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status_1}")
                app_payment_msg_1 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg_1}")
                app_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id_1}")
                app_rrn_1 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_1}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(orig_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {orig_txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {orig_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {orig_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {orig_txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {orig_txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {orig_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {orig_txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {orig_txn_id}, {app_order_id}")

                actual_app_values = {
                    "pmt_mode_1": payment_mode_1,
                    "pmt_status_1": payment_status_1.split(':')[1],
                    "txn_amt_1": app_amount_1.split(' ')[1],
                    "txn_id_1": app_txn_id_1,
                    "rrn_1": str(app_rrn_1),
                    "customer_name_1": app_customer_name_1,
                    "settle_status_1": app_settlement_status_1,
                    "order_id_1": app_order_id_1,
                    "auth_code_1": app_auth_code_1,
                    "pmt_msg_1": app_payment_msg_1,
                    "date_1": app_date_and_time_1,

                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                date_1 = date_time_converter.db_datetime(created_time_1)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "device_serial": device_serial,
                    "nonce_status": "CLOSED",

                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": float(amount),
                    "pmt_mode_1": "BHARATQR",
                    "pmt_state_1": "SETTLED",
                    "rrn_1": str(rrn),
                    "settle_status_1": "SETTLED",
                    "acquirer_code_1": "AXIS",
                    "issuer_code_1": "AXIS",
                    "txn_type_1": "CHARGE",
                    "mid_1": mid,
                    "tid_1": tid,
                    "org_code_1": org_code,
                    "auth_code_1": auth_code,
                    "date_1": date_1,
                    "device_serial_1": device_serial,
                    "nonce_status_1": "OPEN",
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_authorized = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of authorized txn is : {response_authorized}")

                status_api_1 = response_authorized["status"]
                amount_api_1 = float(response_authorized["amount"])
                payment_mode_api_1 = response_authorized["paymentMode"]
                state_api_1 = response_authorized["states"][0]
                rrn_api_1 = response_authorized["rrNumber"]
                settlement_status_api_1 = response_authorized["settlementStatus"]
                issuer_code_api_1 = response_authorized["issuerCode"]
                acquirer_code_api_1 = response_authorized["acquirerCode"]
                orgCode_api_1 = response_authorized["orgCode"]
                mid_api_1 = response_authorized["mid"]
                tid_api_1 = response_authorized["tid"]
                txn_type_api_1 = response_authorized["txnType"]
                auth_code_api_1 = response_authorized["authCode"]
                date_api_1 = response_authorized["createdTime"]
                device_serial_api_1 = response_authorized['deviceSerial']
                nonce_status_api_1 = response_authorized['nonceStatus']

                response_expired = [x for x in response["txns"] if x["txnId"] == orig_txn_id][0]
                logger.debug(f"Response after filtering data of expired txn is : {response_expired}")

                status_api = response_expired["status"]
                amount_api = float(response_expired["amount"])
                payment_mode_api = response_expired["paymentMode"]
                state_api = response_expired["states"][0]
                settlement_status_api = response_expired["settlementStatus"]
                issuer_code_api = response_expired["issuerCode"]
                acquirer_code_api = response_expired["acquirerCode"]
                orgCode_api = response_expired["orgCode"]
                mid_api = response_expired["mid"]
                tid_api = response_expired["tid"]
                txn_type_api = response_expired["txnType"]
                date_api = response_expired["createdTime"]
                device_serial_api = response_expired['deviceSerial']
                nonce_status_api = response_expired['nonceStatus']

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
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "device_serial": device_serial_api,
                    "nonce_status": nonce_status_api,

                    "pmt_status_1": status_api_1,
                    "txn_amt_1": amount_api_1,
                    "pmt_mode_1": payment_mode_api_1,
                    "pmt_state_1": state_api_1,
                    "rrn_1": str(rrn_api_1),
                    "settle_status_1": settlement_status_api_1,
                    "acquirer_code_1": acquirer_code_api_1,
                    "issuer_code_1": issuer_code_api_1,
                    "txn_type_1": txn_type_api_1,
                    "mid_1": mid_api_1,
                    "tid_1": tid_api_1,
                    "org_code_1": orgCode_api_1,
                    "auth_code_1": auth_code_api_1,
                    "date_1": date_time_converter.from_api_to_datetime_format(date_api_1),
                    "device_serial_1": device_serial_api_1,
                    "nonce_status_1": nonce_status_api_1,
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
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "acquirer_code" : "AXIS",
                    "mid" :mid,
                    "tid" : tid,
                    "pmt_gateway": "ATOS",
                    "settle_status": "FAILED",
                    "device_serial":device_serial,
                    "txn_type": "CHARGE",
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "AXIS",
                    "bqr_merchant_config_id": bqr_mc_id,
                    "bqr_txn_primary_id": orig_txn_id,
                    "bqr_org_code": org_code,

                    "txn_amt_1": float(amount),
                    "pmt_mode_1": "BHARATQR",
                    "pmt_status_1": "AUTHORIZED",
                    "pmt_state_1": "SETTLED",
                    "acquirer_code_1": "AXIS",
                    "bank_name_1": "Axis Bank",
                    "payer_name_1": payer_name,
                    "mid_1": mid,
                    "tid_1": tid,
                    "pmt_gateway_1": "ATOS",
                    "rrn_1": str(rrn),
                    "settle_status_1": "SETTLED",
                    "device_serial_1": device_serial,
                    "txn_type_1": "CHARGE",
                    "bqr_pmt_state_1": "SETTLED",
                    "bqr_txn_amt_1": float(amount),
                    "bqr_txn_type_1": "DYNAMIC_QR",
                    "brq_terminal_info_id_1": terminal_info_id,
                    "bqr_bank_code_1": "AXIS",
                    "bqr_merchant_config_id_1": bqr_mc_id,
                    "bqr_txn_primary_id_1": txn_id,
                    "bqr_org_code_1": org_code,
                    "bqr_auth_code_1": auth_code,
                    "bqr_rrn_1": rrn,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data of authorized txn from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_1 = float(result["amount"].iloc[0])
                payment_mode_db_1 = result["payment_mode"].iloc[0]
                payment_status_db_1 = result["status"].iloc[0]
                payment_state_db_1 = result["state"].iloc[0]
                acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                bank_name_db_1 = result["bank_name"].iloc[0]
                payer_name_db_1 = result["payer_name"].iloc[0]
                mid_db_1 = result["mid"].iloc[0]
                tid_db_1 = result["tid"].iloc[0]
                payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                rr_number_db_1 = result["rr_number"].iloc[0]
                settlement_status_db_1 = result["settlement_status"].iloc[0]
                device_serial_db_1 = result["device_serial"].iloc[0]
                txn_type_db_1 = result["txn_type"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data of authorized txn from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db_1 = result["state"].iloc[0]
                bqr_amount_db_1 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_1 = result["txn_type"].iloc[0]
                brq_terminal_info_id_db_1 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_1 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_1 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_1 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_1 = result['org_code'].values[0]
                bqr_auth_code_db_1 = result['txn_auth_code'].values[0]
                bqr_rrn_db_1 = result['rrn'].values[0]

                query = "select * from txn where id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data of expired txn from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                device_serial_db = result["device_serial"].iloc[0]
                txn_type_db = result["txn_type"].iloc[0]

                query = "select * from bharatqr_txn where id='" + orig_txn_id + "'"
                logger.debug(f"Query to fetch data of expired txn from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code" : acquirer_code_db,
                    "mid" :mid_db,
                    "tid" : tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "device_serial":device_serial_db,
                    "txn_type": txn_type_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,

                    "txn_amt_1": amount_db_1,
                    "pmt_mode_1": payment_mode_db_1,
                    "pmt_status_1": payment_status_db_1,
                    "pmt_state_1": payment_state_db_1,
                    "acquirer_code_1": acquirer_code_db_1,
                    "bank_name_1": bank_name_db_1,
                    "payer_name_1": payer_name_db_1,
                    "mid_1": mid_db_1,
                    "tid_1": tid_db_1,
                    "pmt_gateway_1": payment_gateway_db_1,
                    "rrn_1": rr_number_db_1,
                    "settle_status_1": settlement_status_db_1,
                    "device_serial_1": device_serial_db_1,
                    "txn_type_1": txn_type_db_1,
                    "bqr_pmt_state_1": bqr_state_db_1,
                    "bqr_txn_amt_1": bqr_amount_db_1,
                    "bqr_txn_type_1": bqr_txn_type_db_1,
                    "brq_terminal_info_id_1": brq_terminal_info_id_db_1,
                    "bqr_bank_code_1": bqr_bank_code_db_1,
                    "bqr_merchant_config_id_1": bqr_merchant_config_id_db_1,
                    "bqr_txn_primary_id_1": bqr_txn_primary_id_db_1,
                    "bqr_org_code_1": bqr_org_code_db_1,
                    "bqr_auth_code_1": bqr_auth_code_db_1,
                    "bqr_rrn_1": bqr_rrn_db_1,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_1)
                expected_values = {'PAID BY:': 'BHARATQR',
                                   'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date,
                                   'time': txn_time,
                                   'AUTH CODE': auth_code}
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
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
def test_common_100_102_291():
    """
    Sub Feature code: TID_Dep_UI_Common_BQRV4_BQR_two_Callback_Success_AXIS_ATOS
    Sub Feature Description: TID Dep-Verification of a BQR Success with two Callback via AXIS_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 291: TC291
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='BHARATQR' and payment_gateway='ATOS';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='AXIS'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        vtid = result["virtual_tid"].iloc[0]
        vmid = result["virtual_mid"].iloc[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan, virtual_mid, virtual_tid  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}, {vmid}, {vtid}")

        query = "select device_serial from terminal_info where tid = '" + str(vtid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetching device_serial : {device_serial}")

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
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(401, 999)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)

            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id ='"+txn_id+"';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            provide_ref_id = result["provider_ref_id"].iloc[0]

            # First callback
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id},"
                f" Auth code : {auth_code}, RRN : {rrn}, Primary id : {provide_ref_id}")

            api_details = DBProcessor.get_api_details('callback_Bqr_AXIS',
                                                      request_body={"primary_id": provide_ref_id,
                                                                    "secondary_id":provide_ref_id,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no":rrn,
                                                                    "mid":mid, "mpan": bqr_m_pan,
                                                                    "settlement_amount": str(amount)
                                                                    }
                                                      )
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for first BQR call back : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            auth_code_db = result['auth_code'].values[0]
            rrn_db = result['rr_number'].iloc[0]
            amount_db = float(result["amount"].iloc[0])
            customer_name = result["customer_name"].iloc[0]
            payment_mode_db = result["payment_mode"].iloc[0]
            payment_status_db = result["status"].iloc[0]
            payment_state_db = result["state"].iloc[0]
            acquirer_code_db = result["acquirer_code"].iloc[0]
            bank_name_db = result["bank_name"].iloc[0]
            mid_db = result["mid"].iloc[0]
            tid_db = result["tid"].iloc[0]
            payment_gateway_db = result["payment_gateway"].iloc[0]
            settlement_status_db = result["settlement_status"].iloc[0]
            device_serial_db = result["device_serial"].iloc[0]
            txn_type_db = result["txn_type"].iloc[0]

            #Second callback
            auth_code_2 = "AE" + str(random.randint(110000000, 110099999))
            rrn_2 = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(f"generated random auth_code_2 to perform the 2nd callback is : {auth_code_2}")
            logger.debug(f"generated random rrn_2 to perform the 2nd callback is : {rrn_2}")

            api_details = DBProcessor.get_api_details('callback_Bqr_AXIS',
                                                      request_body={"primary_id": provide_ref_id,
                                                                    "secondary_id": provide_ref_id,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code_2, "ref_no": rrn_2,
                                                                    "mid": mid, "mpan": bqr_m_pan,
                                                                    "settlement_amount": str(amount)
                                                                    }
                                                      )
            response_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for second BQR call back : {response_2}")
            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            auth_code_db_2 = result['auth_code'].values[0]
            rrn_db_2 = result['rr_number'].iloc[0]
            created_time_2 = result['created_time'].values[0]
            amount_db_2 = float(result["amount"].iloc[0])
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            payment_status_db_2 = result["status"].iloc[0]
            payment_state_db_2 = result["state"].iloc[0]
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            bank_name_db_2 = result["bank_name"].iloc[0]
            mid_db_2 = result["mid"].iloc[0]
            tid_db_2 = result["tid"].iloc[0]
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            device_serial_db_2 = result["device_serial"].iloc[0]
            txn_type_db_2 = result["txn_type"].iloc[0]
            customer_name_2 = result["customer_name"].iloc[0]

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
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                expected_app_values = {"pmt_mode": "BHARAT QR",
                                       "pmt_status": "AUTHORIZED",
                                       "txn_amt": "{:.2f}".format(amount),
                                       "settle_status": "SETTLED",
                                       "txn_id": txn_id,
                                       "rrn": str(rrn),
                                       "order_id": order_id,
                                       "pmt_msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code,
                                       "date": date_and_time,
                                       "customer_name": customer_name,

                                       "pmt_mode_2": "BHARAT QR",
                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": "{:.2f}".format(amount),
                                       "settle_status_2": "SETTLED",
                                       "txn_id_2": txn_id_2,
                                       "rrn_2": str(rrn_2),
                                       "order_id_2": order_id,
                                       "pmt_msg_2": "PAYMENT SUCCESSFUL",
                                       "auth_code_2": auth_code_2,
                                       "date_2": date_and_time_2,
                                       "customer_name_2": customer_name_2,
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_2}")


                actual_app_values = {"pmt_mode": payment_mode,
                                     "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1],
                                     "txn_id": app_txn_id,
                                     "rrn": str(app_rrn),
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "auth_code": app_auth_code,
                                     "pmt_msg": app_payment_msg,
                                     "date": app_date_and_time,
                                     "customer_name": app_customer_name,

                                     "pmt_mode_2": payment_mode_2,
                                     "pmt_status_2": payment_status_2.split(':')[1],
                                     "txn_amt_2": app_amount_2.split(' ')[1],
                                     "txn_id_2": app_txn_id_2,
                                     "rrn_2": str(app_rrn_2),
                                     "settle_status_2": app_settlement_status_2,
                                     "order_id_2": app_order_id_2,
                                     "auth_code_2": app_auth_code_2,
                                     "pmt_msg_2": app_payment_msg_2,
                                     "date_2": app_date_and_time_2,
                                     "customer_name_2": app_customer_name_2
                                     }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {"pmt_status": "AUTHORIZED",
                                       "txn_amt": float(amount),
                                       "pmt_mode": "BHARATQR",
                                       "pmt_state": "SETTLED",
                                       "rrn": str(rrn),
                                       "settle_status": "SETTLED",
                                       "acquirer_code": "AXIS",
                                       "issuer_code": "AXIS",
                                       "txn_type": "CHARGE",
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code,
                                       "auth_code": auth_code,
                                       "date": date,
                                       "device_serial": device_serial,

                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": float(amount),
                                       "pmt_mode_2": "BHARATQR",
                                       "pmt_state_2": "SETTLED",
                                       "rrn_2": str(rrn_2),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "AXIS",
                                       "issuer_code_2": "AXIS",
                                       "txn_type_2": "CHARGE",
                                       "mid_2": mid,
                                       "tid_2": tid,
                                       "org_code_2": org_code,
                                       "auth_code_2": auth_code_2,
                                       "date_2": date_2,
                                       "device_serial_2": device_serial
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response_1}")

                status_api = response_1["status"]
                amount_api = float(response_1["amount"])
                payment_mode_api = response_1["paymentMode"]
                state_api = response_1["states"][0]
                rrn_api = response_1["rrNumber"]
                settlement_status_api = response_1["settlementStatus"]
                issuer_code_api = response_1["issuerCode"]
                acquirer_code_api = response_1["acquirerCode"]
                orgCode_api = response_1["orgCode"]
                mid_api = response_1["mid"]
                tid_api = response_1["tid"]
                txn_type_api = response_1["txnType"]
                auth_code_api = response_1["authCode"]
                date_api = response_1["createdTime"]
                device_serial_api = response_1['deviceSerial']

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of second txn is : {response_2}")

                status_api_2 = response_2["status"]
                amount_api_2 = float(response_2["amount"])
                payment_mode_api_2 = response_2["paymentMode"]
                state_api_2 = response_2["states"][0]
                rrn_api_2 = response_2["rrNumber"]
                settlement_status_api_2 = response_2["settlementStatus"]
                issuer_code_api_2 = response_2["issuerCode"]
                acquirer_code_api_2 = response_2["acquirerCode"]
                orgCode_api_2 = response_2["orgCode"]
                mid_api_2 = response_2["mid"]
                tid_api_2 = response_2["tid"]
                txn_type_api_2 = response_2["txnType"]
                auth_code_api_2 = response_2["authCode"]
                date_api_2 = response_2["createdTime"]
                device_serial_api_2 = response_2['deviceSerial']

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "auth_code": auth_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "device_serial": device_serial_api,

                                     "pmt_status_2": status_api_2,
                                     "txn_amt_2": amount_api_2,
                                     "pmt_mode_2": payment_mode_api_2,
                                     "pmt_state_2": state_api_2,
                                     "rrn_2": str(rrn_api_2),
                                     "settle_status_2": settlement_status_api_2,
                                     "acquirer_code_2": acquirer_code_api_2,
                                     "issuer_code_2": issuer_code_api_2, "mid_2": mid_api_2,
                                     "txn_type_2": txn_type_api_2,
                                     "tid_2": tid_api_2,
                                     "org_code_2": orgCode_api_2,
                                     "auth_code_2": auth_code_api_2,
                                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                                     "device_serial_2": device_serial_api_2
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
                expected_db_values = {"txn_amt": float(amount),
                                      "pmt_mode": "BHARATQR",
                                      "pmt_status": "AUTHORIZED",
                                      "pmt_state": "SETTLED",
                                      "acquirer_code" : "AXIS",
                                      "bank_name" : "Axis Bank",
                                      "mid" :mid,
                                      "tid" : tid,
                                      "pmt_gateway": "ATOS",
                                      "rrn" : str(rrn),
                                      "auth_code":auth_code,
                                      "settle_status": "SETTLED",
                                      "device_serial":device_serial,
                                      "txn_type": "CHARGE",
                                      "bqr_pmt_state": "SETTLED",
                                      "bqr_txn_amt": float(amount),
                                      "bqr_txn_type": "DYNAMIC_QR",
                                      "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "AXIS",
                                      "bqr_merchant_config_id": bqr_mc_id,
                                      "bqr_txn_primary_id": txn_id,
                                      "bqr_org_code": org_code,
                                      "bqr_auth_code":auth_code,
                                      "bqr_rrn":rrn,
                                      "bqr_merchant_pan":"ME" + txn_id.split('E')[1],

                                      "txn_amt_2": float(amount),
                                      "pmt_mode_2": "BHARATQR",
                                      "pmt_status_2": "AUTHORIZED",
                                      "pmt_state_2": "SETTLED",
                                      "acquirer_code_2": "AXIS",
                                      "bank_name_2": "Axis Bank",
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "pmt_gateway_2": "ATOS",
                                      "rrn_2": str(rrn_2),
                                      "auth_code_2":auth_code_2,
                                      "settle_status_2": "SETTLED",
                                      "device_serial_2": device_serial,
                                      "txn_type_2": "CHARGE",
                                      "bqr_pmt_state_2": "SETTLED",
                                      "bqr_txn_amt_2": float(amount),
                                      "bqr_txn_type_2": "DYNAMIC_QR",
                                      "brq_terminal_info_id_2": terminal_info_id,
                                      "bqr_bank_code_2": "AXIS",
                                      "bqr_merchant_config_id_2": bqr_mc_id,
                                      "bqr_txn_primary_id_2": txn_id_2,
                                      "bqr_org_code_2": org_code,
                                      "bqr_auth_code_2": auth_code_2,
                                      "bqr_rrn_2": rrn_2,
                                      "bqr_merchant_pan_2": "ME" + txn_id.split('E')[1],
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]
                bqr_auth_code_db = result['txn_auth_code'].values[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_m_pan_db = result['merchant_pan'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table for second txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db_2 = result["state"].iloc[0]
                bqr_amount_db_2 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_2 = result["txn_type"].iloc[0]
                brq_terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_2 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_2 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_2 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_2 = result['org_code'].values[0]
                bqr_auth_code_db_2 = result['txn_auth_code'].values[0]
                bqr_rrn_db_2 = result['rrn'].values[0]
                bqr_m_pan_db_2 = result['merchant_pan'].values[0]

                actual_db_values = {"txn_amt": amount_db,
                                    "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db,
                                    "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db,
                                    "bank_name" : bank_name_db,
                                    "mid" :mid_db,
                                    "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "rrn" : rrn_db,
                                    "auth_code":auth_code_db,
                                    "settle_status": settlement_status_db,
                                    "device_serial":device_serial_db,
                                    "txn_type": txn_type_db,

                                    "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db,
                                    "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_org_code": bqr_org_code_db,
                                    "bqr_auth_code":bqr_auth_code_db,
                                    "bqr_rrn":bqr_rrn_db,
                                    "bqr_merchant_pan":bqr_m_pan_db,

                                    "txn_amt_2": amount_db_2,
                                    "pmt_mode_2": payment_mode_db_2,
                                    "pmt_status_2": payment_status_db_2,
                                    "pmt_state_2": payment_state_db_2,
                                    "acquirer_code_2" : acquirer_code_db_2,
                                    "bank_name_2" : bank_name_db_2,
                                    "mid_2" :mid_db_2,
                                    "tid_2" : tid_db_2,
                                    "pmt_gateway_2": payment_gateway_db_2,
                                    "rrn_2" : rrn_db_2,
                                    "auth_code_2":auth_code_db_2,
                                    "settle_status_2": settlement_status_db_2,
                                    "device_serial_2":device_serial_db_2,
                                    "txn_type_2": txn_type_db_2,

                                    "bqr_pmt_state_2": bqr_state_db_2,
                                    "bqr_txn_amt_2": bqr_amount_db_2,
                                    "bqr_txn_type_2": bqr_txn_type_db_2,
                                    "brq_terminal_info_id_2": brq_terminal_info_id_db_2,
                                    "bqr_bank_code_2": bqr_bank_code_db_2,
                                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_2,
                                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_2,
                                    "bqr_org_code_2": bqr_org_code_db_2,
                                    "bqr_auth_code_2":bqr_auth_code_db_2,
                                    "bqr_rrn_2":bqr_rrn_db_2,
                                    "bqr_merchant_pan_2":bqr_m_pan_db_2,
                                    }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)

                expected_charge_slip_values_1 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': str(auth_code)
                }

                expected_charge_slip_values_2 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_2)
                }

                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(txn_id,
                                                                                            {"username": app_username,
                                                                                             "password": app_password},
                                                                                            expected_charge_slip_values_1)

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_2,
                                                                                            {"username": app_username,
                                                                                             "password": app_password},
                                                                                            expected_charge_slip_values_2)

                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

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
def test_common_100_102_293():
    """
    Sub Feature code: TID_Dep_UI_Common_BQRV4_BQR_two_Callback_After_expired_Success_AXIS_ATOS
    Sub Feature Description: TID Dep - Verification of  two BQR Callback After Expiry via AXIS_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 293: TC293
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='BHARATQR' and payment_gateway='ATOS';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='AXIS'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        vtid = result["virtual_tid"].iloc[0]
        vmid = result["virtual_mid"].iloc[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan, virtual_mid, virtual_tid  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}, {vmid}, {vtid}")

        query = "select device_serial from terminal_info where tid = '" + str(vtid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetching device_serial : {device_serial}")

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
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(401, 999)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)

            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            query = "select * from txn where org_code='" + org_code + "' and id ='" + txn_id + "';"
            logger.debug(f"Query to fetch transaction details of qr generation from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]

            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id ='"+txn_id+"';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            provide_ref_id = result["provider_ref_id"].iloc[0]

            logger.info(f"Waiting for 60 seconds till expiry...")
            sleep(60)

            # First callback
            auth_code_1 = "AE" + str(random.randint(110000000, 110099999))
            rrn_1 = "RE" + str(random.randint(110000000, 110099999))

            api_details = DBProcessor.get_api_details('callback_Bqr_AXIS',
                                                      request_body={"primary_id": provide_ref_id,
                                                                    "secondary_id":provide_ref_id,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code_1, "ref_no":rrn_1,
                                                                    "mid":mid, "mpan": bqr_m_pan,
                                                                    "settlement_amount": str(amount)
                                                                    }
                                                      )
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for first BQR call back : {response}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_1 = result['id'].values[0]
            created_time_1 = result['created_time'].values[0]
            auth_code_db_1 = result['auth_code'].values[0]
            rrn_db_1 = result['rr_number'].iloc[0]
            amount_db_1 = float(result["amount"].iloc[0])
            payment_mode_db_1 = result["payment_mode"].iloc[0]
            payment_status_db_1 = result["status"].iloc[0]
            payment_state_db_1 = result["state"].iloc[0]
            acquirer_code_db_1 = result["acquirer_code"].iloc[0]
            bank_name_db_1 = result["bank_name"].iloc[0]
            mid_db_1 = result["mid"].iloc[0]
            tid_db_1= result["tid"].iloc[0]
            payment_gateway_db_1 = result["payment_gateway"].iloc[0]
            settlement_status_db_1 = result["settlement_status"].iloc[0]
            device_serial_db_1 = result["device_serial"].iloc[0]
            txn_type_db_1 = result["txn_type"].iloc[0]
            customer_name_1 = result["customer_name"].iloc[0]

            #Second callback
            auth_code_2 = "AE" + str(random.randint(110000000, 110099999))
            rrn_2 = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(f"generated random auth_code_2 to perform the 2nd callback is : {auth_code_2}")
            logger.debug(f"generated random rrn_2 to perform the 2nd callback is : {rrn_2}")

            api_details = DBProcessor.get_api_details('callback_Bqr_AXIS',
                                                      request_body={"primary_id": provide_ref_id,
                                                                    "secondary_id": provide_ref_id,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code_2, "ref_no": rrn_2,
                                                                    "mid": mid, "mpan": bqr_m_pan,
                                                                    "settlement_amount": str(amount)
                                                                    }
                                                      )
            response_2 = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for second BQR call back : {response_2}")
            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            auth_code_db_2 = result['auth_code'].values[0]
            rrn_db_2 = result['rr_number'].iloc[0]
            created_time_2 = result['created_time'].values[0]
            amount_db_2 = float(result["amount"].iloc[0])
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            payment_status_db_2 = result["status"].iloc[0]
            payment_state_db_2 = result["state"].iloc[0]
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            bank_name_db_2 = result["bank_name"].iloc[0]
            mid_db_2 = result["mid"].iloc[0]
            tid_db_2 = result["tid"].iloc[0]
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            device_serial_db_2 = result["device_serial"].iloc[0]
            txn_type_db_2 = result["txn_type"].iloc[0]
            customer_name_2 = result["customer_name"].iloc[0]

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
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_1 = date_time_converter.to_app_format(created_time_1)
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,

                    "pmt_mode_1": "BHARAT QR",
                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": "{:.2f}".format(amount),
                    "settle_status_1": "SETTLED",
                    "txn_id_1": txn_id_1,
                    "rrn_1": str(rrn_1),
                    "order_id_1": order_id,
                    "pmt_msg_1": "PAYMENT SUCCESSFUL",
                    "auth_code_1": auth_code_1,
                    "date_1": date_and_time_1,
                    "customer_name_1": customer_name_1,

                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2,
                    "customer_name_2": customer_name_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_1)
                payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_1}, {payment_status_1}")
                app_auth_code_1 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_1}, {app_auth_code_1}")
                payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_1}, {payment_mode_1}")
                app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_1}, {app_txn_id_1}")
                app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_1}, {app_amount_1}")
                app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_1}, {app_date_and_time_1}")
                app_customer_name_1 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_1}, {app_customer_name_1}")
                app_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_1}, {app_settlement_status_1}")
                app_payment_msg_1 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_1}, {app_payment_msg_1}")
                app_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_1}, {app_order_id_1}")
                app_rrn_1 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_1}, {app_rrn_1}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn_2}")


                actual_app_values = {"pmt_mode": payment_mode,
                                     "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1],
                                     "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "pmt_msg": app_payment_msg,
                                     "date": app_date_and_time,

                                     "pmt_mode_1": payment_mode_1,
                                     "pmt_status_1": payment_status_1.split(':')[1],
                                     "txn_amt_1": app_amount_1.split(' ')[1],
                                     "txn_id_1": app_txn_id_1,
                                     "rrn_1": str(app_rrn_1),
                                     "settle_status_1": app_settlement_status_1,
                                     "order_id_1": app_order_id_1,
                                     "auth_code_1": app_auth_code_1,
                                     "pmt_msg_1": app_payment_msg_1,
                                     "date_1": app_date_and_time_1,
                                     "customer_name_1": app_customer_name_1,

                                     "pmt_mode_2": payment_mode_2,
                                     "pmt_status_2": payment_status_2.split(':')[1],
                                     "txn_amt_2": app_amount_2.split(' ')[1],
                                     "txn_id_2": app_txn_id_2,
                                     "rrn_2": str(app_rrn_2),
                                     "settle_status_2": app_settlement_status_2,
                                     "order_id_2": app_order_id_2,
                                     "auth_code_2": app_auth_code_2,
                                     "pmt_msg_2": app_payment_msg_2,
                                     "date_2": app_date_and_time_2,
                                     "customer_name_2": app_customer_name_2,
                                     }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                date_1 = date_time_converter.db_datetime(created_time_1)
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {"pmt_status": "EXPIRED",
                                       "txn_amt": float(amount),
                                       "pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED",
                                       "settle_status": "FAILED",
                                       "acquirer_code": "AXIS",
                                       "issuer_code": "AXIS",
                                       "txn_type": "CHARGE",
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code,
                                       "date": date,
                                       "device_serial": device_serial,

                                       "pmt_status_1": "AUTHORIZED",
                                       "txn_amt_1": float(amount),
                                       "pmt_mode_1": "BHARATQR",
                                       "pmt_state_1": "SETTLED",
                                       "rrn_1": str(rrn_1),
                                       "settle_status_1": "SETTLED",
                                       "acquirer_code_1": "AXIS",
                                       "issuer_code_1": "AXIS",
                                       "txn_type_1": "CHARGE",
                                       "mid_1": mid,
                                       "tid_1": tid,
                                       "org_code_1": org_code,
                                       "auth_code_1": auth_code_1,
                                       "date_1": date_1,
                                       "device_serial_1": device_serial,

                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": float(amount),
                                       "pmt_mode_2": "BHARATQR",
                                       "pmt_state_2": "SETTLED",
                                       "rrn_2": str(rrn_2),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "AXIS",
                                       "issuer_code_2": "AXIS",
                                       "txn_type_2": "CHARGE",
                                       "mid_2": mid,
                                       "tid_2": tid,
                                       "org_code_2": org_code,
                                       "auth_code_2": auth_code_2,
                                       "date_2": date_2,
                                       "device_serial_2": device_serial
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                res = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {res}")
                response = [x for x in res["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response}")

                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]
                device_serial_api = response['deviceSerial']

                response_1 = [x for x in res["txns"] if x["txnId"] == txn_id_1][0]
                logger.debug(f"Response after filtering data of first txn is : {response_1}")

                status_api_1 = response_1["status"]
                amount_api_1 = float(response_1["amount"])
                payment_mode_api_1 = response_1["paymentMode"]
                state_api_1 = response_1["states"][0]
                rrn_api_1 = response_1["rrNumber"]
                settlement_status_api_1 = response_1["settlementStatus"]
                issuer_code_api_1 = response_1["issuerCode"]
                acquirer_code_api_1 = response_1["acquirerCode"]
                orgCode_api_1 = response_1["orgCode"]
                mid_api_1 = response_1["mid"]
                tid_api_1 = response_1["tid"]
                txn_type_api_1 = response_1["txnType"]
                auth_code_api_1 = response_1["authCode"]
                date_api_1 = response_1["createdTime"]
                device_serial_api_1 = response_1['deviceSerial']

                response_2 = [x for x in res["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of second txn is : {response_2}")

                status_api_2 = response_2["status"]
                amount_api_2 = float(response_2["amount"])
                payment_mode_api_2 = response_2["paymentMode"]
                state_api_2 = response_2["states"][0]
                rrn_api_2 = response_2["rrNumber"]
                settlement_status_api_2 = response_2["settlementStatus"]
                issuer_code_api_2 = response_2["issuerCode"]
                acquirer_code_api_2 = response_2["acquirerCode"]
                orgCode_api_2 = response_2["orgCode"]
                mid_api_2 = response_2["mid"]
                tid_api_2 = response_2["tid"]
                txn_type_api_2 = response_2["txnType"]
                auth_code_api_2 = response_2["authCode"]
                date_api_2 = response_2["createdTime"]
                device_serial_api_2 = response_2['deviceSerial']

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "mid": mid_api,
                                     "txn_type": txn_type_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "device_serial": device_serial_api,

                                     "pmt_status_1": status_api_1,
                                     "txn_amt_1": amount_api_1,
                                     "pmt_mode_1": payment_mode_api_1,
                                     "pmt_state_1": state_api_1,
                                     "rrn_1": str(rrn_api_1),
                                     "settle_status_1": settlement_status_api_1,
                                     "acquirer_code_1": acquirer_code_api_1,
                                     "issuer_code_1": issuer_code_api_1, "mid_1": mid_api_1,
                                     "txn_type_1": txn_type_api_1,
                                     "tid_1": tid_api_1,
                                     "org_code_1": orgCode_api_1,
                                     "auth_code_1": auth_code_api_1,
                                     "date_1": date_time_converter.from_api_to_datetime_format(date_api_1),
                                     "device_serial_1": device_serial_api_1,

                                     "pmt_status_2": status_api_2,
                                     "txn_amt_2": amount_api_2,
                                     "pmt_mode_2": payment_mode_api_2,
                                     "pmt_state_2": state_api_2,
                                     "rrn_2": str(rrn_api_2),
                                     "settle_status_2": settlement_status_api_2,
                                     "acquirer_code_2": acquirer_code_api_2,
                                     "issuer_code_2": issuer_code_api_2, "mid_2": mid_api_2,
                                     "txn_type_2": txn_type_api_2,
                                     "tid_2": tid_api_2,
                                     "org_code_2": orgCode_api_2,
                                     "auth_code_2": auth_code_api_2,
                                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                                     "device_serial_2": device_serial_api_2
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
                expected_db_values = {"txn_amt": float(amount),
                                      "pmt_mode": "BHARATQR",
                                      "pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED",
                                      "acquirer_code" : "AXIS",
                                      "mid" :mid,
                                      "tid" : tid,
                                      "pmt_gateway": "ATOS",
                                      "settle_status": "FAILED",
                                      "device_serial":device_serial,
                                      "txn_type": "CHARGE",
                                      "bqr_pmt_state": "EXPIRED",
                                      "bqr_txn_amt": float(amount),
                                      "bqr_txn_type": "DYNAMIC_QR",
                                      "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "AXIS",
                                      "bqr_merchant_config_id": bqr_mc_id,
                                      "bqr_txn_primary_id": txn_id,
                                      "bqr_org_code": org_code,

                                      "txn_amt_1": float(amount),
                                      "pmt_mode_1": "BHARATQR",
                                      "pmt_status_1": "AUTHORIZED",
                                      "pmt_state_1": "SETTLED",
                                      "acquirer_code_1": "AXIS",
                                      "bank_name_1": "Axis Bank",
                                      "mid_1": mid,
                                      "tid_1": tid,
                                      "pmt_gateway_1": "ATOS",
                                      "rrn_1": str(rrn_1),
                                      "auth_code_1": auth_code_1,
                                      "settle_status_1": "SETTLED",
                                      "device_serial_1": device_serial,
                                      "txn_type_1": "CHARGE",
                                      "bqr_pmt_state_1": "SETTLED",
                                      "bqr_txn_amt_1": float(amount),
                                      "bqr_txn_type_1": "DYNAMIC_QR",
                                      "brq_terminal_info_id_1": terminal_info_id,
                                      "bqr_bank_code_1": "AXIS",
                                      "bqr_merchant_config_id_1": bqr_mc_id,
                                      "bqr_txn_primary_id_1": txn_id_1,
                                      "bqr_org_code_1": org_code,
                                      "bqr_auth_code_1": auth_code_1,
                                      "bqr_rrn_1": rrn_1,
                                      "bqr_merchant_pan_1": "ME" + txn_id.split('E')[1],

                                      "txn_amt_2": float(amount),
                                      "pmt_mode_2": "BHARATQR",
                                      "pmt_status_2": "AUTHORIZED",
                                      "pmt_state_2": "SETTLED",
                                      "acquirer_code_2": "AXIS",
                                      "bank_name_2": "Axis Bank",
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "pmt_gateway_2": "ATOS",
                                      "rrn_2": str(rrn_2),
                                      "auth_code_2":auth_code_2,
                                      "settle_status_2": "SETTLED",
                                      "device_serial_2": device_serial,
                                      "txn_type_2": "CHARGE",
                                      "bqr_pmt_state_2": "SETTLED",
                                      "bqr_txn_amt_2": float(amount),
                                      "bqr_txn_type_2": "DYNAMIC_QR",
                                      "brq_terminal_info_id_2": terminal_info_id,
                                      "bqr_bank_code_2": "AXIS",
                                      "bqr_merchant_config_id_2": bqr_mc_id,
                                      "bqr_txn_primary_id_2": txn_id_2,
                                      "bqr_org_code_2": org_code,
                                      "bqr_auth_code_2": auth_code_2,
                                      "bqr_rrn_2": rrn_2,
                                      "bqr_merchant_pan_2": "ME" + txn_id.split('E')[1],
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id ='" + txn_id + "';"
                logger.debug(f"Query to fetch transaction details of expired from database is: {query}")
                result = DBProcessor.getValueFromDB(query)
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                device_serial_db = result["device_serial"].iloc[0]
                txn_type_db = result["txn_type"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_1 + "'"
                logger.debug(f"Query to fetch data of first callback from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db_1 = result["state"].iloc[0]
                bqr_amount_db_1 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_1 = result["txn_type"].iloc[0]
                brq_terminal_info_id_db_1 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_1 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_1 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_1 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_1 = result['org_code'].values[0]
                bqr_auth_code_db_1 = result['txn_auth_code'].values[0]
                bqr_rrn_db_1 = result['rrn'].values[0]
                bqr_m_pan_db_1 = result['merchant_pan'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table for second txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db_2 = result["state"].iloc[0]
                bqr_amount_db_2 = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_2 = result["txn_type"].iloc[0]
                brq_terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_2 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_2 = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_2 = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db_2 = result['org_code'].values[0]
                bqr_auth_code_db_2 = result['txn_auth_code'].values[0]
                bqr_rrn_db_2 = result['rrn'].values[0]
                bqr_m_pan_db_2 = result['merchant_pan'].values[0]

                actual_db_values = {"txn_amt": amount_db,
                                    "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db,
                                    "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db,
                                    "mid" :mid_db,
                                    "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "device_serial":device_serial_db,
                                    "txn_type": txn_type_db,
                                    "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db,
                                    "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_org_code": bqr_org_code_db,

                                    "txn_amt_1": amount_db_1,
                                    "pmt_mode_1": payment_mode_db_1,
                                    "pmt_status_1": payment_status_db_1,
                                    "pmt_state_1": payment_state_db_1,
                                    "acquirer_code_1": acquirer_code_db_1,
                                    "bank_name_1": bank_name_db_1,
                                    "mid_1": mid_db_1,
                                    "tid_1": tid_db_1,
                                    "pmt_gateway_1": payment_gateway_db_1,
                                    "rrn_1": rrn_db_1,
                                    "auth_code_1": auth_code_db_1,
                                    "settle_status_1": settlement_status_db_1,
                                    "device_serial_1": device_serial_db_1,
                                    "txn_type_1": txn_type_db_1,
                                    "bqr_pmt_state_1": bqr_state_db_1,
                                    "bqr_txn_amt_1": bqr_amount_db_1,
                                    "bqr_txn_type_1": bqr_txn_type_db_1,
                                    "brq_terminal_info_id_1": brq_terminal_info_id_db_1,
                                    "bqr_bank_code_1": bqr_bank_code_db_1,
                                    "bqr_merchant_config_id_1": bqr_merchant_config_id_db_1,
                                    "bqr_txn_primary_id_1": bqr_txn_primary_id_db_1,
                                    "bqr_org_code_1": bqr_org_code_db_1,
                                    "bqr_auth_code_1": bqr_auth_code_db_1,
                                    "bqr_rrn_1": bqr_rrn_db_1,
                                    "bqr_merchant_pan_1": bqr_m_pan_db_1,

                                    "txn_amt_2": amount_db_2,
                                    "pmt_mode_2": payment_mode_db_2,
                                    "pmt_status_2": payment_status_db_2,
                                    "pmt_state_2": payment_state_db_2,
                                    "acquirer_code_2" : acquirer_code_db_2,
                                    "bank_name_2" : bank_name_db_2,
                                    "mid_2" :mid_db_2,
                                    "tid_2" : tid_db_2,
                                    "pmt_gateway_2": payment_gateway_db_2,
                                    "rrn_2" : rrn_db_2,
                                    "auth_code_2":auth_code_db_2,
                                    "settle_status_2": settlement_status_db_2,
                                    "device_serial_2":device_serial_db_2,
                                    "txn_type_2": txn_type_db_2,
                                    "bqr_pmt_state_2": bqr_state_db_2,
                                    "bqr_txn_amt_2": bqr_amount_db_2,
                                    "bqr_txn_type_2": bqr_txn_type_db_2,
                                    "brq_terminal_info_id_2": brq_terminal_info_id_db_2,
                                    "bqr_bank_code_2": bqr_bank_code_db_2,
                                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_2,
                                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_2,
                                    "bqr_org_code_2": bqr_org_code_db_2,
                                    "bqr_auth_code_2":bqr_auth_code_db_2,
                                    "bqr_rrn_2":bqr_rrn_db_2,
                                    "bqr_merchant_pan_2":bqr_m_pan_db_2,
                                    }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date_1, txn_time_1 = date_time_converter.to_chargeslip_format(created_time_1)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)

                expected_charge_slip_values_1 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_1),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_1,
                    'time': txn_time_1, 'AUTH CODE': str(auth_code_1)
                }

                expected_charge_slip_values_2 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_2)
                }

                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(txn_id_1,
                                                                                            {"username": app_username,
                                                                                             "password": app_password},
                                                                                            expected_charge_slip_values_1)

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_2,
                                                                                            {"username": app_username,
                                                                                             "password": app_password},
                                                                                            expected_charge_slip_values_2)

                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

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