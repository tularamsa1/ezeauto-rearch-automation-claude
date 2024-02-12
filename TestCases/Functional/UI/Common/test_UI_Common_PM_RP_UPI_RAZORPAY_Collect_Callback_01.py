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
def test_common_100_103_235():
    """
    Sub Feature Code: UI_Common_PM_UPI_success_callback_before_expiry_AutoRefund_Enabled_RAZORPAY
    Sub Feature Description: Performing a  UPI Collect success callback via RAZORPAY before expiry when auto refund is enabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 235: TC_235
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
        logger.debug(f"Fetching pg_merchant_id from upi_merchant_config table: {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching upi_mc_id from upi_merchant_config table: {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Fetching tid from upi_merchant_config table: {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Fetching mid from upi_merchant_config table: {mid}")

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
            logger.debug(f"fetched status_db from txn table: {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode_db from txn table: {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount_db from txn table: {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state_db from txn table: {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway_db from txn table: {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code_db from txn table: {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code_db from txn table: {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status_db from txn table: {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid_db from txn table: {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid_db from txn table: {mid_db}")

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
                logger.debug(f"fetched app_payment_status from txn_history_page is : {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"fetched app_date_and_time from txn_history_page is : {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"fetched app_payment_mode from txn_history_page is : {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"fetched app_txn_id from txn_history_page is : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"fetched app_amount from txn_history_page is : {app_amount}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"fetched app_rrn from txn_history_page is : {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"fetched app_customer_name from txn_history_page is : {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"fetched app_settlement_status from txn_history_page is : {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.debug(f"fetched app_payer_name from txn_history_page is : {app_payer_name}")
                app_payment_status = app_payment_status.split(':')[1]
                logger.debug(f"processed app_payment_status: {app_payment_status}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"fetched app_order_id from txn_history_page is : {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"fetched app_payment_msg from txn_history_page is : {app_payment_msg}")

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
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"fetched status_api from response is : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"fetched amount_api from response is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"fetched payment_mode_api from response is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"fetched state_api from response is : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"fetched rrn_api from response is : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"fetched settlement_status_api from response is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"fetched issuer_code_api from response is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"fetched acquirer_code_api from response is : {acquirer_code_api}")
                orgCode_api = response["orgCode"]
                logger.debug(f"fetched orgCode_api from response is : {orgCode_api}")
                mid_api = response["mid"]
                logger.debug(f"fetched mid_api from response is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"fetched tid_api from response is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"fetched txn_type_api from response is : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"fetched date_api from response is : {date_api}")
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
                logger.debug(f"fetched upi_status_db from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type_db from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code_db from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id_db from upi_txn table is : {upi_mc_id_db}")

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
                logger.debug(f"fetched date_time from portal is : {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"fetched transaction_id from portal is : {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total_amount from portal is : {total_amount}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal is : {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"fetched transaction_type from portal is : {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"fetched status from portal is : {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"fetched username from portal is : {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code_portal from portal is : {auth_code_portal}")

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
                logger.debug(f"expected_values : {expected_charge_slip_values}")
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
def test_common_100_103_236():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Failed_Via_UPI_Callback_RAZORPAY
    Sub Feature Description: Verification of a failed UPI txn via RAZORPAY using Callback
    TC naming code description: 100: Payment Method, 103: RemotePay, 236: TC_236
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
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' and" \
                f" bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(
            f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f" pg_merchant_id from db : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f" vpa from db : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f" upi_mc_id from db : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f" tid from db : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f" mid from db : {mid}")
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

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{str(order_id)}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")

            query = f"select * from upi_txn where org_code = '{str(org_code)}' AND txn_id = '{str(txn_id)}';"
            logger.debug(f"Query to fetch txn_ref from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]
            logger.debug(f"Query result, txn_ref : {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.debug(f"Query result, txn_ref3 : {txn_ref_3}")
            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount_api = amount * 100

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
            logger.debug(f"fetched status_db from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode_db from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount_db from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state_db from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway_db from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code_db from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code_db from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status_db from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid_db from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid_db from txn table is : {mid_db}")
            # ---------------------------------------------------------------------------------------------
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
                logger.debug(f"fetched app_payment_status from txn_history_page is : {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"fetched app_date_and_time from txn_history_page is : {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"fetched app_payment_mode from txn_history_page is : {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"fetched app_txn_id from txn_history_page is : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"fetched app_amount from txn_history_page is : {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"fetched app_customer_name from txn_history_page is : {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"fetched app_settlement_status from txn_history_page is : {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.debug(f"fetched app_payer_name from txn_history_page is : {app_payer_name}")
                app_payment_status = app_payment_status.split(':')[1]
                logger.debug(f"processed app_payment_status: {app_payment_status}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"fetched app_order_id from txn_history_page is : {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"fetched app_payment_msg from txn_history_page is : {app_payment_msg}")

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
                logger.debug(f"fetched status_api from response is : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"fetched amount_api from response is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"fetched payment_mode_api from response is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"fetched state_api from response is : {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"fetched settlement_status_api from response is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"fetched issuer_code_api from response is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"fetched acquirer_code_api from response is : {acquirer_code_api}")
                orgCode_api = response["orgCode"]
                logger.debug(f"fetched orgCode_api from response is : {orgCode_api}")
                mid_api = response["mid"]
                logger.debug(f"fetched mid_api from response is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"fetched tid_api from response is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"fetched txn_type_api from response is : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"fetched date_api from response is : {date_api}")

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
                logger.debug(f"fetched upi_status_db from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type_db from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code_db from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id_db from upi_txn table is : {upi_mc_id_db}")

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
                logger.debug(f"fetched date_time from portal is : {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"fetched transaction_id from portal is : {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total_amount from portal is : {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"fetched transaction_type from portal is : {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"fetched status from portal is : {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"fetched username from portal is : {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code_portal from portal is : {auth_code_portal}")

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
                # ---------------------------------------------------------------------------------------------
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
def test_common_100_103_238():
    """
    Sub Feature Code: UI_Common_PM_UPI_Collect_success_callback_after_expiry_AutoRefund_Disabled_RAZORPAY
    Sub Feature Description: Performing a  UPI Collect success callback via RAZORPAY after expiry when auto refund is disabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 238: TC_238
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
        logger.debug(f"Query to fetch upi_mc_id  and pgMerchantId from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f" pg_merchant_id from db : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f" upi_mc_id from db : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f" tid from db : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f" mid from db : {mid}")
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
            amount = random.randint(601, 700)
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
            logger.debug(f"Query result, txn_ref : {txn_ref} and txn_ref_3 : {txn_ref_3}")
            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))

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

            query = f"select * from txn where orig_txn_id = '{str(txn_id)}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {rrn}")
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
            logger.debug(f"fetched status_db from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode_db from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount_db from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state_db from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway_db from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code_db from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code_db from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status_db from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid_db from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid_db from txn table is : {mid_db}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": upi_txn_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn),
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
                txn_history_page.click_on_transaction_by_txn_id(upi_txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"fetched app_payment_status from txn_history_page is : {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"fetched app_date_and_time from txn_history_page is : {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"fetched app_payment_mode from txn_history_page is : {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"fetched app_txn_id from txn_history_page is : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"fetched app_amount from txn_history_page is : {app_amount}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"fetched app_rrn from txn_history_page is : {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"fetched app_customer_name from txn_history_page is : {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"fetched app_settlement_status from txn_history_page is : {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.debug(f"fetched app_payer_name from txn_history_page is : {app_payer_name}")
                app_payment_status = app_payment_status.split(':')[1]
                logger.debug(f"processed app_payment_status: {app_payment_status}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"fetched app_order_id from txn_history_page is : {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"fetched app_payment_msg from txn_history_page is : {app_payment_msg}")

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
                response = [x for x in response["txns"] if x["txnId"] == upi_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"fetched status_api from response is : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"fetched amount_api from response is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"fetched payment_mode_api from response is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"fetched state_api from response is : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"fetched rrn_api from response is : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"fetched settlement_status_api from response is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"fetched issuer_code_api from response is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"fetched acquirer_code_api from response is : {acquirer_code_api}")
                orgCode_api = response["orgCode"]
                logger.debug(f"fetched orgCode_api from response is : {orgCode_api}")
                mid_api = response["mid"]
                logger.debug(f"fetched mid_api from response is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"fetched tid_api from response is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"fetched txn_type_api from response is : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"fetched date_api from response is : {date_api}")

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

                query = f"select * from upi_txn where txn_id='{upi_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"fetched upi_status_db from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type_db from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code_db from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id_db from upi_txn table is : {upi_mc_id_db}")

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
                    "txn_id": upi_txn_id,
                    "rrn": rrn,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"fetched date_time from portal is : {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"fetched transaction_id from portal is : {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total_amount from portal is : {total_amount}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal is : {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"fetched transaction_type from portal is : {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"fetched status from portal is : {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"fetched username from portal is : {username}")

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
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date, 'time': txn_time,
                                   }
                logger.debug(f"expected_values : {expected_values}")
                receipt_validator.perform_charge_slip_validations(upi_txn_id,
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
def test_common_100_103_240():
    """
    Sub Feature Code: UI_Common_PM_UPI_Collect_success_callback_after_expiry_AutoRefund_Enabled_RAZORPAY
    Sub Feature Description: Verification of a one upi collect success callback after expiry via RAZORPAY when auto refund is enalbed.
    TC naming code description: 100: Payment Method, 103: RemotePay, 240: TC_240
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
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id: {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Query result, tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"Query result, mid : {mid}")
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
            amount = random.randint(601, 700)
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

            query = f"SELECT * FROM txn WHERE org_code = '{org_code}' AND external_ref = '{order_id}' ORDER BY created_time DESC LIMIT 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_1 = result["id"].values[0]
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
            logger.debug(f"fetched status_db from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode_db from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount_db from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state_db from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway_db from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code_db from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code_db from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status_db from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid_db from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid_db from txn table is : {mid_db}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution-----------------------------------------------
        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "REFUND_PENDING",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id_1,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "REFUND PENDING",
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
                txn_history_page.click_on_transaction_by_txn_id(txn_id_1)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"fetched app_payment_status from txn_history_page is : {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"fetched app_date_and_time from txn_history_page is : {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"fetched app_payment_mode from txn_history_page is : {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"fetched app_txn_id from txn_history_page is : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"fetched app_amount from txn_history_page is : {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"fetched app_customer_name from txn_history_page is : {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"fetched app_settlement_status from txn_history_page is : {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.debug(f"fetched app_payer_name from txn_history_page is : {app_payer_name}")
                app_payment_status = app_payment_status.split(':')[1]
                logger.debug(f"processed app_payment_status: {app_payment_status}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"fetched app_order_id from txn_history_page is : {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"fetched app_payment_msg from txn_history_page is : {app_payment_msg}")

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
        # -----------------------------------------End of App Validation------------------------------------------------
        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "REFUND_PENDING",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "REFUND_PENDING",
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
                response = [x for x in response["txns"] if x["txnId"] == txn_id_1][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"fetched status_api from response is : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"fetched amount_api from response is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"fetched payment_mode_api from response is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"fetched state_api from response is : {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"fetched settlement_status_api from response is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"fetched issuer_code_api from response is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"fetched acquirer_code_api from response is : {acquirer_code_api}")
                orgCode_api = response["orgCode"]
                logger.debug(f"fetched orgCode_api from response is : {orgCode_api}")
                mid_api = response["mid"]
                logger.debug(f"fetched mid_api from response is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"fetched tid_api from response is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"fetched txn_type_api from response is : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"fetched date_api from response is : {date_api}")

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
        # -----------------------------------------End of API Validation------------------------------------------------
        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "REFUND_PENDING",
                    "pmt_state": "REFUND_PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "REFUND_PENDING",
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

                query = f"select * from upi_txn where txn_id='{txn_id_1}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"fetched upi_status_db from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type_db from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code_db from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id_db from upi_txn table is : {upi_mc_id_db}")

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
        # -----------------------------------------End of DB Validation-------------------------------------------------
        # -----------------------------------------Start of Portal Validation-------------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "REFUND_PENDING",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id_1,
                    "auth_code": "-" if auth_code is None else auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"fetched date_time from portal is : {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"fetched transaction_id from portal is : {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total_amount from portal is : {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"fetched transaction_type from portal is : {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"fetched status from portal is : {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"fetched username from portal is : {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code_portal from portal is : {auth_code_portal}")

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
def test_common_100_103_241():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Failed_Via_UPI_Callback_After_Expiry_AutoRefund_Disabled_RAZORPAY
    Sub Feature Description: Performing a  UPI Collect failed callback via RAZORPAY after expiry when auto refund is disabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 241: TC_241
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
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id: {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"Query result, tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"mid from db : {mid}")
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
            logger.debug(f"Query result, txn_ref : {txn_ref}")
            txn_ref_3 = result['txn_ref3'].values[0]
            logger.debug(f"Query result, txn_ref_3 : {txn_ref_3}")
            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount_api = amount * 100

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
            logger.debug(f"fetched status_db from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode_db from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount_db from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state_db from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway_db from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code_db from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code_db from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status_db from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid_db from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid_db from txn table is : {mid_db}")
            # ---------------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------
        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------------------
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
                logger.debug(f"fetched app_payment_status from txn_history_page is : {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"fetched app_date_and_time from txn_history_page is : {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"fetched app_payment_mode from txn_history_page is : {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"fetched app_txn_id from txn_history_page is : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"fetched app_amount from txn_history_page is : {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"fetched app_customer_name from txn_history_page is : {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"fetched app_settlement_status from txn_history_page is : {app_settlement_status}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.debug(f"fetched app_payer_name from txn_history_page is : {app_payer_name}")
                app_payment_status = app_payment_status.split(':')[1]
                logger.debug(f"processed app_payment_status: {app_payment_status}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"fetched app_order_id from txn_history_page is : {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"fetched app_payment_msg from txn_history_page is : {app_payment_msg}")

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
        # -----------------------------------------End of App Validation------------------------------------------------
        # -----------------------------------------Start of API Validation----------------------------------------------
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
                logger.debug(f"fetched status_api from response is : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"fetched amount_api from response is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"fetched payment_mode_api from response is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"fetched state_api from response is : {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"fetched settlement_status_api from response is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"fetched issuer_code_api from response is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"fetched acquirer_code_api from response is : {acquirer_code_api}")
                orgCode_api = response["orgCode"]
                logger.debug(f"fetched orgCode_api from response is : {orgCode_api}")
                mid_api = response["mid"]
                logger.debug(f"fetched mid_api from response is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"fetched tid_api from response is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"fetched txn_type_api from response is : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"fetched date_api from response is : {date_api}")
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
                # -----------------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------
        # -----------------------------------------Start of DB Validation-----------------------------------------------
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
                logger.debug(f"fetched upi_status_db from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched upi_txn_type_db from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched upi_bank_code_db from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id_db from upi_txn table is : {upi_mc_id_db}")

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
        # -----------------------------------------End of DB Validation-------------------------------------------------

        # -----------------------------------------Start of Portal Validation-------------------------------------------
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
                logger.debug(f"fetched date_time from portal is : {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"fetched transaction_id from portal is : {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total_amount from portal is : {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"fetched transaction_type from portal is : {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"fetched status from portal is : {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"fetched username from portal is : {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code_portal from portal is : {auth_code_portal}")

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
        # -----------------------------------------End of Portal Validation---------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
