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
@pytest.mark.chargeSlipVal
def test_common_100_103_247():
    """
    Sub Feature Code: UI_Common_PM_2_UPI_Collect_success_callback_before_expiry_RAZORPAY_AutoRefund_Enabled
    Sub Feature Description: Performing two UPI Collect success callback via RAZORPAY before expiry the when autorefund is enabled
    100: Payment Method, 103: RemotePay, 247: TC0247
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
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
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
        logger.debug(f"Query result, pgMerchantId : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id: {upi_mc_id}")
        upi_account_id = result['pgMerchantId'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Query result, tid: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Query result, mid: {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()

            amount = random.randint(601, 700)
            logger.info(f"Entered amount is: {amount}")
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

            query = f"select * from upi_txn where txn_id = '{original_txn_id}';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            logger.debug(f"Query result, txn_ref : {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.debug(f"Query result, txn_ref_3 : {txn_ref_3}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            logger.info(f"generated rrn is {rrn}")
            amount_api = amount * 100
            logger.info(f"amount is: {amount_api}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn

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

            query = f"select * from txn where org_code = '{org_code}' AND id = '{original_txn_id}';"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Results from txn Query is: {result}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_created_time = result['created_time'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_created_time}")

            query = f"select * from payment_intent where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"fetching  payment_intent_id : {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"fetching Payment intent status for UPI is: {intent_status}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn_2 = str(random.randint(1000000000000, 9999999999999))
            logger.info(f"generated rrn is {rrn_2}")
            amount_api = amount * 100
            logger.info(f"amount is {amount_api}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn_2

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

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id_1 from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_2 = result['id'].values[0]
            logger.debug(f"Query result new_txn_id_1 : {new_txn_id_2}")

            query = f"select * from txn where id = '{new_txn_id_2}';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"fetching customer name for new txn from db is:{txn_customer_name_2}")
            txn_payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"fetching payer name for new txn from db is:{txn_payer_name_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"fetching txn type for new txn from db is:{txn_type_2}")
            txn_created_date_time_2 = result['created_time'].values[0]
            logger.debug(f"fetching date for new txn from db is:{txn_created_date_time_2}")

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
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": str(amount) + ".00",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": txn_customer_name_2,
                    "payer_name_2": txn_payer_name_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND PENDING",
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
                logger.info(f"fetching status from history page: {app_payment_status}")
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.info(f"fetching payment mode from history page: {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.info(f"fetching txn id from history page: {app_txn_id}")
                app_amount = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"fetching amount from history page: {app_amount}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"fetching date from history page: {app_date_and_time}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"fetching settlement_status from history page: {app_settlement_status}")
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(f"fetching customer name from history page: {app_customer_name}")
                app_payer_name = transactions_history_page.fetch_payer_name_text()
                logger.info(f"fetching payer name from history page: {app_payer_name}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"fetching order id from history page: {app_order_id}")
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"fetching payment msg from history page: {app_payment_msg}")
                app_rrn = transactions_history_page.fetch_RRN_text()
                logger.info(f"fetching rrn from history page: {app_rrn}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id_2)

                app_payment_status_1 = transactions_history_page.fetch_txn_status_text()
                app_payment_status_1 = app_payment_status_1.split(':')[1]
                logger.info(f"fetching status from history page: {app_payment_status_1}")
                app_payment_mode_1 = transactions_history_page.fetch_txn_type_text()
                logger.info(f"fetching payment mode from history page: {app_payment_mode_1}")
                app_txn_id_1 = transactions_history_page.fetch_txn_id_text()
                logger.info(f"fetching txn id from history page: {app_txn_id_1}")
                app_amount_1 = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"fetching amount from history page: {app_amount_1}")
                app_rrn_1 = transactions_history_page.fetch_RRN_text()
                logger.info(f"fetching rrn from history page: {app_rrn_1}")
                app_date_and_time_1 = transactions_history_page.fetch_date_time_text()
                logger.info(f"fetching date from history page: {app_date_and_time_1}")
                app_settlement_status_1 = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"fetching settlement_status from history page: {app_settlement_status_1}")
                app_customer_name_1 = transactions_history_page.fetch_customer_name_text()
                logger.info(f"fetching customer name from history page: {app_customer_name_1}")
                app_payer_name_1 = transactions_history_page.fetch_payer_name_text()
                logger.info(f"fetching payer name from history page: {app_payer_name_1}")
                app_order_id_1 = transactions_history_page.fetch_order_id_text()
                logger.info(f"fetching order id from history page: {app_order_id_1}")
                app_payment_msg_1 = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"fetching payment msg from history page: {app_payment_msg_1}")

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
        # -----------------------------------------End of App Validation----------------------------------------------
        # -----------------------------------------Start of API Validation---------------------------------------------
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
                                       "pmt_status_2": "REFUND_PENDING",
                                       "txn_amt_2": amount,
                                       "pmt_mode_2": "UPI",
                                       "pmt_state_2": "REFUND_PENDING",
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
                logger.debug(f"status from api response is: {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount from api response is: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment mode from api response is: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"txn_state from api response is: {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement status from api response is: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer code from api response is: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer code from api response is: {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code from api response is: {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"mid from api response is: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid from api response is: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn type from api response is: {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"date from api response is: {date_api}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == new_txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                new_txn_status_api_1 = response["status"]
                logger.debug(f"status from api response is: {new_txn_status_api_1}")
                new_txn_amount_api_1 = int(response["amount"])
                logger.debug(f"amount from api response is: {new_txn_amount_api_1}")
                new_payment_mode_api_1 = response["paymentMode"]
                logger.debug(f"payment mode from api response is: {new_payment_mode_api_1}")
                new_txn_state_api_1 = response["states"][0]
                logger.debug(f"state from api response is: {new_txn_state_api_1}")
                new_txn_settlement_status_api_1 = response["settlementStatus"]
                logger.debug(f"settlement status from api response is: {new_txn_settlement_status_api_1}")
                new_txn_issuer_code_api_1 = response["issuerCode"]
                logger.debug(f"issuer code from api response is: {new_txn_issuer_code_api_1}")
                new_txn_acquirer_code_api_1 = response["acquirerCode"]
                logger.debug(f"acquirer code from api response is: {new_txn_acquirer_code_api_1}")
                new_txn_org_code_api_1 = response["orgCode"]
                logger.debug(f"org_code from api response is: {new_txn_org_code_api_1}")
                new_txn_mid_api_1 = response["mid"]
                logger.debug(f"mid from api response is: {new_txn_mid_api_1}")
                new_txn_tid_api_1 = response["tid"]
                logger.debug(f"tid from api response is: {new_txn_tid_api_1}")
                new_txn_txn_type_api_1 = response["txnType"]
                logger.debug(f"txn type from api response is: {new_txn_txn_type_api_1}")
                new_txn_date_api_1 = response["createdTime"]
                logger.debug(f"date from api response is: {new_txn_date_api_1}")

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
                                     "org_code_2": new_txn_org_code_api_1,
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
                                      "ptm_gateway": "RAZORPAY",
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
                                      "mid": mid,
                                      "tid": tid,
                                      "mid_1": mid,
                                      "tid_1": tid,
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"fetched status from txn table is : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"fetched amount from txn table is : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"fetched state from txn table is : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"fetched payment_gateway from txn table is : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"fetched acquirer_code from txn table is : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched bank_code from txn table is : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"fetched tid from txn table is : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"fetched mid from txn table is : {mid_db}")

                query = f"select * from upi_txn where txn_id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db}")

                query = f"select * from txn where id='{new_txn_id_2}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_1 = result["status"].iloc[0]
                logger.debug(f"fetched status from txn table is : {new_txn_status_db_1}")
                new_txn_payment_mode_db_1 = result["payment_mode"].iloc[0]
                logger.debug(f"fetched payment_mode from txn table is : {new_txn_payment_mode_db_1}")
                new_txn_amount_db_1 = int(result["amount"].iloc[0])
                logger.debug(f"fetched amount from txn table is : {new_txn_amount_db_1}")
                new_txn_state_db_1 = result["state"].iloc[0]
                logger.debug(f"fetched state from txn table is : {new_txn_state_db_1}")
                new_txn_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                logger.debug(f"fetched payment_gateway from txn table is : {new_txn_payment_gateway_db_1}")
                new_txn_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                logger.debug(f"fetched acquirer_code from txn table is : {new_txn_acquirer_code_db_1}")
                new_txn_bank_code_db_1 = result["bank_code"].iloc[0]
                logger.debug(f"fetched bank_code from txn table is : {new_txn_bank_code_db_1}")
                new_txn_settlement_status_db_1 = result["settlement_status"].iloc[0]
                logger.debug(f"fetched settlement_status from txn table is : {new_txn_settlement_status_db_1}")
                new_txn_tid_db_1 = result['tid'].values[0]
                logger.debug(f"fetched tid from txn table is : {new_txn_tid_db_1}")
                new_txn_mid_db_1 = result['mid'].values[0]
                logger.debug(f"fetched mid from txn table is : {new_txn_mid_db_1}")

                query = f"select * from upi_txn where txn_id='{new_txn_id_2}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_1 = result["status"].iloc[0]
                logger.debug(f"fetched upi_status from upi_txn table is : {new_txn_upi_status_db_1}")
                new_txn_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {new_txn_upi_txn_type_db_1}")
                new_txn_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {new_txn_upi_bank_code_db_1}")
                new_txn_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {new_txn_upi_mc_id_db_1}")

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
                    "ptm_gateway": payment_gateway_db,
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
                    "mid_1": new_txn_mid_db_1,
                    "tid_1": new_txn_tid_db_1,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation----------------------------------------------
        # -----------------------------------------Start of Portal Validation----------------------------------------
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
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str(amount) + ".00",
                    "username_2": app_username,
                    "txn_id_2": new_txn_id_2,
                    "date_time_2": date_and_time_portal_new
                }
                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time_2}")
                transaction_id_2 = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount_2}")
                rr_number_2 = transaction_details[0]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number_2}")
                transaction_type_2 = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type_2}")
                status_2 = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status_2}")
                username_2 = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username_2}")

                date_time_original = transaction_details[1]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time_original}")
                transaction_id_original = transaction_details[1]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id_original}")
                total_amount_original = transaction_details[1]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount_original}")
                rr_number_original = transaction_details[1]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number_original}")
                transaction_type_original = transaction_details[1]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type_original}")
                status_original = transaction_details[1]['Status']
                logger.debug(f"status from portal is: {status_original}")
                username_original = transaction_details[1]['Username']
                logger.debug(f"username from portal is: {username_original}")

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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(original_created_time)
                expected_charge_slip_values = {'PAID BY:': 'UPI',
                                               'merchant_ref_no': 'Ref # ' + str(order_id),
                                               'RRN': str(original_rrn),
                                               'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                               'date': txn_date,
                                               'time': txn_time,
                                               }
                logger.debug(f"expected_charge_slip_values : {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(original_txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation----------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_251():
    """
    Sub Feature Code: UI_Common_PM_RP_2_UPI_failed_callback_before_expiry_RAZORPAY_AutoRefund_Disabled
    Sub Feature Description: Performing two UPI Collect failed callback via RAZORPAY after expiry the  when auto refund is disabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 251: TC_251
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
        # -----------------------------PreConditions(Setup to be done for the test case)-------------------------------
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
        logger.debug(f"Query result, pgMerchantId : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id: {upi_mc_id}")
        upi_account_id = result['pgMerchantId'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Query result, tid: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Query result, mid: {mid}")

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
            logger.info(f"Entered amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")

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
            logger.info(f"generated rrn is {rrn}")
            amount_api = amount * 100
            logger.info(f"amount is: {amount_api}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_failed')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn

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

            logger.debug("Performing 2nd callback")
            rrn_2 = str(random.randint(1000000000000, 9999999999999))
            logger.info(f"generated rrn is {rrn_2}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_failed')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn_2

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

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
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
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid from txn table is : {mid_db}")
            # --------------------------------------------------------------------------------------------------------
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
                app_payment_status = app_payment_status.split(':')[1]
                logger.info(f"fetching status from history page: {app_payment_status}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"fetching payment mode from history page: {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"fetching txn id from history page: {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"fetching amount from history page: {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"fetching date from history page: {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"fetching settlement_status from history page: {app_settlement_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"fetching customer name from history page: {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"fetching payer name from history page: {app_payer_name}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"fetching order id from history page: {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"fetching payment msg from history page: {app_payment_msg}")

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
                logger.debug(f"status from api response is: {status_api}")
                amount_api = response["amount"]
                logger.debug(f"amount from api response is: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment mode from api response is: {payment_mode_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer code from api response is: {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement status from api response is: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer code from api response is: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn type from api response is: {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"date from api response is: {date_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code from api response is: {org_code_api}")
                tid_api = response["tid"]
                logger.debug(f"tid from api response is: {tid_api}")
                mid_api = response["mid"]
                logger.debug(f"mid from api response is: {mid_api}")
                state_api = response["states"][0]
                logger.debug(f"txn_state from api response is: {state_api}")

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
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
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db}")

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
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code_portal}")

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
def test_common_100_103_252():
    """
    Sub Feature Code: UI_Common_PM_RP_2_UPI_failed_callback_before_expiry_RAZORPAY_AutoRefund_Disabled
    Sub Feature Description: Performing two  UPI Collect failed callback via RAZORPAY before expiry the  when autorefund is disabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 252: TC_252
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
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(
            f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Query result, pgMerchantId : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id: {upi_mc_id}")
        upi_account_id = result['pgMerchantId'].values[0]
        logger.debug(f"upi account id from db : {upi_account_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Query result, tid: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Query result, mid: {mid}")

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
            logger.info(f"Entered amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")

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

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{str(order_id)}' order by created_time desc limit 1"
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
            logger.info(f"generated rrn is {rrn}")
            amount_api = amount * 100
            logger.info(f"amount is: {amount_api}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_failed')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn

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

            logger.debug("Performing 2nd callback")
            rrn_2 = str(random.randint(1000000000000, 9999999999999))
            logger.info(f"generated rrn is {rrn_2}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_failed')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn_2

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

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
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
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid from txn table is : {mid_db}")
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
                app_payment_status = app_payment_status.split(':')[1]
                logger.info(f"fetching status from history page: {app_payment_status}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"fetching payment mode from history page: {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"fetching txn id from history page: {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"fetching amount from history page: {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"fetching date from history page: {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"fetching settlement_status from history page: {app_settlement_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"fetching customer name from history page: {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"fetching payer name from history page: {app_payer_name}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"fetching order id from history page: {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"fetching payment msg from history page: {app_payment_msg}")

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
                logger.debug(f"status from api response is: {status_api}")
                amount_api = response["amount"]
                logger.debug(f"amount from api response is: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment mode from api response is: {payment_mode_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer code from api response is: {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement status from api response is: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer code from api response is: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn type from api response is: {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"date from api response is: {date_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code from api response is: {org_code_api}")
                tid_api = response["tid"]
                logger.debug(f"tid from api response is: {tid_api}")
                mid_api = response["mid"]
                logger.debug(f"mid from api response is: {mid_api}")
                state_api = response["states"][0]
                logger.debug(f"txn_state from api response is: {state_api}")

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
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
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db}")

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
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code_portal}")

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
def test_common_100_103_253():
    """
    Sub Feature Code: UI_Common_PM_RP_2_UPI_failed_callback_before_expiry_RAZORPAY_AutoRefund_Enabled
    Sub Feature Description: Performing two UPI Collect failed callback via RAZORPAY before expiry the  when autorefund is enabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 253: TC_253
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
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(
            f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Query result, pgMerchantId : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id: {upi_mc_id}")
        upi_account_id = result['pgMerchantId'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Query result, tid: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Query result, mid: {mid}")

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
            logger.info(f"Entered amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")

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

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{str(order_id)}' order by created_time desc limit 1"
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
            logger.info(f"generated rrn is {rrn}")
            amount_api = amount * 100
            logger.info(f"amount is: {amount_api}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_failed')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn

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

            logger.debug("Performing 2nd callback")
            rrn_2 = str(random.randint(1000000000000, 9999999999999))
            logger.info(f"generated rrn is {rrn_2}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_failed')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn_2

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

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
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
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid from txn table is : {mid_db}")

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
                app_payment_status = app_payment_status.split(':')[1]
                logger.info(f"fetching status from history page: {app_payment_status}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"fetching payment mode from history page: {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"fetching txn id from history page: {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"fetching amount from history page: {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"fetching date from history page: {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"fetching settlement_status from history page: {app_settlement_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"fetching customer name from history page: {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"fetching payer name from history page: {app_payer_name}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"fetching order id from history page: {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"fetching payment msg from history page: {app_payment_msg}")

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
                logger.debug(f"status from api response is: {status_api}")
                amount_api = response["amount"]
                logger.debug(f"amount from api response is: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment mode from api response is: {payment_mode_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer code from api response is: {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement status from api response is: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer code from api response is: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn type from api response is: {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"date from api response is: {date_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code from api response is: {org_code_api}")
                tid_api = response["tid"]
                logger.debug(f"tid from api response is: {tid_api}")
                mid_api = response["mid"]
                logger.debug(f"mid from api response is: {mid_api}")
                state_api = response["states"][0]
                logger.debug(f"txn_state from api response is: {state_api}")

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
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
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db}")

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
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code_portal}")

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
def test_common_100_103_254():
    """
    Sub Feature Code: UI_Common_PM_RP_2_UPI_failed_callback_after_expiry_RAZORPAY_AutoRefund_Enabled
    Sub Feature Description: Performing two UPI failed callback via RAZORPAY after expiry the when autorefund is enabled
    TC naming code description:100: Payment Method, 103: RemotePay, 254: TC_254
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
        logger.debug(f"Query result, pgMerchantId : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id: {upi_mc_id}")
        upi_account_id = result['pgMerchantId'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Query result, tid: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Query result, mid: {mid}")

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
            logger.info(f"Entered amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")

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
            logger.debug(f"Query result, txn_ref : {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.debug(f"Query result, txn_ref_3 : {txn_ref_3}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            logger.info(f"generated rrn is {rrn}")
            amount_api = amount * 100
            logger.info(f"amount is: {amount_api}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_failed')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn

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

            logger.debug("Performing 2nd callback")
            rrn_2 = str(random.randint(1000000000000, 9999999999999))
            logger.info(f"generated rrn is {rrn_2}")

            api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_failed')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = amount * 100
            api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn_2

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
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid from txn table is : {mid_db}")

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
                app_payment_status = app_payment_status.split(':')[1]
                logger.info(f"fetching status from history page: {app_payment_status}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"fetching payment mode from history page: {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"fetching txn id from history page: {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"fetching amount from history page: {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"fetching date from history page: {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"fetching settlement_status from history page: {app_settlement_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"fetching customer name from history page: {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"fetching payer name from history page: {app_payer_name}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"fetching order id from history page: {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"fetching payment msg from history page: {app_payment_msg}")

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
                logger.debug(f"status from api response is: {status_api}")
                amount_api = response["amount"]
                logger.debug(f"amount from api response is: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment mode from api response is: {payment_mode_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer code from api response is: {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement status from api response is: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer code from api response is: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn type from api response is: {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"date from api response is: {date_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code from api response is: {org_code_api}")
                tid_api = response["tid"]
                logger.debug(f"tid from api response is: {tid_api}")
                mid_api = response["mid"]
                logger.debug(f"mid from api response is: {mid_api}")
                state_api = response["states"][0]
                logger.debug(f"txn_state from api response is: {state_api}")

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
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
                logger.debug(f"fetched upi_status from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db}")

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
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code_portal}")

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