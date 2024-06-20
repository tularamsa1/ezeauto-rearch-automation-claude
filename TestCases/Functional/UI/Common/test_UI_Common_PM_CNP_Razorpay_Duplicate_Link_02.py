import random
import sys
import time
from datetime import datetime
import pytest

from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal, \
    get_txn_details_for_diff_order_id
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter, card_processor, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_384():
    """
    Sub Feature Code: UI_Common_PM_CNP_Same_Amt_Same_OrderID_First_Txn_CNP_Success_Second_Txn_Cash_Success
    Sub Feature Description: Verify two txns with same amount and same orderID when first txn CNP success and second txn cash success
    TC naming code description: 100: Payment Method, 103: RemotePay, 387: TC384
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        api_details["RequestBody"]["settings"]["duplicatePaymentFields"] = "null"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for duplicate payment setup to be enabled:  {response}")

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

        logger.info(f"Performing DB refresh")
        refresh_db()

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
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
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.remote_pay_netbanking()
                remote_pay_txn.remote_pay_click_and_expand_netbanking()
                remote_pay_txn.remote_pay_select_netbanking_bank_select("AU Small Finance Bank")
                remote_pay_txn.remote_pay_proceed_netbanking()
                remote_pay_txn.click_success_pmt_btn()

            logger.debug(f"Second txn initiated to check duplicate payment")
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Cash()
            logger.info("Selected payment mode is cash")
            payment_page.click_on_confirm()
            error_msg = payment_page.fetch_message_for_duplicate_check()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table for first txn: {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for first txn: {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for first txn: {acquirer_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for first txn: {customer_name_txn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for first txn: {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for first txn: {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for first txn: {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for first txn: {pmt_status}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for first txn: {payment_mode}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for first txn: {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for first txn: {amount_txn}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for first txn: {merchant_name}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for first txn: {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for first txn: {org_code_txn}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for first txn: {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for first txn: {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for first txn: {tid_txn}")
            payment_gateway = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for first txn: {payment_gateway}")

            query = f"select * from payment_intent where id = '{payment_intent_id}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

            query = f"select * from cnp_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnp_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for cnp_txn table for first txn: {result} ")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from cnp_txn table for first txn: {cnp_txn_rrn}")
            cnp_txn_payment_option = result['payment_option'].values[0]
            logger.debug(f"Fetching payment_option from cnp_txn table for first txn: {cnp_txn_payment_option}")
            cnp_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnp_txn table for first txn: {cnp_txn_payment_flow}")
            cnp_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnp_txn table for first txn: {cnp_txn_payment_status}")
            cnp_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnp_txn table for first txn: {cnp_txn_type}")
            cnp_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnp_txn table for first txn: {cnp_txn_payment_mode}")
            cnp_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnp_txn table for first txn: {cnp_txn_payment_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from cnp_txn table for first txn: {cnp_txn_acquirer_code}")
            cnp_txn_org_code = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from cnp_txn table for first txn: {cnp_txn_org_code}")
            cnp_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnp_txn table for first txn: {cnp_txn_payment_gateway}")
            cnp_payment_option_value_1 = result['payment_option_value1'].values[0]
            logger.debug(f"Fetching payment_option_value1 from cnp_txn table for first txn: {cnp_payment_option_value_1}")

            query = f"select * from cnpware_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnpware_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Fetching result for cnpware_txn table for first txn: {result} ")
            cnpware_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnpware_txn table for first txn: {cnpware_txn_payment_flow}")
            cnpware_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnpware_txn table for first txn: {cnpware_txn_payment_status}")
            cnpware_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnpware_txn table for first txn: {cnpware_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnpware_txn table for first txn: {cnpware_txn_payment_mode}")
            cnpware_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnpware_txn table for first txn: {cnpware_txn_payment_state}")
            cnpware_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnpware_txn table for first txn: {cnpware_txn_payment_gateway}")

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
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "customer_name": customer_name_txn,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile_txn,
                    "rrn": cnp_txn_rrn,

                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                logger.info("resetting the com.ezetap.basicapp")
                app_driver.reset()
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the first txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the first txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the first txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the first txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the first txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the first txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the first txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the first txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the first txn : {txn_id}, {app_customer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the first txn : {txn_id}, {app_customer_mobile}")

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
                    "rrn": str(app_rrn)
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    "rrn": str(cnp_txn_rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "customer_mobile": customer_mobile_txn,
                    "pmt_gateway": "RAZORPAY",

                    "err_msg": "You have already made a similar payment for the same Ref# " + str(
                        order_id) + " and amount " + str(
                        amount) + ".00. Please check the status of the payment(s) made before you proceed.",

                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount for first txn: {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for first txn: {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status for first txn: {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state for first txn: {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid for first txn: {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid for first txn: {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for first txn: {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for first txn: {api_settle_status}")
                api_rrn = response.get('rrNumber')
                logger.debug(f"From response fetch rrn : {api_rrn}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type for first txn: {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code for first txn: {api_org_code}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time for first txn: {api_date_time}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name for first txn: {api_merchant_name}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for first txn: {api_ext_ref_number}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name for first txn: {api_customer_name}")
                api_customer_mobile = response.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for first txn: {api_customer_mobile}")
                api_payment_gateway = response.get('paymentGateway')
                logger.debug(f"From response fetch paymentGateway for first txn: {api_payment_gateway}")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "rrn": str(api_rrn),
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "customer_mobile": api_customer_mobile,
                    "pmt_gateway": api_payment_gateway,
                    "err_msg": error_msg,
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
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_intent_status": "COMPLETED",

                    "cnp_pmt_option": "CNP_NB",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "cnp_pmt_state": "SETTLED",
                    "cnp_org_code": org_code,
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "cnpware_pmt_status": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state": "SETTLED",
                    "cnpware_pmt_mode": "CNP",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY"
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
                    "pmt_gateway": payment_gateway,
                    "pmt_intent_status": payment_intent_status,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "cnpware_pmt_status": cnpware_txn_payment_status,
                    "cnpware_pmt_state": cnpware_txn_payment_state,
                    "cnpware_pmt_mode": cnpware_txn_payment_mode,
                    "cnpware_pmt_flow": cnpware_txn_payment_flow,
                    "cnpware_pmt_gateway": cnpware_txn_payment_gateway,
                    "cnpware_txn_type": cnpware_txn_type
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code
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

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "rrn": portal_rrn,
                    "auth_code": portal_auth_code
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
                    "RRN": str(cnp_txn_rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "MID": mid_txn,
                    "TID": tid_txn,
                    "Net Banking": cnp_payment_option_value_1,
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
            api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "false"
            api_details["RequestBody"]["settings"]["duplicatePaymentFields"] = "paymentMode,username,processCode,txnType,amount"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for duplicate payment setup to be disabled:  {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_385():
    """
    Sub Feature Code: UI_Common_PM_CNP_Same_Amt_Same_OrderID_First_CNP_Success_Second_Cheque_Success
    Sub Feature Description: Verify two txns with same amount and same orderID when first txn CNP  success and second txn cheque success
    TC naming code description: 100: Payment Method, 103: RemotePay, 387: TC385
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        api_details["RequestBody"]["settings"]["duplicatePaymentFields"] = "null"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(
            f"Response received for setting preconditions for duplicate payment setup to be enabled:  {response}")

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

        logger.info(f"Performing DB refresh")
        refresh_db()

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
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
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.remote_pay_netbanking()
                remote_pay_txn.remote_pay_click_and_expand_netbanking()
                remote_pay_txn.remote_pay_select_netbanking_bank_select("AU Small Finance Bank")
                remote_pay_txn.remote_pay_proceed_netbanking()
                remote_pay_txn.click_success_pmt_btn()

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_cheque()
            logger.info("Selected payment mode is cheque")
            payment_page.fill_cheque_number(123456)
            payment_page.fill_bank_name("Allahabad Bank")
            x, y = payment_page.get_relative_coordinate_for_bank()
            payment_page.perform_click_to_bank(x, y)
            today_date = datetime.today().date().strftime("%d %B %Y")
            logger.debug(f"Generating today's date: {today_date}")
            payment_page.click_on_date(today_date)
            payment_page.fill_ifsc_code("ALLA0210329")
            x1, y1 = payment_page.get_relative_coordinate_for_ifsc_code()
            payment_page.perform_touch_action_on_cheque_home_page(x1, y1)
            payment_page.click_on_cheque_submit()
            error_msg = payment_page.fetch_message_for_duplicate_check()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table for first txn: {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for first txn: {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for first txn: {acquirer_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for first txn: {customer_name_txn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for first txn: {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for first txn: {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for first txn: {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for first txn: {pmt_status}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for first txn: {payment_mode}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for first txn: {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for first txn: {amount_txn}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for first txn: {merchant_name}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for first txn: {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for first txn: {org_code_txn}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for first txn: {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for first txn: {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for first txn: {tid_txn}")
            payment_gateway = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for first txn: {payment_gateway}")

            query = f"select * from payment_intent where id = '{payment_intent_id}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

            query = f"select * from cnp_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnp_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for cnp_txn table for first txn: {result} ")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from cnp_txn table for first txn: {cnp_txn_rrn}")
            cnp_txn_payment_option = result['payment_option'].values[0]
            logger.debug(f"Fetching payment_option from cnp_txn table for first txn: {cnp_txn_payment_option}")
            cnp_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnp_txn table for first txn: {cnp_txn_payment_flow}")
            cnp_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnp_txn table for first txn: {cnp_txn_payment_status}")
            cnp_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnp_txn table for first txn: {cnp_txn_type}")
            cnp_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnp_txn table for first txn: {cnp_txn_payment_mode}")
            cnp_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnp_txn table for first txn: {cnp_txn_payment_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from cnp_txn table for first txn: {cnp_txn_acquirer_code}")
            cnp_txn_org_code = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from cnp_txn table for first txn: {cnp_txn_org_code}")
            cnp_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnp_txn table for first txn: {cnp_txn_payment_gateway}")
            cnp_payment_option_value_1 = result['payment_option_value1'].values[0]
            logger.debug(
                f"Fetching payment_option_value1 from cnp_txn table for first txn: {cnp_payment_option_value_1}")

            query = f"select * from cnpware_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnpware_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Fetching result for cnpware_txn table for first txn: {result} ")
            cnpware_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnpware_txn table for first txn: {cnpware_txn_payment_flow}")
            cnpware_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnpware_txn table for first txn: {cnpware_txn_payment_status}")
            cnpware_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnpware_txn table for first txn: {cnpware_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnpware_txn table for first txn: {cnpware_txn_payment_mode}")
            cnpware_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnpware_txn table for first txn: {cnpware_txn_payment_state}")
            cnpware_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(
                f"Fetching payment_gateway from cnpware_txn table for first txn: {cnpware_txn_payment_gateway}")

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
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "customer_name": customer_name_txn,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile_txn,
                    "rrn": cnp_txn_rrn,

                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                logger.info("resetting the com.ezetap.basicapp")
                app_driver.reset()
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOS application using username : {app_username}")
                home_page = HomePage(driver=app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the first txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the first txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the first txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the first txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching payment_status from txn history for the first txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the first txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the first txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement_status from txn history for the first txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching customer_name from txn history for the first txn : {txn_id}, {app_customer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(
                    f"Fetching customer_mobile from txn history for the first txn : {txn_id}, {app_customer_mobile}")

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
                    "rrn": str(app_rrn)
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    "rrn": str(cnp_txn_rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "customer_mobile": customer_mobile_txn,
                    "pmt_gateway": "RAZORPAY",
                    "err_msg": "You have already made a similar payment for the same Ref# " + str(
                        order_id) + " and amount " + str(
                        amount) + ".00. Please check the status of the payment(s) made before you proceed.",
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount for first txn: {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for first txn: {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status for first txn: {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state for first txn: {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid for first txn: {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid for first txn: {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for first txn: {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for first txn: {api_settle_status}")
                api_rrn = response.get('rrNumber')
                logger.debug(f"From response fetch rrn : {api_rrn}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type for first txn: {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code for first txn: {api_org_code}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time for first txn: {api_date_time}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name for first txn: {api_merchant_name}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for first txn: {api_ext_ref_number}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name for first txn: {api_customer_name}")
                api_customer_mobile = response.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for first txn: {api_customer_mobile}")
                api_payment_gateway = response.get('paymentGateway')
                logger.debug(f"From response fetch paymentGateway for first txn: {api_payment_gateway}")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "rrn": str(api_rrn),
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "customer_mobile": api_customer_mobile,
                    "pmt_gateway": api_payment_gateway,
                    "err_msg": error_msg,
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
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_intent_status": "COMPLETED",

                    "cnp_pmt_option": "CNP_NB",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "cnp_pmt_state": "SETTLED",
                    "cnp_org_code": org_code,
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "cnpware_pmt_status": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state": "SETTLED",
                    "cnpware_pmt_mode": "CNP",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY"
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
                    "pmt_gateway": payment_gateway,
                    "pmt_intent_status": payment_intent_status,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "cnpware_pmt_status": cnpware_txn_payment_status,
                    "cnpware_pmt_state": cnpware_txn_payment_state,
                    "cnpware_pmt_mode": cnpware_txn_payment_mode,
                    "cnpware_pmt_flow": cnpware_txn_payment_flow,
                    "cnpware_pmt_gateway": cnpware_txn_payment_gateway,
                    "cnpware_txn_type": cnpware_txn_type
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[0]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[0]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_rrn = transaction_details[0]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[0]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[0]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")
                portal_auth_code = transaction_details[0]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "rrn": portal_rrn,
                    "auth_code": portal_auth_code
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
                    "RRN": str(cnp_txn_rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "MID": mid_txn,
                    "TID": tid_txn,
                    "Net Banking": cnp_payment_option_value_1,
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
            api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "false"
            api_details["RequestBody"]["settings"][
                "duplicatePaymentFields"] = "paymentMode,username,processCode,txnType,amount"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for duplicate payment setup to be disabled:  {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_387():
    """
    Sub Feature Code: UI_Common_PM_CNP_Same_Amt_Same_OrderID_First_Netbanking_Success_Second_CNP_Success
    Sub Feature Description: Verify two txns with same amount and same orderID when first txn Netbanking success and second txn CNP success
    TC naming code description: 100: Payment Method, 103: RemotePay, 387: TC387
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        api_details["RequestBody"]["settings"]["duplicatePaymentFields"] = "null"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for duplicate payment setup to be enabled:  {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
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
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.remote_pay_netbanking()
                remote_pay_txn.remote_pay_click_and_expand_netbanking()
                remote_pay_txn.remote_pay_select_netbanking_Rzp()
                remote_pay_txn.remote_pay_proceed_netbanking()
                remote_pay_txn.click_success_pmt_btn()

                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")

            status = response.get('success')
            logger.debug(f"From response fetch status : {status}")
            error_code = response.get('errorCode')
            logger.debug(f"From response fetch errorCode : {error_code}")
            error_message = response.get('errorMessage')
            logger.debug(f"From response fetch errorMessage : {error_message}")
            real_code = response.get('realCode')
            logger.debug(f"From response fetch realCode : {real_code}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table for first txn: {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for first txn: {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for first txn: {acquirer_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for first txn: {customer_name_txn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for first txn: {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for first txn: {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for first txn: {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for first txn: {pmt_status}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for first txn: {payment_mode}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for first txn: {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for first txn: {amount_txn}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for first txn: {merchant_name}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for first txn: {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for first txn: {org_code_txn}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for first txn: {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for first txn: {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for first txn: {tid_txn}")
            payment_gateway = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for first txn: {payment_gateway}")

            query = f"select * from payment_intent where id = '{payment_intent_id}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

            query = f"select * from cnp_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnp_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for cnp_txn table for first txn: {result} ")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from cnp_txn table for first txn: {cnp_txn_rrn}")
            cnp_txn_payment_option = result['payment_option'].values[0]
            logger.debug(f"Fetching payment_option from cnp_txn table for first txn: {cnp_txn_payment_option}")
            cnp_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnp_txn table for first txn: {cnp_txn_payment_flow}")
            cnp_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnp_txn table for first txn: {cnp_txn_payment_status}")
            cnp_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnp_txn table for first txn: {cnp_txn_type}")
            cnp_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnp_txn table for first txn: {cnp_txn_payment_mode}")
            cnp_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnp_txn table for first txn: {cnp_txn_payment_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from cnp_txn table for first txn: {cnp_txn_acquirer_code}")
            cnp_txn_org_code = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from cnp_txn table for first txn: {cnp_txn_org_code}")
            cnp_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnp_txn table for first txn: {cnp_txn_payment_gateway}")
            cnp_payment_option_value_1 = result['payment_option_value1'].values[0]
            logger.debug(f"Fetching payment_option_value1 from cnp_txn table for first txn: {cnp_payment_option_value_1}")

            query = f"select * from cnpware_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnpware_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Fetching result for cnpware_txn table for first txn: {result} ")
            cnpware_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnpware_txn table for first txn: {cnpware_txn_payment_flow}")
            cnpware_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnpware_txn table for first txn: {cnpware_txn_payment_status}")
            cnpware_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnpware_txn table for first txn: {cnpware_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnpware_txn table for first txn: {cnpware_txn_payment_mode}")
            cnpware_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnpware_txn table for first txn: {cnpware_txn_payment_state}")
            cnpware_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnpware_txn table for first txn: {cnpware_txn_payment_gateway}")

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
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "customer_name": customer_name_txn,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile_txn,
                    "rrn": cnp_txn_rrn,

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
                logger.info(f"Fetching txn amount from txn history for the first txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the first txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the first txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the first txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the first txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the first txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the first txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the first txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the first txn : {txn_id}, {app_customer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the first txn : {txn_id}, {app_customer_mobile}")

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
                    "rrn": str(app_rrn)
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
                    "txn_amt": float(amount),
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    "rrn": str(cnp_txn_rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "customer_mobile": customer_mobile_txn,
                    "pmt_gateway": "RAZORPAY",

                    "status": False,
                    "err_msg": "You have already made a similar payment for the same Ref# " + str(
                        order_id) + " and amount " + str(
                        amount) + ".00. Please check the status of the payment(s) made before you proceed.",
                    "err_code": "EZETAP_0000033",
                    "real_code": "PAYMENT_TXN_PRCSSD_FOR_REF_AMNT"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount for first txn: {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for first txn: {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status for first txn: {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state for first txn: {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid for first txn: {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid for first txn: {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for first txn: {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for first txn: {api_settle_status}")
                api_rrn = response.get('rrNumber')
                logger.debug(f"From response fetch rrn : {api_rrn}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type for first txn: {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code for first txn: {api_org_code}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time for first txn: {api_date_time}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name for first txn: {api_merchant_name}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for first txn: {api_ext_ref_number}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name for first txn: {api_customer_name}")
                api_customer_mobile = response.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for first txn: {api_customer_mobile}")
                api_payment_gateway = response.get('paymentGateway')
                logger.debug(f"From response fetch paymentGateway for first txn: {api_payment_gateway}")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "rrn": str(api_rrn),
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "customer_mobile": api_customer_mobile,
                    "pmt_gateway": api_payment_gateway,

                    "status": status,
                    "err_msg": error_message,
                    "err_code": error_code,
                    "real_code": real_code
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
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_intent_status": "COMPLETED",

                    "cnp_pmt_option": "CNP_NB",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "cnp_pmt_state": "SETTLED",
                    "cnp_org_code": org_code,
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "cnpware_pmt_status": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state": "SETTLED",
                    "cnpware_pmt_mode": "CNP",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY"
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
                    "pmt_gateway": payment_gateway,
                    "pmt_intent_status": payment_intent_status,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "cnpware_pmt_status": cnpware_txn_payment_status,
                    "cnpware_pmt_state": cnpware_txn_payment_state,
                    "cnpware_pmt_mode": cnpware_txn_payment_mode,
                    "cnpware_pmt_flow": cnpware_txn_payment_flow,
                    "cnpware_pmt_gateway": cnpware_txn_payment_gateway,
                    "cnpware_txn_type": cnpware_txn_type
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code
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

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "rrn": portal_rrn,
                    "auth_code": portal_auth_code
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
                    "RRN": str(cnp_txn_rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "MID": mid_txn,
                    "TID": tid_txn,
                    "Net Banking": cnp_payment_option_value_1,
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
            api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "false"
            api_details["RequestBody"]["settings"]["duplicatePaymentFields"] = "paymentMode,username,processCode,txnType,amount"
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for duplicate payment setup to be disabled:  {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)
