import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.uiVal
def test_common_100_112_043():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_Success_Razorpay_MultiAcc
    Sub Feature Description: Multi Account - Verification of a Remote Pay successful credit card txn
    TC naming code description:100: Payment Method, 112: MultiAcc_CNP_CARD, 043: TC043
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
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
        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"account_label_name: {account_label_name}")
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"Query result, org_code : {acc_label_id}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(601, 700)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "accountLabel": str(account_label_name)})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                ui_browser.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(ui_browser)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("ezeauto")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("12")
                remote_pay_txn.enterCreditCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_success_pmt_btn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected message is:  {expected_message}")

                if success_message == expected_message:
                    pass
                else:
                    raise Exception("Success Message is not matching.")

                query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                Txn_id = result['id'].values[0]
                logger.debug(f"Query result, Txn_id : {Txn_id}")
                auth_code = result['auth_code'].values[0]
                logger.debug(f"Query result, auth_code : {auth_code}")
                rrn = result['rr_number'].values[0]
                logger.debug(f"Query result, rrn : {rrn}")
                txn_id = result['id'].values[0]
                status = result['status'].values[0]
                logger.debug(f"Query result, status : {status}")
                customer_name = result['customer_name'].values[0]
                logger.debug(f"Query result, customer_name : {customer_name}")
                payer_name = result['payer_name'].values[0]
                logger.debug(f"Query result, payer_name : {payer_name}")
                mid = result['mid'].values[0]
                logger.debug(f"Query result, mid : {mid}")
                tid = result['tid'].values[0]
                logger.debug(f"Query result, tid : {tid}")
                posting_date = result['created_time'].values[0]
                logger.debug(f"Query result, posting_date : {posting_date}")
                org_code_txn = result['org_code'].values[0]
                logger.debug(f"Query result, org_code_txn : {org_code_txn}")
                txn_type = result['txn_type'].values[0]
                logger.debug(f"Query result, txn_type : {txn_type}")
                label_ids = str(result['label_ids'].values[0]).strip(',')
                logger.debug(f"Query result, label_ids : {label_ids}")
                settle_status = result['settlement_status'].values[0]
                logger.debug(f"Query result, txn_settle_status : {settle_status}")
                created_time = result['created_time'].values[0]
                logger.debug(f"Query result, created_time from db : {created_time}")

                query = f"select * from cnp_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of cnp_txn table is : {result}")
                cnp_txn_rrn = result['rr_number'].values[0]
                logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
                cnp_txn_state = result['state'].values[0]
                logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
                cnp_txn_acquirer_code = result['acquirer_code'].values[0]
                logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
                cnp_txn_auth_code = result['auth_code'].values[0]
                logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
                cnp_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
                cnp_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Query result, cnp_payment_flow : {cnp_payment_flow}")

                query = f"select * from cnpware_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                logger.debug(f"Query result of cnpware_txn table is : {result}")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
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
                # --------------------------------------------------------------------------------------------
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": customer_name,
                    "settle_status": settle_status,
                    "auth_code": auth_code,
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                logger.debug("Login completed in the app.")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Waiting completed for txn history page.")
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
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "order_id": payment_order_id,
                    "msg": payment_status_msg,
                    "customer_name": payment_customer_name,
                    "settle_status": payment_settlement_status,
                    "auth_code": payment_auth_code,
                    "date": app_date_and_time
                }
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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnp_pmt_card_type": "CREDIT",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date,
                    "tid": tid,
                    "mid": mid,
                    "acc_label_id": str(account_label_name)
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response received for transaction list api is for txn_id {txn_id} : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                amount_api = response["amount"]
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                payment_card_brand = response["paymentCardBrand"]
                logger.debug(f"Fetching Transaction payment Card Brand from transaction api : {payment_card_brand} ")
                payment_card_type = response["paymentCardType"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {payment_card_type} ")
                acquirer_code__api = response["acquirerCode"]
                logger.debug(
                    f"Fetching Transaction payment Card  acquirer_code from transaction api : {acquirer_code__api} ")
                settlement_status_api = response["settlementStatus"]
                logger.debug(
                    f"Fetching Transaction payment Card settlement_status from transaction api : {settlement_status_api} ")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching Transaction payment Card issuer_code from transaction api : {issuer_code_api} ")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching Transaction payment txn_type from transaction api : {txn_type_api} ")
                date_api = response["postingDate"]
                logger.debug(f"Fetching Transaction payment Card date from transaction api : {date_api} ")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching Transaction payment Card org code from transaction api : {org_code_api} ")
                tid_api = response["tid"]
                logger.debug(f"Fetching Transaction payment Card tid from transaction api : {tid_api} ")
                mid_api = response["mid"]
                logger.debug(f"Fetching Transaction payment Card mid from transaction api : {mid_api} ")
                account_label_name_api = response["accountLabel"]
                logger.debug(
                    f"Fetching Transaction payment Card account_label from transaction api : {account_label_name_api} ")
                txn_state = response["states"][0]
                logger.debug(
                    f"Fetching Transaction payment Card txn state from transaction api : {account_label_name_api} ")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "cnp_pmt_card_brand": payment_card_brand,
                    "cnp_pmt_card_type": payment_card_type,
                    "pmt_state": txn_state,
                    "acquirer_code": acquirer_code__api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "tid": tid_api,
                    "mid": mid_api,
                    "acc_label_id": str(account_label_name_api)
                }

                logger.debug(f"actualAPIValues: {actual_api_values}")
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
                # --------------------------------------------------------------------------------------------

                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "COMPLETED",
                    "tid": tid,
                    "mid": mid,
                    "acc_label_id": str(acc_label_id)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table in db validation is : {result}")
                pmt_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching pmt_status_db from txn table : {pmt_status_db} ")
                pmt_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching pmt_mode_db from txn table : {pmt_mode_db} ")
                txn_amt_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching txn_amt_db from txn table : {txn_amt_db} ")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settle_status_db from txn table : {settle_status_db} ")
                pmt_state_db = result["state"].iloc[0]
                logger.debug(f"Fetching pmt_state_db from txn table : {pmt_state_db} ")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching payment_gateway_db from txn table : {payment_gateway_db} ")
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                logger.debug(f"Query result, tid : {tid_db} and mid : {mid_db}")

                query = f"select * from payment_intent where id='{payment_intent_id}';"
                logger.debug(f"Query to fetch payment_intent table : {query} ")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of payment_intent table is : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table is : {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": pmt_status_db,
                    "pmt_state": pmt_state_db,
                    "pmt_mode": pmt_mode_db,
                    "txn_amt": txn_amt_db,
                    "settle_status": settle_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status,
                    "tid": tid_db,
                    "mid": mid_db,
                    "acc_label_id": str(label_ids)
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
                # ---------------------------------------------------------------------------------------------
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

                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else str(rrn),
                    "acc_label": str(account_label_name)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code,
                    "rrn": rr_number,
                    "acc_label": labels
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {'CARD TYPE': 'MasterCard',
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date,
                                   'time': txn_time,
                                   "AUTH CODE": auth_code
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
@pytest.mark.chargeSlipVal
@pytest.mark.uiVal
def test_common_100_112_049():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_Success_Razorpay_with_2nd_label_MultiAcc
    Sub Feature Description: Multi Account - Performing a successful credit card txn via CNP link second account (ex:acc2 label)
    TC naming code description: 100: Payment Method, 112: MultiAcc_CNP_CARD, 049: TC049
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
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
        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name2']
        print(f"account_label_name: {account_label_name}")
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' AND acc_label_id=(select id from label " \
                        f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"Query result, org_code : {acc_label_id}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(601, 700)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "accountLabel": str(account_label_name)})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                ui_browser.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(ui_browser)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("ezeauto")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("12")
                remote_pay_txn.enterCreditCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_success_pmt_btn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expiryMessage is:  {expected_message}")

                if success_message == expected_message:
                    pass
                else:
                    raise Exception("Success Message is not matching.")
                query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                Txn_id = result['id'].values[0]
                logger.debug(f"Query result, Txn_id : {Txn_id}")
                auth_code = result['auth_code'].values[0]
                rrn = result['rr_number'].values[0]
                txn_id = result['id'].values[0]
                status = result['status'].values[0]
                customer_name = result['customer_name'].values[0]
                payer_name = result['payer_name'].values[0]
                mid = result['mid'].values[0]
                tid = result['tid'].values[0]
                posting_date = result['created_time'].values[0]
                org_code_txn = result['org_code'].values[0]
                txn_type = result['txn_type'].values[0]
                label_ids = str(result['label_ids'].values[0]).strip(',')
                settle_status = result['settlement_status'].values[0]
                created_time = result['created_time'].values[0]
                logger.debug(f"Query result, created_time from db : {created_time}")
                logger.debug(f"Query result, txn_settle_status : {settle_status}")
                logger.debug(f"Query result, auth_code : {auth_code}")
                logger.debug(f"Query result, status : {status}")
                logger.debug(f"Query result, posting_date : {posting_date}")
                logger.debug(f"Query result, rrn : {rrn}")
                logger.debug(f"Query result, mid : {mid}")
                logger.debug(f"Query result, tid : {tid}")
                logger.debug(f"Query result, customer_name : {customer_name}")
                logger.debug(f"Query result, payer_name : {payer_name}")
                logger.debug(f"Query result, org_code_txn : {org_code_txn}")
                logger.debug(f"Query result, txn_type : {txn_type}")
                logger.debug(f"Query result, label_ids : {label_ids}")

                query = f"select * from cnp_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of cnp_txn table is : {result}")
                cnp_txn_rrn = result['rr_number'].values[0]
                logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
                cnp_txn_state = result['state'].values[0]
                logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
                cnp_txn_acquirer_code = result['acquirer_code'].values[0]
                logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
                cnp_txn_auth_code = result['auth_code'].values[0]
                logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
                cnp_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
                cnp_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Query result, cnp_payment_flow : {cnp_payment_flow}")

                query = f"select * from cnpware_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                logger.debug(f"Query result of cnpware_txn table is : {result}")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
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
                # --------------------------------------------------------------------------------------------
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": customer_name,
                    "settle_status": settle_status,
                    "auth_code": auth_code,
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                logger.debug("Login completed in the app.")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Waiting completed for txn history page.")
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
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "order_id": payment_order_id,
                    "msg": payment_status_msg,
                    "customer_name": payment_customer_name,
                    "settle_status": payment_settlement_status,
                    "auth_code": payment_auth_code,
                    "date": app_date_and_time
                }
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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnp_pmt_card_type": "CREDIT",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date,
                    "tid": tid,
                    "mid": mid,
                    "acc_label_id": str(account_label_name)
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response received for transaction list api is for txn_id {txn_id} : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                amount_api = response["amount"]
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                payment_card_brand = response["paymentCardBrand"]
                logger.debug(f"Fetching Transaction payment Card Brand from transaction api : {payment_card_brand} ")
                payment_card_type = response["paymentCardType"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {payment_card_type} ")
                acquirer_code__api = response["acquirerCode"]
                logger.debug(
                    f"Fetching Transaction payment Card  acquirer_code from transaction api : {acquirer_code__api} ")
                settlement_status_api = response["settlementStatus"]
                logger.debug(
                    f"Fetching Transaction payment Card settlement_status from transaction api : {settlement_status_api} ")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching Transaction payment Card issuer_code from transaction api : {issuer_code_api} ")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching Transaction payment txn_type from transaction api : {txn_type_api} ")
                date_api = response["postingDate"]
                logger.debug(f"Fetching Transaction payment Card date from transaction api : {date_api} ")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching Transaction payment Card org code from transaction api : {org_code_api} ")
                tid_api = response["tid"]
                logger.debug(f"Fetching Transaction payment Card tid from transaction api : {tid_api} ")
                mid_api = response["mid"]
                logger.debug(f"Fetching Transaction payment Card mid from transaction api : {mid_api} ")
                account_label_name_api = response["accountLabel"]
                logger.debug(
                    f"Fetching Transaction payment Card account_label from transaction api : {account_label_name_api} ")
                txn_state = response["states"][0]
                logger.debug(
                    f"Fetching Transaction payment Card txn state from transaction api : {account_label_name_api} ")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "cnp_pmt_card_brand": payment_card_brand,
                    "cnp_pmt_card_type": payment_card_type,
                    "pmt_state": txn_state,
                    "acquirer_code": acquirer_code__api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "tid": tid_api,
                    "mid": mid_api,
                    "acc_label_id": str(account_label_name_api)
                }
                logger.debug(f"actualAPIValues: {actual_api_values}")
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
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "COMPLETED",
                    "tid": tid,
                    "mid": mid,
                    "acc_label_id": str(acc_label_id)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table in db validation is : {result}")
                pmt_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching pmt_status_db from txn table : {pmt_status_db} ")
                pmt_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching pmt_mode_db from txn table : {pmt_mode_db} ")
                txn_amt_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching txn_amt_db from txn table : {txn_amt_db} ")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settle_status_db from txn table : {settle_status_db} ")
                pmt_state_db = result["state"].iloc[0]
                logger.debug(f"Fetching pmt_state_db from txn table : {pmt_state_db} ")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching payment_gateway_db from txn table : {payment_gateway_db} ")
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                logger.debug(f"Query result, tid : {tid_db} and mid : {mid_db}")

                query = f"select * from payment_intent where id='{payment_intent_id}';"
                logger.debug(f"Query to fetch payment_intent table : {query} ")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of payment_intent table is : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table is : {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": pmt_status_db,
                    "pmt_state": pmt_state_db,
                    "pmt_mode": pmt_mode_db,
                    "txn_amt": txn_amt_db,
                    "settle_status": settle_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status,
                    "tid": tid_db,
                    "mid": mid_db,
                    "acc_label_id": str(label_ids)
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
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------

                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else str(rrn),
                    "acc_label": str(account_label_name)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code,
                    "rrn": rr_number,
                    "acc_label": labels
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {'CARD TYPE': 'MasterCard',
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date,
                                   'time': txn_time,
                                   "AUTH CODE": auth_code
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
@pytest.mark.chargeSlipVal
@pytest.mark.uiVal
def test_common_100_112_050():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Success_Razorpay_with_2nd_label_MultiAcc
    Sub Feature Description: Multi Account - Performing a successful Debit card txn via CNP link second account (ex:acc2 label)
    TC naming code description: 100: Payment Method, 112: MultiAcc_CNP_CARD, 050: TC050
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
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
        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name2']
        print(f"account_label_name: {account_label_name}")
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' AND acc_label_id=(select id from label " \
                        f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"Query result, org_code : {acc_label_id}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(601, 700)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "accountLabel": str(account_label_name)})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response['paymentLink']
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Initiating a Remote pay Link")
                ui_browser.goto(payment_link_url)
                logger.info("Remote pay Link initiation completed and opening in a browser")
                remote_pay_txn = RemotePayTxnPage(ui_browser)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info("Enter Debit card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterDebitCardExpiryMonth("12")
                remote_pay_txn.enterDebitCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_success_pmt_btn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expiryMessage is:  {expected_message}")

                if success_message == expected_message:
                    pass
                else:
                    raise Exception("Success Message is not matching.")
                query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                Txn_id = result['id'].values[0]
                logger.debug(f"Query result, Txn_id : {Txn_id}")
                auth_code = result['auth_code'].values[0]
                rrn = result['rr_number'].values[0]
                logger.debug(f"Query result, rrn : {rrn}")
                txn_id = result['id'].values[0]
                status = result['status'].values[0]
                logger.debug(f"Query result, status : {status}")
                customer_name = result['customer_name'].values[0]
                logger.debug(f"Query result, customer_name : {customer_name}")
                payer_name = result['payer_name'].values[0]
                logger.debug(f"Query result, payer_name : {payer_name}")
                mid = result['mid'].values[0]
                logger.debug(f"Query result, mid : {mid}")
                tid = result['tid'].values[0]
                logger.debug(f"Query result, tid : {tid}")
                posting_date = result['created_time'].values[0]
                logger.debug(f"Query result, posting_date : {posting_date}")
                org_code_txn = result['org_code'].values[0]
                logger.debug(f"Query result, org_code_txn : {org_code_txn}")
                txn_type = result['txn_type'].values[0]
                logger.debug(f"Query result, txn_type : {txn_type}")
                label_ids = str(result['label_ids'].values[0]).strip(',')
                logger.debug(f"Query result, label_ids : {label_ids}")
                logger.debug(f"Query result, auth_code : {auth_code}")
                settle_status = result['settlement_status'].values[0]
                logger.debug(f"Query result, txn_settle_status : {settle_status}")
                created_time = result['created_time'].values[0]
                logger.debug(f"Query result, created_time from db : {created_time}")

                query = f"select * from cnp_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of cnp_txn table is : {result}")
                cnp_txn_rrn = result['rr_number'].values[0]
                logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
                cnp_txn_state = result['state'].values[0]
                logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
                cnp_txn_acquirer_code = result['acquirer_code'].values[0]
                logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
                cnp_txn_auth_code = result['auth_code'].values[0]
                logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
                cnp_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
                cnp_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Query result, cnp_payment_flow : {cnp_payment_flow}")

                query = f"select * from cnpware_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                logger.debug(f"Query result of cnpware_txn table is : {result}")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
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
                # --------------------------------------------------------------------------------------------
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": customer_name,
                    "settle_status": settle_status,
                    "auth_code": auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                logger.debug("Login completed in the app.")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Waiting completed for txn history page.")
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
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "order_id": payment_order_id,
                    "msg": payment_status_msg,
                    "customer_name": payment_customer_name,
                    "settle_status": payment_settlement_status,
                    "auth_code": payment_auth_code,
                    "date": app_date_and_time
                }
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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date,
                    "tid": tid,
                    "mid": mid,
                    "acc_label_id": str(account_label_name)
                }

                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response received for transaction list api is for txn_id {txn_id} : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                amount_api = response["amount"]
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                payment_card_brand = response["paymentCardBrand"]
                logger.debug(f"Fetching Transaction payment Card Brand from transaction api : {payment_card_brand} ")
                payment_card_type = response["paymentCardType"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {payment_card_type} ")
                acquirer_code__api = response["acquirerCode"]
                logger.debug(
                    f"Fetching Transaction payment Card  acquirer_code from transaction api : {acquirer_code__api} ")
                settlement_status_api = response["settlementStatus"]
                logger.debug(
                    f"Fetching Transaction payment Card settlement_status from transaction api : {settlement_status_api} ")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching Transaction payment Card issuer_code from transaction api : {issuer_code_api} ")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching Transaction payment txn_type from transaction api : {txn_type_api} ")
                date_api = response["postingDate"]
                logger.debug(f"Fetching Transaction payment Card date from transaction api : {date_api} ")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching Transaction payment Card org code from transaction api : {org_code_api} ")
                tid_api = response["tid"]
                logger.debug(f"Fetching Transaction payment Card tid from transaction api : {tid_api} ")
                mid_api = response["mid"]
                logger.debug(f"Fetching Transaction payment Card mid from transaction api : {mid_api} ")
                account_label_name_api = response["accountLabel"]
                logger.debug(
                    f"Fetching Transaction payment Card account_label from transaction api : {account_label_name_api} ")
                txn_state = response["states"][0]
                logger.debug(
                    f"Fetching Transaction payment Card txn state from transaction api : {account_label_name_api} ")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "cnp_pmt_card_brand": payment_card_brand,
                    "pmt_state": txn_state,
                    "acquirer_code": acquirer_code__api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "tid": tid_api,
                    "mid": mid_api,
                    "acc_label_id": str(account_label_name_api)
                }

                logger.debug(f"actualAPIValues: {actual_api_values}")
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
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "COMPLETED",
                    "tid": tid,
                    "mid": mid,
                    "acc_label_id": str(acc_label_id)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table in db validation is : {result}")
                pmt_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching pmt_status_db from txn table : {pmt_status_db} ")
                pmt_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching pmt_mode_db from txn table : {pmt_mode_db} ")
                txn_amt_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching txn_amt_db from txn table : {txn_amt_db} ")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settle_status_db from txn table : {settle_status_db} ")
                pmt_state_db = result["state"].iloc[0]
                logger.debug(f"Fetching pmt_state_db from txn table : {pmt_state_db} ")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching payment_gateway_db from txn table : {payment_gateway_db} ")
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                logger.debug(f"Query result, tid : {tid_db} and mid : {mid_db}")

                query = f"select * from payment_intent where id='{payment_intent_id}';"
                logger.debug(f"Query to fetch payment_intent table : {query} ")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of payment_intent table is : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table is : {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": pmt_status_db,
                    "pmt_state": pmt_state_db,
                    "pmt_mode": pmt_mode_db,
                    "txn_amt": txn_amt_db,
                    "settle_status": settle_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status,
                    "tid": tid_db,
                    "mid": mid_db,
                    "acc_label_id": str(label_ids)
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
                # ---------------------------------------------------------------------------------------------
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

                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else str(rrn),
                    "acc_label": str(account_label_name)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code,
                    "rrn": rr_number,
                    "acc_label": labels
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {'CARD TYPE': 'MasterCard',
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date,
                                   'time': txn_time,
                                   "AUTH CODE": auth_code
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
