import sys
import pytest
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_447():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Org_Settings_Txn_Amt_Same_As_Min_Amt_Allowed_For_Txn
    Sub Feature Description: To verify the Remote Pay transaction when amount is exactly as Minimum amount
    set in Org Setting - "Minimum amount allowed for a transaction".
    TC naming code description: 100: Payment Method, 103: RemotePay, 447: TC_447
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table: {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-----------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["remotePaymentEnabled"] = "true"
        api_details["RequestBody"]["settings"]["minTxnAmount"] = "1"
        api_details["RequestBody"]["settings"]["maxTxnAmount"] = "2"
        logger.debug(f"API details : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for Remote pay, min and max amount:  {response}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for net banking: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the net banking details : {result}")
        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for credit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for credit card : {result}")
        logger.debug(f"result length of credit card: {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the credit card details : {result}")
        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for debit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for debit card : {result}")
        logger.debug(f"result length of debit card : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the debit card  details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the debit card details : {result}")

        refresh_db()
        logger.info(f"Performing DB refresh")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ----------------------------------------PreConditions(Completed) - --------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 1
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"clicking on payment link")
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info(f"Entering card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enterDebitCardExpiryMonth("5")
                remote_pay_txn.enterDebitCardExpiryYear("2045")
                remote_pay_txn.enter_debit_card_cvv("111")
                remote_pay_txn.clickOnProceedToPay()
                logger.info(f"click on proceed button")
                remote_pay_txn.clickOnSuccessBtn()
                logger.info(f"click on success button")
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your actual success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from the txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer name from the txn table: {payer_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting date from the txn table: {posting_date}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table: {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table: {rrn}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Fetching status from the txn table: {status_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table: {settlement_status_db}")
            pmt_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from the txn table: {pmt_mode_db}")
            amount_db = float(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from the txn table: {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Fetching state from the txn table: {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from the txn table {payment_gateway_db}")
            acquirer_code_db = result['acquirer_code']
            logger.debug(f"Fetching acquirer code from the txn table {acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetching bank name from the txn table {bank_name_db}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch details from the cnp_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Fetching cnp_txn_state from cnp_txn table: {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching cnp_txn_auth_code from cnp_txn table : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching cnp_payment_gateway from cnp_txn table : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching cnp_payment_flow from cnp_txn table : {cnp_payment_flow}")
            txn_card_type = result['payment_option'].values[0]
            logger.debug(f"Fetching card type from cnp_txn table: {txn_card_type}")
            cnp_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment card brand name from cnp_txn table: {cnp_pmt_card_brand}")

            query = f"select * from cnpware_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch details from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching cnpware_payment_gateway from cnpware_txn table: {cnpware_payment_gateway}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": customer_name,
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.debug("Logging into the app.")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Clicking on History")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                logger.debug("Clicking on txn by txn id.")
                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {payment_status}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id from txn history for the txn : {app_payment_order_id}")
                app_payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {app_payment_status_msg}")
                app_payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer name from txn history for the txn : {app_payment_customer_name}")
                app_payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement status from txn history for the txn : {app_payment_settlement_status}")
                app_payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn :{app_payment_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "order_id": app_payment_order_id,
                    "msg": app_payment_status_msg,
                    "customer_name": app_payment_customer_name,
                    "settle_status": app_payment_settlement_status,
                    "auth_code": app_payment_auth_code,
                    "date": app_date_and_time
                }

                logger.debug(f"actualAppValues: {actual_app_values}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from api response: {amount_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer_code from api response: {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement_status from api response: {settlement_status_api}")
                state_api = response['states'][0]
                logger.debug(f"Fetching state from api response : {state_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer_code from api response: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn_type from api response: {txn_type_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org_code from api response: {org_code_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response: {payment_mode_api}")
                date_api = response["postingDate"]
                logger.debug(f"Fetching date from api response: {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "acquirer_code": acquirer_code_api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }
                logger.debug(f"actualAPIValues: {actual_api_values}")

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
                    "auth_code": auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "COMPLETED",
                    "card_type": "CNP_DC",
                }

                query = f"select * from payment_intent where id='{payment_intent_id}'"
                logger.debug(f"Query to fetch payment intent status from payment_intent table is: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table: {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": pmt_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnp_pmt_card_brand": cnp_pmt_card_brand,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status,
                    "card_type": txn_card_type
                }

                logger.debug(f"actualDBValues : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(posting_date)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "txn_id": txn_id,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    'auth_code': auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                logger.info(f"Fetching portal txn details : {transaction_details}")
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Fetching date_time from portal: {date_time}")
                txn_id_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"Fetching txn_id from portal: {txn_id_portal}")
                total_amt = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total_amt from portal: {total_amt}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal: {auth_code_portal}")
                txn_type = transaction_details[0]['Type']
                logger.debug(f"Fetching txn_type from portal: {txn_type}")
                status_portal = transaction_details[0]['Status']
                logger.debug(f"Fetching status from portal: {status_portal}")
                username = transaction_details[0]['Username']
                logger.debug(f"Fetching username from portal: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "pmt_state": str(status_portal),
                    "pmt_type": txn_type,
                    "txn_amt": total_amt[1],
                    "username": username,
                    'auth_code': auth_code_portal
                }
                logger.debug(f"expected_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                logger.info(f"date and time is: {txn_date},{txn_time}")

                expected_charge_slip_values = {
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                receipt_validator.perform_charge_slip_validations(txn_id, {"username": app_username,
                                                                           "password": app_password},
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
        try:
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["minTxnAmount"] = "1"
            api_details["RequestBody"]["settings"]["maxTxnAmount"] = "999999"
            logger.debug(f"API details : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for setting min amd max amount: {response}")
        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_448():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Org_Settings_Txn_Amt_Same_As_Max_Amt_Allowed_For_Txn
    Sub Feature Description: To verify the Remote Pay transaction when amount is exactly as Maximum amount
    set in Org setting- "Maximum amount allowed for a transaction".
    TC naming code description: 100: Payment Method, 103: RemotePay, 448: TC_448
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table: {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-----------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["remotePaymentEnabled"] = "true"
        api_details["RequestBody"]["settings"]["minTxnAmount"] = "1"
        api_details["RequestBody"]["settings"]["maxTxnAmount"] = "2"
        logger.debug(f"API details : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for Remote pay, min and max amount:  {response}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for net banking: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the net banking details : {result}")
        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for credit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for credit card : {result}")
        logger.debug(f"result length of credit card: {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the credit card details : {result}")
        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for debit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for debit card : {result}")
        logger.debug(f"result length of debit card : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the debit card  details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the debit card details : {result}")

        refresh_db()
        logger.info(f"Performing DB refresh")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)---------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 2
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"clicking on payment link")
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info(f"Entering card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enterDebitCardExpiryMonth("5")
                remote_pay_txn.enterDebitCardExpiryYear("2045")
                remote_pay_txn.enter_debit_card_cvv("111")
                remote_pay_txn.clickOnProceedToPay()
                logger.info(f"click on proceed button")
                remote_pay_txn.clickOnSuccessBtn()
                logger.info(f"click on success button")
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your actual success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from the txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer name from the txn table: {payer_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting date from the txn table: {posting_date}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table: {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table: {rrn}")
            acquirer_code_db = result['acquirer_code']
            logger.debug(f"Fetching acquirer code from the txn table {acquirer_code_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Fetching status from the txn table: {status_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table: {settlement_status_db}")
            pmt_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from the txn table: {pmt_mode_db}")
            amount_db = float(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from the txn table: {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Fetching state from the txn table: {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from the txn table {payment_gateway_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetching bank name from the txn table {bank_name_db}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch details from the cnp_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Fetching cnp_txn_state from cnp_txn table: {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching cnp_txn_auth_code from cnp_txn table : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching cnp_payment_gateway from cnp_txn table : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching cnp_payment_flow from cnp_txn table : {cnp_payment_flow}")
            txn_card_type = result['payment_option'].values[0]
            logger.debug(f"Fetching card type from cnp_txn table: {txn_card_type}")
            cnp_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment card brand name from cnp_txn table: {cnp_pmt_card_brand}")

            query = f"select * from cnpware_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch details from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching cnpware_payment_gateway from cnpware_txn table: {cnpware_payment_gateway}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "msg": "PAYMENT SUCCESSFUL",
                    "customer_name": customer_name,
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.debug("Logging into the app.")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Clicking on History")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                logger.debug("Clicking on txn by txn id.")
                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {payment_status}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id from txn history for the txn : {app_payment_order_id}")
                app_payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {app_payment_status_msg}")
                app_payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer name from txn history for the txn : {app_payment_customer_name}")
                app_payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement status from txn history for the txn : {app_payment_settlement_status}")
                app_payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn :{app_payment_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "order_id": app_payment_order_id,
                    "msg": app_payment_status_msg,
                    "customer_name": app_payment_customer_name,
                    "settle_status": app_payment_settlement_status,
                    "auth_code": app_payment_auth_code,
                    "date": app_date_and_time
                }

                logger.debug(f"actualAppValues: {actual_app_values}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from api response : {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from api response: {amount_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer_code from api response: {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement_status from api response: {settlement_status_api}")
                state_api = response['states'][0]
                logger.debug(f"Fetching state from api response : {state_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer_code from api response: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn_type from api response: {txn_type_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org_code from api response: {org_code_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response: {payment_mode_api}")
                date_api = response["postingDate"]
                logger.debug(f"Fetching date from api response: {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "acquirer_code": acquirer_code_api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }
                logger.debug(f"actualAPIValues: {actual_api_values}")

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
                    "auth_code": auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "COMPLETED",
                    "card_type": "CNP_DC",
                }

                query = f"select * from payment_intent where id='{payment_intent_id}'"
                logger.debug(f"Query to fetch payment intent status from payment_intent table is: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table: {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": pmt_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "pmt_gateway": payment_gateway_db,
                    "auth_code": cnp_txn_auth_code,
                    "cnp_pmt_gateway": cnp_payment_gateway,
                    "cnp_pmt_card_brand": cnp_pmt_card_brand,
                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                    "pmt_flow": cnp_payment_flow,
                    "pmt_intent_status": payment_intent_status,
                    "card_type": txn_card_type
                }

                logger.debug(f"actualDBValues : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(posting_date)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "txn_id": txn_id,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": app_username,
                    'auth_code': auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                logger.info(f"Fetching portal txn details : {transaction_details}")
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Fetching date_time from portal: {date_time}")
                txn_id_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"Fetching txn_id from portal: {txn_id_portal}")
                total_amt = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total_amt from portal: {total_amt}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal: {auth_code_portal}")
                txn_type = transaction_details[0]['Type']
                logger.debug(f"Fetching txn_type from portal: {txn_type}")
                status_portal = transaction_details[0]['Status']
                logger.debug(f"Fetching status from portal: {status_portal}")
                username = transaction_details[0]['Username']
                logger.debug(f"Fetching username from portal: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "pmt_state": str(status_portal),
                    "pmt_type": txn_type,
                    "txn_amt": total_amt[1],
                    "username": username,
                    'auth_code': auth_code_portal
                }
                logger.debug(f"expected_portal_values : {actual_portal_values}")

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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                logger.info(f"date and time is: {txn_date},{txn_time}")

                expected_charge_slip_values = {
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': '' if auth_code is None else auth_code
                }

                receipt_validator.perform_charge_slip_validations(txn_id, {"username": app_username,
                                                                           "password": app_password},
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
        try:
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["minTxnAmount"] = "1"
            api_details["RequestBody"]["settings"]["maxTxnAmount"] = "999999"
            logger.debug(f"API details : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for setting min amd max amount: {response}")
        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_449():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Org_Settings_Txn_Amt_Less_Than_Min_Amt_Allowed_For_Txn
    Sub Feature Description: To verify the Remote Pay transaction when amount is less than Minimum amount set in Org
    Setting - "Minimum amount allowed for a transaction".
    TC naming code description: 100: Payment Method, 103: RemotePay, 449: TC_449
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table: {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-----------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["remotePaymentEnabled"] = "true"
        api_details["RequestBody"]["settings"]["minTxnAmount"] = "2"
        api_details["RequestBody"]["settings"]["maxTxnAmount"] = "10"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for Remote pay, min and max amount:  {response}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for net banking: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the net banking details : {result}")
        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for credit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for credit card : {result}")
        logger.debug(f"result length of credit card: {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the credit card details : {result}")
        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for debit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for debit card : {result}")
        logger.debug(f"result length of debit card : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the debit card  details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the debit card details : {result}")

        refresh_db()
        logger.info(f"Performing DB refresh")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 1
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received from payment link api is: {response}")
            success = response['success']
            logger.info(f"success value from api response is: {success}")
            error_message = response['errorMessage']
            logger.info(f"error message received from api response is: {error_message}")

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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:

                expected_api_values = {
                    "success": False,
                    "error_message": f"Transaction amount is less than the allowed limit."
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": success,
                    "error_message": error_message
                }
                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["minTxnAmount"] = "1"
            api_details["RequestBody"]["settings"]["maxTxnAmount"] = "999999"
            logger.debug(f"API details : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for setting min and max txn amount: {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_450():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Org_Settings_Txn_Amt_More_Than_Max_Amt_Allowed_For_Txn
    Sub Feature Description: To verify the Remote Pay transaction when amount is more than Maximum amount set in Org
    setting- "Maximum amount allowed for a transaction".
    TC naming code description: 100: Payment Method, 103: RemotePay, 450: TC_450
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table: {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-----------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["remotePaymentEnabled"] = "true"
        api_details["RequestBody"]["settings"]["minTxnAmount"] = "2"
        api_details["RequestBody"]["settings"]["maxTxnAmount"] = "10"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for Remote pay, min and max amount:  {response}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for net banking: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the net banking details : {result}")
        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for credit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for credit card : {result}")
        logger.debug(f"result length of credit card: {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the credit card details : {result}")
        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for debit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for debit card : {result}")
        logger.debug(f"result length of debit card : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the debit card  details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the debit card details : {result}")

        refresh_db()
        logger.info(f"Performing DB refresh")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)---------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 11
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received from payment link api is: {response}")
            success = response['success']
            logger.info(f"success value from api response is: {success}")
            error_message = response['errorMessage']
            logger.info(f"error message received from api response is: {error_message}")

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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:

                expected_api_values = {
                    "success": False,
                    "error_message": f"Transaction amount is greater than the allowed limit."
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": success,
                    "error_message": error_message
                }
                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["minTxnAmount"] = "1"
            api_details["RequestBody"]["settings"]["maxTxnAmount"] = "999999"
            logger.debug(f"API details : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for setting min and max txn amount: {response}")

        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)