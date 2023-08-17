import sys
from time import sleep
import pytest
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.Portal_TransHistoryPage import get_transaction_details_for_portal
from PageFactory.sa.App_CardPage import CardPage
from PageFactory.sa.App_PaymentPage import PaymentPage
from PageFactory.mpos.App_HomePage import HomePage
from PageFactory.mpos.App_LoginPage import LoginPage
from PageFactory.sa.App_TransHistoryPage import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, ResourceAssigner, date_time_converter, APIProcessor, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_card():
    """
        Sub Feature Code: authorised txn, void an authorised txn, failed txn with error message
        Sub Feature Description: Verification of authorised txn, void an authorised txn and failed txn with error message
        TC naming code description:
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

        query = "select * from terminal_info where org_code='" + org_code + "' and status = 'ACTIVE' and acquirer_code='HDFC' and payment_gateway='DUMMY'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        device_serial = result["device_serial"].iloc[0]

        testsuite_teardown.revert_card_payment_settings_default(org_code, '', portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["cardPaymentEnabled"] = "true"

        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
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
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = 455
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_for_card(amount, order_id, device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card(amount, order_id, device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(app_driver)
            card_page.select_cardtype("HDFC_EMVCTLS_DEBIT_RUPAY")

            # ============ card txn based on specific amounts for diff failed scenarios ======================
            # error_code = card_page.fetch_error_code_text()
            # error_mssg = card_page.fetch_error_message_text()

            # print(error_code)
            # print(error_mssg)
            # card_page.click_on_ok_error_mssg()

            sleep(2)
            payment_page.click_on_proceed_homepage()

            query = "select * from txn where org_code ='" + str(
                org_code) + "' AND payment_mode = 'CARD' AND device_serial='"+device_serial+"' AND external_ref='"+order_id+"' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time = result['created_time'].values[0]
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {txn_created_time}")

            rrn = result['rr_number'].values[0]
            auth_code = result['auth_code'].values[0]
            batch_number = result['batch_number'].values[0]
            # tid = result['tid'].values[0]
            # mid = result['mid'].values[0]
            customer_name = result['customer_name'].values[0]
            amount_db = result['amount'].values[0]
            payment_mode_db = result['payment_mode'].values[0]
            payment_status_db = result['status'].values[0]
            payment_state_db = result['state'].values[0]
            acquirer_code_db = result['acquirer_code'].values[0]
            bank_name_db = result['bank_name'].values[0]
            mid_db = result['mid'].values[0]
            tid_db = result['tid'].values[0]
            payment_gateway_db = result['payment_gateway'].values[0]
            settlement_status_db = result['settlement_status'].values[0]

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
            date_and_time = date_time_converter.to_app_format(txn_created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "NIROSHA V",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*3493 CTLS"
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
                # ============== Void an authorized txn ====================
                # txn_history_page.click_on_void_card_txn()

                payment_status = txn_history_page.fetch_txn_status_text()
                payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_auth_code = txn_history_page.fetch_auth_code_text()
                app_batch_no = txn_history_page.fetch_batch_number_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_mid = txn_history_page.fetch_mid_text()
                app_tid = txn_history_page.fetch_tid_text()
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rr_number": app_rrn,
                    "auth_code": app_auth_code,
                    "customer_name": app_customer_name,
                    "batch_number": app_batch_no,
                    "mid": app_mid,
                    "tid": app_tid,
                    "card_type_desc": app_card_type_desc
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
                date = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {"pmt_status": "AUTHORIZED",
                                       "txn_amt": float(amount),
                                       "pmt_mode": "CARD",
                                       "pmt_state": "AUTHORIZED",
                                       "rrn": str(rrn),
                                       "settle_status": "PENDING",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid,
                                       "org_code": org_code,
                                       "auth_code": auth_code,
                                       "date": date}
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

                actual_api_values = {"pmt_status": status_api,
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
                                     "auth_code": auth_code_api,
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
                expected_db_values = {"txn_amt": float(amount),
                                      "pmt_mode": "CARD",
                                      "pmt_status": "AUTHORIZED",
                                      "pmt_state": "AUTHORIZED",
                                      "acquirer_code": "HDFC",
                                      "mid": mid, "tid": tid,
                                      "pmt_gateway": "DUMMY",
                                      "settle_status": "PENDING"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {"txn_amt": amount_db,
                                    "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db,
                                    "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
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
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']
                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                expected_values = {'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn), 'merchant_info':'Cardtxn, Bangalore, Bangalore',
                                   'SALE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                                   'AUTH CODE': auth_code, 'BATCH NO':'7', 'CARD TYPE':'RUPAY', 'AUTH CODE':auth_code,
                                   'payment_option': 'DEBIT SALE'}
                receipt_validator.perform_charge_slip_validations(txn_id,
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_card_sale_tip():
    """
        Sub Feature Code: authorised txn with tip amount
        Sub Feature Description: Verification of authorised txn with tip amount
        TC naming code description:
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

        query = "select * from terminal_info where org_code='" + org_code + "' and status = 'ACTIVE' and acquirer_code='HDFC' and payment_gateway='DUMMY'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        device_serial = result["device_serial"].iloc[0]

        testsuite_teardown.revert_card_payment_settings_default(org_code, '', portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["tipEnabled"] = "true"
        api_details["RequestBody"]["settings"]["tipPercentage"] = "10"

        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
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
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = 455
            order_id = datetime.now().strftime('%m%d%H%M%S')
            tip_amt = 4
            home_page.enter_tip_amount_and_order_number_for_card(amount, order_id, tip_amt, device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered tip_amt is : {tip_amt}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed_card_with_tip(amount, order_id, tip_amt, device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(app_driver)
            card_page.select_cardtype("HDFC_EMVCTLS_DEBIT_RUPAY")

            sleep(2)
            payment_page.click_on_proceed_homepage()

            query = "select * from txn where org_code ='" + str(
                org_code) + "' AND payment_mode = 'CARD' AND device_serial='"+device_serial+"' AND external_ref='"+order_id+"' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {txn_created_time}")
            txn_id = result['id'].values[0]
            logger.debug(f"Txn_id: {txn_id}")

            rrn = result['rr_number'].values[0]
            auth_code = result['auth_code'].values[0]
            batch_number = result['batch_number'].values[0]
            # tid = result['tid'].values[0]
            # mid = result['mid'].values[0]
            customer_name = result['customer_name'].values[0]
            amount_db = result['amount'].values[0]
            payment_mode_db = result['payment_mode'].values[0]
            payment_status_db = result['status'].values[0]
            payment_state_db = result['state'].values[0]
            acquirer_code_db = result['acquirer_code'].values[0]
            bank_name_db = result['bank_name'].values[0]
            mid_db = result['mid'].values[0]
            tid_db = result['tid'].values[0]
            payment_gateway_db = result['payment_gateway'].values[0]
            settlement_status_db = result['settlement_status'].values[0]
            tip_amt_db = result['amount_additional'].values[0]
            amt_original_db = result['amount_original'].values[0]

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
            date_and_time = date_time_converter.to_app_format(txn_created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount+tip_amt),
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "NIROSHA V",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*3493 CTLS",
                    "tip_amt": "{:.2f}".format(tip_amt),
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_auth_code = txn_history_page.fetch_auth_code_text()
                app_batch_no = txn_history_page.fetch_batch_number_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_mid = txn_history_page.fetch_mid_text()
                app_tid = txn_history_page.fetch_tid_text()
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                app_tip_amt = txn_history_page.fetch_tip_amt_text()

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rr_number": app_rrn,
                    "auth_code": app_auth_code,
                    "customer_name": app_customer_name,
                    "batch_number": app_batch_no,
                    "mid": app_mid,
                    "tid": app_tid,
                    "card_type_desc": app_card_type_desc,
                    "tip_amt": app_tip_amt.split(' ')[1],
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
                date = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {"pmt_status": "AUTHORIZED",
                                       "txn_amt": float(amount+tip_amt),
                                       "tip_amt": float(tip_amt),
                                       "amt_original": float(amount),
                                       "pmt_mode": "CARD",
                                       "pmt_state": "AUTHORIZED",
                                       "rrn": str(rrn),
                                       "settle_status": "PENDING",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid,
                                       "org_code": org_code,
                                       "auth_code": auth_code,
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
                tip_amt_api = response["amountAdditional"]
                amt_original_api = response["amountOriginal"]
                amount_api = float(response["amount"])

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "tip_amt": tip_amt_api,
                                     "amt_original": amt_original_api,
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
                                     "auth_code": auth_code_api,
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
                expected_db_values = {"txn_amt": float(amount+tip_amt),
                                      "amt_original": float(amount),
                                      "tip_amt": str(tip_amt)+".0",
                                      "pmt_mode": "CARD",
                                      "pmt_status": "AUTHORIZED",
                                      "pmt_state": "AUTHORIZED",
                                      "acquirer_code": "HDFC",
                                      "mid": mid, "tid": tid,
                                      "pmt_gateway": "DUMMY",
                                      "settle_status": "PENDING"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {"txn_amt": amount_db,
                                    "amt_original": amt_original_db,
                                    "tip_amt": str(tip_amt_db),
                                    "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db,
                                    "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db
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
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(amount+tip_amt),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']
                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                expected_values = {'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn), 'merchant_info':'Cardtxn, Bangalore, Bangalore',
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   "TIP AMOUNT:":"Rs."+str(tip_amt)+".00",
                                   "TOTAL AMOUNT:": "Rs."+str(amount+tip_amt)+".00",
                                   'date': txn_date, 'time': txn_time,
                                   'AUTH CODE': auth_code, 'BATCH NO': batch_number,
                                   'CARD TYPE':'RUPAY',
                                   'payment_option': 'TIP ADJUSTED SALE'}
                receipt_validator.perform_charge_slip_validations(txn_id,
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_card_sale_cashback():
    """
        Sub Feature Code: authorised txn with cashback
        Sub Feature Description: Verification of authorised txn with cashback
        TC naming code description:
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

        query = "select * from terminal_info where org_code='" + org_code + "' and status = 'ACTIVE' and acquirer_code='HDFC' " \
                                                                            "and payment_gateway='DUMMY'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        device_serial = result["device_serial"].iloc[0]

        testsuite_teardown.revert_card_payment_settings_default(org_code, '', portal_username, portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["cashBackOption"] = 1
        api_details["RequestBody"]["settings"]["minCashBackAmount"] = "200"
        api_details["RequestBody"]["settings"]["maxCashBackAmount"] = "3000"

        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
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
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_cash_at_pos()
            home_page.click_cash_at_pos_with_sale_switch()
            amount = 300
            cashback_Amt = 200
            home_page.enter_cash_at_pos_amount(cashback_Amt)
            home_page.enter_cash_at_pos_sale_amount(amount)
            app_driver.back()
            home_page.click_pay_now_button()
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_order_number_for_card(order_id, device_serial)
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            card_page = CardPage(app_driver)
            card_page.select_cardtype("IDFC_MSR_DEBIT_VISA")

            sleep(2)
            payment_page.click_on_proceed_homepage()

            query = "select * from txn where org_code ='" + str(
                org_code) + "' AND payment_mode = 'CARD' AND external_ref='"+order_id+"' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {txn_created_time}")
            txn_id = result['id'].values[0]
            logger.debug(f"Txn_id: {txn_id}")

            rrn = result['rr_number'].values[0]
            auth_code = result['auth_code'].values[0]
            batch_number = result['batch_number'].values[0]
            payment_mode_db = result['payment_mode'].values[0]
            payment_status_db = result['status'].values[0]
            payment_state_db = result['state'].values[0]
            acquirer_code_db = result['acquirer_code'].values[0]
            bank_name_db = result['bank_name'].values[0]
            mid_db = result['mid'].values[0]
            tid_db = result['tid'].values[0]
            payment_gateway_db = result['payment_gateway'].values[0]
            settlement_status_db = result['settlement_status'].values[0]
            amt_original_db = result['amount_original'].values[0]
            amt_cashback_db = result['amount_cash_back'].values[0]
            amount_db = result['amount'].values[0]

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
            date_and_time = date_time_converter.to_app_format(txn_created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount+cashback_Amt),
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "rr_number": rrn,
                    "auth_code": auth_code,
                    "customer_name": "NIROSHA V",
                    "batch_number": batch_number,
                    "mid": mid,
                    "tid": tid,
                    "card_type_desc": "*3493 Swipe with PIN ByPass",
                    "cash_amt": "{:.2f}".format(cashback_Amt),
                    "sale_amt": "{:.2f}".format(amount),
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_auth_code = txn_history_page.fetch_auth_code_text()
                app_batch_no = txn_history_page.fetch_batch_number_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_mid = txn_history_page.fetch_mid_text()
                app_tid = txn_history_page.fetch_tid_text()
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                app_cash_amt = txn_history_page.fetch_cash_amt_text()
                app_sale_amt = txn_history_page.fetch_sale_amt_text()

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rr_number": app_rrn,
                    "auth_code": app_auth_code,
                    "customer_name": app_customer_name,
                    "batch_number": app_batch_no,
                    "mid": app_mid,
                    "tid": app_tid,
                    "card_type_desc": app_card_type_desc,
                    "cash_amt": app_cash_amt.split(' ')[1],
                    "sale_amt": app_sale_amt.split(' ')[1],
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
                date = date_time_converter.db_datetime(txn_created_time)
                expected_api_values = {"pmt_status": "AUTHORIZED",
                                       "txn_amt": float(amount+cashback_Amt),
                                       "cash_amt": float(cashback_Amt),
                                       "sale_amt": float(amount),
                                       "pmt_mode": "CARD",
                                       "pmt_state": "AUTHORIZED",
                                       "rrn": str(rrn),
                                       "settle_status": "PENDING",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "CASH_BACK",
                                       "mid": mid, "tid": tid,
                                       "org_code": org_code,
                                       "auth_code": auth_code,
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
                cash_amt_api = response["amountCashBack"]
                sale_amt_api = response["amountOriginal"]
                amount_api = float(response["amount"])

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "cash_amt": cash_amt_api,
                                     "sale_amt": sale_amt_api,
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
                                     "auth_code": auth_code_api,
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
                expected_db_values = {"txn_amt": float(amount+cashback_Amt),
                                      "sale_amt": float(amount),
                                      "cash_amt": str(cashback_Amt)+".0",
                                      "pmt_mode": "CARD",
                                      "pmt_status": "AUTHORIZED",
                                      "pmt_state": "AUTHORIZED",
                                      "acquirer_code": "HDFC",
                                      "mid": mid, "tid": tid,
                                      "pmt_gateway": "DUMMY",
                                      "settle_status": "PENDING"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {"txn_amt": amount_db,
                                    "sale_amt": amt_original_db,
                                    "cash_amt": str(amt_cashback_db),
                                    "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db,
                                    "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db
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
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:.2f}".format(amount+cashback_Amt),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']
                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                expected_values = {'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn), 'merchant_info':'Cardtxn, Bangalore, Bangalore',
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   "TIP AMOUNT:":"Rs."+str(cashback_Amt)+".00",
                                   "TOTAL AMOUNT:": "Rs."+str(amount+cashback_Amt)+".00",
                                   'date': txn_date, 'time': txn_time,
                                   'BATCH NO': batch_number,
                                   'CARD TYPE':'RUPAY', 'AUTH CODE':auth_code}
                receipt_validator.perform_charge_slip_validations(txn_id,
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