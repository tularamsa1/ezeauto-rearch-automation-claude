import random
import sys
import pytest

from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from PageFactory.portal_remotePayPage import RemotePayTxnPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_103_151():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Success_Cyber_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a successful debit card txn via CNP link
    TC naming code description:100: Payment Method,103: RemotePay,151: TC_151
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table is: {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code +"' and payment_gateway = 'CYBERSOURCE' and payment_mode = 'CNP';"
        logger.debug(f"Query to fetch terminal_dependent_enabled from the DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            msg =""
            amount = random.randint(300, 399)
            logger.debug(f"amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")

            query = "select * from merchant_pg_config where org_code = '" + str(org_code) + "' and payment_gateway = 'CYBERSOURCE';"
            logger.debug(f"Query to fetch tid from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of merchant_pg_config table is : {result}")
            tid_settings = result['tid'].values[0]
            logger.info(f"tid from setting is: {tid_settings}")

            # get the deviceSerial from terminal_info
            query = "select * from terminal_info where tid='" + str(tid_settings) + "';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of terminal_info table is : {result}")
            terminal_info_id = result['id'].values[0]
            logger.debug(f"Query result, terminal_info_id from db : {terminal_info_id}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',request_body={
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
            remote_pay_txn.enterNameOnTheCard("EzeAuto")
            remote_pay_txn.enterCreditCardNumber("4000 0000 0000 1091")
            remote_pay_txn.enterDebitCardExpiryMonth("12")
            remote_pay_txn.enterDebitCardExpiryYear("2050")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnProceedToPay()
            remote_pay_txn.switch_to_iframe()
            remote_pay_txn.wait_for_success_message()
            success_message = str(remote_pay_txn.succcessScreenMessage())
            logger.info(f"Your success message is:  {success_message}")
            logger.info(f"Your expected success message is:  {expected_success_message}")

            if success_message == expected_success_message:
                pass
            else:
                raise Exception("Success messages are not matching.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table is : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, txn_payer_name : {txn_payer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, txn_rrn : {txn_rrn}")
            txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Query result, txn_issuer_code : {txn_issuer_code}")
            txn_bank_name = result['bank_name'].values[0]
            logger.debug(f"Query result, txn_bank_name : {txn_bank_name}")
            txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, txn_acquirer_code : {txn_acquirer_code}")
            txn_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settlement_status : {txn_settlement_status}")
            txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, txn_payment_mode : {txn_payment_mode}")
            txn_amount = result['amount'].values[0]
            logger.debug(f"Query result, txn_amount : {txn_amount}")
            txn_created_time = result['created_time'].values[0]
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of cnp_txn table is : {result}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")
            txn_id = result['txn_id'].values[0]
            logger.debug(f"Query result from cnp_txn, Txn_id : {txn_id}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_gateway : {payment_gateway}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_mode : {payment_mode}")
            payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_flow : {payment_flow}")
            payment_option = result['payment_option'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_option : {payment_option}")
            payment_option_value1 = result['payment_option_value1'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_option_value1 : {payment_option_value1}")
            payment_status = result['payment_status'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_status : {payment_status}")
            state = result['state'].values[0]
            logger.debug(f"Query result from cnp_txn, state : {state}")
            payment_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_card_brand : {payment_card_brand}")
            payment_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_card_type : {payment_card_type}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result from cnp_txn, acquirer_code : {acquirer_code}")
            issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Query result from cnp_txn, issuer_code : {issuer_code}")
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result from cnp_txn, org_code : {org_code}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of cnp_txn table is : {result}")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, cnp_txn_card_type : {cnp_txn_card_type}")
            cnp_txn_external_ref = result['external_ref'].values[0]
            logger.debug(f"Query result, cnp_txn_external_ref : {cnp_txn_external_ref}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]

            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            cnpware_txn_rrn_number = result['rr_number'].values[0]
            logger.debug(f"Query result, cnpware_txn_rrn_number : {cnpware_txn_rrn_number}")
            cnpware_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnpware_txn_acquirer_code : {cnpware_txn_acquirer_code}")
            cnpware_txn_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_card_type : {cnpware_txn_card_type}")
            cnpware_txn_external_ref = result['external_ref'].values[0]
            logger.debug(f"Query result, cnpware_txn_external_ref : {cnpware_txn_external_ref}")
            cnpware_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnpware_txn_auth_code : {cnpware_txn_auth_code}")
            cnpware_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnpware_txn_state : {cnpware_txn_state}")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]

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
                expectedAppValues = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "rrn": cnp_txn_rrn,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "auth_code": txn_auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
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
                payment_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {payment_rrn}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")

                actualAppValues = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": payment_rrn,
                    "order_id": payment_order_id,
                    "msg": payment_status_msg,
                    "customer_name": payment_customer_name,
                    "settle_status": payment_settlement_status,
                    "auth_code": payment_auth_code,
                    "date": app_date_and_time
                }

                logger.debug(f"actualAppValues: {actualAppValues}")

                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(txn_created_time)

                expectedAPIValues = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": cnp_txn_acquirer_code,
                    "settle_status": txn_settle_status,
                    "rrn": cnp_txn_rrn,
                    "issuer_code": txn_issuer_code,
                    "org_code": org_code,
                    "date": date,
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial,
                }

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                response = APIProcessor.send_request(api_details)
                response_in_list = response["txns"]
                status_api = ''
                amount_api = ''

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        logger.debug(f"status_api is: {status_api} ")
                        amount_api = int(elements["amount"])
                        logger.debug(f"amount_api is: {amount_api} ")
                        acquirer_code__api = elements["acquirerCode"]
                        logger.debug(f"acquirer_code__api is: {acquirer_code__api} ")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"settlement_status_api is: {settlement_status_api} ")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"issuer_code_api is: {issuer_code_api} ")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"txn_type_api is: {txn_type_api} ")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"org_code_api is: {org_code_api} ")
                        date_api = elements["postingDate"]
                        logger.debug(f"date_api is: {date_api} ")
                        tid_api = elements["tid"]
                        logger.debug(f"tid_api is : {tid_api} ")
                        mid_api = elements["mid"]
                        logger.debug(f"mid_api is : {mid_api} ")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"device_serial_api is : {device_serial_api} ")
                        rr_number_api = elements["rrNumber"]

                actualAPIValues = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": "CNP",
                    "pmt_state": cnp_txn_state,
                    "acquirer_code": acquirer_code__api,
                    "settle_status": settlement_status_api,
                    "rrn": rr_number_api,
                    "issuer_code": issuer_code_api,
                    "org_code": org_code_api,
                    "date": date,
                    "tid": tid_api,
                    "mid": mid_api,
                    "device_serial": device_serial_api
                }

                logger.debug(f"actualAPIValues: {actualAPIValues}")


                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expectedDBValues = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "pmt_gateway": "CYBERSOURCE",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "CYBERSOURCE",
                    "cnpware_pmt_gateway": "CYBERSOURCE",
                    "pmt_flow": cnpware_payment_flow,
                    "pmt_intent_status": "COMPLETED",
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial,
                }

                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + txn_id + "';"
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

                query = "select * from payment_intent where id='" + payment_intent_id + "';"
                logger.debug(f"Query to fetch data from payment_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of payment_intent table : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"payment_intent_status is : {payment_intent_status}")

                actualDBValues = {
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

                logger.debug(f"actualDBValues : {actualDBValues}")

                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                expectedValues = {'CARD TYPE': 'VISA',
                                  'merchant_ref_no': 'Ref # ' + str(order_id),
                                  'RRN': str(cnp_txn_rrn),
                                  'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                  'date': txn_date, "time": txn_time,
                                  "AUTH CODE": txn_auth_code
                                  }

                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expectedValues)

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
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
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
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
def test_common_100_103_152():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Failed_Cyber_Tid_dep
    Sub Feature Description: Tid Dep - Verification debit card failed txn for cybersource pg
    TC naming code description:100: Payment Method,103: RemotePay,152: TC_152
    """
    expectedfailed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications."

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
        logger.debug(f"Query result of org_employee table is: {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'CYBERSOURCE' and payment_mode = 'CNP';"
        logger.debug(f"Query to fetch terminal_dependent_enabled from the DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            msg =""
            amount = random.randint(300, 399)
            logger.debug(f"amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")

            query = "select * from merchant_pg_config where org_code = '" + str(org_code) + "' and payment_gateway = 'CYBERSOURCE';"
            logger.debug(f"Query to fetch tid from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of merchant_pg_config table is : {result}")
            tid_settings = result['tid'].values[0]
            logger.info(f"tid from setting is: {tid_settings}")

            # get the deviceSerial from terminal_info
            query = "select * from terminal_info where tid='" + str(tid_settings) + "';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of terminal_info table is : {result}")
            logger.info(f"id from setting is: {tid_settings}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',request_body={
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
            remote_pay_txn.enterCreditCardNumber("4111 1111 1111 1111")
            remote_pay_txn.enterDebitCardExpiryMonth("12")
            remote_pay_txn.enterDebitCardExpiryYear("2050")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnProceedToPay()

            actualFailedMessage = str(remote_pay_txn.failedScreenMessage())
            logger.info(f"After txn message is:  : {actualFailedMessage}")

            if expectedfailed_message == actualFailedMessage:
                pass
            else:
                logger.error(f"Failed Message is not matching")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
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

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
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
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")

            query = "select * from payment_intent where id='" + payment_intent_id + "';"
            logger.debug(f"Query to fetch payment_intent from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of payment_intent table is : {result}")
            payment_intent_status = result["status"].iloc[0]

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

                expectedAppValues = {
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

                logger.debug(f"expectedAppValues: {expectedAppValues}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
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
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")

                actualAppValues = {
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

                logger.debug(f"actualAppValues: {actualAppValues}")

                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)

                expectedAPIValues = {
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

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id
                })

                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                amount_api = response["amount"]
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                response = APIProcessor.send_request(api_details)
                response_in_list = response["txns"]

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        acquirer_code__api = elements["acquirerCode"]
                        logger.debug(f"acquirer_code__api is: {acquirer_code__api} ")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"settlement_status_api is: {settlement_status_api} ")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"issuer_code_api is: {issuer_code_api} ")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"txn_type_api is: {txn_type_api} ")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"org_code_api is: {org_code_api} ")
                        date_api = elements["postingDate"]
                        logger.debug(f"date_api is: {date_api} ")
                        tid_api = elements["tid"]
                        logger.debug(f"tid_api is : {tid_api} ")
                        mid_api = elements["mid"]
                        logger.debug(f"mid_api is : {mid_api} ")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"device_serial_api is : {device_serial_api} ")

                actualAPIValues = {
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

                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:

                expectedDBValues = {
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "CNP",
                    "txn_amt": amount,
                    "settle_status": "FAILED",
                    "pmt_gateway": "CYBERSOURCE",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "CYBERSOURCE",
                    "cnpware_pmt_gateway": "CYBERSOURCE",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "ACTIVE",
                    "tid": txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial
                }

                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + txn_id + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Txn query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db is : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db is : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"amount_db is : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db is : {state_db}")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settle_status_db is : {settle_status_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db is : {payment_gateway_db}")

                query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                logger.debug(f"cnpware_txn query result : {result}")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")

                actualDBValues = {
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

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
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
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
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
def test_common_100_103_153():
    """
    Sub Feature Code: UI_Common_PM_CNP_Refund_Card_txn_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a refund for card txn using remote pay.
    TC naming code description:100: Payment Method,103: RemotePay,153: TC_153
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result is : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'CYBERSOURCE' and payment_mode = 'CNP';"
        logger.debug(f"Query to set terminal_dependent_enabled to the DB : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
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

            query = "select * from merchant_pg_config where org_code = '" + str(org_code) + "' and payment_gateway = 'CYBERSOURCE';"
            logger.debug(f"Query to fetch tid from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of merchant_pg_config is : {result}")
            tid_settings = result['tid'].values[0]
            logger.debug(f"tid from setting is: {tid_settings}")

            # get the deviceSerial from terminal_info
            query = "select * from terminal_info where tid='" + str(tid_settings) + "';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.info(f"id from setting is: {tid_settings}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial_db
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            if response['success'] == False:
                raise Exception ("Api could not initate a cnp txn.")
            else:
                paymentLinkUrl = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(paymentLinkUrl)
                remotePayTxn = RemotePayTxnPage(page)
                remotePayTxn.clickOnCreditCardToExpand()
                logger.info("Enter Debit card details")
                remotePayTxn.enterNameOnTheCard("EzeAuto")
                remotePayTxn.enterCreditCardNumber("4000 0000 0000 1091")
                remotePayTxn.enterCreditCardExpiryMonth("12")
                remotePayTxn.enterCreditCardExpiryYear("2050")
                remotePayTxn.enterCreditCardCvv("111")
                remotePayTxn.clickOnProceedToPay()
                remotePayTxn.switch_to_iframe()
                remotePayTxn.wait_for_success_message()
                successMessage = str(remotePayTxn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {successMessage}")
                logger.info(f"Your expiryMessage is:  {expectedMessage}")
            if successMessage == expectedMessage:
                pass
            else:
                raise Exception("Success Message is not matching.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"txn id from txn table : {original_txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            original_txn_type = result['txn_type'].values[0]
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")

            query = "select * from cnpware_txn where txn_id='" + original_txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            original_acquirer_code_cnpware = result['acquirer_code'].values[0]
            logger.debug(f"original_acquirer_code_cnpware from cnpware_txn table : {original_acquirer_code_cnpware}")
            original_payment_flow_cnpware = result['payment_flow'].values[0]
            logger.debug(f"original_payment_flow from cnpware_txn table : {original_payment_flow_cnpware}")

            query = "select * from cnp_txn where txn_id='"+original_txn_id+"';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_rrn_cnp_txn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_rrn_cnp_txn : {original_rrn_cnp_txn}")
            state_cnp_txn_original = result['state'].values[0]
            logger.debug(f"Query result, state_cnp_txn_original : {state_cnp_txn_original}")

            #Refund
            api_details = DBProcessor.get_api_details('RemotePayRefund', request_body={
                "username": app_username,
                "password":app_password,
                "amount": amount,
                "originalTransactionId": str(original_txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            txn_id_after_refund = response.get('txnId')
            logger.debug(f"Query result, txn_id_after_refund : {txn_id_after_refund}")

            query = "select * from txn where orig_txn_id = '" + str(original_txn_id) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn details from the DB after refund: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_after_refund = result['id'].values[0]
            logger.debug(f"txn id from txn table after refund : {txn_id_after_refund}")
            amount_after_refund = result['amount'].values[0]
            logger.debug(f"amount from txn table after refund: {amount_after_refund}")
            paymentMode_after_refund = result['payment_mode'].values[0]
            logger.debug(f"paymentMode from txn table after refund: {paymentMode_after_refund}")
            state_after_refund = result['state'].values[0]
            logger.debug(f"state from txn table after refund: {state_after_refund}")
            status_after_refund = result['status'].values[0]
            logger.debug(f"status from txn table after refund: {status_after_refund}")
            acquirer_code_after_refund = result['acquirer_code'].values[0]
            logger.debug(f"acquirer_code from txn table after refund: {acquirer_code_after_refund}")
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway from txn table after refund: {payment_gateway_after_refund}")
            settlement_status_after_refund = result['settlement_status'].values[0]
            logger.debug(f"settlement_status from txn table after refund: {settlement_status_after_refund}")
            created_datetime_after_refund = result['created_time'].values[0]
            logger.debug(f"posting_date from txn table after refund: {created_datetime_after_refund}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name_2}")
            refund_rrn = result['rr_number'].iloc[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            order_id_after_refund = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id_after_refund}")
            bank_code_after_refund = result['bank_code'].values[0]
            logger.debug(f"bank_code_after_refund is : {bank_code_after_refund}")

            query = "select * from cnpware_txn where txn_id='" + txn_id_after_refund + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query,"cnpware")
            txn_id_after_refund_cnpware = result['txn_id'].values[0]
            logger.debug(f"txn id from cnpware_txn table : {txn_id_after_refund_cnpware}")
            amount_after_refund = result['amount'].values[0]
            logger.debug(f"amount from cnpware_txn table : {amount_after_refund}")
            paymentMode_after_refund = result['payment_mode'].values[0]
            logger.debug(f"paymentMode from cnpware_txn table : {paymentMode_after_refund}")
            state_after_refund = result['state'].values[0]
            logger.debug(f"state from cnpware_txn table : {state_after_refund}")
            acquirer_code_after_refund = result['acquirer_code'].values[0]
            logger.debug(f"acquirer_code from cnpware_txn table : {acquirer_code_after_refund}")
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway from cnpware_txn table : {payment_gateway_after_refund}")
            payment_flow_after_refund = result['payment_flow'].values[0]
            logger.debug(f"payment_flow from cnpware_txn table : {payment_flow_after_refund}")
            txn_type_after_refund = result['txn_type'].values[0]

            query = "select * from cnp_txn where txn_id='" + txn_id_after_refund + "';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn_cnp_txn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn_cnp_txn : {rrn_cnp_txn}")
            acquirer_code_cnp_txn = result['acquirer_code'].values[0]
            logger.debug(f"Query result, acquirer_code_cnp_txn : {acquirer_code_cnp_txn}")
            state_cnp_txn = result['state'].values[0]
            logger.debug(f"Query result, state_cnp_txn : {state_cnp_txn}")
            payment_flow_cnp_txn = result['payment_flow'].values[0]
            logger.debug(f"Query result, payment_flow_cnp_txn : {payment_flow_cnp_txn}")
            txn_type_cnp_txn = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type_cnp_txn : {txn_type_cnp_txn}")
            payment_mode_cnp_txn = result['payment_mode'].values[0]
            payment_gateway_cnp_txn = result['payment_gateway'].values[0]
            logger.debug(f"Query result, payment_gateway_cnp_txn : {payment_gateway_cnp_txn}")
            org_code_cnp_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code_cnp_txn : {org_code_cnp_txn}")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")

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
                expectedAppValues = {
                    "pmt_status": "STATUS:AUTHORIZED REFUNDED",
                    "pmt_mode": "PAY LINK",
                    "txn_id": original_txn_id,
                    "txn_amt": str(amount) + ".00",
                    "rrn": str(original_rrn_cnp_txn),
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,

                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode_2": "PAY LINK",
                    "txn_id_2": txn_id_after_refund,
                    "txn_amt_2": str(amount) + ".00",
                    "rrn_2": str(rrn_cnp_txn),
                    "order_id_2": order_id,
                    "msg_2": "PAYMENT SUCCESSFUL",
                    "customer_name_2": txn_customer_name,
                    "settle_status_2": txn_settle_status,
                    "date_2": date_and_time
                }

                logger.debug(f"expectedAppValues: {expectedAppValues}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_after_refund)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_after_refund}, {app_rrn_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_after_refund}, {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: settlement status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from app transaction history: order Id = {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {original_txn_id}, {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(f"Fetching order id from app transaction history: order Id = {app_order_id}")

                actualAppValues = {
                    "pmt_status": app_payment_status_original,
                    "pmt_mode": app_payment_mode_original,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_id": original_txn_id,
                    "rrn": str(original_rrn_cnp_txn),
                    "order_id": order_id,
                    "msg": payment_msg_original,
                    "customer_name": txn_customer_name,
                    "settle_status": txn_settle_status,
                    "date": date_and_time,

                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "rrn_2": str(app_rrn_refunded),
                    "order_id_2": app_order_id_refunded,
                    "msg_2": payment_msg_refunded,
                    "customer_name_2": txn_customer_name,
                    "settle_status_2": app_settlement_status_refunded,
                    "date_2": app_date_and_time_refunded
                }

                logger.debug(f"actualAppValues: {actualAppValues}")

                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expectedAPIValues = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "CNP",
                    "pmt_mode_2": "CNP",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name_2,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name_2,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "rrn": str(original_rrn_cnp_txn),
                    "rrn_2": str(rrn_cnp_txn),
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

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]
                state_api_original = response["states"][0]
                settlement_status_api_original = response["settlementStatus"]
                issuer_code_api_original = response["issuerCode"]
                acquirer_code_api_original = response["acquirerCode"]
                org_code_api_original = response["orgCode"]
                mid_api_original = response["mid"]
                tid_api_original = response["tid"]
                txn_type_api_original = response["txnType"]
                auth_code_api_original = response["authCode"]
                date_api_original = response["createdTime"]
                order_id_api_original = response["orderNumber"]
                device_serial_api_original = response["deviceSerial"]

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_after_refund][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                rrn_api_refunded = response["rrNumber"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["createdTime"]
                order_id_api_refunded = response["orderNumber"]

                actualAPIValues = {
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
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
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

                logger.debug(f"actualAPIValues: {actualAPIValues}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
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
                    "pmt_status": "REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "CNP",
                    "pmt_mode_2": "CNP",
                    "txn_amt": amount,
                    "txn_amt_2": amount,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "cnp_txn_status": "SETTLED",
                    "cnp_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "pmt_gateway": "CYBERSOURCE",
                    "pmt_gateway_2": "CYBERSOURCE",
                    "cnpware_txn_type": "REMOTE_PAY",
                    "cnpware_txn_type_2": "REFUND",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_flow_2": "None",
                    "tid": tid_db,
                    "mid": mid_db,
                    "device_serial": device_serial_db
                }
                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = "select * from txn where id = '" + str(txn_id_after_refund) + "';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
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
                Org_Code_db = result['org_code'].values[0]
                logger.debug(f"Org code from txn table : {Org_Code_db}")

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
                date_and_time_portal_refund = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "auth_code": auth_code,

                    "date_time_2": date_and_time_portal_refund,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "CNP",
                    "txn_amt_2": str(amount) + ".00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_after_refund,

                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

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

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of Chargeslip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                logger.info(f"date and time is: {txn_date},{txn_time}")
                expectedValues = {
                    'CARD TYPE': 'VISA',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(original_rrn_cnp_txn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    "AUTH CODE": txn_auth_code
                }
                receipt_validator.perform_charge_slip_validations(original_txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expectedValues)
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

