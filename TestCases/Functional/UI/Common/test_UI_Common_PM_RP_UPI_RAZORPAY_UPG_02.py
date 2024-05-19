import sys
import pytest
from datetime import datetime
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_220():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Amount_Mismatch_Razorpay
    Sub Feature Description: Verification of a Remote Pay upi for amount mismatch
    TC naming code description: 100: Payment Method, 103: RemotePay, 220: TC220
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                               portal_un=portal_username, portal_pw=portal_password,
                                                               payment_gateway='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "update remotepay_setting set setting_value= '1' where setting_name='cnpTxnTimeoutDuration' and " \
                "org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result for remote pay setting is: {result}")

        query = f"select * from upi_merchant_config where bank_code = 'RAZORPAY_PSP' AND status = 'ACTIVE' AND " \
                f"org_code = '{str(org_code)}' and card_terminal_acquirer_code = 'NONE' order by created_time desc limit 1"
        logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Query result pgMerchantId : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result upi_mc_id: {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize(browser_type='firefox')
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            amount = 650
            mismatch_amount = 800
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
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
                remote_pay_upi_txn = RemotePayTxnPage(ui_browser)
                remote_pay_upi_txn.clickOnRemotePayUPI()
                logger.info("Opening UPI intent to start the txn.")
                remote_pay_upi_txn.clickOnRemotePayLaunchUPI()
                logger.info("UPI flow completed")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            query = f"select * from upi_txn where txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_ref = result['txn_ref'].values[0]
            txn_ref_3 = result['txn_ref3'].values[0]

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = mismatch_amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = mismatch_amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = order_id

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")
            error_message = response['message']
            logger.debug(f"amount miss match error message :{error_message}")

            query = f"select * from txn where id='{original_txn_id}'"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")
            original_mid = result['mid'].values[0]
            logger.debug(f"MID is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"TID is : {original_tid}")
            original_state = result['state'].values[0]
            logger.debug(f"State of txn is : {original_state}")
            original_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Payment mode from txn is : {original_payment_mode}")
            original_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"Settlement status from txn is : {original_settlement_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"Posting date from txn is : {original_posting_date}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Posting created_time from txn is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Posting auth_code from txn is : {auth_code}")

            query = f"select * from payment_intent where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")

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
        # -----------------------------------------End of Test Execution--------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "PENDING",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "PENDING",
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT PENDING",
                    "date": date_and_time,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn  {app_txn_id}")
                app_amount = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn :  {app_settlement_status}")
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {app_customer_name}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {app_payment_msg}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
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
                date = date_time_converter.db_datetime(original_posting_date)
                expected_api_values = {"pmt_status": "PENDING",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "PENDING",
                                       "settle_status": "PENDING",
                                       "acquirer_code": "RAZORPAY",
                                       "issuer_code": "RAZORPAY",
                                       "txn_type": "REMOTE_PAY",
                                       "mid": original_mid,
                                       "tid": original_tid,
                                       "org_code": org_code,
                                       "date": date,
                                       "error_msg": f"AMOUNT MISMATCH. razorpay_payment_id = {str(txn_ref)}, txn "
                                                    f"Amount = {str(amount)}.00, callback amount = {str(mismatch_amount)}"
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('paymentStatus',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug("Response from API DETAILS is :", api_details)
                status_api = response["status"]
                logger.debug(f"status_api: {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api: {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api: {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api: {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api: {txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"date_api: {date_api}")

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
                                     "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "error_msg": error_message
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
                    "pmt_status": "PENDING",
                    "pmt_state": "PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "PENDING",
                    "settle_status": "PENDING",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "intent_status": "ACTIVE"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")
                query = f"select * from upi_txn where txn_id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db: {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": original_status,
                    "pmt_state": original_state,
                    "pmt_mode": original_payment_mode,
                    "txn_amt": amount,
                    "settle_status": original_settlement_status,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "intent_status": intent_status
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
                    "pmt_state": "PENDING",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "auth_code": "-" if auth_code is None else auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time_portal: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code: {auth_code}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code
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
        query = "update remotepay_setting set setting_value=2 where setting_name='cnpTxnTimeoutDuration' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"In finally, remote pay setting is: {result}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_233():
    """
    Sub Feature Code: UI_Common_PM_RP_RP_upi_collect_Callback_Amount_Mismatch_Razorpay UPGRefund_&_UPGAutoRefund_Enabled
    Sub Feature Description: Verification a Remote Pay upi collect callback for upg txn using amount mismatch UPGRefund_&_UPGAutoRefund_Enabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 233: TC233
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                               portal_un=portal_username, portal_pw=portal_password,
                                                               payment_gateway='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})

        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = "update remotepay_setting set setting_value= '2' where setting_name='cnpTxnTimeoutDuration' and " \
                f"org_code='{org_code}';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result for remote pay setting is: {result}")

        query = "select * from upi_merchant_config where bank_code = 'RAZORPAY_PSP' AND status = 'ACTIVE' AND " \
                "org_code = '" + str(
            org_code) + "' and card_terminal_acquirer_code = 'NONE' order by created_time desc limit 1"
        logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Query result pgMerchantId : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result upi_mc_id: {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            amount = 650
            mismatch_amount = 651
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
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
                remote_pay_upi_collect_txn = RemotePayTxnPage(ui_browser)
                remote_pay_upi_collect_txn.clickOnRemotePayUPI()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectAppSelection()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectId("abc")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectDropDown("okicici")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectProceed()

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{str(order_id)}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            query = f"select * from upi_txn where txn_id='{original_txn_id}'"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_ref = result['txn_ref'].values[0]
            txn_ref_3 = result['txn_ref3'].values[0]

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = mismatch_amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = mismatch_amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = order_id

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")
            error_message = response['message']
            logger.debug(f"amount miss match error message :{error_message}")

            query = f"select * from txn where id='{original_txn_id}'"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")
            original_mid = result['mid'].values[0]
            logger.debug(f"MID is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"TID is : {original_tid}")
            original_bank_code = result['bank_code'].values[0]
            logger.debug(f"bank code from txn is : {original_bank_code}")
            original_state = result['state'].values[0]
            logger.debug(f"State of txn is : {original_state}")
            original_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Payment mode from txn is : {original_payment_mode}")
            original_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"Settlement status from txn is : {original_settlement_status}")
            original_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Settlement status from txn is : {original_acquirer_code}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"Posting date from txn is : {original_posting_date}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Posting created_time from txn is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Posting auth_code from txn is : {auth_code}")

            query = f"select * from payment_intent where org_code = '{org_code}' AND external_ref = '{order_id}' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")

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
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "PENDING",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "PENDING",
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT PENDING",
                    "date": date_and_time,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn  {app_txn_id}")
                app_amount = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn :  {app_settlement_status}")
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {app_customer_name}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {app_payment_msg}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
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
                date = date_time_converter.db_datetime(original_posting_date)
                expected_api_values = {"pmt_status": "PENDING",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "PENDING",
                                       "settle_status": "PENDING",
                                       "acquirer_code": "RAZORPAY",
                                       "issuer_code": "RAZORPAY",
                                       "txn_type": "REMOTE_PAY",
                                       "mid": original_mid,
                                       "tid": original_tid,
                                       "org_code": org_code,
                                       "date": date,
                                       "error_msg": f"AMOUNT MISMATCH. razorpay_payment_id = {str(txn_ref)}, txn "
                                                    f"Amount = {str(amount)}.00, callback amount = {str(mismatch_amount)}"
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
                logger.debug(f"status_api: {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api :{amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api :{payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api :{state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api :{settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api :{issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api :{acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api :{org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api :{mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api :{tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api :{txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"date_api :{date_api}")

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
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "error_msg": error_message
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
                    "pmt_status": "PENDING",
                    "pmt_state": "PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "PENDING",
                    "settle_status": "PENDING",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "intent_status": "ACTIVE"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{original_txn_id}'"
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
                    "pmt_status": original_status,
                    "pmt_state": original_state,
                    "pmt_mode": original_payment_mode,
                    "txn_amt": amount,
                    "settle_status": original_settlement_status,
                    "acquirer_code": original_acquirer_code,
                    "bank_code": original_bank_code,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "intent_status": intent_status
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
                    "pmt_state": "PENDING",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "auth_code": "-" if auth_code is None else auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time_portal: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code: {auth_code}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code
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
        query = "update remotepay_setting set setting_value=2 where setting_name='cnpTxnTimeoutDuration' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"In finally, remote pay setting is: {result}")
        Configuration.executeFinallyBlock(testcase_id)
