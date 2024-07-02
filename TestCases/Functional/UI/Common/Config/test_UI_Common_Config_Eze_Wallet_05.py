import random
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import (Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, ResourceAssigner,
                       date_time_converter, Ezewallet_processor)
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_200_202_021():
    """
        Sub Feature Code: UI_Common_Config_Ezewallet_Verify_Topup_Field_Proceed_Button
        Sub Feature Description: verify topup field and proceed button in the ezewallet screen (Role: agent)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 021: TC021
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        org_code = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["MerchantCode"]
        logger.debug(f"Fetching the org_code from Ezewallet sheet : {org_code}")
        app_username = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Username"]
        logger.debug(f"Fetching the app_username from Ezewallet sheet : {app_username}")
        app_password = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Password"]
        logger.debug(f"Fetching the app_password from Ezewallet sheet : {app_password}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet in preconditions : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_side_menu_eng()
            logger.debug(f"clicked on side menu")
            home_page.click_on_eze_wallet()
            logger.debug(f"clicked on eze wallet option from the side menu")
            try:
                home_page.validate_topup_field_and_proceed_btn()
                msg = "topup field and proceed button is visible"
            except Exception as e:
                logger.error(f"topup field and proceed button is not visible due to error : {e}")
                msg = "topup field and proceed button is not visible"

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
                expected_app_values = {
                    "msg": "topup field and proceed button is visible",
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "msg": msg,
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation--------------------------------------
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
def test_common_100_200_202_022():
    """
        Sub Feature Code: UI_Common_Config_Ezewallet_Verify_Success_Topup_Via_Upi
        Sub Feature Description: Verify success upi txn for agent top-up(Role: agent)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 022: TC022
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        org_code = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["MerchantCode"]
        logger.debug(f"Fetching the org_code from Ezewallet sheet : {org_code}")
        app_username = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Username"]
        logger.debug(f"Fetching the app_username from Ezewallet sheet : {app_username}")
        app_password = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Password"]
        logger.debug(f"Fetching the app_password from Ezewallet sheet : {app_password}")

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet in preconditions : {response}")

        query = (f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code "
                 f"= 'HDFC' AND acc_label_id=(select id from label where name='TOPUP' AND org_code ='{org_code}')")
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : id : {upi_mc_id}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the upi_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the upi_merchant_config table : tid : {tid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_side_menu_eng()
            logger.debug(f"clicked on side menu")
            home_page.click_on_eze_wallet()
            logger.debug(f"clicked on ezewallet option from the side menu")
            amount = random.randint(201, 250)
            home_page.perform_top_up(amount=amount)
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            payment_page.click_on_goto_homepage()
            home_page.click_on_back_btn_cash_at_pos_page()

            query = (f"select * from txn where org_code='{org_code}' and customer_mobile= '{app_username}'"
                     f" order by created_time desc limit 1")
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result obtained from txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id from txn table : {txn_id}")
            amount_db = result['amount'].iloc[0]
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            customer_mobile = result['customer_mobile'].iloc[0]
            logger.debug(f"Fetching customer_mobile from txn table : {customer_mobile}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table : {txn_created_time}")
            txn_type_db = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table : {txn_type_db}")
            external_ref_db = result['external_ref'].values[0]
            logger.debug(f"Fetching external_ref from txn table : {external_ref_db}")
            state_db = result['state'].values[0]
            logger.debug(f"Fetching state from txn table : {state_db}")
            status_db = result['status'].values[0]
            logger.debug(f"Fetching status from txn table : {status_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from txn table : {settlement_status_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from txn table : {payment_mode_db}")
            external_ref2_db = result['external_ref2'].values[0]
            logger.debug(f"Fetching external_ref2 from txn table : {external_ref2_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            customer_name_db = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from txn table : {customer_name_db}")
            payer_name_db = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from txn table : {payer_name_db}")
            bank_name_db = result['bank_name'].values[0]
            logger.debug(f"Fetching bank_name from txn table : {bank_name_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from txn table : {acquirer_code_db}")
            bank_code_db = result['bank_code'].values[0]
            logger.debug(f"Fetching bank_code from txn table : {bank_code_db}")
            rr_number_db = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from txn table : {rr_number_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from txn table : {payment_gateway_db}")

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
                date_and_time = date_time_converter.to_app_format(txn_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "rrn": rrn,
                    "order_id": external_ref_db,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "date": date_and_time,
                    "customer_name": customer_name_db,
                    "payer_name": payer_name_db,
                    "external_ref2": external_ref2_db,
                    "customer_no": app_username
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.click_on_history_config()
                transactions_history_page = TransHistoryPage(app_driver)
                logger.info("selecting txn by txn id")
                transactions_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_msg_app = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment message from txn history for the txn : {payment_msg_app}")
                payment_type_app = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment type from txn history for the txn : {payment_type_app}")
                txn_amount_app = transactions_history_page.fetch_txn_amount_text()[2:]
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_amount_app}")
                order_id_app = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching order id from txn history for the txn : {order_id_app}")
                txn_id_app = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn id from txn history for the txn :, {txn_id_app}")
                status_app = transactions_history_page.fetch_txn_status_text().replace('STATUS:', '')
                logger.info(f"Fetching status from txn history for the txn : {status_app}")
                settlement_status_app = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {settlement_status_app}")
                rrn_app = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {rrn_app}")
                date_and_time_app = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {date_and_time_app}")
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {app_customer_name}")
                app_payer_name = transactions_history_page.fetch_payer_name_text()
                logger.info(f"Fetching payer_name from txn history for the txn : {app_payer_name}")
                app_external_ref2 = transactions_history_page.fetch_reference_2_text()
                logger.info(f"Fetching external_ref2 from txn history for the txn : {app_external_ref2}")
                app_customer_no = transactions_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_number from txn history for the txn : {app_customer_no}")

                actual_app_values = {
                    "pmt_mode": payment_type_app,
                    "pmt_status": status_app,
                    "txn_amt": txn_amount_app,
                    "txn_id": txn_id_app,
                    "rrn": rrn_app,
                    "order_id": order_id_app,
                    "pmt_msg": payment_msg_app,
                    "settle_status": settlement_status_app,
                    "date": date_and_time_app,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "external_ref2": app_external_ref2,
                    "customer_no": app_customer_no
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
                date = date_time_converter.db_datetime(txn_created_time)
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
                    "order_id": external_ref_db,
                    "date": date,
                    "account_label": 'TOPUP'
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
                account_label_name_api = response["accountLabel"]

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
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "account_label": account_label_name_api
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
                    "payer_name": "Test Payer",
                    "bank_name": "HDFC Bank",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "pmt_gateway": "HDFC",
                    "rrn": rrn,
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
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rr_number_db,
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

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(external_ref_db),
                    'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                }
                logger.info(f"Performing ChargeSlip validation for the txn")
                receipt_validator.perform_charge_slip_validations(txn_id, {"username": app_username,
                                                                           "password": app_password},
                                                                  expected_charge_slip_values)
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
@pytest.mark.appVal
def test_common_100_200_202_023():
    """
        Sub Feature Code: UI_Common_Config_Ezewallet_Verify_Proceed_Button_clickable_By_Not_Entering_Top_Up_Amount
        Sub Feature Description: Verify if the proceed button is clickable when the top-up amount is not entered (Role: agent)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 023: TC023
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        org_code = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["MerchantCode"]
        logger.debug(f"Fetching the org_code from Ezewallet sheet : {org_code}")
        app_username = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Username"]
        logger.debug(f"Fetching the app_username from Ezewallet sheet : {app_username}")
        app_password = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Password"]
        logger.debug(f"Fetching the app_password from Ezewallet sheet : {app_password}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet in preconditions : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_side_menu_eng()
            logger.debug(f"clicked on side menu")
            home_page.click_on_eze_wallet()
            logger.debug(f"clicked on ezewallet option from the side menu")
            response = home_page.validate_top_up_proceed_button()
            if response:
                msg = 'Proceed button is clickable'
            else:
                msg = 'Proceed button is not clickable'

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
                expected_app_values = {
                    "is_button_enabled": False,
                    'msg': 'Proceed button is not clickable'
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "is_button_enabled": response,
                    'msg': msg
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation--------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_200_202_024():
    """
        Sub Feature Code: UI_Common_Config_Ezewallet_Verify_Agent_Passbook_And_Transaction
        Sub Feature Description: verification of agent passbook and transaction under quick action (Role: agent)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 024: TC024
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        org_code = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["MerchantCode"]
        logger.debug(f"Fetching the org_code from Ezewallet sheet : {org_code}")
        app_username = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Username"]
        logger.debug(f"Fetching the app_username from Ezewallet sheet : {app_username}")
        app_password = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Password"]
        logger.debug(f"Fetching the app_password from Ezewallet sheet : {app_password}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet in preconditions : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_side_menu_eng()
            logger.debug(f"clicked on side menu")
            home_page.click_on_eze_wallet()
            logger.debug(f"clicked on ezewallet option from the side menu")
            try:
                logger.debug("validating passbook and transaction under quick action")
                agent_passbook = home_page.validate_agent_passbook()
                agent_transaction = home_page.validate_agent_transaction()
                logger.debug("passbook and transaction are visible")
                msg = "agent passbook and transaction is visible under quick action"
            except Exception as e:
                logger.error(f"agent passbook and transaction is not visible under quick action due to error: {e}")
                msg = "agent passbook and transaction is not visible under quick action"

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
                expected_app_values = {
                    "text_1": "My Passbook",
                    "text_2": "Transactions",
                    'msg': "agent passbook and transaction is visible under quick action"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "text_1": agent_passbook,
                    "text_2": agent_transaction,
                    'msg': msg
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation--------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_200_202_025():
    """
        Sub Feature Code: UI_Common_Config_Ezewallet_Verify_Agent_Eze_wallet_screen
        Sub Feature Description: Verify the agent's balance, last top-up, last top-up date, and mobile number in the
                                  eze wallet screen (Role: agent)
        TC naming code description: 100: Payment Method, 200: Ezewallet , 202: North Bihar, 025: TC025
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        org_code = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["MerchantCode"]
        logger.debug(f"Fetching the org_code from Ezewallet sheet : {org_code}")
        app_username = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Username"]
        logger.debug(f"Fetching the app_username from Ezewallet sheet : {app_username}")
        app_password = Ezewallet_processor.get_ezewallet_details_from_excel("Maheswaran_Unni")["Password"]
        logger.debug(f"Fetching the app_password from Ezewallet sheet : {app_password}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["enableClosedLoopWalletForMerchants"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for enabling closed loop wallet in preconditions : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True, closedloop_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_side_menu_eng()
            logger.debug(f"clicked on side menu")
            home_page.click_on_eze_wallet()
            logger.debug(f"clicked on ezewallet option from the side menu")

            query = f"select * from account where entity_id ='{app_username}'"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query, db_name='closedloop')
            logger.debug(f"Query result obtained from account table : {result}")
            agent_balance_db = result['balance'].values[0]
            logger.debug(f"fetched agent balance from db :{agent_balance_db}")

            query = f"select * from wallet_txn order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from wallet_txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query, db_name='closedloop')
            agent_last_top_up_db = result['amount'].values[0]
            logger.debug(f"fetched agent last top up  from db :{agent_last_top_up_db}")
            agent_last_top_up_time_db = result['created_time'].values[0]
            logger.debug(f"fetched agent last top up on from db :{agent_last_top_up_time_db}")

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
                date_and_time = date_time_converter.to_app_format(agent_last_top_up_time_db)
                expected_app_values = {
                    "agent_balance": f"{agent_balance_db:,}",
                    "last_top_up": f"{agent_last_top_up_db:,}".rstrip("0").rstrip("."),
                    "last_top_up_on": date_and_time.replace(',', ''),
                    "ph_no": app_username
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                agent_balance = home_page.fetch_agent_balance()
                agent_last_top_up = home_page.fetch_last_top_up()
                agent_last_top_up_time = home_page.fetch_last_top_up_on()
                agent_mobile_number = home_page.fetch_mobile_no()

                actual_app_values = {
                    "agent_balance": agent_balance.split(' ')[1],
                    "last_top_up": agent_last_top_up.split(' ')[1],
                    "last_top_up_on": agent_last_top_up_time,
                    "ph_no": agent_mobile_number
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation--------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
