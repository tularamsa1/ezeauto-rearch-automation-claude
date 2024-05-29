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
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.uiVal
def test_common_100_111_051():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Multi_Account_Label2_In_Request_Default_Label1
    Sub Feature Description: Verify Remote Pay txn by sending LABEL2 in request when default is acc1.
    TC naming code description:100: Payment Method, 111: MultiAcc_RemotePay, 051: TC_051

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
        logger.debug(f"Query result, org_code : {org_code}")
        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"account_label_name: {account_label_name}")
        account2_label_name = account_labels['name2']
        logger.debug(f"account2_label_name: {account2_label_name}")

        query = f"select id from label where name='{account2_label_name}' and org_code='{org_code}';"
        logger.debug(f"Query to fetch id from the label table is: {query}")
        result = DBProcessor.getValueFromDB(query)
        acc_label_id = result['id'].values[0]
        logger.debug(f"Fetching account label id from label table is : {acc_label_id}")

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
        logger.info(f"Perform DB refresh")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------PreConditions(Completed)--------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(3000, 5000)
            logger.info(f"Entered amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "accountLabel": str(account2_label_name)
            })
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"Clicking on payment link")
                ui_browser.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(ui_browser)
                remote_pay_txn.clickOnCreditCardToExpand()
                logger.info(f"Entering card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("5")
                remote_pay_txn.enterCreditCardExpiryYear("2045")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                logger.info(f"click on proceed button")
                remote_pay_txn.clickOnSuccessBtn()
                logger.info(f"click on success button")
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected message is:  {expected_message}")
                assert expected_message == success_message, "Success message is not matching."

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
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is : {created_time}")
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
            txn_type_db = result['txn_type'].values[0]
            logger.debug(f"Fetching txn type from the txn table {txn_type_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table {acquirer_code_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table: {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table: {tid_db}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"Fetching label id from the txn table: {label_ids}")
            bank_code_db = result['bank_code'].values[0]
            logger.debug(f"Fetching bank code from the txn table: {bank_code_db}")

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
            cnp_txn_card_type = result['payment_option'].values[0]
            logger.debug(f"Fetching card type from cnp_txn table: {cnp_txn_card_type}")
            cnp_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment card brand name from cnp_txn table: {cnp_pmt_card_brand}")

            query = f"select * from cnpware_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch details from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching cnpware_payment_gateway from cnpware_txn table: {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnpware_txn table: {cnpware_payment_flow}")

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
                    "txn_amt": "{:,.2f}".format(amount),
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
                login_page.perform_login(app_username, app_password)
                logger.debug("Logging into the app.")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Clicking on txn history page.")
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
                logger.info(f"Fetching txn orderId from txn history for the txn : {app_payment_order_id}")
                app_payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {app_payment_status_msg}")
                app_payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer name from txn history for the txn : {app_payment_customer_name}")
                app_payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement status from txn history for the txn : {app_payment_settlement_status}")
                app_payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth code from txn history for the txn :{app_payment_auth_code}")
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
                date = date_time_converter.db_datetime(created_time)

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
                    "date": date,
                    "acc_label_name": str(account2_label_name)
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
                    "pmt_state": txn_state,
                    "acquirer_code": acquirer_code__api,
                    "settle_status": settlement_status_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "acc_label_name": str(account_label_name_api)
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
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "COMPLETED",
                    "card_type": "CNP_CC",
                    "acc_label_id": str(acc_label_id)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from payment_intent where id='{payment_intent_id}';"
                logger.debug(f"Query to fetch payment_intent table : {query} ")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of payment_intent table is : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table is : {payment_intent_status}")

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
                    "card_type": cnp_txn_card_type,
                    "acc_label_id": str(label_ids)
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "acc_label": str(account2_label_name)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code: {auth_code_portal}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status_portal = transaction_details[0]['Status']
                logger.debug(f"status: {status_portal}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status_portal),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "acc_label": labels
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
                expected_values = {
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': "Rs.{:,.2f}".format(amount),
                    'date': txn_date,
                    'time': txn_time,
                    "AUTH CODE": '' if auth_code is None else auth_code
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
def test_common_100_111_052():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Multi_Account_No_Label_In_Request_Default_Label1
    Sub Feature Description: Verify Remote Pay txn by sending no label in request when default label 1
    TC naming code description: 100: Payment Method, 111: MultiAcc_RemotePay, 052: TC_052
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

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"account_label_name: {account_label_name}")

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

            amount = random.randint(100, 500)
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"response received for remote pay initiate api is : {response} ")
            success = response['success']
            logger.info(f"success status is: {success}")
            error_message = response['errorMessage']
            logger.info(f"error message is : {error_message}")
            real_code_api = response['realCode']
            logger.info(f"real code is: {real_code_api}")

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
                    "error_message": f"Input parameter missing: Account label",
                    "real_code": "INPUT_PARAM_MISSING"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": success,
                    "error_message": error_message,
                    "real_code": real_code_api
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
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_111_053():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Multi_Account_No_Label_In_Request_Default_Label_Not_Configured
    Sub Feature Description: Verify Remote Pay txn by sending no label in request when default label is not configured.
    TC naming code description: 100: Payment Method, 111: MultiAcc_RemotePay, 053: TC_053
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
            "username": portal_username, "password": portal_password, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"] = {"defaultAccount": ""}
        logger.debug(f"API details : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting defaultAccount is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # # -----------------------------------------PreConditions(Completed)---------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(100, 500)
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"response received for remote pay initiate api is : {response} ")
            success = response['success']
            logger.info(f"success status is: {success}")
            error_message = response['errorMessage']
            logger.info(f"error message is : {error_message}")
            real_code_api = response['realCode']
            logger.info(f"real code is: {real_code_api}")

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
                    "error_message": f"Input parameter missing: Account label",
                    "real_code": "INPUT_PARAM_MISSING"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": success,
                    "error_message": error_message,
                    "real_code": real_code_api
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
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_111_054():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Multi_Account_No_Label_In_Request_RemotePay_Disabled
    Sub Feature Description: Verify Remote Pay txn by sending no label in request when payment mode "Remote Pay" is disabled.
    TC naming code description: 100: Payment Method, 111: MultiAcc_RemotePay, 598: TC_598
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

        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"account_label_name: {account_label_name}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["remotePaymentEnabled"] = "false"
        logger.debug(f"API details : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for Remote Pay to be disabled: {response}")

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

            amount = random.randint(100, 500)
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"response received for remote pay initiate api is : {response} ")
            success = response['success']
            logger.info(f"success status is: {success}")
            error_message = response['errorMessage']
            logger.info(f"error message is : {error_message}")
            real_code_api = response['realCode']
            logger.info(f"real code is: {real_code_api}")

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
                    "error_message": f"Remote pay is not supported!",
                    "real_code": "REMOTEPAY_NOT_ENABLED"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": success,
                    "error_message": error_message,
                    "real_code": real_code_api
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
            api_details["RequestBody"]["settings"]["remotePaymentEnabled"] = "true"
            logger.debug(f"API details : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for enabling Remote Pay: {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.uiVal
def test_common_100_111_050():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Multi_Account_Label1_In_Request_Default_Label_Empty
    Sub Feature Description: Verify Remote Pay txn by sending LABEL1 in request when default is not set
    TC naming code description:100: Payment Method, 111: MultiAcc, 050: TC050
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
        query = f"select * from merchant_pg_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch details from the merchant_pg_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"Fetching acc_label_id from the merchant_pg_config table : {acc_label_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["defaultAccount"] = ""
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for default account setup to be enabled:  {response}")

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
                logger.debug(f"Query to fetch txn details from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                txn_id = result['id'].values[0]
                logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
                created_time = result['created_time'].values[0]
                logger.debug(f"Fetching created_time from the txn table : {created_time}")
                acquirer_code = result['acquirer_code'].values[0]
                logger.debug(f"Fetching acquirer_code from the txn table : {acquirer_code}")
                auth_code = result['auth_code'].values[0]
                logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
                customer_name_txn = result['customer_name'].values[0]
                logger.debug(f"Fetching customer_name from the txn table : {customer_name_txn}")
                payer_name = result['payer_name'].values[0]
                logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
                rrn = result['rr_number'].values[0]
                logger.debug(f"Fetching rr_number from the txn table : {rrn}")
                settle_status = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status from the txn table : {settle_status}")
                pmt_status = result['status'].values[0]
                logger.debug(f"Fetching status from the txn table : {pmt_status}")
                payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from the txn table : {payment_mode}")
                issuer_code_txn = result['issuer_code'].values[0]
                logger.debug(f"Fetching issuer_code from the txn table : {issuer_code_txn}")
                pmt_state = result['state'].values[0]
                logger.debug(f"Fetching state from the txn table : {pmt_state}")
                amount_txn = result['amount'].values[0]
                logger.debug(f"Fetching amount from the txn table : {amount_txn}")
                merchant_name = result['merchant_name'].values[0]
                logger.debug(f"Fetching merchant_name from the txn table : {merchant_name}")
                order_id_txn = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from the txn table : {order_id_txn}")
                org_code_txn = result['org_code'].values[0]
                logger.debug(f"Fetching org_code from the txn table : {org_code_txn}")
                customer_mobile_txn = result['customer_mobile'].values[0]
                logger.debug(f"Fetching customer_mobile from the txn table : {customer_mobile_txn}")
                mid_txn = result['mid'].values[0]
                logger.debug(f"Fetching mid from the txn table : {mid_txn}")
                tid_txn = result['tid'].values[0]
                logger.debug(f"Fetching tid from the txn table : {tid_txn}")
                payment_gateway = result["payment_gateway"].values[0]
                logger.debug(f"Fetching payment_gateway from the txn table : {payment_gateway}")
                label_ids = str(result['label_ids'].values[0]).strip(',')
                logger.debug(f"Fetching label_ids from the txn tabl : {label_ids}")

                query = f"select * from payment_intent where id = '{payment_intent_id}'"
                logger.debug(f"Query to fetch data from the payment_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from payment_intent table :{result}")
                payment_intent_status = result["status"].values[0]
                logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

                query = f"select * from cnp_txn where txn_id = '{txn_id}'"
                logger.debug(f"Query to fetch data from the cnp_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result for cnp_txn table : {result} ")
                cnp_txn_rrn = result['rr_number'].values[0]
                logger.debug(f"Fetching rr_number from cnp_txn table : {cnp_txn_rrn}")
                cnp_txn_payment_option = result['payment_option'].values[0]
                logger.debug(f"Fetching payment_option from cnp_txn table : {cnp_txn_payment_option}")
                cnp_txn_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnp_txn table : {cnp_txn_payment_flow}")
                cnp_txn_payment_status = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnp_txn table : {cnp_txn_payment_status}")
                cnp_txn_type = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnp_txn table : {cnp_txn_type}")
                cnp_txn_payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnp_txn table : {cnp_txn_payment_mode}")
                cnp_txn_payment_state = result['state'].values[0]
                logger.debug(f"Fetching state from cnp_txn table : {cnp_txn_payment_state}")
                cnp_txn_payment_card_bin = result['payment_card_bin'].values[0]
                logger.debug(f"Fetching payment_card_bin from cnp_txn table : {cnp_txn_payment_card_bin}")
                cnp_txn_payment_card_brand = result['payment_card_brand'].values[0]
                logger.debug(f"Fetching payment_card_brand from cnp_txn table : {cnp_txn_payment_card_brand}")
                cnp_txn_payment_card_type = result['payment_card_type'].values[0]
                logger.debug(f"Fetching payment_card_type from cnp_txn table : {cnp_txn_payment_card_type}")
                cnp_txn_acquirer_code = result['acquirer_code'].values[0]
                logger.debug(f"Fetching acquirer_code from cnp_txn table : {cnp_txn_acquirer_code}")
                cnp_txn_issuer_code = result['issuer_code'].values[0]
                logger.debug(f"Fetching issuer_code from cnp_txn table : {cnp_txn_issuer_code}")
                cnp_txn_card_last_four_digit = result['card_last_four_digit'].values[0]
                logger.debug(f"Fetching card_last_four_digit from cnp_txn table : {cnp_txn_card_last_four_digit}")
                cnp_txn_org_code = result['org_code'].values[0]
                logger.debug(f"Fetching org_code from cnp_txn table : {cnp_txn_org_code}")
                cnp_txn_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from cnp_txn table : {cnp_txn_payment_gateway}")

                query = f"select * from cnpware_txn where txn_id = '{txn_id}'"
                logger.debug(f"Query to fetch data from the cnpware_txn table : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                logger.debug(f"Fetching result for cnpware_txn table : {result} ")
                cnpware_txn_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnpware_txn table : {cnpware_txn_payment_flow}")
                cnpware_txn_payment_status = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnpware_txn table : {cnpware_txn_payment_status}")
                cnpware_txn_type = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnpware_txn table : {cnpware_txn_type}")
                cnpware_txn_payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnpware_txn table : {cnpware_txn_payment_mode}")
                cnpware_txn_payment_state = result['state'].values[0]
                logger.debug(f"Fetching state from cnpware_txn table : {cnpware_txn_payment_state}")
                cnpware_txn_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from cnpware_txn table : {cnpware_txn_payment_gateway}")
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
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "customer_name": customer_name_txn,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile_txn,
                    "card": "*5449",
                    "auth_code": auth_code
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
                login_page = LoginPage(driver=app_driver)
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page = HomePage(driver=app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history : {txn_id}, {app_settle_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history : {txn_id}, {app_customer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history : {txn_id}, {app_customer_mobile}")
                app_card = txn_history_page.fetch_card_text()
                logger.info(f"Fetching card from txn history : {txn_id}, {app_card}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history : {txn_id}, {app_auth_code}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settle_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_time,
                    "customer_mobile": app_customer_mobile,
                    "card": app_card,
                    "auth_code": app_auth_code
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "name_on_card": payer_name,
                    "customer_mobile": customer_mobile_txn,
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": auth_code,
                    "acc_label_id": str(account_label_name)
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount : {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode : {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status : {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state : {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid : {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid : {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status : {api_settle_status}")
                api_issuer_code = response.get('issuerCode')
                logger.debug(f"From response fetch issuer_code : {api_issuer_code}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type : {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code : {api_org_code}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time : {api_date_time}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name : {api_merchant_name}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number : {api_ext_ref_number}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name : {api_customer_name}")
                api_payer_name = response.get('payerName')
                logger.debug(f"From response fetch payer_name : {api_payer_name}")
                api_name_on_card = response.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card : {api_name_on_card}")
                api_customer_mobile = response.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile : {api_customer_mobile}")
                api_payment_gateway = response.get('paymentGateway')
                logger.debug(f"From response fetch paymentGateway : {api_payment_gateway}")
                api_auth_code = response.get('authCode')
                logger.debug(f"From response fetch authCode : {api_auth_code}")
                api_account_label_name = response.get("accountLabel")
                logger.debug(f"From response fetch account_label : {api_account_label_name} ")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "customer_mobile": api_customer_mobile,
                    "pmt_gateway": api_payment_gateway,
                    "auth_code": api_auth_code,
                    "acc_label_id": str(api_account_label_name)
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
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_intent_status": "COMPLETED",

                    "cnp_pmt_option": "CNP_CC",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "cnp_pmt_state": "SETTLED",
                    "cnp_pmt_card_bin": "526731",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnp_pmt_card_type": "CREDIT",
                    "cnp_acquirer_code": "HDFC",
                    "cnp_issuer_code": "HDFC",
                    "cnp_card_last_four_digit": "5449",
                    "cnp_org_code": org_code,
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "cnpware_pmt_status": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state": "SETTLED",
                    "cnpware_pmt_mode": "CNP",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY",
                    "acc_label_id": str(acc_label_id)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "settle_status": settle_status,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "pmt_gateway": payment_gateway,
                    "pmt_intent_status": payment_intent_status,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_pmt_card_bin": cnp_txn_payment_card_bin,
                    "cnp_pmt_card_brand": cnp_txn_payment_card_brand,
                    "cnp_pmt_card_type": cnp_txn_payment_card_type,
                    "cnp_acquirer_code": cnp_txn_acquirer_code,
                    "cnp_issuer_code": cnp_txn_issuer_code,
                    "cnp_card_last_four_digit": cnp_txn_card_last_four_digit,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "cnpware_pmt_status": cnpware_txn_payment_status,
                    "cnpware_pmt_state": cnpware_txn_payment_state,
                    "cnpware_pmt_mode": cnpware_txn_payment_mode,
                    "cnpware_pmt_flow": cnpware_txn_payment_flow,
                    "cnpware_pmt_gateway": cnpware_txn_payment_gateway,
                    "cnpware_txn_type": cnpware_txn_type,
                    "acc_label_id": str(label_ids)
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
                # --------------------------------------------------------------------------------------------
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "acc_label": str(account_label_name)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[0]['Total Amount']
                logger.info(f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_rrn = transaction_details[0]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[0]['Status']
                logger.info(f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")
                portal_auth_code = transaction_details[0]['Auth Code']
                logger.info(f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")
                portal_labels = transaction_details[0]['Labels']
                logger.info(f"Fetching Labels from portal txn history for the order_id : {order_id}, {portal_labels}")

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "rrn": portal_rrn,
                    "auth_code": portal_auth_code,
                    "acc_label": portal_labels
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
                expected_charge_slip_values = {
                    "payment_option": "SALE",
                    "merchant_ref_no": 'Ref # ' + str(order_id),
                    "RRN": "" if rrn is None else rrn,
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "MID": mid_txn,
                    "TID": tid_txn,
                    "time": txn_time,
                    "CARD": f"XXXX-XXXX-XXXX-5449",
                    "CARD TYPE": "MasterCard",
                    "AUTH CODE": str(auth_code).strip()
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
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
            api_details["RequestBody"]["settings"]["defaultAccount"] = "acc1"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for revert back default account setup:  {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.uiVal
def test_common_100_111_055():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Multi_Account_Label2_In_Request_Default_Label_Empty
    Sub Feature Description: Verify Remote Pay txn by sending LABEL2 in request when default is not set
    TC naming code description:100: Payment Method, 112: MultiAcc, 055: TC055
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
        logger.debug(f"account_label_name: {account_label_name}")
        query = f"select * from merchant_pg_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch details from the merchant_pg_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"Fetching acc_label_id from the merchant_pg_config table : {acc_label_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["defaultAccount"] = ""
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for default account setup to be enabled:  {response}")

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
                logger.debug(f"Query to fetch txn details from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                txn_id = result['id'].values[0]
                logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
                created_time = result['created_time'].values[0]
                logger.debug(f"Fetching created_time from the txn table : {created_time}")
                acquirer_code = result['acquirer_code'].values[0]
                logger.debug(f"Fetching acquirer_code from the txn table : {acquirer_code}")
                auth_code = result['auth_code'].values[0]
                logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
                customer_name_txn = result['customer_name'].values[0]
                logger.debug(f"Fetching customer_name from the txn table : {customer_name_txn}")
                payer_name = result['payer_name'].values[0]
                logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
                rrn = result['rr_number'].values[0]
                logger.debug(f"Fetching rr_number from the txn table : {rrn}")
                settle_status = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status from the txn table : {settle_status}")
                pmt_status = result['status'].values[0]
                logger.debug(f"Fetching status from the txn table : {pmt_status}")
                payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from the txn table : {payment_mode}")
                issuer_code_txn = result['issuer_code'].values[0]
                logger.debug(f"Fetching issuer_code from the txn table : {issuer_code_txn}")
                pmt_state = result['state'].values[0]
                logger.debug(f"Fetching state from the txn table : {pmt_state}")
                amount_txn = result['amount'].values[0]
                logger.debug(f"Fetching amount from the txn table : {amount_txn}")
                merchant_name = result['merchant_name'].values[0]
                logger.debug(f"Fetching merchant_name from the txn table : {merchant_name}")
                order_id_txn = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from the txn table : {order_id_txn}")
                org_code_txn = result['org_code'].values[0]
                logger.debug(f"Fetching org_code from the txn table : {org_code_txn}")
                customer_mobile_txn = result['customer_mobile'].values[0]
                logger.debug(f"Fetching customer_mobile from the txn table : {customer_mobile_txn}")
                mid_txn = result['mid'].values[0]
                logger.debug(f"Fetching mid from the txn table : {mid_txn}")
                tid_txn = result['tid'].values[0]
                logger.debug(f"Fetching tid from the txn table : {tid_txn}")
                payment_gateway = result["payment_gateway"].values[0]
                logger.debug(f"Fetching payment_gateway from the txn table : {payment_gateway}")
                label_ids = str(result['label_ids'].values[0]).strip(',')
                logger.debug(f"Fetching label_ids from the txn tabl : {label_ids}")

                query = f"select * from payment_intent where id = '{payment_intent_id}'"
                logger.debug(f"Query to fetch data from the payment_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from payment_intent table :{result}")
                payment_intent_status = result["status"].values[0]
                logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

                query = f"select * from cnp_txn where txn_id = '{txn_id}'"
                logger.debug(f"Query to fetch data from the cnp_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result for cnp_txn table : {result} ")
                cnp_txn_rrn = result['rr_number'].values[0]
                logger.debug(f"Fetching rr_number from cnp_txn table : {cnp_txn_rrn}")
                cnp_txn_payment_option = result['payment_option'].values[0]
                logger.debug(f"Fetching payment_option from cnp_txn table : {cnp_txn_payment_option}")
                cnp_txn_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnp_txn table : {cnp_txn_payment_flow}")
                cnp_txn_payment_status = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnp_txn table : {cnp_txn_payment_status}")
                cnp_txn_type = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnp_txn table : {cnp_txn_type}")
                cnp_txn_payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnp_txn table : {cnp_txn_payment_mode}")
                cnp_txn_payment_state = result['state'].values[0]
                logger.debug(f"Fetching state from cnp_txn table : {cnp_txn_payment_state}")
                cnp_txn_payment_card_bin = result['payment_card_bin'].values[0]
                logger.debug(f"Fetching payment_card_bin from cnp_txn table : {cnp_txn_payment_card_bin}")
                cnp_txn_payment_card_brand = result['payment_card_brand'].values[0]
                logger.debug(f"Fetching payment_card_brand from cnp_txn table : {cnp_txn_payment_card_brand}")
                cnp_txn_payment_card_type = result['payment_card_type'].values[0]
                logger.debug(f"Fetching payment_card_type from cnp_txn table : {cnp_txn_payment_card_type}")
                cnp_txn_acquirer_code = result['acquirer_code'].values[0]
                logger.debug(f"Fetching acquirer_code from cnp_txn table : {cnp_txn_acquirer_code}")
                cnp_txn_issuer_code = result['issuer_code'].values[0]
                logger.debug(f"Fetching issuer_code from cnp_txn table : {cnp_txn_issuer_code}")
                cnp_txn_card_last_four_digit = result['card_last_four_digit'].values[0]
                logger.debug(f"Fetching card_last_four_digit from cnp_txn table : {cnp_txn_card_last_four_digit}")
                cnp_txn_org_code = result['org_code'].values[0]
                logger.debug(f"Fetching org_code from cnp_txn table : {cnp_txn_org_code}")
                cnp_txn_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from cnp_txn table : {cnp_txn_payment_gateway}")

                query = f"select * from cnpware_txn where txn_id = '{txn_id}'"
                logger.debug(f"Query to fetch data from the cnpware_txn table : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                logger.debug(f"Fetching result for cnpware_txn table : {result} ")
                cnpware_txn_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnpware_txn table : {cnpware_txn_payment_flow}")
                cnpware_txn_payment_status = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnpware_txn table : {cnpware_txn_payment_status}")
                cnpware_txn_type = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnpware_txn table : {cnpware_txn_type}")
                cnpware_txn_payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnpware_txn table : {cnpware_txn_payment_mode}")
                cnpware_txn_payment_state = result['state'].values[0]
                logger.debug(f"Fetching state from cnpware_txn table : {cnpware_txn_payment_state}")
                cnpware_txn_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from cnpware_txn table : {cnpware_txn_payment_gateway}")
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
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "customer_name": customer_name_txn,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile_txn,
                    "card": "*5449",
                    "auth_code": auth_code
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
                login_page = LoginPage(driver=app_driver)
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page = HomePage(driver=app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history : {txn_id}, {app_settle_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history : {txn_id}, {app_customer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history : {txn_id}, {app_customer_mobile}")
                app_card = txn_history_page.fetch_card_text()
                logger.info(f"Fetching card from txn history : {txn_id}, {app_card}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history : {txn_id}, {app_auth_code}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settle_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_time,
                    "customer_mobile": app_customer_mobile,
                    "card": app_card,
                    "auth_code": app_auth_code
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "name_on_card": payer_name,
                    "customer_mobile": customer_mobile_txn,
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": auth_code,
                    "acc_label_id": str(account_label_name)
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount : {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode : {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status : {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state : {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid : {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid : {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status : {api_settle_status}")
                api_issuer_code = response.get('issuerCode')
                logger.debug(f"From response fetch issuer_code : {api_issuer_code}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type : {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code : {api_org_code}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time : {api_date_time}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name : {api_merchant_name}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number : {api_ext_ref_number}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name : {api_customer_name}")
                api_payer_name = response.get('payerName')
                logger.debug(f"From response fetch payer_name : {api_payer_name}")
                api_name_on_card = response.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card : {api_name_on_card}")
                api_customer_mobile = response.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile : {api_customer_mobile}")
                api_payment_gateway = response.get('paymentGateway')
                logger.debug(f"From response fetch paymentGateway : {api_payment_gateway}")
                api_auth_code = response.get('authCode')
                logger.debug(f"From response fetch authCode : {api_auth_code}")
                api_account_label_name = response.get("accountLabel")
                logger.debug(f"From response fetch account_label : {api_account_label_name} ")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "customer_mobile": api_customer_mobile,
                    "pmt_gateway": api_payment_gateway,
                    "auth_code": api_auth_code,
                    "acc_label_id": str(api_account_label_name)
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
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_intent_status": "COMPLETED",

                    "cnp_pmt_option": "CNP_CC",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "cnp_pmt_state": "SETTLED",
                    "cnp_pmt_card_bin": "526731",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnp_pmt_card_type": "CREDIT",
                    "cnp_acquirer_code": "HDFC",
                    "cnp_issuer_code": "HDFC",
                    "cnp_card_last_four_digit": "5449",
                    "cnp_org_code": org_code,
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "cnpware_pmt_status": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state": "SETTLED",
                    "cnpware_pmt_mode": "CNP",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY",
                    "acc_label_id": str(acc_label_id)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "settle_status": settle_status,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "pmt_gateway": payment_gateway,
                    "pmt_intent_status": payment_intent_status,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_pmt_card_bin": cnp_txn_payment_card_bin,
                    "cnp_pmt_card_brand": cnp_txn_payment_card_brand,
                    "cnp_pmt_card_type": cnp_txn_payment_card_type,
                    "cnp_acquirer_code": cnp_txn_acquirer_code,
                    "cnp_issuer_code": cnp_txn_issuer_code,
                    "cnp_card_last_four_digit": cnp_txn_card_last_four_digit,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "cnpware_pmt_status": cnpware_txn_payment_status,
                    "cnpware_pmt_state": cnpware_txn_payment_state,
                    "cnpware_pmt_mode": cnpware_txn_payment_mode,
                    "cnpware_pmt_flow": cnpware_txn_payment_flow,
                    "cnpware_pmt_gateway": cnpware_txn_payment_gateway,
                    "cnpware_txn_type": cnpware_txn_type,
                    "acc_label_id": str(label_ids)
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
                # --------------------------------------------------------------------------------------------
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "acc_label": str(account_label_name)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[0]['Total Amount']
                logger.info(f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_rrn = transaction_details[0]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[0]['Status']
                logger.info(f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")
                portal_auth_code = transaction_details[0]['Auth Code']
                logger.info(f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")
                portal_labels = transaction_details[0]['Labels']
                logger.info(f"Fetching Labels from portal txn history for the order_id : {order_id}, {portal_labels}")

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "rrn": portal_rrn,
                    "auth_code": portal_auth_code,
                    "acc_label": portal_labels
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
                expected_charge_slip_values = {
                    "payment_option": "SALE",
                    "merchant_ref_no": 'Ref # ' + str(order_id),
                    "RRN": "" if rrn is None else rrn,
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "MID": mid_txn,
                    "TID": tid_txn,
                    "time": txn_time,
                    "CARD": f"XXXX-XXXX-XXXX-5449",
                    "CARD TYPE": "MasterCard",
                    "AUTH CODE": str(auth_code).strip()
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
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
            api_details["RequestBody"]["settings"]["defaultAccount"] = "acc1"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for revert back default account setup:  {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)