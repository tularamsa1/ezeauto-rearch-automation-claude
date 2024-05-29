import random
import sys
from datetime import datetime
import pytest
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
def test_common_100_103_488():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Success_RP_UPI_SF_Enabled_JSON_Configured
    Sub Feature Description: Verify CNP flow works for UPI when service fee is enabled for Card & Net banking and  JSON configured
    TC naming code description: 100: Payment Method, 103: RemotePay, 488: TC488
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
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

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'RAZORPAY_PSP' and card_terminal_acquirer_code = 'NONE'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f" pg_merchant_id from db : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f" upi_mc_id from db : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"tid from db : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"mid from db : {mid}")

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

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "MASTER_CARD"
        payment_by = "CREDIT"
        json_id = "service_fee_json_TC_100_103_488"
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
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(2200, 2300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Amount used : {amount}, order ID : {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')
            ui_browser.goto(payment_link_url)
            remote_pay_upi_txn = RemotePayTxnPage(ui_browser)

            actual_order_amount = remote_pay_upi_txn.fetch_order_amount()
            logger.debug(f"actual order_amount = {actual_order_amount}")

            logger.debug(f"Initiating UPI payment")
            remote_pay_upi_txn.clickOnRemotePayUPI()
            remote_pay_upi_txn.clickOnRemotePayLaunchUPI()
            remote_pay_upi_txn.clickOnRemotePayCancelUPI()
            remote_pay_upi_txn.clickOnRemotePayProceed()

            actual_order_amount = float(actual_order_amount.replace("₹", ""))
            assert amount == actual_order_amount, "Amount is not matching."
            success_message = str(remote_pay_upi_txn.succcessScreenMessage())
            logger.info(f"Your actual success message is:  {success_message}")
            logger.info(f"Your expected Message is:  {expected_message}")
            assert success_message == expected_message, "Success Message is not matching."

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query to fetch txn_id from txn table : {txn_id}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {created_time}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"acquirer_code_db from db : {acquirer_code_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"amount_db from db : {amount_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"bank_code_db from db : {bank_code_db}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"customer_name from db : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"payer_name from db : {payer_name}")
            issuer_code_db = result['issuer_code'].values[0]
            logger.debug(f"issuer_code from db : {issuer_code_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"mid from db : {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"tid from db : {tid_db}")
            org_code_db = result['org_code'].values[0]
            logger.debug(f"org_code_txn from db : {org_code_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"payment_mode_db from db : {payment_mode_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"rrn_db from db : {rrn_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"settlement_status_db from db : {settlement_status_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"status_db from db : {status_db}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"txn_type from db : {txn_type}")
            state_db = result["state"].iloc[0]
            logger.debug(f"state_db from db : {state_db}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"txn_auth_code from db : {txn_auth_code}")

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
                    "txn_amt": "{:,.2f}".format(amount) ,
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn_db),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

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
                logger.info(f"Fetching status from txn history for the txn :{payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn :{payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn :{app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn :{app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn :{app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn :  {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn :{app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
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
                date_time = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn_db),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_db,
                    "date": date_time
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
                logger.debug(f"Fetching status_api: {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"Fetching amount_api: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment_mode_api: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state_api: {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn_api: {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement_status_api: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer_code_api: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer_code_api: {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org_code_api: {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid_api: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid_api: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn_type_api: {txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"Fetching date_api: {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
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
                    "issuer_code": "RAZORPAY",
                    "org_code": org_code,
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from payment_intent where id='{payment_intent_id}'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result from payment_intent table: {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table: {payment_intent_status}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result from upi_txn table: {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status_db from upi_txn table: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type_db from upi_txn table: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code_db from upi_txn table: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id_db from upi_txn table: {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code_db,
                    "bank_code": bank_code_db,
                    "org_code": org_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
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
            date_and_time_portal = date_time_converter.to_portal_format(created_time)
            try:
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "txn_id": txn_id,
                    "rrn": rrn_db,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount) ,
                    "username": app_username,
                    'auth_code': "-" if txn_auth_code is None else txn_auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Fetching date_time from portal: {date_time}")
                txn_id_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"Fetching txn_id_portal from portal: {txn_id_portal}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total_amount from portal: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rr_number from portal: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"Fetching transaction_type from portal: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"Fetching status from portal: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"Fetching username from portal: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "rrn": rr_number,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "auth_code": auth_code
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
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn_db),
                    'BASE AMOUNT:': f"Rs.{amount:,}.00",
                    'date': txn_date,
                    'time': txn_time,
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
        try:
            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_489():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Success_RP_UPI_SF_Enabled_JSON_Not_Configured
    Sub Feature Description: Verify CNP flow works for UPI when service fee is enabled for Card & Net banking  and JSON not configured
    TC naming code description: 100: Payment Method, 103: RemotePay, 489: TC489
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
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
        # testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
        #                                                        portal_un=portal_username,
        #                                                        portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'RAZORPAY_PSP' and card_terminal_acquirer_code = 'NONE'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f" pg_merchant_id from db : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f" upi_mc_id from db : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"tid from db : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"mid from db : {mid}")

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

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)

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
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(2200, 2300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Amount used : {amount}, order ID : {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')
            ui_browser.goto(payment_link_url)
            remote_pay_upi_txn = RemotePayTxnPage(ui_browser)

            actual_order_amount = remote_pay_upi_txn.fetch_order_amount()
            logger.debug(f"actual order_amount = {actual_order_amount}")

            logger.debug(f"Initiating UPI payment")
            remote_pay_upi_txn.clickOnRemotePayUPI()
            remote_pay_upi_txn.clickOnRemotePayLaunchUPI()
            remote_pay_upi_txn.clickOnRemotePayCancelUPI()
            remote_pay_upi_txn.clickOnRemotePayProceed()

            actual_order_amount = float(actual_order_amount.replace("₹", ""))
            assert amount == actual_order_amount, "Amount is not matching."
            success_message = str(remote_pay_upi_txn.succcessScreenMessage())
            logger.info(f"Your actual success message is:  {success_message}")
            logger.info(f"Your expected Message is:  {expected_message}")
            assert success_message == expected_message, "Success Message is not matching."

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query to fetch txn_id from txn table : {txn_id}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {created_time}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"acquirer_code_db from db : {acquirer_code_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"amount_db from db : {amount_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"bank_code_db from db : {bank_code_db}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"customer_name from db : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"payer_name from db : {payer_name}")
            issuer_code_db = result['issuer_code'].values[0]
            logger.debug(f"issuer_code from db : {issuer_code_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"mid from db : {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"tid from db : {tid_db}")
            org_code_db = result['org_code'].values[0]
            logger.debug(f"org_code_txn from db : {org_code_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"payment_mode_db from db : {payment_mode_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"rrn_db from db : {rrn_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"settlement_status_db from db : {settlement_status_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"status_db from db : {status_db}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"txn_type from db : {txn_type}")
            state_db = result["state"].iloc[0]
            logger.debug(f"state_db from db : {state_db}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"txn_auth_code from db : {txn_auth_code}")

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
                    "txn_amt": "{:,.2f}".format(amount) ,
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn_db),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

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
                logger.info(f"Fetching status from txn history for the txn :{payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn :{payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn :{app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn :{app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn :{app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn :  {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn :{app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
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
                date_time = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn_db),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_db,
                    "date": date_time
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
                logger.debug(f"Fetching status_api: {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"Fetching amount_api: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment_mode_api: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state_api: {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn_api: {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement_status_api: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer_code_api: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer_code_api: {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org_code_api: {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid_api: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid_api: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching txn_type_api: {txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"Fetching date_api: {date_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
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
                    "issuer_code": "RAZORPAY",
                    "org_code": org_code,
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from payment_intent where id='{payment_intent_id}'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result from payment_intent table: {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table: {payment_intent_status}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result from upi_txn table: {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status_db from upi_txn table: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type_db from upi_txn table: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code_db from upi_txn table: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id_db from upi_txn table: {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code_db,
                    "bank_code": bank_code_db,
                    "org_code": org_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
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
            date_and_time_portal = date_time_converter.to_portal_format(created_time)
            try:
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "txn_id": txn_id,
                    "rrn": rrn_db,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount) ,
                    "username": app_username,
                    'auth_code': "-" if txn_auth_code is None else txn_auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"Fetching date_time from portal: {date_time}")
                txn_id_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"Fetching txn_id_portal from portal: {txn_id_portal}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total_amount from portal: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"Fetching rr_number from portal: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"Fetching transaction_type from portal: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"Fetching status from portal: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"Fetching username from portal: {username}")

                actual_portal_values = {
                    "date_time": date_time,
                    "txn_id": txn_id_portal,
                    "rrn": rr_number,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "auth_code": auth_code
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
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(rrn_db),
                    'BASE AMOUNT:': f"Rs.{amount:,}.00",
                    'date': txn_date,
                    'time': txn_time,
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
        try:
            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
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

