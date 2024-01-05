import random
import sys
import time
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter, receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_242():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Failed_Via_UPI_Callback_After_Expiry_AutoRefund_Enabled_RAZORPAY
    Sub Feature Description: Performing a  UPI Collect failed callback via RAZORPAY after expiry the  when auto refund is enabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 242: TC_242
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(
            f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        upi_account_id = result['pgMerchantId'].values[0]
        tid = result['virtual_tid'].values[0]
        mid = result['virtual_mid'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")
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
            amount = random.randint(601, 700)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
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

            query = f"select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '{org_code}';"
            logger.debug(f"Query to fetch txn timeout from the DB : {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                org_setting_value = int(result['setting_value'].values[0])
                logger.info(f"txn timeout for {org_code} is {org_setting_value}")
            except Exception as e:
                org_setting_value = None
                logger.error(e)

            query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = 'EZETAP'"
            logger.debug(f"Query to fetch Txn_id from the DB : {query1}")
            try:
                defaultValue = DBProcessor.getValueFromDB(query1)
                setting_value = int(defaultValue['setting_value'].values[0])
                logger.info(f"txn timeout attempt is: {setting_value}")
            except Exception as e:
                setting_value = None
                logger.error(e)
            except Exception as e:
                setting_value = None
                logger.error(e)
            except Exception as e:
                logger.error(e)

            if org_setting_value:
                logger.info(f"Value for max upi attempt is: {org_setting_value} min.")
                time.sleep(3 + (org_setting_value * 60))
            else:
                logger.info(f"Value for Ezetap org is: {org_setting_value} min.")
                time.sleep(3 + (setting_value * 60))

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            query = f"select * from upi_txn where org_code = '{org_code}' AND txn_id = '{txn_id}';"
            logger.debug(f"Query to fetch txn_ref from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.debug(f"Query result, txn_ref : {txn_ref} and txn_ref_3 : {txn_ref_3}")
            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount_api = amount * 100

            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "base_amount": amount_api,
                            "status": "failed",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where id = '{str(txn_id)}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            status_db = result["status"].iloc[0]
            payment_mode_db = result["payment_mode"].iloc[0]
            amount_db = int(result["amount"].iloc[0])
            state_db = result["state"].iloc[0]
            payment_gateway_db = result["payment_gateway"].iloc[0]
            acquirer_code_db = result["acquirer_code"].iloc[0]
            bank_code_db = result["bank_code"].iloc[0]
            settlement_status_db = result["settlement_status"].iloc[0]
            tid_db = result['tid'].values[0]
            mid_db = result['mid'].values[0]
            logger.debug(
                f"Fetching status_db,payment_mode_db, amount_db, state_db, payment_gateway_db, acquirer_code_db, bank_code_db, settlement_status_db, mid_db, tid_db from database for "
                f"current merchant:{status_db},{payment_mode_db}, {amount_db}, {state_db}, {payment_gateway_db}, {acquirer_code_db}, {bank_code_db}, {settlement_status_db}, {mid_db}, {tid_db}")
            # ---------------------------------------------------------------------------------------------------------
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
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }

                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payer_name = txn_history_page.fetch_payer_name_text()
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
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
                    "pmt_status": "FAILED",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
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
                amount_api = int(response["amount"])
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

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api,
                                     "mid": mid_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api)
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
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
                    "txn_amt": amount,
                    "upi_txn_status": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

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
                    "auth_code": "-" if auth_code is None else auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal
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
def test_common_100_103_243():
    """
    Sub Feature Code: UI_Common_PM_UPI_success_callback_before_expiry_AutoRefund_Disabled_RAZORPAY
    Sub Feature Description: Performing a  UPI Collect success callback via RAZORPAY before expiry when auto refund is Disabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 243: TC_243
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(
            f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        upi_account_id = result['pgMerchantId'].values[0]
        tid = result['virtual_tid'].values[0]
        mid = result['virtual_mid'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")
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
            amount = random.randint(601, 700)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
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
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            query = f"select * from upi_txn where org_code = '{org_code}' AND txn_id = '{txn_id}';"
            logger.debug(f"Query to fetch txn_ref from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            logger.debug(f"Query result, txn_ref : {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.debug(f"Query result, txn_ref_3 : {txn_ref_3}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount_api = amount * 100
            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "base_amount": amount_api,
                            "status": "captured",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            status_db = result["status"].iloc[0]
            payment_mode_db = result["payment_mode"].iloc[0]
            amount_db = int(result["amount"].iloc[0])
            state_db = result["state"].iloc[0]
            payment_gateway_db = result["payment_gateway"].iloc[0]
            acquirer_code_db = result["acquirer_code"].iloc[0]
            bank_code_db = result["bank_code"].iloc[0]
            settlement_status_db = result["settlement_status"].iloc[0]
            tid_db = result['tid'].values[0]
            mid_db = result['mid'].values[0]
            logger.debug(
                f"Fetching status_db,payment_mode_db, amount_db, state_db, payment_gateway_db, acquirer_code_db, bank_code_db, settlement_status_db, mid_db, tid_db from database for "
                f"current merchant:{status_db},{payment_mode_db}, {amount_db}, {state_db}, {payment_gateway_db}, {acquirer_code_db}, {bank_code_db}, {settlement_status_db}, {mid_db}, {tid_db}")
            # ----------------------------------------------------------------------------------------------------------
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
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn),
                    "date": date_and_time,
                }

                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                app_txn_id = txn_history_page.fetch_txn_id_text()
                app_amount = txn_history_page.fetch_txn_amount_text()
                app_rrn = txn_history_page.fetch_RRN_text()
                app_customer_name = txn_history_page.fetch_customer_name_text()
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                app_payer_name = txn_history_page.fetch_payer_name_text()
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "rrn": str(app_rrn),
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
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
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
                amount_api = int(response["amount"])
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

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api,
                                     "mid": mid_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api)
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
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
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

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
                    "rrn": rrn,
                    "auth_code": "-" if auth_code is None else auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
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
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal
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
                expected_charge_slip_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                               'RRN': str(rrn),
                                               'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                               'date': txn_date, 'time': txn_time,
                                               }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id,
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
def test_common_100_103_244():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Success_Via_Two_UPI_Callback_RAZORPAY
    Sub Feature Description: Verification of a two upi callback after expiry via RAZORPAY when auto refund is disabled.
    TC naming code description:
    100: Payment Method, 103: RemotePay, 244: TC_244
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(
            f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        upi_account_id = result['pgMerchantId'].values[0]
        tid = result['virtual_tid'].values[0]
        mid = result['virtual_mid'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")
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
            amount = random.randint(601, 700)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
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

                query = f"select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '{str(org_code)}';"
                logger.debug(f"Query to fetch max Attempts from the DB : {query}")
                try:
                    result = DBProcessor.getValueFromDB(query)
                    print("result: ", result)
                    print("type of result: ", type(result))
                    org_setting_value = int(result['setting_value'].values[0])
                    logger.info(f"max upi attempt for {org_code} is {org_setting_value}")
                except Exception as e:
                    org_setting_value = None
                    logger.error(e)

                query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = 'EZETAP'"
                logger.debug(f"Query to fetch Txn_id from the DB : {query1}")
                try:
                    defaultValue = DBProcessor.getValueFromDB(query1)
                    setting_value = int(defaultValue['setting_value'].values[0])
                    logger.info(f"max upi attempt is: {setting_value}")
                except NameError as e:
                    setting_value = None
                    logger.error(e)
                except IndexError as e:
                    setting_value = None
                    logger.error(e)
                except Exception as e:
                    logger.error(e)

                if org_setting_value:
                    logger.info(f"Value for max upi attempt is: {org_setting_value} min.")
                    time.sleep(3 + (org_setting_value * 60))
                else:
                    logger.info(f"Value for Ezetap org is: {org_setting_value} min.")
                    time.sleep(3 + (setting_value * 60))

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")

            query = f"select * from upi_txn where org_code = '{org_code}' AND txn_id = '{original_txn_id}';"
            logger.debug(f"Query to fetch txn_ref from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            logger.debug(f"Query result, txn_ref : {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.debug(f"Query result, txn_ref_3 : {txn_ref_3}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount_api = amount * 100
            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "base_amount": amount_api,
                            "status": "captured",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_1 = result['id'].values[0]
            logger.debug(f"Query result, txn_id_new : {new_txn_id_1}")

            logger.debug(f"Generating razorpay_callback_generator_HMAC for 2nd CallBack")
            rrn_2 = str(random.randint(1000000000000, 9999999999999))
            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "base_amount": amount_api,
                            "status": "captured",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn_2
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api_2 is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_2 = result['id'].values[0]
            logger.debug(f"Query result, txn_id_new_2 : {new_txn_id_2}")

            query = f"select * from txn where id = '{original_txn_id}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            orig_txn_type = result['txn_type'].values[0]
            orig_created_time = result['created_time'].values[0]

            query = f"select * from txn where id = '{new_txn_id_1}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_customer_name_1 = result['customer_name'].values[0]
            new_txn_payer_name_1 = result['payer_name'].values[0]
            new_txn_type_1 = result['txn_type'].values[0]
            new_txn_created_time_1 = result['created_time'].values[0]
            new_txn_created_time_api_1 = result['created_time'].values[0]

            query = f"select * from txn where id = '{new_txn_id_2}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_customer_name_2 = result['customer_name'].values[0]
            new_txn_payer_name_2 = result['payer_name'].values[0]
            new_txn_type_2 = result['txn_type'].values[0]
            logger.info(f"New txn type is: {new_txn_type_2}")
            new_txn_created_time_api = result['created_time'].values[0]
            logger.info(f"New txn_created_time time for api is : {new_txn_created_time_api}")
            new_txn_created_time_app = result['created_time'].values[0]
            logger.info(f"New created time for app is : {new_txn_created_time_app}")
            new_auth_code = result['auth_code'].values[0]
            logger.info(f"New created time for app is : {new_auth_code}")
            new_txn_created_time_2 = result['created_time'].values[0]
            logger.info(f"New created time for app is : {new_txn_created_time_2}")
            # ---------------------------------------------------------------------------------------------------
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
                date_and_time = date_time_converter.to_app_format(orig_created_time)
                new_txn_date_and_time_1 = date_time_converter.to_app_format(new_txn_created_time_1)
                new_txn_date_and_time_2 = date_time_converter.to_app_format(new_txn_created_time_app)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    "customer_name": original_customer_name,
                    "payer_name": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount) + ".00",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id_1,
                    "rrn_2": str(rrn),
                    "customer_name_2": new_txn_customer_name_1,
                    "payer_name_2": new_txn_payer_name_1,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": new_txn_date_and_time_1,

                    "pmt_mode_3": "UPI",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": str(amount) + ".00",
                    "settle_status_3": "SETTLED",
                    "txn_id_3": new_txn_id_2,
                    "rrn_3": str(rrn_2),
                    "customer_name_3": new_txn_customer_name_2,
                    "payer_name_3": new_txn_payer_name_2,
                    "order_id_3": order_id,
                    "pmt_msg_3": "PAYMENT SUCCESSFUL",
                    "date_3": new_txn_date_and_time_2,

                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                app_amount = transactions_history_page.fetch_txn_amount_text()
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                app_payer_name = transactions_history_page.fetch_payer_name_text()
                app_order_id = transactions_history_page.fetch_order_id_text()
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id_1)
                app_payment_status_1 = transactions_history_page.fetch_txn_status_text()
                app_payment_status_1 = app_payment_status_1.split(':')[1]
                app_payment_mode_1 = transactions_history_page.fetch_txn_type_text()
                app_txn_id_1 = transactions_history_page.fetch_txn_id_text()
                app_amount_1 = transactions_history_page.fetch_txn_amount_text()
                app_rrn_1 = transactions_history_page.fetch_RRN_text()
                app_date_and_time_1 = transactions_history_page.fetch_date_time_text()
                app_settlement_status_1 = transactions_history_page.fetch_settlement_status_text()
                app_customer_name_1 = transactions_history_page.fetch_customer_name_text()
                app_payer_name_1 = transactions_history_page.fetch_payer_name_text()
                app_order_id_1 = transactions_history_page.fetch_order_id_text()

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id_2)
                app_payment_status_2 = transactions_history_page.fetch_txn_status_text()
                app_payment_status_2 = app_payment_status_2.split(':')[1]
                app_payment_mode_2 = transactions_history_page.fetch_txn_type_text()
                app_txn_id_2 = transactions_history_page.fetch_txn_id_text()
                app_amount_2 = transactions_history_page.fetch_txn_amount_text()
                app_rrn_2 = transactions_history_page.fetch_RRN_text()
                app_date_and_time_2 = transactions_history_page.fetch_date_time_text()
                app_settlement_status_2 = transactions_history_page.fetch_settlement_status_text()
                app_customer_name_2 = transactions_history_page.fetch_customer_name_text()
                app_payer_name_2 = transactions_history_page.fetch_payer_name_text()
                app_order_id_2 = transactions_history_page.fetch_order_id_text()
                app_payment_msg_2 = transactions_history_page.fetch_txn_payment_msg_text()

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,

                    "pmt_mode_2": app_payment_mode_1,
                    "pmt_status_2": app_payment_status_1,
                    "txn_amt_2": app_amount_1.split(' ')[1],
                    "settle_status_2": app_settlement_status_1,
                    "txn_id_2": app_txn_id_1,
                    "rrn_2": str(app_rrn_1),
                    "customer_name_2": app_customer_name_1,
                    "payer_name_2": app_payer_name_1,
                    "order_id_2": app_order_id_1,
                    "date_2": app_date_and_time_1,
                    "pmt_msg_2": app_payment_msg_2,

                    "pmt_mode_3": app_payment_mode_2,
                    "pmt_status_3": app_payment_status_2,
                    "txn_amt_3": app_amount_2.split(' ')[1],
                    "settle_status_3": app_settlement_status_2,
                    "txn_id_3": app_txn_id_2,
                    "rrn_3": str(app_rrn_2),
                    "customer_name_3": app_customer_name_2,
                    "payer_name_3": app_payer_name_2,
                    "order_id_3": app_order_id_2,
                    "pmt_msg_3": app_payment_msg_2,
                    "date_3": app_date_and_time_2,
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(orig_created_time)
                new_txn_date_1 = date_time_converter.db_datetime(new_txn_created_time_api_1)
                new_txn_date_2 = date_time_converter.db_datetime(new_txn_created_time_api)
                expected_api_values = {"pmt_status": "FAILED",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "FAILED",
                                       "settle_status": "FAILED",
                                       "acquirer_code": "RAZORPAY",
                                       "issuer_code": "RAZORPAY",
                                       "txn_type": orig_txn_type,
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code,

                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": amount,
                                       "pmt_mode_2": "UPI",
                                       "pmt_state_2": "SETTLED",
                                       "new_rrn_1": str(rrn),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "RAZORPAY",
                                       "issuer_code_2": "RAZORPAY",
                                       "txn_type_2": new_txn_type_1,
                                       "mid_2": mid,
                                       "tid_2": tid,
                                       "org_code_2": org_code,

                                       "pmt_status_3": "AUTHORIZED",
                                       "txn_amt_3": amount,
                                       "pmt_mode_3": "UPI",
                                       "pmt_state_3": "SETTLED",
                                       "new_rrn_2": str(rrn_2),
                                       "settle_status_3": "SETTLED",
                                       "acquirer_code_3": "RAZORPAY",
                                       "issuer_code_3": "RAZORPAY",
                                       "txn_type_3": new_txn_type_2,
                                       "mid_3": mid,
                                       "tid_3": tid,
                                       "org_code_3": org_code,
                                       "date": date,
                                       "date_2": new_txn_date_1,
                                       "date_3": new_txn_date_2
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])
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

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == new_txn_id_1][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                new_txn_status_api_1 = response["status"]
                new_txn_amount_api_1 = int(response["amount"])
                new_payment_mode_api_1 = response["paymentMode"]
                new_txn_state_api_1 = response["states"][0]
                new_txn_rrn_api_1 = response["rrNumber"]
                new_txn_settlement_status_api_1 = response["settlementStatus"]
                new_txn_issuer_code_api_1 = response["issuerCode"]
                new_txn_acquirer_code_api_1 = response["acquirerCode"]
                new_txn_orgCode_api_1 = response["orgCode"]
                new_txn_mid_api_1 = response["mid"]
                new_txn_tid_api_1 = response["tid"]
                new_txn_txn_type_api_1 = response["txnType"]
                new_txn_date_api_1 = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == new_txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                new_txn_status_api_2 = response["status"]
                new_txn_amount_api_2 = int(response["amount"])
                new_payment_mode_api_2 = response["paymentMode"]
                new_txn_state_api_2 = response["states"][0]
                new_txn_rrn_api_2 = response["rrNumber"]
                new_txn_settlement_status_api_2 = response["settlementStatus"]
                new_txn_issuer_code_api_2 = response["issuerCode"]
                new_txn_acquirer_code_api_2 = response["acquirerCode"]
                new_txn_orgCode_api_2 = response["orgCode"]
                new_txn_mid_api_2 = response["mid"]
                new_txn_tid_api_2 = response["tid"]
                new_txn_type_api_2 = response["txnType"]
                new_txn_date_api_2 = response["createdTime"]
                #
                actual_api_values = {"pmt_status": status_api,
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

                                     "pmt_status_2": new_txn_status_api_1,
                                     "txn_amt_2": new_txn_amount_api_1,
                                     "pmt_mode_2": new_payment_mode_api_1,
                                     "pmt_state_2": new_txn_state_api_1,
                                     "new_rrn_1": str(new_txn_rrn_api_1),
                                     "settle_status_2": new_txn_settlement_status_api_1,
                                     "acquirer_code_2": new_txn_acquirer_code_api_1,
                                     "issuer_code_2": new_txn_issuer_code_api_1,
                                     "txn_type_2": new_txn_txn_type_api_1,
                                     "mid_2": new_txn_mid_api_1,
                                     "tid_2": new_txn_tid_api_1,
                                     "org_code_2": new_txn_orgCode_api_1,

                                     "pmt_status_3": new_txn_status_api_2,
                                     "txn_amt_3": new_txn_amount_api_2,
                                     "pmt_mode_3": new_payment_mode_api_2,
                                     "pmt_state_3": new_txn_state_api_2,
                                     "new_rrn_2": str(new_txn_rrn_api_2),
                                     "settle_status_3": new_txn_settlement_status_api_2,
                                     "acquirer_code_3": new_txn_acquirer_code_api_2,
                                     "issuer_code_3": new_txn_issuer_code_api_2,
                                     "txn_type_3": new_txn_type_api_2,
                                     "mid_3": new_txn_mid_api_2,
                                     "tid_3": new_txn_tid_api_2,
                                     "org_code_3": new_txn_orgCode_api_2,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "date_2": date_time_converter.from_api_to_datetime_format(
                                         new_txn_date_api_1),
                                     "date_3": date_time_converter.from_api_to_datetime_format(
                                         new_txn_date_api_2)

                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {"pmt_status": "FAILED",
                                      "pmt_state": "FAILED",
                                      "pmt_mode": "UPI",
                                      "txn_amt": amount,
                                      "upi_txn_status": "FAILED",
                                      "settle_status": "FAILED",
                                      "acquirer_code": "RAZORPAY",
                                      "bank_code": "RAZORPAY",
                                      "upi_txn_type": "COLLECT",
                                      "upi_bank_code": "RAZORPAY_PSP",
                                      "pmt_gateway": "RAZORPAY",
                                      "upi_mc_id": upi_mc_id,

                                      "pmt_status_2": "AUTHORIZED",
                                      "pmt_state_2": "SETTLED",
                                      "pmt_mode_2": "UPI",
                                      "txn_amt_2": amount,
                                      "upi_txn_status_2": "AUTHORIZED",
                                      "settle_status_2": "SETTLED",
                                      "acquirer_code_2": "RAZORPAY",
                                      "bank_code_2": "RAZORPAY",
                                      "pmt_gateway_2": "RAZORPAY",
                                      "upi_txn_type_2": "COLLECT",
                                      "upi_bank_code_2": "RAZORPAY_PSP",
                                      "upi_mc_id_2": upi_mc_id,

                                      "pmt_status_3": "AUTHORIZED",
                                      "pmt_state_3": "SETTLED",
                                      "pmt_mode_3": "UPI",
                                      "txn_amt_3": amount,
                                      "upi_txn_status_3": "AUTHORIZED",
                                      "settle_status_3": "SETTLED",
                                      "acquirer_code_3": "RAZORPAY",
                                      "bank_code_3": "RAZORPAY",
                                      "pmt_gateway_3": "RAZORPAY",
                                      "upi_txn_type_3": "COLLECT",
                                      "upi_bank_code_3": "RAZORPAY_PSP",
                                      "upi_mc_id_3": upi_mc_id,
                                      "mid": mid,
                                      "tid": tid,
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "mid_3": mid,
                                      "tid_3": tid
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = f"select * from txn where id='{new_txn_id_1}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_1 = result["status"].iloc[0]
                new_txn_payment_mode_db_1 = result["payment_mode"].iloc[0]
                new_txn_amount_db_1 = int(
                    result["amount"].iloc[0])
                new_txn_state_db_1 = result["state"].iloc[0]
                new_txn_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_1 = result["settlement_status"].iloc[0]
                new_txn_tid_db_1 = result['tid'].values[0]
                new_txn_mid_db_1 = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{new_txn_id_1}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_1 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = f"select * from txn where id='{new_txn_id_2}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_2 = result["status"].iloc[0]
                new_txn_payment_mode_db_2 = result["payment_mode"].iloc[0]
                new_txn_amount_db_2 = int(
                    result["amount"].iloc[0])
                new_txn_state_db_2 = result["state"].iloc[0]
                new_txn_payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_2 = result["settlement_status"].iloc[0]
                new_txn_tid_db_2 = result['tid'].values[0]
                new_txn_mid_db_2 = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{new_txn_id_2}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_2 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_2 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_mc_id": upi_mc_id_db,

                    "pmt_status_2": new_txn_status_db_1,
                    "pmt_state_2": new_txn_state_db_1,
                    "pmt_mode_2": new_txn_payment_mode_db_1,
                    "txn_amt_2": new_txn_amount_db_1,
                    "upi_txn_status_2": new_txn_upi_status_db_1,
                    "settle_status_2": new_txn_settlement_status_db_1,
                    "acquirer_code_2": new_txn_acquirer_code_db_1,
                    "bank_code_2": new_txn_bank_code_db_1,
                    "pmt_gateway_2": new_txn_payment_gateway_db_1,
                    "upi_txn_type_2": new_txn_upi_txn_type_db_1,
                    "upi_bank_code_2": new_txn_upi_bank_code_db_1,
                    "upi_mc_id_2": new_txn_upi_mc_id_db_1,

                    "pmt_status_3": new_txn_status_db_2,
                    "pmt_state_3": new_txn_state_db_2,
                    "pmt_mode_3": new_txn_payment_mode_db_2,
                    "txn_amt_3": new_txn_amount_db_2,
                    "upi_txn_status_3": new_txn_upi_status_db_2,
                    "settle_status_3": new_txn_settlement_status_db_2,
                    "acquirer_code_3": new_txn_acquirer_code_db_2,
                    "bank_code_3": new_txn_bank_code_db_2,
                    "pmt_gateway_3": new_txn_payment_gateway_db_2,
                    "upi_txn_type_3": new_txn_upi_txn_type_db_2,
                    "upi_bank_code_3": new_txn_upi_bank_code_db_2,
                    "upi_mc_id_3": new_txn_upi_mc_id_db_2,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": new_txn_mid_db_1,
                    "tid_2": new_txn_tid_db_1,
                    "mid_3": new_txn_mid_db_2,
                    "tid_3": new_txn_tid_db_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(orig_created_time)
                date_and_time_portal_new_1 = date_time_converter.to_portal_format(new_txn_created_time_1)
                date_and_time_portal_new_2 = date_time_converter.to_portal_format(new_txn_created_time_2)

                expected_portal_values = {
                    "pmt_state": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "rrn": str(original_rrn),
                    "date_time": date_and_time_portal,

                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str(amount) + ".00",
                    "username_2": app_username,
                    "txn_id_2": new_txn_id_1,
                    "rrn_2": str(rrn),
                    "date_time_2": date_and_time_portal_new_1,

                    "pmt_state_3": "AUTHORIZED",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": str(amount) + ".00",
                    "username_3": app_username,
                    "txn_id_3": new_txn_id_2,
                    "rrn_3": str(rrn_2),
                    "date_time_3": date_and_time_portal_new_2,
                }
                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_3 = transaction_details[0]['Date & Time']
                transaction_id_3 = transaction_details[0]['Transaction ID']
                total_amount_3 = transaction_details[0]['Total Amount'].split()
                rr_number_3 = transaction_details[0]['RR Number']
                transaction_type_3 = transaction_details[0]['Type']
                status_3 = transaction_details[0]['Status']
                username_3 = transaction_details[0]['Username']

                date_time_2 = transaction_details[1]['Date & Time']
                transaction_id_2 = transaction_details[1]['Transaction ID']
                total_amount_2 = transaction_details[1]['Total Amount'].split()
                rr_number_2 = transaction_details[1]['RR Number']
                transaction_type_2 = transaction_details[1]['Type']
                status_2 = transaction_details[1]['Status']
                username_2 = transaction_details[1]['Username']

                date_time_original = transaction_details[2]['Date & Time']
                transaction_id_original = transaction_details[2]['Transaction ID']
                total_amount_original = transaction_details[2]['Total Amount'].split()
                rr_number_original = transaction_details[2]['RR Number']
                transaction_type_original = transaction_details[2]['Type']
                status_original = transaction_details[2]['Status']
                username_original = transaction_details[2]['Username']

                actual_portal_values = {
                    "pmt_state": str(status_original),
                    "pmt_type": transaction_type_original,
                    "txn_amt": total_amount_original[1],
                    "username": username_original,
                    "txn_id": transaction_id_original,
                    "rrn": rr_number_original,
                    "date_time": date_time_original,

                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2,

                    "pmt_state_3": str(status_3),
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "rrn_3": rr_number_3,
                    "date_time_3": date_time_3
                }

                logger.debug(f"actualPortalValues : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(new_txn_created_time_app)
                expected_charge_slip_values = {'PAID BY:': 'UPI',
                                               'merchant_ref_no': 'Ref # ' + str(order_id),
                                               'RRN': str(rrn_2),
                                               'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                               'date': txn_date,
                                               'time': txn_time,
                                               'AUTH CODE': "" if new_auth_code is None else new_auth_code
                                               }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(new_txn_id_2,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation----------------------------------
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
def test_common_100_103_245():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Success_Via_Two_UPI_Callback_RAZORPAY
    Sub Feature Description: Verification of a two upi callback after expiry via RAZORPAY when auto refund is Enabled.
    TC naming code description: 100: Payment Method, 103: RemotePay, 245: TC_245
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(
            f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        upi_account_id = result['pgMerchantId'].values[0]
        tid = result['virtual_tid'].values[0]
        mid = result['virtual_mid'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")
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
            amount = random.randint(601, 700)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)  # Check
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
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

                query = f"select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '{org_code}';"
                logger.debug(f"Query to fetch max Attempts from the DB : {query}")
                try:
                    result = DBProcessor.getValueFromDB(query)
                    print("result: ", result)
                    print("type of result: ", type(result))
                    org_setting_value = int(result['setting_value'].values[0])
                    logger.info(f"max upi attempt for {org_code} is {org_setting_value}")
                except Exception as e:
                    org_setting_value = None
                    print(e)

                query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = 'EZETAP'"
                logger.debug(f"Query to fetch Txn_id from the DB : {query1}")
                try:
                    defaultValue = DBProcessor.getValueFromDB(query1)
                    setting_value = int(defaultValue['setting_value'].values[0])
                    logger.info(f"max upi attempt is: {setting_value}")
                except NameError as e:
                    setting_value = None
                    print(e)
                except IndexError as e:
                    setting_value = None
                    print(e)
                except Exception as e:
                    print(e)

                if org_setting_value:
                    logger.info(f"Value for max upi attempt is: {org_setting_value} min.")
                    time.sleep(3 + (org_setting_value * 60))
                else:
                    logger.info(f"Value for Ezetap org is: {org_setting_value} min.")
                    time.sleep(3 + (setting_value * 60))

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")

            query = f"select * from upi_txn where org_code = '{org_code}' AND txn_id = '{original_txn_id}';"
            logger.debug(f"Query to fetch txn_ref from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            logger.debug(f"Query result, txn_ref : {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.debug(f"Query result, txn_ref_3 : {txn_ref_3}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount_api = amount * 100
            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "base_amount": amount_api,
                            "status": "captured",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_1 = result['id'].values[0]
            logger.debug(f"Query result, txn_id_new : {new_txn_id_1}")

            logger.debug(f"Generating razorpay_callback_generator_HMAC for 2nd CallBack")
            rrn_2 = str(random.randint(1000000000000, 9999999999999))
            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "base_amount": amount_api,
                            "status": "captured",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn_2
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api_2 is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_2 = result['id'].values[0]
            logger.debug(f"Query result, txn_id_new_2 : {new_txn_id_2}")

            query = f"select * from txn where id = '{original_txn_id}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            orig_txn_type = result['txn_type'].values[0]
            orig_created_time = result['created_time'].values[0]

            query = f"select * from txn where id = '{new_txn_id_1}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_customer_name_1 = result['customer_name'].values[0]
            new_txn_payer_name_1 = result['payer_name'].values[0]
            new_txn_type_1 = result['txn_type'].values[0]
            new_txn_created_time_1 = result['created_time'].values[0]
            new_txn_created_time_api_1 = result['created_time'].values[0]

            query = f"select * from txn where id = '{new_txn_id_2}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_customer_name_2 = result['customer_name'].values[0]
            new_txn_payer_name_2 = result['payer_name'].values[0]
            new_txn_type_2 = result['txn_type'].values[0]
            logger.info(f"New txn type is: {new_txn_type_2}")
            new_txn_created_time_api = result['created_time'].values[0]
            logger.info(f"New txn_created_time time for api is : {new_txn_created_time_api}")
            new_txn_created_time_app = result['created_time'].values[0]
            logger.info(f"New created time for app is : {new_txn_created_time_app}")
            new_auth_code = result['auth_code'].values[0]
            logger.info(f"New created time for app is : {new_auth_code}")
            new_txn_created_time_2 = result['created_time'].values[0]
            logger.info(f"New created time for app is : {new_txn_created_time_2}")
            # -----------------------------------------------------------------------------------------------------
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
                date_and_time = date_time_converter.to_app_format(orig_created_time)
                new_txn_date_and_time_1 = date_time_converter.to_app_format(new_txn_created_time_1)
                new_txn_date_and_time_2 = date_time_converter.to_app_format(new_txn_created_time_app)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    "customer_name": original_customer_name,
                    "payer_name": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": str(amount) + ".00",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id_1,
                    "rrn_2": str(rrn),
                    "customer_name_2": new_txn_customer_name_1,
                    "payer_name_2": new_txn_payer_name_1,
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND PENDING",
                    "date_2": new_txn_date_and_time_1,
                    "pmt_mode_3": "UPI",
                    "pmt_status_3": "REFUND_PENDING",
                    "txn_amt_3": str(amount) + ".00",
                    "settle_status_3": "SETTLED",
                    "txn_id_3": new_txn_id_2,
                    "rrn_3": str(rrn_2),
                    "customer_name_3": new_txn_customer_name_2,
                    "payer_name_3": new_txn_payer_name_2,
                    "order_id_3": order_id,
                    "pmt_msg_3": "REFUND PENDING",
                    "date_3": new_txn_date_and_time_2,

                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                app_amount = transactions_history_page.fetch_txn_amount_text()
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                app_payer_name = transactions_history_page.fetch_payer_name_text()
                app_order_id = transactions_history_page.fetch_order_id_text()
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id_1)
                app_payment_status_1 = transactions_history_page.fetch_txn_status_text()
                app_payment_status_1 = app_payment_status_1.split(':')[1]
                app_payment_mode_1 = transactions_history_page.fetch_txn_type_text()
                app_txn_id_1 = transactions_history_page.fetch_txn_id_text()
                app_amount_1 = transactions_history_page.fetch_txn_amount_text()
                app_rrn_1 = transactions_history_page.fetch_RRN_text()
                app_date_and_time_1 = transactions_history_page.fetch_date_time_text()
                app_settlement_status_1 = transactions_history_page.fetch_settlement_status_text()
                app_customer_name_1 = transactions_history_page.fetch_customer_name_text()
                app_payer_name_1 = transactions_history_page.fetch_payer_name_text()
                app_order_id_1 = transactions_history_page.fetch_order_id_text()

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id_2)
                app_payment_status_2 = transactions_history_page.fetch_txn_status_text()
                app_payment_status_2 = app_payment_status_2.split(':')[1]
                app_payment_mode_2 = transactions_history_page.fetch_txn_type_text()
                app_txn_id_2 = transactions_history_page.fetch_txn_id_text()
                app_amount_2 = transactions_history_page.fetch_txn_amount_text()
                app_rrn_2 = transactions_history_page.fetch_RRN_text()
                app_date_and_time_2 = transactions_history_page.fetch_date_time_text()
                app_settlement_status_2 = transactions_history_page.fetch_settlement_status_text()
                app_customer_name_2 = transactions_history_page.fetch_customer_name_text()
                app_payer_name_2 = transactions_history_page.fetch_payer_name_text()
                app_order_id_2 = transactions_history_page.fetch_order_id_text()
                app_payment_msg_2 = transactions_history_page.fetch_txn_payment_msg_text()

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,

                    "pmt_mode_2": app_payment_mode_1,
                    "pmt_status_2": app_payment_status_1,
                    "txn_amt_2": app_amount_1.split(' ')[1],
                    "settle_status_2": app_settlement_status_1,
                    "txn_id_2": app_txn_id_1,
                    "rrn_2": str(app_rrn_1),
                    "customer_name_2": app_customer_name_1,
                    "payer_name_2": app_payer_name_1,
                    "order_id_2": app_order_id_1,
                    "date_2": app_date_and_time_1,
                    "pmt_msg_2": app_payment_msg_2,

                    "pmt_mode_3": app_payment_mode_2,
                    "pmt_status_3": app_payment_status_2,
                    "txn_amt_3": app_amount_2.split(' ')[1],
                    "settle_status_3": app_settlement_status_2,
                    "txn_id_3": app_txn_id_2,
                    "rrn_3": str(app_rrn_2),
                    "customer_name_3": app_customer_name_2,
                    "payer_name_3": app_payer_name_2,
                    "order_id_3": app_order_id_2,
                    "pmt_msg_3": app_payment_msg_2,
                    "date_3": app_date_and_time_2,
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(orig_created_time)
                new_txn_date_1 = date_time_converter.db_datetime(new_txn_created_time_api_1)
                new_txn_date_2 = date_time_converter.db_datetime(new_txn_created_time_api)
                expected_api_values = {"pmt_status": "FAILED",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "FAILED",
                                       "settle_status": "FAILED",
                                       "acquirer_code": "RAZORPAY",
                                       "issuer_code": "RAZORPAY",
                                       "txn_type": orig_txn_type,
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code,
                                       "pmt_status_2": "REFUND_PENDING",
                                       "txn_amt_2": amount,
                                       "pmt_mode_2": "UPI",
                                       "pmt_state_2": "REFUND_PENDING",
                                       "new_rrn_1": str(rrn),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "RAZORPAY",
                                       "issuer_code_2": "RAZORPAY",
                                       "txn_type_2": new_txn_type_1,
                                       "mid_2": mid,
                                       "tid_2": tid,
                                       "org_code_2": org_code,
                                       "pmt_status_3": "REFUND_PENDING",
                                       "txn_amt_3": amount,
                                       "pmt_mode_3": "UPI",
                                       "pmt_state_3": "REFUND_PENDING",
                                       "new_rrn_2": str(rrn_2),
                                       "settle_status_3": "SETTLED",
                                       "acquirer_code_3": "RAZORPAY",
                                       "issuer_code_3": "RAZORPAY",
                                       "txn_type_3": new_txn_type_2,
                                       "mid_3": mid,
                                       "tid_3": tid,
                                       "org_code_3": org_code,
                                       "date": date,
                                       "date_2": new_txn_date_1,
                                       "date_3": new_txn_date_2
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])
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

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == new_txn_id_1][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                new_txn_status_api_1 = response["status"]
                new_txn_amount_api_1 = int(response["amount"])
                new_payment_mode_api_1 = response["paymentMode"]
                new_txn_state_api_1 = response["states"][0]
                new_txn_rrn_api_1 = response["rrNumber"]
                new_txn_settlement_status_api_1 = response["settlementStatus"]
                new_txn_issuer_code_api_1 = response["issuerCode"]
                new_txn_acquirer_code_api_1 = response["acquirerCode"]
                new_txn_orgCode_api_1 = response["orgCode"]
                new_txn_mid_api_1 = response["mid"]
                new_txn_tid_api_1 = response["tid"]
                new_txn_txn_type_api_1 = response["txnType"]
                new_txn_date_api_1 = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == new_txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                new_txn_status_api_2 = response["status"]
                new_txn_amount_api_2 = int(response["amount"])
                new_payment_mode_api_2 = response["paymentMode"]
                new_txn_state_api_2 = response["states"][0]
                new_txn_rrn_api_2 = response["rrNumber"]
                new_txn_settlement_status_api_2 = response["settlementStatus"]
                new_txn_issuer_code_api_2 = response["issuerCode"]
                new_txn_acquirer_code_api_2 = response["acquirerCode"]
                new_txn_orgCode_api_2 = response["orgCode"]
                new_txn_mid_api_2 = response["mid"]
                new_txn_tid_api_2 = response["tid"]
                new_txn_type_api_2 = response["txnType"]
                new_txn_date_api_2 = response["createdTime"]
                #
                actual_api_values = {"pmt_status": status_api,
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

                                     "pmt_status_2": new_txn_status_api_1,
                                     "txn_amt_2": new_txn_amount_api_1,
                                     "pmt_mode_2": new_payment_mode_api_1,
                                     "pmt_state_2": new_txn_state_api_1,
                                     "new_rrn_1": str(new_txn_rrn_api_1),
                                     "settle_status_2": new_txn_settlement_status_api_1,
                                     "acquirer_code_2": new_txn_acquirer_code_api_1,
                                     "issuer_code_2": new_txn_issuer_code_api_1,
                                     "txn_type_2": new_txn_txn_type_api_1,
                                     "mid_2": new_txn_mid_api_1,
                                     "tid_2": new_txn_tid_api_1,
                                     "org_code_2": new_txn_orgCode_api_1,

                                     "pmt_status_3": new_txn_status_api_2,
                                     "txn_amt_3": new_txn_amount_api_2,
                                     "pmt_mode_3": new_payment_mode_api_2,
                                     "pmt_state_3": new_txn_state_api_2,
                                     "new_rrn_2": str(new_txn_rrn_api_2),
                                     "settle_status_3": new_txn_settlement_status_api_2,
                                     "acquirer_code_3": new_txn_acquirer_code_api_2,
                                     "issuer_code_3": new_txn_issuer_code_api_2,
                                     "txn_type_3": new_txn_type_api_2,
                                     "mid_3": new_txn_mid_api_2,
                                     "tid_3": new_txn_tid_api_2,
                                     "org_code_3": new_txn_orgCode_api_2,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "date_2": date_time_converter.from_api_to_datetime_format(
                                         new_txn_date_api_1),
                                     "date_3": date_time_converter.from_api_to_datetime_format(
                                         new_txn_date_api_2)
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {"pmt_status": "FAILED",
                                      "pmt_state": "FAILED",
                                      "pmt_mode": "UPI",
                                      "txn_amt": amount,
                                      "upi_txn_status": "FAILED",
                                      "settle_status": "FAILED",
                                      "acquirer_code": "RAZORPAY",
                                      "bank_code": "RAZORPAY",
                                      "upi_txn_type": "COLLECT",
                                      "upi_bank_code": "RAZORPAY_PSP",
                                      "upi_mc_id": upi_mc_id,
                                      "pmt_gateway": "RAZORPAY",
                                      "pmt_status_2": "REFUND_PENDING",
                                      "pmt_state_2": "REFUND_PENDING",
                                      "pmt_mode_2": "UPI",
                                      "txn_amt_2": amount,
                                      "upi_txn_status_2": "REFUND_PENDING",
                                      "settle_status_2": "SETTLED",
                                      "acquirer_code_2": "RAZORPAY",
                                      "bank_code_2": "RAZORPAY",
                                      "pmt_gateway_2": "RAZORPAY",
                                      "upi_txn_type_2": "COLLECT",
                                      "upi_bank_code_2": "RAZORPAY_PSP",
                                      "upi_mc_id_2": upi_mc_id,
                                      "pmt_status_3": "REFUND_PENDING",
                                      "pmt_state_3": "REFUND_PENDING",
                                      "pmt_mode_3": "UPI",
                                      "txn_amt_3": amount,
                                      "upi_txn_status_3": "REFUND_PENDING",
                                      "settle_status_3": "SETTLED",
                                      "acquirer_code_3": "RAZORPAY",
                                      "bank_code_3": "RAZORPAY",
                                      "pmt_gateway_3": "RAZORPAY",
                                      "upi_txn_type_3": "COLLECT",
                                      "upi_bank_code_3": "RAZORPAY_PSP",
                                      "upi_mc_id_3": upi_mc_id,
                                      "mid": mid,
                                      "tid": tid,
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "mid_3": mid,
                                      "tid_3": tid
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = f"select * from txn where id='{new_txn_id_1}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_1 = result["status"].iloc[0]
                new_txn_payment_mode_db_1 = result["payment_mode"].iloc[0]
                new_txn_amount_db_1 = int(result["amount"].iloc[0])
                new_txn_state_db_1 = result["state"].iloc[0]
                new_txn_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_1 = result["settlement_status"].iloc[0]
                new_txn_tid_db_1 = result['tid'].values[0]
                new_txn_mid_db_1 = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{new_txn_id_1}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_1 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = f"select * from txn where id='{new_txn_id_2}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_2 = result["status"].iloc[0]
                new_txn_payment_mode_db_2 = result["payment_mode"].iloc[0]
                new_txn_amount_db_2 = int(result["amount"].iloc[0])
                new_txn_state_db_2 = result["state"].iloc[0]
                new_txn_payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_2 = result["settlement_status"].iloc[0]
                new_txn_tid_db_2 = result['tid'].values[0]
                new_txn_mid_db_2 = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{new_txn_id_2}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_2 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_2 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_gateway": payment_gateway_db,
                    "pmt_status_2": new_txn_status_db_1,
                    "pmt_state_2": new_txn_state_db_1,
                    "pmt_mode_2": new_txn_payment_mode_db_1,
                    "txn_amt_2": new_txn_amount_db_1,
                    "upi_txn_status_2": new_txn_upi_status_db_1,
                    "settle_status_2": new_txn_settlement_status_db_1,
                    "acquirer_code_2": new_txn_acquirer_code_db_1,
                    "bank_code_2": new_txn_bank_code_db_1,
                    "pmt_gateway_2": new_txn_payment_gateway_db_1,
                    "upi_txn_type_2": new_txn_upi_txn_type_db_1,
                    "upi_bank_code_2": new_txn_upi_bank_code_db_1,
                    "upi_mc_id_2": new_txn_upi_mc_id_db_1,
                    "pmt_status_3": new_txn_status_db_2,
                    "pmt_state_3": new_txn_state_db_2,
                    "pmt_mode_3": new_txn_payment_mode_db_2,
                    "txn_amt_3": new_txn_amount_db_2,
                    "upi_txn_status_3": new_txn_upi_status_db_2,
                    "settle_status_3": new_txn_settlement_status_db_2,
                    "acquirer_code_3": new_txn_acquirer_code_db_2,
                    "bank_code_3": new_txn_bank_code_db_2,
                    "pmt_gateway_3": new_txn_payment_gateway_db_2,
                    "upi_txn_type_3": new_txn_upi_txn_type_db_2,
                    "upi_bank_code_3": new_txn_upi_bank_code_db_2,
                    "upi_mc_id_3": new_txn_upi_mc_id_db_2,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": new_txn_mid_db_1,
                    "tid_2": new_txn_tid_db_1,
                    "mid_3": new_txn_mid_db_2,
                    "tid_3": new_txn_tid_db_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(orig_created_time)
                date_and_time_portal_new_1 = date_time_converter.to_portal_format(new_txn_created_time_1)
                date_and_time_portal_new_2 = date_time_converter.to_portal_format(new_txn_created_time_2)

                expected_portal_values = {
                    "pmt_state": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "rrn": str(original_rrn),
                    "date_time": date_and_time_portal,
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str(amount) + ".00",
                    "username_2": app_username,
                    "txn_id_2": new_txn_id_1,
                    "rrn_2": str(rrn),
                    "date_time_2": date_and_time_portal_new_1,
                    "pmt_state_3": "REFUND_PENDING",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": str(amount) + ".00",
                    "username_3": app_username,
                    "txn_id_3": new_txn_id_2,
                    "rrn_3": str(rrn_2),
                    "date_time_3": date_and_time_portal_new_2,
                }
                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_3 = transaction_details[0]['Date & Time']
                transaction_id_3 = transaction_details[0]['Transaction ID']
                total_amount_3 = transaction_details[0]['Total Amount'].split()
                rr_number_3 = transaction_details[0]['RR Number']
                transaction_type_3 = transaction_details[0]['Type']
                status_3 = transaction_details[0]['Status']
                username_3 = transaction_details[0]['Username']

                date_time_2 = transaction_details[1]['Date & Time']
                transaction_id_2 = transaction_details[1]['Transaction ID']
                total_amount_2 = transaction_details[1]['Total Amount'].split()
                rr_number_2 = transaction_details[1]['RR Number']
                transaction_type_2 = transaction_details[1]['Type']
                status_2 = transaction_details[1]['Status']
                username_2 = transaction_details[1]['Username']

                date_time_original = transaction_details[2]['Date & Time']
                transaction_id_original = transaction_details[2]['Transaction ID']
                total_amount_original = transaction_details[2]['Total Amount'].split()
                rr_number_original = transaction_details[2]['RR Number']
                transaction_type_original = transaction_details[2]['Type']
                status_original = transaction_details[2]['Status']
                username_original = transaction_details[2]['Username']

                actual_portal_values = {
                    "pmt_state": str(status_original),
                    "pmt_type": transaction_type_original,
                    "txn_amt": total_amount_original[1],
                    "username": username_original,
                    "txn_id": transaction_id_original,
                    "rrn": rr_number_original,
                    "date_time": date_time_original,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2,
                    "pmt_state_3": str(status_3),
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "rrn_3": rr_number_3,
                    "date_time_3": date_time_3
                }

                logger.debug(f"actualPortalValues : {actual_portal_values}")
                # -----------------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------------
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
def test_common_100_103_246():
    """
    Sub Feature Code: UI_Common_PM_2_UPI_Collect_success_callback_before_expiry_RAZORPAY_AutoRefund_Disabled
    Sub Feature Description: Verification of a two  UPI Collect success callback via RAZORPAY before expiry the  when autorefund is disabled
    100: Payment Method, 103: RemotePay, 246: TC246
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(
            f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        upi_account_id = result['pgMerchantId'].values[0]
        tid = result['virtual_tid'].values[0]
        mid = result['virtual_mid'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            amount = random.randint(601, 700)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                paymentLinkUrl = response['paymentLink']
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_browser.goto(paymentLinkUrl)
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

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{str(order_id)}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.info(f"original txn id is: {original_txn_id}")

            query = f"select * from payment_intent where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"payment intent is : {payment_intent_id}")

            query = f"select * from upi_txn where txn_id = '{original_txn_id}';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.info(f"original txn ref is: {txn_ref} AND txn_ref_3: {txn_ref_3}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount_api = amount * 100
            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "base_amount": amount_api,
                            "status": "captured",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND id = '{original_txn_id}';"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Results from txn Query is: {result}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"Query result, status is : {original_status}")
            original_created_time = result['created_time'].values[0]
            logger.debug(f"Query result, original_posting_date is : {original_created_time}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn_2 = str(random.randint(1000000000000, 9999999999999))
            amount_api = amount * 100
            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "base_amount": amount_api,
                            "status": "captured",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn_2
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id_1 from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id_1 : {new_txn_id}")

            query = f"select * from txn where id = '{new_txn_id}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_customer_name_2 = result['customer_name'].values[0]
            txn_payer_name_2 = result['payer_name'].values[0]
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Second callback txn type is: {txn_type_2}")
            txn_created_date_time_2 = result['created_time'].values[0]
            logger.debug(f"Second Callback orig_posting_date is : {txn_created_date_time_2}")
            txn_posting_date_api_2 = result['posting_date'].values[0]
            logger.debug(f"Second Callback orig_posting_date is : {txn_posting_date_api_2}")
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
                date_and_time = date_time_converter.to_app_format(original_created_time)
                new_txn_date_and_time_1 = date_time_converter.to_app_format(txn_created_date_time_2)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": original_txn_id,
                    "rrn": str(original_rrn),
                    "customer_name": original_customer_name,
                    "payer_name": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount) + ".00",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": txn_customer_name_2,
                    "payer_name_2": txn_payer_name_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": new_txn_date_and_time_1,

                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                app_amount = transactions_history_page.fetch_txn_amount_text()
                app_rrn = transactions_history_page.fetch_RRN_text()
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                app_payer_name = transactions_history_page.fetch_payer_name_text()
                app_order_id = transactions_history_page.fetch_order_id_text()
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id)
                app_payment_status_1 = transactions_history_page.fetch_txn_status_text()
                app_payment_status_1 = app_payment_status_1.split(':')[1]
                app_payment_mode_1 = transactions_history_page.fetch_txn_type_text()
                app_txn_id_1 = transactions_history_page.fetch_txn_id_text()
                app_amount_1 = transactions_history_page.fetch_txn_amount_text()
                app_rrn_1 = transactions_history_page.fetch_RRN_text()
                app_date_and_time_1 = transactions_history_page.fetch_date_time_text()
                app_settlement_status_1 = transactions_history_page.fetch_settlement_status_text()
                app_customer_name_1 = transactions_history_page.fetch_customer_name_text()
                app_payer_name_1 = transactions_history_page.fetch_payer_name_text()
                app_order_id_1 = transactions_history_page.fetch_order_id_text()
                app_payment_msg_1 = transactions_history_page.fetch_txn_payment_msg_text()

                actual_app_values = {"pmt_mode": app_payment_mode,
                                     "pmt_status": app_payment_status,
                                     "txn_amt": app_amount.split(' ')[1],
                                     "settle_status": app_settlement_status,
                                     "txn_id": app_txn_id,
                                     "rrn": str(app_rrn),
                                     "customer_name": app_customer_name,
                                     "payer_name": app_payer_name,
                                     "order_id": app_order_id,
                                     "pmt_msg": app_payment_msg,
                                     "date": app_date_and_time,

                                     "pmt_mode_2": app_payment_mode_1,
                                     "pmt_status_2": app_payment_status_1,
                                     "txn_amt_2": app_amount_1.split(' ')[1],
                                     "settle_status_2": app_settlement_status_1,
                                     "txn_id_2": app_txn_id_1,
                                     "rrn_2": str(app_rrn_1),
                                     "customer_name_2": app_customer_name_1,
                                     "payer_name_2": app_payer_name_1,
                                     "order_id_2": app_order_id_1,
                                     "pmt_msg_2": app_payment_msg_1,
                                     "date_2": app_date_and_time_1,

                                     }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(original_created_time)
                new_txn_date_1 = date_time_converter.db_datetime(txn_created_date_time_2)
                expected_api_values = {"pmt_status": "AUTHORIZED",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "SETTLED",
                                       "settle_status": "SETTLED",
                                       "acquirer_code": "RAZORPAY",
                                       "issuer_code": "RAZORPAY",
                                       "txn_type": txn_type_2,
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code,
                                       "date": date,

                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": amount,
                                       "pmt_mode_2": "UPI",
                                       "pmt_state_2": "SETTLED",
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "RAZORPAY",
                                       "issuer_code_2": "RAZORPAY",
                                       "txn_type_2": txn_type_2,
                                       "mid_2": mid,
                                       "tid_2": tid,
                                       "org_code_2": org_code,
                                       "date_2": new_txn_date_1,

                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])
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

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == new_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                new_txn_status_api_1 = response["status"]
                new_txn_amount_api_1 = int(response["amount"])
                new_payment_mode_api_1 = response["paymentMode"]
                new_txn_state_api_1 = response["states"][0]
                new_txn_settlement_status_api_1 = response["settlementStatus"]
                new_txn_issuer_code_api_1 = response["issuerCode"]
                new_txn_acquirer_code_api_1 = response["acquirerCode"]
                new_txn_orgCode_api_1 = response["orgCode"]
                new_txn_mid_api_1 = response["mid"]
                new_txn_tid_api_1 = response["tid"]
                new_txn_txn_type_api_1 = response["txnType"]
                new_txn_date_api_1 = response["createdTime"]

                #
                actual_api_values = {"pmt_status": status_api,
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

                                     "pmt_status_2": new_txn_status_api_1,
                                     "txn_amt_2": new_txn_amount_api_1,
                                     "pmt_mode_2": new_payment_mode_api_1,
                                     "pmt_state_2": new_txn_state_api_1,
                                     "settle_status_2": new_txn_settlement_status_api_1,
                                     "acquirer_code_2": new_txn_acquirer_code_api_1,
                                     "issuer_code_2": new_txn_issuer_code_api_1,
                                     "txn_type_2": new_txn_txn_type_api_1,
                                     "mid_2": new_txn_mid_api_1,
                                     "tid_2": new_txn_tid_api_1,
                                     "org_code_2": new_txn_orgCode_api_1,
                                     "date_2": date_time_converter.from_api_to_datetime_format(
                                         new_txn_date_api_1),

                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {"pmt_status": "AUTHORIZED",
                                      "pmt_state": "SETTLED",
                                      "pmt_mode": "UPI",
                                      "txn_amt": amount,
                                      "upi_txn_status": "AUTHORIZED",
                                      "settle_status": "SETTLED",
                                      "acquirer_code": "RAZORPAY",
                                      "bank_code": "RAZORPAY",
                                      "upi_txn_type": "COLLECT",
                                      "upi_bank_code": "RAZORPAY_PSP",
                                      "upi_mc_id": upi_mc_id,

                                      "pmt_status_2": "AUTHORIZED",
                                      "pmt_state_2": "SETTLED",
                                      "pmt_mode_2": "UPI",
                                      "txn_amt_2": amount,
                                      "upi_txn_status_2": "AUTHORIZED",
                                      "settle_status_2": "SETTLED",
                                      "acquirer_code_2": "RAZORPAY",
                                      "bank_code_2": "RAZORPAY",
                                      "pmt_gateway_2": "RAZORPAY",
                                      "upi_txn_type_2": "COLLECT",
                                      "upi_bank_code_2": "RAZORPAY_PSP",
                                      "upi_mc_id_2": upi_mc_id,
                                      "mid": mid,
                                      "tid": tid,
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "pmt_gateway": "RAZORPAY"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = f"select * from txn where id='{new_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_1 = result["status"].iloc[0]
                new_txn_payment_mode_db_1 = result["payment_mode"].iloc[0]
                new_txn_amount_db_1 = int(result["amount"].iloc[0])
                new_txn_state_db_1 = result["state"].iloc[0]
                new_txn_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_1 = result["settlement_status"].iloc[0]
                new_txn_tid_db_1 = result['tid'].values[0]
                new_txn_mid_db_1 = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{new_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_1 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,

                    "pmt_status_2": new_txn_status_db_1,
                    "pmt_state_2": new_txn_state_db_1,
                    "pmt_mode_2": new_txn_payment_mode_db_1,
                    "txn_amt_2": new_txn_amount_db_1,
                    "upi_txn_status_2": new_txn_upi_status_db_1,
                    "settle_status_2": new_txn_settlement_status_db_1,
                    "acquirer_code_2": new_txn_acquirer_code_db_1,
                    "bank_code_2": new_txn_bank_code_db_1,
                    "pmt_gateway_2": new_txn_payment_gateway_db_1,
                    "upi_txn_type_2": new_txn_upi_txn_type_db_1,
                    "upi_bank_code_2": new_txn_upi_bank_code_db_1,
                    "upi_mc_id_2": new_txn_upi_mc_id_db_1,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": new_txn_mid_db_1,
                    "tid_2": new_txn_tid_db_1,
                    "pmt_gateway": payment_gateway_db,

                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
            # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(original_created_time)
                date_and_time_portal_new = date_time_converter.to_portal_format(txn_created_date_time_2)

                expected_portal_values = {
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "rrn": str(original_rrn),
                    "date_time": date_and_time_portal,

                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str(amount) + ".00",
                    "username_2": app_username,
                    "txn_id_2": new_txn_id,
                    "rrn_2": str(rrn_2),
                    "date_time_2": date_and_time_portal_new
                }
                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                date_time_original = transaction_details[1]['Date & Time']
                transaction_id_original = transaction_details[1]['Transaction ID']
                total_amount_original = transaction_details[1]['Total Amount'].split()
                rr_number_original = transaction_details[1]['RR Number']
                transaction_type_original = transaction_details[1]['Type']
                status_original = transaction_details[1]['Status']
                username_original = transaction_details[1]['Username']

                actual_portal_values = {
                    "pmt_state": str(status_original),
                    "pmt_type": transaction_type_original,
                    "txn_amt": total_amount_original[1],
                    "username": username_original,
                    "txn_id": transaction_id_original,
                    "rrn": rr_number_original,
                    "date_time": date_time_original,

                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2
                }
                logger.debug(f"actualPortalValues : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_date_time_2)
                expected_values = {'PAID BY:': 'UPI',
                                   'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn_2),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date,
                                   'time': txn_time,
                                   }
                logger.debug(f"expected_values : {expected_values}")
                receipt_validator.perform_charge_slip_validations(new_txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_values)

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)
