import json
import random
import sys
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_L3_5058_101_001():
    """
    Sub Feature Code: L3_5058_DMart_Ready_UPI_Success_Checkstatus_With_GSTIN_HDFC
    Sub Feature Description: verification of Dmart ready upi success checkstatus with GSTIN information via HDFC through
    sample app
    TC naming code description: L3_5058: L3_Ticket_Id, 101: UPI, 001: TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from org_employee table: {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Value of pg_merchant_id from upi_merchant_config table: {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table: {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table: {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table: {mid}")
        gst_in = result['gst_in'].values[0]
        logger.debug(f"Value of gst_in from upi_merchant_config table: {mid}")

        query = f"update upi_merchant_config set gst_in='27AANCA0090J1ZK' where id='{upi_mc_id}'; "
        logger.debug(f"Query to update upi_merchant_config to add gst_in : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query to fetch result from upi_merchant_config to add gst_in : {result}")

        refresh_db()
        logger.debug(f"Using DB refresh method after adding gst_in")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(500, 600)
            gst_amt = (amount * 10) / 100
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")
            app_driver = TestSuiteSetup.initialize_app_driver_for_sample_app(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.config_merchant_for_sample_app(org_code=org_code, username=app_username, password=app_password)
            logger.info(f"configured merchant for sample app : {org_code}, {app_username}, {app_password}")
            payment_page = PaymentPage(app_driver)
            payment_page.upi_txn_in_sample_app()
            logger.info(f"selected upi transaction in sample app")
            payment_page.enter_order_id_and_amount(order_id=order_id, amt=amount)
            logger.info(f"entered order_id and amount: {order_id}, {amount}")
            payment_page.enter_gst_amount(gst_amt=gst_amt)
            logger.info(f"entered gst amount: {gst_amt}")
            payment_page.confirm_upi_txn_in_sample_app()
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            txn_amt_app = payment_page.fetch_payment_amount()
            logger.debug(f"fetching txn amount from success payment page : {txn_amt_app}")
            pmt_mode_app = payment_page.fetch_payment_mode()
            logger.debug(f"fetching payment mode from success payment page : {pmt_mode_app}")
            pmt_msg_app = payment_page.fetch_payment_status()
            logger.debug(f"fetching payment msg from success payment page : {pmt_msg_app}")
            payment_page.click_on_view_details_in_sample_app()
            customer_name_app = payment_page.fetch_customer_name_text()
            logger.debug(f"fetching customer_name from view details page : {customer_name_app}")
            order_id_app = payment_page.fetch_order_id_text()
            logger.debug(f"fetching order_id from view details page : {order_id_app}")
            mid_app = payment_page.fetch_mid_text()
            logger.debug(f"fetching mid from view details page : {mid_app}")
            tid_app = payment_page.fetch_tid_text()
            logger.debug(f"fetching tid from view details page : {tid_app}")
            rrn_app = payment_page.fetch_rrn_text()
            logger.debug(f"fetching rrn from view details page : {rrn_app}")
            txn_id_app = payment_page.fetch_transaction_id_text()
            logger.debug(f"fetching txn_id from view details page : {txn_id_app}")
            date_app = payment_page.fetch_date_text()
            logger.debug(f"fetching date from view details page : {date_app}")
            payer_name_app = payment_page.fetch_payer_name_text()
            logger.debug(f"fetching payer_name from view details page : {payer_name_app}")
            status_app = payment_page.fetch_status_text()
            logger.debug(f"fetching status from view details page : {status_app}")
            payment_page.click_on_dismiss()
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id value from the txn table : {txn_id}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table is : {payer_name}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table is : {auth_code}")
            status_db = result["status"].iloc[0]
            logger.info(f"Fetching status from txn table: {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.info(f"Fetching amount from txn table: {amount_db}")
            state_db = result["state"].iloc[0]
            logger.info(f"Fetching state from txn table: {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.info(f"Fetching bank code from txn table: {bank_code_db}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.info(f"Fetching bank name from txn table: {bank_name_db}")
            payer_name_db = result["payer_name"].iloc[0]
            logger.info(f"Fetching payer name from txn table: {payer_name_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            rrn = result["rr_number"].iloc[0]
            logger.info(f"Fetching rrn from txn table: {rrn}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].iloc[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].iloc[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_msg_db = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

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
        # -----------------------------------------Start of App Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "txn_amt": "{:.2f}".format(amount),
                    "pmt_msg": "Payment Successful",
                    "pmt_status": "AUTHORIZED",
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": order_id,
                    "date": date_and_time,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                actual_app_values = {
                    "pmt_mode": pmt_mode_app,
                    "txn_amt": txn_amt_app.split(' ')[1],
                    "pmt_msg": pmt_msg_app,
                    "pmt_status": status_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "date": date_app,
                    "customer_name": customer_name_app,
                    "payer_name": payer_name_app,
                    "mid": mid_app,
                    "tid": tid_app
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation-----------------------------------------
        #
        # -----------------------------------------Start of API Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": order_id,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api response")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response")

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
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "order_id": order_id_api,
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
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "payer_name": payer_name,
                    "bank_name": "HDFC Bank",
                    "error_msg": "None",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status from the upi_txn table: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type from the upi_txn table: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code from the upi_txn table: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from the upi_txn table: {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "payer_name": payer_name_db,
                    "bank_name": bank_name_db,
                    "error_msg": error_msg_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
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
                    "rrn": str(rrn)
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetching auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"fetching username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal
                }

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
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            query = f"update upi_merchant_config set gst_in= '{gst_in}' where id='{upi_mc_id}'; "
            logger.debug(f"Query to update upi_merchant_config to revert the value of gst_in : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query to fetch result from upi_merchant_config : {result}")
            refresh_db()
            logger.debug(f"Using DB refresh method after reverting gst_in value")
        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_L3_5006_101_001():
    """
    Sub Feature Code: L3_5006_DMart_Ready_UPI_Success_Checkstatus_HDFC
    Sub Feature Description: Verification of Dmart ready upi success checkstatus via HDFC through sample app
    TC naming code description: L3_5006: L3_Ticket_Id, 101: UPI, 001: TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetching app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetching portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from org_employee table: {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'HDFC';"
        logger.debug(f"Query to fetch data from the upi_merchant_config table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id from upi_merchant_config table: {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"Value of tid from upi_merchant_config table: {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"Value of mid from upi_merchant_config table: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(500, 600)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Generating unique order ID  : {order_id}")

            app_driver = TestSuiteSetup.initialize_app_driver_for_sample_app(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.config_merchant_for_sample_app(org_code=org_code, username=app_username, password=app_password)
            logger.info(f"Configing in the Sample application using app_username, app_password : {app_username} , {app_password}")
            payment_page = PaymentPage(app_driver)
            payment_page.upi_txn_in_sample_app()
            payment_page.enter_order_id_and_amount(order_id, amount)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page.confirm_upi_txn_in_sample_app()
            # logger.info("Payment QR generated and displayed successfully")
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Pressed back button and clicked Yes on transaction cancel page")
            txn_amt_app = payment_page.fetch_payment_amount()
            logger.debug(f"fetching txn amount from success msg page : {txn_amt_app}")
            pmt_mode_app = payment_page.fetch_payment_mode()
            logger.debug(f"fetching payment mode from success msg page : {pmt_mode_app}")
            pmt_msg_app = payment_page.fetch_payment_status()
            logger.debug(f"fetching payment msg from success msg page : {pmt_msg_app}")

            payment_page.click_on_view_details_in_sample_app()
            customer_name_app = payment_page.fetch_customer_name_text()
            logger.debug(f"fetching customer name from view details page : {customer_name_app}")
            order_id_app = payment_page.fetch_order_id_text()
            logger.debug(f"fetching order_id from view details page : {order_id_app}")
            mid_app = payment_page.fetch_mid_text()
            logger.debug(f"fetching mid from view details page : {mid_app}")
            tid_app = payment_page.fetch_tid_text()
            logger.debug(f"fetching tid from view details page : {tid_app}")
            rrn_app = payment_page.fetch_rrn_text()
            logger.debug(f"fetching rrn from view details page : {rrn_app}")
            txn_id_app = payment_page.fetch_transaction_id_text()
            logger.debug(f"fetching txn_id from view details page : {txn_id_app}")
            date_and_time_app = payment_page.fetch_date_text()
            logger.debug(f"fetching date from view details page : {date_and_time_app}")
            payer_name_app = payment_page.fetch_payer_name_text()
            logger.debug(f"fetching payer name from view details page : {payer_name_app}")
            status_app = payment_page.fetch_status_text()
            logger.debug(f"fetching status from view details page : {payer_name_app}")
            payment_page.click_on_dismiss()
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id value from the txn table : {txn_id}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table is : {payer_name}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table is : {auth_code}")
            status_db = result["status"].iloc[0]
            logger.info(f"Fetching status from txn table: {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.info(f"Fetching payment mode from txn table: {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.info(f"Fetching amount from txn table: {amount_db}")
            state_db = result["state"].iloc[0]
            logger.info(f"Fetching state from txn table: {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.info(f"Fetching payment gateway from txn table: {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.info(f"Fetching acquirer code from txn table: {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.info(f"Fetching bank code from txn table: {bank_code_db}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.info(f"Fetching bank name from txn table: {bank_name_db}")
            payer_name_db = result["payer_name"].iloc[0]
            logger.info(f"Fetching payer name from txn table: {payer_name_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.info(f"Fetching settlement status from txn table: {settlement_status_db}")
            rrn = result["rr_number"].iloc[0]
            logger.info(f"Fetching rrn from txn table: {rrn}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.info(f"Fetching txn type from txn table: {txn_type_db}")
            tid_db = result['tid'].iloc[0]
            logger.info(f"Fetching tid from txn table: {tid_db}")
            mid_db = result['mid'].iloc[0]
            logger.info(f"Fetching mid from txn table: {mid_db}")
            error_msg_db = str(result['error_message'].iloc[0])
            logger.info(f"Fetching error message from txn table: {error_msg_db}")

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
        # -----------------------------------------Start of App Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": order_id,
                    "pmt_msg": "Payment Successful",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                actual_app_values = {
                    "pmt_mode": pmt_mode_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amt_app.split(" ")[1],
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": pmt_msg_app,
                    "date": date_and_time_app
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation-----------------------------------------

        # -----------------------------------------Start of API Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": rrn,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "order_id": order_id,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response")
                amount_api = response["amount"]
                logger.debug(f"Fetching amount from api response")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from api response")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from api response")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from api response")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from api response")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from api response")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from api response")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from api response")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from api response")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn type from api response")
                order_id_api = response["orderNumber"]
                logger.debug(f"Fetching order number from api response")
                date_api = response["createdTime"]
                logger.debug(f"Fetching date from api response")

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
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "order_id": order_id_api,
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
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "payer_name": payer_name,
                    "bank_name": "HDFC Bank",
                    "error_msg": "None",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status from the upi_txn table: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type from the upi_txn table: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code from the upi_txn table: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from the upi_txn table: {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "payer_name": payer_name_db,
                    "bank_name": bank_name_db,
                    "error_msg": error_msg_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "txn_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
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
                    "rrn": str(rrn)
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.info(f"fetching date time from portal {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.info(f"fetching txn_id from portal {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetching total amount from portal {total_amount_portal}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetching auth_code from portal {auth_code_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"fetching rr_number from portal {rr_number_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.info(f"fetching txn_type from portal {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.info(f"fetching status {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.info(f"fetching username from portal {username_portal}")

                actual_portal_values = {
                    "date_time": date_time_portal,
                    "pmt_state": status_portal,
                    "pmt_type": transaction_type_portal,
                    "txn_amt": total_amount_portal[1],
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number_portal
                }

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }
                logger.info(f"Performing ChargeSlip validation for the txn")

                receipt_validator.perform_charge_slip_validations(txn_id, {
                    "username": app_username,
                    "password": app_password}, expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------

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
def test_L3_5210_101_001():
    """
    Sub Feature Code: L3_5210_DMart_LockerAPP_UPI_Success_Txn_with_HDFC_SA_response
    Sub Feature Description: Verifying json response from SA to Sample App for upi success transaction
    TC naming code description: L3_5210: L3_Ticket_Id, 101: UPI, 001: TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        logger.debug(f"Fetched app_username : {app_username}")
        app_password = app_cred['Password']
        logger.debug(f"Fetched app_password : {app_password}")
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result_resp = DBProcessor.getValueFromDB(query)
        org_code = result_resp['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")
        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'UPI')

        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver_for_sample_app(testcase_id)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Order ID used : {order_id}")
            amount = random.randint(500, 550)
            logger.debug(f"Amount used : {amount}")
            login_page = LoginPage(app_driver)
            login_page.config_merchant_for_sample_app(org_code, app_username, app_password)
            payment_page = PaymentPage(app_driver)
            payment_page.upi_txn_in_sample_app()
            payment_page.enter_order_id_and_amount(order_id, amount)
            payment_page.confirm_upi_txn_in_sample_app()
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            payment_page.click_on_proceed_homepage()
            result_resp = payment_page.getting_result_sample().text
            result_resp = json.loads(result_resp)
            logger.debug(f"Result = {result_resp}")
            txn_details = result_resp['result']['txn']
            logger.debug(f"txn details : {txn_details}")
            txn_id_resp = txn_details['txnId']
            logger.debug(f"Transaction ID from response from sample App : {txn_id_resp}")
            amount_resp = int(txn_details['amount'])
            logger.debug(f"Amount from response from sample App : {amount_resp}")
            payment_mode_resp = txn_details['paymentMode']
            logger.debug(f"Payment mode from response from sample App : {payment_mode_resp}")
            mid_resp = txn_details['mid']
            logger.debug(f"MID from response from sample App : {mid_resp}")
            tid_resp = txn_details['tid']
            logger.debug(f"TID from response from sample App : {tid_resp}")
            status_resp = txn_details['status']
            logger.debug(f"Status from response from sample App : {status_resp}")
            txn_type_resp = txn_details['txnType']
            logger.debug(f"Transaction type from response from sample App : {txn_type_resp}")
            acquirer_code_resp = txn_details['acquirerCode']
            logger.debug(f"Acquirer code from response from sample App : {acquirer_code_resp}")
            issuer_code_resp = txn_details['issuerCode']
            logger.debug(f"Issuer code from response from sample App : {issuer_code_resp}")
            settlement_status_resp = txn_details['settlementStatus']
            logger.debug(f"Settlement status from response from sample App : {settlement_status_resp}")
            posting_date_resp = txn_details['postingDate']
            logger.debug(f"Posting date from response from sample App : {posting_date_resp}")
            rrn_resp = txn_details['rrNumber']
            logger.debug(f"RRN from response from sample App : {rrn_resp}")
            customer_name_resp = result_resp['result']['customer']['name']
            logger.debug(f"Customer name from response from sample App : {customer_name_resp}")
            order_id_resp = result_resp['result']['references']['reference1']
            logger.debug(f"Order ID from response from sample App : {order_id_resp}")
            date_and_time_resp = txn_details["txnDate"]
            logger.debug(f"Date and time from response from sample App : {date_and_time_resp}")

            query = f"select * from txn where id='{txn_id_resp}'"
            result_db = DBProcessor.getValueFromDB(query)
            payment_mode_db = result_db["payment_mode"].values[0]
            logger.debug(f"Payment Mode from txn table : {payment_mode_db}")
            status_db = result_db["status"].values[0]
            logger.debug(f"Status from txn table : {status_db}")
            amount_db = int(result_db["amount"].values[0])
            logger.debug(f"Amount from txn table : {amount_db}")
            settlement_status_db = result_db["settlement_status"].values[0]
            logger.debug(f"Settlement status from txn table : {settlement_status_db}")
            txn_id_db = result_db["id"].values[0]
            logger.debug(f"Transaction ID from txn table : {txn_id_db}")
            rr_number_db = result_db["rr_number"].values[0]
            logger.debug(f"RR Number from txn table : {rr_number_db}")
            customer_name_db = result_db["customer_name"].values[0]
            logger.debug(f"Customer Name from txn table : {customer_name_db}")
            txn_type_db = result_db["txn_type"].values[0]
            logger.debug(f"Transaction Type from txn table : {txn_type_db}")
            mid_db = result_db["mid"].values[0]
            logger.debug(f"MID from txn table : {mid_db}")
            tid_db = result_db["tid"].values[0]
            logger.debug(f"TID from txn table : {tid_db}")
            acquirer_code_db = result_db["acquirer_code"].values[0]
            logger.debug(f"Acquirer Code from txn table : {acquirer_code_db}")
            issuer_code_db = result_db["issuer_code"].values[0]
            logger.debug(f"Issuer Code from txn table : {issuer_code_db}")
            order_id_db = result_db["external_ref"].values[0]
            logger.debug(f"Order ID from txn table : {order_id_db}")
            created_time_db = result_db["created_time"].values[0]
            logger.debug(f"Created Time from txn table : {created_time_db}")
            posting_date_db = result_db["posting_date"].values[0]
            logger.debug(f"Posting Date from txn table : {posting_date_db}")

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
                date_and_time = date_time_converter.db_datetime(created_time_db)
                posting_date = date_time_converter.db_datetime(posting_date_db)
                expected_app_values = {
                    "order_id": order_id_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": status_db,
                    "txn_amt": "{:.2f}".format(amount_db),
                    "settle_status": settlement_status_db,
                    "transaction_id": txn_id_db,
                    "rr_number": rr_number_db,
                    "customer_name": customer_name_db,
                    "transaction_type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code_db,
                    "date": date_and_time,
                    "posting_date": posting_date
                }
                logger.debug(f"Expected values for App Validation : {expected_app_values}")

                actual_app_values = {
                    "order_id": order_id_resp,
                    "pmt_mode": payment_mode_resp,
                    "pmt_status": status_resp,
                    "txn_amt": "{:.2f}".format(amount_resp),
                    "settle_status": settlement_status_resp,
                    "transaction_id": txn_id_resp,
                    "rr_number": rrn_resp,
                    "customer_name": customer_name_resp,
                    "transaction_type": txn_type_resp,
                    "mid": mid_resp,
                    "tid": tid_resp,
                    "acquirer_code": acquirer_code_resp,
                    "issuer_code": issuer_code_resp,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_resp),
                    "posting_date": date_time_converter.from_api_to_datetime_format(posting_date_resp)
                }
                logger.debug(f"Actual values for App Validation : {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.db_datetime(created_time_db)
                expected_api_values = {
                    "pmt_mode": payment_mode_db,
                    "pmt_status": status_db,
                    "txn_amt": "{:.2f}".format(amount_db),
                    "settle_status": settlement_status_db,
                    "txn_id": txn_id_db,
                    "rrn": str(rr_number_db),
                    "customer_name": customer_name_db,
                    "txn-type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code_db,
                    "order_id": order_id_db,
                    "date": date_and_time
                }
                logger.debug(f"Expected API Values for API validations : {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_resp][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Status from TXN List API : {status_api}")
                amount_api = response["amount"]
                logger.debug(f"Amount from TXN List API : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Payment Mode from TXN List API : {payment_mode_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"RRN from TXN List API : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Settlement Status from TXN List API : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Issuer Code from TXN List API : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Acquirer Code from TXN List API : {acquirer_code_api}")
                mid_api = response["mid"]
                logger.debug(f"MID from TXN List API : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"TID from TXN List API : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Transaction Type from TXN List API : {txn_type_api}")
                txn_id_api = response["txnId"]
                logger.debug(f"Transaction ID from TXN List API : {txn_id_api}")
                customer_name_api = response["customerName"]
                logger.debug(f"Customer Name from TXN List API : {customer_name_api}")
                order_id_api = response["externalRefNumber"]
                logger.debug(f"Order ID from TXN List API : {order_id_api}")
                date_and_time_api = response["createdTime"]
                logger.debug(f"Date and Time from TXN List API : {date_and_time_api}")

                actual_api_values = {
                    "pmt_mode": payment_mode_api,
                    "pmt_status": status_api,
                    "txn_amt": "{:.2f}".format(amount_api),
                    "settle_status": settlement_status_api,
                    "txn_id": txn_id_api,
                    "rrn": str(rrn_api),
                    "customer_name": customer_name_api,
                    "txn-type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api)
                }
                logger.debug(f"Actual API Values for API validations : {actual_api_values}")
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
                    "pmt_mode": payment_mode_resp,
                    "pmt_status": status_resp,
                    "txn_amt": "{:.2f}".format(amount_resp),
                    "settle_status": settlement_status_resp,
                    "txn_id": txn_id_resp,
                    "rrn": str(rrn_resp),
                    "customer_name": customer_name_resp,
                    "txn-type": txn_type_resp,
                    "mid": mid_resp,
                    "tid": tid_resp,
                    "acquirer_code": acquirer_code_resp,
                    "issuer_code": issuer_code_resp,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_resp),
                }
                logger.debug(f"Expected Values for DB Validations : {expected_db_values}")

                actual_db_values = {
                    "pmt_mode": payment_mode_db,
                    "pmt_status": status_db,
                    "txn_amt": "{:.2f}".format(amount_db),
                    "settle_status": settlement_status_db,
                    "txn_id": txn_id_db,
                    "rrn": str(rr_number_db),
                    "customer_name": customer_name_db,
                    "txn-type": txn_type_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code_db,
                    "date": date_time_converter.db_datetime(created_time_db)
                }
                logger.debug(f"Actual Values for DB Validations : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_db = date_time_converter.to_portal_format(created_time_db)
                expected_portal_values = {
                    "pmt_state": status_db,
                    "pmt_mode": "UPI",
                    "txn_amt": f"{str(amount_db)}.00",
                    "txn_id": txn_id_db,
                    "rrn": rr_number_db,
                    "username": app_username,
                    "date": date_and_time_db
                }

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_portal = transaction_details[0]['Date & Time']
                logger.debug(f"Fetched Date and Time from Portal : {date_time_portal}")
                transaction_id_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"Transaction ID from Portal : {transaction_id_portal}")
                total_amount_portal = transaction_details[0]['Total Amount'].split()[1]
                logger.debug(f"Total Amount from Portal : {total_amount_portal}")
                transaction_type_portal = transaction_details[0]['Type']
                logger.debug(f"Transaction Type from Portal : {transaction_type_portal}")
                status_portal = transaction_details[0]['Status']
                logger.debug(f"Status from Portal : {status_portal}")
                username_portal = transaction_details[0]['Username']
                logger.debug(f"Username from Portal : {username_portal}")
                rr_number_portal = transaction_details[0]['RR Number']
                logger.debug(f"RR Number from Portal : {rr_number_portal}")

                actual_portal_values = {
                    "pmt_state": status_portal,
                    "pmt_mode": transaction_type_portal,
                    "txn_amt": f"{str(total_amount_portal)}",
                    "username": username_portal,
                    "txn_id": transaction_id_portal,
                    "rrn": rr_number_portal,
                    "date": date_time_portal
                }
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_db)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id_db),
                    'RRN': str(rr_number_db),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time
                }
                receipt_validator.perform_charge_slip_validations(txn_id_db,
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
