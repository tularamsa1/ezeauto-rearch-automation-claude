import random
import sys
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, receipt_validator, ResourceAssigner, \
    date_time_val, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_L3_5304_101_001():
    """
    Sub Feature Code: L3_5304_PM_UPI_Success_Callback_AXIS_FC
    Sub Feature Description: Verification of a upi Callback Success transaction via AXIS_FC
    TC naming code description: L3_5304: L3_Ticket_Id, 101: UPI, 001: TC001
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, 'AXIS_FC', portal_username, portal_password, 'UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "True"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND bank_code = 'AXIS_FC'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Query result pgMerchantId : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result vpa : {vpa}")
        mid = result['mid'].values[0]
        logger.debug(f"Query result mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Query result tid : {tid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # -----------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(100, 200)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is upi")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query fetched result is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            query = f"select * from upi_txn where txn_id = '{str(txn_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            bank_txn_id = str(random.randint(100000000000, 999999999999))

            api_details = DBProcessor.get_api_details('axisfc_hash', request_body={
                "amount": amount,
                "errMsg": "Transaction Successful",
                "merchantTxnId": txn_ref,
                "monitorId": pg_merchant_id,
                "bankTxnId": bank_txn_id,
                "payableAmount": 0.00,
                "userPaymentIdentifier": vpa,
                "feeAmount": 0.00,
                "merchantId": mid,
                "errCode": "00",
                "status": "SUCCESS",
                "txnId": txn_id,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for axisfc_hash api is : {response}")

            api_details = DBProcessor.get_api_details('upi_confirm_axisfc', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_axisfc api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from txn_db : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn_db : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching from amount txn_db : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment_mode from txn_db : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment_status from txn_db : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment_state from txn_db : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer_code from txn_db : {acquirer_code_db}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.debug(f"Fetching bank_name from txn_db : {bank_name_db}")
            payer_name_db = result["payer_name"].iloc[0]
            logger.debug(f"Fetching payer_name from txn_db : {payer_name_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn_db : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn_db : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment_gateway from txn_db : {payment_gateway_db}")
            rr_number_db = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rr_number from txn_db : {rr_number_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement_status from txn_db : {settlement_status_db}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from txn_db : {rrn}")

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
                date_and_time = date_time_val.date_and_time_val_against_app(created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": vpa,
                    "payer_name": vpa,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
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
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

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
                    "msg": app_payment_msg,
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
                date = date_time_val.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date
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
                logger.debug(f"status_api : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"amount_api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"rrn_api : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api : {acquirer_code_api}")
                orgCode_api = response["orgCode"]
                logger.debug(f"orgCode_api : {orgCode_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"date_api : {date_api}")

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
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_val.date_and_time_val_against_api(date_api)
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
                    "acquirer_code": "AXIS",
                    "bank_name": "Axis Bank",
                    "payer_name": vpa,
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "FC",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "upi_pmt_status": "AUTHORIZED",
                    "upi_txn_type": "PAY_QR",
                    "upi_mc_id": upi_mc_id,
                    "upi_bank_code": "AXIS_FC"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db : {upi_txn_type_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db : {upi_mc_id_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db : {upi_bank_code_db}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_name": bank_name_db,
                    "payer_name": payer_name_db,
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
                    "rrn": "-" if rrn is None else str(rrn)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.info(f"fetched date time from portal {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type}")
                status = transaction_details[0]['Status']
                logger.info(f"fetched status {status}")
                username = transaction_details[0]['Username']
                logger.info(f"fetched username from portal {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": status,
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": str(rr_number)
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
                txn_date, txn_time = date_time_val.date_and_time_val_against_charge_slip(created_time)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
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
@pytest.mark.portalVal
@pytest.mark.appVal
def test_L3_4998_101_001():
    """
    Sub Feature Code: L3_4998_PM_UPI_failed_Callback_AXIX_FC
    Sub Feature Description: Verification of a upi Callback failed transaction and RRN NUMBER is captured or not via AXIS_FC
    TC naming code description: L3_4998: T3_Ticket_Id, 101: UPI, 001: TC001
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, 'AXIS_FC', portal_username, portal_password, 'UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "True"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND bank_code = 'AXIS_FC'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id  from database for current merchant: {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Query result pgMerchantId : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result vpa : {vpa}")
        mid = result['mid'].values[0]
        logger.debug(f"Query result mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Query result tid : {tid}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # -----------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(100, 200)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is upi")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query fetched result is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            query = f"select * from upi_txn where txn_id = '{str(txn_id)}';"
            logger.debug(f"Query to fetch Txn_ref from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            bank_txn_id = str(random.randint(100000000000, 999999999999))

            api_details = DBProcessor.get_api_details('axisfc_hash', request_body={
                "amount": amount,
                "errMsg": "Transaction Failed",
                "merchantTxnId": txn_ref,
                "monitorId": pg_merchant_id,
                "bankTxnId": bank_txn_id,
                "payableAmount": 0.00,
                "userPaymentIdentifier": vpa,
                "feeAmount": 0.00,
                "merchantId": mid,
                "errCode": "U91",
                "status": "FAILED",
                "txnId": txn_id,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for axisfc_hash api is : {response}")
            logger.debug(f"performing upi callback for axisfc")
            api_details = DBProcessor.get_api_details('upi_confirm_axisfc', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_axisfc api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
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
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.launch_app()
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
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
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
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "order_id": order_id,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"status_api :{status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api :{amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api :{payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api :{state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"rrn_api :{rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api :{settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api :{issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api :{acquirer_code_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api :{mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api :{tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api :{txn_type_api}")
                order_id_api = response["externalRefNumber"]
                logger.debug(f"order_id_api :{order_id_api}")
                date_api = response["createdTime"]
                logger.debug(f"date_api :{date_api}")

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
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
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": str(amount),
                    "upi_txn_status": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "FC",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "AXIS_FC",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db :{status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db :{payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"amount_db :{amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db :{state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db :{payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db :{acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db :{bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db :{settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"tid_db :{tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"mid_db :{mid_db}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db :{upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db :{upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db :{upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db :{upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": str(amount_db),
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
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
                    "pmt_state": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time :{date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id :{transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount :{total_amount}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number :{rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type :{transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status :{status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username :{username}")

                actual_portal_values = {

                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
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
