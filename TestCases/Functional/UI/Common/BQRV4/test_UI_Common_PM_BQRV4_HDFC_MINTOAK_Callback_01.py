import random
import sys
import time
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, ResourceAssigner, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_378():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Success_UPI_Callback_HDFC_MINTOAK
    Sub Feature Description: Verification of a BQRV4 Callback Success transaction via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 378: TC378
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

        query = f"select org_code from org_employee where username='{str(app_username)}'"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username, portal_pw=portal_password,
                                                           bank_code_bqr='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        logger.debug(f"Fetching mid, tid from database for current merchant: {mid}, {tid}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)----------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=True,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            # home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info("App homepage loaded successfully")

            amount = random.randint(251, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].values[0]
            logger.debug(f"Fetching Txn_id data base : Txn_id : {txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating random mtxn_id: {mtxn_id}")
            issuer_ref_number = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating random issuer_ref_number: {issuer_ref_number}")

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")

            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id = '{txn_id}'"
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            rrn = result['rr_number'].values[0]
            created_time = result['created_time'].values[0]
            logger.debug(
                f"Fetching auth_code, rrn, created_time from database for current merchant:{auth_code}, {rrn}, {created_time}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"Fetching amount from db : {amount_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"Fetching payment mode from db : {payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"Fetching payment status from db : {payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"Fetching payment state from db : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"Fetching acquirer code from db : {acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetching bank name from db : {bank_name_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"Fetching mid from db : {mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"Fetching tid from db : {tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment gateway from db : {payment_gateway_db}")
            rr_number_db = result["rr_number"].values[0]
            logger.debug(f"Fetching rrn from db : {rr_number_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"Fetching settlement status from db : {settlement_status_db}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
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

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer from api : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org coe from api : {status_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api : {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "txn_type": txn_type_api,
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
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_name": "HDFC Bank",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "MINTOAK",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "upi_pmt_status": "AUTHORIZED",
                    "upi_txn_type": "PAY_BQR",
                    "upi_mc_id": upi_mc_id,
                    "upi_bank_code": "HDFC_MINTOAK"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"Fetching status from db : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching txn type from db : {upi_txn_type_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching mc id from db : {upi_mc_id_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bank code from db : {upi_bank_code_db}")

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
                    "upi_pmt_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_bank_code": upi_bank_code_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": rrn
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code_portal = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': "" if auth_code is None else auth_code
                }
                receipt_validator.perform_charge_slip_validations(txn_id, {
                    "username": app_username,
                    "password": app_password
                }, expected_values)
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
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_379():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPI_Failed_Callback_HDFC_MINTOAK
    Sub Feature Description: Verification of a BQRV4 Callback Failed transaction via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 379: TC379
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

        query = f"select org_code from org_employee where username='{str(app_username)}'"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        logger.debug(f"Fetching mid  from bharatqr_merchant_config : {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching tid  from bharatqr_merchant_config : {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"Fetching terminal_info_id  from bharatqr_merchant_config : {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"Fetching id  from bharatqr_merchant_config : {bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching merchant_pan  from bharatqr_merchant_config : {bqr_m_pan}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)----------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            # home_page.check_home_page_logo()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")

            amount = random.randint(251, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")

            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            query = f"select * from bharatqr_txn where org_code='{org_code}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].values[0]
            logger.debug(f"Fetching Txn_id from data base : Txn_id : {txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating random mtxn_id: {mtxn_id}")
            issuer_ref_number = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating random issuer_ref_number: {issuer_ref_number}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_failed')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")

            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id = '{txn_id}'"
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            rrn = result['rr_number'].values[0]
            created_time = result['created_time'].values[0]
            logger.debug(
                f"Fetching auth_code, rrn, created_time from database for current merchant:{auth_code}, {rrn}, {created_time}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"Fetching amount from db : {amount_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"Fetching payment mode from db : {payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"Fetching payment status from db : {payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"Fetching payment state from db : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"Fetching acquirer code from db : {acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetching bank name from db : {bank_name_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"Fetching mid from db : {mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"Fetching tid from db : {tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment gateway from db : {payment_gateway_db}")
            rr_number_db = result["rr_number"].values[0]
            logger.debug(f"Fetching rrn from db : {rr_number_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"Fetching settlement status from db : {settlement_status_db}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "rrn": str(rrn)
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                payment_page.click_on_back_btn()
                # home_page.click_on_back_btn_enter_amt_page()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
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
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rrn": str(app_rrn)
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
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "rrn": str(rrn)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password}
                                                          )
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api: {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from api: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api: {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api: {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api: {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching status from api: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api: {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api: {date_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api : {rrn_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "rrn": rrn_api
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
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_name": "HDFC Bank",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "MINTOAK",
                    "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "upi_pmt_status": "FAILED",
                    "upi_txn_type": "PAY_BQR",
                    "upi_mc_id": upi_mc_id,
                    "upi_bank_code": "HDFC_MINTOAK"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"Fetching upi status from db: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching upi txn type from db: {upi_txn_type_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching upi mc id from db: {upi_mc_id_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching upi bank code from db: {upi_bank_code_db}")

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
                    "upi_pmt_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_bank_code": upi_bank_code_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": rrn
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code_portal = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_403():
    """
    Sub Feature Code: UI_Common_BQRV4_UPI_Success_Callback_After_QR_Expiry_Auto_Refund_Disabled_HDFC_MINTOAK
    Sub Feature Description: Performing a BQRV4 UPI pure upi success callback via HDFC after expiry the qr
     when auto refund is disabled.
    TC naming code description: 100: Payment Method, 102: BQRV4, 403: TC403
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

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        logger.debug("Fetching details from database for current merchant:")
        mid = result["mid"].values[0]
        logger.debug(f"Fetching MID: {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching TID: {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"Fetching Terminal Info ID: {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"Fetching BQR MC ID: {bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching BQR M PAN: {bqr_m_pan}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Query result,pgMerchantId : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result,vpa : {vpa}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ----------------------------------------PreConditions(Completed)-------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = float(random.randint(251, 300))
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount} and order ID:{order_id}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": order_id
            })
            response = APIProcessor.send_request(api_details)
            txn_id = response["txnId"]
            order_id = response["externalRefNumber"]
            logger.debug(f"Fetching txn_id from the API_OUTPUT, txn_id : {txn_id}")
            logger.debug(f"Fetching order_id from the API_OUTPUT, order_id : {order_id}")

            time.sleep(75)

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Generating mtxn_id : {mtxn_id}")
            issuer_ref_number = str(random.randint(10000000, 99999999))
            logger.debug(f"Generating issuer_ref_number : {issuer_ref_number}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch txn data from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {txn_id} and {rrn}")
            created_date = result['created_time'].values[0]
            logger.debug(f"Fetching created_date from txn table:{created_date}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Auth Code from txn table: {auth_code}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result['id'].values[0]
            logger.debug(f"Fetching txn_id_new from txn table:{txn_id_new}")
            created_date_new = result['created_time'].values[0]
            logger.debug(f"Fetching created_date_new from txn table:{created_date_new}")
            rrn_new = result['rr_number'].values[0]
            logger.debug(f"Fetching RRN from txn table:{rrn_new}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table:{auth_code_2}")

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
                date_and_time = date_time_converter.to_app_format(created_date)
                date_and_time_new = date_time_converter.to_app_format(created_date_new)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_new,
                    "rrn_2": str(rrn_new),
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_new
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)
                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching app_rrn_new from txn history for the txn : {txn_id_new}, {app_rrn_new}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new,
                    "pmt_status_2": payment_status_new.split(':')[1],
                    "txn_amt_2": app_amount_new.split(' ')[1],
                    "txn_id_2": app_txn_id_new,
                    "rrn_2": str(app_rrn_new),
                    "settle_status_2": app_settlement_status_new,
                    "order_id_2": app_order_id_new,
                    "payment_msg_2": app_payment_msg_new,
                    "date_2": app_date_and_time_new
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
                date = date_time_converter.db_datetime(created_date)
                date_new = date_time_converter.db_datetime(created_date_new)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(rrn_new),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": "CHARGE",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_new,
                    "order_id_2": order_id,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response_list = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response_list["txns"] if x["txnId"] == txn_id][0]
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
                logger.debug(
                    f"Details from Original TXN: status:{status_api}, amount:{amount_api}, payment mode:{payment_mode_api}, state:{state_api}, settlement status:{settlement_status_api}, issuer code:{issuer_code_api}, acquirer code:{acquirer_code_api}, org code:{org_code_api}, mid:{mid_api}, tid:{tid_api}, txn type:{txn_type_api}, date:{date_api}")

                response = [x for x in response_list["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new = response["status"]
                amount_api_new = float(response["amount"])
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                org_code_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                date_api_new = response["createdTime"]
                order_id_api_new = response["orderNumber"]
                logger.debug(
                    f"Details from Original TXN: status:{status_api_new}, amount:{amount_api_new}, payment mode:{payment_mode_api_new}, state:{state_api_new}, settlement status:{settlement_status_api_new}, issuer code:{issuer_code_api_new}, acquirer code:{acquirer_code_api_new}, org code:{org_code_api_new}, mid:{mid_api_new}, tid:{tid_api_new}, txn type:{txn_type_api_new}, date:{date_api_new}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new,
                    "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "rrn_2": str(rrn_api_new),
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "issuer_code_2": issuer_code_api_new,
                    "txn_type_2": txn_type_api_new,
                    "mid_2": mid_api_new,
                    "tid_2": tid_api_new,
                    "org_code_2": org_code_api_new,
                    "order_id_2": order_id_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new)
                }
                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------
        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "txn_amt": amount,
                    "pmt_mode": "BHARATQR",
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "acquirer_code": "HDFC",
                    "bank_name": "HDFC Bank",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "MINTOAK",
                    "settle_status": "FAILED",
                    # "bqr_pmt_status": "Failed",
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_mc_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "upi_txn_status_2": "AUTHORIZED",
                    "rrn_2": rrn_new,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "bank_code_2": "HDFC",
                    "payment_gateway_2": "MINTOAK",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "HDFC_MINTOAK",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "order_id_2": order_id,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                logger.debug(f"Fetching DB details for txn: {txn_id}")
                amount_db = float(result["amount"].values[0])
                logger.debug(f"Fetching Amount from txn table: {amount_db}")
                payment_mode_db = result["payment_mode"].values[0]
                logger.debug(f"Fetching Payment Mode from txn table: {payment_mode_db}")
                payment_status_db = result["status"].values[0]
                logger.debug(f"Fetching Payment Status from txn table: {payment_status_db}")
                payment_state_db = result["state"].values[0]
                logger.debug(f"Fetching Payment State from txn table: {payment_state_db}")
                acquirer_code_db = result["acquirer_code"].values[0]
                logger.debug(f"Fetching Acquirer Code from txn table: {acquirer_code_db}")
                bank_name_db = result["bank_name"].values[0]
                logger.debug(f"Fetching Bank Name from txn table: {bank_name_db}")
                mid_db = result["mid"].values[0]
                logger.debug(f"Fetching MID from txn table: {mid_db}")
                tid_db = result["tid"].values[0]
                logger.debug(f"Fetching TID from txn table: {tid_db}")
                payment_gateway_db = result["payment_gateway"].values[0]
                logger.debug(f"Fetching Payment Gateway from txn table: {payment_gateway_db}")
                settlement_status_db = result["settlement_status"].values[0]
                logger.debug(f"Fetching Settlement Status from txn table: {settlement_status_db}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                logger.debug(f"Fetching details from bharatqr_txn table for ID {txn_id}:")
                bqr_status_db = result["status_desc"].values[0]
                logger.debug(f"Fetching Status from bharatqr_txn table: {bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching State from bharatqr_txn table: {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].values[0])
                logger.debug(f"Fetching Amount from bharatqr_txn table: {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type from bharatqr_txn table: {bqr_txn_type_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching Terminal Info from bharatqr_txn table: {brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from bharatqr_txn table: {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching Merchant Config from bharatqr_txn table: {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching Transaction Primary ID from bharatqr_txn table: {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching Org Code from bharatqr_txn table: {bqr_org_code_db}")

                query = f"select * from txn where id='{txn_id_new}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                logger.debug(f"Fetching DB details for txn: {txn_id_new}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].values[0]
                logger.debug(f"Fetching Payment Status from txn table: {status_db_new}")
                payment_mode_db_new = result["payment_mode"].values[0]
                logger.debug(f"Fetching Payment Mode from txn table: {payment_mode_db_new}")
                amount_db_new = float(result["amount"].values[0])
                logger.debug(f"Fetching Amount from txn table: {amount_db_new}")
                state_db_new = result["state"].values[0]
                logger.debug(f"Fetching Payment State from txn table: {state_db_new}")
                payment_gateway_db_new = result["payment_gateway"].values[0]
                logger.debug(f"Fetching Payment Gateway from txn table: {payment_gateway_db_new}")
                acquirer_code_db_new = result["acquirer_code"].values[0]
                logger.debug(f"Fetching Acquirer Code from txn table: {acquirer_code_db_new}")
                bank_code_db_new = result["bank_code"].values[0]
                logger.debug(f"Fetching bank_code from txn table: {bank_code_db_new}")
                settlement_status_db_new = result["settlement_status"].values[0]
                logger.debug(f"Fetching settlement_status from txn table: {settlement_status_db_new}")
                tid_db_new = result['tid'].values[0]
                logger.debug(f"Fetching TID from txn table: {tid_db_new}")
                mid_db_new = result['mid'].values[0]
                logger.debug(f"Fetching MID from txn table: {mid_db_new}")
                order_id_db_new = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id: {order_id_db_new}")
                rrn_db_new = result['rr_number'].values[0]
                logger.debug(f"Fetching rrn: {rrn_db_new}")

                query = f"select * from upi_txn where txn_id='{txn_id_new}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                logger.debug("Fetching UPI details from database")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].values[0]
                logger.debug(f"Fetching Status: {upi_status_db_new}")
                upi_txn_type_db_new = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type: {upi_txn_type_db_new}")
                upi_bank_code_db_new = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code: {upi_bank_code_db_new}")
                upi_mc_id_db_new = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching MC ID: {upi_mc_id_db_new}")

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
                    "settle_status": settlement_status_db,
                    # "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_new,
                    "pmt_state_2": state_db_new,
                    "pmt_mode_2": payment_mode_db_new,
                    "txn_amt_2": amount_db_new,
                    "upi_txn_status_2": upi_status_db_new,
                    "settle_status_2": settlement_status_db_new,
                    "acquirer_code_2": acquirer_code_db_new,
                    "bank_code_2": bank_code_db_new,
                    "payment_gateway_2": payment_gateway_db_new,
                    "upi_txn_type_2": upi_txn_type_db_new,
                    "upi_bank_code_2": upi_bank_code_db_new,
                    "upi_mc_id_2": upi_mc_id_db_new,
                    "rrn_2": rrn_db_new,
                    "mid_2": mid_db_new,
                    "tid_2": tid_db_new,
                    "order_id_2": order_id_db_new,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # ---------------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_new)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": '-' if rrn is None else rrn,
                    "auth_code": '-' if auth_code is None else auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_new,
                    "rrn_2": '-' if rrn_new is None else str(rrn_new),
                    "auth_code_2": '-' if auth_code_2 is None else auth_code_2,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                logger.debug("Fetching Portal details for first TXN:")
                date_time_2 = transaction_details[0]['Date & Time']
                logger.debug(f"Date and Time: {date_time_2}")
                transaction_id_2 = transaction_details[0]['Transaction ID']
                logger.debug(f"Transaction ID: {transaction_id_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Total Amount: {total_amount_2}")
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                logger.debug(f"Auth Code Portal: {auth_code_portal_2}")
                rr_number_2 = transaction_details[0]['RR Number']
                logger.debug(f"RR Number: {rr_number_2}")
                transaction_type_2 = transaction_details[0]['Type']
                logger.debug(f"Transaction Type: {transaction_type_2}")
                status_2 = transaction_details[0]['Status']
                logger.debug(f"Status: {status_2}")
                username_2 = transaction_details[0]['Username']
                logger.debug(f"Username: {username_2}")

                logger.debug("Fetching Portal details for second TXN:")
                date_time = transaction_details[1]['Date & Time']
                logger.debug(f"Date and Time: {date_time}")
                transaction_id = transaction_details[1]['Transaction ID']
                logger.debug(f"Transaction ID: {transaction_id}")
                total_amount = transaction_details[1]['Total Amount'].split()
                logger.debug(f"Total Amount: {total_amount}")
                rr_number = transaction_details[1]['RR Number']
                logger.debug(f"RR Number: {rr_number}")
                transaction_type = transaction_details[1]['Type']
                logger.debug(f"Transaction Type: {transaction_type}")
                status = transaction_details[1]['Status']
                logger.debug(f"Status: {status}")
                username = transaction_details[1]['Username']
                logger.debug(f"Username: {username}")
                auth_code_portal = transaction_details[1]['Auth Code']
                logger.debug(f"Auth Code Portal: {auth_code_portal}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal,

                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": str(rr_number_2),
                    "auth_code_2": auth_code_portal_2,
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_date_new)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn_new),
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),
                    'date': txn_date,
                    'time': txn_time,
                    "AUTH CODE": '' if auth_code_2 is None else auth_code_2
                }
                receipt_validator.perform_charge_slip_validations(txn_id_new,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_409():
    """
    Sub Feature Code: UI_Common_BQRV4_UPI_Success_Two_Callback_Before_QR_Expiry_Auto_Refund_Disabled_HDFC_MINTOAK
    Sub Feature Description: Performing a pure upi success two callback via HDFC_MINTOAK when auto refund is disabled.
    TC naming code description:
    100: Payment Method,
    102: BQRV4,
    409: TC409
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

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

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

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        logger.debug(f"Fetching MID from bharatqr_merchant_config: {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching TID from bharatqr_merchant_config: {tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"Fetching Terminal Info ID from bharatqr_merchant_config: {terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"Fetching BQR MC ID from bharatqr_merchant_config: {bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching BQR M PAN from bharatqr_merchant_config: {bqr_m_pan}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from upi_merchant_config for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Fetching pg_merchant_id from upi_merchant_config: {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = float(random.randint(251, 300))
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Initiating bqr for the amount of {amount} and order ID:{order_id}")
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": order_id
            })
            response = APIProcessor.send_request(api_details)
            txn_id = response["txnId"]
            order_id = response["externalRefNumber"]
            logger.debug(f"Fetching txn_id  from the API_OUTPUT, txn_id : {txn_id}")
            logger.debug(f"Fetching order ID from the API_OUTPUT, orderID : {order_id}")

            logger.debug(f"preparing data to perform the encryption generation for first callback")
            mtxn_id_first = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"Fetching mtxn_id_first from the API_OUTPUT, orderID : {mtxn_id_first}")
            rrn = str(random.randint(10000000, 99999999))
            logger.debug(f"Fetching issuer_ref_number_first from the API_OUTPUT, orderID : {rrn}")

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id_first
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing first callback for mintoak")

            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id the DB after first callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_first = result['id'].values[0]
            logger.debug(f"Fetching txn ID from txn table : {txn_id_first}")
            created_date_first = result['created_time'].values[0]
            logger.debug(f"Fetching created_date_first from txn table : {created_date_first}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table : {auth_code}")

            logger.debug(f"preparing data to perform the encryption generation for second callback")
            mtxn_id_second = str(random.randint(10000000000000000000, 99999999999999999999))
            rrn_2 = str(random.randint(10000000, 99999999))

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id_second
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn_2
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id the DB after first callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_second = result['id'].values[0]
            logger.debug(f"Fetching txn from txn table : {txn_id_second}")
            created_date_second = result['created_time'].values[0]
            logger.debug(f"created_date_second for second Callback:{created_date_second}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn table : {auth_code_2}")

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
                date_and_time = date_time_converter.to_app_format(created_date_first)
                date_and_time_2 = date_time_converter.to_app_format(created_date_second)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id_first,
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_second,
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(txn_id_first)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_first}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_first}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_first}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_first}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_first}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_first}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_first}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_first}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching app_rrn_new from txn history for the txn : {txn_id_first}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_second)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_second}, {payment_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_second}, {app_date_and_time_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_second}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_second}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_second}, {app_amount_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_second}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_second}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_second}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching app_rrn_new_3 from txn history for the txn : {txn_id_second}, {app_rrn_2}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "settle_status_2": app_settlement_status_2,
                    "order_id_2": app_order_id_2,
                    "payment_msg_2": app_payment_msg_2,
                    "date_2": app_date_and_time_2
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
                date_new = date_time_converter.db_datetime(created_date_first)
                date_new_3 = date_time_converter.db_datetime(created_date_second)
                expected_api_values = {
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "date": date_new,
                    "order_id": order_id,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": "CHARGE",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_new_3,
                    "order_id_2": order_id
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response_list = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response_list["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                logger.debug(f"MID:{mid_api},TID:{tid_api}")

                response = [x for x in response_list["txns"] if x["txnId"] == txn_id_first][0]
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
                order_id_api = response["orderNumber"]
                logger.debug(
                    f"API Details for second txn : rrn: {rrn_api},status:{status_api}, amount:{amount_api}, payment mode:{payment_mode_api}, state:{state_api}, settlement status:{settlement_status_api}, issuer code:{issuer_code_api}, acquirer code:{acquirer_code_api}, org code:{orgCode_api}, mid:{mid_api}, tid:{tid_api}, txn type:{txn_type_api}, date:{date_api}")

                response = [x for x in response_list["txns"] if x["txnId"] == txn_id_second][0]
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
                order_id_api_2 = response["orderNumber"]
                logger.debug(
                    f"API Details for second txn : rrn: {rrn_api_2},status:{status_api_2}, amount:{amount_api_2}, payment mode:{payment_mode_api_2}, state:{state_api_2}, settlement status:{settlement_status_api_2}, issuer code:{issuer_code_api_2}, acquirer code:{acquirer_code_api_2}, org code:{org_code_api_2}, mid:{mid_api_2}, tid:{tid_api_2}, txn type:{txn_type_api_2}, date:{date_api_2}")

                actual_api_values = {
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "order_id_2": order_id_api_2,
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
                    "upi_txn_status": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "MINTOAK",
                    "upi_txn_type": "PAY_BQR",
                    "upi_bank_code": "HDFC_MINTOAK",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": float(amount),
                    "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "bank_code_2": "HDFC",
                    "payment_gateway_2": "MINTOAK",
                    "rrn_2": str(rrn_2),
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "HDFC_MINTOAK",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "order_id_2": order_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id_first}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                logger.debug(f"Fetching Payment Status from txn table: {status_db}")
                payment_mode_db = result["payment_mode"].values[0]
                logger.debug(f"Fetching Payment Mode from txn table: {payment_mode_db}")
                amount_db = float(result["amount"].values[0])
                logger.debug(f"Fetching Amount from txn table: {amount_db}")
                state_db = result["state"].values[0]
                logger.debug(f"Fetching Payment State from txn table: {state_db}")
                payment_gateway_db = result["payment_gateway"].values[0]
                logger.debug(f"Fetching Payment Gateway from txn table: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].values[0]
                logger.debug(f"Fetching Acquirer Code from txn table: {acquirer_code_db}")
                bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bank_code_db_new_2 from txn table: {bank_code_db}")
                settlement_status_db = result["settlement_status"].values[0]
                logger.debug(f"Fetching Settlement Status from txn table: {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching TID from txn table: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching MID from txn table: {mid_db}")
                order_id_db = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id_db_new_2 from txn table: {order_id_db}")
                rrn_db = result['rr_number'].values[0]
                logger.debug(f"Fetching rrn_db_2 from txn table: {rrn_db}")

                query = f"select * from upi_txn where txn_id='{txn_id_first}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                logger.debug(f"Fetching Status from upi_txn: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type from upi_txn: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from upi_txn: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching MC ID from upi_txn: {upi_mc_id_db}")

                query = f"select * from txn where id='{txn_id_second}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result["status"].values[0]
                logger.debug(f"Fetching Payment Status from txn table: {status_db_2}")
                payment_mode_db_2 = result["payment_mode"].values[0]
                logger.debug(f"Fetching Payment Mode from txn table: {payment_mode_db_2}")
                amount_db_2 = float(result["amount"].values[0])
                logger.debug(f"Fetching Amount from txn table: {amount_db_2}")
                state_db_2 = result["state"].values[0]
                logger.debug(f"Fetching Payment State from txn table: {state_db_2}")
                payment_gateway_db_2 = result["payment_gateway"].values[0]
                logger.debug(f"Fetching Payment Gateway from txn table: {payment_gateway_db_2}")
                acquirer_code_db_2 = result["acquirer_code"].values[0]
                logger.debug(f"Fetching Acquirer Code from txn table: {acquirer_code_db_2}")
                bank_code_db_2 = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from txn table: {bank_code_db_2}")
                settlement_status_db_2 = result["settlement_status"].values[0]
                logger.debug(f"Fetching Settlement Status from txn table: {settlement_status_db_2}")
                tid_db_2 = result['tid'].values[0]
                logger.debug(f"Fetching TID from txn table: {tid_db_2}")
                mid_db_2 = result['mid'].values[0]
                logger.debug(f"Fetching MID from txn table: {mid_db_2}")
                order_id_db_2 = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id_db_new_2 from txn table: {order_id_db_2}")
                rrn_db_2 = result['rr_number'].values[0]
                logger.debug(f"Fetching rrn_db_2 from txn table: {rrn_db_2}")

                query = f"select * from upi_txn where txn_id='{txn_id_second}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].values[0]
                logger.debug(f"Fetching Status from upi_txn table: {upi_status_db_2}")
                upi_txn_type_db_2 = result["txn_type"].values[0]
                logger.debug(f"Fetching Transaction Type from upi_txn table: {upi_txn_type_db_2}")
                upi_bank_code_db_2 = result["bank_code"].values[0]
                logger.debug(f"Fetching Bank Code from upi_txn table: {upi_bank_code_db_2}")
                upi_mc_id_db_2 = result["upi_mc_id"].values[0]
                logger.debug(f"Fetching MC ID from upi_txn table: {upi_mc_id_db_2}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "rrn": rrn_db,
                    "order_id": order_id_db,
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt_2": amount_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "payment_gateway_2": payment_gateway_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "rrn_2": rrn_db_2,
                    "tid_2": tid_db_2,
                    "order_id_2": order_id_db_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_date_first)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_second)
                expected_portal_values = {
                    "auth_code": '-' if auth_code is None else auth_code,
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id_first,
                    "rrn": str(rrn),

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_second,
                    "rrn_2": str(rrn_2),
                    "auth_code_2": '-' if auth_code_2 is None else auth_code_2,
                }

                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)

                date_time = transaction_details[1]['Date & Time']
                logger.debug(f"Date and Time from Portal: {date_time}")
                transaction_id = transaction_details[1]['Transaction ID']
                logger.debug(f"Transaction ID: {transaction_id}")
                total_amount = transaction_details[1]['Total Amount'].split()
                logger.debug(f"Total Amount: {total_amount}")
                rr_number = transaction_details[1]['RR Number']
                logger.debug(f"RR Number: {rr_number}")
                transaction_type = transaction_details[1]['Type']
                logger.debug(f"Transaction Type: {transaction_type}")
                status = transaction_details[1]['Status']
                logger.debug(f"Status: {status}")
                username = transaction_details[1]['Username']
                logger.debug(f"Username: {username}")
                auth_code_portal = transaction_details[1]['Auth Code']
                logger.debug(f"Auth Code from Portal: {auth_code_portal}")

                date_time_2 = transaction_details[0]['Date & Time']
                logger.debug(f"Date and Time from Portal: {date_time_2}")
                transaction_id_2 = transaction_details[0]['Transaction ID']
                logger.debug(f"Transaction ID: {transaction_id_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Total Amount: {total_amount_2}")
                rr_number_2 = transaction_details[0]['RR Number']
                logger.debug(f"RR Number: {rr_number_2}")
                transaction_type_2 = transaction_details[0]['Type']
                logger.debug(f"Transaction Type: {transaction_type_2}")
                status_2 = transaction_details[0]['Status']
                logger.debug(f"Status: {status_2}")
                username_2 = transaction_details[0]['Username']
                logger.debug(f"Username: {username_2}")
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                logger.debug(f"Auth Code from Portal: {auth_code_portal_2}")

                actual_portal_values = {
                    "auth_code": auth_code_portal,
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": str(rr_number),

                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": str(rr_number_2),
                    "auth_code_2": auth_code_portal_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_date_second)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code_2 is None else auth_code_2
                }
                receipt_validator.perform_charge_slip_validations(txn_id_second,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
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
