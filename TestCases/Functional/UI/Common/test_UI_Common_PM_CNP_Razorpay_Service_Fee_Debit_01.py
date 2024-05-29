import random
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
def test_common_100_103_490():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Debit_Only_Enabled_Amt_FIXED_JSON_Debit_With_FIXED_Scheme_Debit_Card_Details
    Sub Feature Description: Verify Service Fee calculated when debit only enabled and amount ranges with FIXED is
    passed and JSON is debit with FIXED scheme with Debit Card details.
    TC naming code description: 100: Payment Method, 103: RemotePay, 490: TC_490
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

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
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
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
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

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "MASTER_CARD"
        payment_by = "DEBIT"
        json_id = "service_fee_json_TC_100_103_490"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "FIXED"
        bank = "NULL"
        flat_fee, percent = testsuite_teardown.create_service_fee_config_data(portal_username=portal_username,
                                                                              org_code=org_code,
                                                                              derivation_type=derivation_type,
                                                                              scheme=scheme, payment_by=payment_by,
                                                                              config_data_json_id=json_id,
                                                                              payment_mode=payment_mode,
                                                                              account_label=acc_label, bank=bank)
        logger.info(f"flat_fee is: {flat_fee}")
        logger.info(f"fee percentage is: {percent}")

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

            amount = random.randint(36, 40)
            logger.info(f"amount is: {amount}")
            flat_fee = float(flat_fee) if flat_fee is not 'NULL' else 0.0
            percent = float(percent) if percent is not 'NULL' else 0.0
            logger.debug(f"Flat Fee : {flat_fee},Percentage : {percent}")
            service_fee = round((amount * percent / 100) + flat_fee, 2)
            total_amount = amount + service_fee
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
                logger.info(f"Initiating a card txn")
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info(f"Entering card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enter_debit_expiry_month_debit_only("5")
                remote_pay_txn.enter_debit_expiry_year_debit_only("2045")
                remote_pay_txn.enter_debit_card_cvv("111")
                actual_service_fee = remote_pay_txn.fetch_service_fee()
                logger.debug(f"fetching actual service_fee = {actual_service_fee}")
                actual_order_amount = remote_pay_txn.fetch_order_amount()
                logger.debug(f"fetching actual order_amount = {actual_order_amount}")
                actual_total_amount = remote_pay_txn.fetch_total_amount()
                logger.debug(f"fetching actual total_amount = {actual_total_amount}")

                remote_pay_txn.clickOnProceedToPay()
                logger.info(f"click on proceed button")
                remote_pay_txn.clickOnSuccessBtn()
                logger.info(f"click on success button")
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your actual success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."

                actual_service_fee = float(actual_service_fee.replace("₹", ""))
                logger.info(f"actual service fee is:  {actual_service_fee}")
                logger.info(f"expected service fee is:  {service_fee}")
                actual_order_amount = int(float(actual_order_amount.replace("₹", "")))
                logger.info(f"actual order amount is:  {actual_order_amount}")
                logger.info(f"expected order amount is:  {amount}")
                actual_total_amount = float(actual_total_amount.replace("₹", ""))
                logger.info(f"actual total amount is:  {actual_total_amount}")
                logger.info(f"expected total mount is:  {total_amount}")
                assert service_fee == actual_service_fee, "Service Fee is not matching."
                assert amount == actual_order_amount, "Amount is not matching."
                assert total_amount == actual_total_amount, "Total amount is not matching."

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
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetching bank name from the txn table {bank_name_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Fetching status from the txn table: {status_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table: {settlement_status_db}")
            pmt_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from the txn table: {pmt_mode_db}")
            amount_db = int(result["amount"].iloc[0])
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
                    "txn_amt": "{:.2f}".format(total_amount),
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
                    "txn_amt": total_amount,
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
                amount_api = int(response["amount"])
                logger.debug(f"Fetching amount from api response: {amount_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer_code from api response: {acquirer_code_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement_status from api response: {settlement_status_api}")
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
                state_api = response['states'][0]
                logger.debug(f"Fetching state from api response : {state_api}")

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
                    "txn_amt": total_amount,
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
                    "txn_amt": "{:.2f}".format(total_amount),
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
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal: {auth_code}")
                txn_type = transaction_details[0]['Type']
                logger.debug(f"Fetching txn_type from portal: {txn_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"Fetching status from portal: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"Fetching username from portal: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "pmt_state": str(status),
                    "pmt_type": txn_type,
                    "txn_amt": total_amt[1],
                    "username": username,
                    'auth_code': auth_code
                }
                logger.debug(f"expected_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation----------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                logger.info(f"date and time is: {txn_date},{txn_time}")

                expected_charge_slip_values = {
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),
                    'SERVICE FEE:': "Rs." + "{:.2f}".format(service_fee),
                    'TOTAL AMOUNT:': "Rs." + "{:.2f}".format(total_amount),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': auth_code
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

            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to disable Service Fee for the current merchant : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Reverting back credit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back credit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Reverting back debit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back debit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Reverting back netbanking details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back netbanking details in remotepay_setting table : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay and org settings")
        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_491():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Debit_Only_Enabled_Amt_PERCENT_JSON_Debit_With_PERCENT_Scheme_Debit_Card_Details
    Sub Feature Description: Verify Service Fee calculated when debit only enabled and amount ranges with PERCENT is
    passed and JSON is debit with PERCENT scheme  with Debit Card details.
    TC naming code description: 100: Payment Method, 103: RemotePay, 491: TC_491
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
        logger.debug(f"Query to fetch org_code from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-----------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
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
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
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

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "MASTER_CARD"
        payment_by = "DEBIT"
        json_id = "service_fee_json_TC_100_103_491"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "PERCENT"
        bank = "NULL"
        flat_fee, percent = testsuite_teardown.create_service_fee_config_data(portal_username=portal_username,
                                                                              org_code=org_code,
                                                                              derivation_type=derivation_type,
                                                                              scheme=scheme, payment_by=payment_by,
                                                                              config_data_json_id=json_id,
                                                                              payment_mode=payment_mode,
                                                                              account_label=acc_label, bank=bank)
        logger.info(f"flat_fee is : {flat_fee}")
        logger.info(f"fee percent is : {percent}")

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

            amount = random.randint(36, 40)
            logger.info(f"amount is: {amount}")
            flat_fee = float(flat_fee) if flat_fee is not 'NULL' else 0.0
            percent = float(percent) if percent is not 'NULL' else 0.0
            logger.debug(f"Flat Fee : {flat_fee}, Percentage : {percent}")
            service_fee = round((amount * percent / 100) + flat_fee, 2)
            total_amount = amount + service_fee
            logger.info(f"total amount is : {total_amount}")
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
                logger.info(f"Initiating a card txn")
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info(f"Entering card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enter_debit_expiry_month_debit_only("5")
                remote_pay_txn.enter_debit_expiry_year_debit_only("2045")
                remote_pay_txn.enter_debit_card_cvv("111")
                actual_service_fee = remote_pay_txn.fetch_service_fee()
                logger.debug(f"fetching actual service_fee = {actual_service_fee}")
                actual_order_amount = remote_pay_txn.fetch_order_amount()
                logger.debug(f"fetching actual order_amount = {actual_order_amount}")
                actual_total_amount = remote_pay_txn.fetch_total_amount()
                logger.debug(f"fetching actual total_amount = {actual_total_amount}")

                actual_service_fee = float(actual_service_fee.replace("₹", ""))
                logger.info(f"actual service fee is:  {actual_service_fee}")
                logger.info(f"expected service fee is:  {service_fee}")
                actual_order_amount = int(float(actual_order_amount.replace("₹", "")))
                logger.info(f"actual order amount is:  {actual_order_amount}")
                logger.info(f"expected order amount is:  {amount}")
                actual_total_amount = float(actual_total_amount.replace("₹", ""))
                logger.info(f"actual total amount is:  {actual_total_amount}")
                logger.info(f"expected total mount is:  {total_amount}")
                assert service_fee == actual_service_fee, "Service Fee is not matching."
                assert amount == actual_order_amount, "Amount is not matching."
                assert total_amount == actual_total_amount, "Total amount is not matching."

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
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetching bank name from the txn table {bank_name_db}")
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
                    "txn_amt": "{:.2f}".format(total_amount),
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
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": total_amount,
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
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer_code from api response: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn_type from api response: {txn_type_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org_code from api response: {org_code_api}")
                date_api = response["postingDate"]
                logger.debug(f"Fetching date from api response: {date_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response: {payment_mode_api}")
                state_api = response['states'][0]
                logger.debug(f"Fetching state from api response : {state_api}")

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
                    "txn_amt": total_amount,
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
                    "txn_amt": "{:.2f}".format(total_amount),
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

        # -----------------------------------------Start of ChargeSlip Validation----------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                logger.info(f"date and time is: {txn_date},{txn_time}")

                expected_charge_slip_values = {
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': "Rs." + "{:.2f}".format(amount),
                    'SERVICE FEE:': "Rs." + "{:.2f}".format(service_fee),
                    'TOTAL AMOUNT:': "Rs." + "{:.2f}".format(total_amount),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': auth_code
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
            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to disable Service Fee for the current merchant : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Reverting back credit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back credit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Reverting back debit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back debit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Reverting back netbanking details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back netbanking details in remotepay_setting table : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay and org settings")
        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_493():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Debit_Only_Enabled_JSON_Debit_With_FIXED_PERCENT_Scheme_Credit_Card_Details
    Sub Feature Description: Verify Error message when debit only enabled and JSON is debit with FIXED_PERCENT scheme
    with Credit Card details.
    TC naming code description: 100: Payment Method, 103: RemotePay, 493: TC_493
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
        logger.debug(f"Query to fetch org_code from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-----------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
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
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
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

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "MASTER_CARD"
        payment_by = "DEBIT"
        json_id = "service_fee_json_TC_100_103_493"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "FIXED_PERCENT"
        bank = "NULL"
        flat_fee, percent = testsuite_teardown.create_service_fee_config_data(portal_username=portal_username,
                                                                              org_code=org_code,
                                                                              derivation_type=derivation_type,
                                                                              scheme=scheme, payment_by=payment_by,
                                                                              config_data_json_id=json_id,
                                                                              payment_mode=payment_mode,
                                                                              account_label=acc_label, bank=bank)
        logger.info(f"flat_fee is: {flat_fee}")
        logger.info(f"fee percentage is: {percent}")

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

            amount = random.randint(35, 40)
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
                logger.info(f"payment intent id is: {payment_intent_id}")
                page = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"clicking on payment link")
                page.goto(payment_link_url)
                logger.info(f"Initiating a card txn")
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info(f"Entering card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("5267 3181 8797 5449")
                remote_pay_txn.enter_debit_expiry_month_debit_only("5")
                remote_pay_txn.enter_debit_expiry_year_debit_only("2045")
                remote_pay_txn.enter_debit_card_cvv("111")
                config_error_message = str(remote_pay_txn.serviceFeeConfigErrorMessage())
                logger.info(f"config_error_message: {config_error_message}")
                expected_message = f"An error occured. Please try another payment method or contact {org_code} support."
                assert expected_message == config_error_message, "Expected and actual error message is not matching."

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

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to disable Service Fee for the current merchant : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where setting_name='dcEnabledInCnp' and " \
                    f"org_code='{org_code}';"
            logger.debug(f"Query to update remote pay settings is : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Result for remote pay setting is: {result}")

            query = f"update remotepay_setting set setting_value='true' where setting_name='ccEnabledInCnp' and " \
                    f"org_code='{org_code}';"
            logger.debug(f"Query to update remote pay settings is : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Result for remote pay setting is: {result}")

            query = f"update remotepay_setting set setting_value='true' where setting_name='nbEnabledInCnp' and " \
                    f"org_code='{org_code}';"
            logger.debug(f"Query to update remote pay settings is : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Result for remote pay setting is: {result}")

            refresh_db()
            logger.info(f"Performing DB refresh")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_492():
    """
    Sub Feature Code:UI_Common_PM_CNP_Razorpay_Service_Fee_Debit_Only_Enabled_Amt_FIXED_PERCENT_JSON_Debit_With_FIXED_PERCENT_Scheme_Debit_Card_Details
    Sub Feature Description:Verify Service Fee calculated when debit only enabled and amount ranges with FIXED_PERCENT is passed and JSON is debit with FIXED_PERCENT scheme  with Debit Card details
    TC naming code description: 100: Payment Method, 103: RemotePay, 492: TC_492
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

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")
        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
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
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
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

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "MASTER_CARD"
        payment_by = "DEBIT"
        json_id = "service_fee_json_TC_100_103_492"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "FIXED_PERCENT"
        bank = "NULL"
        flat_fee, percent = testsuite_teardown.create_service_fee_config_data(portal_username=portal_username,
                                                                              org_code=org_code,
                                                                              derivation_type=derivation_type,
                                                                              scheme=scheme, payment_by=payment_by,
                                                                              config_data_json_id=json_id,
                                                                              payment_mode=payment_mode,
                                                                              account_label=acc_label, bank=bank)

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(36, 40)
            flat_fee = float(flat_fee) if flat_fee is not 'NULL' else 0.0
            percent = float(percent) if percent is not 'NULL' else 0.0
            logger.debug(f"Flat Fee : {flat_fee},Percentage : {percent}")
            print(f"percent*amount:{percent*amount}")
            print(f"(percent*amount)/100:{(percent*amount)/100}")
            print(f"round(percent*amount)/100:{round(percent*amount)/100}")
            service_fee = round((percent * amount)/100, 2) + flat_fee
            total_amount = amount + service_fee
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Amount used : {amount}, order ID : {order_id}")
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
                page.goto(payment_link_url)
                logger.debug(f"Initiating Card Payment")
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enter_debit_expiry_month_debit_only("3")
                remote_pay_txn.enter_debit_expiry_year_debit_only("2048")
                remote_pay_txn.enter_debit_card_cvv("111")
                actual_service_fee = remote_pay_txn.fetch_service_fee()
                logger.debug(f"actual service_fee = {actual_service_fee}")
                actual_order_amount = remote_pay_txn.fetch_order_amount()
                logger.debug(f"actual order_amount = {actual_order_amount}")
                actual_total_amount = remote_pay_txn.fetch_total_amount()
                logger.debug(f"actual total_amount = {actual_total_amount}")

                actual_service_fee=float(actual_service_fee.replace("₹", ""))
                actual_order_amount=float(actual_order_amount.replace("₹", ""))
                actual_total_amount=float(actual_total_amount.replace("₹", ""))

                assert service_fee == actual_service_fee, "Service Fee is not matching."
                assert amount == actual_order_amount, "Amount is not matching."
                assert total_amount == actual_total_amount, "Total amount is not matching."

                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.clickOnSuccessBtn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your actual success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."


            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")

            query = f"select * from cnp_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            txn_card_type = result['payment_option'].values[0]
            logger.debug(f"txn card type from db : {txn_card_type}")

            query = f"select * from cnpware_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(total_amount),
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
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Waiting completed for txn history page.")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

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
                logger.info(f"Fetching txn customer name from txn history for the txn : {app_payment_customer_name}")
                app_payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"txn settlement status from txn history for the txn : {app_payment_settlement_status}")
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
                    "txn_amt": total_amount,
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date}
                logger.debug(f"expectedAPIValues: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"status_api: {status_api}")
                amount_api = float(response["amount"])
                logger.debug(f"amount_api: {amount_api}")
                acquirer_code__api = response["acquirerCode"]
                logger.debug(f"acquirer_code__api: {acquirer_code__api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api: {issuer_code_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api: {txn_type_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api: {org_code_api}")
                date_api = response["postingDate"]
                logger.debug(f"date_api: {date_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response: {payment_mode_api}")

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
                    "txn_amt": total_amount,
                    "settle_status": "SETTLED",
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": txn_auth_code,
                    "cnp_pmt_gateway": "RAZORPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "pmt_flow": "REMOTEPAY",
                    "pmt_intent_status": "COMPLETED",
                    "card_type": "CNP_DC"
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")
                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                pmt_status_db = result["status"].iloc[0]
                logger.debug(f"pmt_status_db: {pmt_status_db}")
                pmt_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"pmt_mode_db: {pmt_mode_db}")
                txn_amt_db = float(result["amount"].iloc[0])
                logger.debug(f"txn_amt_db: {txn_amt_db}")
                settle_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settle_status_db: {settle_status_db}")
                pmt_state_db = result["state"].iloc[0]
                logger.debug(f"pmt_state_db: {pmt_state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db: {payment_gateway_db}")

                query = f"select * from payment_intent where id='{payment_intent_id}'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"payment_intent_status: {payment_intent_status}")

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
                    "txn_amt": float(total_amount),
                    "username": app_username,
                    'auth_code': txn_auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                logger.info(f"portal txn details : {transaction_details}")
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                txn_id_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"txn_id_portal: {txn_id_portal}")
                total_amt = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amt: {total_amt}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code: {auth_code}")
                txn_type = transaction_details[0]['Type']
                logger.debug(f"txn_type: {txn_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "pmt_state": str(status),
                    "pmt_type": txn_type,
                    "txn_amt": float(total_amt[1]),
                    "username": username,
                    'auth_code': auth_code
                }
                logger.debug(f"expected_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                logger.info(f"date and time is: {txn_date},{txn_time}")

                expected_charge_slip_values = {
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'SERVICE FEE:': "Rs." + "{:,.2f}".format(service_fee),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': txn_auth_code}
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

            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to disable Service Fee for the current merchant : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Reverting back credit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back credit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Reverting back debit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back debit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Reverting back netbanking details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back netbanking details in remotepay_setting table : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")
        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)