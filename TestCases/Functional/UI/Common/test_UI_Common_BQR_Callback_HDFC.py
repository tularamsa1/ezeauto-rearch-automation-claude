import shutil
import sys
from time import sleep
import pytest
import random
from datetime import datetime
from termcolor import colored
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_001():
    """
    :Description: Verification of a BQR Callback Success transaction via HDFC
    :Sub Feature code: UI_Common_PM_BQR_Callback_Success_HDFC_01
    :TC naming code description: 100->Payment Method, 102->BQR, 001-> TC01
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')

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

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]

        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")
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
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(401, 1000)
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
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' " \
                                                                    "order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN from data base : Txn_id : {txn_id},"
                f" Auth code : {auth_code}, RRN : {rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_AMOUNT": str(amount),
                                                                    "TXN_ID": txn_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            rrn = result['rr_number'].iloc[0]
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching auth_code, rrn, posting_date, customer name and payer name from database for "
                         f"current merchant:{auth_code}, {rrn}, {posting_date}")

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
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "AUTHORIZED","txn_amt": str(amount),
                                       "settle_status": "SETTLED","txn_id": txn_id, "rrn": str(rrn),
                                       "order_id": order_id,"msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code, "date": date_and_time}
                logger.debug(f"expectedAppValues: {expected_app_values}")
                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
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
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,"auth_code": app_auth_code,
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
                expected_api_values = {"pmt_status": "AUTHORIZED","txn_amt": amount,"pmt_mode": "BHARATQR",
                                       "pmt_state": "SETTLED", "rrn": str(rrn),"settle_status": "SETTLED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC","txn_type": "CHARGE",
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "BHARATQR","pmt_status": "AUTHORIZED",
                                      "pmt_state": "SETTLED","acquirer_code" : "HDFC", "bank_name" : "HDFC Bank",
                                      "mid" :mid, "tid" : tid, "pmt_gateway": "HDFC",
                                      "rrn" : str(rrn), "settle_status": "SETTLED",
                                      "bqr_pmt_status": "Transaction Success", "bqr_pmt_state": "SETTLED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": bqr_m_pan,
                                      "bqr_rrn": str(rrn), "bqr_org_code": org_code
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
                bank_name_db = result["bank_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = int(
                    result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn" : rr_number_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_rrn": bqr_rrn_db, "bqr_org_code": bqr_org_code_db
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
                expected_values = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
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
def test_common_100_102_002():
    """
    :Description: Verification of a BQR Callback Failed transaction via HDFC
    :Sub Feature code: UI_Common_PM_BQR_Callback_Failed_HDFC _02
    :TC naming code description: 100->Payment Method
                                102->BQR
                                002-> TC02
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        username = app_cred['Username']
        password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')
        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            loginPage = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.wait_for_navigation_to_load()
            homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(101, 200)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            query = "select * from bharatqr_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code and RRN from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}")
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id,"TXN_ID": txn_id,
                                                                    "TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback of transaction is : {response}")
            print("API Res:", response)
            #
            logger.info(f"Execution is completed for the test case : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()

            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1

            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                logger.info(f"Starting APP Validation for the test case: {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:FAILED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}
                app_payment_status = paymentPage.fetch_payment_status()
                logger.info(f"Fetching status of payment from payment screen: {app_payment_status} ")
                paymentPage.click_on_proceed_homepage()
                paymentPage.click_on_back_btn()
                homePage.click_on_back_btn_enter_amt_page()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info(f"App Validation Completed successfully for test case : {testcase_id}")
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info(f"Starting API Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"FAILED","Amount": amount, "Payment Mode": "BHARATQR","Acquirer Code":"HDFC"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                accuirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")

                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Acquirer Code":accuirer_code_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info(f"Starting DB Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment mode": "BHARATQR","Acquirer Code":"HDFC",
                                    "Payment amount": "{:.2f}".format(amount), "State": "FAILED", "State Bharatqr": "FAILED",
                                    "Amount Bharatqr": amount, "Status Bharatqr": "Transaction failed"}
                #
                query = "select status,amount,payment_mode,acquirer_code,state from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, acquirer_code,payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                accuirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                logger.debug(f"Fetching Transaction state from DB : {state_db} ")

                query = "select state,txn_amount,status_desc from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch state, txn amount and status_desc from bahratqr_txn DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from bharatqr txn table of DB : {result} ")
                state_bharatqr_db = result["state"].iloc[0]
                amount_bharatqr_db = result["txn_amount"].iloc[0]
                status_bharatqr_db = result["status_desc"].iloc[0]
                logger.debug(f"Fetching Transaction state from bharatqr txn table of DB : {state_bharatqr_db} ")
                logger.debug(f"Fetching Transaction amount from bharatqr txn table of DB : {amount_bharatqr_db} ")
                logger.debug(
                    f"Fetching Transaction status description from bharatqr txn table of DB : {status_bharatqr_db} ")
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,"Acquirer Code":accuirer_code_db,
                                  "Payment amount": amount_db, "State": state_db, "State Bharatqr": state_bharatqr_db,
                                  "Amount Bharatqr": amount_bharatqr_db, "Status Bharatqr": status_bharatqr_db}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")

        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Failed", "Payment mode":"BHARATQR" , "Payment amount":str(amount)}
                #
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                loginPagePortal = PortalLoginPage(ui_driver)
                logger.info(f"Logging in Portal using username : {portal_username}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(ui_driver)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
            GlobalVariables.time_calc.validation.end()
            print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))
            logger.info(f"Completed Validation for the test case : {testcase_id}")

    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_003():
    """
    :Description: Verification of a BQR Callback After QR Expiry transaction via HDFC
    :Sub Feature code: UI_Common_PM_BQR_Callback_AfterExpiry_HDFC _03
    :TC naming code description: 100->Payment Method
                                102->BQR
                                003-> TC03
    """


    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        username = app_cred['Username']
        password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')
        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        logger.info("Finished performing preconditions before starting test case execution")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            loginPage = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {username}")
            loginPage.perform_login(username, password)
            homePage = HomePage(app_driver)
            homePage.wait_for_navigation_to_load()
            homePage.check_home_page_logo()
            homePage.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.choice([i for i in range(51, 100) if i != 55])
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            paymentPage.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code and RRN from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}")
            logger.info(f"Waiting for QR code to get Expired.. Please wait")
            sleep(60)
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id,
                                                                    "TXN_ID": txn_id,"TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            logger.info(f"Execution is completed for the test case : {testcase_id}")

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()

            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1

            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Starting App Validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:EXPIRED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}
                #
                logger.info(f"Logining in to app again with username : {username}")
                loginPage.perform_login(username, password)
                homePage = HomePage(app_driver)
                homePage.check_home_page_logo()
                logger.info(f"App homepage loaded successfully")
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt)}
                logger.info("App Validation Completed successfully for test case")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info("Starting API Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Payment Status":"EXPIRED","Amount": amount, "Payment Mode": "BHARATQR","Acquirer Code":"HDFC"}

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                accuirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Acquirer Code":accuirer_code_api}

                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
                logger.info("API Validation Completed successfully for test case")
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info("Starting DB Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "EXPIRED", "Payment mode": "BHARATQR","Acquirer Code":"HDFC",
                                    "Payment amount": "{:.2f}".format(amount), "State": "EXPIRED", "State Bharatqr": "EXPIRED",
                                    "Amount Bharatqr": amount, "Status Bharatqr": "Transaction Pending"}
                #
                query = "select status,amount,payment_mode,acquirer_code,state from txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, acquirer_code,payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                accuirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                logger.debug(f"Fetching Transaction state from DB : {state_db} ")

                query = "select state,txn_amount,status_desc from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"DB query to fetch state, txn amount and status_desc from bahratqr_txn DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from bharatqr txn table of DB : {result} ")
                state_bharatqr_db = result["state"].iloc[0]
                amount_bharatqr_db = result["txn_amount"].iloc[0]
                status_bharatqr_db = result["status_desc"].iloc[0]
                logger.debug(f"Fetching Transaction state from bharatqr txn table of DB : {state_bharatqr_db} ")
                logger.debug(f"Fetching Transaction amount from bharatqr txn table of DB : {amount_bharatqr_db} ")
                logger.debug(
                    f"Fetching Transaction status description from bharatqr txn table of DB : {status_bharatqr_db} ")
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,"Acquirer Code":accuirer_code_db,
                                  "Payment amount": amount_db, "State": state_db, "State Bharatqr": state_bharatqr_db,
                                  "Amount Bharatqr": amount_bharatqr_db, "Status Bharatqr": status_bharatqr_db}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                logger.info("DB Validation Completed successfully for test case")

            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Expired", "Payment mode":"BHARATQR" , "Payment amount":str(amount)}
                #
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                loginPagePortal = PortalLoginPage(ui_driver)
                logger.info(f"Logging in Portal using username : {portal_username}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(ui_driver)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
            GlobalVariables.time_calc.validation.end()
            print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))
            logger.info(f"Completed Validation for the test case : {testcase_id}")

    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)

#
# @pytest.mark.usefixtures("log_on_success", "method_setup")
# @pytest.mark.apiVal
# @pytest.mark.dbVal
# @pytest.mark.portalVal
# @pytest.mark.appVal
# def test_common_100_102_012():
#     """
#     :Description: Verification of  a BQR expired Callback when auto refund disabled viaHDFC
#     :Sub Feature code: UI_Common_PM_BQR_Expired_Callback_AutoRefund_disabled_HDFC_12
#     :TC naming code description: 100->Payment Method
#                                 102->BQR
#                                 012-> TC12
#     """
#
#     try:
#         testcase_id = sys._getframe().f_code.co_name
#         GlobalVariables.time_calc.setup.resume()
#         print(
#             colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
#         # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
#         logger.info("Performing preconditions before starting test case execution")
#         app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
#         logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
#         username = app_cred['Username']
#         password = app_cred['Password']
#         portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
#         logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
#         portal_username = portal_cred['Username']
#         portal_password = portal_cred['Password']
#
#         query = "select org_code from org_employee where username='" + str(username) + "';"
#         logger.debug(f"Query to fetch org_code from the DB : {query}")
#         result = DBProcessor.getValueFromDB(query)
#         org_code = result['org_code'].values[0]
#         logger.debug(f"Query result, org_code : {org_code}")
#
#         testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')
#         api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
#                                                                                "password": portal_password,
#                                                                                "settingForOrgCode": org_code})
#         api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
#         logger.debug(f"API details  : {api_details} ")
#         response = APIProcessor.send_request(api_details)
#         logger.debug(f"Response received for setting preconditions is : {response}")
#
#         api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
#         api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
#         logger.debug(f"API details  : {api_details} ")
#         response = APIProcessor.send_request(api_details)
#         logger.debug(f"Response received for setting preconditions is : {response}")
#         api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
#                                                                               "password": portal_password,
#                                                                               "settingForOrgCode": org_code})
#         api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
#         logger.debug(f"API details  : {api_details}")
#         response = APIProcessor.send_request(api_details)
#         logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
#         query = "update bharatqr_provider_config set auto_check_status_enabled = 0 where id = '2'"
#         result = DBProcessor.setValueToDB(query)
#         logger.debug(f"Result of updating autocheck status in db is : {result}")
#
#         GlobalVariables.setupCompletedSuccessfully = True
#         logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
#
#         # Set the below variables depending on the log capturing need of the test case.
#         Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
#         msg = ""
#         GlobalVariables.time_calc.setup.end()
#         print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
#
#         # -----------------------------------------Start of Test Execution-------------------------------------
#         try:
#             logger.info(f"Starting execution for the test case : {testcase_id}")
#             GlobalVariables.time_calc.execution.start()
#             print(
#                 colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
#                         'cyan'))
#
#             app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
#             loginPage = LoginPage(app_driver)
#             logger.info(f"Logging in the MPOSX application using username : {username}")
#             loginPage.perform_login(username, password)
#             homePage = HomePage(app_driver)
#             homePage.wait_for_navigation_to_load()
#             homePage.check_home_page_logo()
#             homePage.wait_for_home_page_load()
#             logger.info(f"App homepage loaded successfully")
#             amount = random.randint(501, 1000)
#             order_id = datetime.now().strftime('%m%d%H%M%S')
#             homePage.enter_amount_and_order_number(amount, order_id)
#             logger.debug(f"Entered amount is : {amount}")
#             logger.debug(f"Entered order_id is : {order_id}")
#             paymentPage = PaymentPage(app_driver)
#             paymentPage.is_payment_page_displayed(amount, order_id)
#             paymentPage.click_on_Bqr_paymentMode()
#             logger.info("Selected payment mode is BQR")
#             paymentPage.validate_upi_bqr_payment_screen()
#             logger.info("Payment QR generated and displayed successfully")
#             app_driver.reset()
#             query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
#             logger.debug(f"Query to fetch expired transaction id from database is: {query}")
#             result = DBProcessor.getValueFromDB(query)
#             txn_id_expired = result["id"].iloc[0]
#             auth_code = "AE" + txn_id_expired.split('E')[1]
#             rrn = "RE" + txn_id_expired.split('E')[1]
#             logger.debug(
#                 f"Fetching Txn_id,Auth code and RRN from data base : Txn_id expired : {txn_id_expired}, Auth code : {auth_code}, RRN : {rrn}")
#             logger.info(f"Waiting for QR code to get Expired.. Please wait")
#             sleep(60)
#             api_details = DBProcessor.get_api_details('callbackHDFC',
#                                                       request_body={"PRIMARY_ID": txn_id_expired,
#                                                                     "TXN_ID": txn_id_expired,
#                                                                     "TXN_AMOUNT": str(amount),
#                                                                     "AUTH_CODE": auth_code, "RRN": rrn})
#             response = APIProcessor.send_request(api_details)
#             logger.debug(f"Fetching API Response for call back : {response}")
#             logger.info(f"Logining in to app again with username : {username}")
#             loginPage.perform_login(username, password)
#             homePage = HomePage(app_driver)
#             homePage.check_home_page_logo()
#             logger.info(f"App homepage loaded successfully")
#             query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
#             logger.debug(f"Query to fetch transaction id from database is: {query}")
#             result = DBProcessor.getValueFromDB(query)
#             txn_id = result["id"].iloc[0]
#             query = "update bharatqr_provider_config set auto_check_status_enabled = 1 where id = '2'"
#             result = DBProcessor.setValueToDB(query)
#             logger.debug(f"Result of updating autocheck status in db is : {result}")
#             api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
#                                                                                   "password": portal_password})
#             response = APIProcessor.send_request(api_details)
#             logger.debug(f"Response recieved is : {response}")
#             logger.info(f"Execution is completed for the test case : {testcase_id}")
#             #
#             # ------------------------------------------------------------------------------------------------
#             GlobalVariables.EXCEL_TC_Execution = "Pass"
#             GlobalVariables.time_calc.execution.pause()
#             print(colored(
#                 "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
#                                                                                   "="), 'cyan'))
#             logger.info(f"Execution is completed for the test case : {testcase_id}")
#         except Exception as e:
#             if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
#                 GlobalVariables.time_calc.execution.pause()
#                 print(colored(
#                     "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
#                         shutil.get_terminal_size().columns, "="), 'cyan'))
#             GlobalVariables.time_calc.execution.resume()
#             print(colored("Execution Timer resumed in execpt block of testcase function".center(
#                 shutil.get_terminal_size().columns, "="), 'cyan'))
#
#             ReportProcessor.capture_ss_when_app_val_exe_failed()
#
#             GlobalVariables.EXCEL_TC_Execution = "Fail"
#             GlobalVariables.Incomplete_ExecutionCount += 1
#
#             GlobalVariables.time_calc.execution.pause()
#             print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
#                 shutil.get_terminal_size().columns, "="), 'cyan'))
#
#             logger.exception(f"Execution is completed for the test case : {testcase_id}")
#             pytest.fail("Test case execution failed due to the exception -" + str(e))
#         # -----------------------------------------End of Test Execution--------------------------------------
#
#         # -----------------------------------------Start of Validation----------------------------------------
#         logger.info(f"Starting Validation for the test case : {testcase_id}")
#         GlobalVariables.time_calc.validation.start()
#         print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
#                       'cyan'))
#
#         # -----------------------------------------Start of App Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "app_validation")) == "True":
#             try:
#                 logger.info(f"Starting App Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#                 expectedAppValues = {"Payment Status": "STATUS:AUTHORIZED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount), "Payment Status Original": "STATUS:EXPIRED", "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id_expired, "Payment Amt Original": str(amount)}
#                 homePage.wait_for_navigation_to_load()
#                 homePage.check_home_page_logo()
#                 homePage.click_on_history()
#                 transactionsHistoryPage = TransHistoryPage(app_driver)
#                 transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
#                 app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
#                 logger.debug(
#                     f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
#                 app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
#                 logger.debug(
#                     f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
#                 app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
#                 logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
#                 app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
#                 logger.debug(
#                     f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
#                 transactionsHistoryPage.click_back_Btn_transaction_details()
#                 transactionsHistoryPage.click_on_second_transaction_by_order_id(order_id)
#                 app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
#                 logger.debug(
#                     f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
#                 app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
#                 logger.debug(
#                     f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn Mode = {app_payment_mode_original}")
#                 app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
#                 logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
#                 app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
#                 logger.debug(
#                     f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
#
#                 actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt), "Payment Status Original": app_payment_status_original, "Payment mode Original": app_payment_mode_original, "Payment Txn ID Original": app_txn_id_original, "Payment Amt Original": str(app_payment_amt_original)}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
#                 logger.info("App Validation Completed successfully for test case")
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_app_val_exe_failed()
#                 print("App Validation failed due to exception - " + str(e))
#                 logger.exception(f"App Validation failed due to exception - {e}")
#                 msg = msg + "App Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_app_val_result = "Fail"
#             logger.info(f"Completed APP validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of App Validation---------------------------------------
#
#         # -----------------------------------------Start of API Validation------------------------------------
#         if (ConfigReader.read_config("Validations", "api_validation")) == "True":
#             try:
#                 logger.info(f"Starting API Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#
#                 expectedAPIValues = {"Payment Status":"AUTHORIZED","Amount": amount, "Payment Mode": "BHARATQR", "Payment Status Original":"EXPIRED","Acquirer Code":"HDFC","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
#                 api_details = DBProcessor.get_api_details('txnDetails',
#                                                           request_body={"username": username, "password": password,
#                                                                         "txnId": txn_id})
#                 print("API DETAILS:", api_details)
#                 response = APIProcessor.send_request(api_details)
#                 logger.debug(f"Response received for transaction details api is : {response}")
#                 print(response)
#                 status_api = response["status"]
#                 amount_api = response["amount"]
#                 payment_mode_api = response["paymentMode"]
#                 accuirer_code_api = response["acquirerCode"]
#                 logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
#                 logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
#                 logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
#
#                 api_details = DBProcessor.get_api_details('txnDetails',
#                                                           request_body={"username": username, "password": password,
#                                                                         "txnId": txn_id_expired})
#                 print("API DETAILS:", api_details)
#                 response = APIProcessor.send_request(api_details)
#                 logger.debug(f"Response received for transaction details api is : {response}")
#                 print(response)
#                 status_api_orginal = response["status"]
#                 amount_api_original = response["amount"]
#                 payment_mode_api_orginal = response["paymentMode"]
#                 logger.debug(f"Fetching Transaction status from transaction api : {status_api_orginal} ")
#                 logger.debug(f"Fetching Transaction amount from transaction api : {amount_api_original} ")
#                 logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api_orginal} ")
#
#                  #
#                 actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Acquirer Code":accuirer_code_api, "Payment Status Original":status_api_orginal,"Amount Original": amount_api_original, "Payment Mode Original": payment_mode_api_orginal}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
#                 logger.info("API Validation Completed successfully for test case")
#             except Exception as e:
#                 print("API Validation failed due to exception - " + str(e))
#                 logger.exception(f"API Validation failed due to exception : {e} ")
#                 msg = msg + "API Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_api_val_result = 'Fail'
#             logger.info(f"Completed API validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of API Validation---------------------------------------
#
#         # -----------------------------------------Start of DB Validation--------------------------------------
#         if (ConfigReader.read_config("Validations", "db_validation")) == "True":
#             try:
#                 logger.info(f"Starting DB Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#                 expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount),"Acquirer Code":"HDFC", "Payment Status Original":"EXPIRED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
#                 #
#                 query = "select status,amount,payment_mode,acquirer_code,external_ref from txn where id='" + txn_id + "'"
#                 logger.debug(f"DB query to fetch status, amount,acquirer_code, payment mode and external reference from DB : {query}")
#                 print("Query:", query)
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Fetching Query result from DB : {result} ")
#                 print(result)
#                 status_db = result["status"].iloc[0]
#                 payment_mode_db = result["payment_mode"].iloc[0]
#                 amount_db = "{:.2f}".format(result["amount"].iloc[0])
#                 accuirer_code_db = result["acquirer_code"].iloc[0]
#                 logger.debug(f"Fetching Transaction status from DB : {status_db} ")
#                 logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
#                 logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
#                 query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_expired + "'"
#                 logger.debug(f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
#                 print("Query:", query)
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Fetching Query result from DB of original txn : {result} ")
#                 print(result)
#                 status_db_original = result["status"].iloc[0]
#                 payment_mode_db_original = result["payment_mode"].iloc[0]
#                 amount_db_original = int(result["amount"].iloc[0])
#                 logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
#                 logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
#                 logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
#                 #
#                 actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db,"Acquirer Code":accuirer_code_db, "Payment Status Original":status_db_original,"Amount Original": amount_db_original, "Payment Mode Original": payment_mode_db_original}
#
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
#                 logger.info("DB Validation Completed successfully for test case")
#             except Exception as e:
#                 print("DB Validation failed due to exception - " + str(e))
#                 logger.exception(f"DB Validation failed due to exception :  {e}")
#                 msg = msg + "DB Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_db_val_result = 'Fail'
#             logger.info(f"Completed DB validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of DB Validation---------------------------------------
#
#         # -----------------------------------------Start of Portal Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
#             try:
#                 logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#                 expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"BHARATQR" , "Payment amount":str(amount), "Payment Status Original":"Expired","Amount Original": str(amount), "Payment Mode Original": "BHARATQR"}
#                 #
#                 ui_driver = TestSuiteSetup.initialize_portal_driver()
#                 loginPagePortal = PortalLoginPage(ui_driver)
#                 logger.info(f"Logging in Portal using username : {portal_username}")
#                 loginPagePortal.perform_login_to_portal(portal_username, portal_password)
#                 homePagePortal = PortalHomePage(ui_driver)
#                 homePagePortal.wait_for_home_page_load()
#                 homePagePortal.search_merchant_name(org_code)
#                 logger.info(f"Switching to merchant : {org_code}")
#                 homePagePortal.click_switch_button(org_code)
#                 homePagePortal.click_transaction_search_menu()
#                 transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
#                 portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
#                 portal_status = portalValuesDict['Status']
#                 portal_txn_type = portalValuesDict['Type']
#                 portal_amt = portalValuesDict['Total Amount']
#                 logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
#                 logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
#                 logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
#                 transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
#                 portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id_expired)
#                 portal_status_original = portalValuesDict['Status']
#                 portal_txn_type_original = portalValuesDict['Type']
#                 portal_amt_original = portalValuesDict['Total Amount']
#                 logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
#                 logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
#                 logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")       #
#                 actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Payment Status Original":portal_status_original,"Amount Original": str(portal_amt_original.split('.')[1]), "Payment Mode Original": portal_txn_type_original}
#
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
#                 logger.info("Portal Validation Completed successfully for test case")
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_portal_val_exe_failed()
#                 print("Portal Validation failed due to exception - " + str(e))
#                 logger.exception(f"Portal Validation failed due to exception : {e}")
#                 msg = msg + "Portal Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_portal_val_result = 'Fail'
#         logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
#         # -----------------------------------------End of Portal Validation---------------------------------------
#         GlobalVariables.time_calc.validation.end()
#         print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
#                       'cyan'))
#         logger.info(f"Completed Validation for the test case : {testcase_id}")
#
#     # -------------------------------------------End of Validation---------------------------------------------
#     finally:
#         Configuration.executeFinallyBlock(testcase_id)
#
#
# @pytest.mark.usefixtures("log_on_success", "method_setup")
# @pytest.mark.apiVal
# @pytest.mark.dbVal
# @pytest.mark.portalVal
# @pytest.mark.appVal
# def test_common_100_102_013(): # check if this is a valid scenario
#     """
#     :Description: Verification of a BQR expired Callback when auto refund enabled via HDFC
#     :Sub Feature code: UI_Common_PM_BQR_Expired_Callback_AutoRefund_enabled_HDFC_13
#     :TC naming code description: 100->Payment Method
#                                 102->BQR
#                                 013-> TC13
#     """
#
#     try:
#         testcase_id = sys._getframe().f_code.co_name
#         GlobalVariables.time_calc.setup.resume()
#         print(
#             colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
#         # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
#         logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
#         app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
#         logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
#         username = app_cred['Username']
#         password = app_cred['Password']
#         portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
#         logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
#         portal_username = portal_cred['Username']
#         portal_password = portal_cred['Password']
#
#         query = "select org_code from org_employee where username='" + str(username) + "';"
#         logger.debug(f"Query to fetch org_code from the DB : {query}")
#         result = DBProcessor.getValueFromDB(query)
#         org_code = result['org_code'].values[0]
#         logger.debug(f"Query result, org_code : {org_code}")
#
#         testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')
#         api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
#                                                                                "password": portal_password,
#                                                                                "settingForOrgCode": org_code})
#         api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
#         logger.debug(f"API details  : {api_details} ")
#         response = APIProcessor.send_request(api_details)
#         logger.debug(f"Response received for setting preconditions is : {response}")
#
#         api_details = DBProcessor.get_api_details('QRExpiryTime',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
#         api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
#         logger.debug(f"API details  : {api_details} ")
#         response = APIProcessor.send_request(api_details)
#         logger.debug(f"Response received for setting preconditions is : {response}")
#         api_details = DBProcessor.get_api_details('AutoRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
#         api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
#         logger.debug(f"API details  : {api_details}")
#         response = APIProcessor.send_request(api_details)
#         logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
#         query = "update bharatqr_provider_config set auto_check_status_enabled=0 where id='2'" #remove this
#         result = DBProcessor.setValueToDB(query)
#         logger.debug(f"Result from updating autocheck status is : {result}")
#
#         GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
#         logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
#
#         # Set the below variables depending on the log capturing need of the test case.
#         Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
#         msg = ""
#         GlobalVariables.time_calc.setup.end()
#         print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
#
#         # -----------------------------------------Start of Test Execution-------------------------------------
#         try:
#             logger.info(f"Starting execution for the test case : {testcase_id}")
#             GlobalVariables.time_calc.execution.start()
#             print(
#                 colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
#                         'cyan'))
#
#             app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
#             loginPage = LoginPage(app_driver)
#             logger.info(f"Logging in the MPOSX application using username : {username}")
#             loginPage.perform_login(username, password)
#             homePage = HomePage(app_driver)
#             homePage.wait_for_navigation_to_load()
#             homePage.check_home_page_logo()
#             homePage.wait_for_home_page_load()
#             logger.info(f"App homepage loaded successfully")
#             amount = random.randint(501, 1000)# use magic numbers for pending txns
#             order_id = datetime.now().strftime('%m%d%H%M%S')
#             homePage.enter_amount_and_order_number(amount, order_id)
#             logger.debug(f"Entered amount is : {amount}")
#             logger.debug(f"Entered order_id is : {order_id}")
#             paymentPage = PaymentPage(app_driver)
#             paymentPage.is_payment_page_displayed(amount, order_id)
#             paymentPage.click_on_Bqr_paymentMode()
#             logger.info("Selected payment mode is BQR")
#             paymentPage.validate_upi_bqr_payment_screen()
#             logger.info("Payment QR generated and displayed successfully")
#             app_driver.reset()
#             query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
#             logger.debug(f"Query to fetch expired transaction id from database is: {query}")
#             result = DBProcessor.getValueFromDB(query)
#             txn_id_expired = result["id"].iloc[0]
#             auth_code = "AE" + txn_id_expired.split('E')[1]
#             rrn = "RE" + txn_id_expired.split('E')[1]
#             logger.debug(
#                 f"Fetching Txn_id,Auth code and RRN from data base : Txn_id expired : {txn_id_expired}, Auth code : {auth_code}, RRN : {rrn}")
#             logger.info(f"Waiting for QR code to get Expired.. Please wait")
#             sleep(60) # check if app txn history page shows correct results
#             api_details = DBProcessor.get_api_details('callbackHDFC',
#                                                       request_body={"PRIMARY_ID": txn_id_expired, "TXN_AMOUNT": str(amount),
#                                                                     "AUTH_CODE": auth_code, "RRN": rrn})
#             response = APIProcessor.send_request(api_details)
#             logger.debug(f"Fetching API Response for call back : {response}")
#             logger.info(f"Logining in to app again with username : {username}")
#             loginPage.perform_login(username, password)
#             homePage = HomePage(app_driver)
#             homePage.check_home_page_logo()
#             logger.info(f"App homepage loaded successfully")
#             query = "select id from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
#             logger.debug(f"Query to fetch transaction id from database is: {query}")
#             result = DBProcessor.getValueFromDB(query)
#             txn_id = result["id"].iloc[0]
#
#             query = "update bharatqr_provider_config set auto_check_status_enabled=1 where id='2'"
#             result = DBProcessor.setValueToDB(query)
#             logger.debug(f"Result from updating autocheck status is : {result}")
#             api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
#                                                                                   "password": portal_password})
#             response = APIProcessor.send_request(api_details)
#             logger.debug(f"Response received for setting precondition DB refresh is : {response}")
#
#             logger.info(f"Execution is completed for the test case : {testcase_id}")
#             #
#             # ------------------------------------------------------------------------------------------------
#             GlobalVariables.EXCEL_TC_Execution = "Pass"
#             GlobalVariables.time_calc.execution.pause()
#             print(colored(
#                 "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
#                                                                                   "="), 'cyan'))
#             logger.info(f"Execution is completed for the test case : {testcase_id}")
#         except Exception as e:
#             if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
#                 GlobalVariables.time_calc.execution.pause()
#                 print(colored(
#                     "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
#                         shutil.get_terminal_size().columns, "="), 'cyan'))
#             GlobalVariables.time_calc.execution.resume()
#             print(colored("Execution Timer resumed in execpt block of testcase function".center(
#                 shutil.get_terminal_size().columns, "="), 'cyan'))
#
#             ReportProcessor.capture_ss_when_app_val_exe_failed()
#
#             GlobalVariables.EXCEL_TC_Execution = "Fail"
#             GlobalVariables.Incomplete_ExecutionCount += 1
#
#             GlobalVariables.time_calc.execution.pause()
#             print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
#                 shutil.get_terminal_size().columns, "="), 'cyan'))
#
#             logger.exception(f"Execution is completed for the test case : {testcase_id}")
#             pytest.fail("Test case execution failed due to the exception -" + str(e))
#         # -----------------------------------------End of Test Execution--------------------------------------
#
#         # -----------------------------------------Start of Validation----------------------------------------
#         logger.info(f"Starting Validation for the test case : {testcase_id}")
#         GlobalVariables.time_calc.validation.start()
#         print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
#                       'cyan'))
#         # -----------------------------------------Start of App Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "app_validation")) == "True":
#             try:
#                 logger.info(f"Starting App Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#                 expectedAppValues = {"Payment Status": "STATUS:REFUND_PENDING", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount), "Payment Status Original": "STATUS:EXPIRED", "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": txn_id_expired, "Payment Amt Original": str(amount)}
#                 homePage.wait_for_navigation_to_load()
#                 homePage.check_home_page_logo()
#                 homePage.click_on_history()
#                 transactionsHistoryPage = TransHistoryPage(app_driver)
#                 transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
#                 app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
#                 logger.debug(
#                     f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
#                 app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
#                 logger.debug(
#                     f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
#                 app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
#                 logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
#                 app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
#                 logger.debug(
#                     f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
#                 transactionsHistoryPage.click_back_Btn_transaction_details()
#                 transactionsHistoryPage.click_on_second_transaction_by_order_id(order_id)
#                 app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
#                 logger.debug(
#                     f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
#                 app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
#                 logger.debug(
#                     f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn Mode = {app_payment_mode_original}")
#                 app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
#                 logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
#                 app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
#                 logger.debug(
#                     f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
#
#                 actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt), "Payment Status Original": app_payment_status_original, "Payment mode Original": app_payment_mode_original, "Payment Txn ID Original": app_txn_id_original, "Payment Amt Original": str(app_payment_amt_original)}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
#                 logger.info("App Validation Completed successfully for test case")
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_app_val_exe_failed()
#                 print("App Validation failed due to exception - " + str(e))
#                 logger.exception(f"App Validation failed due to exception - {e}")
#                 msg = msg + "App Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_app_val_result = "Fail"
#             logger.info(f"Completed APP validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of App Validation---------------------------------------
#
#         # -----------------------------------------Start of API Validation------------------------------------
#         if (ConfigReader.read_config("Validations", "api_validation")) == "True":
#             try:
#                 logger.info(f"Starting API Validation for the test case : {testcase_id}")
#
#                 # --------------------------------------------------------------------------------------------
#
#                 expectedAPIValues = {"Payment Status":"REFUND_PENDING","Amount": amount, "Payment Mode": "BHARATQR","Acquirer Code":"HDFC", "Payment Status Original":"EXPIRED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
#                 api_details = DBProcessor.get_api_details('txnDetails',
#                                                           request_body={"username": username, "password": password,
#                                                                         "txnId": txn_id})
#                 print("API DETAILS:", api_details)
#                 response = APIProcessor.send_request(api_details)
#                 logger.debug(f"Response received for transaction details api is : {response}")
#                 print(response)
#                 status_api = response["status"]
#                 amount_api = response["amount"]
#                 payment_mode_api = response["paymentMode"]
#                 accuirer_code_api = response["acquirerCode"]
#                 logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
#                 logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
#                 logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
#
#                 api_details = DBProcessor.get_api_details('txnDetails',
#                                                           request_body={"username": username, "password": password,
#                                                                         "txnId": txn_id_expired})
#                 print("API DETAILS:", api_details)
#                 response = APIProcessor.send_request(api_details)
#                 logger.debug(f"Response received for transaction details api is : {response}")
#                 print(response)
#                 status_api_orginal = response["status"]
#                 amount_api_original = response["amount"]
#                 payment_mode_api_orginal = response["paymentMode"]
#                 logger.debug(f"Fetching Transaction status from transaction api : {status_api_orginal} ")
#                 logger.debug(f"Fetching Transaction amount from transaction api : {amount_api_original} ")
#                 logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api_orginal} ")
#                  #
#                 actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Acquirer Code":accuirer_code_api, "Payment Status Original":status_api_orginal,"Amount Original": amount_api_original, "Payment Mode Original": payment_mode_api_orginal}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
#                 logger.info("API Validation Completed successfully for test case")
#             except Exception as e:
#                 print("API Validation failed due to exception - " + str(e))
#                 logger.exception(f"API Validation failed due to exception : {e} ")
#                 msg = msg + "API Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_api_val_result = 'Fail'
#             logger.info(f"Completed API validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of API Validation---------------------------------------
#
#         # -----------------------------------------Start of DB Validation--------------------------------------
#         if (ConfigReader.read_config("Validations", "db_validation")) == "True":
#             try:
#                 logger.info(f"Starting DB Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#                 expectedDBValues = {"Payment Status": "REFUND_PENDING", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount),"Acquirer Code":"HDFC", "Payment Status Original":"EXPIRED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
#                 #
#                 query = "select status,amount,payment_mode,acquirer_code,external_ref from txn where id='" + txn_id + "'"
#                 logger.debug(f"DB query to fetch status, amount, acquirer_code,payment mode and external reference from DB : {query}")
#                 print("Query:", query)
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Fetching Query result from DB : {result} ")
#                 print(result)
#                 status_db = result["status"].iloc[0]
#                 payment_mode_db = result["payment_mode"].iloc[0]
#                 amount_db = "{:.2f}".format(result["amount"].iloc[0])
#                 accuirer_code_db = result["acquirer_code"].iloc[0]
#                 logger.debug(f"Fetching Transaction status from DB : {status_db} ")
#                 logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
#                 logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
#                 query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id_expired + "'"
#                 logger.debug(f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
#                 print("Query:", query)
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Fetching Query result from DB of original txn : {result} ")
#                 print(result)
#                 status_db_original = result["status"].iloc[0]
#                 payment_mode_db_original = result["payment_mode"].iloc[0]
#                 amount_db_original = int(result["amount"].iloc[0])
#                 logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
#                 logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
#                 logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
#                 #
#                 actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db,"Acquirer Code":accuirer_code_db, "Payment Status Original":status_db_original,"Amount Original": amount_db_original, "Payment Mode Original": payment_mode_db_original}
#
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
#                 logger.info("DB Validation Completed successfully for test case")
#             except Exception as e:
#                 print("DB Validation failed due to exception - " + str(e))
#                 logger.exception(f"DB Validation failed due to exception :  {e}")
#                 msg = msg + "DB Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_db_val_result = 'Fail'
#             logger.info(f"Completed DB validation for the test case : {testcase_id}")
#         # -----------------------------------------End of DB Validation---------------------------------------
#
#         # -----------------------------------------Start of Portal Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
#             try:
#                 logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#                 expectedPortalValues = {"Payment Status": "Refund Pending", "Payment mode":"BHARATQR" , "Payment amount":str(amount), "Payment Status Original":"Expired","Amount Original": str(amount), "Payment Mode Original": "BHARATQR"}
#                 #
#                 ui_driver = TestSuiteSetup.initialize_portal_driver()
#                 loginPagePortal = PortalLoginPage(ui_driver)
#                 logger.info(f"Logging in Portal using username : {portal_username}")
#                 loginPagePortal.perform_login_to_portal(portal_username, portal_password)
#                 homePagePortal = PortalHomePage(ui_driver)
#                 homePagePortal.wait_for_home_page_load()
#                 homePagePortal.search_merchant_name(org_code)
#                 logger.info(f"Switching to merchant : {org_code}")
#                 homePagePortal.click_switch_button(org_code)
#                 homePagePortal.click_transaction_search_menu()
#                 transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
#                 portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
#                 portal_status = portalValuesDict['Status']
#                 portal_txn_type = portalValuesDict['Type']
#                 portal_amt = portalValuesDict['Total Amount']
#                 logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
#                 logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
#                 logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
#                 transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
#                 portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id_expired)
#                 portal_status_original = portalValuesDict['Status']
#                 portal_txn_type_original = portalValuesDict['Type']
#                 portal_amt_original = portalValuesDict['Total Amount']
#                 logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
#                 logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
#                 logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
#                 #
#                 actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Payment Status Original":portal_status_original,"Amount Original": str(portal_amt_original.split('.')[1]), "Payment Mode Original": portal_txn_type_original}
#
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
#                 logger.info("Portal Validation Completed successfully for test case")
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_portal_val_exe_failed()
#                 print("Portal Validation failed due to exception - " + str(e))
#                 logger.exception(f"Portal Validation failed due to exception : {e}")
#                 msg = msg + "Portal Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_portal_val_result = 'Fail'
#             logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of Portal Validation---------------------------------------
#         GlobalVariables.time_calc.validation.end()
#         print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
#                       'cyan'))
#         logger.info(f"Completed Validation for the test case : {testcase_id}")
#
#     # -------------------------------------------End of Validation---------------------------------------------
#     finally:
#         Configuration.executeFinallyBlock(testcase_id)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_012():
    """
    :Description: Verification of a BQRV4 BQR Callback After QR code gets expired when auto refund is Disabled via HDFC
    :Sub Feature code: UI_Common_BQRV4_Callback_AfterExpiry_AutoRefund_Disabled_HDFC_12
    :TC naming code description: 100->Payment Method, 102->BQR, 012-> TC12
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')

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

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]

        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

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
            amount = 49.65
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response revived for QR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Txn id, auth code, rrn for this transaction is : "
                         f"{txn_id}, {rrn}, {auth_code}")
            logger.debug("Waiting for 1min to QR code to get expired")
            sleep(60)
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_ID": txn_id,
                                                                    "TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting date for {txn_id} : {posting_date} ")

            query = "select * from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' " \
                                                                    "order by created_time desc limit 1"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result["id"].iloc[0]
            auth_code_new = result['auth_code'].values[0]
            rrn_new = result['rr_number'].iloc[0]
            posting_date_new = result['posting_date'].values[0]
            modified_date_new = result['modified_time'].values[0]
            logger.debug(f"Fetching new txn_id, auth_code, rrn, posting_date, customer name and payer name"
                f" from database for current merchant:{txn_id_new}, {auth_code_new}, {rrn_new}, {posting_date_new}")

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
                date_and_time_new = date_time_converter.to_app_format(modified_date_new)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED","txn_amt": str(amount),
                                       "settle_status": "FAILED","txn_id": txn_id,
                                       "order_id": order_id,"msg": "PAYMENT FAILED",
                                       "date": date_and_time,
                                       "pmt_mode_new": "BHARAT QR", "pmt_status_new": "AUTHORIZED",
                                       "txn_amt_new": str(amount), "rrn_new": str(rrn_new),
                                       "settle_status_new": "SETTLED", "txn_id_new": txn_id_new,
                                       "order_id_new": order_id, "msg_new": "PAYMENT SUCCESSFUL",
                                       "auth_code_new": auth_code_new, "date_new": date_and_time_new
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
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_new": payment_mode_new, "pmt_status_new": payment_status_new.split(':')[1],
                                     "txn_amt_new": app_amount_new.split(' ')[1],
                                     "txn_id_new": app_txn_id_new, "rrn_new": str(app_rrn_new),
                                     "settle_status_new": app_settlement_status_new,
                                     "order_id_new": app_order_id_new, "auth_code_new": app_auth_code_new,
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
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date,
                                       "pmt_status_new": "AUTHORIZED", "txn_amt_new": amount,
                                       "pmt_mode_new": "BHARATQR","pmt_state_new": "SETTLED",
                                       "rrn_new": str(rrn_new), "settle_status_new": "SETTLED","acquirer_code_new": "HDFC",
                                       "issuer_code_new": "HDFC", "txn_type_new": "CHARGE",
                                       "mid_new": mid, "tid_new": tid, "org_code_new": org_code,
                                       "auth_code_new": auth_code_new, "date_new": date_new
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
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_new][0]
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
                auth_code_api_new = response["authCode"]
                date_api_new = response["postingDate"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_new": status_api_new, "txn_amt_new": amount_api_new,
                                     "pmt_mode_new": payment_mode_api_new,
                                     "pmt_state_new": state_api_new, "rrn_new": str(rrn_api_new),
                                     "settle_status_new": settlement_status_api_new,
                                     "acquirer_code_new": acquirer_code_api_new,
                                     "issuer_code_new": issuer_code_api_new, "mid_new": mid_api_new,
                                     "txn_type_new": txn_type_api_new, "tid_new": tid_api_new,
                                     "auth_code_new": auth_code_api_new, "org_code_new": org_code_api_new,
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "BHARATQR","pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED","acquirer_code" : "HDFC", "bank_name" : "HDFC Bank",
                                      "mid" :mid, "tid" : tid, "pmt_gateway": "HDFC",
                                      "settle_status": "FAILED",
                                      "bqr_pmt_status": "FAILURE", "bqr_pmt_state": "EXPIRED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": bqr_m_pan,
                                      "bqr_org_code": org_code,
                                      "txn_amt_new": amount, "pmt_mode_new": "BHARATQR",
                                      "pmt_status_new": "AUTHORIZED",
                                      "pmt_state_new": "SETTLED", "acquirer_code_new": "HDFC",
                                      "bank_name_new": "HDFC Bank",
                                      "mid_new": mid, "tid_new": tid, "pmt_gateway_new": "HDFC",
                                      "rrn_new": str(rrn), "settle_status_new": "SETTLED",
                                      "bqr_pmt_status_new": "Transaction Success", "bqr_pmt_state_new": "SETTLED",
                                      "bqr_txn_amt_new": amount,
                                      "bqr_txn_type_new": "DYNAMIC_QR", "brq_terminal_info_id_new": terminal_info_id,
                                      "bqr_bank_code_new": "HDFC",
                                      "bqr_merchant_config_id_new": bqr_mc_id, "bqr_txn_primary_id_new": txn_id_new,
                                      "bqr_merchant_pan_new": bqr_m_pan,
                                      "bqr_rrn_new": str(rrn), "bqr_org_code_new": org_code
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
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new = float(result["amount"].iloc[0])
                payment_mode_db_new = result["payment_mode"].iloc[0]
                payment_status_db_new = result["status"].iloc[0]
                payment_state_db_new = result["state"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_name_db_new = result["bank_name"].iloc[0]
                mid_db_new = result["mid"].iloc[0]
                tid_db_new = result["tid"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                rr_number_db_new = result["rr_number"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_new = result["status_desc"].iloc[0]
                bqr_state_db_new = result["state"].iloc[0]
                bqr_amount_db_new = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_new = result["txn_type"].iloc[0]
                brq_terminal_info_id_db_new = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_new = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_new = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db_new = result["merchant_pan"].iloc[0]
                bqr_rrn_db_new = result['rrn'].values[0]
                bqr_org_code_db_new = result['org_code'].values[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_org_code": bqr_org_code_db,
                                    "txn_amt_new": amount_db_new, "pmt_mode_new": payment_mode_db_new,
                                    "pmt_status_new": payment_status_db_new, "pmt_state_new": payment_state_db_new,
                                    "acquirer_code_new": acquirer_code_db_new, "bank_name_new": bank_name_db_new,
                                    "mid_new": mid_db_new, "tid_new": tid_db_new,
                                    "pmt_gateway_new": payment_gateway_db_new, "rrn_new": rr_number_db_new,
                                    "settle_status_new": settlement_status_db_new,
                                    "bqr_pmt_status_new": bqr_status_db_new, "bqr_pmt_state_new": bqr_state_db_new,
                                    "bqr_txn_amt_new": bqr_amount_db_new,
                                    "bqr_txn_type_new": bqr_txn_type_db_new,
                                    "brq_terminal_info_id_new": brq_terminal_info_id_db_new,
                                    "bqr_bank_code_new": bqr_bank_code_db_new,
                                    "bqr_merchant_config_id_new": bqr_merchant_config_id_db_new,
                                    "bqr_txn_primary_id_new": bqr_txn_primary_id_db_new,
                                    "bqr_merchant_pan_new": bqr_merchant_pan_db_new,
                                    "bqr_rrn_new": bqr_rrn_db_new, "bqr_org_code_new": bqr_org_code_db_new
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(modified_date_new)
                expected_values = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_new),
                                   'BASE AMOUNT:': "Rs." + str(amount) ,  'date': txn_date,'time': txn_time,
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_013():
    """
    :Description: Verification of a BQRV4 BQR Callback After QR code gets expired when auto refund is Enabled via HDFC
    :Sub Feature code: UI_Common_BQRV4_Callback_AfterExpiry_AutoRefund_Enabled_HDFC_13
    :TC naming code description: 100->Payment Method, 102->BQR, 013-> TC13
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')

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

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
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

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]

        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

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
            amount = 49.65
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response revived for QR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Txn id, auth code, rrn for this transaction is : "
                         f"{txn_id}, {rrn}, {auth_code}")
            logger.debug("Waiting for 1min to QR code to get expired")
            sleep(60)
            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": txn_id, "TXN_ID": txn_id,
                                                                    "TXN_AMOUNT": str(amount),
                                                                    "AUTH_CODE": auth_code, "RRN": rrn,
                                                                    "MERCHANT_PAN": bqr_m_pan})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting date for {txn_id} : {posting_date} ")

            query = "select * from txn where org_code='"+org_code+"' and external_ref='"+order_id+"' " \
                                                                    "order by created_time desc limit 1"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result["id"].iloc[0]
            auth_code_new = result['auth_code'].values[0]
            rrn_new = result['rr_number'].iloc[0]
            posting_date_new = result['posting_date'].values[0]
            modified_date_new = result['modified_time'].values[0]
            logger.debug(f"Fetching new txn_id, auth_code, rrn, posting_date, customer name and payer name"
                f" from database for current merchant:{txn_id_new}, {auth_code_new}, {rrn_new}, {posting_date_new}")

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
                date_and_time_new = date_time_converter.to_app_format(modified_date_new)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED","txn_amt": str(amount),
                                       "settle_status": "FAILED","txn_id": txn_id,
                                       "order_id": order_id,"msg": "PAYMENT FAILED",
                                       "date": date_and_time,
                                       "pmt_mode_new": "BHARAT QR", "pmt_status_new": "REFUND_PENDING",
                                       "txn_amt_new": str(amount), "rrn_new": str(rrn_new),
                                       "settle_status_new": "SETTLED", "txn_id_new": txn_id_new,
                                       "order_id_new": order_id, "msg_new": "PAYMENT SUCCESSFUL",
                                       "auth_code_new": auth_code_new, "date_new": date_and_time_new
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
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)


                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_new": payment_mode_new, "pmt_status_new": payment_status_new.split(':')[1],
                                     "txn_amt_new": app_amount_new.split(' ')[1],
                                     "txn_id_new": app_txn_id_new, "rrn_new": str(app_rrn_new),
                                     "settle_status_new": app_settlement_status_new,
                                     "order_id_new": app_order_id_new, "auth_code_new": app_auth_code_new,
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
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date,
                                       "pmt_status_new": "REFUND_PENDING", "txn_amt_new": amount,
                                       "pmt_mode_new": "BHARATQR","pmt_state_new": "REFUND_PENDING",
                                       "rrn_new": str(rrn_new), "settle_status_new": "SETTLED","acquirer_code_new": "HDFC",
                                       "issuer_code_new": "HDFC", "txn_type_new": "CHARGE",
                                       "mid_new": mid, "tid_new": tid, "org_code_new": org_code,
                                       "auth_code_new": auth_code_new, "date_new": date_new
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
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_new = response["status"]
                amount_api_new = float(response["amount"])  # actual=345.00, expected should be in the same format
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
                auth_code_api_new = response["authCode"]
                date_api_new = response["postingDate"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_new": status_api_new, "txn_amt_new": amount_api_new,
                                     "pmt_mode_new": payment_mode_api_new,
                                     "pmt_state_new": state_api_new, "rrn_new": str(rrn_api_new),
                                     "settle_status_new": settlement_status_api_new,
                                     "acquirer_code_new": acquirer_code_api_new,
                                     "issuer_code_new": issuer_code_api_new, "mid_new": mid_api_new,
                                     "txn_type_new": txn_type_api_new, "tid_new": tid_api_new,
                                     "auth_code_new": auth_code_api_new, "org_code_new": org_code_api_new,
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "BHARATQR","pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED","acquirer_code" : "HDFC", "bank_name" : "HDFC Bank",
                                      "mid" :mid, "tid" : tid, "pmt_gateway": "HDFC",
                                      "settle_status": "FAILED",
                                      "bqr_pmt_status": "FAILURE", "bqr_pmt_state": "EXPIRED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": bqr_m_pan,
                                      "bqr_org_code": org_code,
                                      "txn_amt_new": amount, "pmt_mode_new": "BHARATQR",
                                      "pmt_status_new": "REFUND_PENDING",
                                      "pmt_state_new": "REFUND_PENDING", "acquirer_code_new": "HDFC",
                                      "bank_name_new": "HDFC Bank",
                                      "mid_new": mid, "tid_new": tid, "pmt_gateway_new": "HDFC",
                                      "rrn_new": str(rrn), "settle_status_new": "SETTLED",
                                      "bqr_pmt_status_new": "Transaction Success", "bqr_pmt_state_new": "REFUND_PENDING",
                                      "bqr_txn_amt_new": amount,
                                      "bqr_txn_type_new": "DYNAMIC_QR", "brq_terminal_info_id_new": terminal_info_id,
                                      "bqr_bank_code_new": "HDFC",
                                      "bqr_merchant_config_id_new": bqr_mc_id, "bqr_txn_primary_id_new": txn_id_new,
                                      "bqr_merchant_pan_new": bqr_m_pan,
                                      "bqr_rrn_new": str(rrn), "bqr_org_code_new": org_code
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
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new = float(result["amount"].iloc[0])
                payment_mode_db_new = result["payment_mode"].iloc[0]
                payment_status_db_new = result["status"].iloc[0]
                payment_state_db_new = result["state"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_name_db_new = result["bank_name"].iloc[0]
                mid_db_new = result["mid"].iloc[0]
                tid_db_new = result["tid"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                rr_number_db_new = result["rr_number"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = "select * from bharatqr_txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_new = result["status_desc"].iloc[0]
                bqr_state_db_new = result["state"].iloc[0]
                bqr_amount_db_new = float(result["txn_amount"].iloc[0])
                bqr_txn_type_db_new = result["txn_type"].iloc[0]
                brq_terminal_info_id_db_new = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_new = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_new = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db_new = result["merchant_pan"].iloc[0]
                bqr_rrn_db_new = result['rrn'].values[0]
                bqr_org_code_db_new = result['org_code'].values[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_org_code": bqr_org_code_db,
                                    "txn_amt_new": amount_db_new, "pmt_mode_new": payment_mode_db_new,
                                    "pmt_status_new": payment_status_db_new, "pmt_state_new": payment_state_db_new,
                                    "acquirer_code_new": acquirer_code_db_new, "bank_name_new": bank_name_db_new,
                                    "mid_new": mid_db_new, "tid_new": tid_db_new,
                                    "pmt_gateway_new": payment_gateway_db_new, "rrn_new": rr_number_db_new,
                                    "settle_status_new": settlement_status_db_new,
                                    "bqr_pmt_status_new": bqr_status_db_new, "bqr_pmt_state_new": bqr_state_db_new,
                                    "bqr_txn_amt_new": bqr_amount_db_new,
                                    "bqr_txn_type_new": bqr_txn_type_db_new,
                                    "brq_terminal_info_id_new": brq_terminal_info_id_db_new,
                                    "bqr_bank_code_new": bqr_bank_code_db_new,
                                    "bqr_merchant_config_id_new": bqr_merchant_config_id_db_new,
                                    "bqr_txn_primary_id_new": bqr_txn_primary_id_db_new,
                                    "bqr_merchant_pan_new": bqr_merchant_pan_db_new,
                                    "bqr_rrn_new": bqr_rrn_db_new, "bqr_org_code_new": bqr_org_code_db_new
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(modified_date_new)
                expected_values = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_new),
                                   'BASE AMOUNT:': "Rs." + str(amount),  'date': txn_date,'time': txn_time,
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
