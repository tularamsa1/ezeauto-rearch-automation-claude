import random
import sys
import time
import pytest

from datetime import datetime
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from Utilities.execution_log_processor import EzeAutoLogger
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, date_time_converter

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
def test_sa_100_101_169():
    """
    Sub Feature Code: UI_SA_PM_UPI_SA_CheckStatus_After_Expiry_KOTAK_ATOS
    Sub Feature Description: Verification of a UPI txn after expiry for KOTAK_ATOS using SA check status
    TC naming code description: 100: Payment method, 101: UPI, 169: Testcase ID
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details for QR Exipry Time : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received from UPI QR Expiry time : {response}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from upi_merchant_config table : {tid}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True,
                                                   cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)

            amount = random.choice([i for i in range(1, 100) if i not in [45, 46]])
            logger.debug(f"Initiating UPI QR for the amount of {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")

            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("QR code generated successfully")

            logger.info("resetting the com.ezetap.basicapp")
            app_driver.reset()
            logger.info(f"After reseting the app logging in again in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()

            logger.info("waiting for the time till qr get expired...")
            time.sleep(60)

            home_page.enter_amount_and_order_number(amount, order_id)
            payment_page = PaymentPage(app_driver)
            home_page.perform_check_status()
            payment_page.click_on_proceed_homepage()
            home_page.click_on_back_btn_enter_amt_page()

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching id from the txn table : {txn_id}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {created_time}")

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
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
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
                    "pmt_status": "EXPIRED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                response_in_list = response["txns"]
                logger.debug(f"list of txns is : {response_in_list}")

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api is : {status_api}")
                        amount_api = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api is : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api is : {state_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api}")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api is : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api is : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api}")
                        date_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")

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
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "mid": mid,
                    "tid": tid,
                    "upi_mc_id": upi_mc_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data for actual db values from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from txn table based on txn_id : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the txn table based on txn_id : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching actual db payment_mode value from the txn table based on txn_id : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching actual db amount value from the txn table based on txn_id : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching actual db state value from the txn table based on txn_id : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching actual db payment_gateway value from the txn table based on txn_id : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching actual db acquirer_code value from the txn table based on txn_id : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the txn table based on txn_id : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching actual db settlement_status value from the txn table based on txn_id : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching actual db tid value from the txn table based on txn_id : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching actual db mid value from the txn table based on txn_id : {mid_db}")

                query = "select * from upi_txn where txn_id='" + txn_id + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching status from upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type from upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code from upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from upi_txn table : {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "upi_mc_id": upi_mc_id_db
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

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