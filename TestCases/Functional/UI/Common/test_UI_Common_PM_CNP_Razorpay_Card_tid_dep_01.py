import random
import sys
import time
import pytest
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, ResourceAssigner, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_103_275():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_Success_RAZORPAY_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a Remote Pay successful credit card txn
    TC naming code description:100: Payment Method,103: RemotePay,275: TC_275
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
        logger.debug(f"Query result of org_employee table is: {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='{org_code}' and payment_gateway = 'RAZORPAY' and payment_mode = 'CNP';"
        logger.debug(f"Query to fetch terminal_dependent_enabled from the DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from merchant_pg_config where org_code = '{str(org_code)}' and payment_gateway = 'RAZORPAY';"
        logger.debug(f"Query to fetch tid from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of merchant_pg_config table is : {result}")
        tid_settings = result['tid'].values[0]
        logger.info(f"tid from setting is: {tid_settings}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 500)
            logger.debug(f"amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")

            query = f"select * from terminal_info where tid='{str(tid_settings)}';"
            logger.debug(f"Query to fetch id from the terminal info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of terminal_info table is : {result}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial_db
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            if not response['success']:
                raise Exception("Api could not initate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                logger.info("Going to payment link url and clicking on it")
                ui_browser.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(ui_browser)
                logger.info("Click on the card")
                remote_pay_txn.clickOnCreditCardToExpand()
                logger.info("Entering the details")
                remote_pay_txn.enterNameOnTheCard("ezeauto")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("12")
                remote_pay_txn.enterCreditCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                logger.info("Click on proceed to pay")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_success_pmt_btn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")

                if success_message == expected_message:
                    pass
                else:
                    raise Exception("Success Message is not matching.")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time from db : {created_time}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")
            rrn_number = result['rr_number'].values[0]
            logger.debug(f"Query result, db rrn_number from db : {rrn_number}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
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
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "auth_code": txn_auth_code,
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                logger.debug("Login completed in the app.")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
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
                logger.debug(f"actualAppValues: {actual_app_values}")
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
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial,
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
                logger.debug(f"status from api response is: {status_api}")
                amount_api = response["amount"]
                logger.debug(f"amount from api response is: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment mode from api response is: {payment_mode_api}")
                payment_card_brand = response["paymentCardBrand"]
                logger.debug(f"payment card brand name from api response is: {payment_card_brand}")
                payment_card_type = response["paymentCardType"]
                logger.debug(f"payment card type from api response is: {payment_card_type}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer code from api response is: {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement status from api response is: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer code from api response is: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn type from api response is: {txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"date from api response is: {date_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code from api response is: {org_code_api}")
                tid_api = response["tid"]
                logger.debug(f"tid from api response is: {tid_api}")
                mid_api = response["mid"]
                logger.debug(f"mid from api response is: {mid_api}")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"device serial from api response is: {device_serial_api}")
                txn_state = response["states"][0]
                logger.debug(f"txn_state from api response is: {txn_state}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "cnp_pmt_card_brand": payment_card_brand,
                    "cnp_pmt_card_type": payment_card_type,
                    "pmt_state": txn_state,
                    "acquirer_code": acquirer_code_api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "tid": tid_api,
                    "mid": mid_api,
                    "device_serial": device_serial_api
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
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "COMPLETED",
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial,
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
                    "device_serial": device_serial_db
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
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "auth_code": "-" if txn_auth_code is None else txn_auth_code,
                    "rrn": "-" if rrn_number is None else rrn_number,
                    "txn_id": txn_id,
                    "date_time": date_and_time_portal
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username}")

                actual_portal_values = {
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "auth_code": auth_code,
                    "rrn": rr_number,
                    "txn_id": transaction_id,
                    "date_time": date_time
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
                logger.info(f"date and time is: {txn_date},{txn_time}")
                expected_charge_slip_values = {'CARD TYPE': 'MasterCard',
                                               'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                               'date': txn_date,
                                               'time': txn_time,
                                               "AUTH CODE": txn_auth_code
                                               }
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
@pytest.mark.appVal
@pytest.mark.portalVal
def test_common_100_103_276():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_Failed_Razorpay_Tid_dep
    Sub Feature Description: Tid Dep - Verification of failed remote pay credit card txn for Razorpay pg
    TC naming code description:100: Payment Method,103: RemotePay,276: TC_276
    """
    expected_failed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications."

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
        logger.debug(f"Query result of org_employee table is: {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='{org_code}' and payment_gateway = 'RAZORPAY' and payment_mode = 'CNP';"
        logger.debug(f"Query to fetch terminal_dependent_enabled from the DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from merchant_pg_config where org_code = '{str(org_code)}' and payment_gateway = 'RAZORPAY';"
        logger.debug(f"Query to fetch tid from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of merchant_pg_config table is : {result}")
        tid_settings = result['tid'].values[0]
        logger.info(f"tid from setting is: {tid_settings}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution--------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            logger.debug(f"amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")

            query = f"select * from terminal_info where tid='{str(tid_settings)}';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of terminal_info table is : {result}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial_db
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            if not response['success']:
                raise Exception("Api could not initate a cnp txn.")
            else:
                response = APIProcessor.send_request(api_details)
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                logger.info("Going to payment link url and clicking on it")
                ui_browser.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(ui_browser)
                logger.info("Click on the card")
                remote_pay_txn.clickOnCreditCardToExpand()
                logger.info("Entering the details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("12")
                remote_pay_txn.enterCreditCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                logger.info("Click on proceed to pay")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_failure_pmt_btn()

            time.sleep(5)
            remote_pay_txn.wait_for_failed_message()
            failed_message = str(remote_pay_txn.failedScreenMessage())
            logger.info(f"Your failed Message is:  {failed_message}")

            if failed_message == expected_failed_message:
                pass
            else:
                logger.info(f"expected failed message is: {failed_message}")
                logger.info(f"actual failed message is: {expected_failed_message}")
                raise Exception(f"failed Messages are not matching")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time from db : {created_time}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")
            txn_rrn_number = result['rr_number'].values[0]
            logger.debug(f"Query result, txn_rrn_number from db : {txn_rrn_number}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of cnp_txn table is : {result}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_flow : {cnp_payment_flow}")
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
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "FAILED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT FAILED",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)

                login_page = LoginPage(app_driver)
                logger.info("logging into the application")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.info("Go to history page")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                logger.info("Select txn by order_id")
                txn_history_page.click_on_transaction_by_order_id(order_id)

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
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")

                actual_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "FAILED",
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "order_id": payment_order_id,
                    "msg": payment_status_msg,
                    "customer_name": payment_customer_name,
                    "settle_status": payment_settlement_status,
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
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "pmt_state": "FAILED",
                    "acquirer_code": "HDFC",
                    "settle_status": "FAILED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date,
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response received for transaction list api is for txn_id {txn_id} : {response}")
                status_api = response["status"]
                logger.debug(f"status_api is: {status_api} ")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api is: {amount_api} ")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code__api is: {acquirer_code_api} ")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api is: {settlement_status_api} ")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api is: {issuer_code_api} ")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api is: {txn_type_api} ")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api is: {org_code_api} ")
                date_api = response["postingDate"]
                logger.debug(f"date_api is: {date_api} ")
                tid_api = response["tid"]
                logger.debug(f"tid_api is : {tid_api} ")
                mid_api = response["mid"]
                logger.debug(f"mid_api is : {mid_api} ")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"device_serial_api is : {device_serial_api} ")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": "CNP",
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": acquirer_code_api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "tid": tid_api,
                    "mid": mid_api,
                    "device_serial": device_serial_api
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
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "FAILED",
                    "pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "ACTIVE",
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial
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

                query = f"select * from payment_intent where id='{payment_intent_id}';"
                logger.debug(f"Query to fetch payment_intent table : {query} ")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of payment_intent table is : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table is : {payment_intent_status}")

                query = f"select * from cnpware_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                logger.debug(f"Query result of cnpware_txn table is : {result}")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
                cnpware_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Query result, cnpware_payment_flow : {cnpware_payment_flow}")

                actual_db_values = {
                    "pmt_status": pmt_status_db,
                    "pmt_state": pmt_state_db,
                    "pmt_mode": pmt_mode_db,
                    "txn_amt": txn_amt_db,
                    "settle_status": settle_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "cnpware_pmt_flow": cnpware_payment_flow,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status,
                    "mid": mid_db,
                    "tid": tid_db,
                    "device_serial": device_serial_db
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
            date_and_time_portal = date_time_converter.to_portal_format(created_time)
            try:
                expected_portal_values = {
                    "pmt_state": "FAILED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "auth_code": "-" if txn_auth_code is None else txn_auth_code,
                    "rrn": "-" if txn_rrn_number is None else txn_rrn_number,
                    "txn_id": txn_id,
                    "date_time": date_and_time_portal
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username}")

                actual_portal_values = {
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "auth_code": auth_code,
                    "rrn": rr_number,
                    "txn_id": transaction_id,
                    "date_time": date_time
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -------------------------------------------End of Validation---------------------------------------------
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
@pytest.mark.portalVal
def test_common_100_103_277():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Success_Razorpay_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a successful debit card txn via CNP link
    TC naming code description:100: Payment Method,103: RemotePay,277: TC_277
    """
    expected_success_message = "Your payment is successfully completed! You may close the browser now."

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
        logger.debug(f"Query result of org_employee table is: {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='{org_code}' and payment_gateway = 'RAZORPAY' and payment_mode = 'CNP';"
        logger.debug(f"Query to fetch terminal_dependent_enabled from the DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from merchant_pg_config where org_code = '{str(org_code)}' and payment_gateway = 'RAZORPAY';"
        logger.debug(f"Query to fetch tid from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of merchant_pg_config table is : {result}")
        tid_settings = result['tid'].values[0]
        logger.info(f"tid from setting is: {tid_settings}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            logger.debug(f"amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")

            query = f"select * from terminal_info where tid='{str(tid_settings)}';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of terminal_info table is : {result}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial_db
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

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
            remote_pay_txn.wait_for_success_message()
            success_message = str(remote_pay_txn.succcessScreenMessage())
            logger.info(f"Your success message is:  {success_message}")
            logger.info(f"Your expected success message is:  {expected_success_message}")

            if success_message == expected_success_message:
                pass
            else:
                raise Exception("Success messages are not matching.")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, txn_rrn : {txn_rrn}")
            txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Query result, txn_issuer_code : {txn_issuer_code}")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Query result, txn_created_time : {txn_created_time}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of cnp_txn table is : {result}")
            txn_id = result['txn_id'].values[0]
            logger.debug(f"Query result from cnp_txn, Txn_id : {txn_id}")
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result from cnp_txn, org_code : {org_code}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of cnp_txn table is : {result}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]

            query = f"select * from cnpware_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnpware_payment_flow : {cnpware_payment_flow}")
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
                date_and_time = date_time_converter.to_app_format(txn_created_time)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "auth_code": txn_auth_code,
                    "date": date_and_time
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
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")

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
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(txn_created_time)

                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": cnp_txn_acquirer_code,
                    "settle_status": txn_settle_status,
                    "issuer_code": txn_issuer_code,
                    "org_code": org_code,
                    "date": date,
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial,
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
                logger.debug(f"status_api is: {status_api} ")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api is: {amount_api} ")
                acquirer_code__api = response["acquirerCode"]
                logger.debug(f"acquirer_code__api is: {acquirer_code__api} ")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api is: {settlement_status_api} ")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api is: {issuer_code_api} ")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api is: {txn_type_api} ")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api is: {org_code_api} ")
                date_api = response["postingDate"]
                logger.debug(f"date_api is: {date_api} ")
                tid_api = response["tid"]
                logger.debug(f"tid_api is : {tid_api} ")
                mid_api = response["mid"]
                logger.debug(f"mid_api is : {mid_api} ")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"device_serial_api is : {device_serial_api} ")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": "CNP",
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": acquirer_code__api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "org_code": org_code_api,
                    "date": date,
                    "tid": tid_api,
                    "mid": mid_api,
                    "device_serial": device_serial_api
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
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": cnpware_payment_flow,
                    "pmt_intent_status": "COMPLETED",
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table : {result}")
                pmt_status_db = result["status"].iloc[0]
                logger.debug(f"pmt_status_db is : {pmt_status_db}")
                pmt_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"pmt_mode_db is : {pmt_mode_db}")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settle_status_db is : {settle_status_db}")
                pmt_state_db = result["state"].iloc[0]
                logger.debug(f"pmt_state_db is : {pmt_state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db is : {payment_gateway_db}")

                query = f"select * from payment_intent where id='{payment_intent_id}';"
                logger.debug(f"Query to fetch data from payment_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of payment_intent table : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"payment_intent_status is : {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": pmt_status_db,
                    "pmt_state": pmt_state_db,
                    "pmt_mode": pmt_mode_db,
                    "txn_amt": amount,
                    "settle_status": settle_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status,
                    "tid": tid_db,
                    "mid": mid_db,
                    "device_serial": device_serial_db
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
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "auth_code": "-" if txn_auth_code is None else txn_auth_code,
                    "rrn": "-" if txn_rrn is None else txn_rrn,
                    "txn_id": txn_id,
                    "date_time": date_and_time_portal
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username}")

                actual_portal_values = {
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "auth_code": auth_code,
                    "rrn": rr_number,
                    "txn_id": transaction_id,
                    "date_time": date_time
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
            # -----------------------------------------Start of ChargeSlip Validation-----------------------------------
            if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
                logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
                try:
                    txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                    expected_charge_slip_values = {'CARD TYPE': 'MasterCard',
                                      'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                      'date': txn_date, "time": txn_time,
                                      "AUTH CODE": txn_auth_code
                                      }
                    receipt_validator.perform_charge_slip_validations(txn_id,
                                                                      {"username": app_username,
                                                                       "password": app_password},
                                                                      expected_charge_slip_values)
                except Exception as e:
                    Configuration.perform_charge_slip_val_exception(testcase_id, e)
                logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
            # -----------------------------------------End of ChargeSlip Validation-------------------------------------

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
@pytest.mark.portalVal
def test_common_100_103_278():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Failed_Razorpay_Tid_dep
    Sub Feature Description: Tid Dep - Verification debit card failed txn for Razorpay pg
    TC naming code description:100: Payment Method,103: RemotePay,278: TC_278
    """
    expected_failed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications."

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
        logger.debug(f"Query result of org_employee table is: {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='{org_code}' and payment_gateway = 'RAZORPAY' and payment_mode = 'CNP';"
        logger.debug(f"Query to fetch terminal_dependent_enabled from the DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from merchant_pg_config where org_code = '{str(org_code)}' and payment_gateway = 'RAZORPAY';"
        logger.debug(f"Query to fetch tid from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of merchant_pg_config table is : {result}")
        tid_settings = result['tid'].values[0]
        logger.info(f"tid from setting is: {tid_settings}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            logger.debug(f"amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")

            query = f"select * from terminal_info where tid='{str(tid_settings)}';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of terminal_info table is : {result}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial_db
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
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
            remote_pay_txn.click_failure_pmt_btn()

            actualFailedMessage = str(remote_pay_txn.failedScreenMessage())
            logger.info(f"After txn message is:  : {actualFailedMessage}")

            if expected_failed_message == actualFailedMessage:
                pass
            else:
                logger.error(f"Failed Message is not matching")

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            txn_rr_number = result['rr_number'].values[0]
            logger.debug(f"Query result, txn_rr_number : {txn_rr_number}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Query result, txn_created_time from db : {txn_created_time}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of cnp_txn table is : {result}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_flow}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")

            query = f"select * from payment_intent where id='{payment_intent_id}';"
            logger.debug(f"Query to fetch payment_intent from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of payment_intent table is : {result}")
            payment_intent_status = result["status"].iloc[0]
            logger.debug(f"payment_intent_status from payment_intent table is : {payment_intent_status}")

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

                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "FAILED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,
                    "order_id": order_id,
                    "msg": "PAYMENT FAILED",
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
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "customer_name": payment_customer_name,
                    "settle_status": payment_settlement_status,
                    "date": app_date_and_time,
                    "order_id": payment_order_id,
                    "msg": payment_status_msg,
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

                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "pmt_state": "FAILED",
                    "acquirer_code": "HDFC",
                    "settle_status": "FAILED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date,
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial,
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
                acquirer_code__api = response["acquirerCode"]
                logger.debug(f"acquirer_code__api is: {acquirer_code__api} ")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api is: {settlement_status_api} ")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api is: {issuer_code_api} ")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api is: {txn_type_api} ")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api is: {org_code_api} ")
                date_api = response["postingDate"]
                logger.debug(f"date_api is: {date_api} ")
                tid_api = response["tid"]
                logger.debug(f"tid_api is : {tid_api} ")
                mid_api = response["mid"]
                logger.debug(f"mid_api is : {mid_api} ")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"device_serial_api is : {device_serial_api} ")
                status_api = response["status"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                amount_api = response["amount"]
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": acquirer_code__api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "tid": tid_api,
                    "mid": mid_api,
                    "device_serial": device_serial_api
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
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "FAILED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "ACTIVE",
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Txn query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db is : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db is : {payment_mode_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db is : {state_db}")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settle_status_db is : {settle_status_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db is : {payment_gateway_db}")

                query = f"select * from cnpware_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                logger.debug(f"cnpware_txn query result : {result}")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount,
                    "settle_status": settle_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status,
                    "tid": tid_db,
                    "mid": mid_db,
                    "device_serial": device_serial_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")

            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "pmt_state": "FAILED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "auth_code": "-" if txn_auth_code is None else txn_auth_code,
                    "rrn": "-" if txn_rr_number is None else txn_rr_number,
                    "txn_id": txn_id,
                    "date_time": date_and_time_portal
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username}")

                actual_portal_values = {
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "auth_code": auth_code,
                    "rrn": rr_number,
                    "txn_id": transaction_id,
                    "date_time": date_time
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------End of DB Validation---------------------------------------
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
@pytest.mark.portalVal
def test_common_100_103_279():
    """
    Sub Feature Code: UI_Common_PM_CNP_Refund_Card_txn_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a refund for card txn using remote pay.
    TC naming code description:100: Payment Method,103: RemotePay,279: TC_279
    """
    expectedMessage = "Your payment is successfully completed! You may close the browser now."
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
        logger.debug(f"Query result is : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='{org_code}' and payment_gateway = 'RAZORPAY' and payment_mode = 'CNP';"
        logger.debug(f"Query to set terminal_dependent_enabled to the DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from merchant_pg_config where org_code = '{str(org_code)}' and payment_gateway = 'RAZORPAY';"
        logger.debug(f"Query to fetch tid from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of merchant_pg_config is : {result}")
        tid_settings = result['tid'].values[0]
        logger.debug(f"tid from setting is: {tid_settings}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1501, 1601)
            logger.debug(f"amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")

            query = f"select * from terminal_info where tid='{str(tid_settings)}';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result is : {result}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial_db
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            if not response['success']:
                raise Exception("Api could not initate a cnp txn.")
            else:
                paymentLinkUrl = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(paymentLinkUrl)
                remotePayTxn = RemotePayTxnPage(page)
                remotePayTxn.clickOnCreditCardToExpand()
                logger.info("Enter Debit card details")
                remotePayTxn.enterNameOnTheCard("Sandeep")
                remotePayTxn.enterCreditCardNumber("4111 1111 1111 1111")
                remotePayTxn.enterCreditCardExpiryMonth("12")
                remotePayTxn.enterCreditCardExpiryYear("2050")
                remotePayTxn.enterCreditCardCvv("111")
                remotePayTxn.clickOnProceedToPay()
                remotePayTxn.click_success_pmt_btn()
                remotePayTxn.wait_for_success_message()

                successMessage = str(remotePayTxn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {successMessage}")
                logger.info(f"Your expected Message is:  {expectedMessage}")
            if successMessage == expectedMessage:
                pass
            else:
                raise Exception("Success Message is not matching.")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result is : {result}")
            original_txn_id = result['id'].values[0]
            logger.debug(f"txn id from txn table : {original_txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            original_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched original_txn_type from txn table is : {original_txn_type}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")

            query = f"select * from cnp_txn where txn_id='{original_txn_id}';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result is : {result}")
            state_cnp_txn_original = result['state'].values[0]
            logger.debug(f"Query result, state_cnp_txn_original : {state_cnp_txn_original}")
            original_acquirer_code_cnpware = result['acquirer_code'].values[0]
            logger.debug(f"original_acquirer_code_cnpware from cnpware_txn table : {original_acquirer_code_cnpware}")
            original_payment_flow_cnpware = result['payment_flow'].values[0]
            logger.debug(f"original_payment_flow from cnpware_txn table : {original_payment_flow_cnpware}")

            api_details = DBProcessor.get_api_details('RemotePayRefund', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "originalTransactionId": str(original_txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            txn_id_after_refund = response.get('txnId')
            logger.debug(f"Query result, txn_id_after_refund : {txn_id_after_refund}")

            query = f"select * from txn where orig_txn_id = '{(original_txn_id)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn details from the DB after refund: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result is : {result}")
            txn_id_after_refund = result['id'].values[0]
            logger.debug(f"txn id from txn table after refund : {txn_id_after_refund}")
            amount_after_refund = result['amount'].values[0]
            logger.debug(f"amount from txn table after refund: {amount_after_refund}")
            state_after_refund = result['state'].values[0]
            logger.debug(f"state from txn table after refund: {state_after_refund}")
            status_after_refund = result['status'].values[0]
            logger.debug(f"status from txn table after refund: {status_after_refund}")
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway from txn table after refund: {payment_gateway_after_refund}")
            settlement_status_after_refund = result['settlement_status'].values[0]
            logger.debug(f"settlement_status from txn table after refund: {settlement_status_after_refund}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name_2}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            order_id_after_refund = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id_after_refund}")


            query = f"select * from cnpware_txn where txn_id='{txn_id_after_refund}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Query result is : {result}")
            amount_after_refund = result['amount'].values[0]
            logger.debug(f"amount from cnpware_txn table : {amount_after_refund}")
            state_after_refund = result['state'].values[0]
            logger.debug(f"state from cnpware_txn table : {state_after_refund}")
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway from cnpware_txn table : {payment_gateway_after_refund}")
            payment_flow_after_refund = result['payment_flow'].values[0]
            logger.debug(f"payment_flow from cnpware_txn table : {payment_flow_after_refund}")
            txn_type_after_refund = result['txn_type'].values[0]
            logger.debug(f"txn_type_after_refund from cnpware_txn table : {txn_type_after_refund}")

            query = f"select * from cnp_txn where txn_id='{txn_id_after_refund}';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result is : {result}")
            state_cnp_txn = result['state'].values[0]
            logger.debug(f"Query result, state_cnp_txn : {state_cnp_txn}")
            payment_mode_cnp_txn = result['payment_mode'].values[0]
            logger.debug(f"Query result, payment_mode_cnp_txn : {payment_mode_cnp_txn}")

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
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_mode": "PAY LINK",
                    "txn_id": original_txn_id,
                    "txn_amt": f"{amount:,}.00",
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,

                    "pmt_status_2": "STATUS:REFUND_POSTED",
                    "pmt_mode_2": "PAY LINK",
                    "txn_id_2": txn_id_after_refund,
                    "txn_amt_2": f"{amount:,}.00",
                    "order_id_2": order_id,
                    "msg_2": "REFUND PENDING",
                    "customer_name_2": txn_customer_name,
                    "settle_status_2": "REVPENDING",
                    "date_2": date_and_time
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_after_refund)

                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {txn_id_after_refund}, {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from app transaction history: order Id = {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {original_txn_id}, {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from app transaction history: order Id = {app_order_id}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_mode": app_payment_mode_original,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "msg": payment_msg_original,
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,

                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "order_id_2": app_order_id_refunded,
                    "msg_2": payment_msg_refunded,
                    "customer_name_2": txn_customer_name,
                    "settle_status_2": app_settlement_status_refunded,
                    "date_2": app_date_and_time_refunded
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------
        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode": "CNP",
                    "pmt_mode_2": "CNP",
                    "settle_status": "SETTLED",
                    "settle_status_2": "REVPENDING",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name_2,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name_2,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": refund_txn_type,
                    "org_code_2": org_code_txn,
                    "auth_code": auth_code,
                    "date": date,
                    "date_2": refund_date,
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status from api response for original txn is: {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"amount from api response for original txn is: {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"payment_mode from api response for original txn is: {payment_mode_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state from api response for original txn is: {state_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"settlement_status from api response for original txn is: {settlement_status_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code from api response for original txn is: {issuer_code_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"acquirer_code from api response for original txn is: {acquirer_code_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code from api response for original txn is: {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid from api response for original txn is: {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid from api response for original txn is: {tid_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"txn_type from api response for original txn is: {txn_type_api_original}")
                auth_code_api_original = response["authCode"]
                logger.debug(f"auth_code from api response for original txn is: {auth_code_api_original}")
                date_api_original = response["createdTime"]
                logger.debug(f"date from api response for original txn is: {date_api_original}")
                order_id_api_original = response["orderNumber"]
                logger.debug(f"order_id from api response for original txn is: {order_id_api_original}")
                device_serial_api_original = response["deviceSerial"]
                logger.debug(f"device_serial from api response for original txn is: {device_serial_api_original}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_after_refund][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status from api response for refund txn is: {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount from api response for refund txn is: {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode from api response for refund txn is: {payment_mode_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state from api response for refund txn is: {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status from api response for refund txn is: {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code from api response for refund txn is: {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code from api response for refund txn is: {org_code_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type from api response for refund txn is: {txn_type_api_refunded}")
                date_api_refunded = response["createdTime"]
                logger.debug(f"date from api response for refund txn is: {date_api_refunded}")
                order_id_api_refunded = response["orderNumber"]
                logger.debug(f"order_id from api response for refund txn is: {order_id_api_refunded}")

                actual_api_values = {
                    "pmt_status": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt": str(amount_api_original),
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "auth_code": auth_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "tid": tid_api_original,
                    "mid": mid_api_original,
                    "device_serial": device_serial_api_original
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
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                expected_db_values = {
                    "pmt_status": "REFUND_POSTED",
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_state": "REFUND_INITIATED",
                    "pmt_mode": "CNP",
                    "pmt_mode_2": "CNP",
                    "txn_amt": amount,
                    "txn_amt_2": amount,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "cnp_txn_status": "SETTLED",
                    "cnp_txn_status_2": "REFUND_INITIATED",
                    "settle_status": "REVPENDING",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY",
                    "cnpware_txn_type_2": "REFUND",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_flow_2": "None",
                    "tid": tid_db,
                    "mid": mid_db,
                    "device_serial": device_serial_db
                }
                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from txn where id = '{str(txn_id_after_refund)}';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result is : {result}")
                original_txn_id_db = result['id'].values[0]
                logger.debug(f"txn id from txn table : {original_txn_id_db}")
                amount_txn_db = result['amount'].values[0]
                logger.debug(f"amount from txn table : {amount_txn_db}")
                paymentMode_db = result['payment_mode'].values[0]
                logger.debug(f"paymentMode from txn table : {paymentMode_db}")
                state_db = result['state'].values[0]
                logger.debug(f"state from txn table : {state_db}")
                status_db = result['status'].values[0]
                logger.debug(f"status from txn table : {status_db}")
                acquirer_code_db = result['acquirer_code'].values[0]
                logger.debug(f"acquirer_code from txn table : {acquirer_code_db}")
                payment_gateway_db = result['payment_gateway'].values[0]
                logger.debug(f"payment_gateway from txn table : {payment_gateway_db}")
                settlement_status_db = result['settlement_status'].values[0]
                logger.debug(f"settlement_status from txn table : {settlement_status_db}")
                txn_type_db = result['txn_type'].values[0]
                logger.debug(f"txn type from txn table : {txn_type_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_status_2": status_after_refund,
                    "pmt_state": state_db,
                    "pmt_state_2": state_after_refund,
                    "pmt_mode": paymentMode_db,
                    "pmt_mode_2": payment_mode_cnp_txn,
                    "txn_amt": amount_txn_db,
                    "txn_amt_2": amount_after_refund,
                    "order_id": order_id,
                    "order_id_2": order_id_after_refund,
                    "cnp_txn_status": state_cnp_txn_original,
                    "cnp_txn_status_2": state_cnp_txn,
                    "settle_status": settlement_status_db,
                    "settle_status_2": settlement_status_after_refund,
                    "acquirer_code": acquirer_code_db,
                    "acquirer_code_2": original_acquirer_code_cnpware,
                    "pmt_gateway": payment_gateway_db,
                    "pmt_gateway_2": payment_gateway_after_refund,
                    "cnpware_txn_type": original_txn_type,
                    "cnpware_txn_type_2": txn_type_after_refund,
                    "cnpware_pmt_flow": original_payment_flow_cnpware,
                    "cnpware_pmt_flow_2": str(payment_flow_after_refund),
                    "tid": tid_db,
                    "mid": mid_db,
                    "device_serial": device_serial_db
                }
                logger.debug(f"actualDBValues : {actual_db_values}")

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
                    "pmt_type": "CNP",
                    "txn_amt": f"{amount:,}.00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "auth_code": auth_code,

                    "date_time_2": date_and_time_portal,
                    "pmt_state_2": "REFUND_POSTED",
                    "pmt_type_2": "CNP",
                    "txn_amt_2": f"{amount:,}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_after_refund
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[1]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[1]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                auth_code_portal = transaction_details[1]['Auth Code']
                logger.debug(f"auth_code from portal is: {auth_code}")
                transaction_type = transaction_details[1]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[1]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[1]['Username']
                logger.debug(f"username from portal is: {username}")

                date_time_2 = transaction_details[0]['Date & Time']
                logger.debug(f"date_time_2 from portal is: {date_time_2}")
                transaction_id_2 = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id_2 from portal is: {transaction_id_2}")
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount_2 from portal is: {total_amount_2}")
                transaction_type_2 = transaction_details[0]['Type']
                logger.debug(f"transaction_type_2 from portal is: {transaction_type_2}")
                status_2 = transaction_details[0]['Status']
                logger.debug(f"status_2 from portal is: {status_2}")
                username_2 = transaction_details[0]['Username']
                logger.debug(f"username_2 from portal is: {username_2}")

                actual_portal_values = {
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "auth_code": auth_code_portal,
                    "txn_id": transaction_id,
                    "date_time": date_time,

                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "date_time_2": date_time_2
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
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