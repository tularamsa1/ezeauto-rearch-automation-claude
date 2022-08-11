import sys
from time import sleep

import pytest
import random
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import Validator,ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner,  date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_076():
    """
    :Description: Verification of a BQRV4 Checkstatus Success via AXIS_ATOS
    :Sub Feature code: UI_Common_BQRV4_Checkstatus_Success_AXIS_ATOS_076
    :TC naming code description: 100->Payment Method, 102->BQR, 076-> TC76
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'AXIS', portal_username, portal_password, 'BQRV4')

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

        query = "select * from upi_merchant_config where org_code='" + org_code + "' " \
                                                             "and status = 'ACTIVE' and bank_code='AXIS'"
        logger.debug(f"Query to fetch upi_mc_id and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching mid, tid from database for current merchant:{mid}, {tid}")
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching vpa, upi_mc_id from database for current merchant:{vpa}, {upi_mc_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_home_page_load()
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(301, 400)
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
            app_driver.reset()
            logger.info("Restarting MPOSX app to perfrom checkstatus of the transaction")
            query = "select * from bharatqr_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            api_details = DBProcessor.get_api_details('stopPayment',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "orgCode":org_code ,"txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stopPayment api of transaction is : {response}")
            api_details = DBProcessor.get_api_details('paymentStatus',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for checkstatus of transaction is : {response}")
            app_driver.reset()
            logger.info("Restarting MPOSX app after perfroming checkstatus of the transaction")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            posting_date = result['posting_date'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching auth_code, posting_date, customer name and payer name from database for "
                         f"current merchant:{auth_code}, {posting_date}, {customer_name}, {payer_name}")
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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {"pmt_mode": "UPI", "pmt_status": "AUTHORIZED","txn_amt": str(amount),
                                       "settle_status": "SETTLED","txn_id": txn_id, "rrn": str(rrn),
                                       "customer_name": customer_name,"payer_name": payer_name,
                                       "order_id": order_id,"msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code, "date": date_and_time}
                logger.debug(f"expectedAppValues: {expected_app_values}")
                login_page = LoginPage(app_driver)
                logger.debug(f"Loging in again with user name : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Homepage of MPOSX app loaded successfully")
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
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
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     "customer_name": app_customer_name,"settle_status": app_settlement_status,
                                     "payer_name": app_payer_name,"order_id": app_order_id,"auth_code": app_auth_code,
                                     "msg": app_payment_msg, "date": app_date_and_time}
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
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {"pmt_status": "AUTHORIZED","txn_amt": amount,"pmt_mode": "UPI",
                                       "pmt_state": "SETTLED", "rrn": str(rrn),"settle_status": "SETTLED",
                                       "acquirer_code": "AXIS", "issuer_code": "AXIS","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code, "auth_code": auth_code,
                                       "date": date}
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
                                                                        "txnId": txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
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
                date_api = response["postingDate"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "auth_code": auth_code_api, "date": date_time_converter.from_api_to_datetime_format(date_api)}
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "UPI","pmt_status": "AUTHORIZED",
                                      "pmt_state": "SETTLED","acquirer_code" : "AXIS", "bank_name" : "Axis Bank",
                                      "payer_name": payer_name, "mid" :mid, "tid" : tid, "pmt_gateway": "ATOS",
                                      "rrn" : str(rrn), "settle_status": "SETTLED","upi_pmt_status": "AUTHORIZED",
                                      "upi_txn_type": "PAY_BQR", "upi_mc_id": upi_mc_id, "upi_bank_code": "AXIS"}
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = int(result["amount"].iloc[0])
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

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "payer_name": payer_name_db, "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn" : rr_number_db,
                                    "settle_status": settlement_status_db,"upi_pmt_status": upi_status_db,
                                    "upi_txn_type": upi_txn_type_db, "upi_mc_id": upi_mc_id_db, "upi_bank_code": upi_bank_code_db}
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
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                #
                # Write the test case Portal validation code block here. Set this to pass if not required.
                #
                actual_portal_values = {}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",  'date': txn_date,'time': txn_time,
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_077():
    """
    :Description: Verification of a BQRV4 Expired Check status transaction when auto refund disabled via AXIS_ATOS
    :Sub Feature code: UI_Common_BQRV4_CheckStatus_Expired_AXIS_ATOS_077
    :TC naming code description: 100->Payment Method, 102->BQR, 077-> TC77
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'AXIS', portal_username, portal_password, 'BQRV4')

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

        query = "select mid, tid from bharatqr_merchant_config where org_code='" + org_code + "' and bank_code='AXIS'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching mid, tid from database for current merchant:{mid}, {tid}")
        query = "select * from upi_merchant_config where bank_code = 'AXIS' AND status = 'ACTIVE' AND org_code = " \
                "'" + str(org_code) + "'; "
        logger.debug(f"Query to fetch upi_mc_id and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching vpa, upi_mc_id from database for current merchant:{vpa}, {upi_mc_id}")

        api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_home_page_load()
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(301, 400)
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
            app_driver.reset()
            logger.info("Restarting MPOSX app to perfrom checkstatus of the transaction")
            query = "select * from bharatqr_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            logger.debug("Waiting for 1 min to QR get expired")
            sleep(60)
            api_details = DBProcessor.get_api_details('stopPayment',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "orgCode":org_code ,"txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stopPayment api of transaction is : {response}")
            api_details = DBProcessor.get_api_details('paymentStatus',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for checkstatus of transaction is : {response}")
            app_driver.reset()
            logger.info("Restarting MPOSX app after perfroming checkstatus of the transaction")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from database for current merchant:{posting_date}")

            query = "select * from txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result["id"].iloc[0]
            customer_name_new = result['customer_name'].values[0]
            payer_name_new = result['payer_name'].values[0]
            auth_code_new = result['auth_code'].values[0]
            posting_date_new = result['posting_date'].values[0]

            logger.debug(f"Fetching new txn_id, auth_code, posting_date, customer name and payer name from database for "
                         f"current merchant:{txn_id_new},{auth_code_new}, {posting_date_new}, {customer_name_new}, {payer_name_new}")

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                date_and_time_new = date_time_converter.to_app_format(posting_date_new)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED","txn_amt": str(amount),
                                       "settle_status": "FAILED","txn_id": txn_id,
                                       "order_id": order_id,"msg": "PAYMENT FAILED", "date": date_and_time,
                                       "pmt_mode_new": "UPI", "pmt_status_new": "AUTHORIZED", "txn_amt_new": str(amount),
                                       "settle_status_new": "SETTLED", "txn_id_new": txn_id_new, "rrn_new": str(rrn),
                                       "customer_name_new": customer_name_new, "payer_name_new": payer_name_new,
                                       "order_id_new": order_id, "msg_new": "PAYMENT SUCCESSFUL",
                                       "auth_code_new": auth_code_new, "date_new": date_and_time_new
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
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
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)
                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                app_auth_code_new = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new}, {app_auth_code_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_customer_name_new = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payer_name_new = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_new}, {app_payer_name_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,"order_id": app_order_id,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_new": payment_mode_new, "pmt_status_new": payment_status_new.split(':')[1],
                                     "txn_amt_new": app_amount_new.split(' ')[1], "txn_id_new": app_txn_id_new, "rrn_new": str(app_rrn_new),
                                     "customer_name_new": app_customer_name_new, "settle_status_new": app_settlement_status_new,
                                     "payer_name_new": app_payer_name_new, "order_id_new": app_order_id_new, "auth_code_new": app_auth_code_new,
                                     "msg_new": app_payment_msg_new, "date_new": app_date_and_time_new
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
                date = date_time_converter.db_datetime(posting_date)
                date_new = date_time_converter.db_datetime(posting_date_new)
                expected_api_values = {"pmt_status": "EXPIRED","txn_amt": amount,"pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED","settle_status": "FAILED",
                                       "acquirer_code": "AXIS", "issuer_code": "AXIS","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date,
                                       "pmt_status_new": "AUTHORIZED", "txn_amt_new": amount, "pmt_mode_new": "UPI",
                                       "pmt_state_new": "SETTLED", "rrn_new": str(rrn), "settle_status_new": "SETTLED",
                                       "acquirer_code_new": "AXIS", "issuer_code_new": "AXIS", "txn_type_new": "CHARGE",
                                       "mid_new": mid, "tid_new": tid, "org_code_new": org_code, "auth_code_new": auth_code_new,
                                       "date_new": date_new
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
                                                                        "txnId": txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
                                                                        "txnId": txn_id_new})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api_new = response["status"]
                amount_api_new = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                orgCode_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                auth_code_api_new = response["authCode"]
                date_api_new = response["postingDate"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_new": status_api_new, "txn_amt_new": amount_api_new, "pmt_mode_new": payment_mode_api_new,
                                     "pmt_state_new": state_api_new, "rrn_new": str(rrn_api_new),
                                     "settle_status_new": settlement_status_api_new,
                                     "acquirer_code_new": acquirer_code_api_new, "issuer_code_new": issuer_code_api_new, "mid_new": mid_api_new,
                                     "txn_type_new": txn_type_api_new, "tid_new": tid_api_new, "org_code_new": orgCode_api_new,
                                     "auth_code_new": auth_code_api_new,
                                     "date_new": date_time_converter.from_api_to_datetime_format(date_api_new)
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
                expected_db_values = {"txn_amt": amount, "pmt_mode": "BHARATQR", "pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED", "acquirer_code": "AXIS",
                                      "mid": mid, "tid": tid, "pmt_gateway": "ATOS",
                                      "settle_status": "FAILED",
                                      "txn_amt_new": amount, "pmt_mode_new": "UPI", "pmt_status_new": "AUTHORIZED",
                                      "pmt_state_new": "SETTLED", "acquirer_code_new": "AXIS",
                                      "bank_name_new": "Axis Bank",
                                      "payer_name_new": payer_name_new, "mid_new": mid, "tid_new": tid,
                                      "pmt_gateway_new": "ATOS",
                                      "rrn_new": str(rrn), "settle_status_new": "SETTLED",
                                      "upi_pmt_status_new": "AUTHORIZED",
                                      "upi_txn_type_new": "PAY_BQR", "upi_mc_id_new": upi_mc_id,
                                      "upi_bank_code_new": "AXIS"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = int(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new = int(result["amount"].iloc[0])
                payment_mode_db_new = result["payment_mode"].iloc[0]
                payment_status_db_new = result["status"].iloc[0]
                payment_state_db_new = result["state"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_name_db_new = result["bank_name"].iloc[0]
                payer_name_db_new = result["payer_name"].iloc[0]
                mid_db_new = result["mid"].iloc[0]
                tid_db_new = result["tid"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                rr_number_db_new = result["rr_number"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]
                upi_mc_id_db_new = result["upi_mc_id"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]

                actual_db_values = {"txn_amt": amount_db, "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "txn_amt_new": amount_db_new, "pmt_mode_new": payment_mode_db_new,
                                    "pmt_status_new": payment_status_db_new, "pmt_state_new": payment_state_db_new,
                                    "acquirer_code_new": acquirer_code_db_new, "bank_name_new": bank_name_db_new,
                                    "payer_name_new": payer_name_db_new, "mid_new": mid_db_new, "tid_new": tid_db_new,
                                    "pmt_gateway_new": payment_gateway_db_new, "rrn_new": rr_number_db_new,
                                    "settle_status_new": settlement_status_db_new,
                                    "upi_pmt_status_new": upi_status_db_new,
                                    "upi_txn_type_new": upi_txn_type_db_new, "upi_mc_id_new": upi_mc_id_db_new,
                                    "upi_bank_code_new": upi_bank_code_db_new
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
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                #
                # Write the test case Portal validation code block here. Set this to pass if not required.
                #
                actual_portal_values = {}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",  'date': txn_date,'time': txn_time,
                                   'AUTH CODE': auth_code_new}
                receipt_validator.perform_charge_slip_validations(txn_id_new,
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